#!/usr/bin/env python3
"""
Enterprise Threat Detection System
Real-time security monitoring and response
"""

import asyncio
import logging
from typing import Dict, List, Any
import json
from datetime import datetime
import hashlib
import re

logger = logging.getLogger(__name__)

class EnterpriseThreatDetector:
    """Enterprise-grade threat detection system"""
    
    def __init__(self):
        self.threat_patterns = {
            'sql_injection': [
                r"'\s*(OR|AND)\s*'",
                r"UNION\s+SELECT",
                r"DROP\s+TABLE",
                r"--\s*$"
            ],
            'xss': [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
                r"on\w+\s*="
            ],
            'csrf': [
                r"<iframe[^>]*>",
                r"<form[^>]*action\s*=[^>]*>"
            ]
        }
        self.alerts = []
    
    def detect_sql_injection(self, input_data: str) -> bool:
        """Detect SQL injection attempts"""
        for pattern in self.threat_patterns['sql_injection']:
            if re.search(pattern, input_data, re.IGNORECASE):
                self.log_threat("SQL_INJECTION", input_data, pattern)
                return True
        return False
    
    def detect_xss(self, input_data: str) -> bool:
        """Detect XSS attempts"""
        for pattern in self.threat_patterns['xss']:
            if re.search(pattern, input_data, re.IGNORECASE):
                self.log_threat("XSS", input_data, pattern)
                return True
        return False
    
    def detect_csrf(self, input_data: str) -> bool:
        """Detect CSRF attempts"""
        for pattern in self.threat_patterns['csrf']:
            if re.search(pattern, input_data, re.IGNORECASE):
                self.log_threat("CSRF", input_data, pattern)
                return True
        return False
    
    def log_threat(self, threat_type: str, input_data: str, pattern: str) -> None:
        """Log detected threat"""
        threat_hash = hashlib.sha256(input_data.encode()).hexdigest()[:16]
        
        alert = {
            "timestamp": datetime.now().isoformat(),
            "threat_type": threat_type,
            "threat_hash": threat_hash,
            "pattern_matched": pattern,
            "severity": "HIGH",
            "status": "DETECTED"
        }
        
        self.alerts.append(alert)
        logger.warning(f"THREAT DETECTED: {threat_type} - {threat_hash}")
    
    def validate_input(self, input_data: str) -> Dict[str, Any]:
        """Comprehensive input validation"""
        results = {
            "is_safe": True,
            "threats_detected": [],
            "validation_timestamp": datetime.now().isoformat()
        }
        
        # Check for various threats
        if self.detect_sql_injection(input_data):
            results["threats_detected"].append("SQL_INJECTION")
            results["is_safe"] = False
        
        if self.detect_xss(input_data):
            results["threats_detected"].append("XSS")
            results["is_safe"] = False
        
        if self.detect_csrf(input_data):
            results["threats_detected"].append("CSRF")
            results["is_safe"] = False
        
        return results
    
    def get_security_metrics(self) -> Dict[str, Any]:
        """Get security metrics and alerts"""
        threat_counts = {}
        for alert in self.alerts:
            threat_type = alert["threat_type"]
            threat_counts[threat_type] = threat_counts.get(threat_type, 0) + 1
        
        return {
            "total_threats": len(self.alerts),
            "threat_breakdown": threat_counts,
            "last_24h_alerts": len([a for a in self.alerts 
                                  if (datetime.now() - datetime.fromisoformat(a["timestamp"])).days < 1]),
            "system_status": "SECURE" if len(self.alerts) == 0 else "MONITORING"
        }

if __name__ == "__main__":
    detector = EnterpriseThreatDetector()
    
    # Test inputs
    test_inputs = [
        "SELECT * FROM users WHERE id = 1",
        "' OR '1'='1' --",
        "<script>alert('xss')</script>",
        "normal input text"
    ]
    
    for test_input in test_inputs:
        result = detector.validate_input(test_input)
        print(f"Input: {test_input[:50]}...")
        print(f"Result: {result}")
        print("-" * 50)
    
    metrics = detector.get_security_metrics()
    print("Security Metrics:")
    print(json.dumps(metrics, indent=2))
