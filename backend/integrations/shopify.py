"""Shopify Integration - E-commerce Platform Integration
======================================================

Professional Shopify API integration for product management,
order processing, and influencer commerce features.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass
import json
import aiohttp
import hashlib
import hmac
import base64

logger = logging.getLogger(__name__)


class ProductStatus(str, Enum):
    """Product status options."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DRAFT = "draft"


class OrderStatus(str, Enum):
    """Order status options."""
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class FulfillmentStatus(str, Enum):
    """Fulfillment status options."""
    SHIPPED = "shipped"
    PARTIAL = "partial"
    UNSHIPPED = "unshipped"
    FULFILLED = "fulfilled"


class FinancialStatus(str, Enum):
    """Financial status options."""
    PENDING = "pending"
    AUTHORIZED = "authorized"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    PARTIALLY_REFUNDED = "partially_refunded"
    REFUNDED = "refunded"
    VOIDED = "voided"


@dataclass
class ShopifyProduct:
    """Shopify product."""
    product_id: int
    title: str
    body_html: str
    vendor: str
    product_type: str
    status: ProductStatus
    tags: List[str]
    variants: List[Dict[str, Any]]
    images: List[Dict[str, Any]]
    seo_title: Optional[str]
    seo_description: Optional[str]
    handle: str
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]


@dataclass
class ShopifyOrder:
    """Shopify order."""
    order_id: int
    order_number: str
    email: str
    financial_status: FinancialStatus
    fulfillment_status: Optional[FulfillmentStatus]
    total_price: Decimal
    subtotal_price: Decimal
    total_tax: Decimal
    currency: str
    line_items: List[Dict[str, Any]]
    customer: Optional[Dict[str, Any]]
    shipping_address: Optional[Dict[str, Any]]
    billing_address: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]


@dataclass
class ShopifyCustomer:
    """Shopify customer."""
    customer_id: int
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    verified_email: bool
    total_spent: Decimal
    orders_count: int
    state: str
    tags: List[str]
    addresses: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]


@dataclass
class ShopifyCollection:
    """Shopify collection."""
    collection_id: int
    title: str
    body_html: str
    sort_order: str
    template_suffix: Optional[str]
    disjunctive: bool
    rules: List[Dict[str, Any]]
    published_at: Optional[datetime]
    image: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]


