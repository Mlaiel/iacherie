"""Export Manager - Data Export and Integration Service

Advanced data export service for exporting analytics data to various formats
and integrating with external systems and platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import csv
import json
from typing import Dict, List, Optional, Any, Union, IO
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import io
import zipfile

# Import from existing analytics if available
try:
    from ....data_management.analytics.exporters import (
        ExportFormat,
        ExportDestination,
        ExportConfiguration
    )
except ImportError:
    # Fallback definitions
    class ExportFormat(Enum):
        JSON = "json"
        CSV = "csv"
        EXCEL = "excel"
        PDF = "pdf"
        XML = "xml"
    
    class ExportDestination(Enum):
        LOCAL_FILE = "local_file"
        CLOUD_STORAGE = "cloud_storage"
        EMAIL = "email"
        API_ENDPOINT = "api_endpoint"
        DATABASE = "database"
    
    @dataclass
    class ExportConfiguration:
        format: ExportFormat
        destination: ExportDestination
        filters: Dict[str, Any] = field(default_factory=dict)
        schedule: Optional[str] = None

logger = logging.getLogger(__name__)


class DataSource(Enum):
    """Available data sources for export"""
    USER_BEHAVIOR = "user_behavior"
    CONTENT_PERFORMANCE = "content_performance"
    ENGAGEMENT_METRICS = "engagement_metrics"
    SEO_ANALYTICS = "seo_analytics"
    REVENUE_METRICS = "revenue_metrics"
    SYSTEM_METRICS = "system_metrics"


class CompressionType(Enum):
    """Compression types for exports"""
    NONE = "none"
    ZIP = "zip"
    GZIP = "gzip"


@dataclass
class ExportRequest:
    """Data export request"""
    export_id: str
    data_source: DataSource
    format: ExportFormat
    destination: ExportDestination
    date_range: Dict[str, datetime]
    filters: Dict[str, Any] = field(default_factory=dict)
    compression: CompressionType = CompressionType.NONE
    user_id: Optional[str] = None
    email_recipients: List[str] = field(default_factory=list)


@dataclass
class ExportResult:
    """Export operation result"""
    export_id: str
    success: bool
    file_path: Optional[str] = None
    download_url: Optional[str] = None
    record_count: int = 0
    file_size: int = 0
    error_message: Optional[str] = None
    completed_at: Optional[datetime] = None


@dataclass
class ScheduledExport:
    """Scheduled export configuration"""
    schedule_id: str
    name: str
    export_config: ExportRequest
    cron_schedule: str  # Cron format
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None


class ExportManager:
    """Data export and integration management service"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.export_directory = self.config.get('export_directory', '/tmp/exports')
        self.max_file_size = self.config.get('max_file_size', 100 * 1024 * 1024)  # 100MB
        self.supported_formats = list(ExportFormat)
        self.active_exports = {}
        logger.info("ExportManager service initialized")
    
    async def export_data(self, request: ExportRequest) -> ExportResult:
        """
        Export data based on request configuration
        
        Args:
            request: Export request parameters
            
        Returns:
            ExportResult: Export operation result
        """
        try:
            logger.info(f"Starting export: {request.export_id}")
            
            # Track active export
            self.active_exports[request.export_id] = {
                'status': 'in_progress',
                'started_at': datetime.now()
            }
            
            # Extract data from source
            data = await self._extract_data(request)
            
            if not data:
                return ExportResult(
                    export_id=request.export_id,
                    success=False,
                    error_message="No data found for export",
                    completed_at=datetime.now()
                )
            
            # Format data
            formatted_data = await self._format_data(data, request.format)
            
            # Compress if requested
            if request.compression != CompressionType.NONE:
                formatted_data = await self._compress_data(formatted_data, request.compression)
            
            # Export to destination
            result = await self._export_to_destination(request, formatted_data, len(data))
            
            # Update export status
            self.active_exports[request.export_id]['status'] = 'completed'
            result.completed_at = datetime.now()
            
            logger.info(f"Export completed: {request.export_id}")
            return result
            
        except Exception as e:
            logger.error(f"Export failed: {request.export_id} - {str(e)}")
            self.active_exports[request.export_id]['status'] = 'failed'
            
            return ExportResult(
                export_id=request.export_id,
                success=False,
                error_message=str(e),
                completed_at=datetime.now()
            )
    
    async def schedule_export(self, schedule: ScheduledExport) -> bool:
        """
        Schedule recurring data export
        
        Args:
            schedule: Scheduled export configuration
            
        Returns:
            bool: Success status
        """
        try:
            # Calculate next run time based on cron schedule
            # This is a simplified implementation
            next_run = await self._calculate_next_run(schedule.cron_schedule)
            schedule.next_run = next_run
            
            # Store schedule (in real implementation, this would go to database)
            logger.info(f"Export scheduled: {schedule.schedule_id} - Next run: {next_run}")
            
            # TODO: Implement actual scheduling mechanism
            # This would typically integrate with a job scheduler like Celery or similar
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to schedule export: {str(e)}")
            return False
    
    async def get_export_status(self, export_id: str) -> Dict[str, Any]:
        """
        Get status of an export operation
        
        Args:
            export_id: Export identifier
            
        Returns:
            Dict: Export status information
        """
        if export_id in self.active_exports:
            return self.active_exports[export_id]
        else:
            # Check completed exports (would be from database in real implementation)
            return {
                'status': 'not_found',
                'message': 'Export not found'
            }
    
    async def list_scheduled_exports(self, user_id: Optional[str] = None) -> List[ScheduledExport]:
        """
        List scheduled exports
        
        Args:
            user_id: Optional user filter
            
        Returns:
            List[ScheduledExport]: Scheduled exports
        """
        # Simulate scheduled exports
        schedules = [
            ScheduledExport(
                schedule_id="daily_user_behavior",
                name="Daily User Behavior Export",
                export_config=ExportRequest(
                    export_id="daily_user_behavior",
                    data_source=DataSource.USER_BEHAVIOR,
                    format=ExportFormat.CSV,
                    destination=ExportDestination.EMAIL,
                    date_range={
                        'start_date': datetime.now() - timedelta(days=1),
                        'end_date': datetime.now()
                    },
                    email_recipients=["admin@example.com"]
                ),
                cron_schedule="0 6 * * *",  # Daily at 6 AM
                enabled=True
            ),
            ScheduledExport(
                schedule_id="weekly_performance",
                name="Weekly Performance Report",
                export_config=ExportRequest(
                    export_id="weekly_performance",
                    data_source=DataSource.CONTENT_PERFORMANCE,
                    format=ExportFormat.EXCEL,
                    destination=ExportDestination.CLOUD_STORAGE,
                    date_range={
                        'start_date': datetime.now() - timedelta(days=7),
                        'end_date': datetime.now()
                    }
                ),
                cron_schedule="0 8 * * 1",  # Monday at 8 AM
                enabled=True
            )
        ]
        
        return schedules
    
    async def cancel_export(self, export_id: str) -> bool:
        """
        Cancel an ongoing export operation
        
        Args:
            export_id: Export to cancel
            
        Returns:
            bool: Success status
        """
        try:
            if export_id in self.active_exports:
                self.active_exports[export_id]['status'] = 'cancelled'
                logger.info(f"Export cancelled: {export_id}")
                return True
            else:
                logger.warning(f"Export not found for cancellation: {export_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to cancel export: {str(e)}")
            return False
    
    async def bulk_export(self, requests: List[ExportRequest]) -> List[ExportResult]:
        """
        Execute multiple exports in batch
        
        Args:
            requests: List of export requests
            
        Returns:
            List[ExportResult]: Export results
        """
        try:
            results = []
            
            # Process exports concurrently (with limit)
            semaphore = asyncio.Semaphore(5)  # Limit concurrent exports
            
            async def export_with_semaphore(request):
                async with semaphore:
                    return await self.export_data(request)
            
            tasks = [export_with_semaphore(request) for request in requests]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append(ExportResult(
                        export_id=requests[i].export_id,
                        success=False,
                        error_message=str(result),
                        completed_at=datetime.now()
                    ))
                else:
                    processed_results.append(result)
            
            logger.info(f"Bulk export completed: {len(processed_results)} exports")
            return processed_results
            
        except Exception as e:
            logger.error(f"Bulk export failed: {str(e)}")
            return []
    
    # Private helper methods
    
    async def _extract_data(self, request: ExportRequest) -> List[Dict[str, Any]]:
        """Extract data from specified source"""
        try:
            # This would integrate with actual data sources
            # For now, simulate data based on source type
            
            data = []
            record_count = 100  # Simulate 100 records
            
            if request.data_source == DataSource.USER_BEHAVIOR:
                for i in range(record_count):
                    data.append({
                        'user_id': f'user_{i}',
                        'session_id': f'session_{i}',
                        'action_type': 'view',
                        'timestamp': (datetime.now() - timedelta(minutes=i)).isoformat(),
                        'platform': 'web'
                    })
            
            elif request.data_source == DataSource.CONTENT_PERFORMANCE:
                for i in range(record_count):
                    data.append({
                        'content_id': f'content_{i}',
                        'title': f'Content Title {i}',
                        'views': 1000 + i * 10,
                        'likes': 100 + i,
                        'shares': 10 + i // 10,
                        'performance_score': 70 + (i % 30),
                        'created_at': (datetime.now() - timedelta(days=i)).isoformat()
                    })
            
            elif request.data_source == DataSource.ENGAGEMENT_METRICS:
                for i in range(record_count):
                    data.append({
                        'content_id': f'content_{i // 10}',
                        'user_id': f'user_{i}',
                        'engagement_type': ['like', 'comment', 'share', 'save'][i % 4],
                        'timestamp': (datetime.now() - timedelta(hours=i)).isoformat(),
                        'platform': 'mobile' if i % 2 else 'web'
                    })
            
            # Apply filters
            if request.filters:
                data = await self._apply_filters(data, request.filters)
            
            # Apply date range filter
            if 'start_date' in request.date_range and 'end_date' in request.date_range:
                data = await self._apply_date_filter(data, request.date_range)
            
            logger.info(f"Extracted {len(data)} records from {request.data_source.value}")
            return data
            
        except Exception as e:
            logger.error(f"Data extraction failed: {str(e)}")
            return []
    
    async def _format_data(self, data: List[Dict[str, Any]], format: ExportFormat) -> Union[str, bytes]:
        """Format data according to specified format"""
        try:
            if format == ExportFormat.JSON:
                return json.dumps(data, indent=2, default=str)
            
            elif format == ExportFormat.CSV:
                if not data:
                    return ""
                
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
                return output.getvalue()
            
            elif format == ExportFormat.XML:
                # Simple XML formatting
                xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<data>']
                
                for record in data:
                    xml_lines.append('  <record>')
                    for key, value in record.items():
                        xml_lines.append(f'    <{key}>{value}</{key}>')
                    xml_lines.append('  </record>')
                
                xml_lines.append('</data>')
                return '\n'.join(xml_lines)
            
            else:
                # Default to JSON for unsupported formats
                return json.dumps(data, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Data formatting failed: {str(e)}")
            return ""
    
    async def _compress_data(self, data: Union[str, bytes], compression: CompressionType) -> bytes:
        """Compress data using specified compression type"""
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            if compression == CompressionType.ZIP:
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    zip_file.writestr('export_data.txt', data)
                return zip_buffer.getvalue()
            
            elif compression == CompressionType.GZIP:
                import gzip
                return gzip.compress(data)
            
            else:
                return data
                
        except Exception as e:
            logger.error(f"Data compression failed: {str(e)}")
            return data if isinstance(data, bytes) else data.encode('utf-8')
    
    async def _export_to_destination(self, request: ExportRequest, data: Union[str, bytes], record_count: int) -> ExportResult:
        """Export data to specified destination"""
        try:
            if request.destination == ExportDestination.LOCAL_FILE:
                return await self._export_to_local_file(request, data, record_count)
            
            elif request.destination == ExportDestination.EMAIL:
                return await self._export_to_email(request, data, record_count)
            
            elif request.destination == ExportDestination.CLOUD_STORAGE:
                return await self._export_to_cloud_storage(request, data, record_count)
            
            elif request.destination == ExportDestination.API_ENDPOINT:
                return await self._export_to_api(request, data, record_count)
            
            else:
                raise ValueError(f"Unsupported destination: {request.destination}")
                
        except Exception as e:
            logger.error(f"Export to destination failed: {str(e)}")
            raise
    
    async def _export_to_local_file(self, request: ExportRequest, data: Union[str, bytes], record_count: int) -> ExportResult:
        """Export to local file"""
        try:
            file_extension = request.format.value
            if request.compression != CompressionType.NONE:
                file_extension += f".{request.compression.value}"
            
            file_name = f"{request.export_id}.{file_extension}"
            file_path = f"{self.export_directory}/{file_name}"
            
            # Create directory if it doesn't exist
            import os
            os.makedirs(self.export_directory, exist_ok=True)
            
            # Write file
            mode = 'wb' if isinstance(data, bytes) else 'w'
            encoding = None if isinstance(data, bytes) else 'utf-8'
            
            with open(file_path, mode, encoding=encoding) as f:
                f.write(data)
            
            file_size = len(data) if isinstance(data, bytes) else len(data.encode('utf-8'))
            
            return ExportResult(
                export_id=request.export_id,
                success=True,
                file_path=file_path,
                record_count=record_count,
                file_size=file_size
            )
            
        except Exception as e:
            logger.error(f"Local file export failed: {str(e)}")
            raise
    
    async def _export_to_email(self, request: ExportRequest, data: Union[str, bytes], record_count: int) -> ExportResult:
        """Export via email (simulate)"""
        try:
            # In real implementation, this would send email with attachment
            logger.info(f"Email export simulated for {len(request.email_recipients)} recipients")
            
            return ExportResult(
                export_id=request.export_id,
                success=True,
                record_count=record_count,
                file_size=len(data) if isinstance(data, bytes) else len(data.encode('utf-8'))
            )
            
        except Exception as e:
            logger.error(f"Email export failed: {str(e)}")
            raise
    
    async def _export_to_cloud_storage(self, request: ExportRequest, data: Union[str, bytes], record_count: int) -> ExportResult:
        """Export to cloud storage (simulate)"""
        try:
            # In real implementation, this would upload to cloud storage
            download_url = f"https://storage.example.com/exports/{request.export_id}"
            
            logger.info(f"Cloud storage export simulated: {download_url}")
            
            return ExportResult(
                export_id=request.export_id,
                success=True,
                download_url=download_url,
                record_count=record_count,
                file_size=len(data) if isinstance(data, bytes) else len(data.encode('utf-8'))
            )
            
        except Exception as e:
            logger.error(f"Cloud storage export failed: {str(e)}")
            raise
    
    async def _export_to_api(self, request: ExportRequest, data: Union[str, bytes], record_count: int) -> ExportResult:
        """Export to API endpoint (simulate)"""
        try:
            # In real implementation, this would POST data to API endpoint
            logger.info(f"API export simulated for {record_count} records")
            
            return ExportResult(
                export_id=request.export_id,
                success=True,
                record_count=record_count,
                file_size=len(data) if isinstance(data, bytes) else len(data.encode('utf-8'))
            )
            
        except Exception as e:
            logger.error(f"API export failed: {str(e)}")
            raise
    
    async def _apply_filters(self, data: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply filters to data"""
        filtered_data = data
        
        for filter_key, filter_value in filters.items():
            filtered_data = [
                record for record in filtered_data
                if record.get(filter_key) == filter_value
            ]
        
        return filtered_data
    
    async def _apply_date_filter(self, data: List[Dict[str, Any]], date_range: Dict[str, datetime]) -> List[Dict[str, Any]]:
        """Apply date range filter to data"""
        start_date = date_range.get('start_date')
        end_date = date_range.get('end_date')
        
        if not start_date or not end_date:
            return data
        
        filtered_data = []
        for record in data:
            # Look for timestamp fields
            timestamp_fields = ['timestamp', 'created_at', 'updated_at', 'date']
            record_date = None
            
            for field in timestamp_fields:
                if field in record:
                    try:
                        if isinstance(record[field], str):
                            record_date = datetime.fromisoformat(record[field].replace('Z', '+00:00'))
                        elif isinstance(record[field], datetime):
                            record_date = record[field]
                        break
                    except:
                        continue
            
            if record_date and start_date <= record_date <= end_date:
                filtered_data.append(record)
            elif not record_date:  # Include records without timestamps
                filtered_data.append(record)
        
        return filtered_data
    
    async def _calculate_next_run(self, cron_schedule: str) -> datetime:
        """Calculate next run time from cron schedule (simplified)"""
        # This is a very simplified implementation
        # In production, use a proper cron parsing library like croniter
        
        now = datetime.now()
        
        # Simple patterns
        if cron_schedule == "0 6 * * *":  # Daily at 6 AM
            next_run = now.replace(hour=6, minute=0, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
        elif cron_schedule == "0 8 * * 1":  # Monday at 8 AM
            next_run = now.replace(hour=8, minute=0, second=0, microsecond=0)
            days_ahead = 0 - now.weekday()  # Monday is 0
            if days_ahead <= 0 or (days_ahead == 0 and next_run <= now):
                days_ahead += 7
            next_run += timedelta(days=days_ahead)
        else:
            # Default to next hour
            next_run = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        
        return next_run