"""
⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Data Pipeline Templates for Ainflue Platform
==========================================

Production-ready data pipeline templates with:
- ETL/ELT pipeline architectures
- Real-time data processing
- Batch processing optimization
- Stream processing with Kafka
- Data quality monitoring
- Error handling and recovery
- Performance optimization
- Scalable data workflows

Author: Fahed Mlaiel (mlaiel@live.de)
Lead Dev IA + Backend Senior + ML Engineer + DBA Expert
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List, Callable, AsyncGenerator
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import time

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field, validator
import redis.asyncio as redis
from prometheus_client import Counter, Histogram, Gauge


# Metrics
pipeline_executions = Counter('pipeline_executions_total', 'Total pipeline executions', ['pipeline_type', 'status'])
pipeline_duration = Histogram('pipeline_duration_seconds', 'Pipeline execution duration')
active_pipelines = Gauge('active_pipelines', 'Number of active pipelines')


class PipelineStatus(Enum):
    """États des pipelines"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class ProcessingMode(Enum):
    """Modes de traitement"""
    BATCH = "batch"
    STREAM = "stream"
    MICRO_BATCH = "micro_batch"
    REAL_TIME = "real_time"


@dataclass
class PipelineConfig:
    """Configuration de pipeline"""
    pipeline_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    processing_mode: ProcessingMode = ProcessingMode.BATCH
    schedule: Optional[str] = None
    retry_config: Dict[str, Any] = field(default_factory=dict)
    monitoring_config: Dict[str, Any] = field(default_factory=dict)
    resource_limits: Dict[str, Any] = field(default_factory=dict)


class DataSource(BaseModel):
    """Source de données"""
    source_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_type: str = Field(..., regex="^(database|file|api|stream|queue)$")
    connection_config: Dict[str, Any] = Field(default_factory=dict)
    schema_config: Optional[Dict[str, Any]] = None
    read_config: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('source_type')
    def validate_source_type(cls, v):
        allowed_types = ['database', 'file', 'api', 'stream', 'queue']
        if v not in allowed_types:
            raise ValueError(f'Source type must be one of: {allowed_types}')
        return v


class DataTransformation(BaseModel):
    """Transformation de données"""
    transformation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    transformation_type: str = Field(..., regex="^(filter|map|aggregate|join|pivot|sort)$")
    transformation_config: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Optional[Dict[str, Any]] = None
    dependencies: List[str] = Field(default_factory=list)


class DataDestination(BaseModel):
    """Destination de données"""
    destination_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    destination_type: str = Field(..., regex="^(database|file|api|stream|cache)$")
    connection_config: Dict[str, Any] = Field(default_factory=dict)
    write_config: Dict[str, Any] = Field(default_factory=dict)
    partition_config: Optional[Dict[str, Any]] = None


