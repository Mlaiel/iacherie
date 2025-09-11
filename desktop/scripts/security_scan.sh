#!/bin/bash

# Ainflue Desktop - Security Scan Script
# 
# Comprehensive security scanning for desktop application
# Includes vulnerability assessment, dependency analysis, and security best practices
# 
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
DESKTOP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_ROOT="$(cd "$DESKTOP_DIR/.." && pwd)"
SECURITY_REPORT_FILE="$PROJECT_ROOT/test_reports/desktop/security_scan_report.json"
EXIT_CODE=0

echo -e "${BLUE}🔒 AINFLUE DESKTOP - SECURITY SCAN${NC}"
echo "===================================="
echo "Desktop Directory: $DESKTOP_DIR"
echo "Project Root: $PROJECT_ROOT"
echo "Report File: $SECURITY_REPORT_FILE"
echo ""

# Ensure reports directory exists
mkdir -p "$(dirname "$SECURITY_REPORT_FILE")"

# Initialize security report
cat > "$SECURITY_REPORT_FILE" << EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "project": "Ainflue Desktop",
  "author": "Fahed Mlaiel",
  "contact": "mlaiel@live.de",
  "scan_version": "1.0.0",
  "scans": {
    "secrets": { "status": "pending", "severity": "none", "findings": [] },
    "dependencies": { "status": "pending", "severity": "none", "vulnerabilities": [] },
    "code_injection": { "status": "pending", "severity": "none", "issues": [] },
    "file_permissions": { "status": "pending", "severity": "none", "issues": [] },
    "crypto_usage": { "status": "pending", "severity": "none", "issues": [] },
    "electron_security": { "status": "pending", "severity": "none", "issues": [] },
    "xss_prevention": { "status": "pending", "severity": "none", "issues": [] },
    "input_validation": { "status": "pending", "severity": "none", "issues": [] }
  },
  "summary": {
    "total_issues": 0,
    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0,
    "info": 0,
    "overall_rating": "A",
    "secure": true
  },
  "recommendations": []
}
EOF

# Function to update report
update_scan_result() {
  local scan_name="$1"
  local status="$2"
  local severity="$3"
  local findings="$4"
  
  jq --arg scan "$scan_name" --arg status "$status" --arg severity "$severity" --argjson findings "$findings" \
    '.scans[$scan].status = $status | .scans[$scan].severity = $severity | .scans[$scan] += $findings' \
    "$SECURITY_REPORT_FILE" > "${SECURITY_REPORT_FILE}.tmp" && mv "${SECURITY_REPORT_FILE}.tmp" "$SECURITY_REPORT_FILE"
}

# Function to add recommendation
add_recommendation() {
  local recommendation="$1"
  jq --arg rec "$recommendation" '.recommendations += [$rec]' \
    "$SECURITY_REPORT_FILE" > "${SECURITY_REPORT_FILE}.tmp" && mv "${SECURITY_REPORT_FILE}.tmp" "$SECURITY_REPORT_FILE"
}

# Function to calculate summary
calculate_summary() {
  local critical=0 high=0 medium=0 low=0 info=0
  
  # Count issues by severity from all scans
  for scan in secrets dependencies code_injection file_permissions crypto_usage electron_security xss_prevention input_validation; do
    local severity=$(jq -r ".scans.$scan.severity" "$SECURITY_REPORT_FILE")
    case $severity in
      "critical") critical=$((critical + 1)) ;;
      "high") high=$((high + 1)) ;;
      "medium") medium=$((medium + 1)) ;;
      "low") low=$((low + 1)) ;;
      "info") info=$((info + 1)) ;;
    esac
  done
  
  local total=$((critical + high + medium + low + info))
  local rating="A"
  local secure=true
  
  if [ $critical -gt 0 ]; then
    rating="F"
    secure=false
  elif [ $high -gt 2 ]; then
    rating="D"
    secure=false
  elif [ $high -gt 0 ] || [ $medium -gt 3 ]; then
    rating="C"
  elif [ $medium -gt 0 ] || [ $low -gt 5 ]; then
    rating="B"
  fi
  
  jq --argjson total "$total" --argjson critical "$critical" --argjson high "$high" \
     --argjson medium "$medium" --argjson low "$low" --argjson info "$info" \
     --arg rating "$rating" --argjson secure "$secure" \
    '.summary.total_issues = $total | .summary.critical = $critical | .summary.high = $high |
     .summary.medium = $medium | .summary.low = $low | .summary.info = $info |
     .summary.overall_rating = $rating | .summary.secure = $secure' \
    "$SECURITY_REPORT_FILE" > "${SECURITY_REPORT_FILE}.tmp" && mv "${SECURITY_REPORT_FILE}.tmp" "$SECURITY_REPORT_FILE"
}

