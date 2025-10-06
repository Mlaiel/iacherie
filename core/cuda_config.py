"""🚀 CUDA Configuration & GPU Detection
========================================

Configuration automatique CUDA/GPU pour la plateforme IA Chérie.
Détection intelligente du hardware disponible et optimisation des performances.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import logging
import torch
import tensorflow as tf
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def configure_cuda_environment():
    """
Configure l'environnement CUDA optimal."""
    
    # Configuration des variables d'environnement CUDA
    cuda_config = {
        "CUDA_VISIBLE_DEVICES": "0",  # Utiliser GPU 0 si disponible
        "CUDA_DEVICE_ORDER": "PCI_BUS_ID",
        "TF_FORCE_GPU_ALLOW_GROWTH": "true",
        "TF_GPU_MEMORY_ALLOW_GROWTH": "true",
        "PYTORCH_CUDA_ALLOC_CONF": "max_split_size_mb:512",
        "CUDA_LAUNCH_BLOCKING": "1",  # Pour debugging
    }
    
    for key, value in cuda_config.items():
        os.environ[key] = value
        logger.info(f"✅ {key} = {value}")

def detect_gpu_capabilities() -> Dict[str, Any]:
    """
Détecte les capacités GPU disponibles."""
    
    gpu_info = {
        "torch_cuda_available": torch.cuda.is_available(),
        "torch_cuda_device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        "tf_gpu_available": len(tf.config.experimental.list_physical_devices('GPU')) > 0,
        "recommended_device": "cpu",
        "performance_mode": "cpu_optimized"
    }
    
    # PyTorch GPU Detection
    if torch.cuda.is_available():
        gpu_info["torch_device_name"] = torch.cuda.get_device_name(0)
        gpu_info["torch_memory_total"] = torch.cuda.get_device_properties(0).total_memory
        gpu_info["recommended_device"] = "cuda"
        gpu_info["performance_mode"] = "gpu_accelerated"
        logger.info(f"🚀 GPU détecté: {gpu_info['torch_device_name']}")
    
    # TensorFlow GPU Detection
    if gpu_info["tf_gpu_available"]:
        gpus = tf.config.experimental.list_physical_devices('GPU')
        logger.info(f"🚀 TensorFlow GPU: {len(gpus)} dispositifs détectés")
        
        # Configuration mémoire TensorFlow
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            logger.info("✅ TensorFlow GPU memory growth configuré")
        except RuntimeError as e:
            logger.warning(f"⚠️ Configuration TF GPU: {e}")
    
    return gpu_info

def optimize_for_cpu():
    """
Optimise les performances pour CPU seulement."""
    
    cpu_config = {
        "OMP_NUM_THREADS": str(os.cpu_count()),
        "MKL_NUM_THREADS": str(os.cpu_count()),
        "NUMEXPR_NUM_THREADS": str(os.cpu_count()),
        "TF_NUM_INTEROP_THREADS": str(os.cpu_count()),
        "TF_NUM_INTRAOP_THREADS": str(os.cpu_count()),
    }
    
    for key, value in cpu_config.items():
        os.environ[key] = value
        logger.info(f"🔧 CPU Optimisation: {key} = {value}")
    
    # Configuration PyTorch CPU
    torch.set_num_threads(os.cpu_count())
    
    # Configuration TensorFlow CPU
    tf.config.threading.set_inter_op_parallelism_threads(os.cpu_count())
    tf.config.threading.set_intra_op_parallelism_threads(os.cpu_count())
    
    logger.info(f"⚡ CPU optimisé pour {os.cpu_count()} threads")

def get_optimal_device() -> str:
    """
Retourne le dispositif optimal (cuda ou cpu)."""
    
    if torch.cuda.is_available():
        device = "cuda"
        logger.info("🚀 Utilisation GPU CUDA")
    else:
        device = "cpu" 
        logger.info("🔧 Utilisation CPU optimisé")
    
    return device

