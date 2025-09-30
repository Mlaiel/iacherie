#!/usr/bin/env python3
"""
⚡ Enterprise ReDoc Template - Ainflue API Templates
Advanced production-ready ReDoc documentation system with enterprise features

⚠️ PROTECTION INTELLECTUELLE:
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS - Code propriétaire de Fahed Mlaiel
Utilisation commerciale INTERDITE sans autorisation écrite
Reverse engineering STRICTEMENT INTERDIT
Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence  
- Maintenance et mises à jour assurées
- Formation équipe technique fournie
"""

import json
import yaml
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from pathlib import Path
import structlog
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Template, Environment, FileSystemLoader
import aiofiles
import markdown
from datetime import datetime
import re
import base64


class ReDocTemplate:
    """
    🚀 Enterprise ReDoc Template
    
    Fonctionnalités:
    - ✅ ReDoc documentation interactive avancée
    - ✅ Multi-version API support
    - ✅ Custom branding et theming enterprise
    - ✅ Authentication integration
    - ✅ Code samples multi-languages
    - ✅ Try-it-out functionality
    - ✅ Download specifications
    - ✅ Embedded markdown guides
    - ✅ Search et navigation avancée
    - ✅ Analytics et usage tracking
    - ✅ White-label customization
    """
    
    def __init__(
        self,
        title: str = "Ainflue API Documentation",
        description: str = "Enterprise API Documentation",
        version: str = "1.0.0",
        logo_url: Optional[str] = None,
        favicon_url: Optional[str] = None
    ):
        self.title = title
        self.description = description
        self.version = version
        self.logo_url = logo_url
        self.favicon_url = favicon_url
        
        # Logger structuré
        self.logger = structlog.get_logger(__name__)
        
        # Configuration ReDoc
        self.redoc_config = ReDocConfiguration()
        
        # Theme manager
        self.theme_manager = ReDocThemeManager()
        
        # Content manager
        self.content_manager = DocumentationContentManager()
        
        # Code samples generator
        self.code_generator = CodeSamplesGenerator()
        
        # Analytics tracker
        self.analytics = DocumentationAnalytics()
        
        # Version manager
        self.version_manager = APIVersionManager()
        
        # Template environment
        self.template_env = self._setup_template_environment()
    
    def _setup_template_environment(self) -> Environment:
        """Configure l'environnement de templates"""
        
        # Créer le répertoire templates s'il n'existe pas
        templates_dir = Path(__file__).parent / "redoc_templates"
        templates_dir.mkdir(exist_ok=True)
        
        env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=True
        )
        
        # Ajouter des filtres personnalisés
        env.filters['format_json'] = self._format_json_filter
        env.filters['format_yaml'] = self._format_yaml_filter
        env.filters['markdown'] = self._markdown_filter
        
        return env
    
    def generate_redoc_html(
        self,
        openapi_spec: Dict[str, Any],
        custom_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Génère le HTML ReDoc avec configuration avancée"""
        
        # Merger la configuration personnalisée
        config = self.redoc_config.get_config()
        if custom_config:
            config.update(custom_config)
        
        # Préparer les données du template
        template_data = {
            'title': self.title,
            'description': self.description,
            'version': self.version,
            'logo_url': self.logo_url,
            'favicon_url': self.favicon_url,
            'openapi_spec': json.dumps(openapi_spec, indent=2),
            'redoc_config': json.dumps(config, indent=2),
            'custom_css': self.theme_manager.get_custom_css(),
            'custom_js': self._generate_custom_javascript(),
            'analytics_code': self.analytics.get_tracking_code(),
            'api_versions': self.version_manager.get_versions(),
            'current_version': self.version,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Générer le HTML
        template = self._get_redoc_template()
        html_content = template.render(template_data)
        
        return html_content
    
    def _get_redoc_template(self) -> Template:
        """Retourne le template ReDoc principal"""
        
        template_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}{% if version %} - v{{ version }}{% endif %}</title>
    
    {% if favicon_url %}
    <link rel="icon" type="image/x-icon" href="{{ favicon_url }}">
    {% endif %}
    
    <!-- ReDoc CSS -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/redoc@latest/bundles/redoc.standalone.css">
    
    <!-- Custom CSS -->
    <style>
        {{ custom_css }}
        
        /* Ainflue Enterprise Branding */
        .redoc-wrap {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        .api-info-wrap {
            background: white;
            border-radius: 8px;
            margin: 20px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .api-logo img {
            max-height: 60px;
            margin-bottom: 20px;
        }
        
        /* Enterprise Features */
        .version-selector {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 8px 12px;
        }
        
        .download-spec-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 12px 20px;
            cursor: pointer;
            font-weight: bold;
            text-decoration: none;
            display: inline-block;
        }
        
        .download-spec-btn:hover {
            background: #5a6fd8;
        }
        
        /* Code samples enhancement */
        .redoc-json > code {
            background: #f8f9fa;
            padding: 16px;
            border-radius: 4px;
            border-left: 4px solid #667eea;
        }
        
        /* Search enhancement */
        .redoc-search {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }
        
        /* Mobile responsive */
        @media (max-width: 768px) {
            .version-selector {
                position: relative;
                top: auto;
                right: auto;
                margin: 10px 20px;
            }
            
            .download-spec-btn {
                position: relative;
                bottom: auto;
                right: auto;
                margin: 10px 20px;
                display: block;
                text-align: center;
            }
        }
        
        /* Dark mode support */
        @media (prefers-color-scheme: dark) {
            .redoc-wrap {
                background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
            }
            
            .api-info-wrap {
                background: #2d3748;
                color: #e2e8f0;
            }
        }
    </style>
</head>
<body>
    <!-- Version Selector -->
    {% if api_versions|length > 1 %}
    <div class="version-selector">
        <label for="version-select">API Version:</label>
        <select id="version-select" onchange="switchApiVersion(this.value)">
            {% for version_info in api_versions %}
            <option value="{{ version_info.version }}" 
                    {% if version_info.version == current_version %}selected{% endif %}>
                {{ version_info.version }}{% if version_info.is_latest %} (Latest){% endif %}
            </option>
            {% endfor %}
        </select>
    </div>
    {% endif %}
    
    <!-- Download Specification Button -->
    <a href="#" class="download-spec-btn" onclick="downloadSpecification()">
        📥 Download OpenAPI Spec
    </a>
    
    <!-- ReDoc Container -->
    <div id="redoc-container"></div>
    
    <!-- Enterprise Features JavaScript -->
    <script>
        {{ custom_js }}
        
        // Configuration ReDoc
        const redocConfig = {{ redoc_config | safe }};
        
        // Specification data
        const openApiSpec = {{ openapi_spec | safe }};
        
        // Version management
        const apiVersions = {{ api_versions | tojson }};
        const currentVersion = "{{ current_version }}";
        
        // Initialize ReDoc
        function initializeReDoc() {
            Redoc.init(
                openApiSpec,
                {
                    ...redocConfig,
                    // Enterprise enhancements
                    theme: {
                        ...redocConfig.theme,
                        logo: {
                            url: "{{ logo_url }}",
                            backgroundColor: "transparent",
                            altText: "{{ title }}"
                        },
                        typography: {
                            fontSize: "14px",
                            lineHeight: "1.6",
                            code: {
                                fontSize: "13px",
                                fontFamily: "Monaco, 'Cascadia Code', 'Roboto Mono', monospace"
                            }
                        }
                    },
                    scrollYOffset: 60,
                    hideDownloadButton: false,
                    disableSearch: false,
                    onlyRequiredInSamples: false,
                    expandResponses: "200,201",
                    hideHostname: false,
                    hideSingleRequestSampleTab: false,
                    menuToggle: true,
                    nativeScrollbars: false,
                    pathInMiddlePanel: false,
                    requiredPropsFirst: true,
                    sortPropsAlphabetically: true,
                    showExtensions: true,
                    showObjectSchemaExamples: true,
                    unstable_ignoreMimeTypeParameters: false
                },
                document.getElementById('redoc-container')
            );
        }
        
        // Version switching
        function switchApiVersion(version) {
            if (version !== currentVersion) {
                const baseUrl = window.location.href.split('?')[0];
                window.location.href = `${baseUrl}?version=${version}`;
            }
        }
        
        // Download specification
        function downloadSpecification() {
            const specData = JSON.stringify(openApiSpec, null, 2);
            const blob = new Blob([specData], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            
            const link = document.createElement('a');
            link.href = url;
            link.download = `${openApiSpec.info.title}-v${openApiSpec.info.version}-openapi.json`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
            
            // Analytics tracking
            if (typeof gtag !== 'undefined') {
                gtag('event', 'download', {
                    'event_category': 'api_docs',
                    'event_label': 'openapi_spec',
                    'value': 1
                });
            }
        }
        
        // Enhanced search functionality
        function enhanceSearch() {
            // Add keyboard shortcuts
            document.addEventListener('keydown', function(e) {
                // Ctrl/Cmd + K to focus search
                if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                    e.preventDefault();
                    const searchInput = document.querySelector('[data-role="search:input"]');
                    if (searchInput) {
                        searchInput.focus();
                    }
                }
            });
        }
        
        // Copy code samples enhancement
        function enhanceCodeSamples() {
            document.addEventListener('click', function(e) {
                if (e.target.classList.contains('copy-code-btn')) {
                    const codeBlock = e.target.nextElementSibling;
                    const text = codeBlock.textContent;
                    
                    navigator.clipboard.writeText(text).then(function() {
                        e.target.textContent = 'Copied!';
                        setTimeout(() => {
                            e.target.textContent = 'Copy';
                        }, 2000);
                    });
                }
            });
        }
        
        // Theme switching
        function toggleTheme() {
            const body = document.body;
            const isDark = body.classList.contains('dark-theme');
            
            if (isDark) {
                body.classList.remove('dark-theme');
                localStorage.setItem('redoc-theme', 'light');
            } else {
                body.classList.add('dark-theme');
                localStorage.setItem('redoc-theme', 'dark');
            }
        }
        
        // Initialize theme from localStorage
        function initializeTheme() {
            const savedTheme = localStorage.getItem('redoc-theme');
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            
            if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
                document.body.classList.add('dark-theme');
            }
        }
        
        // Print functionality
        function printDocumentation() {
            window.print();
        }
        
        // Initialize all features
        document.addEventListener('DOMContentLoaded', function() {
            initializeTheme();
            initializeReDoc();
            enhanceSearch();
            enhanceCodeSamples();
            
            // Add print button
            const printBtn = document.createElement('button');
            printBtn.textContent = '🖨️ Print';
            printBtn.className = 'download-spec-btn';
            printBtn.style.bottom = '80px';
            printBtn.onclick = printDocumentation;
            document.body.appendChild(printBtn);
        });
    </script>
    
    <!-- ReDoc JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/redoc@latest/bundles/redoc.standalone.js"></script>
    
    <!-- Analytics -->
    {{ analytics_code | safe }}
    
    <!-- Enterprise Features -->
    <script>
        // API Usage Analytics
        function trackApiEndpoint(endpoint, method) {
            if (typeof gtag !== 'undefined') {
                gtag('event', 'api_endpoint_view', {
                    'event_category': 'api_docs',
                    'event_label': `${method} ${endpoint}`,
                    'custom_map.dimension1': endpoint,
                    'custom_map.dimension2': method
                });
            }
        }
        
        // Track time spent on documentation
        let startTime = Date.now();
        window.addEventListener('beforeunload', function() {
            const timeSpent = Date.now() - startTime;
            if (typeof gtag !== 'undefined') {
                gtag('event', 'time_spent', {
                    'event_category': 'api_docs',
                    'value': Math.round(timeSpent / 1000)
                });
            }
        });
        
        // Progressive Web App features
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js').then(function(registration) {
                console.log('SW registered: ', registration);
            }).catch(function(registrationError) {
                console.log('SW registration failed: ', registrationError);
            });
        }
    </script>
</body>
</html>'''
        
        return Template(template_content)
    
    def _generate_custom_javascript(self) -> str:
        """Génère le JavaScript personnalisé"""
        
        js_code = """
        // Ainflue Enterprise ReDoc Enhancements
        
        // Advanced copy functionality
        function addCopyButtons() {
            const codeBlocks = document.querySelectorAll('pre code');
            codeBlocks.forEach(block => {
                const copyBtn = document.createElement('button');
                copyBtn.textContent = 'Copy';
                copyBtn.className = 'copy-code-btn';
                copyBtn.style.cssText = `
                    position: absolute;
                    top: 8px;
                    right: 8px;
                    background: #667eea;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 12px;
                    cursor: pointer;
                `;
                
                const container = block.parentElement;
                container.style.position = 'relative';
                container.appendChild(copyBtn);
            });
        }
        
        // Enhanced try-it-out functionality
        function enhanceTryItOut() {
            // Add authentication helpers
            const authInputs = document.querySelectorAll('[data-role="auth-input"]');
            authInputs.forEach(input => {
                input.addEventListener('change', function() {
                    localStorage.setItem('redoc-auth-' + input.name, input.value);
                });
                
                // Restore saved auth values
                const saved = localStorage.getItem('redoc-auth-' + input.name);
                if (saved) {
                    input.value = saved;
                }
            });
        }
        
        // API endpoint bookmarking
        function addBookmarkFeature() {
            const endpoints = document.querySelectorAll('[data-section-id]');
            endpoints.forEach(endpoint => {
                const bookmarkBtn = document.createElement('button');
                bookmarkBtn.textContent = '🔖';
                bookmarkBtn.title = 'Bookmark this endpoint';
                bookmarkBtn.onclick = () => bookmarkEndpoint(endpoint.id);
                
                const header = endpoint.querySelector('h2, h3');
                if (header) {
                    header.appendChild(bookmarkBtn);
                }
            });
        }
        
        function bookmarkEndpoint(endpointId) {
            const bookmarks = JSON.parse(localStorage.getItem('redoc-bookmarks') || '[]');
            
            if (!bookmarks.includes(endpointId)) {
                bookmarks.push(endpointId);
                localStorage.setItem('redoc-bookmarks', JSON.stringify(bookmarks));
                showNotification('Endpoint bookmarked!');
            } else {
                showNotification('Endpoint already bookmarked!');
            }
        }
        
        function showNotification(message) {
            const notification = document.createElement('div');
            notification.textContent = message;
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                background: #667eea;
                color: white;
                padding: 12px 20px;
                border-radius: 4px;
                z-index: 10000;
                animation: slideDown 0.3s ease;
            `;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.remove();
            }, 3000);
        }
        
        // Advanced search with filters
        function enhanceSearchWithFilters() {
            const searchContainer = document.querySelector('[data-role="search"]');
            if (!searchContainer) return;
            
            const filterContainer = document.createElement('div');
            filterContainer.innerHTML = `
                <div style="margin-top: 10px;">
                    <label>
                        <input type="checkbox" id="filter-endpoints" checked> Endpoints
                    </label>
                    <label style="margin-left: 15px;">
                        <input type="checkbox" id="filter-schemas" checked> Schemas
                    </label>
                    <label style="margin-left: 15px;">
                        <input type="checkbox" id="filter-responses" checked> Responses
                    </label>
                </div>
            `;
            
            searchContainer.appendChild(filterContainer);
        }
        
        // Export functionality
        function addExportFeatures() {
            const exportBtn = document.createElement('button');
            exportBtn.textContent = '📤 Export';
            exportBtn.className = 'download-spec-btn';
            exportBtn.style.bottom = '140px';
            exportBtn.onclick = showExportOptions;
            document.body.appendChild(exportBtn);
        }
        
        function showExportOptions() {
            const modal = document.createElement('div');
            modal.innerHTML = `
                <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 10000; display: flex; align-items: center; justify-content: center;">
                    <div style="background: white; padding: 30px; border-radius: 8px; max-width: 400px; width: 90%;">
                        <h3>Export Documentation</h3>
                        <button onclick="exportToPDF()" style="display: block; width: 100%; margin: 10px 0; padding: 12px; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer;">Export as PDF</button>
                        <button onclick="exportToMarkdown()" style="display: block; width: 100%; margin: 10px 0; padding: 12px; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer;">Export as Markdown</button>
                        <button onclick="exportToPostman()" style="display: block; width: 100%; margin: 10px 0; padding: 12px; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer;">Export to Postman</button>
                        <button onclick="closeModal()" style="display: block; width: 100%; margin: 10px 0; padding: 12px; background: #ccc; color: black; border: none; border-radius: 4px; cursor: pointer;">Cancel</button>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            
            window.closeModal = () => modal.remove();
        }
        
        function exportToPDF() {
            window.print();
            closeModal();
        }
        
        function exportToMarkdown() {
            // Implementation would convert OpenAPI spec to Markdown
            showNotification('Markdown export feature coming soon!');
            closeModal();
        }
        
        function exportToPostman() {
            // Implementation would convert OpenAPI spec to Postman collection
            showNotification('Postman export feature coming soon!');
            closeModal();
        }
        
        // Initialize all enhancements
        setTimeout(() => {
            addCopyButtons();
            enhanceTryItOut();
            addBookmarkFeature();
            enhanceSearchWithFilters();
            addExportFeatures();
        }, 2000);
        """
        
        return js_code
    
    def _format_json_filter(self, value) -> str:
        """Filtre pour formater JSON"""
        if isinstance(value, str):
            return value
        return json.dumps(value, indent=2)
    
    def _format_yaml_filter(self, value) -> str:
        """Filtre pour formater YAML"""
        if isinstance(value, str):
            return value
        return yaml.dump(value, default_flow_style=False)
    
    def _markdown_filter(self, value) -> str:
        """Filtre pour convertir Markdown en HTML"""
        return markdown.markdown(value)
    
    async def generate_interactive_examples(
        self,
        openapi_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Génère des exemples interactifs pour chaque endpoint"""
        
        examples = {}
        
        paths = openapi_spec.get('paths', {})
        
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.upper() not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                    continue
                
                operation_id = operation.get('operationId', f"{method}_{path}")
                
                # Générer des exemples de code
                code_samples = await self.code_generator.generate_samples(
                    path, method, operation
                )
                
                # Générer des données d'exemple
                example_data = self._generate_example_data(operation)
                
                examples[operation_id] = {
                    'path': path,
                    'method': method.upper(),
                    'operation': operation,
                    'code_samples': code_samples,
                    'example_data': example_data
                }
        
        return examples
    
    def _generate_example_data(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Génère des données d'exemple pour une opération"""
        
        example_data = {
            'request': {},
            'response': {}
        }
        
        # Exemples de requête
        if 'requestBody' in operation:
            request_body = operation['requestBody']
            content = request_body.get('content', {})
            
            for content_type, schema_info in content.items():
                if 'schema' in schema_info:
                    example_data['request'][content_type] = self._generate_schema_example(
                        schema_info['schema']
                    )
        
        # Exemples de réponse
        responses = operation.get('responses', {})
        for status_code, response_info in responses.items():
            content = response_info.get('content', {})
            
            for content_type, schema_info in content.items():
                if 'schema' in schema_info:
                    if status_code not in example_data['response']:
                        example_data['response'][status_code] = {}
                    
                    example_data['response'][status_code][content_type] = self._generate_schema_example(
                        schema_info['schema']
                    )
        
        return example_data
    
    def _generate_schema_example(self, schema: Dict[str, Any]) -> Any:
        """Génère un exemple basé sur un schéma OpenAPI"""
        
        if 'example' in schema:
            return schema['example']
        
        schema_type = schema.get('type')
        
        if schema_type == 'object':
            example = {}
            properties = schema.get('properties', {})
            
            for prop_name, prop_schema in properties.items():
                example[prop_name] = self._generate_schema_example(prop_schema)
            
            return example
        
        elif schema_type == 'array':
            items_schema = schema.get('items', {})
            return [self._generate_schema_example(items_schema)]
        
        elif schema_type == 'string':
            return schema.get('default', 'example_string')
        
        elif schema_type == 'integer':
            return schema.get('default', 123)
        
        elif schema_type == 'number':
            return schema.get('default', 123.45)
        
        elif schema_type == 'boolean':
            return schema.get('default', True)
        
        else:
            return None
    
    async def create_swagger_ui_redoc_hybrid(
        self,
        openapi_spec: Dict[str, Any]
    ) -> str:
        """Crée une interface hybride ReDoc + Swagger UI"""
        
        hybrid_template = '''<!DOCTYPE html>
<html>
<head>
    <title>{{ title }} - API Documentation</title>
    <meta charset="UTF-8">
    <style>
        body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        .nav-tabs { display: flex; background: #f8f9fa; border-bottom: 1px solid #dee2e6; }
        .nav-tab { padding: 12px 24px; cursor: pointer; border: none; background: none; font-size: 14px; }
        .nav-tab.active { background: white; border-bottom: 2px solid #667eea; }
        .tab-content { height: calc(100vh - 50px); }
        .tab-pane { height: 100%; display: none; }
        .tab-pane.active { display: block; }
        iframe { width: 100%; height: 100%; border: none; }
    </style>
</head>
<body>
    <div class="nav-tabs">
        <button class="nav-tab active" onclick="switchTab('redoc')">📖 ReDoc</button>
        <button class="nav-tab" onclick="switchTab('swagger')">🚀 Swagger UI</button>
        <button class="nav-tab" onclick="switchTab('postman')">📮 Postman</button>
    </div>
    
    <div class="tab-content">
        <div id="redoc" class="tab-pane active">
            <iframe src="/docs/redoc"></iframe>
        </div>
        <div id="swagger" class="tab-pane">
            <iframe src="/docs/swagger"></iframe>
        </div>
        <div id="postman" class="tab-pane">
            <iframe src="/docs/postman"></iframe>
        </div>
    </div>
    
    <script>
        function switchTab(tabName) {
            // Remove active class from all tabs and panes
            document.querySelectorAll('.nav-tab').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
            
            // Add active class to selected tab and pane
            event.target.classList.add('active');
            document.getElementById(tabName).classList.add('active');
        }
    </script>
</body>
</html>'''
        
        template = Template(hybrid_template)
        return template.render(title=self.title)


@dataclass
class ReDocConfiguration:
    """Configuration avancée ReDoc"""
    
    def __init__(self):
        self.config = {
            'theme': {
                'colors': {
                    'primary': {
                        'main': '#667eea'
                    },
                    'success': {
                        'main': '#10b981'
                    },
                    'warning': {
                        'main': '#f59e0b'
                    },
                    'error': {
                        'main': '#ef4444'
                    },
                    'http': {
                        'get': '#10b981',
                        'post': '#667eea',
                        'put': '#f59e0b',
                        'delete': '#ef4444',
                        'patch': '#8b5cf6'
                    }
                },
                'typography': {
                    'fontSize': '14px',
                    'lineHeight': '1.6',
                    'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                    'headings': {
                        'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                        'fontWeight': '600'
                    },
                    'code': {
                        'fontSize': '13px',
                        'fontFamily': 'Monaco, "Cascadia Code", "Roboto Mono", monospace',
                        'backgroundColor': '#f8f9fa'
                    }
                },
                'sidebar': {
                    'backgroundColor': '#ffffff',
                    'width': '300px'
                },
                'rightPanel': {
                    'backgroundColor': '#f8f9fa',
                    'width': '40%'
                }
            },
            'scrollYOffset': 60,
            'hideDownloadButton': False,
            'disableSearch': False,
            'expandDefaultServerVariables': True,
            'expandResponses': 'all',
            'hideHostname': False,
            'hideSingleRequestSampleTab': True,
            'menuToggle': True,
            'nativeScrollbars': False,
            'pathInMiddlePanel': False,
            'requiredPropsFirst': True,
            'sortPropsAlphabetically': True,
            'showExtensions': True,
            'showObjectSchemaExamples': True
        }
    
    def get_config(self) -> Dict[str, Any]:
        """Retourne la configuration"""
        return self.config
    
    def update_config(self, updates: Dict[str, Any]):
        """Met à jour la configuration"""
        self._deep_update(self.config, updates)
    
    def _deep_update(self, base_dict: Dict, update_dict: Dict):
        """Mise à jour récursive de dictionnaire"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value


class ReDocThemeManager:
    """Gestionnaire de thèmes ReDoc"""
    
    def __init__(self):
        self.themes = {
            'default': self._get_default_theme(),
            'dark': self._get_dark_theme(),
            'enterprise': self._get_enterprise_theme(),
            'minimal': self._get_minimal_theme()
        }
        
        self.current_theme = 'enterprise'
    
    def get_custom_css(self) -> str:
        """Retourne le CSS personnalisé"""
        theme = self.themes.get(self.current_theme, self.themes['default'])
        return theme['css']
    
    def _get_default_theme(self) -> Dict[str, str]:
        """Thème par défaut"""
        return {
            'css': '''
                /* Default ReDoc Theme */
                :root {
                    --primary-color: #32329f;
                    --background-color: #ffffff;
                    --text-color: #333333;
                }
            '''
        }
    
    def _get_dark_theme(self) -> Dict[str, str]:
        """Thème sombre"""
        return {
            'css': '''
                /* Dark ReDoc Theme */
                :root {
                    --primary-color: #667eea;
                    --background-color: #1a1a1a;
                    --text-color: #e2e8f0;
                }
                
                .redoc-wrap {
                    background: #1a1a1a !important;
                    color: #e2e8f0 !important;
                }
                
                .api-info-wrap {
                    background: #2d3748 !important;
                    color: #e2e8f0 !important;
                }
            '''
        }
    
    def _get_enterprise_theme(self) -> Dict[str, str]:
        """Thème enterprise Ainflue"""
        return {
            'css': '''
                /* Ainflue Enterprise Theme */
                :root {
                    --primary-color: #667eea;
                    --secondary-color: #764ba2;
                    --success-color: #10b981;
                    --warning-color: #f59e0b;
                    --error-color: #ef4444;
                }
                
                /* Enterprise gradient background */
                body {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }
                
                /* Enhanced typography */
                .redoc-wrap {
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                }
                
                /* Professional code blocks */
                pre, code {
                    background: #f8f9fa !important;
                    border: 1px solid #e9ecef !important;
                    border-radius: 6px !important;
                }
                
                /* Enhanced buttons */
                button {
                    transition: all 0.2s ease !important;
                    border-radius: 6px !important;
                }
                
                /* Professional shadows */
                .api-info-wrap, .menu-content {
                    box-shadow: 0 10px 25px rgba(0,0,0,0.1) !important;
                }
            '''
        }
    
    def _get_minimal_theme(self) -> Dict[str, str]:
        """Thème minimal"""
        return {
            'css': '''
                /* Minimal ReDoc Theme */
                :root {
                    --primary-color: #000000;
                    --background-color: #ffffff;
                }
                
                .redoc-wrap {
                    font-family: 'Georgia', serif;
                }
                
                /* Minimal styling */
                * {
                    border-radius: 0 !important;
                    box-shadow: none !important;
                }
            '''
        }


class DocumentationContentManager:
    """Gestionnaire de contenu de documentation"""
    
    def __init__(self):
        self.content_sections = {}
        self.guides = {}
        self.tutorials = {}
    
    async def add_markdown_guide(
        self,
        guide_id: str,
        markdown_file: str,
        title: str
    ):
        """Ajoute un guide Markdown"""
        
        try:
            async with aiofiles.open(markdown_file, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            html_content = markdown.markdown(
                content,
                extensions=['codehilite', 'toc', 'tables']
            )
            
            self.guides[guide_id] = {
                'title': title,
                'content': html_content,
                'markdown': content,
                'updated_at': datetime.utcnow()
            }
            
        except Exception as e:
            raise ValueError(f"Failed to load guide {guide_id}: {str(e)}")
    
    async def generate_getting_started_guide(
        self,
        api_spec: Dict[str, Any]
    ) -> str:
        """Génère un guide de démarrage automatique"""
        
        guide_content = f'''# Getting Started with {api_spec.get("info", {}).get("title", "API")}

## Introduction

Welcome to the {api_spec.get("info", {}).get("title", "API")} documentation. This guide will help you get started quickly.

## Base URL

```
{api_spec.get("servers", [{}])[0].get("url", "https://api.example.com") if api_spec.get("servers") else "https://api.example.com"}
```

## Authentication

'''
        
        # Analyser les méthodes d'authentification
        security_schemes = api_spec.get('components', {}).get('securitySchemes', {})
        
        for scheme_name, scheme_info in security_schemes.items():
            guide_content += f'''### {scheme_name}

- **Type**: {scheme_info.get("type", "Unknown")}
- **Description**: {scheme_info.get("description", "No description available")}

'''
        
        guide_content += '''## Quick Start

1. Obtain your API credentials
2. Make your first API call
3. Handle the response

## Code Examples

### cURL
```bash
curl -X GET "https://api.example.com/endpoint" \\
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Python
```python
import requests

headers = {
    "Authorization": "Bearer YOUR_TOKEN"
}

response = requests.get("https://api.example.com/endpoint", headers=headers)
print(response.json())
```

### JavaScript
```javascript
fetch('https://api.example.com/endpoint', {
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN'
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

## Next Steps

- Explore the API endpoints in the documentation
- Check out our tutorials for advanced usage
- Join our developer community

'''
        
        return guide_content


class CodeSamplesGenerator:
    """Générateur d'échantillons de code"""
    
    def __init__(self):
        self.languages = {
            'curl': self._generate_curl,
            'python': self._generate_python,
            'javascript': self._generate_javascript,
            'node': self._generate_nodejs,
            'php': self._generate_php,
            'java': self._generate_java,
            'csharp': self._generate_csharp,
            'go': self._generate_go,
            'ruby': self._generate_ruby
        }
    
    async def generate_samples(
        self,
        path: str,
        method: str,
        operation: Dict[str, Any]
    ) -> Dict[str, str]:
        """Génère des échantillons pour toutes les langues"""
        
        samples = {}
        
        for lang, generator in self.languages.items():
            try:
                samples[lang] = generator(path, method, operation)
            except Exception as e:
                samples[lang] = f"// Error generating {lang} sample: {str(e)}"
        
        return samples
    
    def _generate_curl(self, path: str, method: str, operation: Dict[str, Any]) -> str:
        """Génère un exemple cURL"""
        
        base_url = "https://api.ainflue.com"  # Configuration
        
        sample = f'''curl -X {method.upper()} "{base_url}{path}"'''
        
        # Headers
        headers = []
        
        # Authentication
        if 'security' in operation:
            headers.append('"Authorization: Bearer YOUR_API_KEY"')
        
        # Content-Type
        if method.upper() in ['POST', 'PUT', 'PATCH']:
            headers.append('"Content-Type: application/json"')
        
        for header in headers:
            sample += f' \\\n  -H {header}'
        
        # Body
        if method.upper() in ['POST', 'PUT', 'PATCH'] and 'requestBody' in operation:
            sample += ' \\\n  -d \'{\n    "example": "data"\n  }\''
        
        return sample
    
    def _generate_python(self, path: str, method: str, operation: Dict[str, Any]) -> str:
        """Génère un exemple Python"""
        
        sample = '''import requests
import json

url = "https://api.ainflue.com{path}"

headers = {{
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}}

'''.format(path=path)
        
        if method.upper() in ['POST', 'PUT', 'PATCH']:
            sample += '''data = {
    "example": "data"
}

response = requests.{method}(url, headers=headers, json=data)
'''.format(method=method.lower())
        else:
            sample += '''response = requests.{method}(url, headers=headers)
'''.format(method=method.lower())
        
        sample += '''
if response.status_code == 200:
    result = response.json()
    print(json.dumps(result, indent=2))
else:
    print(f"Error: {response.status_code} - {response.text}")'''
        
        return sample
    
    def _generate_javascript(self, path: str, method: str, operation: Dict[str, Any]) -> str:
        """Génère un exemple JavaScript"""
        
        if method.upper() in ['POST', 'PUT', 'PATCH']:
            sample = f'''fetch('https://api.ainflue.com{path}', {{
  method: '{method.upper()}',
  headers: {{
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
  }},
  body: JSON.stringify({{
    example: 'data'
  }})
}})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));'''
        else:
            sample = f'''fetch('https://api.ainflue.com{path}', {{
  method: '{method.upper()}',
  headers: {{
    'Authorization': 'Bearer YOUR_API_KEY'
  }}
}})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));'''
        
        return sample
    
    def _generate_nodejs(self, path: str, method: str, operation: Dict[str, Any]) -> str:
        """Génère un exemple Node.js"""
        
        sample = f'''const axios = require('axios');

const config = {{
  method: '{method.lower()}',
  url: 'https://api.ainflue.com{path}',
  headers: {{
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
  }}'''
        
        if method.upper() in ['POST', 'PUT', 'PATCH']:
            sample += ''',
  data: {
    example: 'data'
  }'''
        
        sample += '''
};

axios(config)
  .then(response => {
    console.log(JSON.stringify(response.data, null, 2));
  })
  .catch(error => {
    console.error('Error:', error.response ? error.response.data : error.message);
  });'''
        
        return sample
    
    def _generate_php(self, path: str, method: str, operation: Dict[str, Any]) -> str:
        """Génère un exemple PHP"""
        
        sample = f'''<?php
$url = 'https://api.ainflue.com{path}';

$headers = [
    'Authorization: Bearer YOUR_API_KEY',
    'Content-Type: application/json'
];

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
curl_setopt($ch, CURLOPT_CUSTOMREQUEST, '{method.upper()}');
'''
        
        if method.upper() in ['POST', 'PUT', 'PATCH']:
            sample += '''
$data = json_encode([
    'example' => 'data'
]);
curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
'''
        
        sample += '''
$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

if ($httpCode == 200) {
    $result = json_decode($response, true);
    echo json_encode($result, JSON_PRETTY_PRINT);
} else {
    echo "Error: $httpCode - $response";
}
?>'''
        
        return sample
    
    def _generate_java(self, path: str, method: str, operation: Dict[str, Any]) -> str:
        """Génère un exemple Java"""
        
        sample = f'''import java.io.*;
import java.net.http.*;
import java.net.URI;

public class ApiExample {{
    public static void main(String[] args) throws Exception {{
        HttpClient client = HttpClient.newHttpClient();
        
        HttpRequest.Builder requestBuilder = HttpRequest.newBuilder()
            .uri(URI.create("https://api.ainflue.com{path}"))
            .header("Authorization", "Bearer YOUR_API_KEY")
            .header("Content-Type", "application/json");
        '''
        
        if method.upper() in ['POST', 'PUT', 'PATCH']:
            sample += f'''
        String json = "{{\\\"example\\\": \\\"data\\\"}}";
        HttpRequest request = requestBuilder
            .{method.upper()}(HttpRequest.BodyPublishers.ofString(json))
            .build();
        '''
        else:
            sample += f'''
        HttpRequest request = requestBuilder
            .{method.upper()}()
            .build();
        '''
        
        sample += '''
        HttpResponse<String> response = client.send(request, 
            HttpResponse.BodyHandlers.ofString());
        
        System.out.println("Status: " + response.statusCode());
        System.out.println("Response: " + response.body());
    }
}'''
        
        return sample
    
    def _generate_csharp(self, path: str, method: str, operation: Dict[str, Any]) -> str:
        """Génère un exemple C#"""
        
        sample = f'''using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;

class Program
{{
    private static readonly HttpClient client = new HttpClient();
    
    static async Task Main(string[] args)
    {{
        client.DefaultRequestHeaders.Add("Authorization", "Bearer YOUR_API_KEY");
        
        try
        {{'''
        
        if method.upper() in ['POST', 'PUT', 'PATCH']:
            sample += f'''
            string json = "{{\\\"example\\\": \\\"data\\\"}}";
            var content = new StringContent(json, Encoding.UTF8, "application/json");
            
            HttpResponseMessage response = await client.{method.capitalize()}Async(
                "https://api.ainflue.com{path}", content);
            '''
        else:
            sample += f'''
            HttpResponseMessage response = await client.{method.capitalize()}Async(
                "https://api.ainflue.com{path}");
            '''
        
        sample += '''
            response.EnsureSuccessStatusCode();
            string responseBody = await response.Content.ReadAsStringAsync();
            
            Console.WriteLine(responseBody);
        }
        catch (HttpRequestException e)
        {
            Console.WriteLine($"Error: {e.Message}");
        }
    }
}'''
        
        return sample
    
    def _generate_go(self, path: str, method: str, operation: Dict[str, Any]) -> str:
        """Génère un exemple Go"""
        
        sample = f'''package main

import (
    "bytes"
    "fmt"
    "io/ioutil"
    "net/http"
)

func main() {{
    url := "https://api.ainflue.com{path}"
    '''
        
        if method.upper() in ['POST', 'PUT', 'PATCH']:
            sample += f'''
    jsonStr := []byte(`{{"example": "data"}}`)
    
    req, err := http.NewRequest("{method.upper()}", url, bytes.NewBuffer(jsonStr))
    if err != nil {{
        fmt.Printf("Error creating request: %v\\n", err)
        return
    }}
    
    req.Header.Set("Content-Type", "application/json")
    '''
        else:
            sample += f'''
    req, err := http.NewRequest("{method.upper()}", url, nil)
    if err != nil {{
        fmt.Printf("Error creating request: %v\\n", err)
        return
    }}
    '''
        
        sample += '''
    req.Header.Set("Authorization", "Bearer YOUR_API_KEY")
    
    client := &http.Client{}
    resp, err := client.Do(req)
    if err != nil {
        fmt.Printf("Error making request: %v\\n", err)
        return
    }
    defer resp.Body.Close()
    
    body, err := ioutil.ReadAll(resp.Body)
    if err != nil {
        fmt.Printf("Error reading response: %v\\n", err)
        return
    }
    
    fmt.Printf("Status: %s\\n", resp.Status)
    fmt.Printf("Response: %s\\n", string(body))
}'''
        
        return sample
    
    def _generate_ruby(self, path: str, method: str, operation: Dict[str, Any]) -> str:
        """Génère un exemple Ruby"""
        
        sample = f'''require 'net/http'
require 'json'
require 'uri'

uri = URI('https://api.ainflue.com{path}')
http = Net::HTTP.new(uri.host, uri.port)
http.use_ssl = true

request = Net::HTTP::{method.capitalize()}.new(uri)
request['Authorization'] = 'Bearer YOUR_API_KEY'
request['Content-Type'] = 'application/json'
'''
        
        if method.upper() in ['POST', 'PUT', 'PATCH']:
            sample += '''
request.body = {
  example: 'data'
}.to_json
'''
        
        sample += '''
response = http.request(request)

if response.code == '200'
  result = JSON.parse(response.body)
  puts JSON.pretty_generate(result)
else
  puts "Error: #{response.code} - #{response.body}"
end'''
        
        return sample


class DocumentationAnalytics:
    """Analytics pour la documentation"""
    
    def __init__(self):
        self.tracking_id = None
        self.custom_events = []
    
    def set_google_analytics(self, tracking_id: str):
        """Configure Google Analytics"""
        self.tracking_id = tracking_id
    
    def get_tracking_code(self) -> str:
        """Retourne le code de tracking"""
        
        if not self.tracking_id:
            return ""
        
        return f'''
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id={self.tracking_id}"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){{dataLayer.push(arguments);}}
          gtag('js', new Date());
          gtag('config', '{self.tracking_id}', {{
            custom_map: {{
              'dimension1': 'api_endpoint',
              'dimension2': 'http_method',
              'dimension3': 'user_role'
            }}
          }});
        </script>
        '''
    
    def add_custom_event(self, event_name: str, parameters: Dict[str, Any]):
        """Ajoute un événement personnalisé"""
        self.custom_events.append({
            'name': event_name,
            'parameters': parameters
        })


class APIVersionManager:
    """Gestionnaire de versions d'API"""
    
    def __init__(self):
        self.versions = []
    
    def add_version(
        self,
        version: str,
        spec_url: str,
        is_latest: bool = False,
        is_deprecated: bool = False
    ):
        """Ajoute une version d'API"""
        self.versions.append({
            'version': version,
            'spec_url': spec_url,
            'is_latest': is_latest,
            'is_deprecated': is_deprecated,
            'added_at': datetime.utcnow()
        })
    
    def get_versions(self) -> List[Dict[str, Any]]:
        """Retourne toutes les versions"""
        return sorted(self.versions, key=lambda x: x['version'], reverse=True)
    
    def get_latest_version(self) -> Optional[Dict[str, Any]]:
        """Retourne la dernière version"""
        latest = [v for v in self.versions if v['is_latest']]
        return latest[0] if latest else None


# Factory et helper functions
def create_redoc_template(
    title: str = "Ainflue API Documentation",
    description: str = "Enterprise API Documentation",
    version: str = "1.0.0",
    **kwargs
) -> ReDocTemplate:
    """Factory pour créer un template ReDoc"""
    
    return ReDocTemplate(
        title=title,
        description=description,
        version=version,
        **kwargs
    )


async def setup_redoc_documentation(
    app: FastAPI,
    openapi_spec: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> ReDocTemplate:
    """Setup complet de la documentation ReDoc"""
    
    redoc = create_redoc_template(
        title=openapi_spec.get('info', {}).get('title', 'API Documentation'),
        description=openapi_spec.get('info', {}).get('description', ''),
        version=openapi_spec.get('info', {}).get('version', '1.0.0')
    )
    
    # Configuration analytics
    if config and 'analytics_id' in config:
        redoc.analytics.set_google_analytics(config['analytics_id'])
    
    # Configuration des versions
    if config and 'versions' in config:
        for version_info in config['versions']:
            redoc.version_manager.add_version(**version_info)
    
    # Route pour ReDoc
    @app.get("/docs/redoc", response_class=HTMLResponse)
    async def redoc_documentation():
        html_content = redoc.generate_redoc_html(openapi_spec, config)
        return HTMLResponse(content=html_content)
    
    # Route pour télécharger la spécification
    @app.get("/docs/openapi.json")
    async def download_openapi_spec():
        return JSONResponse(content=openapi_spec)
    
    # Route hybride
    @app.get("/docs/hybrid", response_class=HTMLResponse)
    async def hybrid_documentation():
        hybrid_content = await redoc.create_swagger_ui_redoc_hybrid(openapi_spec)
        return HTMLResponse(content=hybrid_content)
    
    return redoc


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def example_redoc_setup():
        # Exemple de spécification OpenAPI
        openapi_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Ainflue Creator Economy API",
                "description": "Advanced API for creator economy platform",
                "version": "2.0.0"
            },
            "servers": [
                {"url": "https://api.ainflue.com/v2"}
            ],
            "paths": {
                "/creators": {
                    "get": {
                        "summary": "List creators",
                        "operationId": "listCreators",
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        # Créer le template ReDoc
        redoc = create_redoc_template(
            title="Ainflue API Documentation",
            description="Enterprise Creator Economy API",
            version="2.0.0",
            logo_url="https://ainflue.com/logo.png"
        )
        
        # Configuration analytics
        redoc.analytics.set_google_analytics("GA_TRACKING_ID")
        
        # Ajouter des versions
        redoc.version_manager.add_version("2.0.0", "/api/v2/openapi.json", is_latest=True)
        redoc.version_manager.add_version("1.0.0", "/api/v1/openapi.json")
        
        # Générer la documentation
        html_content = redoc.generate_redoc_html(openapi_spec)
        
        print(f"ReDoc documentation generated: {len(html_content)} characters")
        
        # Générer des exemples interactifs
        examples = await redoc.generate_interactive_examples(openapi_spec)
        print(f"Generated {len(examples)} interactive examples")
    
    asyncio.run(example_redoc_setup())