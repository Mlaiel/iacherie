"""💳 Multi-Provider Payment Gateway Demo
=======================================

Demonstration of the unified payment gateway showing all supported payment types:
- Stripe Connect marketplace split payments
- PayPal Business escrow payments
- Wise international transfers
- Cryptocurrency payments (Bitcoin, Ethereum, USDC)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
from decimal import Decimal
from datetime import datetime, timedelta
import logging

from payment.multi_provider_gateway import (
    MultiProviderPaymentGateway,
    PaymentRequest,
    PaymentProvider,
    PaymentType,
    PaymentStatus
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def demo_marketplace_split_payment(gateway):
    """Demo Stripe Connect marketplace split payment"""
    print("\n🏪 === STRIPE CONNECT MARKETPLACE SPLIT PAYMENT ===")
    
    request = PaymentRequest(
        amount=Decimal("100.00"),
        currency="USD",
        payment_type=PaymentType.MARKETPLACE_SPLIT,
        provider=PaymentProvider.STRIPE_CONNECT,
        sender_id="customer_123",
        recipient_id="seller_456",
        description="Digital artwork purchase",
        platform_fee_percent=Decimal("0.025"),  # 2.5% platform fee
        recipients=[
            {"account_id": "seller_456", "amount": Decimal("97.50")},
            {"account_id": "platform", "amount": Decimal("2.50")}
        ]
    )
    
    response = await gateway.process_payment(request)
    
    print(f"✅ Payment processed: {response.transaction_id}")
    print(f"   Status: {response.status.value}")
    print(f"   Amount: ${response.amount}")
    print(f"   Platform Fee: ${response.fees['platform_fee']}")
    print(f"   Stripe Fee: ${response.fees['stripe_fee']}")
    print(f"   Provider Transaction: {response.provider_transaction_id}")
    
    return response


async def demo_paypal_escrow_payment(gateway):
    """Demo PayPal Business escrow payment"""
    print("\n🏦 === PAYPAL BUSINESS ESCROW PAYMENT ===")
    
    release_date = datetime.now() + timedelta(days=30)
    
    request = PaymentRequest(
        amount=Decimal("500.00"),
        currency="USD",
        payment_type=PaymentType.ESCROW_PAYMENT,
        provider=PaymentProvider.PAYPAL_BUSINESS,
        sender_id="buyer_789",
        recipient_id="freelancer_012",
        description="Website development project",
        escrow_release_date=release_date,
        escrow_conditions={
            "project_completion": True,
            "quality_approval": True,
            "testing_complete": True
        },
        metadata={"recipient_email": "freelancer@example.com"}
    )
    
    response = await gateway.process_payment(request)
    
    print(f"✅ Escrow created: {response.transaction_id}")
    print(f"   Status: {response.status.value}")
    print(f"   Amount: ${response.amount}")
    print(f"   Escrow ID: {response.escrow_id}")
    print(f"   PayPal Fee: ${response.fees['paypal_fee']}")
    print(f"   Release Date: {release_date.strftime('%Y-%m-%d')}")
    
    # Demo escrow release
    print("\n   ⏳ Simulating project completion...")
    await asyncio.sleep(1)
    
    release_result = await gateway.release_escrow(
        response.escrow_id,
        {
            "project_completion": True,
            "quality_approved": True,
            "testing_complete": True,
            "released_by": "buyer_789"
        }
    )
    
    print(f"   💰 Escrow released: ${release_result['amount']}")
    print(f"   Released at: {release_result['released_at']}")
    
    return response


async def demo_wise_international_transfer(gateway):
    """Demo Wise international transfer"""
    print("\n🌍 === WISE INTERNATIONAL TRANSFER ===")
    
    request = PaymentRequest(
        amount=Decimal("1000.00"),
        currency="USD",
        payment_type=PaymentType.INTERNATIONAL_TRANSFER,
        provider=PaymentProvider.WISE,
        sender_id="us_company",
        recipient_id="eu_contractor",
        description="Monthly contractor payment",
        recipient_country="DE",
        transfer_purpose="digital_services",
        metadata={"target_currency": "EUR"}
    )
    
    response = await gateway.process_payment(request)
    
    print(f"✅ International transfer initiated: {response.transaction_id}")
    print(f"   Status: {response.status.value}")
    print(f"   Amount: ${response.amount} USD")
    print(f"   Exchange Rate: {response.fees['exchange_rate']}")
    print(f"   Wise Fee: ${response.fees['wise_fee']}")
    print(f"   Estimated EUR: ~€{float(response.amount) * float(response.fees['exchange_rate']):.2f}")
    
    return response


async def demo_crypto_bitcoin_transfer(gateway):
    """Demo Bitcoin cryptocurrency transfer"""
    print("\n₿ === BITCOIN CRYPTOCURRENCY TRANSFER ===")
    
    request = PaymentRequest(
        amount=Decimal("0.01"),
        currency="BTC",
        payment_type=PaymentType.CRYPTO_TRANSFER,
        provider=PaymentProvider.CRYPTO,
        sender_id="crypto_user_1",
        recipient_id="crypto_user_2",
        description="NFT purchase payment",
        from_address="1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
        to_address="1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2",
        network="bitcoin"
    )
    
    response = await gateway.process_payment(request)
    
    print(f"✅ Bitcoin transfer initiated: {response.transaction_id}")
    print(f"   Status: {response.status.value}")
    print(f"   Amount: {response.amount} BTC")
    print(f"   Network Fee: {response.fees['network_fee']} BTC")
    print(f"   Processing Fee: {response.fees['processing_fee']} BTC")
    print(f"   From: {request.from_address}")
    print(f"   To: {request.to_address}")
    
    return response


async def demo_crypto_ethereum_transfer(gateway):
    """Demo Ethereum cryptocurrency transfer"""
    print("\n⟠ === ETHEREUM CRYPTOCURRENCY TRANSFER ===")
    
    request = PaymentRequest(
        amount=Decimal("0.5"),
        currency="ETH",
        payment_type=PaymentType.CRYPTO_TRANSFER,
        provider=PaymentProvider.CRYPTO,
        sender_id="eth_user_1",
        recipient_id="eth_user_2",
        description="Smart contract service payment",
        from_address="0x742d35cc694c048e5b1b1e6c9dcaa9999e2b8b4d",
        to_address="0x742d35cc694c048e5b1b1e6c9dcaa9999e2b8b4e",
        network="ethereum"
    )
    
    response = await gateway.process_payment(request)
    
    print(f"✅ Ethereum transfer initiated: {response.transaction_id}")
    print(f"   Status: {response.status.value}")
    print(f"   Amount: {response.amount} ETH")
    print(f"   Gas Fee: {response.fees['network_fee']} ETH")
    print(f"   Processing Fee: {response.fees['processing_fee']} ETH")
    
    return response


async def demo_crypto_usdc_transfer(gateway):
    """Demo USDC stablecoin transfer"""
    print("\n💵 === USDC STABLECOIN TRANSFER ===")
    
    request = PaymentRequest(
        amount=Decimal("1000.00"),
        currency="USDC",
        payment_type=PaymentType.CRYPTO_TRANSFER,
        provider=PaymentProvider.CRYPTO,
        sender_id="usdc_user_1",
        recipient_id="usdc_user_2",
        description="Subscription payment",
        from_address="0x742d35cc694c048e5b1b1e6c9dcaa9999e2b8b4d",
        to_address="0x742d35cc694c048e5b1b1e6c9dcaa9999e2b8b4f",
        network="ethereum"
    )
    
    response = await gateway.process_payment(request)
    
    print(f"✅ USDC transfer initiated: {response.transaction_id}")
    print(f"   Status: {response.status.value}")
    print(f"   Amount: {response.amount} USDC")
    print(f"   Network Fee: {response.fees['network_fee']} ETH")
    print(f"   Processing Fee: ${response.fees['processing_fee']}")
    
    return response


async def demo_transaction_tracking(gateway, transactions):
    """Demo transaction status tracking"""
    print("\n📊 === TRANSACTION STATUS TRACKING ===")
    
    for i, transaction in enumerate(transactions):
        status = await gateway.get_transaction_status(transaction.transaction_id)
        print(f"Transaction {i+1}: {status['transaction_id'][:12]}...")
        print(f"   Provider: {status['provider']}")
        print(f"   Status: {status['status']}")
        print(f"   Amount: {status['amount']} {status['currency']}")


async def main():
    """Main demo function"""
    print("🚀 === MULTI-PROVIDER PAYMENT GATEWAY DEMO ===")
    print("Demonstrating all supported payment providers and types")
    
    # Gateway configuration
    config = {
        "stripe": {
            "api_key": "sk_test_demo_key",
            "webhook_secret": "whsec_demo_secret"
        },
        "paypal": {
            "client_id": "demo_paypal_client",
            "client_secret": "demo_paypal_secret",
            "environment": "sandbox"
        },
        "wise": {
            "api_token": "demo_wise_token",
            "webhook_secret": "demo_wise_webhook"
        },
        "crypto": {
            "api_keys": {
                "coinbase": "demo_coinbase_key",
                "bitcoin": "demo_bitcoin_key"
            },
            "webhook_secret": "demo_crypto_webhook",
            "testnet": True
        }
    }
    
    # Initialize gateway
    gateway = MultiProviderPaymentGateway(config)
    print(f"✅ Gateway initialized with {len(gateway.processors)} providers")
    
    # Store transactions for tracking demo
    transactions = []
    
    try:
        # Demo all payment types
        transactions.append(await demo_marketplace_split_payment(gateway))
        transactions.append(await demo_paypal_escrow_payment(gateway))
        transactions.append(await demo_wise_international_transfer(gateway))
        transactions.append(await demo_crypto_bitcoin_transfer(gateway))
        transactions.append(await demo_crypto_ethereum_transfer(gateway))
        transactions.append(await demo_crypto_usdc_transfer(gateway))
        
        # Demo transaction tracking
        await demo_transaction_tracking(gateway, transactions)
        
        print("\n🎉 === DEMO COMPLETED SUCCESSFULLY ===")
        print("All payment providers and types demonstrated!")
        print(f"Total transactions processed: {len(transactions)}")
        
        # Summary
        total_volume = sum(float(tx.amount) for tx in transactions if tx.currency in ["USD", "USDC"])
        print(f"Total USD volume: ${total_volume:.2f}")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())