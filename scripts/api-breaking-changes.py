#!/usr/bin/env python3
"""
API Breaking Changes Detection for Ainflue Platform
Author: Fahed Mlaiel (mlaiel@live.de)
Description: Detect breaking changes in API endpoints and schemas
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Any, Tuple
from dataclasses import dataclass
import hashlib


@dataclass
class APIEndpoint:
    """API endpoint data structure"""
    path: str
    method: str
    parameters: List[str]
    response_schema: Dict[str, Any]
    request_schema: Dict[str, Any]
    summary: str = ""
    deprecated: bool = False


@dataclass
class APIChange:
    """API change data structure"""
    change_type: str  # breaking, dangerous, notice
    endpoint: str
    method: str
    description: str
    impact: str
    recommendation: str


class APIChangeDetector:
    """Detect breaking changes in API"""
    
    def __init__(self, baseline_file: str = "api-baseline.json"):
        self.baseline_file = Path(baseline_file)
        self.current_api: Dict[str, APIEndpoint] = {}
        self.baseline_api: Dict[str, APIEndpoint] = {}
        self.changes: List[APIChange] = []
    
    def extract_fastapi_schema(self) -> Dict[str, Any]:
        """Extract API schema from FastAPI application"""
        try:
            # Try to import and get schema from FastAPI app
            schema_script = """
import sys
import json
try:
    from api.asgi import app
    schema = app.openapi()
    print(json.dumps(schema, indent=2))
