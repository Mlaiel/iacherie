"""
IA Influencer Agent - Fluentd Manager
Advanced Fluentd integration for log forwarding and processing

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

WARNING: This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit 
written permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import json
import logging
import yaml
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import aiohttp
import aiofiles
from jinja2 import Template

from ...core.config import settings
from ...core.exceptions import LoggingError, FluentdError
from .log_aggregator import LogEntry, LogLevel


class FluentdInputType(str, Enum):
    """Fluentd input plugin types"""
    FORWARD = "forward"
    HTTP = "http"
    TCP = "tcp"
    UDP = "udp"
    SYSLOG = "syslog"
    TAIL = "tail"
    EXEC = "exec"


class FluentdOutputType(str, Enum):
    """Fluentd output plugin types"""
    ELASTICSEARCH = "elasticsearch"
    S3 = "s3"
    KAFKA = "kafka"
    MONGODB = "mongodb"
    FILE = "file"
    FORWARD = "forward"
    CLOUDWATCH = "cloudwatch_logs"
    DATADOG = "datadog"


class FluentdFilterType(str, Enum):
    """Fluentd filter plugin types"""
    RECORD_TRANSFORMER = "record_transformer"
    GREP = "grep"
    PARSER = "parser"
    KUBERNETES_METADATA = "kubernetes_metadata_filter"
    PROMETHEUS = "prometheus"


@dataclass
class FluentdConfig:
    """Fluentd configuration"""
    host: str = "localhost"
    port: int = 24224
    buffer_chunk_limit: str = "2M"
    buffer_queue_limit: int = 32
    flush_interval: str = "60s"
    retry_limit: int = 17
    retry_wait: str = "1s"
    max_retry_wait: str = "131072s"
    disable_retry_limit: bool = False
    num_threads: int = 1


class FluentdSourceConfig:
    """Fluentd source configuration builder"""
    
    def __init__(self, input_type: FluentdInputType, tag: str):
        self.input_type = input_type
        self.tag = tag
        self.config = {"@type": input_type.value, "tag": tag}
    
    def set_port(self, port: int):
        """Set port for network inputs"""
        self.config["port"] = port
        return self
    
    def set_bind(self, bind: str):
        """Set bind address"""
        self.config["bind"] = bind
        return self
    
    def set_path(self, path: str):
        """Set path for file-based inputs"""
        self.config["path"] = path
        return self
    
    def set_format(self, format_type: str, **format_options):
        """Set input format"""
        self.config["format"] = format_type
        self.config.update(format_options)
        return self
    
    def set_parser(self, parser_config: Dict[str, Any]):
        """Set parser configuration"""
        self.config["parse"] = parser_config
        return self
    
    def add_custom_config(self, key: str, value: Any):
        """Add custom configuration"""
        self.config[key] = value
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build source configuration"""
        return self.config


