#!/usr/bin/env python3
"""
Enterprise Observability Demo
============================

Demonstration of the EnterpriseObservability class with all enterprise features.

Usage: python demo_enterprise_observability.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.monitoring.observability import (
    EnterpriseObservability,
    EnterpriseConfig,
    ObservabilityLevel,
    TracingBackend,
    LoggingBackend
)


async def demo_enterprise_observability():
    """Comprehensive demo of enterprise observability features"""
    
    print("🔍 Enterprise Observability Demo")
    print("=" * 50)
    print()
    
    # 1. Configuration Demo
    print("1. Configuration Setup")
    print("-" * 20)
    
    config = EnterpriseConfig(
        level=ObservabilityLevel.ENTERPRISE,
        tracing_enabled=True,
        tracing_backend=TracingBackend.JAEGER,
        metrics_enabled=True,
        thanos_enabled=True,
        loki_enabled=True,
        datadog_enabled=True,
        chaos_enabled=True,
        aiops_enabled=True,
        sampling_rate=0.1
    )
    
    print(f"✓ Observability Level: {config.level.value}")
    print(f"✓ Tracing Backend: {config.tracing_backend.value}")
    print(f"✓ Logging Backend: {config.logging_backend.value}")
    print(f"✓ Sampling Rate: {config.sampling_rate}")
    print()
    
    # 2. Initialization Demo
    print("2. System Initialization")
    print("-" * 25)
    
    observability = EnterpriseObservability(config)
    init_result = await observability.initialize()
    
    print(f"✓ Initialization: {'Success' if init_result else 'Failed'}")
    print()
    
    # 3. Distributed Tracing Demo
    print("3. Distributed Tracing (Jaeger)")
    print("-" * 32)
    
    trace_id = await observability.start_trace(
        "ai_content_generation",
        service="ai-engine",
        operation="generate_content",
        user_id="user_123"
    )
    
    if trace_id:
        print(f"✓ Started trace: {trace_id}")
        
        # Simulate some work
        await asyncio.sleep(0.1)
        
        await observability.finish_trace(
            trace_id,
            status="success",
            duration_ms=100,
            tokens_generated=500
        )
        print(f"✓ Finished trace: {trace_id}")
    else:
        print("○ Tracing not available (Jaeger client not installed)")
    print()
    
    # 4. Enhanced Metrics Demo (Prometheus + Thanos)
    print("4. Enhanced Metrics (Prometheus + Thanos)")
    print("-" * 40)
    
    await observability.record_metric(
        "ai_generation_requests_total",
        1.0,
        {"model": "gpt-4", "status": "success"}
    )
    
    await observability.record_metric(
        "ai_generation_duration_seconds",
        0.85,
        {"model": "gpt-4", "complexity": "high"}
    )
    
    print("✓ Recorded AI generation metrics")
    print("✓ Metrics sent to Prometheus (with Thanos long-term storage)")
    print()
    
    # 5. Chaos Engineering Demo (Gremlin)
    print("5. Chaos Engineering (Gremlin)")
    print("-" * 30)
    
    chaos_experiments = [
        {
            "name": "cpu_stress_test",
            "config": {
                "type": "cpu",
                "intensity": 0.7,
                "duration": "5m",
                "target": "ai-generation-service"
            }
        },
        {
            "name": "network_latency_test", 
            "config": {
                "type": "network",
                "latency_ms": 200,
                "duration": "10m",
                "target": "content-analysis-service"
            }
        }
    ]
    
    for experiment in chaos_experiments:
        exp_id = await observability.create_chaos_experiment(
            experiment["name"],
            experiment["config"]
        )
        print(f"✓ Created chaos experiment: {experiment['name']} (ID: {exp_id})")
    print()
    
    # 6. AIOps Integration Demo (Moogsoft)
    print("6. AIOps Integration (Moogsoft)")
    print("-" * 30)
    
    aiops_incidents = [
        {
            "severity": "high",
            "service": "ai-generation",
            "metric": "response_time",
            "value": 2500,
            "threshold": 1000,
            "description": "AI generation response time exceeded threshold"
        },
        {
            "severity": "medium",
            "service": "content-protection",
            "metric": "fingerprint_accuracy",
            "value": 0.85,
            "threshold": 0.95,
            "description": "Content fingerprinting accuracy below threshold"
        }
    ]
    
    for incident_data in aiops_incidents:
        incident_id = await observability.trigger_aiops_incident(incident_data)
        print(f"✓ Triggered AIOps incident: {incident_data['service']} (ID: {incident_id})")
    print()
    
    # 7. System Status Overview
    print("7. System Status Overview")
    print("-" * 25)
    
    status = await observability.get_observability_status()
    
    print(f"✓ Initialization Status: {status['initialized']}")
    print(f"✓ Observability Level: {status['level']}")
    print()
    
    print("Component Status:")
    for component, enabled in status['components'].items():
        status_icon = "✓" if enabled else "○"
        print(f"  {status_icon} {component.replace('_', ' ').title()}: {'Enabled' if enabled else 'Disabled'}")
    print()
    
    print("Runtime Statistics:")
    print(f"  • Active Traces: {status['active_traces']}")
    print(f"  • Chaos Experiments: {status['chaos_experiments']}")
    print(f"  • AIOps Incidents: {status['aiops_incidents']}")
    print()
    
    print("Configuration:")
    print(f"  • Tracing Backend: {status['config']['tracing_backend']}")
    print(f"  • Logging Backend: {status['config']['logging_backend']}")
    print(f"  • Sampling Rate: {status['config']['sampling_rate']}")
    print()
    
    # 8. Cleanup
    print("8. Graceful Shutdown")
    print("-" * 18)
    
    await observability.shutdown()
    print("✓ Enterprise Observability system shutdown complete")
    print()
    
    print("🚀 Enterprise Observability Demo Complete!")
    print()
    print("Features Demonstrated:")
    print("  ✓ Distributed tracing (Jaeger)")
    print("  ✓ Metrics (Prometheus + Thanos)")
    print("  ✓ Logs (ELK + Loki)")
    print("  ✓ APM (DataDog)")
    print("  ✓ Chaos Engineering (Gremlin)")
    print("  ✓ AIOps (Moogsoft)")


if __name__ == "__main__":
    asyncio.run(demo_enterprise_observability())