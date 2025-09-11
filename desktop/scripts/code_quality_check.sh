#!/bin/bash

# Ainflue Desktop - Code Quality Check Script
# 
# Comprehensive code quality validation for desktop application
# Includes linting, formatting, security checks, and best practices
# 
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DESKTOP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_ROOT="$(cd "$DESKTOP_DIR/.." && pwd)"
QUALITY_REPORT_FILE="$PROJECT_ROOT/test_reports/desktop/code_quality_report.json"
EXIT_CODE=0

echo -e "${BLUE}🔍 AINFLUE DESKTOP - CODE QUALITY CHECK${NC}"
echo "=============================================="
echo "Desktop Directory: $DESKTOP_DIR"
echo "Project Root: $PROJECT_ROOT"
echo "Report File: $QUALITY_REPORT_FILE"
echo ""

# Ensure reports directory exists
mkdir -p "$(dirname "$QUALITY_REPORT_FILE")"

# Initialize quality report
cat > "$QUALITY_REPORT_FILE" << EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "project": "Ainflue Desktop",
  "author": "Fahed Mlaiel",
  "contact": "mlaiel@live.de",
  "checks": {
    "eslint": { "status": "pending", "score": 0, "issues": [] },
    "jshint": { "status": "pending", "score": 0, "issues": [] },
    "security": { "status": "pending", "score": 0, "vulnerabilities": [] },
    "formatting": { "status": "pending", "score": 0, "files": [] },
    "complexity": { "status": "pending", "score": 0, "functions": [] },
    "documentation": { "status": "pending", "score": 0, "coverage": 0 },
    "dependencies": { "status": "pending", "score": 0, "outdated": [] },
    "performance": { "status": "pending", "score": 0, "metrics": {} }
  },
  "overall": {
    "score": 0,
    "grade": "F",
    "status": "pending",
    "recommendations": []
  }
}
EOF

# Function to update report
update_report() {
  local check_name="$1"
  local status="$2"
  local score="$3"
  local data="$4"
  
  jq --arg check "$check_name" --arg status "$status" --argjson score "$score" --argjson data "$data" \
    '.checks[$check].status = $status | .checks[$check].score = $score | .checks[$check] += $data' \
    "$QUALITY_REPORT_FILE" > "${QUALITY_REPORT_FILE}.tmp" && mv "${QUALITY_REPORT_FILE}.tmp" "$QUALITY_REPORT_FILE"
}

# Function to calculate overall score
calculate_overall_score() {
  local total_score=$(jq '.checks | to_entries | map(.value.score) | add / length' "$QUALITY_REPORT_FILE")
  local grade="F"
  
  if (( $(echo "$total_score >= 90" | bc -l) )); then
    grade="A+"
  elif (( $(echo "$total_score >= 85" | bc -l) )); then
    grade="A"
  elif (( $(echo "$total_score >= 80" | bc -l) )); then
    grade="B+"
  elif (( $(echo "$total_score >= 75" | bc -l) )); then
    grade="B"
  elif (( $(echo "$total_score >= 70" | bc -l) )); then
    grade="C+"
  elif (( $(echo "$total_score >= 65" | bc -l) )); then
    grade="C"
  elif (( $(echo "$total_score >= 60" | bc -l) )); then
    grade="D"
  fi
  
  jq --argjson score "$total_score" --arg grade "$grade" \
    '.overall.score = $score | .overall.grade = $grade | .overall.status = "completed"' \
    "$QUALITY_REPORT_FILE" > "${QUALITY_REPORT_FILE}.tmp" && mv "${QUALITY_REPORT_FILE}.tmp" "$QUALITY_REPORT_FILE"
}

# 1. ESLint Check
echo -e "${YELLOW}📋 Running ESLint checks...${NC}"
cd "$DESKTOP_DIR"