class FluentdMatchConfig:
    """Fluentd match configuration builder"""
    
    def __init__(self, pattern: str, output_type: FluentdOutputType):
        self.pattern = pattern
        self.output_type = output_type
        self.config = {"@type": output_type.value}
        self.buffer_config = {}
    
    def set_elasticsearch_config(self, hosts: List[str], index_name: str = "fluentd"):
        """Configure Elasticsearch output"""
        self.config.update({
            "hosts": ",".join(hosts),
            "index_name": index_name,
            "type_name": "_doc"
        })
        return self
    
    def set_s3_config(self, bucket: str, region: str, path: str = "logs/"):
        """Configure S3 output"""
        self.config.update({
            "s3_bucket": bucket,
            "s3_region": region,
            "path": path,
            "s3_object_key_format": "%{path}%{time_slice}_%{index}.%{file_extension}",
            "time_slice_format": "%Y%m%d%H"
        })
        return self
    
    def set_kafka_config(self, brokers: List[str], topic: str):
        """Configure Kafka output"""
        self.config.update({
            "brokers": ",".join(brokers),
            "default_topic": topic,
            "output_data_type": "json"
        })
        return self
    
    def set_file_config(self, path: str, append: bool = True):
        """Configure file output"""
        self.config.update({
            "path": path,
            "append": append,
            "format": "json"
        })
        return self
    
    def set_buffer_config(self, 
                         type_: str = "file",
                         path: Optional[str] = None,
                         chunk_limit_size: str = "2M",
                         queue_limit_length: int = 32,
                         flush_interval: str = "60s",
                         retry_type: str = "exponential_backoff"):
        """Configure buffer settings"""
        self.buffer_config = {
            "@type": type_,
            "chunk_limit_size": chunk_limit_size,
            "queue_limit_length": queue_limit_length,
            "flush_interval": flush_interval,
            "retry_type": retry_type
        }
        
        if path:
            self.buffer_config["path"] = path
        
        return self
    
    def set_format_config(self, format_type: str = "json"):
        """Set output format"""
        self.config["format"] = {"@type": format_type}
        return self
    
    def add_custom_config(self, key: str, value: Any):
        """Add custom configuration"""
        self.config[key] = value
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build match configuration"""
        config = {"@type": self.output_type.value}
        config.update(self.config)
        
        if self.buffer_config:
            config["buffer"] = self.buffer_config
        
        return config


class FluentdFilterConfig:
    """Fluentd filter configuration builder"""
    
    def __init__(self, pattern: str, filter_type: FluentdFilterType):
        self.pattern = pattern
        self.filter_type = filter_type
        self.config = {"@type": filter_type.value}
    
    def set_record_transformer(self, 
                              enable_ruby: bool = False,
                              auto_typecast: bool = True,
                              record_transforms: Optional[Dict[str, str]] = None,
                              remove_keys: Optional[List[str]] = None):
        """Configure record transformer filter"""
        self.config.update({
            "enable_ruby": enable_ruby,
            "auto_typecast": auto_typecast
        })
        
        if record_transforms:
            self.config["record"] = record_transforms
        
        if remove_keys:
            self.config["remove_keys"] = ",".join(remove_keys)
        
        return self
    
    def set_grep_filter(self, 
                       regexps: Optional[List[Dict[str, str]]] = None,
                       excludes: Optional[List[Dict[str, str]]] = None):
        """Configure grep filter"""
        if regexps:
            self.config["regexp"] = regexps
        
        if excludes:
            self.config["exclude"] = excludes
        
        return self
    
    def set_parser_filter(self, 
                         key_name: str,
                         parser_type: str,
                         format: str,
                         reserve_data: bool = True):
        """Configure parser filter"""
        self.config.update({
            "key_name": key_name,
            "reserve_data": reserve_data,
            "parse": {
                "@type": parser_type,
                "format": format
            }
        })
        return self
    
    def add_custom_config(self, key: str, value: Any):
        """Add custom configuration"""
        self.config[key] = value
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build filter configuration"""
        return self.config


