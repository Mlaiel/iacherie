#!/usr/bin/env python3
"""Ainflue Production Security Validator
Author: Fahed Mlaiel (mlaiel@live.de)

Validates production configuration and secrets for security compliance.
"""

import os
import re
import sys
import json
import hashlib
import secrets
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ValidationResult:
    """
Validation result for a security check."""
    check_name: str
    passed: bool
    message: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    recommendation: str = ""


class ProductionSecurityValidator:
    """Validates production configuration security."""
    
    def __init__(self, env_file_path: str = ".env.production"):
        self.env_file_path = env_file_path
        self.validation_results: List[ValidationResult] = []
        self.critical_secrets = [
            'JWT_SECRET_KEY', 'PROD_JWT_SECRET', 'ENCRYPTION_KEY', 'PROD_ENCRYPTION_KEY',
            'POSTGRES_PASSWORD', 'REDIS_PASSWORD', 'MONGODB_PASSWORD',
            'STRIPE_SECRET_KEY', 'OPENAI_API_KEY', 'AWS_SECRET_ACCESS_KEY'
        ]
        
    def validate_all(self) -> List[ValidationResult]:
        """Run all security validations."""
        self.validation_results = []
        
        # Load environment variables
        env_vars = self._load_env_file()
        
        if not env_vars:
            self.validation_results.append(ValidationResult(
                check_name="env_file_load",
                passed=False,
                message=f"Could not load environment file: {self.env_file_path}",
                severity="critical",
                recommendation="Ensure .env.production file exists and is readable"
            ))
            return self.validation_results
        
        # Run validation checks
        self._validate_secret_strength(env_vars)
        self._validate_placeholder_values(env_vars)
        self._validate_production_settings(env_vars)
        self._validate_security_headers(env_vars)
        self._validate_database_security(env_vars)
        self._validate_api_security(env_vars)
        self._validate_monitoring_security(env_vars)
        
        return self.validation_results
    
    def _load_env_file(self) -> Dict[str, str]:
        """Load environment variables from file."""
        env_vars = {}
        
        if not os.path.exists(self.env_file_path):
            return env_vars
            
        try:
            with open(self.env_file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        except Exception as e:
            print(f"Error loading env file: {e}")
            
        return env_vars
    
    def _validate_secret_strength(self, env_vars: Dict[str, str]) -> None:
        """Validate the strength of critical secrets."""
        for secret_name in self.critical_secrets:
            value = env_vars.get(secret_name, "")
            
            # Check if secret exists
            if not value:
                self.validation_results.append(ValidationResult(
                    check_name=f"secret_exists_{secret_name}",
                    passed=False,
                    message=f"Critical secret {secret_name} is not set",
                    severity="critical",
                    recommendation=f"Set a strong value for {secret_name}"
                ))
                continue
            
            # Check for placeholder values
            if value.startswith("${") or "placeholder" in value.lower() or "change_me" in value.lower():
                self.validation_results.append(ValidationResult(
                    check_name=f"secret_placeholder_{secret_name}",
                    passed=False,
                    message=f"Secret {secret_name} contains placeholder value",
                    severity="critical",
                    recommendation=f"Replace placeholder with actual secure value for {secret_name}"
                ))
                continue
            
            # Check secret length
            min_length = 32 if "SECRET" in secret_name or "KEY" in secret_name else 16
            if len(value) < min_length:
                self.validation_results.append(ValidationResult(
                    check_name=f"secret_length_{secret_name}",
                    passed=False,
                    message=f"Secret {secret_name} is too short ({len(value)} chars, minimum {min_length})",
                    severity="high",
                    recommendation=f"Use at least {min_length} characters for {secret_name}"
                ))
            
            # Check secret entropy
            entropy = self._calculate_entropy(value)
            min_entropy = 4.0  # bits per character
            if entropy < min_entropy:
                self.validation_results.append(ValidationResult(
                    check_name=f"secret_entropy_{secret_name}",
                    passed=False,
                    message=f"Secret {secret_name} has low entropy ({entropy:.2f} bits/char)",
                    severity="medium",
                    recommendation=f"Use more diverse characters in {secret_name}"
                ))
    
    def _validate_placeholder_values(self, env_vars: Dict[str, str]) -> None:
        """Check for remaining placeholder values in production."""
        placeholder_patterns = [
            r'placeholder', r'change_me', r'your_.*_here', r'example',
            r'test', r'demo', r'localhost', r'127\.0\.0\.1'
        ]
        
        for key, value in env_vars.items():
            value_lower = value.lower()
            for pattern in placeholder_patterns:
                if re.search(pattern, value_lower):
                    severity = "critical" if key in self.critical_secrets else "high"
                    self.validation_results.append(ValidationResult(
                        check_name=f"placeholder_value_{key}",
                        passed=False,
                        message=f"Variable {key} contains placeholder/test value: {value[:50]}...",
                        severity=severity,
                        recommendation=f"Replace with actual production value for {key}"
                    ))
                    break
    
    def _validate_production_settings(self, env_vars: Dict[str, str]) -> None:
        """Validate production-specific settings."""
        # Debug mode check
        debug = env_vars.get('DEBUG', 'false').lower()
        if debug not in ['false', '0', 'no']:
            self.validation_results.append(ValidationResult(
                check_name="debug_mode",
                passed=False,
                message="DEBUG mode is enabled in production",
                severity="critical",
                recommendation="Set DEBUG=false for production"
            ))
        
        # Environment check
        environment = env_vars.get('ENVIRONMENT', '').lower()
        if environment != 'production':
            self.validation_results.append(ValidationResult(
                check_name="environment_setting",
                passed=False,
                message=f"ENVIRONMENT is set to '{environment}' instead of 'production'",
                severity="high",
                recommendation="Set ENVIRONMENT=production"
            ))
        
        # HTTPS enforcement
        force_https = env_vars.get('FORCE_HTTPS', 'false').lower()
        if force_https not in ['true', '1', 'yes']:
            self.validation_results.append(ValidationResult(
                check_name="https_enforcement",
                passed=False,
                message="HTTPS is not enforced",
                severity="high",
                recommendation="Set FORCE_HTTPS=true"
            ))
    
    def _validate_security_headers(self, env_vars: Dict[str, str]) -> None:
        """Validate security headers configuration."""
        # HSTS configuration
        hsts_max_age = env_vars.get('HSTS_MAX_AGE', '0')
        try:
            hsts_age = int(hsts_max_age)
            if hsts_age < 31536000:  # 1 year
                self.validation_results.append(ValidationResult(
                    check_name="hsts_max_age",
                    passed=False,
                    message=f"HSTS max age is too short: {hsts_age} seconds",
                    severity="medium",
                    recommendation="Set HSTS_MAX_AGE to at least 31536000 (1 year)"
                ))
        except ValueError:
            self.validation_results.append(ValidationResult(
                check_name="hsts_max_age_format",
                passed=False,
                message="HSTS_MAX_AGE is not a valid number",
                severity="medium",
                recommendation="Set HSTS_MAX_AGE to a valid number of seconds"
            ))
        
        # Content Security Policy
        csp_default = env_vars.get('CSP_DEFAULT_SRC', '')
        if "'unsafe-eval'" in csp_default or "'unsafe-inline'" in csp_default:
            self.validation_results.append(ValidationResult(
                check_name="csp_unsafe_directives",
                passed=False,
                message="CSP contains unsafe directives",
                severity="medium",
                recommendation="Remove 'unsafe-eval' and 'unsafe-inline' from CSP where possible"
            ))
    
    def _validate_database_security(self, env_vars: Dict[str, str]) -> None:
        """Validate database security configuration."""
        # PostgreSQL SSL mode
        postgres_host = env_vars.get('POSTGRES_HOST', '')
        if 'localhost' in postgres_host or '127.0.0.1' in postgres_host:
            self.validation_results.append(ValidationResult(
                check_name="postgres_localhost",
                passed=False,
                message="PostgreSQL host is set to localhost",
                severity="high",
                recommendation="Use proper cluster hostname for PostgreSQL"
            ))
        
        # Database pool sizes
        pool_size = env_vars.get('DB_POOL_SIZE', '0')
        try:
            pool_int = int(pool_size)
            if pool_int < 10:
                self.validation_results.append(ValidationResult(
                    check_name="db_pool_size",
                    passed=False,
                    message=f"Database pool size is too small: {pool_int}",
                    severity="medium",
                    recommendation="Increase DB_POOL_SIZE to at least 10 for production"
                ))
        except ValueError:
            pass
    
    def _validate_api_security(self, env_vars: Dict[str, str]) -> None:
        """Validate API security settings."""
        # Rate limiting
        rate_limit = env_vars.get('API_RATE_LIMIT', '0')
        try:
            rate_int = int(rate_limit)
            if rate_int < 100:
                self.validation_results.append(ValidationResult(
                    check_name="api_rate_limit",
                    passed=False,
                    message=f"API rate limit is too low: {rate_int}",
                    severity="medium",
                    recommendation="Set appropriate rate limits for production load"
                ))
        except ValueError:
            pass
        
        # CORS origins
        cors_origins = env_vars.get('CORS_ORIGINS', '')
        if '*' in cors_origins:
            self.validation_results.append(ValidationResult(
                check_name="cors_wildcard",
                passed=False,
                message="CORS origins contains wildcard (*)",
                severity="high",
                recommendation="Specify exact domains instead of using wildcard"
            ))
    
    def _validate_monitoring_security(self, env_vars: Dict[str, str]) -> None:
        """Validate monitoring and logging security."""
        # Sentry DSN
        sentry_dsn = env_vars.get('SENTRY_DSN', '')
        if not sentry_dsn or 'placeholder' in sentry_dsn:
            self.validation_results.append(ValidationResult(
                check_name="sentry_configuration",
                passed=False,
                message="Sentry DSN is not configured",
                severity="medium",
                recommendation="Configure Sentry for error tracking in production"
            ))
        
        # Log level
        log_level = env_vars.get('LOG_LEVEL', '').upper()
        if log_level in ['DEBUG', 'TRACE']:
            self.validation_results.append(ValidationResult(
                check_name="log_level",
                passed=False,
                message=f"Log level is set to {log_level}",
                severity="medium",
                recommendation="Use INFO or WARNING log level for production"
            ))
    
    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of text."""
        if not text:
            return 0.0
        
        # Count character frequencies
        freq = {}
        for char in text:
            freq[char] = freq.get(char, 0) + 1
        
        # Calculate entropy
        length = len(text)
        entropy = 0.0
        for count in freq.values():
            prob = count / length
            entropy -= prob * (prob.bit_length() - 1) if prob > 0 else 0
        
        return entropy
    
    def generate_secure_key(self, length: int = 32) -> str:
        """
Generate a cryptographically secure random key."""
        return secrets.token_urlsafe(length)
    
    def print_report(self) -> None:
        """
Print validation report."""
        print("=" * 80)
        print("AINFLUE PRODUCTION SECURITY VALIDATION REPORT")
        print("=" * 80)
        
        # Count results by severity
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        passed_count = 0
        
        for result in self.validation_results:
            if result.passed:
                passed_count += 1
            else:
                severity_counts[result.severity] += 1
        
        # Print summary
        total_checks = len(self.validation_results)
        print(f"\nSUMMARY:")
        print(f"Total checks: {total_checks}")
        print(f"Passed: {passed_count}")
        print(f"Failed: {total_checks - passed_count}")
        print(f"Critical issues: {severity_counts['critical']}")
        print(f"High issues: {severity_counts['high']}")
        print(f"Medium issues: {severity_counts['medium']}")
        print(f"Low issues: {severity_counts['low']}")
        
        # Print detailed results
        print(f"\nDETAILED RESULTS:")
        print("-" * 80)
        
        for result in sorted(self.validation_results, key=lambda x: (x.severity, x.check_name)):
            status = "✅ PASS" if result.passed else f"❌ FAIL ({result.severity.upper()})"
            print(f"{status}: {result.check_name}")
            print(f"  Message: {result.message}")
            if result.recommendation:
                print(f"  Recommendation: {result.recommendation}")
            print()
        
        # Exit with appropriate code
        critical_issues = severity_counts['critical']
        high_issues = severity_counts['high']
        
        if critical_issues > 0:
            print(f"❌ VALIDATION FAILED: {critical_issues} critical security issues found!")
            sys.exit(1)
        elif high_issues > 0:
            print(f"⚠️  VALIDATION WARNING: {high_issues} high severity issues found!")
            sys.exit(2)
        else:
            print("✅ VALIDATION PASSED: No critical or high severity issues found!")
            sys.exit(0)


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate Ainflue production security configuration")
    parser.add_argument("--env-file", default=".env.production", help="Environment file to validate")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--generate-keys", action="store_true", help="Generate secure keys")
    
    args = parser.parse_args()
    
    if args.generate_keys:
        print("Generated secure keys:")
        print(f"JWT_SECRET_KEY={secrets.token_urlsafe(32)}")
        print(f"ENCRYPTION_KEY={secrets.token_urlsafe(32)}")
        print(f"OAUTH2_SECRET_KEY={secrets.token_urlsafe(32)}")
        print(f"PASSWORD_SALT={secrets.token_urlsafe(16)}")
        return
    
    validator = ProductionSecurityValidator(args.env_file)
    results = validator.validate_all()
    
    if args.json:
        json_results = []
        for result in results:
            json_results.append({
                'check_name': result.check_name,
                'passed': result.passed,
                'message': result.message,
                'severity': result.severity,
                'recommendation': result.recommendation
            })
        print(json.dumps(json_results, indent=2))
    else:
        validator.print_report()


if __name__ == "__main__":
    main()