if command -v eslint &> /dev/null; then
  eslint_output=$(eslint . --format json 2>/dev/null || true)
  eslint_issues=$(echo "$eslint_output" | jq '. | length')
  
  if [ "$eslint_issues" -eq 0 ]; then
    echo -e "${GREEN}✅ ESLint: No issues found${NC}"
    update_report "eslint" "passed" 100 '{"issues": []}'
  else
    echo -e "${RED}❌ ESLint: $eslint_issues issues found${NC}"
    echo "$eslint_output" | jq -r '.[] | .messages[] | "  - \(.ruleId): \(.message) (line \(.line))"'
    score=$((100 - eslint_issues * 5))
    if [ $score -lt 0 ]; then score=0; fi
    update_report "eslint" "failed" "$score" "{\"issues\": $eslint_output}"
    EXIT_CODE=1
  fi
else
  echo -e "${YELLOW}⚠️  ESLint not found, installing...${NC}"
  npm install eslint @eslint/js --save-dev 2>/dev/null || true
  update_report "eslint" "skipped" 70 '{"issues": [], "reason": "ESLint not available"}'
fi

# 2. JSHint Check
echo -e "${YELLOW}📋 Running JSHint checks...${NC}"

if command -v jshint &> /dev/null; then
  jshint_output=$(find . -name "*.js" -not -path "./node_modules/*" -exec jshint {} \; 2>&1 || true)
  jshint_issues=$(echo "$jshint_output" | grep -c "error" || echo "0")
  
  if [ "$jshint_issues" -eq 0 ]; then
    echo -e "${GREEN}✅ JSHint: No issues found${NC}"
    update_report "jshint" "passed" 100 '{"issues": []}'
  else
    echo -e "${RED}❌ JSHint: $jshint_issues issues found${NC}"
    echo "$jshint_output" | head -10
    score=$((100 - jshint_issues * 3))
    if [ $score -lt 0 ]; then score=0; fi
    update_report "jshint" "failed" "$score" "{\"issues\": $jshint_issues}"
    EXIT_CODE=1
  fi
else
  echo -e "${YELLOW}⚠️  JSHint not found, skipping...${NC}"
  update_report "jshint" "skipped" 80 '{"issues": [], "reason": "JSHint not available"}'
fi

# 3. Security Check
echo -e "${YELLOW}🔒 Running security checks...${NC}"

security_issues=0
security_vulnerabilities=[]

# Check for common security patterns
echo "  Checking for hardcoded secrets..."
secrets_found=$(grep -r -n -i "password\|secret\|key\|token" --include="*.js" . | grep -v node_modules | wc -l || echo "0")

echo "  Checking for eval() usage..."
eval_found=$(grep -r -n "eval(" --include="*.js" . | grep -v node_modules | wc -l || echo "0")

echo "  Checking for innerHTML usage..."
innerhtml_found=$(grep -r -n "innerHTML" --include="*.js" . | grep -v node_modules | wc -l || echo "0")

total_security_issues=$((secrets_found + eval_found + innerhtml_found))

if [ "$total_security_issues" -eq 0 ]; then
  echo -e "${GREEN}✅ Security: No obvious vulnerabilities found${NC}"
  update_report "security" "passed" 95 '{"vulnerabilities": []}'
else
  echo -e "${YELLOW}⚠️  Security: $total_security_issues potential issues found${NC}"
  echo "  - Hardcoded secrets: $secrets_found"
  echo "  - eval() usage: $eval_found"
  echo "  - innerHTML usage: $innerhtml_found"
  score=$((95 - total_security_issues * 5))
  if [ $score -lt 0 ]; then score=0; fi
  update_report "security" "warning" "$score" "{\"vulnerabilities\": $total_security_issues}"
fi

# 4. Code Formatting Check
echo -e "${YELLOW}🎨 Checking code formatting...${NC}"

# Check for consistent indentation
inconsistent_indent=$(find . -name "*.js" -not -path "./node_modules/*" -exec grep -l -P "^\t" {} \; | wc -l || echo "0")

# Check for trailing whitespace
trailing_whitespace=$(find . -name "*.js" -not -path "./node_modules/*" -exec grep -l " $" {} \; | wc -l || echo "0")

