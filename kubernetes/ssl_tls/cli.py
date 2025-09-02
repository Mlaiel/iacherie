"""IA Influencer Agent - SSL/TLS CLI Tools
Industrial-grade command-line interface for SSL/TLS management operations

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

Team Expertise:
- Lead Dev IA + Backend Senior + ML Engineer
- DBA + Security Expert + Microservices Architect
- Audio Processing + DevOps + Prompt Engineering

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized copying, distribution, or use without explicit written 
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
"""
import sys
import json
import argparse
import logging
import asyncio
import signal
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.syntax import Syntax

from .cert_manager import CertificateManager, create_certificate_manager
from .letsencrypt_manager import LetsEncryptManager, LetsEncryptConfig, CertificateRequest, ChallengeType
from .tls_config import TLSConfigManager, TLSConfig, create_tls_config_manager
from .cert_monitor import CertificateMonitor, CertificateEndpoint, create_certificate_monitor
from .ssl_utils import (
    SSLScanner, SSLValidator, CertificateConverter, SSLTestServer,
    validate_ssl_configuration, generate_csr, create_self_signed_cert
)

console = Console()
logger = logging.getLogger(__name__)


class SSLCLIManager:
    """Industrial-grade SSL/TLS Command Line Interface Manager"""
    
    def __init__(self):
        self.cert_manager = None
        self.letsencrypt_manager = None
        self.tls_config_manager = None
        self.cert_monitor = None
        self.ssl_scanner = None
        self.ssl_validator = None
        self.cert_converter = None
        self.test_server = None
        self._setup_components()
    
    def _setup_components(self):
        """Initialize all SSL/TLS components"""
        try:
            self.cert_manager = create_certificate_manager()
            self.tls_config_manager = create_tls_config_manager()
            self.cert_monitor = create_certificate_monitor()
            self.ssl_scanner = SSLScanner()
            self.ssl_validator = SSLValidator()
            self.cert_converter = CertificateConverter()
            self.test_server = SSLTestServer()
        except Exception as e:
            logger.error(f"Failed to initialize SSL/TLS components: {e}")
            console.print(f"[red]Error: Failed to initialize SSL/TLS components: {e}[/red]")