cd "$DESKTOP_DIR"

# 1. Secrets Detection
echo -e "${YELLOW}🔍 Scanning for hardcoded secrets...${NC}"

secrets_found=()

# Check for common secret patterns
echo "  Checking for API keys..."
api_keys=$(grep -r -n -i "api[_-]key\|apikey" --include="*.js" . | grep -v node_modules | grep -v test || true)

echo "  Checking for passwords..."
passwords=$(grep -r -n -i "password\s*=\|pwd\s*=" --include="*.js" . | grep -v node_modules | grep -v "placeholder\|example" || true)

echo "  Checking for private keys..."
private_keys=$(grep -r -n -i "private[_-]key\|privatekey" --include="*.js" . | grep -v node_modules || true)

echo "  Checking for tokens..."
tokens=$(grep -r -n -i "token\s*=\|access[_-]token" --include="*.js" . | grep -v node_modules | grep -v "placeholder\|example" || true)

echo "  Checking for database URLs..."
db_urls=$(grep -r -n -i "mongodb://\|mysql://\|postgres://" --include="*.js" . | grep -v node_modules || true)

# Count total secrets
total_secrets=0
if [ -n "$api_keys" ]; then total_secrets=$((total_secrets + $(echo "$api_keys" | wc -l))); fi
if [ -n "$passwords" ]; then total_secrets=$((total_secrets + $(echo "$passwords" | wc -l))); fi
if [ -n "$private_keys" ]; then total_secrets=$((total_secrets + $(echo "$private_keys" | wc -l))); fi
if [ -n "$tokens" ]; then total_secrets=$((total_secrets + $(echo "$tokens" | wc -l))); fi
if [ -n "$db_urls" ]; then total_secrets=$((total_secrets + $(echo "$db_urls" | wc -l))); fi

if [ $total_secrets -eq 0 ]; then
  echo -e "${GREEN}✅ No hardcoded secrets found${NC}"
  update_scan_result "secrets" "passed" "none" '{"findings": []}'
elif [ $total_secrets -le 2 ]; then
  echo -e "${YELLOW}⚠️  $total_secrets potential secrets found (review needed)${NC}"
  update_scan_result "secrets" "warning" "medium" "{\"findings\": $total_secrets}"
  add_recommendation "Review and remove any hardcoded secrets, use environment variables instead"
else
  echo -e "${RED}❌ $total_secrets hardcoded secrets found${NC}"
  update_scan_result "secrets" "failed" "high" "{\"findings\": $total_secrets}"
  add_recommendation "Critical: Remove all hardcoded secrets immediately and use secure storage"
  EXIT_CODE=1
fi

# 2. Dependency Vulnerabilities
echo -e "${YELLOW}🔍 Checking for vulnerable dependencies...${NC}"

if [ -f "package.json" ] && command -v npm &> /dev/null; then
  echo "  Running npm audit..."
  audit_output=$(npm audit --json 2>/dev/null || echo '{"vulnerabilities": {}}')
  
  # Parse audit results
  critical_vulns=$(echo "$audit_output" | jq '.metadata.vulnerabilities.critical // 0' 2>/dev/null || echo "0")
  high_vulns=$(echo "$audit_output" | jq '.metadata.vulnerabilities.high // 0' 2>/dev/null || echo "0")
  moderate_vulns=$(echo "$audit_output" | jq '.metadata.vulnerabilities.moderate // 0' 2>/dev/null || echo "0")
  low_vulns=$(echo "$audit_output" | jq '.metadata.vulnerabilities.low // 0' 2>/dev/null || echo "0")
  
  total_vulns=$((critical_vulns + high_vulns + moderate_vulns + low_vulns))
  
  if [ $total_vulns -eq 0 ]; then
    echo -e "${GREEN}✅ No known vulnerabilities in dependencies${NC}"
    update_scan_result "dependencies" "passed" "none" '{"vulnerabilities": []}'
  elif [ $critical_vulns -gt 0 ]; then
    echo -e "${RED}❌ $critical_vulns critical vulnerabilities found${NC}"
    update_scan_result "dependencies" "failed" "critical" "{\"vulnerabilities\": $total_vulns}"
    add_recommendation "Critical: Update dependencies with security vulnerabilities immediately"
    EXIT_CODE=1
  elif [ $high_vulns -gt 0 ]; then
    echo -e "${RED}❌ $high_vulns high-severity vulnerabilities found${NC}"
    update_scan_result "dependencies" "failed" "high" "{\"vulnerabilities\": $total_vulns}"
    add_recommendation "Update dependencies with high-severity vulnerabilities"
    EXIT_CODE=1
  else
    echo -e "${YELLOW}⚠️  $total_vulns moderate/low vulnerabilities found${NC}"
    update_scan_result "dependencies" "warning" "medium" "{\"vulnerabilities\": $total_vulns}"
    add_recommendation "Consider updating dependencies with moderate vulnerabilities"
  fi