class FluentdConfigBuilder:
    """Complete Fluentd configuration builder"""
    
    def __init__(self):
        self.sources = []
        self.filters = []
        self.matches = []
        self.includes = []
        self.system_config = {}
    
    def add_source(self, source_config: FluentdSourceConfig):
        """Add source configuration"""
        self.sources.append(source_config.build())
        return self
    
    def add_filter(self, pattern: str, filter_config: FluentdFilterConfig):
        """Add filter configuration"""
        config = filter_config.build()
        self.filters.append({
            "pattern": pattern,
            "config": config
        })
        return self
    
    def add_match(self, pattern: str, match_config: FluentdMatchConfig):
        """Add match configuration"""
        config = match_config.build()
        self.matches.append({
            "pattern": pattern,
            "config": config
        })
        return self
    
    def add_include(self, path: str):
        """Add include directive"""
        self.includes.append(path)
        return self
    
    def set_system_config(self, 
                         workers: int = 1,
                         root_dir: str = "/var/log/fluentd",
                         log_level: str = "info"):
        """Set system configuration"""
        self.system_config = {
            "workers": workers,
            "root_dir": root_dir,
            "log_level": log_level
        }
        return self
    
    def build_yaml(self) -> str:
        """Build complete Fluentd configuration as YAML"""
        config = {}
        
        # System configuration
        if self.system_config:
            config["system"] = self.system_config
        
        # Includes
        if self.includes:
            config["@include"] = self.includes
        
        # Build complete configuration
        full_config = []
        
        # Add sources
        for source in self.sources:
            full_config.append({"source": source})
        
        # Add filters
        for filter_item in self.filters:
            filter_block = {"filter": filter_item["config"]}
            filter_block["filter"]["tag"] = filter_item["pattern"]
            full_config.append(filter_block)
        
        # Add matches
        for match_item in self.matches:
            match_block = {"match": match_item["config"]}
            match_block["match"]["tag"] = match_item["pattern"]
            full_config.append(match_block)
        
        # Combine system config with main config
        if config:
            full_config.insert(0, config)
        
        return yaml.dump(full_config, default_flow_style=False, sort_keys=False)