@config.command()
@click.argument('config_file')
@click.pass_context
def create(ctx, config_file):
    """Create TLS configuration file"""
    ssl_manager = ctx.obj['ssl_manager']
    config_path = Path(config_file)
    
    try:
        # Create default TLS configuration
        tls_config = TLSConfig(
            min_version="TLSv1.2",
            max_version="TLSv1.3",
            cipher_suites=[
                "TLS_AES_256_GCM_SHA384",
                "TLS_CHACHA20_POLY1305_SHA256",
                "TLS_AES_128_GCM_SHA256",
                "ECDHE-RSA-AES256-GCM-SHA384",
                "ECDHE-RSA-CHACHA20-POLY1305",
                "ECDHE-RSA-AES128-GCM-SHA256"
            ],
            certificate_path="/etc/ssl/certs/server.crt",
            private_key_path="/etc/ssl/private/server.key",
            ca_bundle_path="/etc/ssl/certs/ca-bundle.crt",
            enable_ocsp_stapling=True,
            enable_hsts=True,
            hsts_max_age=31536000,
            enable_session_resumption=True,
            session_timeout=300,
            enable_compression=False,
            require_client_cert=False
        )
        
        ssl_manager.tls_config_manager.save_config(tls_config, str(config_path))
        console.print(f"[green]✓ TLS configuration created: {config_path.absolute()}[/green]")
    
    except Exception as e:
        console.print(f"[red]Error creating TLS configuration: {e}[/red]")
        sys.exit(1)


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    """Setup industrial-grade logging configuration"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    else:
        handlers.append(logging.FileHandler('/var/log/ssl_manager.log'))
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        handlers=handlers
    )


@click.group()
@click.option('--log-level', default='INFO', help='Logging level')
@click.option('--log-file', default=None, help='Log file path')
@click.pass_context
def cli(ctx, log_level, log_file):
    """IA Influencer Agent SSL/TLS Management CLI"""
    ctx.ensure_object(dict)
    setup_logging(log_level, log_file)
    ctx.obj['ssl_manager'] = SSLCLIManager()


@cli.group()
def certificate():
    """Certificate management commands"""
    console.print("🔐 [bold blue]Certificate Management Commands[/bold blue]")
    console.print("Available subcommands:")
    console.print("  • generate    - Generate new certificates")
    console.print("  • list        - List existing certificates")
    console.print("  • renew       - Renew expiring certificates")
    console.print("  • revoke      - Revoke certificates")
    console.print("  • validate    - Validate certificate files")
    console.print("Example: ssl certificate generate --domain example.com")


@cli.group()
def scan():
    """SSL/TLS security scanning commands"""
    console.print("🔍 [bold blue]SSL/TLS Security Scanning[/bold blue]")
    console.print("Available subcommands:")
    console.print("  • domain      - Scan domain SSL configuration")
    console.print("  • endpoints   - Scan multiple endpoints")
    console.print("  • certificate - Analyze certificate details")
    console.print("  • vulnerabilities - Check for SSL vulnerabilities")
    console.print("  • ciphers     - Test supported cipher suites")
    console.print("Example: ssl scan domain --hostname example.com --port 443")


@cli.group()
def config():
    """TLS configuration management commands"""
    console.print("⚙️  [bold blue]TLS Configuration Management[/bold blue]")
    console.print("Available subcommands:")
    console.print("  • generate    - Generate TLS configuration files")
    console.print("  • validate    - Validate TLS configurations")
    console.print("  • optimize    - Optimize TLS settings for security")
    console.print("  • export      - Export configuration templates")
    console.print("  • import      - Import configuration from files")
    console.print("  • benchmark   - Benchmark TLS performance")
    console.print("Example: ssl config generate --type nginx --security-level high")


@cli.group()
def monitor():
    """Certificate monitoring commands"""
    console.print("📊 [bold blue]Certificate Monitoring[/bold blue]")
    console.print("Available subcommands:")
    console.print("  • start       - Start certificate monitoring service")
    console.print("  • status      - Check monitoring service status")
    console.print("  • alerts      - Configure expiration alerts")
    console.print("  • dashboard   - Launch monitoring dashboard")
    console.print("  • endpoints   - Add/remove monitoring endpoints")
    console.print("  • reports     - Generate monitoring reports")
    console.print("Example: ssl monitor start --interval 3600 --alert-days 30")


@cli.group()
def convert():
    """Certificate conversion commands"""
    console.print("🔄 [bold blue]Certificate Conversion[/bold blue]")
    console.print("Available subcommands:")
    console.print("  • pem-to-der  - Convert PEM format to DER")
    console.print("  • der-to-pem  - Convert DER format to PEM")
    console.print("  • p12-to-pem  - Convert PKCS#12 to PEM")
    console.print("  • pem-to-p12  - Convert PEM to PKCS#12")
    console.print("  • extract     - Extract components from certificates")
    console.print("  • combine     - Combine certificate and key files")
    console.print("Example: ssl convert pem-to-der --input cert.pem --output cert.der")


@cli.group()
def test():
    """SSL/TLS testing commands"""
    pass


@certificate.command()
@click.argument('domain')
@click.option('--provider', default='letsencrypt', help='Certificate provider')
@click.option('--challenge', default='http-01', help='Challenge type')
@click.option('--email', required=True, help='Email for registration')
@click.option('--staging', is_flag=True, help='Use staging environment')
@click.pass_context
def issue(ctx, domain, provider, challenge, email, staging):
    """Issue a new SSL certificate"""
    ssl_manager = ctx.obj['ssl_manager']
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(f"Issuing certificate for {domain}...", total=None)
        
        try:
            if provider == 'letsencrypt':
                config = LetsEncryptConfig(
                    email=email,
                    staging=staging,
                    key_size=2048
                )
                
                ssl_manager.letsencrypt_manager = LetsEncryptManager(config)
                
                cert_request = CertificateRequest(
                    domains=[domain],
                    challenge_type=ChallengeType(challenge),
                    key_size=2048
                )
                
                # Issue certificate
                result = ssl_manager.letsencrypt_manager.issue_certificate(cert_request)
                
                if result.success:
                    console.print(f"[green]✓ Certificate issued successfully for {domain}[/green]")
                    console.print(f"Certificate path: {result.certificate_path}")
                    console.print(f"Private key path: {result.private_key_path}")
                    console.print(f"Expiry date: {result.expiry_date}")
                else:
                    console.print(f"[red]✗ Failed to issue certificate: {result.error}[/red]")
                    sys.exit(1)
        except Exception as e:
            console.print(f"[red]✗ Certificate issuance failed: {e}[/red]")
            sys.exit(1)


@certificate.command()
@click.argument('domain')
@click.option('--days', default=30, help='Days until expiry to renew')
@click.pass_context
def renew(ctx, domain, days):
    """Renew SSL certificate"""
    ssl_manager = ctx.obj['ssl_manager']
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(f"Renewing certificate for {domain}...", total=None)
        
        try:
            result = ssl_manager.cert_manager.renew_certificate(domain, days_before_expiry=days)
            
            if result.success:
                console.print(f"[green]✓ Certificate renewed successfully for {domain}[/green]")
                console.print(f"New expiry date: {result.new_expiry_date}")
            else:
                console.print(f"[yellow]Certificate for {domain} does not need renewal yet[/yellow]")
        
        except Exception as e:
            console.print(f"[red]Error renewing certificate: {e}[/red]")
            sys.exit(1)


@certificate.command()
@click.argument('domain')
@click.pass_context
def revoke(ctx, domain):
    """Revoke SSL certificate"""
    ssl_manager = ctx.obj['ssl_manager']
    
    if not click.confirm(f"Are you sure you want to revoke the certificate for {domain}?"):
        return
    
    try:
        result = ssl_manager.cert_manager.revoke_certificate(domain)
        
        if result.success:
            console.print(f"[green]✓ Certificate revoked successfully for {domain}[/green]")
        else:
            console.print(f"[red]✗ Failed to revoke certificate: {result.error}[/red]")
            sys.exit(1)
    
    except Exception as e:
        console.print(f"[red]Error revoking certificate: {e}[/red]")
        sys.exit(1)


@certificate.command()
@click.pass_context
def list_certs(ctx):
    """List all managed certificates"""
    ssl_manager = ctx.obj['ssl_manager']
    
    try:
        certificates = ssl_manager.cert_manager.list_certificates()
        
        if not certificates:
            console.print("[yellow]No certificates found[/yellow]")
            return
        
        table = Table(title="Managed Certificates")
        table.add_column("Domain", style="cyan")
        table.add_column("Status", style="white")
        table.add_column("Expiry Date", style="white")
        table.add_column("Days Left", style="white")
        table.add_column("Issuer", style="white")
        
        for cert in certificates:
            status_color = "green" if cert.is_valid else "red"
            days_left_color = "red" if cert.days_until_expiry < 30 else "yellow" if cert.days_until_expiry < 60 else "green"
            
            table.add_row(
                cert.domain,
                f"[{status_color}]{'Valid' if cert.is_valid else 'Invalid'}[/{status_color}]",
                cert.expiry_date.strftime("%Y-%m-%d %H:%M:%S"),
                f"[{days_left_color}]{cert.days_until_expiry}[/{days_left_color}]",
                cert.issuer
            )
        
        console.print(table)
    
    except Exception as e:
        console.print(f"[red]Error listing certificates: {e}[/red]")
        sys.exit(1)


@certificate.command()
@click.argument('domain')
@click.argument('key_size', type=int, default=2048)
@click.argument('validity_days', type=int, default=365)
@click.option('--country', default='US', help='Country code')
@click.option('--state', default='CA', help='State or province')
@click.option('--city', default='San Francisco', help='City')
@click.option('--organization', default='IA Influencer Agent', help='Organization')
@click.option('--unit', default='IT Department', help='Organizational unit')
@click.pass_context
def self_signed(ctx, domain, key_size, validity_days, country, state, city, organization, unit):
    """Create self-signed certificate"""
    ssl_manager = ctx.obj['ssl_manager']
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(f"Creating self-signed certificate for {domain}...", total=None)
        
        try:
            cert_data, key_data = create_self_signed_cert(
                domain=domain,
                key_size=key_size,
                validity_days=validity_days,
                country=country,
                state=state,
                city=city,
                organization=organization,
                organizational_unit=unit
            )
            
            # Save certificate and key
            cert_path = Path(f"{domain}_cert.pem")
            key_path = Path(f"{domain}_key.pem")
            
            with open(cert_path, 'wb') as f:
                f.write(cert_data)
            
            with open(key_path, 'wb') as f:
                f.write(key_data)
            
            console.print(f"[green]✓ Self-signed certificate created for {domain}[/green]")
            console.print(f"Certificate: {cert_path.absolute()}")
            console.print(f"Private key: {key_path.absolute()}")
            console.print(f"Valid for: {validity_days} days")
        
        except Exception as e:
            console.print(f"[red]Error creating self-signed certificate: {e}[/red]")
            sys.exit(1)


@scan.command()
@click.argument('host')
@click.option('--port', default=443, help='Port to scan')
@click.option('--timeout', default=10, help='Connection timeout')
@click.pass_context
def host(ctx, host, port, timeout):
    """Scan SSL/TLS configuration of a host"""
    ssl_manager = ctx.obj['ssl_manager']
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(f"Scanning {host}:{port}...", total=None)
        
        try:
            scan_result = ssl_manager.ssl_scanner.scan_host(host, port, timeout)
            
            # Create scan results table
            table = Table(title=f"SSL/TLS Scan Results: {host}:{port}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="white")
            table.add_column("Status", style="white")
            
            # Connection info
            table.add_row("Connection", "Success" if scan_result.is_connected else "Failed", 
                         "✓" if scan_result.is_connected else "✗")
            
            if scan_result.is_connected:
                table.add_row("TLS Version", scan_result.tls_version or "Unknown", "")
                table.add_row("Cipher Suite", scan_result.cipher_suite or "Unknown", "")
                
                # Certificate info
                if scan_result.certificate_info:
                    cert_info = scan_result.certificate_info
                    table.add_row("Certificate Subject", cert_info.get('subject', 'Unknown'), "")
                    table.add_row("Certificate Issuer", cert_info.get('issuer', 'Unknown'), "")
                    table.add_row("Certificate Expiry", cert_info.get('not_after', 'Unknown'), "")
                    
                    # Check expiry
                    if cert_info.get('days_until_expiry'):
                        days_left = cert_info['days_until_expiry']
                        status = "✗" if days_left < 0 else "⚠" if days_left < 30 else "✓"
                        table.add_row("Days Until Expiry", str(days_left), status)
                
                # Security assessment
                if scan_result.security_issues:
                    table.add_row("Security Issues", str(len(scan_result.security_issues)), "⚠")
                else:
                    table.add_row("Security Issues", "None", "✓")
            
            console.print(table)
            
            # Show security issues if any
            if scan_result.security_issues:
                console.print("\n[bold red]Security Issues Found:[/bold red]")
                for issue in scan_result.security_issues:
                    console.print(f"  ✗ {issue}")
            
            # Show recommendations
            if scan_result.recommendations:
                console.print("\n[bold yellow]Recommendations:[/bold yellow]")
                for rec in scan_result.recommendations:
                    console.print(f"  ➤ {rec}")
        
        except Exception as e:
            console.print(f"[red]Error scanning host: {e}[/red]")
            sys.exit(1)


@scan.command()
@click.argument('config_file')
@click.pass_context
def bulk(ctx, config_file):
    """Scan multiple hosts from configuration file"""
    ssl_manager = ctx.obj['ssl_manager']
    config_path = Path(config_file)
    
    if not config_path.exists():
        console.print(f"[red]Configuration file {config_path} does not exist[/red]")
        sys.exit(1)
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        hosts = config.get('hosts', [])
        if not hosts:
            console.print("[yellow]No hosts found in configuration file[/yellow]")
            return
        
        results = []
        with Progress(console=console) as progress:
            task = progress.add_task("Scanning hosts...", total=len(hosts))
            
            for host_config in hosts:
                host = host_config['host']
                port = host_config.get('port', 443)
                timeout = host_config.get('timeout', 10)
                
                try:
                    scan_result = ssl_manager.ssl_scanner.scan_host(host, port, timeout)
                    results.append({
                        'host': host,
                        'port': port,
                        'result': scan_result
                    })
                except Exception as e:
                    results.append({
                        'host': host,
                        'port': port,
                        'error': str(e)
                    })
                
                progress.advance(task)
        
        # Display bulk scan results
        table = Table(title="Bulk SSL/TLS Scan Results")
        table.add_column("Host", style="cyan")
        table.add_column("Port", style="white")
        table.add_column("Status", style="white")
        table.add_column("TLS Version", style="white")
        table.add_column("Expiry", style="white")
        table.add_column("Issues", style="white")
        
        for result in results:
            if 'error' in result:
                table.add_row(
                    result['host'],
                    str(result['port']),
                    "[red]Error[/red]",
                    "",
                    "",
                    result['error']
                )
            else:
                scan_result = result['result']
                status = "[green]Connected[/green]" if scan_result.is_connected else "[red]Failed[/red]"
                tls_version = scan_result.tls_version or "Unknown"
                
                expiry = ""
                if scan_result.certificate_info and scan_result.certificate_info.get('days_until_expiry'):
                    days = scan_result.certificate_info['days_until_expiry']
                    color = "red" if days < 0 else "yellow" if days < 30 else "green"
                    expiry = f"[{color}]{days} days[/{color}]"
                
                issues_count = len(scan_result.security_issues) if scan_result.security_issues else 0
                issues_color = "red" if issues_count > 0 else "green"
                issues = f"[{issues_color}]{issues_count}[/{issues_color}]"
                
                table.add_row(
                    result['host'],
                    str(result['port']),
                    status,
                    tls_version,
                    expiry,
                    issues
                )
        
        console.print(table)
    
    except Exception as e:
        console.print(f"[red]Error performing bulk scan: {e}[/red]")
        sys.exit(1)
        sys.exit(1)
    
    try:
        with open(cert_path, 'rb') as f:
            cert_data = f.read()
        
        validation_result = ssl_manager.ssl_validator.validate_certificate(cert_data)
        
        # Create validation table
        table = Table(title=f"Certificate Validation: {cert_path.name}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        table.add_column("Status", style="green")
        
        table.add_row("Valid", str(validation_result.is_valid), 
                     "✓" if validation_result.is_valid else "✗")
        table.add_row("Subject", validation_result.subject or "N/A", "")
        table.add_row("Issuer", validation_result.issuer or "N/A", "")
        table.add_row("Serial Number", validation_result.serial_number or "N/A", "")
        table.add_row("Not Before", str(validation_result.not_before) if validation_result.not_before else "N/A", "")
        table.add_row("Not After", str(validation_result.not_after) if validation_result.not_after else "N/A", "")
        table.add_row("Expired", str(validation_result.is_expired), 
                     "✗" if validation_result.is_expired else "✓")
        table.add_row("Self-Signed", str(validation_result.is_self_signed), "")
        table.add_row("Key Algorithm", validation_result.key_algorithm or "N/A", "")
        table.add_row("Key Size", str(validation_result.key_size) if validation_result.key_size else "N/A", "")
        table.add_row("Signature Algorithm", validation_result.signature_algorithm or "N/A", "")
        
        console.print(table)
        
        if validation_result.extensions:
            console.print("\n[bold]Certificate Extensions:[/bold]")
            for ext in validation_result.extensions:
                console.print(f"  {ext}")
        
        if validation_result.errors:
            console.print("\n[bold red]Validation Errors:[/bold red]")
            for error in validation_result.errors:
                console.print(f"  ✗ {error}")
        
        if validation_result.warnings:
            console.print("\n[bold yellow]Warnings:[/bold yellow]")
            for warning in validation_result.warnings:
                console.print(f"  ⚠ {warning}")
    
    except Exception as e:
        console.print(f"[red]Error validating certificate: {e}[/red]")
        sys.exit(1)
    
    result = SSLValidator.validate_certificate_file(cert_path)
    
    if args.output_format == 'json':
        print(json.dumps(result, indent=2, default=str))
    else:
        if result['valid']:
            print("✅ Certificate is valid")
            print(f"   Common Name: {result.get('common_name', 'N/A')}")
            print(f"   Subject: {result.get('subject', 'N/A')}")
            print(f"   Issuer: {result.get('issuer', 'N/A')}")
            print(f"   Valid Until: {result.get('not_after', 'N/A')}")
            print(f"   Days Until Expiry: {result.get('days_until_expiry', 'N/A')}")
        else:
            print(f"❌ Certificate validation failed: {result['error']}")
            sys.exit(1)


def cmd_validate_config(args) -> None:
    """Validate SSL configuration"""
    cert_path = Path(args.certificate)
    key_path = Path(args.private_key)
    key_password = args.key_password.encode() if args.key_password else None
    
    result = validate_ssl_configuration(cert_path, key_path, key_password)
    
    if args.output_format == 'json':
        print(json.dumps(result, indent=2, default=str))
    else:
        if result['overall_valid']:
            print("✅ SSL configuration is valid")
            print("   Certificate: Valid")
            print("   Private Key: Valid")
            print("   Key Match: ✅" if result['key_match'] else "❌")
        else:
            print("❌ SSL configuration has issues:")
            for issue in result['issues']:
                print(f"   - {issue}")
        
        if result['recommendations']:
            print("\n💡 Recommendations:")
            for rec in result['recommendations']:
                print(f"   - {rec}")


def cmd_scan_host(args) -> None:
    """Scan SSL configuration of remote host"""
    scanner = SSLScanner(timeout=args.timeout)
    result = scanner.scan_host(args.hostname, args.port)
    
    if args.output_format == 'json':
        print(json.dumps(result, indent=2, default=str))
    else:
        if result['success']:
            print(f"✅ SSL scan successful for {args.hostname}:{args.port}")
            
            cert = result.get('certificate', {})
            if 'error' not in cert:
                print(f"\n📜 Certificate Information:")
                print(f"   Common Name: {cert.get('common_name', 'N/A')}")
                print(f"   Issuer: {cert.get('issuer', 'N/A')}")
                print(f"   Expires: {cert.get('not_after', 'N/A')}")
                print(f"   Days Until Expiry: {cert.get('days_until_expiry', 'N/A')}")
                print(f"   Key Size: {cert.get('key_size', 'N/A')} bits")
            
            protocols = result.get('protocols', {})
            print(f"\n🔒 Protocol Support:")
            for protocol, supported in protocols.items():
                status = "✅" if supported else "❌"
                print(f"   {protocol}: {status}")
            
            security = result.get('security_analysis', {})
            if security:
                print(f"\n🛡️ Security Analysis:")
                print(f"   Grade: {security.get('security_grade', 'N/A')}")
                print(f"   Score: {security.get('security_score', 'N/A')}/100")
                
                if security.get('issues'):
                    print(f"   Issues:")
                    for issue in security['issues']:
                        print(f"     - {issue}")
        else:
            print(f"❌ SSL scan failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)


def cmd_generate_csr(args) -> None:
    """Generate Certificate Signing Request"""
    config = {
        'cert_directory': str(Path(args.output_dir) / 'certs'),
        'key_directory': str(Path(args.output_dir) / 'private'),
        'ca_directory': str(Path(args.output_dir) / 'ca')
    }
    
    cert_manager = create_certificate_manager(config)
    
    # Generate private key
    private_key = cert_manager.generate_private_key(key_size=args.key_size)
    
    # Generate CSR
    san_list = args.san.split(',') if args.san else None
    csr = cert_manager.generate_csr(
        private_key=private_key,
        common_name=args.common_name,
        organization=args.organization,
        country=args.country,
        state=args.state,
        city=args.city,
        email=args.email,
        san_list=san_list
    )
    
    # Save files
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save private key
    key_path = output_dir / f"{args.common_name.replace('*', 'wildcard')}.key"
    key_password = args.key_password.encode() if args.key_password else None
    cert_manager.save_private_key(private_key, key_path, key_password)
    
    # Save CSR
    csr_path = output_dir / f"{args.common_name.replace('*', 'wildcard')}.csr"
    from cryptography.hazmat.primitives import serialization
    csr_pem = csr.public_bytes(serialization.Encoding.PEM)
    with open(csr_path, 'wb') as f:
        f.write(csr_pem)
    
    print(f"✅ CSR generated successfully")
    print(f"   Private Key: {key_path}")
    print(f"   CSR: {csr_path}")


def cmd_request_letsencrypt(args) -> None:
    """Request Let's Encrypt certificate"""
    config = LetsEncryptConfig(
        email=args.email,
        staging=args.staging,
        key_size=args.key_size,
        challenge_type=ChallengeType(args.challenge_type),
        webroot_path=args.webroot_path if args.challenge_type == 'http-01' else None,
        dns_provider=args.dns_provider,
        dns_credentials=json.loads(args.dns_credentials) if args.dns_credentials else None
    )
    
    manager = LetsEncryptManager(config)
    
    cert_request = CertificateRequest(
        domains=args.domains.split(','),
        email=args.email,
        challenge_type=ChallengeType(args.challenge_type),
        webroot_path=args.webroot_path,
        key_size=args.key_size
    )
    
    try:
        cert_pem, key_pem, chain_pem = manager.request_certificate(cert_request)
        print("✅ Let's Encrypt certificate issued successfully")
        print(f"   Domains: {args.domains}")
        print(f"   Certificate files saved to: /etc/letsencrypt/live/{args.domains.split(',')[0]}/")
    except Exception as e:
        print(f"❌ Certificate request failed: {e}")
        sys.exit(1)