else
  echo -e "${YELLOW}⚠️  Skipping dependency check (npm not available or no package.json)${NC}"
  update_scan_result "dependencies" "skipped" "none" '{"vulnerabilities": [], "reason": "npm not available"}'
fi

# 3. Code Injection Vulnerabilities
echo -e "${YELLOW}🔍 Scanning for code injection vulnerabilities...${NC}"

injection_issues=0

echo "  Checking for eval() usage..."
eval_usage=$(grep -r -n "eval(" --include="*.js" . | grep -v node_modules | wc -l || echo "0")

echo "  Checking for Function() constructor..."
function_constructor=$(grep -r -n "new Function(" --include="*.js" . | grep -v node_modules | wc -l || echo "0")

echo "  Checking for setTimeout/setInterval with strings..."
timeout_strings=$(grep -r -n "setTimeout\s*(\s*['\"].*['\"]" --include="*.js" . | grep -v node_modules | wc -l || echo "0")

echo "  Checking for document.write usage..."
document_write=$(grep -r -n "document\.write" --include="*.js" . | grep -v node_modules | wc -l || echo "0")

injection_issues=$((eval_usage + function_constructor + timeout_strings + document_write))

if [ $injection_issues -eq 0 ]; then
  echo -e "${GREEN}✅ No code injection vulnerabilities found${NC}"
  update_scan_result "code_injection" "passed" "none" '{"issues": []}'
elif [ $injection_issues -le 2 ]; then
  echo -e "${YELLOW}⚠️  $injection_issues potential injection points found${NC}"
  update_scan_result "code_injection" "warning" "medium" "{\"issues\": $injection_issues}"
  add_recommendation "Review and sanitize dynamic code execution points"
else
  echo -e "${RED}❌ $injection_issues code injection vulnerabilities found${NC}"
  update_scan_result "code_injection" "failed" "high" "{\"issues\": $injection_issues}"
  add_recommendation "Critical: Remove or properly sanitize all dynamic code execution"
  EXIT_CODE=1
fi

# 4. File Permissions Check
echo -e "${YELLOW}🔍 Checking file permissions...${NC}"

permission_issues=0

# Check for overly permissive files
echo "  Checking for world-writable files..."
world_writable=$(find . -type f -perm -002 | grep -v node_modules | wc -l || echo "0")

echo "  Checking for files with execute permissions..."
executable_js=$(find . -name "*.js" -perm -111 | grep -v node_modules | grep -v scripts | wc -l || echo "0")

permission_issues=$((world_writable + executable_js))

if [ $permission_issues -eq 0 ]; then
  echo -e "${GREEN}✅ File permissions are secure${NC}"
  update_scan_result "file_permissions" "passed" "none" '{"issues": []}'
else
  echo -e "${YELLOW}⚠️  $permission_issues permission issues found${NC}"
  echo "  - World-writable files: $world_writable"
  echo "  - Executable JS files: $executable_js"
  update_scan_result "file_permissions" "warning" "low" "{\"issues\": $permission_issues}"
  add_recommendation "Review and fix file permissions for security"
fi

# 5. Cryptography Usage Check
echo -e "${YELLOW}🔍 Checking cryptography usage...${NC}"

crypto_issues=0

