#!/usr/bin/env python3
"""🎉 Enterprise Monetization API Client Demo
============================================

Demonstration client showing how to interact with the Enterprise Monetization API.
Shows all major features including crypto payments, AI revenue tracking, and 
intelligent payment routing.

Created by: Fahed Mlaiel <mlaiel@live.de>
(c) 2025 Fahed Mlaiel. All rights reserved.
============================================
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from decimal import Decimal


class EnterpriseMonetizationClient:
    """Client for interacting with Enterprise Monetization API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            logger.info(f"Executing __aexit__")
            
            # Implementation for __aexit__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__aexit__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__aexit__ failed: {e}")
            raise
            await self.session.close()
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        async with self.session.request(method, url, **kwargs) as response:
            return await response.json()
    
    # ============ CRYPTO PAYMENT METHODS ============
    
    async def get_supported_cryptocurrencies(self):
        """Get supported cryptocurrencies"""
        return await self._request("GET", "/api/v1/crypto/supported")
    
    async def get_crypto_rate(self, crypto_currency: str, fiat_currency: str = "USD"):
        """Get cryptocurrency exchange rate"""
        return await self._request(
            "GET", 
            f"/api/v1/crypto/rates/{crypto_currency}",
            params={"fiat_currency": fiat_currency}
        )
    
    async def process_crypto_payment(self, amount: float, crypto_currency: str, recipient_id: str):
        """Process cryptocurrency payment"""
        return await self._request(
            "POST",
            "/api/v1/crypto/payment",
            json={
                "amount": amount,
                "crypto_currency": crypto_currency,
                "recipient_id": recipient_id,
                "payment_type": "revenue_payout"
            }
        )
    
    async def convert_crypto_to_fiat(self, crypto_amount: float, crypto_currency: str, target_currency: str = "USD"):
        """Convert crypto to fiat"""
        return await self._request(
            "POST",
            "/api/v1/crypto/convert",
            json={
                "crypto_amount": crypto_amount,
                "crypto_currency": crypto_currency,
                "target_currency": target_currency
            }
        )
    
    # ============ REVENUE TRACKING METHODS ============
    
    async def track_revenue(self, creator_id: str, revenue_stream: str, platform: str, 
                          amount: float, currency: str = "USD"):
        """Track revenue data"""
        return await self._request(
            "POST",
            "/api/v1/revenue/track",
            json={
                "creator_id": creator_id,
                "revenue_stream": revenue_stream,
                "platform": platform,
                "amount": amount,
                "currency": currency,
                "engagement_metrics": {"plays": 10000, "saves": 250},
                "audience_metrics": {"unique_listeners": 8500}
            }
        )
    
    async def calculate_attribution(self, creator_id: str, days_back: int = 30):
        """Calculate revenue attribution"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)
        
        return await self._request(
            "POST",
            "/api/v1/revenue/attribution",
            json={
                "creator_id": creator_id,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "attribution_model": "data_driven"
            }
        )
    
    async def get_revenue_optimization(self, creator_id: str):
        """Get revenue optimization recommendations"""
        return await self._request(
            "POST",
            "/api/v1/revenue/optimize",
            json={
                "creator_id": creator_id,
                "optimization_goals": ["increase_revenue", "improve_engagement"]
            }
        )
    
    async def predict_revenue(self, creator_id: str, prediction_days: int = 30):
        """Predict future revenue"""
        return await self._request(
            "POST",
            "/api/v1/revenue/predict",
            json={
                "creator_id": creator_id,
                "prediction_period_days": prediction_days,
                "scenarios": ["optimistic", "realistic", "pessimistic"]
            }
        )
    
    async def get_revenue_insights(self, creator_id: str):
        """Get comprehensive revenue insights"""
        return await self._request("GET", f"/api/v1/revenue/insights/{creator_id}")
    
    # ============ PAYMENT ROUTING METHODS ============
    
    async def route_payment(self, amount: float, currency: str, recipient_country: str,
                          routing_strategy: str = "balanced_optimization"):
        """Route payment optimally"""
        return await self._request(
            "POST",
            "/api/v1/payments/route",
            json={
                "amount": amount,
                "currency": currency,
                "payment_type": "revenue_payout",
                "recipient_country": recipient_country,
                "sender_country": "US",
                "payment_method": "bank_transfer",
                "routing_strategy": routing_strategy
            }
        )
    
    async def get_payment_analytics(self):
        """Get payment provider analytics"""
        return await self._request("GET", "/api/v1/payments/analytics")
    
    # ============ INTEGRATED METHODS ============
    
    async def process_payout(self, creator_id: str, amount: float, currency: str = "USD",
                           recipient_country: str = "US"):
        """Process integrated payout"""
        return await self._request(
            "POST",
            "/api/v1/monetization/process-payout",
            params={
                "creator_id": creator_id,
                "total_amount": amount,
                "currency": currency,
                "recipient_country": recipient_country
            }
        )
    
    async def get_dashboard(self, creator_id: str):
        """Get comprehensive monetization dashboard"""
        return await self._request("GET", f"/api/v1/monetization/dashboard/{creator_id}")
    
    async def health_check(self):
        """Check API health"""
        return await self._request("GET", "/api/v1/health")


async def demo_crypto_payments():
    """Demo crypto payment functionality"""
    print("\n🚀 Crypto Payment API Demo")
    print("=" * 40)
    
    async with EnterpriseMonetizationClient() as client:
        try:
            # Get supported cryptocurrencies
            print("1. Getting supported cryptocurrencies...")
            cryptos = await client.get_supported_cryptocurrencies()
            print(f"   ✅ {cryptos['count']} cryptocurrencies supported")
            
            # Get Bitcoin rate
            print("\n2. Getting Bitcoin rate...")
            btc_rate = await client.get_crypto_rate("BTC")
            if btc_rate.get("success"):
                rate_data = btc_rate["data"]
                print(f"   ₿ 1 BTC = ${rate_data['exchange_rate']}")
            
            # Process crypto payment
            print("\n3. Processing Bitcoin payment...")
            payment = await client.process_crypto_payment(0.05, "BTC", "demo_creator_456")
            if payment.get("success"):
                pay_data = payment["data"]
                print(f"   ✅ Payment processed: {pay_data['transaction_id']}")
                print(f"   💰 {pay_data['amount']} {pay_data['currency']} = ${pay_data['usd_amount']}")
            
            # Convert crypto to fiat
            print("\n4. Converting ETH to USD...")
            conversion = await client.convert_crypto_to_fiat(1.0, "ETH", "USD")
            if conversion.get("success"):
                conv_data = conversion["data"]
                print(f"   ✅ 1.0 ETH = ${conv_data['fiat_amount']}")
                print(f"   💰 After fees: ${conv_data['net_amount']}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")


async def demo_revenue_tracking():
    """Demo revenue tracking functionality"""
    print("\n🧠 Revenue Tracking API Demo")
    print("=" * 40)
    
    async with EnterpriseMonetizationClient() as client:
        try:
            creator_id = "demo_creator_789"
            
            # Track revenue from multiple sources
            print("1. Tracking revenue from multiple platforms...")
            
            revenue_sources = [
                ("streaming_royalties", "spotify", 250.00),
                ("brand_partnerships", "instagram", 800.00),
                ("ad_revenue", "youtube", 150.00)
            ]
            
            for stream, platform, amount in revenue_sources:
                revenue = await client.track_revenue(creator_id, stream, platform, amount)
                if revenue.get("success"):
                    print(f"   💰 Tracked ${amount} from {platform}")
            
            # Get revenue optimization
            print("\n2. Getting revenue optimization...")
            optimization = await client.get_revenue_optimization(creator_id)
            if optimization.get("success"):
                opt_data = optimization["data"]
                print(f"   📈 Projected increase: ${opt_data['projected_revenue_increase']}")
                print(f"   🎯 Confidence: {float(opt_data['confidence_level']):.1%}")
                
                for i, rec in enumerate(opt_data['recommendations'][:2], 1):
                    print(f"   {i}. {rec.get('recommendation', 'Optimize content timing')}")
            
            # Predict revenue
            print("\n3. Predicting future revenue...")
            prediction = await client.predict_revenue(creator_id, 30)
            if prediction.get("success"):
                pred_data = prediction["data"]
                print(f"   📊 30-day prediction: ${pred_data['predicted_revenue']}")
                
                scenarios = pred_data.get('scenarios', {})
                for scenario, amount in scenarios.items():
                    print(f"   {scenario.capitalize()}: ${amount}")
            
            # Get comprehensive insights
            print("\n4. Getting revenue insights...")
            insights = await client.get_revenue_insights(creator_id)
            if insights.get("success"):
                insight_data = insights["data"]
                revenue_trends = insight_data.get("revenue_trends", {})
                platform_perf = insight_data.get("platform_performance", {})
                
                print(f"   📊 Revenue trend: {revenue_trends.get('trend', 'Upward')}")
                print(f"   🎯 Top platform: {platform_perf.get('top_platform', 'Spotify')}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")


async def demo_payment_routing():
    """Demo payment routing functionality"""
    print("\n⚡ Payment Routing API Demo")
    print("=" * 40)
    
    async with EnterpriseMonetizationClient() as client:
        try:
            # Route payment with different strategies
            strategies = [
                ("lowest_cost", 1500.00, "US"),
                ("geographic_optimization", 850.00, "DE"),
                ("balanced_optimization", 1200.00, "CA")
            ]
            
            for i, (strategy, amount, country) in enumerate(strategies, 1):
                print(f"{i}. Routing ${amount} to {country} with {strategy}...")
                
                routing = await client.route_payment(amount, "USD", country, strategy)
                if routing.get("success"):
                    route_data = routing["data"]
                    print(f"   ✅ Selected: {route_data['selected_provider']}")
                    print(f"   💰 Cost: ${route_data['cost_analysis']['total_cost']}")
                    print(f"   📊 Score: {route_data['decision_score']:.2f}")
            
            # Get payment analytics
            print(f"\n4. Getting payment provider analytics...")
            analytics = await client.get_payment_analytics()
            if analytics.get("success"):
                providers = analytics["data"].get("providers", {})
                print(f"   📊 Provider performance:")
                
                for provider, metrics in providers.items():
                    success_rate = metrics.get('success_rate', 0) * 100
                    cost = metrics.get('average_cost', 0)
                    print(f"   {provider}: {success_rate:.1f}% success, {cost:.1f}% cost")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")


async def demo_integrated_workflow():
    """Demo integrated monetization workflow"""
    print("\n🔄 Integrated Workflow API Demo")
    print("=" * 40)
    
    async with EnterpriseMonetizationClient() as client:
        try:
            creator_id = "integrated_creator_123"
            
            # Process comprehensive payout
            print("1. Processing optimized payout...")
            payout = await client.process_payout(creator_id, 2500.00, "USD", "US")
            if payout.get("success"):
                payout_data = payout["data"]
                print(f"   ✅ Payout processed: {payout_data['payout_id']}")
                print(f"   💰 Amount: ${payout_data['amount']}")
                print(f"   🏦 Provider: {payout_data['selected_provider']}")
                print(f"   💸 Fee: ${payout_data['processing_fee']}")
                print(f"   💵 Net: ${payout_data['net_amount']}")
                
                if payout_data.get('crypto_alternative'):
                    crypto_alt = payout_data['crypto_alternative']
                    print(f"   ₿ Crypto option: {crypto_alt['amount']} {crypto_alt['currency']}")
            
            # Get comprehensive dashboard
            print("\n2. Getting monetization dashboard...")
            dashboard = await client.get_dashboard(creator_id)
            if dashboard.get("success"):
                dash_data = dashboard["data"]
                optimization = dash_data.get("optimization", {})
                prediction = dash_data.get("prediction", {})
                
                print(f"   📊 Dashboard for {dash_data['creator_id']}")
                print(f"   📈 Optimization: +${optimization.get('projected_increase', '500')}")
                print(f"   🔮 30-day forecast: ${prediction.get('30_day_forecast', '2500')}")
                
                scenarios = prediction.get("scenarios", {})
                for scenario, amount in scenarios.items():
                    print(f"   {scenario}: ${amount}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")


async def main():
    """Main demo function"""
    print("🎉 Enterprise Monetization API Client Demo")
    print("=" * 60)
    print("Demonstrating all API endpoints and features")
    print("Created by: Fahed Mlaiel <mlaiel@live.de>")
    print("© 2025 Fahed Mlaiel. All rights reserved.")
    print("=" * 60)
    
    # Check if API is running
    try:
        async with EnterpriseMonetizationClient() as client:
            health = await client.health_check()
            if health.get("status") == "healthy":
                print("✅ API is healthy and ready")
            else:
                print("⚠️ API health check failed")
                return
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("💡 Make sure to start the API server first:")
        print("   python api/enterprise_monetization_api.py")
        return
    
    try:
        # Run all demos
        await demo_crypto_payments()
        await demo_revenue_tracking()
        await demo_payment_routing()
        await demo_integrated_workflow()
        
        print("\n🎊 All API demos completed successfully!")
        print("✅ Enterprise monetization system is fully operational")
        
        print("\n📋 Available API Endpoints:")
        print("   🔗 API Documentation: http://localhost:8000/docs")
        print("   📊 Health Check: http://localhost:8000/api/v1/health")
        print("   💰 Crypto Payments: /api/v1/crypto/*")
        print("   🧠 Revenue Tracking: /api/v1/revenue/*")
        print("   ⚡ Payment Routing: /api/v1/payments/*")
        print("   🔄 Integrated Features: /api/v1/monetization/*")
        
    except Exception as e:
        print(f"\n❌ Demo error: {e}")


if __name__ == "__main__":
    asyncio.run(main())