def configure_model_precision(use_half_precision: bool = True) -> Dict[str, Any]:
    """
Configure la précision des modèles pour optimiser les performances."""
    
    config = {
        "torch_dtype": torch.float16 if use_half_precision and torch.cuda.is_available() else torch.float32,
        "tf_mixed_precision": use_half_precision and len(tf.config.experimental.list_physical_devices('GPU')) > 0
    }
    
    # Configuration TensorFlow Mixed Precision
    if config["tf_mixed_precision"]:
        try:
            policy = tf.keras.mixed_precision.Policy('mixed_float16')
            tf.keras.mixed_precision.set_global_policy(policy)
            logger.info("✅ TensorFlow Mixed Precision activé (float16)")
        except Exception as e:
            logger.warning(f"⚠️ Mixed Precision non supporté: {e}")
            config["tf_mixed_precision"] = False
    
    logger.info(f"🎯 Précision configurée: PyTorch={config['torch_dtype']}, TF_Mixed={config['tf_mixed_precision']}")
    return config

def initialize_cuda_system() -> Dict[str, Any]:
    """
Initialise complètement le système CUDA/GPU."""
    
    logger.info("🚀 Initialisation du système CUDA/GPU...")
    
    # 1. Configuration environnement
    configure_cuda_environment()
    
    # 2. Détection GPU
    gpu_info = detect_gpu_capabilities()
    
    # 3. Optimisation selon hardware disponible
    if gpu_info["torch_cuda_available"] or gpu_info["tf_gpu_available"]:
        logger.info("🚀 Mode GPU activé")
        device = "cuda"
    else:
        logger.info("🔧 Mode CPU optimisé activé")
        optimize_for_cpu()
        device = "cpu"
    
    # 4. Configuration précision
    precision_config = configure_model_precision()
    
    # 5. Test de performance
    performance_score = test_performance()
    
    result = {
        **gpu_info,
        **precision_config,
        "optimal_device": device,
        "performance_score": performance_score,
        "status": "ready",
        "recommendations": generate_performance_recommendations(gpu_info)
    }
    
    logger.info("✅ Système CUDA/GPU initialisé avec succès!")
    return result

def test_performance() -> float:
    """
Test rapide de performance du système."""
    
    import time
    start_time = time.time()
    
    # Test PyTorch
    try:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        x = torch.randn(1000, 1000, device=device)
        y = torch.mm(x, x.t())
        torch_time = time.time() - start_time
    except Exception as e:
        logger.warning(f"Test PyTorch échoué: {e}")
        torch_time = float('inf')
    
    # Test TensorFlow
    try:
        with tf.device('/GPU:0' if tf.config.experimental.list_physical_devices('GPU') else '/CPU:0'):
            a = tf.random.normal([1000, 1000])
            b = tf.linalg.matmul(a, a, transpose_b=True)
        tf_time = time.time() - start_time - torch_time
    except Exception as e:
        logger.warning(f"Test TensorFlow échoué: {e}")
        tf_time = float('inf')
    
    total_time = time.time() - start_time
    score = max(0, 100 - (total_time * 10))  # Score sur 100
    
    logger.info(f"📊 Performance Score: {score:.1f}/100 (PyTorch: {torch_time:.3f}s, TF: {tf_time:.3f}s)")
    return score

def generate_performance_recommendations(gpu_info: Dict[str, Any]) -> list:
    """
Génère des recommandations d'optimisation."""
    
    recommendations = []
    
    if not gpu_info["torch_cuda_available"]:
        recommendations.extend([
            "💡 Pour des performances optimales, utilisez un environnement avec GPU CUDA",
            "⚡ Considérez Google Colab Pro ou AWS EC2 avec GPU pour la production",
            "🔧 Le mode CPU est optimisé mais sera plus lent pour les modèles complexes"
        ])
    else:
        recommendations.extend([
            "🚀 GPU CUDA détecté - performances optimales disponibles",
            "💾 Activez Mixed Precision pour économiser la mémoire GPU",
            "⚡ Utilisez des batch sizes plus importants avec GPU"
        ])
    
    recommendations.append("📈 Monitoring des performances activé")
    return recommendations

# Configuration globale au démarrage
CUDA_SYSTEM_INFO = None

def get_cuda_system_info() -> Dict[str, Any]:
    """
Récupère les informations système CUDA (singleton)."""
    global CUDA_SYSTEM_INFO
    if CUDA_SYSTEM_INFO is None:
        CUDA_SYSTEM_INFO = initialize_cuda_system()
    return CUDA_SYSTEM_INFO

# Auto-initialisation
if __name__ == "__main__":
    system_info = initialize_cuda_system()
    print("🚀 Système CUDA/GPU configuré:")
    for key, value in system_info.items():
        print(f"  {key}: {value}")