def cmd_monitor_certificates(args) -> None:
    """Monitor certificate endpoints"""
    config_path = Path(args.config) if args.config else None
    monitor = create_certificate_monitor(config_path)
    
    if args.add_endpoint:
        # Add new endpoint
        endpoint = CertificateEndpoint(
            name=args.endpoint_name,
            hostname=args.hostname,
            port=args.port,
            check_interval=args.check_interval,
            warning_days=args.warning_days,
            critical_days=args.critical_days
        )
        monitor.add_endpoint(endpoint)
        
        if config_path:
            monitor.save_config(config_path)
        
        print(f"✅ Added endpoint: {args.endpoint_name}")
    
    elif args.check_now:
        # Perform immediate check
        if not monitor.endpoints:
            print("❌ No endpoints configured")
            sys.exit(1)
        
        print("🔍 Checking certificates...")
        for endpoint in monitor.endpoints:
            if endpoint.enabled:
                try:
                    status = monitor.check_certificate(endpoint)
                    print(f"\n📋 {endpoint.name} ({endpoint.hostname}:{endpoint.port})")
                    print(f"   Status: {status.status.value}")
                    print(f"   Alert Level: {status.alert_level.value}")
                    print(f"   Days Until Expiry: {status.days_until_expiry}")
                    
                    if status.issues:
                        print("   Issues:")
                        for issue in status.issues:
                            print(f"     - {issue}")
                
                except Exception as e:
                    print(f"❌ Check failed for {endpoint.name}: {e}")
    
    elif args.start_monitoring:
        # Start continuous monitoring
        print("🚀 Starting certificate monitoring...")
        import asyncio
        try:
            asyncio.run(monitor.start_monitoring())
        except KeyboardInterrupt:
            print("\n⏹️ Monitoring stopped by user")
            monitor.stop_monitoring()