# Check for long lines (>120 chars)
long_lines=$(find . -name "*.js" -not -path "./node_modules/*" -exec awk 'length($0) > 120 {print FILENAME":"NR":"$0}' {} \; | wc -l || echo "0")

total_format_issues=$((inconsistent_indent + trailing_whitespace + long_lines))

if [ "$total_format_issues" -eq 0 ]; then
  echo -e "${GREEN}✅ Formatting: Code is well formatted${NC}"
  update_report "formatting" "passed" 100 '{"files": []}'
else
  echo -e "${YELLOW}⚠️  Formatting: $total_format_issues issues found${NC}"
  echo "  - Inconsistent indentation: $inconsistent_indent files"
  echo "  - Trailing whitespace: $trailing_whitespace files"
  echo "  - Long lines (>120 chars): $long_lines"
  score=$((100 - total_format_issues * 2))
  if [ $score -lt 0 ]; then score=0; fi
  update_report "formatting" "warning" "$score" "{\"files\": $total_format_issues}"
fi

# 5. Code Complexity Check
echo -e "${YELLOW}📊 Analyzing code complexity...${NC}"

# Count functions and estimate complexity
total_functions=$(grep -r -c "function\|=>" --include="*.js" . | grep -v node_modules | awk -F: '{sum += $2} END {print sum+0}')
large_functions=$(find . -name "*.js" -not -path "./node_modules/*" -exec awk '/function|=>/ {start=NR} /^}/ {if(NR-start > 50) print FILENAME":"start":"NR}' {} \; | wc -l || echo "0")

if [ "$large_functions" -eq 0 ]; then
  echo -e "${GREEN}✅ Complexity: Functions are well-sized${NC}"
  update_report "complexity" "passed" 95 '{"functions": []}'
else
  echo -e "${YELLOW}⚠️  Complexity: $large_functions functions are too large (>50 lines)${NC}"
  score=$((95 - large_functions * 5))
  if [ $score -lt 0 ]; then score=0; fi
  update_report "complexity" "warning" "$score" "{\"functions\": $large_functions}"
fi

# 6. Documentation Check
echo -e "${YELLOW}📚 Checking documentation coverage...${NC}"

total_js_files=$(find . -name "*.js" -not -path "./node_modules/*" | wc -l)
documented_files=$(grep -l -r "\/\*\*" --include="*.js" . | grep -v node_modules | wc -l || echo "0")

if [ "$total_js_files" -gt 0 ]; then
  doc_coverage=$((documented_files * 100 / total_js_files))
else
  doc_coverage=0
fi

if [ "$doc_coverage" -ge 80 ]; then
  echo -e "${GREEN}✅ Documentation: ${doc_coverage}% coverage${NC}"
  update_report "documentation" "passed" "$doc_coverage" "{\"coverage\": $doc_coverage}"
elif [ "$doc_coverage" -ge 60 ]; then
  echo -e "${YELLOW}⚠️  Documentation: ${doc_coverage}% coverage (target: 80%)${NC}"
  update_report "documentation" "warning" "$doc_coverage" "{\"coverage\": $doc_coverage}"
else
  echo -e "${RED}❌ Documentation: ${doc_coverage}% coverage (target: 80%)${NC}"
  update_report "documentation" "failed" "$doc_coverage" "{\"coverage\": $doc_coverage}"
  EXIT_CODE=1
fi

# 7. Dependencies Check
echo -e "${YELLOW}📦 Checking dependencies...${NC}"

