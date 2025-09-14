"""📊 Industrialization Metrics Dashboard
=====================================

Dashboard for displaying industrialization success metrics as specified
in the problem statement with both technical and business KPIs.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

try:
    from .industrialization_success_metrics import industrialization_metrics
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from industrialization_success_metrics import industrialization_metrics

logger = logging.getLogger(__name__)


class IndustrializationDashboard:
    """
    Dashboard for industrialization success metrics visualization and reporting
    """
    
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.metrics = industrialization_metrics
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get formatted dashboard data for visualization"""
        try:
            # Get all KPIs
            all_kpis = await self.metrics.get_all_kpis()
            
            # Format for dashboard display
            dashboard_data = {
                "title": "📊 MÉTRIQUES DE SUCCÈS INDUSTRIALISATION",
                "timestamp": datetime.now().isoformat(),
                "sections": {
                    "technical": {
                        "title": "🎯 KPIs TECHNIQUES",
                        "description": "Technical performance indicators for industrialization",
                        "kpis": self._format_kpis_for_display(all_kpis["technical_kpis"])
                    },
                    "business": {
                        "title": "💼 KPIs BUSINESS", 
                        "description": "Business performance indicators for industrialization",
                        "kpis": self._format_kpis_for_display(all_kpis["business_kpis"])
                    }
                },
                "summary": all_kpis["summary"],
                "alerts": await self.metrics.check_kpi_alerts()
            }
            
            return dashboard_data
            
        except Exception as e:
            self.logger.error(f"Error getting dashboard data: {str(e)}")
            raise
    
    def _format_kpis_for_display(self, kpis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format KPIs for dashboard display"""
        formatted_kpis = []
        
        for kpi_name, kpi_data in kpis.items():
            # Determine status based on achievement
            status = self._calculate_kpi_status(kpi_data)
            
            formatted_kpi = {
                "name": kpi_data["name"],
                "display_name": self._get_display_name(kpi_data["name"]),
                "objective": kpi_data["objective"],
                "measure": kpi_data["measure"],
                "current_value": kpi_data["current_value"],
                "target_value": kpi_data["target_value"],
                "unit": kpi_data["unit"],
                "status": status,
                "trend": kpi_data["trend"],
                "achievement_percentage": self._calculate_achievement_percentage(kpi_data),
                "last_updated": kpi_data["last_updated"]
            }
            formatted_kpis.append(formatted_kpi)
        
        return formatted_kpis
    
    def _get_display_name(self, kpi_name: str) -> str:
        """Get user-friendly display name for KPI"""
        display_names = {
            "uptime_sla": "Uptime SLA",
            "response_time_api": "Response Time API", 
            "error_rate": "Error Rate",
            "mttr": "MTTR (Mean Time to Repair)",
            "deployment_frequency": "Deployment Frequency",
            "security_score": "Security Score",
            "code_coverage": "Code Coverage",
            "technical_debt_ratio": "Technical Debt Ratio",
            "time_to_market": "Time to Market",
            "customer_satisfaction": "Customer Satisfaction",
            "cost_per_transaction": "Cost per Transaction",
            "revenue_growth": "Revenue Growth",
            "user_retention": "User Retention",
            "support_ticket_volume": "Support Ticket Volume"
        }
        return display_names.get(kpi_name, kpi_name.replace("_", " ").title())
    
    def _calculate_kpi_status(self, kpi_data: Dict[str, Any]) -> str:
        """Calculate KPI status (excellent, good, warning, critical)"""
        if kpi_data["current_value"] == 0.0:
            return "no_data"
        
        achievement = self._calculate_achievement_percentage(kpi_data)
        
        if achievement >= 100:
            return "excellent"
        elif achievement >= 90:
            return "good"
        elif achievement >= 80:
            return "warning"
        else:
            return "critical"
    
    def _calculate_achievement_percentage(self, kpi_data: Dict[str, Any]) -> float:
        """Calculate achievement percentage for a KPI"""
        if kpi_data["target_value"] == 0 or kpi_data["current_value"] == 0:
            return 0.0
        
        kpi_name = kpi_data["name"]
        
        # For metrics where higher is better
        if kpi_name in ["uptime_sla", "security_score", "code_coverage", "customer_satisfaction", 
                       "revenue_growth", "user_retention", "deployment_frequency"]:
            return (kpi_data["current_value"] / kpi_data["target_value"]) * 100
        
        # For metrics where lower is better
        else:
            if kpi_data["current_value"] <= kpi_data["target_value"]:
                return 100.0
            else:
                return (kpi_data["target_value"] / kpi_data["current_value"]) * 100
    
    async def generate_html_dashboard(self) -> str:
        """Generate HTML dashboard for web display"""
        dashboard_data = await self.get_dashboard_data()
        
        html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 MÉTRIQUES DE SUCCÈS INDUSTRIALISATION - Ainflue</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }}
        .dashboard {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(90deg, #4F46E5, #7C3AED);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .timestamp {{
            opacity: 0.8;
            margin-top: 10px;
        }}
        .content {{
            padding: 30px;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .section-title {{
            font-size: 1.8em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #4F46E5;
            display: inline-block;
        }}
        .kpis-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .kpi-card {{
            background: #f8fafc;
            border-radius: 15px;
            padding: 25px;
            border-left: 5px solid #4F46E5;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        .kpi-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        .kpi-card.excellent {{
            border-left-color: #10B981;
            background: linear-gradient(135deg, #f0fdf4, #f8fafc);
        }}
        .kpi-card.good {{
            border-left-color: #3B82F6;
            background: linear-gradient(135deg, #eff6ff, #f8fafc);
        }}
        .kpi-card.warning {{
            border-left-color: #F59E0B;
            background: linear-gradient(135deg, #fffbeb, #f8fafc);
        }}
        .kpi-card.critical {{
            border-left-color: #EF4444;
            background: linear-gradient(135deg, #fef2f2, #f8fafc);
        }}
        .kpi-name {{
            font-size: 1.3em;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 10px;
        }}
        .kpi-objective {{
            font-size: 1.1em;
            color: #4F46E5;
            font-weight: 500;
            margin-bottom: 8px;
        }}
        .kpi-measure {{
            color: #6b7280;
            font-size: 0.9em;
            margin-bottom: 15px;
        }}
        .kpi-value {{
            font-size: 2em;
            font-weight: 700;
            margin-bottom: 10px;
        }}
        .kpi-progress {{
            background: #e5e7eb;
            height: 8px;
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 10px;
        }}
        .kpi-progress-bar {{
            height: 100%;
            border-radius: 4px;
            transition: width 0.5s ease;
        }}
        .kpi-progress-bar.excellent {{
            background: linear-gradient(90deg, #10B981, #34D399);
        }}
        .kpi-progress-bar.good {{
            background: linear-gradient(90deg, #3B82F6, #60A5FA);
        }}
        .kpi-progress-bar.warning {{
            background: linear-gradient(90deg, #F59E0B, #FBBF24);
        }}
        .kpi-progress-bar.critical {{
            background: linear-gradient(90deg, #EF4444, #F87171);
        }}
        .kpi-trend {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 500;
        }}
        .trend-improving {{
            background: #d1fae5;
            color: #065f46;
        }}
        .trend-declining {{
            background: #fee2e2;
            color: #991b1b;
        }}
        .trend-stable {{
            background: #e0e7ff;
            color: #3730a3;
        }}
        .summary {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin: 30px 0;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .summary-item {{
            text-align: center;
        }}
        .summary-value {{
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 5px;
        }}
        .summary-label {{
            opacity: 0.9;
            font-size: 0.9em;
        }}
        .alerts {{
            margin-top: 30px;
        }}
        .alert {{
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            border-left: 4px solid;
        }}
        .alert.critical {{
            background: #fef2f2;
            border-left-color: #EF4444;
            color: #991b1b;
        }}
        .alert.warning {{
            background: #fffbeb;
            border-left-color: #F59E0B;
            color: #92400e;
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>{dashboard_data['title']}</h1>
            <div class="timestamp">Dernière mise à jour: {datetime.fromisoformat(dashboard_data['timestamp']).strftime('%d/%m/%Y %H:%M:%S')}</div>
        </div>
        
        <div class="content">
            <!-- Technical KPIs Section -->
            <div class="section">
                <h2 class="section-title">{dashboard_data['sections']['technical']['title']}</h2>
                <div class="kpis-grid">
"""
        
        # Add technical KPIs
        for kpi in dashboard_data['sections']['technical']['kpis']:
            achievement = kpi['achievement_percentage']
            html += f"""
                    <div class="kpi-card {kpi['status']}">
                        <div class="kpi-name">{kpi['display_name']}</div>
                        <div class="kpi-objective">Objectif: {kpi['objective']}</div>
                        <div class="kpi-measure">{kpi['measure']}</div>
                        <div class="kpi-value">{kpi['current_value']:.2f} {kpi['unit']}</div>
                        <div class="kpi-progress">
                            <div class="kpi-progress-bar {kpi['status']}" style="width: {min(achievement, 100):.1f}%"></div>
                        </div>
                        <div class="kpi-trend trend-{kpi['trend']}">{kpi['trend']}</div>
                    </div>
"""
        
        html += """
                </div>
            </div>
            
            <!-- Business KPIs Section -->
            <div class="section">
                <h2 class="section-title">💼 KPIs BUSINESS</h2>
                <div class="kpis-grid">
"""
        
        # Add business KPIs
        for kpi in dashboard_data['sections']['business']['kpis']:
            achievement = kpi['achievement_percentage']
            html += f"""
                    <div class="kpi-card {kpi['status']}">
                        <div class="kpi-name">{kpi['display_name']}</div>
                        <div class="kpi-objective">Objectif: {kpi['objective']}</div>
                        <div class="kpi-measure">{kpi['measure']}</div>
                        <div class="kpi-value">{kpi['current_value']:.2f} {kpi['unit']}</div>
                        <div class="kpi-progress">
                            <div class="kpi-progress-bar {kpi['status']}" style="width: {min(achievement, 100):.1f}%"></div>
                        </div>
                        <div class="kpi-trend trend-{kpi['trend']}">{kpi['trend']}</div>
                    </div>
"""
        
        # Add summary
        summary = dashboard_data['summary']
        html += f"""
                </div>
            </div>
            
            <!-- Summary Section -->
            <div class="summary">
                <h2>📈 Résumé Industrialisation</h2>
                <div class="summary-grid">
                    <div class="summary-item">
                        <div class="summary-value">{summary['overall_industrialization_score']:.1f}%</div>
                        <div class="summary-label">Score Global</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-value">{summary['technical_kpis_stats']['average_achievement']:.1f}%</div>
                        <div class="summary-label">KPIs Techniques</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-value">{summary['business_kpis_stats']['average_achievement']:.1f}%</div>
                        <div class="summary-label">KPIs Business</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-value">{summary['technical_kpis_stats']['kpis_on_target'] + summary['business_kpis_stats']['kpis_on_target']}</div>
                        <div class="summary-label">KPIs Atteints</div>
                    </div>
                </div>
            </div>
"""
        
        # Add alerts if any
        if dashboard_data['alerts']:
            html += """
            <div class="alerts">
                <h2>🚨 Alertes KPIs</h2>
"""
            for alert in dashboard_data['alerts']:
                html += f"""
                <div class="alert {alert['severity']}">
                    <strong>{alert['kpi_name']}</strong>: Valeur actuelle {alert['current_value']:.2f} {alert['unit']} 
                    (Objectif: {alert['objective']}) - Tendance: {alert['trend']}
                </div>
"""
            html += """
            </div>
"""
        
        html += """
        </div>
    </div>
</body>
</html>
"""
        return html
    
    async def export_metrics_table(self) -> str:
        """Export metrics in the exact format from the problem statement"""
        dashboard_data = await self.get_dashboard_data()
        
        # Technical KPIs table
        technical_table = """📊 MÉTRIQUES DE SUCCÈS INDUSTRIALISATION
🎯 KPIs TECHNIQUES
Métrique\tObjectif\tMesure
"""
        
        for kpi in dashboard_data['sections']['technical']['kpis']:
            technical_table += f"{kpi['display_name']}\t{kpi['objective']}\t{kpi['measure']}\n"
        
        # Business KPIs table  
        business_table = """💼 KPIs BUSINESS
Métrique\tObjectif\tMesure
"""
        
        for kpi in dashboard_data['sections']['business']['kpis']:
            business_table += f"{kpi['display_name']}\t{kpi['objective']}\t{kpi['measure']}\n"
        
        return technical_table + "\n" + business_table


# Global dashboard instance
industrialization_dashboard = IndustrializationDashboard()


async def main() -> None:
    """Test the dashboard"""
    logging.basicConfig(level=logging.INFO)
    
    # Update some sample metrics
    await industrialization_metrics.update_kpi_value("uptime_sla", 99.95)
    await industrialization_metrics.update_kpi_value("response_time_api", 150.0)
    await industrialization_metrics.update_kpi_value("error_rate", 0.05)
    await industrialization_metrics.update_kpi_value("customer_satisfaction", 4.6)
    await industrialization_metrics.update_kpi_value("revenue_growth", 22.5)
    
    # Generate dashboard
    dashboard_data = await industrialization_dashboard.get_dashboard_data()
    print(json.dumps(dashboard_data, indent=2))
    
    # Generate HTML dashboard
    html = await industrialization_dashboard.generate_html_dashboard()
    with open("/tmp/industrialization_dashboard.html", "w") as f:
        f.write(html)
    print("HTML dashboard saved to /tmp/industrialization_dashboard.html")


if __name__ == "__main__":
    asyncio.run(main())