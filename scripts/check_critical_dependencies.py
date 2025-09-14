"""
Check Critical Dependencies module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Critical Dependencies Status Check
Validates which dependencies from PRIORITIES_IMMEDIATES_100_COMPLETION.md are available
"""
import sys
import importlib

def check_dependency(name, display_name=None) -> None:
    """Check if a dependency is available"""
    if display_name is None:
        display_name = name
    
    try:
        module = importlib.import_module(name)
        version = getattr(module, '__version__', 'unknown')
        print(f"  ✅ {display_name}: {version}")
        return True
    except ImportError:
        print(f"  ❌ {display_name}: Not available")
        return False

def main() -> None:
    print("🔍 CRITICAL DEPENDENCIES STATUS CHECK")
    print("=" * 50)
    
    total = 0
    available = 0
    
    # Core dependencies (should be available)
    print("\n📦 Core Dependencies:")
    dependencies = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"), 
        ("pydantic", "Pydantic"),
        ("email_validator", "Email Validator"),
    ]
    
    for dep, name in dependencies:
        total += 1
        if check_dependency(dep, name):
            available += 1
    
    # Critical missing dependencies 
    print("\n🎯 Critical Dependencies (from requirements.txt):")
    critical_deps = [
        ("motor", "Motor (MongoDB Async)"),
        ("pymongo", "PyMongo"),
        ("spacy", "spaCy"),
        ("torchaudio", "TorchAudio"),
        ("lz4", "LZ4 Compression"),
        ("brotli", "Brotli Compression"),
        ("web3", "Web3.py"),
        ("eth_account", "Eth Account"),
        ("elasticapm", "Elastic APM"),
        ("jaeger_client", "Jaeger Client"),
        ("xgboost", "XGBoost"),
        ("lightgbm", "LightGBM"),
        ("tensorflow_hub", "TensorFlow Hub"),
        ("sentence_transformers", "Sentence Transformers"),
    ]
    
    for dep, name in critical_deps:
        total += 1
        if check_dependency(dep, name):
            available += 1
    
    # Already available from base requirements
    print("\n✅ Already Available (from base requirements):")
    base_deps = [
        ("torch", "PyTorch"),
        ("transformers", "Transformers"),
        ("scikit_learn", "Scikit-Learn"),
        ("numpy", "NumPy"),
        ("scipy", "SciPy"),
        ("librosa", "Librosa"),
    ]
    
    for dep, name in base_deps:
        total += 1
        if check_dependency(dep, name):
            available += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 SUMMARY: {available}/{total} dependencies available")
    print(f"📈 Success Rate: {(available/total)*100:.1f}%")
    
    if available == total:
        print("🎉 All critical dependencies are available!")
        return 0
    else:
        missing = total - available
        print(f"⚠️  {missing} dependencies missing - run 'pip install -r requirements.txt' to install")
        return 1

if __name__ == "__main__":
    sys.exit(main())