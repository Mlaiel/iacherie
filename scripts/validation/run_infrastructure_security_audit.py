#!/usr/bin/env python3
"""Comprehensive Infrastructure Security Audit.

==========================================

Complete infrastructure security audit addressing:
"Security audit complet infrastructure"

This script performs a comprehensive security audit of the entire
infrastructure including configuration, dependencies, and runtime security.

Author: Fahed Mlaiel <mlaiel@live.de>
"""
import os
import sys
import json
import hashlib
import subprocess
import time
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Tuple


class InfrastructureSecurityAuditor:
    """Comprehensive infrastructure security auditor."""
    try:
        auditor = InfrastructureSecurityAuditor()
        report = auditor.run_complete_audit()
        
        # Save audit report
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        report_file = f"security_audit_infrastructure_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\\n📄 Detailed audit report saved to: {report_file}")
        
        # Exit with appropriate code
        if report["critical_issues"] == 0 and report["success_rate"] >= 75:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\\n🛑 Security audit interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\\n💥 Security audit failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()