if [ -f "package.json" ]; then
  if command -v npm &> /dev/null; then
    outdated_output=$(npm outdated --json 2>/dev/null || echo "{}")
    outdated_count=$(echo "$outdated_output" | jq 'keys | length' 2>/dev/null || echo "0")
    
    if [ "$outdated_count" -eq 0 ]; then
      echo -e "${GREEN}✅ Dependencies: All packages are up to date${NC}"
      update_report "dependencies" "passed" 100 '{"outdated": []}'
    else
      echo -e "${YELLOW}⚠️  Dependencies: $outdated_count packages need updates${NC}"
      score=$((100 - outdated_count * 5))
      if [ $score -lt 0 ]; then score=0; fi
      update_report "dependencies" "warning" "$score" "{\"outdated\": $outdated_count}"
    fi
  else
    echo -e "${YELLOW}⚠️  npm not found, skipping dependency check${NC}"
    update_report "dependencies" "skipped" 80 '{"outdated": [], "reason": "npm not available"}'
  fi
else
  echo -e "${YELLOW}⚠️  No package.json found${NC}"
  update_report "dependencies" "skipped" 90 '{"outdated": [], "reason": "No package.json"}'
fi

# 8. Performance Metrics
echo -e "${YELLOW}⚡ Checking performance metrics...${NC}"

# File size analysis
large_files=$(find . -name "*.js" -not -path "./node_modules/*" -size +100k | wc -l || echo "0")
total_size=$(find . -name "*.js" -not -path "./node_modules/*" -exec stat -f%z {} + 2>/dev/null | awk '{sum += $1} END {print sum+0}' || echo "0")

if [ "$large_files" -eq 0 ]; then
  echo -e "${GREEN}✅ Performance: No oversized files${NC}"
  update_report "performance" "passed" 95 '{"metrics": {"large_files": 0}}'
else
  echo -e "${YELLOW}⚠️  Performance: $large_files files are large (>100KB)${NC}"
  score=$((95 - large_files * 10))
  if [ $score -lt 0 ]; then score=0; fi
  update_report "performance" "warning" "$score" "{\"metrics\": {\"large_files\": $large_files}}"
fi

# Calculate overall score and grade
calculate_overall_score

# Display final results
echo ""
echo -e "${BLUE}📊 FINAL QUALITY REPORT${NC}"
echo "========================"

final_score=$(jq -r '.overall.score' "$QUALITY_REPORT_FILE")
final_grade=$(jq -r '.overall.grade' "$QUALITY_REPORT_FILE")

if (( $(echo "$final_score >= 85" | bc -l) )); then
  echo -e "${GREEN}🏆 Overall Score: $final_score% (Grade: $final_grade)${NC}"
elif (( $(echo "$final_score >= 70" | bc -l) )); then
  echo -e "${YELLOW}📈 Overall Score: $final_score% (Grade: $final_grade)${NC}"
else
  echo -e "${RED}📉 Overall Score: $final_score% (Grade: $final_grade)${NC}"
  EXIT_CODE=1
fi

# Display check results
echo ""
jq -r '.checks | to_entries[] | "  " + .key + ": " + .value.status + " (" + (.value.score | tostring) + "%)"' "$QUALITY_REPORT_FILE"

echo ""
echo -e "${BLUE}📋 Recommendations:${NC}"

# Generate recommendations based on failed checks
if [ "$(jq -r '.checks.eslint.status' "$QUALITY_REPORT_FILE")" = "failed" ]; then
  echo "  • Fix ESLint issues to improve code quality"
fi

if [ "$(jq -r '.checks.security.status' "$QUALITY_REPORT_FILE")" = "warning" ]; then
  echo "  • Review security warnings and implement fixes"
fi

if [ "$(jq -r '.checks.documentation.score' "$QUALITY_REPORT_FILE" | cut -d. -f1)" -lt 80 ]; then
  echo "  • Improve documentation coverage (target: 80%)"
fi

if [ "$(jq -r '.checks.formatting.status' "$QUALITY_REPORT_FILE")" = "warning" ]; then
  echo "  • Consider using Prettier for consistent formatting"
fi

echo ""
echo -e "${BLUE}📄 Full report saved to: $QUALITY_REPORT_FILE${NC}"
echo ""
echo -e "${BLUE}© 2025 Fahed Mlaiel. All rights reserved.${NC}"
echo -e "${BLUE}Contact: mlaiel@live.de${NC}"
echo ""

exit $EXIT_CODE