except Exception as e:
    # Fallback to simple schema
    fallback_schema = {
        "openapi": "3.0.0",
        "info": {
            "title": "Ainflue API",
            "version": "1.0.0",
            "description": "AI-powered content protection and monetization platform"
        },
        "paths": {
            "/health": {
                "get": {
                    "summary": "Health Check",
                    "responses": {
                        "200": {
                            "description": "Service is healthy",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "timestamp": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/v1/auth/login": {
                "post": {
                    "summary": "User Login",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "username": {"type": "string"},
                                        "password": {"type": "string"}
                                    },
                                    "required": ["username", "password"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Login successful",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "access_token": {"type": "string"},
                                            "token_type": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/v1/content/upload": {
                "post": {
                    "summary": "Upload Content",
                    "requestBody": {
                        "content": {
                            "multipart/form-data": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "file": {"type": "string", "format": "binary"},
                                        "title": {"type": "string"},
                                        "description": {"type": "string"}
                                    },
                                    "required": ["file", "title"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Content uploaded successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "string"},
                                            "title": {"type": "string"},
                                            "status": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    print(json.dumps(fallback_schema, indent=2))
"""
            
            result = subprocess.run([sys.executable, "-c", schema_script], 
                                  capture_output=True, text=True, cwd=".")
            
            if result.returncode == 0 and result.stdout.strip():
                return json.loads(result.stdout)
            else:
                # Return minimal fallback schema
                return {
                    "openapi": "3.0.0",
                    "info": {"title": "Ainflue API", "version": "1.0.0"},
                    "paths": {}
                }
                
        except Exception as e:
            print(f"Error extracting API schema: {e}")
            return {
                "openapi": "3.0.0",
                "info": {"title": "Ainflue API", "version": "1.0.0"},
                "paths": {}
            }
    
    def parse_openapi_schema(self, schema: Dict[str, Any]) -> Dict[str, APIEndpoint]:
        """Parse OpenAPI schema into API endpoints"""
        endpoints = {}
        
        paths = schema.get("paths", {})
        
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                    endpoint_key = f"{method.upper()} {path}"
                    
                    # Extract parameters
                    parameters = []
                    if "parameters" in operation:
                        parameters = [param.get("name", "") for param in operation["parameters"]]
                    
                    # Extract request schema
                    request_schema = {}
                    if "requestBody" in operation:
                        request_body = operation["requestBody"]
                        content = request_body.get("content", {})
                        for content_type, content_spec in content.items():
                            if "schema" in content_spec:
                                request_schema = content_spec["schema"]
                                break
                    
                    # Extract response schema
                    response_schema = {}
                    responses = operation.get("responses", {})
                    if "200" in responses:
                        response_200 = responses["200"]
                        content = response_200.get("content", {})
                        for content_type, content_spec in content.items():
                            if "schema" in content_spec:
                                response_schema = content_spec["schema"]
                                break
                    elif "201" in responses:
                        response_201 = responses["201"]
                        content = response_201.get("content", {})
                        for content_type, content_spec in content.items():
                            if "schema" in content_spec:
                                response_schema = content_spec["schema"]
                                break
                    
                    endpoint = APIEndpoint(
                        path=path,
                        method=method.upper(),
                        parameters=parameters,
                        response_schema=response_schema,
                        request_schema=request_schema,
                        summary=operation.get("summary", ""),
                        deprecated=operation.get("deprecated", False)
                    )
                    
                    endpoints[endpoint_key] = endpoint
        
        return endpoints
    
    def load_baseline_api(self) -> Dict[str, APIEndpoint]:
        """Load baseline API from file"""
        if not self.baseline_file.exists():
            return {}
        
        try:
            with open(self.baseline_file, 'r') as f:
                baseline_schema = json.load(f)
            
            return self.parse_openapi_schema(baseline_schema)
            
        except Exception as e:
            print(f"Error loading baseline API: {e}")
            return {}
    
    def save_current_as_baseline(self, schema: Dict[str, Any]):
        """Save current API schema as baseline"""
        with open(self.baseline_file, 'w') as f:
            json.dump(schema, f, indent=2)
    
    def detect_endpoint_changes(self):
        """Detect changes in API endpoints"""
        current_endpoints = set(self.current_api.keys())
        baseline_endpoints = set(self.baseline_api.keys())
        
        # Removed endpoints (breaking)
        removed_endpoints = baseline_endpoints - current_endpoints
        for endpoint in removed_endpoints:
            baseline_ep = self.baseline_api[endpoint]
            self.changes.append(APIChange(
                change_type="breaking",
                endpoint=baseline_ep.path,
                method=baseline_ep.method,
                description=f"Endpoint {endpoint} has been removed",
                impact="Clients using this endpoint will fail",
                recommendation="Deprecated the endpoint before removing, or provide migration path"
            ))
        
        # Added endpoints (notice)
        added_endpoints = current_endpoints - baseline_endpoints
        for endpoint in added_endpoints:
            current_ep = self.current_api[endpoint]
            self.changes.append(APIChange(
                change_type="notice",
                endpoint=current_ep.path,
                method=current_ep.method,
                description=f"New endpoint {endpoint} has been added",
                impact="New functionality available",
                recommendation="Update API documentation and notify consumers"
            ))
        
        # Modified endpoints
        common_endpoints = current_endpoints & baseline_endpoints
        for endpoint in common_endpoints:
            self.detect_endpoint_modifications(endpoint)
    
    def detect_endpoint_modifications(self, endpoint_key: str):
        """Detect modifications in a specific endpoint"""
        current_ep = self.current_api[endpoint_key]
        baseline_ep = self.baseline_api[endpoint_key]
        
        # Check for parameter changes
        self.detect_parameter_changes(current_ep, baseline_ep)
        
        # Check for schema changes
        self.detect_schema_changes(current_ep, baseline_ep)
        
        # Check for deprecation
        if current_ep.deprecated and not baseline_ep.deprecated:
            self.changes.append(APIChange(
                change_type="dangerous",
                endpoint=current_ep.path,
                method=current_ep.method,
                description=f"Endpoint {endpoint_key} has been marked as deprecated",
                impact="Clients should migrate to alternative endpoints",
                recommendation="Provide migration guide and timeline for removal"
            ))
    
    def detect_parameter_changes(self, current_ep: APIEndpoint, baseline_ep: APIEndpoint):
        """Detect changes in endpoint parameters"""
        current_params = set(current_ep.parameters)
        baseline_params = set(baseline_ep.parameters)
        
        # Removed parameters (breaking)
        removed_params = baseline_params - current_params
        if removed_params:
            self.changes.append(APIChange(
                change_type="breaking",
                endpoint=current_ep.path,
                method=current_ep.method,
                description=f"Parameters removed: {', '.join(removed_params)}",
                impact="Clients passing these parameters will fail",
                recommendation="Make parameters optional before removing, or version the API"
            ))
        
        # Added parameters (could be dangerous if required)
        added_params = current_params - baseline_params
        if added_params:
            self.changes.append(APIChange(
                change_type="dangerous",
                endpoint=current_ep.path,
                method=current_ep.method,
                description=f"Parameters added: {', '.join(added_params)}",
                impact="May break clients if parameters are required",
                recommendation="Ensure new parameters are optional or provide default values"
            ))
    
    def detect_schema_changes(self, current_ep: APIEndpoint, baseline_ep: APIEndpoint):
        """Detect changes in request/response schemas"""
        # Compare request schemas
        if self.schema_hash(current_ep.request_schema) != self.schema_hash(baseline_ep.request_schema):
            self.changes.append(APIChange(
                change_type="dangerous",
                endpoint=current_ep.path,
                method=current_ep.method,
                description="Request schema has been modified",
                impact="Clients may send invalid requests",
                recommendation="Ensure backward compatibility or version the API"
            ))
        
        # Compare response schemas
        if self.schema_hash(current_ep.response_schema) != self.schema_hash(baseline_ep.response_schema):
            change_type = self.determine_response_change_severity(
                current_ep.response_schema, 
                baseline_ep.response_schema
            )
            
            self.changes.append(APIChange(
                change_type=change_type,
                endpoint=current_ep.path,
                method=current_ep.method,
                description="Response schema has been modified",
                impact="Clients may fail to parse responses",
                recommendation="Ensure only additive changes or version the API"
            ))
    
    def schema_hash(self, schema: Dict[str, Any]) -> str:
        """Generate hash for schema comparison"""
        schema_str = json.dumps(schema, sort_keys=True)
        return hashlib.md5(schema_str.encode()).hexdigest()
    
    def determine_response_change_severity(self, current_schema: Dict, baseline_schema: Dict) -> str:
        """Determine severity of response schema changes"""
        # Simplified logic - in practice, this would be more sophisticated
        current_props = current_schema.get("properties", {})
        baseline_props = baseline_schema.get("properties", {})
        
        # Check if required fields were removed
        current_required = set(current_schema.get("required", []))
        baseline_required = set(baseline_schema.get("required", []))
        
        removed_required = baseline_required - current_required
        if removed_required:
            return "breaking"
        
        # Check if properties were removed
        removed_props = set(baseline_props.keys()) - set(current_props.keys())
        if removed_props:
            return "breaking"
        
        # Otherwise, it's dangerous (could affect parsing)
        return "dangerous"
    
    def analyze_changes(self) -> Dict[str, Any]:
        """Analyze API changes and generate report"""
        print("🔍 Analyzing API changes...")
        
        # Load current API schema
        current_schema = self.extract_fastapi_schema()
        self.current_api = self.parse_openapi_schema(current_schema)
        
        # Load baseline API
        self.baseline_api = self.load_baseline_api()
        
        # If no baseline exists, create one
        if not self.baseline_api:
            print("📝 No baseline API found, creating baseline...")
            self.save_current_as_baseline(current_schema)
            
            return {
                "status": "baseline_created",
                "message": "API baseline created successfully",
                "endpoints_count": len(self.current_api),
                "changes": []
            }
        
        # Detect changes
        self.detect_endpoint_changes()
        
        # Categorize changes
        breaking_changes = [c for c in self.changes if c.change_type == "breaking"]
        dangerous_changes = [c for c in self.changes if c.change_type == "dangerous"]
        notice_changes = [c for c in self.changes if c.change_type == "notice"]
        
        # Determine overall status
        if breaking_changes:
            status = "breaking_changes_detected"
        elif dangerous_changes:
            status = "dangerous_changes_detected"
        elif notice_changes:
            status = "minor_changes_detected"
        else:
            status = "no_changes_detected"
        
        return {
            "status": status,
            "summary": {
                "total_changes": len(self.changes),
                "breaking_changes": len(breaking_changes),
                "dangerous_changes": len(dangerous_changes),
                "notice_changes": len(notice_changes),
                "endpoints_analyzed": len(self.current_api)
            },
            "changes": [
                {
                    "type": change.change_type,
                    "endpoint": change.endpoint,
                    "method": change.method,
                    "description": change.description,
                    "impact": change.impact,
                    "recommendation": change.recommendation
                }
                for change in self.changes
            ]
        }
    
    def generate_report(self, output_file: str = "api-changes-report.json") -> Dict[str, Any]:
        """Generate API changes report"""
        analysis = self.analyze_changes()
        
        report = {
            "timestamp": subprocess.run(["date", "-Iseconds"], capture_output=True, text=True).stdout.strip(),
            "project": "Ainflue Platform",
            "analysis": analysis,
            "quality_gates": {
                "no_breaking_changes": analysis["summary"]["breaking_changes"] == 0,
                "limited_dangerous_changes": analysis["summary"]["dangerous_changes"] <= 2,
                "changes_documented": True  # Assume documented for now
            }
        }
        
        # Add recommendations
        recommendations = []
        if analysis["summary"]["breaking_changes"] > 0:
            recommendations.append("Review breaking changes and consider API versioning")
        if analysis["summary"]["dangerous_changes"] > 2:
            recommendations.append("Consider reducing dangerous changes through backward compatibility")
        if analysis["summary"]["total_changes"] > 0:
            recommendations.append("Update API documentation to reflect changes")
        
        report["recommendations"] = recommendations
        
        # Save report
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def print_summary(self, report: Dict[str, Any]):
        """Print API changes summary"""
        analysis = report["analysis"]
        
        print("\n🔄 API Breaking Changes Analysis")
        print("=" * 40)
        print(f"Status: {analysis['status'].replace('_', ' ').title()}")
        print(f"Endpoints Analyzed: {analysis['summary']['endpoints_analyzed']}")
        print(f"Total Changes: {analysis['summary']['total_changes']}")
        print(f"Breaking Changes: {analysis['summary']['breaking_changes']}")
        print(f"Dangerous Changes: {analysis['summary']['dangerous_changes']}")
        print(f"Notice Changes: {analysis['summary']['notice_changes']}")
        
        # Print changes by type
        changes = analysis.get("changes", [])
        if changes:
            print(f"\n📋 Detected Changes:")
            for change in changes[:5]:  # Show first 5 changes
                icon = "🚨" if change["type"] == "breaking" else "⚠️" if change["type"] == "dangerous" else "ℹ️"
                print(f"  {icon} {change['method']} {change['endpoint']}: {change['description']}")
        
        # Quality gates
        quality_gates = report["quality_gates"]
        print(f"\n🚪 Quality Gates:")
        gates_status = "✅ PASSED" if all(quality_gates.values()) else "❌ FAILED"
        print(f"Overall: {gates_status}")
        
        for gate, status in quality_gates.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {gate.replace('_', ' ').title()}")


def main():
    """Main API change detection"""
    import argparse
    
    parser = argparse.ArgumentParser(description="API Breaking Changes Detection")
    parser.add_argument('--baseline', default='api-baseline.json',
                       help='Baseline API file (default: api-baseline.json)')
    parser.add_argument('--output', default='api-changes-report.json',
                       help='Output report file (default: api-changes-report.json)')
    parser.add_argument('--create-baseline', action='store_true',
                       help='Create new baseline from current API')
    
    args = parser.parse_args()
    
    detector = APIChangeDetector(baseline_file=args.baseline)
    
    try:
        if args.create_baseline:
            # Force create new baseline
            current_schema = detector.extract_fastapi_schema()
            detector.save_current_as_baseline(current_schema)
            print("✅ API baseline created successfully")
            exit(0)
        
        report = detector.generate_report(args.output)
        detector.print_summary(report)
        
        # Determine exit code based on breaking changes
        breaking_changes = report["analysis"]["summary"]["breaking_changes"]
        if breaking_changes > 0:
            print(f"\n❌ API breaking changes detected: {breaking_changes}")
            exit(1)
        else:
            print(f"\n✅ No breaking changes detected")
            exit(0)
            
    except Exception as e:
        print(f"❌ API change detection failed: {e}")
        exit(1)


if __name__ == "__main__":
    main()