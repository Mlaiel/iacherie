"""
Export Serializer Module
=========================

Specialized serialization for data export formats and reporting systems.
Optimized for CSV, Excel, PDF, and various report generation formats.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

 LEGAL WARNING - INTELLECTUAL PROPERTY PROTECTION:
This code, concept, and intellectual property belong exclusively to Fahed Mlaiel (mlaiel@live.de). 
Any unauthorized copying, distribution, modification, or commercial use is STRICTLY PROHIBITED 
and will result in immediate legal action under German and International Copyright Law.

ZERO TOLERANCE POLICY: Anyone attempting to steal, copy, or misappropriate this code or concept 
will face severe legal consequences including but not limited to criminal charges, civil litigation, 
and substantial financial damages.

AUTHORIZED USE ONLY: Contact mlaiel@live.de for official licensing agreements.

Expertise combinée:
- Lead Developer IA: Architecture d'export intelligent et automatisé
- Backend Senior: Infrastructure robuste pour génération de rapports enterprise
- ML Engineer: Algorithmes d'analyse pour insights automatiques dans exports
- DBA Expert: Optimisation extraction et export de données massives
- Sécurité: Protection et chiffrement des exports sensibles
- Microservices: Architecture distribuée pour génération de rapports
- Audio/Vidéo: Export spécialisé pour métadonnées multimédia
- DevOps: Automation et scaling pour génération de rapports
- IA Prompt Engineer: Génération automatique de rapports narratifs par IA
"""

import logging
import io
import csv
from typing import Dict, List, Optional, Any, Union, BinaryIO, TextIO
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import base64
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

class ExportFormat(Enum):
    """Supported export formats."""
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"
    XML = "xml"
    PDF = "pdf"
    HTML = "html"
    MARKDOWN = "markdown"
    PARQUET = "parquet"
    YAML = "yaml"
    TSV = "tsv"

class DataGrouping(Enum):
    """Data grouping strategies."""
    NONE = "none"
    BY_DATE = "by_date"
    BY_PLATFORM = "by_platform"
    BY_TYPE = "by_type"
    BY_STATUS = "by_status"
    BY_CATEGORY = "by_category"
    HIERARCHICAL = "hierarchical"

class AggregationMethod(Enum):
    """Data aggregation methods."""
    SUM = "sum"
    COUNT = "count"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    PERCENTILE = "percentile"
    STANDARD_DEVIATION = "std_dev"
    VARIANCE = "variance"

class ReportTemplate(Enum):
    """Predefined report templates."""
    STANDARD = "standard"
    EXECUTIVE_SUMMARY = "executive_summary"
    DETAILED_ANALYSIS = "detailed_analysis"
    COMPLIANCE_REPORT = "compliance_report"
    PERFORMANCE_METRICS = "performance_metrics"
    SECURITY_AUDIT = "security_audit"
    FINANCIAL_SUMMARY = "financial_summary"
    TECHNICAL_REPORT = "technical_report"

@dataclass
class ExportConfiguration:
    """Export configuration settings."""
    format: ExportFormat = ExportFormat.CSV
    include_headers: bool = True
    include_metadata: bool = True
    include_timestamps: bool = True
    date_format: str = "%Y-%m-%d %H:%M:%S"
    decimal_precision: int = 2
    encoding: str = "utf-8"
    delimiter: str = ","
    quote_char: str = '"'
    escape_char: str = "\\"
    null_value: str = ""
    boolean_format: str = "true/false"  # "true/false", "1/0", "yes/no"
    max_rows_per_file: Optional[int] = None
    compress_output: bool = False
    password_protect: bool = False
    password: Optional[str] = None

@dataclass
class ExportMetrics:
    """Export operation metrics."""
    total_records: int = 0
    exported_records: int = 0
    skipped_records: int = 0
    error_records: int = 0
    files_created: int = 0
    total_size_bytes: int = 0
    compression_ratio: float = 1.0
    processing_time_seconds: float = 0.0
    export_speed_rps: float = 0.0  # Records per second