class ShopifyIntegration:
    """Professional Shopify API integration."""
    
    def __init__(
        self,
        shop_domain: str,
        access_token: str,
        api_version: str = "2023-10",
        webhook_secret: Optional[str] = None,
        timeout: int = 30
    ):
        self.shop_domain = shop_domain.replace('.myshopify.com', '')
        self.access_token = access_token
        self.api_version = api_version
        self.webhook_secret = webhook_secret
        self.timeout = timeout
        self.base_url = f"https://{self.shop_domain}.myshopify.com/admin/api/{api_version}"
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Usage tracking
        self.request_count = 0
        self.products_managed = 0
        self.orders_processed = 0
        self.api_call_history: List[Dict[str, Any]] = []
        
        logger.info(f"Shopify integration initialized for shop: {shop_domain}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def _ensure_session(self):
        """Ensure HTTP session is available."""
        if self.session is None or self.session.closed:
            headers = {
                "X-Shopify-Access-Token": self.access_token,
                "Content-Type": "application/json",
                "User-Agent": "Ainflue/1.0"
            }
            
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
    
    async def close(self):
        """Close HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def get_shop_info(self) -> Dict[str, Any]:
        """Get shop information."""
        await self._ensure_session()
        
        try:
            async with self.session.get(f"{self.base_url}/shop.json") as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Shopify API error: {error_data}")
                
                result = await response.json()
                shop_info = result["shop"]
                
                self.request_count += 1
                self._add_to_history("get_shop_info", {}, shop_info)
                
                logger.info(f"Shop info retrieved: {shop_info.get('name')}")
                return shop_info
        
        except Exception as e:
            logger.error(f"Failed to get shop info: {e}")
            raise
    
    async def list_products(
        self,
        limit: int = 50,
        status: Optional[ProductStatus] = None,
        vendor: Optional[str] = None,
        product_type: Optional[str] = None,
        collection_id: Optional[int] = None
    ) -> List[ShopifyProduct]:
        """List products with filters."""
        await self._ensure_session()
        
        params = {"limit": min(limit, 250)}
        
        if status:
            params["status"] = status.value
        if vendor:
            params["vendor"] = vendor
        if product_type:
            params["product_type"] = product_type
        if collection_id:
            params["collection_id"] = collection_id
        
        try:
            async with self.session.get(
                f"{self.base_url}/products.json",
                params=params
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Shopify API error: {error_data}")
                
                result = await response.json()
                products = []
                
                for product_data in result.get("products", []):
                    product = ShopifyProduct(
                        product_id=product_data["id"],
                        title=product_data["title"],
                        body_html=product_data.get("body_html", ""),
                        vendor=product_data.get("vendor", ""),
                        product_type=product_data.get("product_type", ""),
                        status=ProductStatus(product_data.get("status", "active")),
                        tags=product_data.get("tags", "").split(", ") if product_data.get("tags") else [],
                        variants=product_data.get("variants", []),
                        images=product_data.get("images", []),
                        seo_title=product_data.get("seo_title"),
                        seo_description=product_data.get("seo_description"),
                        handle=product_data.get("handle", ""),
                        created_at=datetime.fromisoformat(product_data["created_at"].replace('Z', '+00:00')),
                        updated_at=datetime.fromisoformat(product_data["updated_at"].replace('Z', '+00:00')),
                        metadata={
                            "options": product_data.get("options", []),
                            "template_suffix": product_data.get("template_suffix")
                        }
                    )
                    products.append(product)
                
                self.request_count += 1
                self._add_to_history("list_products", params, {"count": len(products)})
                
                logger.info(f"Retrieved {len(products)} products")
                return products
        
        except Exception as e:
            logger.error(f"Failed to list products: {e}")
            raise
    
    async def get_product(self, product_id: int) -> ShopifyProduct:
        """Get specific product."""
        await self._ensure_session()
        
        try:
            async with self.session.get(f"{self.base_url}/products/{product_id}.json") as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Shopify API error: {error_data}")
                
                result = await response.json()
                product_data = result["product"]
                
                product = ShopifyProduct(
                    product_id=product_data["id"],
                    title=product_data["title"],
                    body_html=product_data.get("body_html", ""),
                    vendor=product_data.get("vendor", ""),
                    product_type=product_data.get("product_type", ""),
                    status=ProductStatus(product_data.get("status", "active")),
                    tags=product_data.get("tags", "").split(", ") if product_data.get("tags") else [],
                    variants=product_data.get("variants", []),
                    images=product_data.get("images", []),
                    seo_title=product_data.get("seo_title"),
                    seo_description=product_data.get("seo_description"),
                    handle=product_data.get("handle", ""),
                    created_at=datetime.fromisoformat(product_data["created_at"].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(product_data["updated_at"].replace('Z', '+00:00')),
                    metadata={
                        "options": product_data.get("options", []),
                        "template_suffix": product_data.get("template_suffix")
                    }
                )
                
                self.request_count += 1
                self._add_to_history("get_product", {"product_id": product_id}, product)
                
                logger.info(f"Product retrieved: {product.title}")
                return product
        
        except Exception as e:
            logger.error(f"Failed to get product: {e}")
            raise
    
    async def create_product(
        self,
        title: str,
        body_html: str = "",
        vendor: str = "",
        product_type: str = "",
        tags: List[str] = None,
        variants: List[Dict[str, Any]] = None,
        images: List[Dict[str, Any]] = None,
        seo_title: Optional[str] = None,
        seo_description: Optional[str] = None,
        status: ProductStatus = ProductStatus.DRAFT
    ) -> ShopifyProduct:
        """Create new product."""
        await self._ensure_session()
        
        product_data = {
            "title": title,
            "body_html": body_html,
            "vendor": vendor,
            "product_type": product_type,
            "status": status.value
        }
        
        if tags:
            product_data["tags"] = ", ".join(tags)
        
        if variants:
            product_data["variants"] = variants
        
        if images:
            product_data["images"] = images
        
        if seo_title:
            product_data["seo_title"] = seo_title
        
        if seo_description:
            product_data["seo_description"] = seo_description
        
        data = {"product": product_data}
        
        try:
            async with self.session.post(
                f"{self.base_url}/products.json",
                json=data
            ) as response:
                if response.status not in [200, 201]:
                    error_data = await response.json()
                    raise Exception(f"Shopify product creation error: {error_data}")
                
                result = await response.json()
                product_data = result["product"]
                
                product = ShopifyProduct(
                    product_id=product_data["id"],
                    title=product_data["title"],
                    body_html=product_data.get("body_html", ""),
                    vendor=product_data.get("vendor", ""),
                    product_type=product_data.get("product_type", ""),
                    status=ProductStatus(product_data.get("status", "active")),
                    tags=product_data.get("tags", "").split(", ") if product_data.get("tags") else [],
                    variants=product_data.get("variants", []),
                    images=product_data.get("images", []),
                    seo_title=product_data.get("seo_title"),
                    seo_description=product_data.get("seo_description"),
                    handle=product_data.get("handle", ""),
                    created_at=datetime.fromisoformat(product_data["created_at"].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(product_data["updated_at"].replace('Z', '+00:00')),
                    metadata={
                        "options": product_data.get("options", []),
                        "template_suffix": product_data.get("template_suffix")
                    }
                )
                
                self.request_count += 1
                self.products_managed += 1
                self._add_to_history("create_product", {"title": title}, product)
                
                logger.info(f"Product created: {product.title} (ID: {product.product_id})")
                return product
        
        except Exception as e:
            logger.error(f"Product creation failed: {e}")
            raise
    
    async def update_product(
        self,
        product_id: int,
        updates: Dict[str, Any]
    ) -> ShopifyProduct:
        """Update existing product."""
        await self._ensure_session()
        
        data = {"product": updates}
        
        try:
            async with self.session.put(
                f"{self.base_url}/products/{product_id}.json",
                json=data
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Shopify product update error: {error_data}")
                
                result = await response.json()
                product_data = result["product"]
                
                product = ShopifyProduct(
                    product_id=product_data["id"],
                    title=product_data["title"],
                    body_html=product_data.get("body_html", ""),
                    vendor=product_data.get("vendor", ""),
                    product_type=product_data.get("product_type", ""),
                    status=ProductStatus(product_data.get("status", "active")),
                    tags=product_data.get("tags", "").split(", ") if product_data.get("tags") else [],
                    variants=product_data.get("variants", []),
                    images=product_data.get("images", []),
                    seo_title=product_data.get("seo_title"),
                    seo_description=product_data.get("seo_description"),
                    handle=product_data.get("handle", ""),
                    created_at=datetime.fromisoformat(product_data["created_at"].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(product_data["updated_at"].replace('Z', '+00:00')),
                    metadata={
                        "options": product_data.get("options", []),
                        "template_suffix": product_data.get("template_suffix")
                    }
                )
                
                self.request_count += 1
                self._add_to_history("update_product", {"product_id": product_id, "updates": updates}, product)
                
                logger.info(f"Product updated: {product.title}")
                return product
        
        except Exception as e:
            logger.error(f"Product update failed: {e}")
            raise
    
    async def list_orders(
        self,
        limit: int = 50,
        status: Optional[OrderStatus] = None,
        financial_status: Optional[FinancialStatus] = None,
        fulfillment_status: Optional[FulfillmentStatus] = None,
        created_at_min: Optional[datetime] = None,
        created_at_max: Optional[datetime] = None
    ) -> List[ShopifyOrder]:
        """List orders with filters."""
        await self._ensure_session()
        
        params = {"limit": min(limit, 250)}
        
        if status:
            params["status"] = status.value
        if financial_status:
            params["financial_status"] = financial_status.value
        if fulfillment_status:
            params["fulfillment_status"] = fulfillment_status.value
        if created_at_min:
            params["created_at_min"] = created_at_min.isoformat()
        if created_at_max:
            params["created_at_max"] = created_at_max.isoformat()
        
        try:
            async with self.session.get(
                f"{self.base_url}/orders.json",
                params=params
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Shopify API error: {error_data}")
                
                result = await response.json()
                orders = []
                
                for order_data in result.get("orders", []):
                    order = ShopifyOrder(
                        order_id=order_data["id"],
                        order_number=str(order_data.get("order_number", "")),
                        email=order_data.get("email", ""),
                        financial_status=FinancialStatus(order_data.get("financial_status", "pending")),
                        fulfillment_status=FulfillmentStatus(order_data["fulfillment_status"]) if order_data.get("fulfillment_status") else None,
                        total_price=Decimal(order_data.get("total_price", "0")),
                        subtotal_price=Decimal(order_data.get("subtotal_price", "0")),
                        total_tax=Decimal(order_data.get("total_tax", "0")),
                        currency=order_data.get("currency", "USD"),
                        line_items=order_data.get("line_items", []),
                        customer=order_data.get("customer"),
                        shipping_address=order_data.get("shipping_address"),
                        billing_address=order_data.get("billing_address"),
                        created_at=datetime.fromisoformat(order_data["created_at"].replace('Z', '+00:00')),
                        updated_at=datetime.fromisoformat(order_data["updated_at"].replace('Z', '+00:00')),
                        metadata={
                            "gateway": order_data.get("gateway"),
                            "processing_method": order_data.get("processing_method"),
                            "reference": order_data.get("reference")
                        }
                    )
                    orders.append(order)
                
                self.request_count += 1
                self.orders_processed += len(orders)
                self._add_to_history("list_orders", params, {"count": len(orders)})
                
                logger.info(f"Retrieved {len(orders)} orders")
                return orders
        
        except Exception as e:
            logger.error(f"Failed to list orders: {e}")
            raise
    
    async def get_order(self, order_id: int) -> ShopifyOrder:
        """Get specific order."""
        await self._ensure_session()
        
        try:
            async with self.session.get(f"{self.base_url}/orders/{order_id}.json") as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Shopify API error: {error_data}")
                
                result = await response.json()
                order_data = result["order"]
                
                order = ShopifyOrder(
                    order_id=order_data["id"],
                    order_number=str(order_data.get("order_number", "")),
                    email=order_data.get("email", ""),
                    financial_status=FinancialStatus(order_data.get("financial_status", "pending")),
                    fulfillment_status=FulfillmentStatus(order_data["fulfillment_status"]) if order_data.get("fulfillment_status") else None,
                    total_price=Decimal(order_data.get("total_price", "0")),
                    subtotal_price=Decimal(order_data.get("subtotal_price", "0")),
                    total_tax=Decimal(order_data.get("total_tax", "0")),
                    currency=order_data.get("currency", "USD"),
                    line_items=order_data.get("line_items", []),
                    customer=order_data.get("customer"),
                    shipping_address=order_data.get("shipping_address"),
                    billing_address=order_data.get("billing_address"),
                    created_at=datetime.fromisoformat(order_data["created_at"].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(order_data["updated_at"].replace('Z', '+00:00')),
                    metadata={
                        "gateway": order_data.get("gateway"),
                        "processing_method": order_data.get("processing_method"),
                        "reference": order_data.get("reference")
                    }
                )
                
                self.request_count += 1
                self._add_to_history("get_order", {"order_id": order_id}, order)
                
                logger.info(f"Order retrieved: {order.order_number}")
                return order
        
        except Exception as e:
            logger.error(f"Failed to get order: {e}")
            raise
    
    async def list_customers(
        self,
        limit: int = 50,
        created_at_min: Optional[datetime] = None,
        created_at_max: Optional[datetime] = None,
        updated_at_min: Optional[datetime] = None,
        updated_at_max: Optional[datetime] = None
    ) -> List[ShopifyCustomer]:
        """List customers with filters."""
        await self._ensure_session()
        
        params = {"limit": min(limit, 250)}
        
        if created_at_min:
            params["created_at_min"] = created_at_min.isoformat()
        if created_at_max:
            params["created_at_max"] = created_at_max.isoformat()
        if updated_at_min:
            params["updated_at_min"] = updated_at_min.isoformat()
        if updated_at_max:
            params["updated_at_max"] = updated_at_max.isoformat()
        
        try:
            async with self.session.get(
                f"{self.base_url}/customers.json",
                params=params
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Shopify API error: {error_data}")
                
                result = await response.json()
                customers = []
                
                for customer_data in result.get("customers", []):
                    customer = ShopifyCustomer(
                        customer_id=customer_data["id"],
                        first_name=customer_data.get("first_name", ""),
                        last_name=customer_data.get("last_name", ""),
                        email=customer_data.get("email", ""),
                        phone=customer_data.get("phone"),
                        verified_email=customer_data.get("verified_email", False),
                        total_spent=Decimal(customer_data.get("total_spent", "0")),
                        orders_count=customer_data.get("orders_count", 0),
                        state=customer_data.get("state", "disabled"),
                        tags=customer_data.get("tags", "").split(", ") if customer_data.get("tags") else [],
                        addresses=customer_data.get("addresses", []),
                        created_at=datetime.fromisoformat(customer_data["created_at"].replace('Z', '+00:00')),
                        updated_at=datetime.fromisoformat(customer_data["updated_at"].replace('Z', '+00:00')),
                        metadata={
                            "note": customer_data.get("note"),
                            "tax_exempt": customer_data.get("tax_exempt"),
                            "accepts_marketing": customer_data.get("accepts_marketing")
                        }
                    )
                    customers.append(customer)
                
                self.request_count += 1
                self._add_to_history("list_customers", params, {"count": len(customers)})
                
                logger.info(f"Retrieved {len(customers)} customers")
                return customers
        
        except Exception as e:
            logger.error(f"Failed to list customers: {e}")
            raise
    
    def verify_webhook_signature(
        self,
        payload: bytes,
        signature_header: str
    ) -> bool:
        """Verify Shopify webhook signature."""
        if not self.webhook_secret:
            logger.warning("Webhook secret not configured")
            return False
        
        try:
            expected_signature = base64.b64encode(
                hmac.new(
                    self.webhook_secret.encode('utf-8'),
                    payload,
                    hashlib.sha256
                ).digest()
            ).decode('utf-8')
            
            return hmac.compare_digest(expected_signature, signature_header)
        
        except Exception as e:
            logger.error(f"Webhook signature verification failed: {e}")
            return False
    
    async def handle_webhook_event(self, event_data: Dict[str, Any], topic: str) -> Dict[str, Any]:
        """Handle incoming webhook event."""
        logger.info(f"Processing webhook event: {topic}")
        
        handlers = {
            "orders/create": self._handle_order_created,
            "orders/updated": self._handle_order_updated,
            "orders/paid": self._handle_order_paid,
            "orders/cancelled": self._handle_order_cancelled,
            "products/create": self._handle_product_created,
            "products/update": self._handle_product_updated,
            "customers/create": self._handle_customer_created,
            "app/uninstalled": self._handle_app_uninstalled
        }
        
        handler = handlers.get(topic)
        if handler:
            return await handler(event_data)
        else:
            logger.info(f"No handler for webhook topic: {topic}")
            return {"status": "ignored"}
    
    async def _handle_order_created(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle order created event."""
        order_id = order_data.get("id")
        logger.info(f"Order created: {order_id}")
        return {"status": "processed", "order_id": order_id}
    
    async def _handle_order_updated(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle order updated event."""
        order_id = order_data.get("id")
        logger.info(f"Order updated: {order_id}")
        return {"status": "processed", "order_id": order_id}
    
    async def _handle_order_paid(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle order paid event."""
        order_id = order_data.get("id")
        total_price = order_data.get("total_price")
        logger.info(f"Order paid: {order_id}, amount: {total_price}")
        return {"status": "processed", "order_id": order_id}
    
    async def _handle_order_cancelled(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle order cancelled event."""
        order_id = order_data.get("id")
        logger.info(f"Order cancelled: {order_id}")
        return {"status": "processed", "order_id": order_id}
    
    async def _handle_product_created(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle product created event."""
        product_id = product_data.get("id")
        title = product_data.get("title")
        logger.info(f"Product created: {product_id}, title: {title}")
        return {"status": "processed", "product_id": product_id}
    
    async def _handle_product_updated(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle product updated event."""
        product_id = product_data.get("id")
        title = product_data.get("title")
        logger.info(f"Product updated: {product_id}, title: {title}")
        return {"status": "processed", "product_id": product_id}
    
    async def _handle_customer_created(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle customer created event."""
        customer_id = customer_data.get("id")
        email = customer_data.get("email")
        logger.info(f"Customer created: {customer_id}, email: {email}")
        return {"status": "processed", "customer_id": customer_id}
    
    async def _handle_app_uninstalled(self, app_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle app uninstalled event."""
        logger.info("App uninstalled")
        return {"status": "processed", "action": "cleanup"}
    
    def _add_to_history(
        self,
        operation: str,
        request_data: Dict[str, Any],
        response_data: Any
    ):
        """Add operation to history."""
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "request": request_data,
            "response_summary": self._summarize_response(response_data)
        }
        
        self.api_call_history.append(history_entry)
        
        # Keep only last 100 entries
        if len(self.api_call_history) > 100:
            self.api_call_history = self.api_call_history[-100:]
    
    def _summarize_response(self, response_data: Any) -> Dict[str, Any]:
        """Create summary of response data."""
        if isinstance(response_data, (ShopifyProduct, ShopifyOrder, ShopifyCustomer)):
            return {
                "type": type(response_data).__name__,
                "id": getattr(response_data, f"{type(response_data).__name__.lower().replace('shopify', '')}_id")
            }
        elif isinstance(response_data, dict):
            return {
                "type": "dict",
                "keys": list(response_data.keys())
            }
        else:
            return {"type": "unknown"}
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            "total_requests": self.request_count,
            "products_managed": self.products_managed,
            "orders_processed": self.orders_processed,
            "recent_operations": len(self.api_call_history),
            "operations_by_type": self._get_operations_breakdown()
        }
    
    def _get_operations_breakdown(self) -> Dict[str, int]:
        """Get breakdown of operations by type."""
        breakdown = {}
        for entry in self.api_call_history:
            operation = entry["operation"]
            breakdown[operation] = breakdown.get(operation, 0) + 1
        return breakdown


# Utility functions
async def create_shopify_integration(
    shop_domain: str,
    access_token: str,
    webhook_secret: Optional[str] = None
) -> ShopifyIntegration:
    """Create and initialize Shopify integration."""
    integration = ShopifyIntegration(
        shop_domain=shop_domain,
        access_token=access_token,
        webhook_secret=webhook_secret
    )
    await integration._ensure_session()
    return integration


async def quick_product_creation(
    title: str,
    price: Decimal,
    inventory_quantity: int,
    shop_domain: str,
    access_token: str
) -> ShopifyProduct:
    """Quick product creation utility."""
    variants = [{
        "price": str(price),
        "inventory_quantity": inventory_quantity,
        "inventory_management": "shopify"
    }]
    
    async with ShopifyIntegration(shop_domain, access_token) as shopify:
        return await shopify.create_product(
            title=title,
            variants=variants,
            status=ProductStatus.DRAFT
        )


if __name__ == "__main__":
    # Example usage
    async def main():
        import os
        shop_domain = os.getenv("SHOPIFY_SHOP_DOMAIN")
        access_token = os.getenv("SHOPIFY_ACCESS_TOKEN")
        
        if not all([shop_domain, access_token]):
            print("Please set SHOPIFY_SHOP_DOMAIN and SHOPIFY_ACCESS_TOKEN")
            return
        
        async with ShopifyIntegration(shop_domain, access_token) as shopify:
            # Test get shop info
            shop_info = await shopify.get_shop_info()
            print(f"Shop: {shop_info.get('name')}")
            
            # Test list products
            products = await shopify.list_products(limit=5)
            print(f"Products: {len(products)}")
            
            # Test usage stats
            stats = shopify.get_usage_stats()
            print(f"Usage stats: {stats}")
    
    asyncio.run(main())