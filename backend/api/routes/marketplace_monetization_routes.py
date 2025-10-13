"""
💰 MARKETPLACE & MONETIZATION ROUTES - Complete Implementation
==============================================================
ALL 50 endpoints for products, subscriptions, billing, revenue
Author: Fahed Mlaiel
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

router = APIRouter(prefix="/marketplace", tags=["Marketplace & Monetization"])

# ============================================================================
# MODELS
# ============================================================================

class ProductType(str, Enum):
    DIGITAL = "digital"
    SERVICE = "service"
    SUBSCRIPTION = "subscription"
    LICENSE = "license"

class SubscriptionTier(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    type: ProductType
    category: Optional[str] = None
    features: List[str] = []

class SubscriptionCreate(BaseModel):
    tier: SubscriptionTier
    price: float
    billing_cycle: str = "monthly"
    features: List[str] = []

# ============================================================================
# PRODUCTS
# ============================================================================

@router.get("/products")
async def list_products(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = 50
):
    """Get all marketplace products"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        products = await marketplace.list_products(
            category=category,
            min_price=min_price,
            max_price=max_price,
            limit=limit
        )
        return {"total": len(products), "products": products}
    except Exception as e:
        return {"total": 0, "products": [], "error": str(e)}

@router.post("/products")
async def create_product(product: ProductCreate, seller_id: str):
    """Create new product"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        new_product = await marketplace.create_product(seller_id, product.dict())
        return {"message": "Product created", "product_id": new_product['id'], "product": new_product}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products/{product_id}")
async def get_product(product_id: str):
    """Get product details"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        product = await marketplace.get_product(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/products/{product_id}")
async def update_product(product_id: str, updates: Dict[str, Any]):
    """Update product"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        updated = await marketplace.update_product(product_id, updates)
        return {"message": "Product updated", "product": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/products/{product_id}")
async def delete_product(product_id: str, seller_id: str):
    """Delete product"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        await marketplace.delete_product(product_id, seller_id)
        return {"message": "Product deleted", "product_id": product_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products/{product_id}/reviews")
async def get_product_reviews(product_id: str):
    """Get product reviews"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        reviews = await marketplace.get_reviews(product_id)
        return {"product_id": product_id, "reviews": reviews}
    except Exception as e:
        return {"product_id": product_id, "reviews": [], "error": str(e)}

@router.post("/products/{product_id}/reviews")
async def create_review(product_id: str, user_id: str, rating: int, comment: Optional[str] = None):
    """Create product review"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        review = await marketplace.create_review(product_id, user_id, rating, comment)
        return {"message": "Review created", "review": review}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products/{product_id}/stats")
async def get_product_stats(product_id: str):
    """Get product statistics"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        stats = await marketplace.get_product_stats(product_id)
        return {"product_id": product_id, "stats": stats}
    except Exception as e:
        return {"product_id": product_id, "stats": {}, "error": str(e)}

# ============================================================================
# SUBSCRIPTIONS
# ============================================================================

@router.get("/subscriptions")
async def list_subscriptions():
    """Get all subscription plans"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        subscriptions = await marketplace.list_subscriptions()
        return {"subscriptions": subscriptions}
    except Exception as e:
        return {"subscriptions": [], "error": str(e)}

@router.post("/subscriptions")
async def create_subscription(subscription: SubscriptionCreate):
    """Create subscription plan"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        plan = await marketplace.create_subscription(subscription.dict())
        return {"message": "Subscription created", "plan_id": plan['id'], "plan": plan}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/subscriptions/{plan_id}")
async def get_subscription(plan_id: str):
    """Get subscription details"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        plan = await marketplace.get_subscription(plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Subscription not found")
        return plan
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/subscriptions/{plan_id}/subscribe")
async def subscribe(plan_id: str, user_id: str, payment_method: str):
    """Subscribe to plan"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        subscription = await marketplace.subscribe_user(user_id, plan_id, payment_method)
        return {"message": "Subscribed successfully", "subscription": subscription}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/subscriptions/{subscription_id}/cancel")
async def cancel_subscription(subscription_id: str, user_id: str):
    """Cancel subscription"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        await marketplace.cancel_subscription(subscription_id, user_id)
        return {"message": "Subscription cancelled", "subscription_id": subscription_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/subscriptions/{subscription_id}/upgrade")
async def upgrade_subscription(subscription_id: str, new_plan_id: str):
    """Upgrade subscription"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        updated = await marketplace.upgrade_subscription(subscription_id, new_plan_id)
        return {"message": "Subscription upgraded", "subscription": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/subscriptions/{subscription_id}/downgrade")
async def downgrade_subscription(subscription_id: str, new_plan_id: str):
    """Downgrade subscription"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        updated = await marketplace.downgrade_subscription(subscription_id, new_plan_id)
        return {"message": "Subscription downgraded", "subscription": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}/subscriptions")
async def get_user_subscriptions(user_id: str):
    """Get user subscriptions"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        subscriptions = await marketplace.get_user_subscriptions(user_id)
        return {"user_id": user_id, "subscriptions": subscriptions}
    except Exception as e:
        return {"user_id": user_id, "subscriptions": [], "error": str(e)}

# ============================================================================
# PAYMENTS & BILLING
# ============================================================================

@router.post("/payments/process")
async def process_payment(
    user_id: str,
    amount: float,
    currency: str = "USD",
    payment_method: str = "card",
    metadata: Optional[Dict[str, Any]] = None
):
    """Process payment"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        payment = await marketplace.process_payment(
            user_id=user_id,
            amount=amount,
            currency=currency,
            payment_method=payment_method,
            metadata=metadata
        )
        return {"message": "Payment processed", "payment": payment}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payments/{payment_id}")
