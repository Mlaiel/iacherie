# Circuit Breakers Service

## Overview
Enterprise circuit breaker pattern implementation for microservices resilience and failure isolation.

## Features
- Automatic failure detection and isolation
- Configurable failure thresholds and timeouts
- Real-time monitoring and alerting
- Fast recovery and self-healing capabilities
- Integration with service mesh and API gateway

## Usage
```python
from microservices.circuit_breakers import circuit_breaker_service

# Register a circuit breaker
await circuit_breaker_service.create_circuit("user-service")

# Execute with circuit breaker protection
result = await circuit_breaker_service.call_with_circuit_breaker(
    "user-service", 
    your_function,
    *args,
    **kwargs
)
```

## Configuration
- `failure_threshold`: Number of failures before opening circuit (default: 5)
- `timeout_seconds`: Circuit open timeout (default: 60)
- `recovery_timeout`: Time before attempting reset (default: 30)
- `success_threshold`: Successes needed to close circuit (default: 2)

## Author
Fahed Mlaiel (mlaiel@live.de)

## Copyright
© 2025 Fahed Mlaiel. All rights reserved.