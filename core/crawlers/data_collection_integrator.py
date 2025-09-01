#!/usr/bin/env python3
"""Data collection integration module to connect crawlers with data harvester
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

class DataCollectionIntegrator:
    """
    Integrates crawler manager with data harvester for complete data collection pipeline
    """
    
    def __init__(self, crawler_manager=None, data_harvester=None, logger=None):
        self.crawler_manager = crawler_manager
        self.data_harvester = data_harvester
        self.logger = logger or logging.getLogger(__name__)
        self.collection_tasks = {}
        self.is_running = False
    
    async def start_integrated_collection(
        self,
        platforms: List[str],
        search_terms: List[str],
        fingerprint_data: Dict[str, Any],
        collection_config: Dict[str, Any] = None
    ) -> str:
        """
        Starts integrated collection across platforms using both crawlers and harvester
        
        Args:
            platforms: List of platforms to collect from
            search_terms: Search terms for crawler
            fingerprint_data: Content fingerprint for matching
            collection_config: Configuration for collection behavior
            
        Returns:
            Task ID for the collection session
        """
        task_id = f"integrated_collection_{int(datetime.now().timestamp())}"
        
        try:
            self.logger.info(f"Starting integrated collection {task_id}")
            
            # Default configuration
            config = collection_config or {}
            
            # Start crawler tasks for each platform
            crawler_tasks = []
            if self.crawler_manager:
                for platform in platforms:
                    crawler_task_id = await self.crawler_manager.create_crawler_task(
                        crawler_type=platform,
                        fingerprint_data=fingerprint_data,
                        search_config={
                            'search_terms': search_terms,
                            'similarity_threshold': config.get('similarity_threshold', 0.8),
                            'max_results': config.get('max_results_per_platform', 50),
                            'interval_minutes': config.get('crawl_interval_minutes', 60)
                        },
                        schedule_config={
                            'type': 'interval',
                            'interval_minutes': config.get('crawl_interval_minutes', 60)
                        }
                    )
                    crawler_tasks.append(crawler_task_id)
            
            # Set up data harvester targets for additional sources
            harvester_targets = []
            if self.data_harvester:
                # Add RSS feeds, news sources, etc.
                additional_sources = config.get('additional_sources', [])
                for source in additional_sources:
                    target_id = await self.data_harvester.add_harvesting_target(
                        source_url=source['url'],
                        source_type=source['type'],
                        data_format=source['format'],
                        extraction_rules=source.get('extraction_rules', {}),
                        scheduling={'interval_minutes': config.get('harvest_interval_minutes', 120)},
                        output_config={'export_formats': ['json', 'csv']}
                    )
                    harvester_targets.append(target_id)
            
            # Store task information
            self.collection_tasks[task_id] = {
                'status': 'running',
                'crawler_tasks': crawler_tasks,
                'harvester_targets': harvester_targets,
                'platforms': platforms,
                'search_terms': search_terms,
                'started_at': datetime.now(),
                'config': config
            }
            
            self.logger.info(f"Integrated collection {task_id} started with {len(crawler_tasks)} crawler tasks and {len(harvester_targets)} harvester targets")
            return task_id
            
        except Exception as e:
            self.logger.error(f"Error starting integrated collection: {e}")
            raise
    
    async def get_collection_results(self, task_id: str) -> Dict[str, Any]:
        """
        Retrieves aggregated results from both crawlers and harvester
        
        Args:
            task_id: Collection task ID
            
        Returns:
            Aggregated results from all collection sources
        """
        if task_id not in self.collection_tasks:
            raise ValueError(f"Collection task {task_id} not found")
        
        task_info = self.collection_tasks[task_id]
        results = {
            'task_id': task_id,
            'status': task_info['status'],
            'started_at': task_info['started_at'],
            'platforms': task_info['platforms'],
            'crawler_results': [],
            'harvester_results': [],
            'summary': {}
        }
        
        try:
            # Get crawler results
            if self.crawler_manager and task_info['crawler_tasks']:
                for crawler_task_id in task_info['crawler_tasks']:
                    try:
                        crawler_result = await self.crawler_manager.get_task_result(crawler_task_id)
                        if crawler_result:
                            results['crawler_results'].append(crawler_result)
                    except Exception as e:
                        self.logger.warning(f"Error getting crawler result {crawler_task_id}: {e}")
            
            # Get harvester results
            if self.data_harvester and task_info['harvester_targets']:
                harvester_status = self.data_harvester.get_harvesting_status()
                for target_id in task_info['harvester_targets']:
                    try:
                        if target_id in harvester_status.get('recent_results', []):
                            target_result = [r for r in harvester_status['recent_results'] if r.get('target_id') == target_id]
                            if target_result:
                                results['harvester_results'].extend(target_result)
                    except Exception as e:
                        self.logger.warning(f"Error getting harvester result {target_id}: {e}")
            
            # Generate summary
            results['summary'] = self._generate_results_summary(results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error retrieving collection results: {e}")
            raise
    
    def _generate_results_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics from collected results"""
        summary = {
            'total_matches': 0,
            'total_data_points': 0,
            'platforms_covered': len(results['platforms']),
            'collection_duration': 0,
            'match_types': {},
            'data_sources': {}
        }
        
        # Count crawler matches
        for crawler_result in results['crawler_results']:
            if 'matches' in crawler_result:
                summary['total_matches'] += len(crawler_result['matches'])
                for match in crawler_result['matches']:
                    match_type = match.get('match_type', 'unknown')
                    summary['match_types'][match_type] = summary['match_types'].get(match_type, 0) + 1
        
        # Count harvester data points
        for harvester_result in results['harvester_results']:
            summary['total_data_points'] += 1
            source_type = harvester_result.get('source_type', 'unknown')
            summary['data_sources'][source_type] = summary['data_sources'].get(source_type, 0) + 1
        
        # Calculate duration
        if 'started_at' in results:
            duration = datetime.now() - results['started_at']
            summary['collection_duration'] = duration.total_seconds()
        
        return summary
    
    async def stop_collection(self, task_id: str) -> bool:
        """
        Stops all collection activities for a task
        
        Args:
            task_id: Collection task ID
            
        Returns:
            True if successfully stopped
        """
        if task_id not in self.collection_tasks:
            return False
        
        try:
            task_info = self.collection_tasks[task_id]
            
            # Stop crawler tasks
            if self.crawler_manager and task_info['crawler_tasks']:
                for crawler_task_id in task_info['crawler_tasks']:
                    try:
                        await self.crawler_manager.stop_task(crawler_task_id)
                    except Exception as e:
                        self.logger.warning(f"Error stopping crawler task {crawler_task_id}: {e}")
            
            # Stop harvester targets
            if self.data_harvester:
                await self.data_harvester.stop_harvesting()
            
            # Update task status
            self.collection_tasks[task_id]['status'] = 'stopped'
            self.collection_tasks[task_id]['stopped_at'] = datetime.now()
            
            self.logger.info(f"Collection task {task_id} stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping collection task {task_id}: {e}")
            return False
    
    async def get_all_collection_status(self) -> Dict[str, Any]:
        """Get status of all collection tasks"""
        status = {
            'total_tasks': len(self.collection_tasks),
            'active_tasks': len([t for t in self.collection_tasks.values() if t['status'] == 'running']),
            'tasks': []
        }
        
        for task_id, task_info in self.collection_tasks.items():
            task_status = {
                'task_id': task_id,
                'status': task_info['status'],
                'platforms': task_info['platforms'],
                'started_at': task_info['started_at'].isoformat(),
                'crawler_tasks_count': len(task_info['crawler_tasks']),
                'harvester_targets_count': len(task_info['harvester_targets'])
            }
            
            if 'stopped_at' in task_info:
                task_status['stopped_at'] = task_info['stopped_at'].isoformat()
            
            status['tasks'].append(task_status)
        
        return status

    async def setup_continuous_monitoring(
        self,
        platforms: List[str],
        keywords: List[str],
        fingerprint_data: Dict[str, Any],
        monitoring_config: Dict[str, Any] = None
    ) -> str:
        """
        Sets up continuous monitoring across multiple platforms
        
        Args:
            platforms: Platforms to monitor
            keywords: Keywords to track
            fingerprint_data: Content fingerprint for matching
            monitoring_config: Monitoring configuration
            
        Returns:
            Monitoring session ID
        """
        config = monitoring_config or {}
        
        # Set up continuous collection with shorter intervals
        collection_config = {
            'similarity_threshold': config.get('similarity_threshold', 0.85),
            'max_results_per_platform': config.get('max_results_per_platform', 25),
            'crawl_interval_minutes': config.get('crawl_interval_minutes', 30),
            'harvest_interval_minutes': config.get('harvest_interval_minutes', 60),
            'additional_sources': config.get('additional_sources', [])
        }
        
        task_id = await self.start_integrated_collection(
            platforms=platforms,
            search_terms=keywords,
            fingerprint_data=fingerprint_data,
            collection_config=collection_config
        )
        
        # Mark as monitoring task
        self.collection_tasks[task_id]['type'] = 'monitoring'
        self.collection_tasks[task_id]['monitoring_config'] = config
        
        self.logger.info(f"Continuous monitoring setup complete: {task_id}")
        return task_id