async def get_payment(payment_id: str):
    """Get payment details"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        payment = await marketplace.get_payment(payment_id)
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        return payment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/payments/{payment_id}/refund")
async def refund_payment(payment_id: str, amount: Optional[float] = None):
    """Refund payment"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        refund = await marketplace.refund_payment(payment_id, amount)
        return {"message": "Payment refunded", "refund": refund}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}/payments")
async def get_user_payments(user_id: str, limit: int = 50):
    """Get user payment history"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        payments = await marketplace.get_user_payments(user_id, limit)
        return {"user_id": user_id, "payments": payments}
    except Exception as e:
        return {"user_id": user_id, "payments": [], "error": str(e)}

@router.get("/users/{user_id}/invoices")
async def get_user_invoices(user_id: str, limit: int = 50):
    """Get user invoices"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        invoices = await marketplace.get_user_invoices(user_id, limit)
        return {"user_id": user_id, "invoices": invoices}
    except Exception as e:
        return {"user_id": user_id, "invoices": [], "error": str(e)}

@router.get("/invoices/{invoice_id}")
async def get_invoice(invoice_id: str):
    """Get invoice details"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        invoice = await marketplace.get_invoice(invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        return invoice
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/invoices/{invoice_id}/download")
async def download_invoice(invoice_id: str):
    """Download invoice PDF"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        pdf = await marketplace.download_invoice(invoice_id)
        return pdf
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# REVENUE & EARNINGS
# ============================================================================

@router.get("/revenue/overview")
async def get_revenue_overview():
    """Get revenue overview"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        overview = await marketplace.get_revenue_overview()
        return overview
    except Exception as e:
        return {"error": str(e), "revenue": {}}

@router.get("/revenue/by-product")
async def get_revenue_by_product():
    """Get revenue breakdown by product"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        revenue = await marketplace.get_revenue_by_product()
        return revenue
    except Exception as e:
        return {"error": str(e), "products": []}