def cmd_generate_config(args) -> None:
    """Generate TLS configuration"""
    tls_config_manager = create_tls_config_manager()
    
    from .tls_config import TLSConfig, TLSVersion, CipherSuite, SecurityLevel
    
    # Create TLS configuration
    tls_config = TLSConfig(
        min_tls_version=TLSVersion(args.min_tls_version),
        cipher_suite=CipherSuite(args.cipher_suite),
        security_level=SecurityLevel(args.security_level),
        certificate_path=args.certificate,
        private_key_path=args.private_key,
        enable_hsts=args.enable_hsts,
        enable_ocsp_stapling=args.enable_ocsp_stapling
    )
    
    if args.server_type == 'nginx':
        from .tls_config import NginxTLSConfig
        
        nginx_config = NginxTLSConfig(
            server_name=args.server_name,
            ssl_certificate=args.certificate,
            ssl_certificate_key=args.private_key,
            listen_port=args.port
        )
        
        config_content = tls_config_manager.generate_nginx_config(tls_config, nginx_config)
        
    elif args.server_type == 'apache':
        from .tls_config import ApacheTLSConfig
        
        apache_config = ApacheTLSConfig(
            server_name=args.server_name,
            document_root=args.document_root or '/var/www/html',
            ssl_certificate_file=args.certificate,
            ssl_certificate_key_file=args.private_key,
            virtual_host_port=args.port
        )
        
        config_content = tls_config_manager.generate_apache_config(tls_config, apache_config)
    
    else:
        print(f"❌ Unsupported server type: {args.server_type}")
        sys.exit(1)
    
    # Save configuration
    output_path = Path(args.output)
    with open(output_path, 'w') as f:
        f.write(config_content)
    
    print(f"✅ {args.server_type.title()} configuration generated: {output_path}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="IA Influencer Agent SSL/TLS Management Tools",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--log-level', 
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level'
    )
    
    parser.add_argument(
        '--output-format',
        choices=['text', 'json'],
        default='text',
        help='Output format'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Certificate validation
    validate_parser = subparsers.add_parser('validate-cert', help='Validate certificate file')
    validate_parser.add_argument('certificate', help='Path to certificate file')
    
    # SSL configuration validation
    config_parser = subparsers.add_parser('validate-config', help='Validate SSL configuration')
    config_parser.add_argument('certificate', help='Path to certificate file')
    config_parser.add_argument('private_key', help='Path to private key file')
    config_parser.add_argument('--key-password', help='Private key password')
    
    # SSL host scanning
    scan_parser = subparsers.add_parser('scan', help='Scan SSL configuration of remote host')
    scan_parser.add_argument('hostname', help='Target hostname')
    scan_parser.add_argument('--port', type=int, default=443, help='Target port')
    scan_parser.add_argument('--timeout', type=int, default=10, help='Connection timeout')
    
    # CSR generation
    csr_parser = subparsers.add_parser('generate-csr', help='Generate Certificate Signing Request')
    csr_parser.add_argument('common_name', help='Certificate common name')
    csr_parser.add_argument('organization', help='Organization name')
    csr_parser.add_argument('country', help='Country code (2 letters)')
    csr_parser.add_argument('--state', help='State/province name')
    csr_parser.add_argument('--city', help='City/locality name')
    csr_parser.add_argument('--email', help='Email address')
    csr_parser.add_argument('--san', help='Subject Alternative Names (comma-separated)')
    csr_parser.add_argument('--key-size', type=int, default=2048, help='RSA key size')
    csr_parser.add_argument('--key-password', help='Private key password')
    csr_parser.add_argument('--output-dir', default='.', help='Output directory')
    
    # Let's Encrypt certificate request
    le_parser = subparsers.add_parser('letsencrypt', help='Request Let\'s Encrypt certificate')
    le_parser.add_argument('domains', help='Comma-separated list of domains')
    le_parser.add_argument('email', help='Email address for account registration')
    le_parser.add_argument('--staging', action='store_true', help='Use staging environment')
    le_parser.add_argument('--challenge-type', choices=['http-01', 'dns-01'], default='http-01')
    le_parser.add_argument('--webroot-path', default='/var/www/html', help='Webroot path for HTTP challenge')
    le_parser.add_argument('--dns-provider', help='DNS provider for DNS challenge')
    le_parser.add_argument('--dns-credentials', help='DNS provider credentials (JSON)')
    le_parser.add_argument('--key-size', type=int, default=2048, help='RSA key size')
    
    # Certificate monitoring
    monitor_parser = subparsers.add_parser('monitor', help='Monitor certificates')
    monitor_parser.add_argument('--config', help='Path to monitoring configuration file')
    monitor_parser.add_argument('--add-endpoint', action='store_true', help='Add new endpoint')
    monitor_parser.add_argument('--check-now', action='store_true', help='Check all endpoints now')
    monitor_parser.add_argument('--start-monitoring', action='store_true', help='Start continuous monitoring')
    monitor_parser.add_argument('--endpoint-name', help='Endpoint name (for --add-endpoint)')
    monitor_parser.add_argument('--hostname', help='Hostname (for --add-endpoint)')
    monitor_parser.add_argument('--port', type=int, default=443, help='Port (for --add-endpoint)')
    monitor_parser.add_argument('--check-interval', type=int, default=3600, help='Check interval in seconds')
    monitor_parser.add_argument('--warning-days', type=int, default=30, help='Warning threshold in days')
    monitor_parser.add_argument('--critical-days', type=int, default=7, help='Critical threshold in days')
    
    # TLS configuration generation
    gen_parser = subparsers.add_parser('generate-config', help='Generate web server TLS configuration')
    gen_parser.add_argument('server_type', choices=['nginx', 'apache'], help='Web server type')
    gen_parser.add_argument('server_name', help='Server name')
    gen_parser.add_argument('certificate', help='Path to certificate file')
    gen_parser.add_argument('private_key', help='Path to private key file')
    gen_parser.add_argument('output', help='Output configuration file path')
    gen_parser.add_argument('--port', type=int, default=443, help='HTTPS port')
    gen_parser.add_argument('--document-root', help='Document root (Apache only)')
    gen_parser.add_argument('--min-tls-version', default='TLSv1.2', help='Minimum TLS version')
    gen_parser.add_argument('--cipher-suite', choices=['modern', 'intermediate', 'old'], default='intermediate')
    gen_parser.add_argument('--security-level', choices=['low', 'medium', 'high', 'maximum'], default='high')
    gen_parser.add_argument('--enable-hsts', action='store_true', default=True, help='Enable HSTS')
    gen_parser.add_argument('--enable-ocsp-stapling', action='store_true', default=True, help='Enable OCSP stapling')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Execute command
    try:
        if args.command == 'validate-cert':
            cmd_validate_cert(args)
        elif args.command == 'validate-config':
            cmd_validate_config(args)
        elif args.command == 'scan':
            cmd_scan_host(args)
        elif args.command == 'generate-csr':
            cmd_generate_csr(args)
        elif args.command == 'letsencrypt':
            cmd_request_letsencrypt(args)
        elif args.command == 'monitor':
            cmd_monitor_certificates(args)
        elif args.command == 'generate-config':
            cmd_generate_config(args)
        else:
            print(f"Unknown command: {args.command}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n⏹️ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Command failed: {e}")
        if args.log_level == 'DEBUG':
            raise
        else:
            print(f"❌ Error: {e}")
            sys.exit(1)


if __name__ == '__main__':
    main()