echo "  Checking for weak hashing algorithms..."
weak_hash=$(grep -r -n -i "md5\|sha1" --include="*.js" . | grep -v node_modules | wc -l || echo "0")

echo "  Checking for hardcoded salts..."
hardcoded_salt=$(grep -r -n -i "salt.*=" --include="*.js" . | grep -v node_modules | grep -v "placeholder\|example" | wc -l || echo "0")

echo "  Checking for insecure random generation..."
weak_random=$(grep -r -n "Math\.random()" --include="*.js" . | grep -v node_modules | wc -l || echo "0")

crypto_issues=$((weak_hash + hardcoded_salt + weak_random))

if [ $crypto_issues -eq 0 ]; then
  echo -e "${GREEN}✅ Cryptography usage appears secure${NC}"
  update_scan_result "crypto_usage" "passed" "none" '{"issues": []}'
elif [ $crypto_issues -le 3 ]; then
  echo -e "${YELLOW}⚠️  $crypto_issues cryptography concerns found${NC}"
  update_scan_result "crypto_usage" "warning" "medium" "{\"issues\": $crypto_issues}"
  add_recommendation "Review cryptographic implementations for security best practices"
else
  echo -e "${RED}❌ $crypto_issues cryptography vulnerabilities found${NC}"
  update_scan_result "crypto_usage" "failed" "high" "{\"issues\": $crypto_issues}"
  add_recommendation "Critical: Fix weak cryptographic implementations"
  EXIT_CODE=1
fi

# 6. Electron Security Check
echo -e "${YELLOW}🔍 Checking Electron security configurations...${NC}"

electron_issues=0

if [ -f "main.js" ] || [ -f "src/main.js" ]; then
  echo "  Checking for nodeIntegration settings..."
  node_integration=$(grep -r -n "nodeIntegration.*true" --include="*.js" . | grep -v node_modules | wc -l || echo "0")
  
  echo "  Checking for contextIsolation settings..."
  context_isolation=$(grep -r -n "contextIsolation.*false" --include="*.js" . | grep -v node_modules | wc -l || echo "0")
  
  echo "  Checking for allowRunningInsecureContent..."
  insecure_content=$(grep -r -n "allowRunningInsecureContent.*true" --include="*.js" . | grep -v node_modules | wc -l || echo "0")
  
  electron_issues=$((node_integration + context_isolation + insecure_content))
  
  if [ $electron_issues -eq 0 ]; then
    echo -e "${GREEN}✅ Electron security configuration is secure${NC}"
    update_scan_result "electron_security" "passed" "none" '{"issues": []}'
  else
    echo -e "${RED}❌ $electron_issues Electron security issues found${NC}"
    echo "  - nodeIntegration enabled: $node_integration"
    echo "  - contextIsolation disabled: $context_isolation"
    echo "  - allowRunningInsecureContent: $insecure_content"
    update_scan_result "electron_security" "failed" "high" "{\"issues\": $electron_issues}"
    add_recommendation "Critical: Fix Electron security configurations (disable nodeIntegration, enable contextIsolation)"
    EXIT_CODE=1
  fi
else
  echo -e "${BLUE}ℹ️  No Electron main files found, skipping Electron-specific checks${NC}"
  update_scan_result "electron_security" "skipped" "none" '{"issues": [], "reason": "No Electron main files found"}'
fi

# 7. XSS Prevention Check
echo -e "${YELLOW}🔍 Checking XSS prevention measures...${NC}"

xss_issues=0

echo "  Checking for innerHTML usage..."
innerhtml_usage=$(grep -r -n "innerHTML\s*=" --include="*.js" . | grep -v node_modules | wc -l || echo "0")

echo "  Checking for document.write usage..."
doc_write_usage=$(grep -r -n "document\.write" --include="*.js" . | grep -v node_modules | wc -l || echo "0")

echo "  Checking for unsanitized user input..."
unsanitized_input=$(grep -r -n "\.value\)" --include="*.js" . | grep -v node_modules | grep -v "sanitize\|escape" | wc -l || echo "0")

xss_issues=$((innerhtml_usage + doc_write_usage))

if [ $xss_issues -eq 0 ]; then
  echo -e "${GREEN}✅ XSS prevention measures are in place${NC}"
  update_scan_result "xss_prevention" "passed" "none" '{"issues": []}'