class ExportData(BaseModel):
    """
    Comprehensive export data model.
    
    Represents data export configuration, content, and metadata
    for the IA-Influencer-Agent export system.
    """
    
    # Export identification
    export_id: str = Field(..., description="Unique export identifier")
    export_name: str = Field(..., description="Export name/title")
    export_format: ExportFormat = Field(default=ExportFormat.CSV)
    template: ReportTemplate = Field(default=ReportTemplate.STANDARD)
    
    # Data configuration
    data_source: str = Field(..., description="Source of exported data")
    query_parameters: Dict[str, Any] = Field(default_factory=dict)
    filters: Dict[str, Any] = Field(default_factory=dict)
    grouping: DataGrouping = Field(default=DataGrouping.NONE)
    aggregation_methods: List[AggregationMethod] = Field(default_factory=list)
    
    # Export configuration
    configuration: ExportConfiguration = Field(default_factory=ExportConfiguration)
    
    # Data content
    headers: List[str] = Field(default_factory=list)
    data_rows: List[List[Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    summary_statistics: Dict[str, Any] = Field(default_factory=dict)
    
    # Export metrics
    metrics: ExportMetrics = Field(default_factory=ExportMetrics)
    
    # File information
    output_filename: Optional[str] = None
    output_files: List[str] = Field(default_factory=list)
    file_paths: List[str] = Field(default_factory=list)
    
    # Security and compliance
    data_classification: str = Field(default="internal")
    retention_days: int = Field(default=90)
    export_permissions: List[str] = Field(default_factory=list)
    audit_trail: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Timestamps
    requested_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    @validator('export_format', pre=True)
    def validate_export_format(cls, v):
        if isinstance(v, str):
            return ExportFormat(v.lower())
        return v
    
    @validator('template', pre=True)
    def validate_template(cls, v):
        if isinstance(v, str):
            return ReportTemplate(v.lower())
        return v
    
    @validator('grouping', pre=True)
    def validate_grouping(cls, v):
        if isinstance(v, str):
            return DataGrouping(v.lower())
        return v

class ExportSerializer:
    """
    Advanced export data serialization system.
    
    Handles efficient serialization and export of crawler data
    to various formats including CSV, Excel, PDF, and other
    reporting formats with comprehensive formatting options.
    """
    
    def __init__(self):
        """Initialize export serializer."""
        self.format_handlers = {
            ExportFormat.CSV: self._export_to_csv,
            ExportFormat.JSON: self._export_to_json,
            ExportFormat.XML: self._export_to_xml,
            ExportFormat.HTML: self._export_to_html,
            ExportFormat.MARKDOWN: self._export_to_markdown,
            ExportFormat.YAML: self._export_to_yaml,
            ExportFormat.TSV: self._export_to_tsv
        }
        
        self.template_processors = {
            ReportTemplate.STANDARD: self._process_standard_template,
            ReportTemplate.EXECUTIVE_SUMMARY: self._process_executive_template,
            ReportTemplate.DETAILED_ANALYSIS: self._process_detailed_template,
            ReportTemplate.COMPLIANCE_REPORT: self._process_compliance_template,
            ReportTemplate.PERFORMANCE_METRICS: self._process_performance_template,
            ReportTemplate.SECURITY_AUDIT: self._process_security_template,
            ReportTemplate.FINANCIAL_SUMMARY: self._process_financial_template,
            ReportTemplate.TECHNICAL_REPORT: self._process_technical_template
        }
        
        logger.info("Export serializer initialized")
    
    def serialize_export_data(
        self,
        export_data: ExportData,
        include_raw_data: bool = False
    ) -> Dict[str, Any]:
        """
        Serialize export data to dictionary format.
        
        Args:
            export_data: Export data to serialize
            include_raw_data: Whether to include raw data rows
            
        Returns:
            Serialized export dictionary
        """



        try:
            # Convert to dictionary
            data = export_data.dict(exclude={'data_rows'} if not include_raw_data else {})
            
            # Handle datetime conversions
            datetime_fields = [
                'requested_at', 'started_at', 'completed_at', 'expires_at'
            ]
            for field in datetime_fields:
                if data.get(field):
                    data[field] = getattr(export_data, field).isoformat()
            
            # Serialize configuration
            data['configuration'] = self._serialize_export_configuration(export_data.configuration)
            
            # Serialize metrics
            data['metrics'] = self._serialize_export_metrics(export_data.metrics)
            
            # Handle data rows
            if include_raw_data:
                data['data_rows'] = export_data.data_rows
                data['_data_included'] = True
            else:
                data['_data_included'] = False
                data['_data_rows_count'] = len(export_data.data_rows)
            
            # Convert enums
            data['export_format'] = export_data.export_format.value
            data['template'] = export_data.template.value
            data['grouping'] = export_data.grouping.value
            data['aggregation_methods'] = [method.value for method in export_data.aggregation_methods]
            
            # Add serialization metadata
            data['_serialization'] = {
                'version': '2.0.0',
                'serialized_at': datetime.now().isoformat(),
                'includes_data': include_raw_data,
                'format': export_data.export_format.value
            }
            
            logger.debug(f"Serialized export data {export_data.export_id}")
            return data
            
        except Exception as e:
            logger.error(f"Export data serialization failed: {e}")
            raise
    
    def deserialize_export_data(
        self,
        data: Dict[str, Any]
    ) -> ExportData:
        """
        Deserialize export data from dictionary format.
        
        Args:
            data: Serialized export dictionary
            
        Returns:
            Deserialized ExportData object
        """



        try:
            # Handle datetime conversions
            datetime_fields = [
                'requested_at', 'started_at', 'completed_at', 'expires_at'
            ]
            for field in datetime_fields:
                if isinstance(data.get(field), str):
                    data[field] = datetime.fromisoformat(data[field])
            
            # Deserialize configuration
            if 'configuration' in data and isinstance(data['configuration'], dict):
                data['configuration'] = self._deserialize_export_configuration(data['configuration'])
            
            # Deserialize metrics
            if 'metrics' in data and isinstance(data['metrics'], dict):
                data['metrics'] = self._deserialize_export_metrics(data['metrics'])
            
            # Handle aggregation methods
            if 'aggregation_methods' in data and isinstance(data['aggregation_methods'], list):
                data['aggregation_methods'] = [
                    AggregationMethod(method) for method in data['aggregation_methods']
                ]
            
            # Remove serialization metadata
            data.pop('_serialization', None)
            data.pop('_data_included', None)
            data.pop('_data_rows_count', None)
            
            # Create ExportData object
            export_data = ExportData(**data)
            
            logger.debug(f"Deserialized export data {export_data.export_id}")
            return export_data
            
        except Exception as e:
            logger.error(f"Export data deserialization failed: {e}")
            raise
    
    def export_to_format(
        self,
        export_data: ExportData,
        output_path: Optional[str] = None
    ) -> Union[str, bytes]:
        """
        Export data to specified format.
        
        Args:
            export_data: Export data to process
            output_path: Optional file path to save export
            
        Returns:
            Exported data as string or bytes
        """



        try:
            # Update metrics
            export_data.started_at = datetime.now()
            export_data.metrics.total_records = len(export_data.data_rows)
            
            # Process template
            if export_data.template in self.template_processors:
                processed_data = self.template_processors[export_data.template](export_data)
            else:
                processed_data = export_data
            
            # Export to format
            if export_data.export_format in self.format_handlers:
                result = self.format_handlers[export_data.export_format](processed_data)
            else:
                # Try external handlers for Excel, PDF, Parquet
                result = self._handle_external_format(processed_data)
            
            # Save to file if path provided
            if output_path:
                self._save_export_file(result, output_path, export_data.export_format)
                export_data.file_paths.append(output_path)
                export_data.metrics.files_created += 1
            
            # Update completion metrics
            export_data.completed_at = datetime.now()
            if export_data.started_at:
                processing_time = (export_data.completed_at - export_data.started_at).total_seconds()
                export_data.metrics.processing_time_seconds = processing_time
                export_data.metrics.export_speed_rps = len(export_data.data_rows) / max(processing_time, 0.001)
            
            export_data.metrics.exported_records = len(export_data.data_rows)
            
            logger.info(f"Exported {len(export_data.data_rows)} records to {export_data.export_format.value}")
            return result
            
        except Exception as e:
            logger.error(f"Export to format failed: {e}")
            export_data.metrics.error_records = len(export_data.data_rows)
            raise
    
    def _export_to_csv(self, export_data: ExportData) -> str:
        """Export data to CSV format."""
        output = io.StringIO()
        config = export_data.configuration
        
        writer = csv.writer(
            output,
            delimiter=config.delimiter,
            quotechar=config.quote_char,
            quoting=csv.QUOTE_MINIMAL
        )
        
        # Write headers
        if config.include_headers and export_data.headers:
            writer.writerow(export_data.headers)
        
        # Write data rows
        for row in export_data.data_rows:
            formatted_row = self._format_row_values(row, config)
            writer.writerow(formatted_row)
        
        return output.getvalue()
    
    def _export_to_json(self, export_data: ExportData) -> str:
        """Export data to JSON format."""
        output_data = {
            'metadata': export_data.metadata,
            'headers': export_data.headers,
            'data': []
        }
        
        if export_data.configuration.include_metadata:
            output_data['export_info'] = {
                'export_id': export_data.export_id,
                'export_name': export_data.export_name,
                'exported_at': datetime.now().isoformat(),
                'total_records': len(export_data.data_rows)
            }
        
        # Convert rows to dictionaries
        for row in export_data.data_rows:
            if export_data.headers and len(row) == len(export_data.headers):
                row_dict = dict(zip(export_data.headers, row))
            else:
                row_dict = {f'column_{i}': value for i, value in enumerate(row)}
            
            output_data['data'].append(row_dict)
        
        return json.dumps(output_data, indent=2, default=self._json_serializer)
    
    def _export_to_xml(self, export_data: ExportData) -> str:
        """Export data to XML format."""
        lines = ['<?xml version="1.0" encoding="utf-8"?>']
        lines.append('<export>')
        
        # Metadata
        if export_data.configuration.include_metadata:
            lines.append('  <metadata>')
            lines.append(f'    <export_id>{export_data.export_id}</export_id>')
            lines.append(f'    <export_name>{export_data.export_name}</export_name>')
            lines.append(f'    <exported_at>{datetime.now().isoformat()}</exported_at>')
            lines.append(f'    <total_records>{len(export_data.data_rows)}</total_records>')
            lines.append('  </metadata>')
        
        # Data
        lines.append('  <data>')
        for i, row in enumerate(export_data.data_rows):
            lines.append(f'    <record id="{i}">')
            
            for j, value in enumerate(row):
                column_name = export_data.headers[j] if j < len(export_data.headers) else f'column_{j}'
                safe_name = self._sanitize_xml_name(column_name)
                safe_value = self._escape_xml_value(str(value))
                lines.append(f'      <{safe_name}>{safe_value}</{safe_name}>')
            
            lines.append('    </record>')
        lines.append('  </data>')
        lines.append('</export>')
        
        return '\n'.join(lines)
    
    def _export_to_html(self, export_data: ExportData) -> str:
        """Export data to HTML format."""
        lines = [
            '<!DOCTYPE html>',
            '<html>',
            '<head>',
            f'  <title>{export_data.export_name}</title>',
            '  <style>',
            '    table { border-collapse: collapse; width: 100%; }',
            '    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }',
            '    th { background-color: #f2f2f2; }',
            '    .metadata { margin-bottom: 20px; }',
            '  </style>',
            '</head>',
            '<body>'
        ]
        
        # Metadata section
        if export_data.configuration.include_metadata:
            lines.extend([
                '  <div class="metadata">',
                f'    <h1>{export_data.export_name}</h1>',
                f'    <p><strong>Export ID:</strong> {export_data.export_id}</p>',
                f'    <p><strong>Exported at:</strong> {datetime.now().strftime(export_data.configuration.date_format)}</p>',
                f'    <p><strong>Total records:</strong> {len(export_data.data_rows)}</p>',
                '  </div>'
            ])
        
        # Data table
        lines.append('  <table>')
        
        # Headers
        if export_data.configuration.include_headers and export_data.headers:
            lines.append('    <thead>')
            lines.append('      <tr>')
            for header in export_data.headers:
                lines.append(f'        <th>{self._escape_html(str(header))}</th>')
            lines.append('      </tr>')
            lines.append('    </thead>')
        
        # Data rows
        lines.append('    <tbody>')
        for row in export_data.data_rows:
            lines.append('      <tr>')
            for value in row:
                formatted_value = self._escape_html(str(value))
                lines.append(f'        <td>{formatted_value}</td>')
            lines.append('      </tr>')
        lines.append('    </tbody>')
        
        lines.extend([
            '  </table>',
            '</body>',
            '</html>'
        ])
        
        return '\n'.join(lines)
    
    def _export_to_markdown(self, export_data: ExportData) -> str:
        """Export data to Markdown format."""
        lines = []
        
        # Title and metadata
        lines.append(f'# {export_data.export_name}')
        lines.append('')
        
        if export_data.configuration.include_metadata:
            lines.extend([
                '## Export Information',
                '',
                f'- **Export ID:** {export_data.export_id}',
                f'- **Exported at:** {datetime.now().strftime(export_data.configuration.date_format)}',
                f'- **Total records:** {len(export_data.data_rows)}',
                ''
            ])
        
        # Data table
        if export_data.headers and export_data.data_rows:
            lines.append('## Data')
            lines.append('')
            
            # Headers
            header_line = '| ' + ' | '.join(str(h) for h in export_data.headers) + ' |'
            separator_line = '| ' + ' | '.join('---' for _ in export_data.headers) + ' |'
            
            lines.append(header_line)
            lines.append(separator_line)
            
            # Data rows
            for row in export_data.data_rows:
                values = [str(v).replace('|', '\\|') for v in row]
                data_line = '| ' + ' | '.join(values) + ' |'
                lines.append(data_line)
        
        return '\n'.join(lines)
    
    def _export_to_yaml(self, export_data: ExportData) -> str:
        """Export data to YAML format."""
        import yaml
        
        output_data = {
            'export_info': {
                'export_id': export_data.export_id,
                'export_name': export_data.export_name,
                'exported_at': datetime.now().isoformat(),
                'total_records': len(export_data.data_rows)
            },
            'headers': export_data.headers,
            'data': []
        }
        
        # Convert rows to dictionaries
        for row in export_data.data_rows:
            if export_data.headers and len(row) == len(export_data.headers):
                row_dict = dict(zip(export_data.headers, row))
            else:
                row_dict = {f'column_{i}': value for i, value in enumerate(row)}
            
            output_data['data'].append(row_dict)
        
        return yaml.dump(output_data, default_flow_style=False, allow_unicode=True)
    
    def _export_to_tsv(self, export_data: ExportData) -> str:
        """Export data to TSV (Tab-Separated Values) format."""
        # Temporarily change delimiter to tab
        original_delimiter = export_data.configuration.delimiter
        export_data.configuration.delimiter = '\t'
        
        result = self._export_to_csv(export_data)
        
        # Restore original delimiter
        export_data.configuration.delimiter = original_delimiter
        
        return result
    
    def _handle_external_format(self, export_data: ExportData) -> Union[str, bytes]:
        """Handle external format exports (Excel, PDF, Parquet)."""
        if export_data.export_format == ExportFormat.EXCEL:
            return self._export_to_excel(export_data)
        elif export_data.export_format == ExportFormat.PDF:
            return self._export_to_pdf(export_data)
        elif export_data.export_format == ExportFormat.PARQUET:
            return self._export_to_parquet(export_data)
        else:
            raise ValueError(f"Unsupported format: {export_data.export_format}")
    
    def _export_to_excel(self, export_data: ExportData) -> bytes:
        """Export data to Excel format."""



        try:
            import pandas as pd
            
            # Create DataFrame
            if export_data.headers and len(export_data.data_rows) > 0:
                df = pd.DataFrame(export_data.data_rows, columns=export_data.headers)
            else:
                df = pd.DataFrame(export_data.data_rows)
            
            # Export to Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Data', index=False)
                
                # Add metadata sheet if requested
                if export_data.configuration.include_metadata:
                    metadata_df = pd.DataFrame([
                        ['Export ID', export_data.export_id],
                        ['Export Name', export_data.export_name],
                        ['Exported At', datetime.now().strftime(export_data.configuration.date_format)],
                        ['Total Records', len(export_data.data_rows)]
                    ], columns=['Property', 'Value'])
                    
                    metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
            
            return output.getvalue()
            
        except ImportError:
            logger.error("pandas and openpyxl required for Excel export")
            raise
        except Exception as e:
            logger.error(f"Excel export failed: {e}")
            raise
    
    def _export_to_pdf(self, export_data: ExportData) -> bytes:
        """Export data to PDF format."""



        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors
            
            output = io.BytesIO()
            doc = SimpleDocTemplate(output, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title = Paragraph(export_data.export_name, styles['Title'])
            story.append(title)
            story.append(Spacer(1, 12))
            
            # Metadata
            if export_data.configuration.include_metadata:
                metadata_text = f"""
                Export ID: {export_data.export_id}<br/>
                Exported at: {datetime.now().strftime(export_data.configuration.date_format)}<br/>
                Total records: {len(export_data.data_rows)}
                """
                metadata = Paragraph(metadata_text, styles['Normal'])
                story.append(metadata)
                story.append(Spacer(1, 12))
            
            # Data table
            if export_data.data_rows:
                table_data = []
                
                # Add headers
                if export_data.headers:
                    table_data.append(export_data.headers)
                
                # Add data rows (limit for PDF)
                max_rows = 50  # Limit for readability
                for i, row in enumerate(export_data.data_rows[:max_rows]):
                    formatted_row = [str(value)[:30] + '...' if len(str(value)) > 30 else str(value) for value in row]
                    table_data.append(formatted_row)
                
                if len(export_data.data_rows) > max_rows:
                    table_data.append(['...'] * len(export_data.headers or [1]))
                
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(table)
            
            doc.build(story)
            return output.getvalue()
            
        except ImportError:
            logger.error("reportlab required for PDF export")
            raise
        except Exception as e:
            logger.error(f"PDF export failed: {e}")
            raise
    
    def _export_to_parquet(self, export_data: ExportData) -> bytes:
        """Export data to Parquet format."""



        try:
            import pandas as pd
            
            # Create DataFrame
            if export_data.headers and len(export_data.data_rows) > 0:
                df = pd.DataFrame(export_data.data_rows, columns=export_data.headers)
            else:
                df = pd.DataFrame(export_data.data_rows)
            
            # Export to Parquet
            output = io.BytesIO()
            df.to_parquet(output, index=False, compression='snappy')
            
            return output.getvalue()
            
        except ImportError:
            logger.error("pandas and pyarrow required for Parquet export")
            raise
        except Exception as e:
            logger.error(f"Parquet export failed: {e}")
            raise
    
    def _serialize_export_configuration(self, config: ExportConfiguration) -> Dict[str, Any]:
        """Serialize export configuration."""



        return {
            'format': config.format.value,
            'include_headers': config.include_headers,
            'include_metadata': config.include_metadata,
            'include_timestamps': config.include_timestamps,
            'date_format': config.date_format,
            'decimal_precision': config.decimal_precision,
            'encoding': config.encoding,
            'delimiter': config.delimiter,
            'quote_char': config.quote_char,
            'escape_char': config.escape_char,
            'null_value': config.null_value,
            'boolean_format': config.boolean_format,
            'max_rows_per_file': config.max_rows_per_file,
            'compress_output': config.compress_output,
            'password_protect': config.password_protect
        }
    
    def _deserialize_export_configuration(self, data: Dict[str, Any]) -> ExportConfiguration:
        """Deserialize export configuration."""
        if 'format' in data:
            data['format'] = ExportFormat(data['format'])
        return ExportConfiguration(**data)
    
    def _serialize_export_metrics(self, metrics: ExportMetrics) -> Dict[str, Any]:
        """Serialize export metrics."""



        return {
            'total_records': metrics.total_records,
            'exported_records': metrics.exported_records,
            'skipped_records': metrics.skipped_records,
            'error_records': metrics.error_records,
            'files_created': metrics.files_created,
            'total_size_bytes': metrics.total_size_bytes,
            'compression_ratio': metrics.compression_ratio,
            'processing_time_seconds': metrics.processing_time_seconds,
            'export_speed_rps': metrics.export_speed_rps
        }
    
    def _deserialize_export_metrics(self, data: Dict[str, Any]) -> ExportMetrics:
        """Deserialize export metrics."""



        return ExportMetrics(**data)
    
    def _format_row_values(self, row: List[Any], config: ExportConfiguration) -> List[str]:
        """Format row values according to configuration."""
        formatted_row = []
        
        for value in row:
            if value is None:
                formatted_row.append(config.null_value)
            elif isinstance(value, bool):
                if config.boolean_format == "1/0":
                    formatted_row.append("1" if value else "0")
                elif config.boolean_format == "yes/no":
                    formatted_row.append("yes" if value else "no")
                else:
                    formatted_row.append("true" if value else "false")
            elif isinstance(value, float):
                formatted_row.append(f"{value:.{config.decimal_precision}f}")
            elif isinstance(value, datetime):
                formatted_row.append(value.strftime(config.date_format))
            else:
                formatted_row.append(str(value))
        
        return formatted_row
    
    def _json_serializer(self, obj):
        """JSON serializer for non-standard types."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        return str(obj)
    
    def _sanitize_xml_name(self, name: str) -> str:
        """Sanitize XML element name."""
        import re
        # Remove invalid characters and ensure it starts with letter
        sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
        if not sanitized[0].isalpha():
            sanitized = 'col_' + sanitized
        return sanitized
    
    def _escape_xml_value(self, value: str) -> str:
        """Escape XML value."""



        return (value.replace('&', '&amp;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;')
                    .replace('"', '&quot;')
                    .replace("'", '&#39;'))
    
    def _escape_html(self, value: str) -> str:
        """Escape HTML value."""



        return (value.replace('&', '&amp;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;')
                    .replace('"', '&quot;'))
    
    def _save_export_file(
        self,
        content: Union[str, bytes],
        file_path: str,
        export_format: ExportFormat
    ):
        """Save export content to file."""



        try:
            if isinstance(content, bytes):
                with open(file_path, 'wb') as f:
                    f.write(content)
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
            logger.info(f"Export saved to {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save export file: {e}")
            raise
    
    # Template processors
    def _process_standard_template(self, export_data: ExportData) -> ExportData:
        """Process standard report template."""



        return export_data  # No special processing for standard template
    
    def _process_executive_template(self, export_data: ExportData) -> ExportData:
        """Process executive summary template."""
        # Add summary statistics
        if export_data.data_rows:
            export_data.summary_statistics = {
                'total_records': len(export_data.data_rows),
                'data_quality_score': 95.0,  # Placeholder
                'completeness_percentage': 98.5  # Placeholder
            }
        return export_data
    
    def _process_detailed_template(self, export_data: ExportData) -> ExportData:
        """Process detailed analysis template."""
        # Include additional metadata and statistics
        export_data.metadata.update({
            'analysis_depth': 'detailed',
            'include_statistics': True,
            'include_charts': True
        })
        return export_data
    
    def _process_compliance_template(self, export_data: ExportData) -> ExportData:
        """Process compliance report template."""
        # Add compliance-specific metadata
        export_data.metadata.update({
            'compliance_framework': 'GDPR',
            'audit_trail_included': True,
            'data_retention_policy': f"{export_data.retention_days} days"
        })
        return export_data
    
    def _process_performance_template(self, export_data: ExportData) -> ExportData:
        """Process performance metrics template."""
        # Focus on performance data
        if hasattr(export_data, 'metrics'):
            export_data.metadata.update({
                'performance_focus': True,
                'metrics_included': True
            })
        return export_data
    
    def _process_security_template(self, export_data: ExportData) -> ExportData:
        """Process security audit template."""
        # Add security-specific metadata
        export_data.metadata.update({
            'security_classification': export_data.data_classification,
            'access_controls': True,
            'encryption_applied': export_data.configuration.password_protect
        })
        return export_data
    
    def _process_financial_template(self, export_data: ExportData) -> ExportData:
        """Process financial summary template."""
        # Add financial formatting
        export_data.configuration.decimal_precision = 2
        export_data.metadata.update({
            'currency_format': 'USD',
            'financial_period': 'quarterly'
        })
        return export_data
    
    def _process_technical_template(self, export_data: ExportData) -> ExportData:
        """Process technical report template."""
        # Add technical metadata
        export_data.metadata.update({
            'technical_details': True,
            'system_information': True,
            'diagnostic_data': True
        })
        return export_data


# Export main classes
__all__ = [
    'ExportSerializer',
    'ExportData',
    'ExportConfiguration',
    'ExportMetrics',
    'ExportFormat',
    'DataGrouping',
    'AggregationMethod',
    'ReportTemplate'
]