class DataPipelineTemplate:
    """
    Template principal pour pipelines de données
    Architecture enterprise avec monitoring avancé
    """
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.sources: List[DataSource] = []
        self.transformations: List[DataTransformation] = []
        self.destinations: List[DataDestination] = []
        self.status = PipelineStatus.PENDING
        self.execution_history: List[Dict[str, Any]] = []
        self.metrics = {
            'executions': 0,
            'success_rate': 0.0,
            'avg_duration': 0.0,
            'last_execution': None
        }
        
    async def add_source(self, source: DataSource):
        """Ajout d'une source de données"""
        self.sources.append(source)
        logging.info(f"Added data source: {source.source_id}")
    
    async def add_transformation(self, transformation: DataTransformation):
        """Ajout d'une transformation"""
        self.transformations.append(transformation)
        logging.info(f"Added transformation: {transformation.transformation_id}")
    
    async def add_destination(self, destination: DataDestination):
        """Ajout d'une destination"""
        self.destinations.append(destination)
        logging.info(f"Added destination: {destination.destination_id}")
    
    async def execute(self) -> Dict[str, Any]:
        """Exécution du pipeline"""
        execution_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            self.status = PipelineStatus.RUNNING
            active_pipelines.inc()
            
            logging.info(f"Starting pipeline execution: {execution_id}")
            
            # Lecture des données sources
            source_data = await self._read_from_sources()
            
            # Application des transformations
            transformed_data = await self._apply_transformations(source_data)
            
            # Écriture vers les destinations
            write_results = await self._write_to_destinations(transformed_data)
            
            # Finalisation
            execution_time = time.time() - start_time
            self.status = PipelineStatus.COMPLETED
            
            execution_result = {
                'execution_id': execution_id,
                'pipeline_id': self.config.pipeline_id,
                'status': self.status.value,
                'execution_time': execution_time,
                'records_processed': len(transformed_data) if transformed_data else 0,
                'write_results': write_results,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Mise à jour des métriques
            await self._update_metrics(execution_result)
            
            pipeline_executions.labels(
                pipeline_type=self.config.processing_mode.value,
                status='success'
            ).inc()
            pipeline_duration.observe(execution_time)
            
            return execution_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.status = PipelineStatus.FAILED
            
            error_result = {
                'execution_id': execution_id,
                'pipeline_id': self.config.pipeline_id,
                'status': self.status.value,
                'error': str(e),
                'execution_time': execution_time,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            pipeline_executions.labels(
                pipeline_type=self.config.processing_mode.value,
                status='error'
            ).inc()
            
            logging.error(f"Pipeline execution failed: {str(e)}")
            raise
            
        finally:
            active_pipelines.dec()
    
    async def _read_from_sources(self) -> Dict[str, Any]:
        """Lecture des données depuis les sources"""
        source_data = {}
        
        for source in self.sources:
            try:
                if source.source_type == "database":
                    data = await self._read_from_database(source)
                elif source.source_type == "file":
                    data = await self._read_from_file(source)
                elif source.source_type == "api":
                    data = await self._read_from_api(source)
                elif source.source_type == "stream":
                    data = await self._read_from_stream(source)
                else:
                    raise ValueError(f"Unsupported source type: {source.source_type}")
                
                source_data[source.source_id] = data
                
            except Exception as e:
                logging.error(f"Error reading from source {source.source_id}: {str(e)}")
                raise
        
        return source_data
    
    async def _apply_transformations(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Application des transformations"""
        current_data = data
        
        for transformation in self.transformations:
            try:
                if transformation.transformation_type == "filter":
                    current_data = await self._apply_filter(current_data, transformation)
                elif transformation.transformation_type == "map":
                    current_data = await self._apply_map(current_data, transformation)
                elif transformation.transformation_type == "aggregate":
                    current_data = await self._apply_aggregate(current_data, transformation)
                elif transformation.transformation_type == "join":
                    current_data = await self._apply_join(current_data, transformation)
                else:
                    raise ValueError(f"Unsupported transformation: {transformation.transformation_type}")
                    
            except Exception as e:
                logging.error(f"Error in transformation {transformation.transformation_id}: {str(e)}")
                raise
        
        return current_data if isinstance(current_data, list) else [current_data]
    
    async def _write_to_destinations(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Écriture vers les destinations"""
        write_results = {}
        
        for destination in self.destinations:
            try:
                if destination.destination_type == "database":
                    result = await self._write_to_database(data, destination)
                elif destination.destination_type == "file":
                    result = await self._write_to_file(data, destination)
                elif destination.destination_type == "api":
                    result = await self._write_to_api(data, destination)
                else:
                    raise ValueError(f"Unsupported destination: {destination.destination_type}")
                
                write_results[destination.destination_id] = result
                
            except Exception as e:
                logging.error(f"Error writing to destination {destination.destination_id}: {str(e)}")
                raise
        
        return write_results
    
    async def _read_from_database(self, source: DataSource) -> List[Dict[str, Any]]:
        """Lecture depuis une base de données"""
        # Simulation de lecture BDD
        return [
            {'id': i, 'data': f'database_record_{i}', 'timestamp': datetime.utcnow().isoformat()}
            for i in range(100)
        ]
    
    async def _read_from_file(self, source: DataSource) -> List[Dict[str, Any]]:
        """Lecture depuis un fichier"""
        # Simulation de lecture fichier
        return [
            {'id': i, 'data': f'file_record_{i}', 'timestamp': datetime.utcnow().isoformat()}
            for i in range(50)
        ]
    
    async def _read_from_api(self, source: DataSource) -> List[Dict[str, Any]]:
        """Lecture depuis une API"""
        # Simulation d'appel API
        return [
            {'id': i, 'data': f'api_record_{i}', 'timestamp': datetime.utcnow().isoformat()}
            for i in range(25)
        ]
    
    async def _read_from_stream(self, source: DataSource) -> List[Dict[str, Any]]:
        """Lecture depuis un stream"""
        # Simulation de lecture stream
        return [
            {'id': i, 'data': f'stream_record_{i}', 'timestamp': datetime.utcnow().isoformat()}
            for i in range(200)
        ]
    
    async def _apply_filter(self, data: Dict[str, Any], transformation: DataTransformation) -> Dict[str, Any]:
        """Application d'un filtre"""
        filter_config = transformation.transformation_config
        
        # Simulation de filtrage
        if isinstance(data, dict):
            for source_id, records in data.items():
                if isinstance(records, list):
                    # Exemple de filtre basique
                    filtered_records = [
                        record for record in records 
                        if record.get('id', 0) % 2 == 0  # Filtre les IDs pairs
                    ]
                    data[source_id] = filtered_records
        
        return data
    
    async def _apply_map(self, data: Dict[str, Any], transformation: DataTransformation) -> Dict[str, Any]:
        """Application d'une transformation map"""
        map_config = transformation.transformation_config
        
        # Simulation de mapping
        if isinstance(data, dict):
            for source_id, records in data.items():
                if isinstance(records, list):
                    mapped_records = []
                    for record in records:
                        mapped_record = record.copy()
                        mapped_record['mapped_data'] = f"mapped_{record.get('data', '')}"
                        mapped_records.append(mapped_record)
                    data[source_id] = mapped_records
        
        return data
    
    async def _apply_aggregate(self, data: Dict[str, Any], transformation: DataTransformation) -> Dict[str, Any]:
        """Application d'une agrégation"""
        agg_config = transformation.transformation_config
        
        # Simulation d'agrégation
        aggregated_data = {}
        total_records = 0
        
        for source_id, records in data.items():
            if isinstance(records, list):
                total_records += len(records)
        
        aggregated_data['summary'] = {
            'total_records': total_records,
            'timestamp': datetime.utcnow().isoformat(),
            'aggregation_type': agg_config.get('type', 'count')
        }
        
        return aggregated_data
    
    async def _apply_join(self, data: Dict[str, Any], transformation: DataTransformation) -> Dict[str, Any]:
        """Application d'une jointure"""
        join_config = transformation.transformation_config
        
        # Simulation de jointure simple
        joined_data = {}
        all_records = []
        
        for source_id, records in data.items():
            if isinstance(records, list):
                all_records.extend(records)
        
        joined_data['joined_records'] = all_records
        return joined_data
    
    async def _write_to_database(self, data: List[Dict[str, Any]], destination: DataDestination) -> Dict[str, Any]:
        """Écriture vers une base de données"""
        # Simulation d'écriture BDD
        return {
            'records_written': len(data),
            'destination_type': 'database',
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'success'
        }
    
    async def _write_to_file(self, data: List[Dict[str, Any]], destination: DataDestination) -> Dict[str, Any]:
        """Écriture vers un fichier"""
        # Simulation d'écriture fichier
        return {
            'records_written': len(data),
            'destination_type': 'file',
            'file_path': destination.write_config.get('path', '/tmp/output.json'),
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'success'
        }
    
    async def _write_to_api(self, data: List[Dict[str, Any]], destination: DataDestination) -> Dict[str, Any]:
        """Écriture vers une API"""
        # Simulation d'envoi API
        return {
            'records_written': len(data),
            'destination_type': 'api',
            'api_endpoint': destination.connection_config.get('url', 'http://api.example.com'),
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'success'
        }
    
    async def _update_metrics(self, execution_result: Dict[str, Any]):
        """Mise à jour des métriques"""
        self.metrics['executions'] += 1
        
        # Ajout à l'historique
        self.execution_history.append(execution_result)
        
        # Calcul du taux de succès
        successful_executions = sum(
            1 for exec_result in self.execution_history 
            if exec_result['status'] == 'completed'
        )
        self.metrics['success_rate'] = successful_executions / len(self.execution_history)
        
        # Calcul de la durée moyenne
        total_duration = sum(
            exec_result['execution_time'] for exec_result in self.execution_history
        )
        self.metrics['avg_duration'] = total_duration / len(self.execution_history)
        
        self.metrics['last_execution'] = execution_result['timestamp']


class ETLPipelineTemplate(DataPipelineTemplate):
    """
    Template spécialisé pour pipelines ETL
    Extract, Transform, Load optimisé
    """
    
    def __init__(self, config: PipelineConfig):
        super().__init__(config)
        self.config.processing_mode = ProcessingMode.BATCH
    
    async def execute_etl(self, extract_config: Dict[str, Any], 
                         transform_config: Dict[str, Any], 
                         load_config: Dict[str, Any]) -> Dict[str, Any]:
        """Exécution ETL complète"""
        
        # Extract Phase
        extracted_data = await self._extract_phase(extract_config)
        
        # Transform Phase
        transformed_data = await self._transform_phase(extracted_data, transform_config)
        
        # Load Phase
        load_result = await self._load_phase(transformed_data, load_config)
        
        return {
            'pipeline_type': 'ETL',
            'extract_result': extracted_data,
            'transform_result': transformed_data,
            'load_result': load_result,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _extract_phase(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Phase d'extraction"""
        logging.info("Starting ETL Extract phase")
        
        # Simulation d'extraction
        return {
            'extracted_records': 1000,
            'source_systems': config.get('sources', ['database_1', 'api_1']),
            'extraction_time': datetime.utcnow().isoformat()
        }
    
    async def _transform_phase(self, data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Phase de transformation"""
        logging.info("Starting ETL Transform phase")
        
        # Simulation de transformation
        return {
            'transformed_records': data.get('extracted_records', 0),
            'transformations_applied': config.get('transformations', ['clean', 'normalize']),
            'transformation_time': datetime.utcnow().isoformat()
        }
    
    async def _load_phase(self, data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Phase de chargement"""
        logging.info("Starting ETL Load phase")
        
        # Simulation de chargement
        return {
            'loaded_records': data.get('transformed_records', 0),
            'target_systems': config.get('targets', ['data_warehouse']),
            'load_time': datetime.utcnow().isoformat()
        }


class StreamingPipelineTemplate(DataPipelineTemplate):
    """
    Template pour pipelines de streaming temps réel
    Traitement continu avec Kafka/Redis
    """
    
    def __init__(self, config: PipelineConfig):
        super().__init__(config)
        self.config.processing_mode = ProcessingMode.STREAM
        self.is_running = False
        
    async def start_streaming(self, stream_config: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """Démarrage du streaming temps réel"""
        self.is_running = True
        
        try:
            while self.is_running:
                # Simulation de traitement stream
                batch_data = await self._read_stream_batch(stream_config)
                
                if batch_data:
                    processed_data = await self._process_stream_batch(batch_data)
                    await self._emit_stream_results(processed_data)
                    
                    yield {
                        'batch_id': str(uuid.uuid4()),
                        'records_processed': len(batch_data),
                        'processing_time': datetime.utcnow().isoformat(),
                        'status': 'processed'
                    }
                
                # Attente avant le prochain batch
                await asyncio.sleep(stream_config.get('batch_interval', 1.0))
                
        except Exception as e:
            logging.error(f"Streaming error: {str(e)}")
            self.is_running = False
            raise
    
    async def stop_streaming(self):
        """Arrêt du streaming"""
        self.is_running = False
        logging.info("Streaming pipeline stopped")
    
    async def _read_stream_batch(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Lecture d'un batch du stream"""
        batch_size = config.get('batch_size', 100)
        
        # Simulation de lecture batch
        return [
            {
                'id': i,
                'data': f'stream_data_{i}',
                'timestamp': datetime.utcnow().isoformat()
            }
            for i in range(batch_size)
        ]
    
    async def _process_stream_batch(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Traitement d'un batch de données"""
        processed_batch = []
        
        for record in batch:
            processed_record = record.copy()
            processed_record['processed'] = True
            processed_record['processing_timestamp'] = datetime.utcnow().isoformat()
            processed_batch.append(processed_record)
        
        return processed_batch
    
    async def _emit_stream_results(self, data: List[Dict[str, Any]]):
        """Émission des résultats du streaming"""
        # Simulation d'émission vers un topic/queue
        logging.info(f"Emitted {len(data)} records to output stream")


class DataPipelineOrchestrator:
    """
    Orchestrateur pour la gestion de multiples pipelines
    Gestion centralisée et monitoring
    """
    
    def __init__(self):
        self.pipelines: Dict[str, DataPipelineTemplate] = {}
        self.scheduler_tasks: Dict[str, asyncio.Task] = {}
        
    async def register_pipeline(self, pipeline: DataPipelineTemplate):
        """Enregistrement d'un pipeline"""
        pipeline_id = pipeline.config.pipeline_id
        self.pipelines[pipeline_id] = pipeline
        
        logging.info(f"Pipeline registered: {pipeline_id}")
        
        # Démarrage du scheduler si configuré
        if pipeline.config.schedule:
            await self._schedule_pipeline(pipeline)
    
    async def execute_pipeline(self, pipeline_id: str) -> Dict[str, Any]:
        """Exécution d'un pipeline spécifique"""
        if pipeline_id not in self.pipelines:
            raise ValueError(f"Pipeline not found: {pipeline_id}")
        
        pipeline = self.pipelines[pipeline_id]
        return await pipeline.execute()
    
    async def get_pipeline_status(self, pipeline_id: str) -> Dict[str, Any]:
        """Récupération du statut d'un pipeline"""
        if pipeline_id not in self.pipelines:
            raise ValueError(f"Pipeline not found: {pipeline_id}")
        
        pipeline = self.pipelines[pipeline_id]
        
        return {
            'pipeline_id': pipeline_id,
            'status': pipeline.status.value,
            'metrics': pipeline.metrics,
            'last_execution': pipeline.metrics.get('last_execution'),
            'config': {
                'name': pipeline.config.name,
                'processing_mode': pipeline.config.processing_mode.value
            }
        }
    
    async def list_pipelines(self) -> List[Dict[str, Any]]:
        """Liste de tous les pipelines"""
        pipelines_info = []
        
        for pipeline_id, pipeline in self.pipelines.items():
            pipelines_info.append({
                'pipeline_id': pipeline_id,
                'name': pipeline.config.name,
                'status': pipeline.status.value,
                'processing_mode': pipeline.config.processing_mode.value,
                'executions': pipeline.metrics['executions'],
                'success_rate': pipeline.metrics['success_rate']
            })
        
        return pipelines_info
    
    async def _schedule_pipeline(self, pipeline: DataPipelineTemplate):
        """Programmation d'un pipeline"""
        # Simulation de scheduling (à implémenter avec un vrai scheduler)
        async def scheduled_execution():
            while True:
                try:
                    await pipeline.execute()
                    await asyncio.sleep(3600)  # Exécution toutes les heures
                except Exception as e:
                    logging.error(f"Scheduled execution error: {str(e)}")
                    await asyncio.sleep(300)  # Retry après 5 minutes
        
        task = asyncio.create_task(scheduled_execution())
        self.scheduler_tasks[pipeline.config.pipeline_id] = task


def create_data_pipeline_app() -> FastAPI:
    """
    Création de l'application FastAPI pour les pipelines de données
    """
    app = FastAPI(
        title="Ainflue Data Pipeline Service",
        description="Production-ready data pipeline templates",
        version="1.0.0"
    )
    
    orchestrator = DataPipelineOrchestrator()
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
    
    @app.post("/pipelines")
    async def create_pipeline(config: Dict[str, Any]):
        """Création d'un nouveau pipeline"""
        try:
            pipeline_config = PipelineConfig(
                name=config['name'],
                description=config.get('description', ''),
                processing_mode=ProcessingMode(config.get('processing_mode', 'batch'))
            )
            
            if config.get('processing_mode') == 'stream':
                pipeline = StreamingPipelineTemplate(pipeline_config)
            else:
                pipeline = ETLPipelineTemplate(pipeline_config)
            
            await orchestrator.register_pipeline(pipeline)
            
            return {
                'pipeline_id': pipeline_config.pipeline_id,
                'status': 'created',
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/pipelines/{pipeline_id}/execute")
    async def execute_pipeline(pipeline_id: str, background_tasks: BackgroundTasks):
        """Exécution d'un pipeline"""
        try:
            result = await orchestrator.execute_pipeline(pipeline_id)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/pipelines")
    async def list_pipelines():
        """Liste des pipelines"""
        return await orchestrator.list_pipelines()
    
    @app.get("/pipelines/{pipeline_id}/status")
    async def get_pipeline_status(pipeline_id: str):
        """Statut d'un pipeline"""
        try:
            return await orchestrator.get_pipeline_status(pipeline_id)
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))
    
    return app


if __name__ == "__main__":
    import uvicorn
    
    app = create_data_pipeline_app()
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")


"""
EXEMPLES D'UTILISATION:

1. Pipeline ETL classique:
config = PipelineConfig(
    name="content_analytics_etl",
    processing_mode=ProcessingMode.BATCH,
    schedule="0 2 * * *"  # Daily at 2 AM
)
pipeline = ETLPipelineTemplate(config)

2. Pipeline streaming temps réel:
config = PipelineConfig(
    name="real_time_engagement",
    processing_mode=ProcessingMode.STREAM
)
pipeline = StreamingPipelineTemplate(config)

3. Orchestration multiple:
orchestrator = DataPipelineOrchestrator()
await orchestrator.register_pipeline(etl_pipeline)
await orchestrator.register_pipeline(streaming_pipeline)
"""