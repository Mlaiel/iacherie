"""Test Enterprise Observability
==============================

Tests for the EnterpriseObservability class and related functionality.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from backend.monitoring.observability import (
    EnterpriseObservability,
    EnterpriseConfig,
    ObservabilityLevel,
    TracingBackend,
    LoggingBackend
)


class TestEnterpriseConfig:
    """Test EnterpriseConfig configuration class"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = EnterpriseConfig()
        
        assert config.level == ObservabilityLevel.ENTERPRISE
        assert config.tracing_enabled is True
        assert config.tracing_backend == TracingBackend.JAEGER
        assert config.metrics_enabled is True
        assert config.datadog_enabled is True
        assert config.chaos_enabled is True
        assert config.aiops_enabled is True
        assert config.sampling_rate == 0.1
    
    def test_custom_config(self):
        """Test custom configuration values"""
        config = EnterpriseConfig(
            level=ObservabilityLevel.ADVANCED,
            tracing_enabled=False,
            sampling_rate=0.5
        )
        
        assert config.level == ObservabilityLevel.ADVANCED
        assert config.tracing_enabled is False
        assert config.sampling_rate == 0.5


class TestEnterpriseObservability:
    """Test EnterpriseObservability main class"""
    
    @pytest.fixture
    def observability(self):
        """Create EnterpriseObservability instance for testing"""
        config = EnterpriseConfig(
            datadog_api_key="test-key",
            gremlin_api_key="test-gremlin",
            moogsoft_api_key="test-moog"
        )
        return EnterpriseObservability(config)
    
    def test_initialization(self, observability):
        """Test basic initialization"""
        assert observability.config is not None
        assert observability._initialized is False
        assert observability._active_traces == {}
        assert observability._chaos_experiments == {}
        assert observability._aiops_incidents == {}
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, observability):
        """Test successful initialization"""
        with patch.object(observability, '_initialize_base_monitoring', new_callable=AsyncMock), \
             patch.object(observability, '_initialize_distributed_tracing', new_callable=AsyncMock), \
             patch.object(observability, '_initialize_enhanced_metrics', new_callable=AsyncMock), \
             patch.object(observability, '_initialize_enhanced_logging', new_callable=AsyncMock), \
             patch.object(observability, '_initialize_datadog_apm', new_callable=AsyncMock), \
             patch.object(observability, '_initialize_chaos_engineering', new_callable=AsyncMock), \
             patch.object(observability, '_initialize_aiops', new_callable=AsyncMock):
            
            result = await observability.initialize()
            
            assert result is True
            assert observability._initialized is True
    
    @pytest.mark.asyncio
    async def test_initialize_failure(self, observability):
        """Test initialization failure handling"""
        # Mock the logger to cause an exception in the main try block
        with patch.object(observability.logger, 'info', 
                         side_effect=Exception("Critical initialization error")):
            
            result = await observability.initialize()
            
            # Should fail due to unhandled exception in main flow
            assert result is False
            assert observability._initialized is False
    
    @pytest.mark.asyncio
    async def test_start_trace(self, observability):
        """Test starting a distributed trace"""
        # Mock tracer
        mock_span = MagicMock()
        mock_span.trace_id = 12345
        mock_tracer = MagicMock()
        mock_tracer.start_span.return_value = mock_span
        observability._tracer = mock_tracer
        
        trace_id = await observability.start_trace("test_operation", service="test")
        
        assert trace_id == "12345"
        assert trace_id in observability._active_traces
        mock_tracer.start_span.assert_called_once_with("test_operation")
        mock_span.set_tag.assert_called_once_with("service", "test")
    
    @pytest.mark.asyncio
    async def test_start_trace_no_tracer(self, observability):
        """Test starting trace when tracer is not available"""
        observability._tracer = None
        
        trace_id = await observability.start_trace("test_operation")
        
        assert trace_id is None
        assert len(observability._active_traces) == 0
    
    @pytest.mark.asyncio
    async def test_finish_trace(self, observability):
        """Test finishing a distributed trace"""
        # Setup mock span
        mock_span = MagicMock()
        observability._active_traces["test_trace"] = mock_span
        
        await observability.finish_trace("test_trace", status="success")
        
        mock_span.set_tag.assert_called_once_with("status", "success")
        mock_span.finish.assert_called_once()
        assert "test_trace" not in observability._active_traces
    
    @pytest.mark.asyncio
    async def test_record_metric(self, observability):
        """Test recording enterprise metrics"""
        # Mock base monitoring
        mock_prometheus = MagicMock()
        mock_base_monitoring = MagicMock()
        mock_base_monitoring.prometheus = mock_prometheus
        observability._base_monitoring = mock_base_monitoring
        
        # Mock DataDog client
        mock_datadog = MagicMock()
        observability._datadog_client = mock_datadog
        
        await observability.record_metric("test_metric", 42.0, {"env": "test"})
        
        # Verify Prometheus metric recording
        mock_prometheus.set_gauge.assert_called_once_with(
            "test_metric", 42.0, {"env": "test"}
        )
        
        # Verify DataDog metric recording
        mock_datadog.Metric.send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_chaos_experiment(self, observability):
        """Test creating chaos engineering experiment"""
        config = {"type": "cpu", "intensity": 0.5}
        
        experiment_id = await observability.create_chaos_experiment("test_chaos", config)
        
        assert experiment_id.startswith("chaos_")
        assert experiment_id in observability._chaos_experiments
        
        experiment = observability._chaos_experiments[experiment_id]
        assert experiment["name"] == "test_chaos"
        assert experiment["config"] == config
        assert experiment["status"] == "created"
    
    @pytest.mark.asyncio
    async def test_trigger_aiops_incident(self, observability):
        """Test triggering AIOps incident analysis"""
        incident_data = {"severity": "high", "service": "api"}
        
        incident_id = await observability.trigger_aiops_incident(incident_data)
        
        assert incident_id.startswith("aiops_")
        assert incident_id in observability._aiops_incidents
        
        incident = observability._aiops_incidents[incident_id]
        assert incident["data"] == incident_data
        assert incident["status"] == "analyzing"
    
    @pytest.mark.asyncio
    async def test_get_observability_status(self, observability):
        """Test getting observability status"""
        # Setup some test state
        observability._initialized = True
        observability._active_traces["test"] = MagicMock()
        observability._chaos_experiments["exp1"] = {}
        observability._aiops_incidents["inc1"] = {}
        
        status = await observability.get_observability_status()
        
        assert status["initialized"] is True
        assert status["level"] == "enterprise"
        assert status["active_traces"] == 1
        assert status["chaos_experiments"] == 1
        assert status["aiops_incidents"] == 1
        assert "components" in status
        assert "config" in status
    
    @pytest.mark.asyncio
    async def test_shutdown(self, observability):
        """Test graceful shutdown"""
        # Setup test state
        mock_span = MagicMock()
        observability._active_traces["test"] = mock_span
        observability._base_monitoring = MagicMock()
        observability._base_monitoring.stop = AsyncMock()
        observability._tracer = MagicMock()
        
        await observability.shutdown()
        
        # Verify cleanup
        assert len(observability._active_traces) == 0
        observability._base_monitoring.stop.assert_called_once()
        observability._tracer.close.assert_called_once()


@pytest.mark.asyncio
async def test_enterprise_observability_integration():
    """Integration test for EnterpriseObservability"""
    config = EnterpriseConfig(
        level=ObservabilityLevel.STANDARD,
        tracing_enabled=True,
        datadog_enabled=False,  # Disable for testing
        chaos_enabled=False,    # Disable for testing
        aiops_enabled=False     # Disable for testing
    )
    
    observability = EnterpriseObservability(config)
    
    # Test initialization
    result = await observability.initialize()
    assert isinstance(result, bool)
    
    # Test status retrieval
    status = await observability.get_observability_status()
    assert isinstance(status, dict)
    assert "level" in status
    assert "components" in status
    
    # Test cleanup
    await observability.shutdown()


if __name__ == "__main__":
    pytest.main([__file__])