elif [ $xss_issues -le 3 ]; then
  echo -e "${YELLOW}⚠️  $xss_issues potential XSS issues found${NC}"
  update_scan_result "xss_prevention" "warning" "medium" "{\"issues\": $xss_issues}"
  add_recommendation "Review and sanitize dynamic HTML generation"
else
  echo -e "${RED}❌ $xss_issues XSS vulnerabilities found${NC}"
  update_scan_result "xss_prevention" "failed" "high" "{\"issues\": $xss_issues}"
  add_recommendation "Critical: Implement proper XSS prevention measures"
  EXIT_CODE=1
fi

# 8. Input Validation Check
echo -e "${YELLOW}🔍 Checking input validation...${NC}"

validation_issues=0

echo "  Checking for SQL query construction..."
sql_queries=$(grep -r -n -i "select\|insert\|update\|delete" --include="*.js" . | grep -v node_modules | grep -v "placeholder\|example" | wc -l || echo "0")

echo "  Checking for file path operations..."
file_operations=$(grep -r -n "fs\.\|path\." --include="*.js" . | grep -v node_modules | wc -l || echo "0")

echo "  Checking for URL parsing..."
url_operations=$(grep -r -n "new URL\|url\.parse" --include="*.js" . | grep -v node_modules | wc -l || echo "0")

# Basic validation check (this is simplified)
if [ $sql_queries -gt 0 ] || [ $file_operations -gt 5 ] || [ $url_operations -gt 3 ]; then
  validation_issues=1
  echo -e "${YELLOW}⚠️  Input validation review recommended${NC}"
  update_scan_result "input_validation" "warning" "medium" "{\"issues\": $validation_issues}"
  add_recommendation "Review input validation for SQL queries, file operations, and URL parsing"
else
  echo -e "${GREEN}✅ Input validation appears adequate${NC}"
  update_scan_result "input_validation" "passed" "none" '{"issues": []}'
fi

# Calculate final summary
calculate_summary

# Display results
echo ""
echo -e "${BLUE}🔒 SECURITY SCAN RESULTS${NC}"
echo "=========================="

overall_rating=$(jq -r '.summary.overall_rating' "$SECURITY_REPORT_FILE")
total_issues=$(jq -r '.summary.total_issues' "$SECURITY_REPORT_FILE")
is_secure=$(jq -r '.summary.secure' "$SECURITY_REPORT_FILE")

if [ "$is_secure" = "true" ]; then
  echo -e "${GREEN}🛡️  Overall Security Rating: $overall_rating${NC}"
  echo -e "${GREEN}✅ Application appears secure${NC}"
else
  echo -e "${RED}⚠️  Overall Security Rating: $overall_rating${NC}"
  echo -e "${RED}❌ Security issues found - immediate attention required${NC}"
fi

echo ""
echo -e "${BLUE}📊 Issue Summary:${NC}"
jq -r '.summary | "  Critical: \(.critical)\n  High: \(.high)\n  Medium: \(.medium)\n  Low: \(.low)\n  Info: \(.info)"' "$SECURITY_REPORT_FILE"

echo ""
echo -e "${BLUE}🔍 Scan Results:${NC}"
jq -r '.scans | to_entries[] | "  " + .key + ": " + .value.status + " (" + .value.severity + ")"' "$SECURITY_REPORT_FILE"

# Display recommendations
rec_count=$(jq '.recommendations | length' "$SECURITY_REPORT_FILE")
if [ "$rec_count" -gt 0 ]; then
  echo ""
  echo -e "${BLUE}💡 Security Recommendations:${NC}"
  jq -r '.recommendations[] | "  • " + .' "$SECURITY_REPORT_FILE"
fi

echo ""
echo -e "${BLUE}📄 Full security report saved to: $SECURITY_REPORT_FILE${NC}"
echo ""
echo -e "${BLUE}🔒 Security Best Practices:${NC}"
echo "  • Use environment variables for secrets"
echo "  • Keep dependencies updated"
echo "  • Implement proper input validation"
echo "  • Use HTTPS for all communications"
echo "  • Enable Content Security Policy (CSP)"
echo "  • Regular security audits and penetration testing"
echo ""
echo -e "${BLUE}© 2025 Fahed Mlaiel. All rights reserved.${NC}"
echo -e "${BLUE}Contact: mlaiel@live.de${NC}"
echo ""

exit $EXIT_CODE