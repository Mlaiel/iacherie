"""
🔮 EDGE & QUANTUM COMPUTING ROUTES - Complete Implementation
===========================================================
ALL 20 endpoints for edge deployment, quantum computing, hybrid processing
Author: Fahed Mlaiel
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

router = APIRouter(prefix="/edge-quantum", tags=["Edge & Quantum Computing"])

# ============================================================================
# MODELS
# ============================================================================

class EdgeDeviceType(str, Enum):
    MOBILE = "mobile"
    IOT = "iot"
    EMBEDDED = "embedded"
    GATEWAY = "gateway"

class QuantumBackend(str, Enum):
    IBM = "ibm"
    GOOGLE = "google"
    AWS = "aws"
    SIMULATOR = "simulator"

# ============================================================================
# EDGE DEVICES
# ============================================================================

@router.post("/edge/devices/register")
async def register_edge_device(
    device_id: str,
    device_type: EdgeDeviceType,
    capabilities: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None
):
    """Register edge device"""
    try:
        from backend.edge.edge_manager import EdgeManager
        manager = EdgeManager()
        await manager.initialize()
        
        device = await manager.register_device(device_id, device_type.value, capabilities, metadata or {})
        return {"message": "Device registered", "device": device}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/edge/devices")
async def list_edge_devices(device_type: Optional[EdgeDeviceType] = None, online_only: bool = False):
    """List edge devices"""
    try:
        from backend.edge.edge_manager import EdgeManager
        manager = EdgeManager()
        await manager.initialize()
        
        type_val = device_type.value if device_type else None
        devices = await manager.list_devices(type_val, online_only)
        return {"devices": devices}
    except Exception as e:
        return {"devices": [], "error": str(e)}

@router.get("/edge/devices/{device_id}")
async def get_edge_device(device_id: str):
    """Get edge device details"""
    try:
        from backend.edge.edge_manager import EdgeManager
        manager = EdgeManager()
        await manager.initialize()
        
        device = await manager.get_device(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        return device
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/edge/devices/{device_id}/status")
async def get_device_status(device_id: str):
    """Get edge device status"""
    try:
        from backend.edge.edge_manager import EdgeManager
        manager = EdgeManager()
        await manager.initialize()
        
        status = await manager.get_device_status(device_id)
        return {"device_id": device_id, "status": status}
    except Exception as e:
        return {"device_id": device_id, "status": "unknown", "error": str(e)}

@router.delete("/edge/devices/{device_id}")
async def unregister_edge_device(device_id: str):
    """Unregister edge device"""
    try:
        from backend.edge.edge_manager import EdgeManager
        manager = EdgeManager()
        await manager.initialize()
        
        await manager.unregister_device(device_id)
        return {"message": "Device unregistered", "device_id": device_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# EDGE DEPLOYMENT
# ============================================================================

@router.post("/edge/deploy")
async def deploy_to_edge(
    model_id: str,
    device_ids: List[str],
    config: Optional[Dict[str, Any]] = None
):
    """Deploy model to edge devices"""
    try:
        from backend.edge.edge_deployment import EdgeDeployment
        deployment = EdgeDeployment()
        await deployment.initialize()
        
        result = await deployment.deploy_model(model_id, device_ids, config or {})
        return {"message": "Model deployed to edge devices", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/edge/deployments")
async def list_edge_deployments():
    """List edge deployments"""
    try:
        from backend.edge.edge_deployment import EdgeDeployment
        deployment = EdgeDeployment()
        await deployment.initialize()
        
        deployments = await deployment.list_deployments()
        return {"deployments": deployments}
    except Exception as e:
        return {"deployments": [], "error": str(e)}

@router.get("/edge/deployments/{deployment_id}")
async def get_edge_deployment(deployment_id: str):
    """Get edge deployment details"""
    try:
        from backend.edge.edge_deployment import EdgeDeployment
        deployment = EdgeDeployment()
        await deployment.initialize()
        
        details = await deployment.get_deployment(deployment_id)
        if not details:
            raise HTTPException(status_code=404, detail="Deployment not found")
        return details
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/edge/deployments/{deployment_id}")
async def remove_edge_deployment(deployment_id: str):
    """Remove edge deployment"""
    try:
        from backend.edge.edge_deployment import EdgeDeployment
        deployment = EdgeDeployment()
        await deployment.initialize()
        
        await deployment.remove_deployment(deployment_id)
        return {"message": "Deployment removed", "deployment_id": deployment_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/edge/sync")
async def sync_edge_devices(device_ids: Optional[List[str]] = None):
    """Sync edge devices"""
    try:
        from backend.edge.edge_manager import EdgeManager
        manager = EdgeManager()
        await manager.initialize()
        
        result = await manager.sync_devices(device_ids)
        return {"message": "Devices synced", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# QUANTUM COMPUTING
# ============================================================================

@router.post("/quantum/circuits/create")
async def create_quantum_circuit(
    name: str,
    num_qubits: int,
    gates: List[Dict[str, Any]],
    metadata: Optional[Dict[str, Any]] = None
):
    """Create quantum circuit"""
    try:
        from backend.quantum.quantum_engine import QuantumEngine
        engine = QuantumEngine()
        await engine.initialize()
        
        circuit = await engine.create_circuit(name, num_qubits, gates, metadata or {})
        return {"message": "Quantum circuit created", "circuit": circuit}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quantum/circuits/{circuit_id}/execute")
async def execute_quantum_circuit(
    circuit_id: str,
    backend: QuantumBackend = QuantumBackend.SIMULATOR,
    shots: int = 1024
):
    """Execute quantum circuit"""
    try:
        from backend.quantum.quantum_engine import QuantumEngine
        engine = QuantumEngine()
        await engine.initialize()
        
        result = await engine.execute_circuit(circuit_id, backend.value, shots)
        return {"message": "Circuit executed", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quantum/circuits")
async def list_quantum_circuits():
    """List quantum circuits"""
    try:
        from backend.quantum.quantum_engine import QuantumEngine
        engine = QuantumEngine()
        await engine.initialize()
        
        circuits = await engine.list_circuits()
        return {"circuits": circuits}
    except Exception as e:
        return {"circuits": [], "error": str(e)}

@router.get("/quantum/circuits/{circuit_id}")
async def get_quantum_circuit(circuit_id: str):
    """Get quantum circuit details"""
    try:
        from backend.quantum.quantum_engine import QuantumEngine
        engine = QuantumEngine()
        await engine.initialize()
        
        circuit = await engine.get_circuit(circuit_id)
        if not circuit:
            raise HTTPException(status_code=404, detail="Circuit not found")
        return circuit
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quantum/backends")
async def list_quantum_backends():
    """List available quantum backends"""
    try:
        from backend.quantum.quantum_engine import QuantumEngine
        engine = QuantumEngine()
        await engine.initialize()
        
        backends = await engine.list_backends()
        return {"backends": backends}
    except Exception as e:
        return {"backends": [], "error": str(e)}

@router.get("/quantum/backends/{backend}/status")
async def get_backend_status(backend: QuantumBackend):
    """Get quantum backend status"""
    try:
        from backend.quantum.quantum_engine import QuantumEngine
        engine = QuantumEngine()
        await engine.initialize()
        
        status = await engine.get_backend_status(backend.value)
        return {"backend": backend.value, "status": status}
    except Exception as e:
        return {"backend": backend.value, "status": "unknown", "error": str(e)}

# ============================================================================
# HYBRID PROCESSING
# ============================================================================

@router.post("/hybrid/optimize")
async def optimize_with_hybrid(
    problem: Dict[str, Any],
    use_quantum: bool = True,
    quantum_backend: QuantumBackend = QuantumBackend.SIMULATOR
):
    """Optimize problem with hybrid classical-quantum processing"""
    try:
        from backend.quantum.hybrid_processor import HybridProcessor
        processor = HybridProcessor()
        await processor.initialize()
        
        backend_val = quantum_backend.value if use_quantum else None
        result = await processor.optimize(problem, use_quantum, backend_val)
        return {"message": "Problem optimized", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hybrid/ml/train")
async def hybrid_ml_training(
    model_config: Dict[str, Any],
    dataset: str,
    use_quantum: bool = False
):
    """Train ML model with hybrid processing"""
    try:
        from backend.quantum.hybrid_processor import HybridProcessor
        processor = HybridProcessor()
        await processor.initialize()
        
        result = await processor.train_model(model_config, dataset, use_quantum)
        return {"message": "Hybrid training completed", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/hybrid/jobs")
async def list_hybrid_jobs():
    """List hybrid processing jobs"""
    try:
        from backend.quantum.hybrid_processor import HybridProcessor
        processor = HybridProcessor()
        await processor.initialize()
        
        jobs = await processor.list_jobs()
        return {"jobs": jobs}
    except Exception as e:
        return {"jobs": [], "error": str(e)}

@router.get("/hybrid/jobs/{job_id}")
async def get_hybrid_job(job_id: str):
    """Get hybrid job details"""
    try:
        from backend.quantum.hybrid_processor import HybridProcessor
        processor = HybridProcessor()
        await processor.initialize()
        
        job = await processor.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