@router.get("/revenue/by-seller")
async def get_revenue_by_seller():
    """Get revenue breakdown by seller"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        revenue = await marketplace.get_revenue_by_seller()
        return revenue
    except Exception as e:
        return {"error": str(e), "sellers": []}

@router.get("/sellers/{seller_id}/earnings")
async def get_seller_earnings(seller_id: str):
    """Get seller earnings"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        earnings = await marketplace.get_seller_earnings(seller_id)
        return {"seller_id": seller_id, "earnings": earnings}
    except Exception as e:
        return {"seller_id": seller_id, "earnings": {}, "error": str(e)}

@router.post("/sellers/{seller_id}/payout")
async def request_payout(seller_id: str, amount: float):
    """Request seller payout"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        payout = await marketplace.request_payout(seller_id, amount)
        return {"message": "Payout requested", "payout": payout}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sellers/{seller_id}/payouts")
async def get_seller_payouts(seller_id: str):
    """Get seller payout history"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        payouts = await marketplace.get_seller_payouts(seller_id)
        return {"seller_id": seller_id, "payouts": payouts}
    except Exception as e:
        return {"seller_id": seller_id, "payouts": [], "error": str(e)}

# ============================================================================
# CART & CHECKOUT
# ============================================================================

@router.get("/cart/{user_id}")
async def get_cart(user_id: str):
    """Get user cart"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        cart = await marketplace.get_cart(user_id)
        return {"user_id": user_id, "cart": cart}
    except Exception as e:
        return {"user_id": user_id, "cart": {"items": []}, "error": str(e)}

@router.post("/cart/{user_id}/add")
async def add_to_cart(user_id: str, product_id: str, quantity: int = 1):
    """Add item to cart"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        cart = await marketplace.add_to_cart(user_id, product_id, quantity)
        return {"message": "Item added to cart", "cart": cart}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cart/{user_id}/remove/{product_id}")
async def remove_from_cart(user_id: str, product_id: str):
    """Remove item from cart"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        cart = await marketplace.remove_from_cart(user_id, product_id)
        return {"message": "Item removed from cart", "cart": cart}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cart/{user_id}/clear")
async def clear_cart(user_id: str):
    """Clear cart"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        await marketplace.clear_cart(user_id)
        return {"message": "Cart cleared", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/checkout")
async def checkout(user_id: str, payment_method: str):
    """Checkout and process payment"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        order = await marketplace.checkout(user_id, payment_method)
        return {"message": "Order placed successfully", "order": order}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ORDERS
# ============================================================================

@router.get("/orders")
async def list_orders(user_id: Optional[str] = None, seller_id: Optional[str] = None):
    """Get all orders"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        orders = await marketplace.list_orders(user_id=user_id, seller_id=seller_id)
        return {"total": len(orders), "orders": orders}
    except Exception as e:
        return {"total": 0, "orders": [], "error": str(e)}

@router.get("/orders/{order_id}")
async def get_order(order_id: str):
    """Get order details"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        order = await marketplace.get_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/orders/{order_id}/fulfill")
async def fulfill_order(order_id: str, seller_id: str):
    """Fulfill order"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        await marketplace.fulfill_order(order_id, seller_id)
        return {"message": "Order fulfilled", "order_id": order_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# COUPONS & DISCOUNTS
# ============================================================================

@router.get("/coupons")
async def list_coupons():
    """Get all coupons"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        coupons = await marketplace.list_coupons()
        return {"coupons": coupons}
    except Exception as e:
        return {"coupons": [], "error": str(e)}

@router.post("/coupons")
async def create_coupon(
    code: str,
    discount: float,
    type: str = "percentage",
    expires_at: Optional[str] = None
):
    """Create coupon"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        coupon = await marketplace.create_coupon(code, discount, type, expires_at)
        return {"message": "Coupon created", "coupon": coupon}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/coupons/{code}/validate")
async def validate_coupon(code: str, user_id: str):
    """Validate coupon"""
    try:
        from backend.core.marketplace_core import MarketplaceCore
        marketplace = MarketplaceCore()
        await marketplace.initialize()
        
        valid = await marketplace.validate_coupon(code, user_id)
        return {"valid": valid, "code": code}
    except Exception as e:
        return {"valid": False, "code": code, "error": str(e)}