class FluentdClient:
    """HTTP client for Fluentd forward protocol"""
    
    def __init__(self, host: str = "localhost", port: int = 24224):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def connect(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
    
    async def disconnect(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
    
    async def send_log(self, tag: str, record: Dict[str, Any], timestamp: Optional[int] = None) -> bool:
        """Send single log record to Fluentd"""
        if not self.session:
            await self.connect()
        
        if timestamp is None:
            timestamp = int(datetime.now(timezone.utc).timestamp())
        
        data = [tag, timestamp, record]
        
        try:
            async with self.session.post(
                f"{self.base_url}/{tag}",
                json=record,
                headers={"Content-Type": "application/json"}
            ) as response:
                return response.status == 200
        
        except Exception as e:
            logging.error(f"Failed to send log to Fluentd: {e}")
            return False
    
    async def send_logs_batch(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Send batch of logs to Fluentd"""
        if not self.session:
            await self.connect()
        
        success_count = 0
        error_count = 0
        errors = []
        
        for log_data in logs:
            tag = log_data.get("tag", "app.default")
            record = log_data.get("record", {})
            timestamp = log_data.get("timestamp")
            
            success = await self.send_log(tag, record, timestamp)
            if success:
                success_count += 1
            else:
                error_count += 1
                errors.append(f"Failed to send log with tag: {tag}")
        
        return {
            "success": success_count,
            "errors": error_count,
            "error_details": errors
        }


class FluentdManager:
    """Advanced Fluentd manager for IA Influencer Agent"""
    
    def __init__(self, config: FluentdConfig):
        self.config = config
        self.client = FluentdClient(config.host, config.port)
        self.config_builder = FluentdConfigBuilder()
        self.is_running = False
        self._setup_default_configuration()
    
    def _setup_default_configuration(self):
        """Setup default Fluentd configuration for IA Influencer Agent"""
        
        # System configuration
        self.config_builder.set_system_config(
            workers=1,
            root_dir="/var/log/fluentd",
            log_level="info"
        )
        
        # Source for HTTP input (API logs)
        http_source = (FluentdSourceConfig(FluentdInputType.HTTP, "ia.api.**")
                      .set_port(9880)
                      .set_bind("0.0.0.0")
                      .set_format("json"))
        
        self.config_builder.add_source(http_source)
        
        # Source for forward input (application logs)
        forward_source = (FluentdSourceConfig(FluentdInputType.FORWARD, "ia.app.**")
                         .set_port(24224)
                         .set_bind("0.0.0.0"))
        
        self.config_builder.add_source(forward_source)
        
        # Source for file tail (container logs)
        file_source = (FluentdSourceConfig(FluentdInputType.TAIL, "ia.container.**")
                      .set_path("/var/log/containers/*.log")
                      .set_format("json")
                      .add_custom_config("pos_file", "/var/log/fluentd/containers.log.pos")
                      .add_custom_config("read_from_head", True))
        
        self.config_builder.add_source(file_source)
        
        # Filter to add metadata
        metadata_filter = FluentdFilterConfig("ia.**", FluentdFilterType.RECORD_TRANSFORMER)
        metadata_filter.set_record_transformer(
            record_transforms={
                "hostname": "${hostname}",
                "environment": "${ENV['ENVIRONMENT']}",
                "service_version": "${ENV['SERVICE_VERSION']}",
                "region": "${ENV['AWS_REGION']}"
            }
        )
        
        self.config_builder.add_filter("ia.**", metadata_filter)
        
        # Filter to parse and enrich AI-specific logs
        ai_filter = FluentdFilterConfig("ia.ai.**", FluentdFilterType.RECORD_TRANSFORMER)
        ai_filter.set_record_transformer(
            record_transforms={
                "log_type": "ai_processing",
                "processing_pipeline": "${record['metadata']['pipeline'] || 'unknown'}",
                "model_version": "${record['metadata']['model_version'] || 'unknown'}"
            }
        )
        
        self.config_builder.add_filter("ia.ai.**", ai_filter)
        
        # Filter to parse fingerprinting logs
        fingerprint_filter = FluentdFilterConfig("ia.fingerprint.**", FluentdFilterType.RECORD_TRANSFORMER)
        fingerprint_filter.set_record_transformer(
            record_transforms={
                "log_type": "fingerprinting",
                "content_type": "${record['metadata']['content_type'] || 'unknown'}",
                "fingerprint_algorithm": "${record['metadata']['algorithm'] || 'unknown'}"
            }
        )
        
        self.config_builder.add_filter("ia.fingerprint.**", fingerprint_filter)
        
        # Filter for error detection and alerting
        error_filter = FluentdFilterConfig("ia.**", FluentdFilterType.GREP)
        error_filter.set_grep_filter(regexps=[
            {"key": "level", "pattern": "ERROR|CRITICAL"}
        ])
        
        self.config_builder.add_filter("ia.error", error_filter)
        
        # Match for Elasticsearch output
        es_match = FluentdMatchConfig("ia.**", FluentdOutputType.ELASTICSEARCH)
        es_match.set_elasticsearch_config(
            hosts=["elasticsearch:9200"],
            index_name="ia-influencer-${Time.at(time).strftime('%Y.%m.%d')}"
        )
        es_match.set_buffer_config(
            type_="file",
            path="/var/log/fluentd/buffers/elasticsearch",
            chunk_limit_size="2M",
            queue_limit_length=32,
            flush_interval="60s"
        )
        
        self.config_builder.add_match("ia.**", es_match)
        
        # Match for S3 backup
        s3_match = FluentdMatchConfig("ia.**", FluentdOutputType.S3)
        s3_match.set_s3_config(
            bucket="ia-influencer-logs",
            region="eu-central-1",
            path="logs/${Time.at(time).strftime('%Y/%m/%d')}/"
        )
        s3_match.set_buffer_config(
            type_="file",
            path="/var/log/fluentd/buffers/s3",
            chunk_limit_size="10M",
            queue_limit_length=16,
            flush_interval="300s"
        )
        
        self.config_builder.add_match("ia.backup.**", s3_match)
        
        # Match for error alerts
        alert_match = FluentdMatchConfig("ia.error", FluentdOutputType.HTTP)
        alert_match.add_custom_config("endpoint", "http://alertmanager:9093/api/v1/alerts")
        alert_match.add_custom_config("http_method", "post")
        alert_match.set_format_config("json")
        
        self.config_builder.add_match("ia.error", alert_match)
    
    async def start(self):
        """Start Fluentd manager"""
        await self.client.connect()
        self.is_running = True
        logging.info("Fluentd manager started")
    
    async def stop(self):
        """Stop Fluentd manager"""
        await self.client.disconnect()
        self.is_running = False
        logging.info("Fluentd manager stopped")
    
    async def send_log_entry(self, log_entry: LogEntry, tag_prefix: str = "ia") -> bool:
        """Send log entry to Fluentd"""
        if not self.is_running:
            raise FluentdError("Fluentd manager not running")
        
        # Generate appropriate tag based on log content
        tag_parts = [tag_prefix]
        
        if log_entry.service:
            tag_parts.append(log_entry.service.lower())
        
        if log_entry.module:
            tag_parts.append(log_entry.module.lower())
        
        tag = ".".join(tag_parts)
        
        # Convert log entry to record
        record = log_entry.to_dict()
        timestamp = int(log_entry.timestamp.timestamp())
        
        return await self.client.send_log(tag, record, timestamp)
    
    async def send_log_entries_batch(self, log_entries: List[LogEntry], tag_prefix: str = "ia") -> Dict[str, Any]:
        """Send batch of log entries to Fluentd"""
        if not self.is_running:
            raise FluentdError("Fluentd manager not running")
        
        logs = []
        for log_entry in log_entries:
            # Generate tag
            tag_parts = [tag_prefix]
            
            if log_entry.service:
                tag_parts.append(log_entry.service.lower())
            
            if log_entry.module:
                tag_parts.append(log_entry.module.lower())
            
            tag = ".".join(tag_parts)
            
            logs.append({
                "tag": tag,
                "record": log_entry.to_dict(),
                "timestamp": int(log_entry.timestamp.timestamp())
            })
        
        return await self.client.send_logs_batch(logs)
    
    def get_configuration(self) -> str:
        """Get complete Fluentd configuration as YAML"""
        return self.config_builder.build_yaml()
    
    async def save_configuration(self, file_path: str):
        """Save Fluentd configuration to file"""
        config_yaml = self.get_configuration()
        
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(config_yaml)
        
        logging.info(f"Fluentd configuration saved to {file_path}")
    
    def add_custom_source(self, source_config: FluentdSourceConfig):
        """Add custom source configuration"""
        self.config_builder.add_source(source_config)
    
    def add_custom_filter(self, pattern: str, filter_config: FluentdFilterConfig):
        """Add custom filter configuration"""
        self.config_builder.add_filter(pattern, filter_config)
    
    def add_custom_match(self, pattern: str, match_config: FluentdMatchConfig):
        """Add custom match configuration"""
        self.config_builder.add_match(pattern, match_config)
    
    async def validate_configuration(self) -> Dict[str, Any]:
        """Validate Fluentd configuration"""
        try:
            config_yaml = self.get_configuration()
            
            # Basic YAML validation
            yaml.safe_load(config_yaml)
            
            # Additional validation could be added here
            # e.g., check for required plugins, validate syntax
            
            return {
                "valid": True,
                "message": "Configuration is valid",
                "warnings": []
            }
        
        except yaml.YAMLError as e:
            return {
                "valid": False,
                "message": f"YAML syntax error: {e}",
                "warnings": []
            }
        
        except Exception as e:
            return {
                "valid": False,
                "message": f"Configuration error: {e}",
                "warnings": []
            }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get Fluentd metrics and statistics"""
        # This would typically query Fluentd's metrics endpoint
        # For now, return basic connection status
        
        try:
            # Try to send a test log to check connectivity
            test_log = LogEntry(
                timestamp=datetime.now(timezone.utc),
                level=LogLevel.INFO,
                message="Fluentd connectivity test",
                service="fluentd_manager",
                module="metrics"
            )
            
            success = await self.send_log_entry(test_log, "ia.test")
            
            return {
                "status": "healthy" if success else "unhealthy",
                "connectivity": success,
                "configuration_valid": await self.validate_configuration(),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        except Exception as e:
            return {
                "status": "error",
                "connectivity": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
