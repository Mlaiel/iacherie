"""
Monetization API Routes
Revenue tracking and monetization management endpoints.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
import asyncio

from ...core.database import database_manager
from ...core.security import security_manager
from ...core.cache import cache_manager
from ...core.logging import logger
from ...monetization.revenue_calculator import RevenueCalculator
from ...monetization.platform_apis import PlatformAPIsManager
from ...monetization.payment_processor import PaymentProcessor
from ...monetization.licensing_manager import LicensingManager


# Pydantic models
class PlatformConnection(BaseModel):
    platform: str = Field(..., regex="^(youtube|spotify|instagram|tiktok|facebook|twitter|patreon|onlyfans)$")
    api_key: Optional[str] = None
    access_token: Optional[str] = None
    channel_id: Optional[str] = None
    account_id: Optional[str] = None
    connection_settings: Optional[Dict[str, Any]] = None


class RevenueStream(BaseModel):
    stream_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    platform: str
    content_id: str
    revenue_type: str = Field(..., regex="^(ad_revenue|subscriptions|donations|sponsorships|licensing|merchandise)$")
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="USD", regex="^[A-Z]{3}$")
    date_earned: datetime
    payment_status: str = Field(default="pending", regex="^(pending|processing|paid|failed)$")
    metadata: Optional[Dict[str, Any]] = None


class RevenueReport(BaseModel):
    report_id: str
    user_id: str
    report_type: str
    period_start: datetime
    period_end: datetime
    total_revenue: Decimal
    revenue_by_platform: Dict[str, Decimal]
    revenue_by_type: Dict[str, Decimal]
    growth_metrics: Dict[str, float]
    top_performing_content: List[Dict[str, Any]]
    payment_summary: Dict[str, Any]
    generated_at: datetime


class MonetizationGoal(BaseModel):
    goal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., min_length=1, max_length=100)
    target_amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="USD")
    target_date: datetime
    platforms: List[str]
    revenue_types: List[str]
    status: str = Field(default="active", regex="^(active|paused|completed|cancelled)$")


class PayoutRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="USD")
    payment_method: str = Field(..., regex="^(bank_transfer|paypal|stripe|wise|crypto)$")
    payment_details: Dict[str, str]
    priority: str = Field(default="normal", regex="^(low|normal|high|urgent)$")


class LicensingDeal(BaseModel):
    deal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    licensee_name: str
    license_type: str = Field(..., regex="^(exclusive|non_exclusive|sync|master|mechanical)$")
    territory: str = Field(default="worldwide")
    duration_months: int = Field(..., gt=0, le=120)
    total_amount: Decimal = Field(..., gt=0)
    advance_amount: Decimal = Field(default=0)
    royalty_rate: float = Field(..., ge=0, le=100)
    payment_schedule: List[Dict[str, Any]]
    terms_conditions: str


class RevenueAnalytics(BaseModel):
    period: str
    total_revenue: Decimal
    revenue_change: float
    platform_breakdown: Dict[str, Decimal]
    top_earners: List[Dict[str, Any]]
    predictions: Dict[str, float]
    optimization_suggestions: List[str]


# Router setup
router = APIRouter()
security = HTTPBearer(auto_error=False)

# Initialize monetization components
revenue_calculator = RevenueCalculator()
platform_apis = PlatformAPIsManager()
payment_processor = PaymentProcessor()
licensing_manager = LicensingManager()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        user_data = await security_manager.verify_token(credentials.credentials)
        return user_data
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )


@router.post("/platforms/connect", response_model=Dict[str, str])
async def connect_platform(
    connection: PlatformConnection,
    user: dict = Depends(get_current_user)
):
    """Connect a monetization platform"""
    try:
        # Validate platform connection
        validation_result = await platform_apis.validate_connection(
            connection.platform, connection.api_key, connection.access_token
        )
        
        if not validation_result['valid']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Platform connection validation failed: {validation_result['error']}"
            )
        
        connection_id = str(uuid.uuid4())
        
        # Store encrypted connection details
        encrypted_credentials = await security_manager.encrypt_credentials({
            'api_key': connection.api_key,
            'access_token': connection.access_token,
            'channel_id': connection.channel_id,
            'account_id': connection.account_id
        })
        
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                INSERT INTO platform_connections (connection_id, user_id, platform, 
                                                encrypted_credentials, connection_settings,
                                                status, created_at, last_validated)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id, platform) DO UPDATE SET
                    encrypted_credentials = EXCLUDED.encrypted_credentials,
                    connection_settings = EXCLUDED.connection_settings,
                    last_validated = EXCLUDED.last_validated,
                    status = 'active'
            """, (
                connection_id, user['user_id'], connection.platform,
                encrypted_credentials, connection.connection_settings,
                'active', datetime.utcnow(), datetime.utcnow()
            ))
            await session.commit()
        
        # Start revenue sync for this platform
        asyncio.create_task(_sync_platform_revenue(user['user_id'], connection.platform))
        
        logger.info(f"Platform connected: {connection.platform} for user {user['user_id']}")
        
        return {
            "connection_id": connection_id,
            "platform": connection.platform,
            "status": "connected",
            "message": "Platform connected successfully"
        }
        
    except Exception as e:
        logger.error(f"Platform connection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to connect platform"
        )


@router.get("/revenue/summary", response_model=RevenueAnalytics)
async def get_revenue_summary(
    period: str = Field(default="30d", regex="^(7d|30d|90d|1y|all)$"),
    user: dict = Depends(get_current_user)
):
    """Get revenue summary and analytics"""
    try:
        # Calculate period dates
        if period == "7d":
            start_date = datetime.utcnow() - timedelta(days=7)
        elif period == "30d":
            start_date = datetime.utcnow() - timedelta(days=30)
        elif period == "90d":
            start_date = datetime.utcnow() - timedelta(days=90)
        elif period == "1y":
            start_date = datetime.utcnow() - timedelta(days=365)
        else:
            start_date = datetime.min
        
        end_date = datetime.utcnow()
        
        # Get total revenue
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""
                SELECT COALESCE(SUM(amount_usd), 0) as total_revenue
                FROM revenue_streams
                WHERE user_id = %s AND date_earned >= %s AND date_earned <= %s
            """, (user['user_id'], start_date, end_date))
            total_revenue = result.fetchone()[0]
            
            # Get previous period for comparison
            prev_start = start_date - (end_date - start_date)
            result = await session.execute("""
                SELECT COALESCE(SUM(amount_usd), 0) as prev_revenue
                FROM revenue_streams
                WHERE user_id = %s AND date_earned >= %s AND date_earned < %s
            """, (user['user_id'], prev_start, start_date))
            prev_revenue = result.fetchone()[0]
            
            # Calculate revenue change
            revenue_change = 0.0
            if prev_revenue > 0:
                revenue_change = ((total_revenue - prev_revenue) / prev_revenue) * 100
            
            # Get platform breakdown
            result = await session.execute("""
                SELECT platform, COALESCE(SUM(amount_usd), 0) as platform_revenue
                FROM revenue_streams
                WHERE user_id = %s AND date_earned >= %s AND date_earned <= %s
                GROUP BY platform
                ORDER BY platform_revenue DESC
            """, (user['user_id'], start_date, end_date))
            platform_breakdown = {row[0]: row[1] for row in result.fetchall()}
            
            # Get top earning content
            result = await session.execute("""
                SELECT content_id, content_title, COALESCE(SUM(amount_usd), 0) as content_revenue
                FROM revenue_streams
                WHERE user_id = %s AND date_earned >= %s AND date_earned <= %s
                GROUP BY content_id, content_title
                ORDER BY content_revenue DESC
                LIMIT 10
            """, (user['user_id'], start_date, end_date))
            top_earners = [
                {
                    "content_id": row[0],
                    "title": row[1],
                    "revenue": float(row[2])
                }
                for row in result.fetchall()
            ]
        
        # Generate revenue predictions using ML
        predictions = await revenue_calculator.predict_future_revenue(
            user['user_id'], period
        )
        
        # Get optimization suggestions
        optimization_suggestions = await revenue_calculator.get_optimization_suggestions(
            user['user_id'], platform_breakdown, top_earners
        )
        
        analytics = RevenueAnalytics(
            period=period,
            total_revenue=Decimal(str(total_revenue)),
            revenue_change=revenue_change,
            platform_breakdown={k: Decimal(str(v)) for k, v in platform_breakdown.items()},
            top_earners=top_earners,
            predictions=predictions,
            optimization_suggestions=optimization_suggestions
        )
        
        return analytics
        
    except Exception as e:
        logger.error(f"Get revenue summary failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get revenue summary"
        )


@router.post("/revenue/streams", response_model=Dict[str, str])
async def add_revenue_stream(
    stream: RevenueStream,
    user: dict = Depends(get_current_user)
):
    """Add a manual revenue stream entry"""
    try:
        # Convert amount to USD for analytics
        amount_usd = await revenue_calculator.convert_to_usd(stream.amount, stream.currency)
        
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                INSERT INTO revenue_streams (stream_id, user_id, platform, content_id,
                                           revenue_type, amount, currency, amount_usd,
                                           date_earned, payment_status, metadata, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                stream.stream_id, user['user_id'], stream.platform, stream.content_id,
                stream.revenue_type, stream.amount, stream.currency, amount_usd,
                stream.date_earned, stream.payment_status, stream.metadata, datetime.utcnow()
            ))
            await session.commit()
        
        # Update revenue goals progress
        await _update_goals_progress(user['user_id'], stream.platform, stream.revenue_type, amount_usd)
        
        logger.info(f"Revenue stream added: {stream.stream_id} for user {user['user_id']}")
        
        return {
            "stream_id": stream.stream_id,
            "message": "Revenue stream added successfully",
            "amount_usd": str(amount_usd)
        }
        
    except Exception as e:
        logger.error(f"Add revenue stream failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add revenue stream"
        )


@router.post("/goals", response_model=Dict[str, str])
async def create_monetization_goal(
    goal: MonetizationGoal,
    user: dict = Depends(get_current_user)
):
    """Create a new monetization goal"""
    try:
        # Convert target amount to USD
        target_amount_usd = await revenue_calculator.convert_to_usd(goal.target_amount, goal.currency)
        
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                INSERT INTO monetization_goals (goal_id, user_id, title, target_amount,
                                              currency, target_amount_usd, target_date,
                                              platforms, revenue_types, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                goal.goal_id, user['user_id'], goal.title, goal.target_amount,
                goal.currency, target_amount_usd, goal.target_date,
                goal.platforms, goal.revenue_types, goal.status, datetime.utcnow()
            ))
            await session.commit()
        
        logger.info(f"Monetization goal created: {goal.goal_id} for user {user['user_id']}")
        
        return {
            "goal_id": goal.goal_id,
            "message": "Monetization goal created successfully"
        }
        
    except Exception as e:
        logger.error(f"Create monetization goal failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create monetization goal"
        )


@router.get("/goals", response_model=List[Dict[str, Any]])
async def get_monetization_goals(
    status: Optional[str] = None,
    user: dict = Depends(get_current_user)
):
    """Get user's monetization goals with progress"""
    try:
        query = """
            SELECT goal_id, title, target_amount, currency, target_amount_usd,
                   target_date, platforms, revenue_types, status, created_at
            FROM monetization_goals
            WHERE user_id = %s
        """
        params = [user['user_id']]
        
        if status:
            query += " AND status = %s"
            params.append(status)
            
        query += " ORDER BY created_at DESC"
        
        async with database_manager.get_postgres_session() as session:
            result = await session.execute(query, params)
            goals = result.fetchall()
        
        goals_with_progress = []
        for goal in goals:
            # Calculate current progress
            progress = await _calculate_goal_progress(
                user['user_id'], goal[0], goal[6], goal[7], goal[9]  # platforms, revenue_types, created_at
            )
            
            goals_with_progress.append({
                "goal_id": goal[0],
                "title": goal[1],
                "target_amount": float(goal[2]),
                "currency": goal[3],
                "target_amount_usd": float(goal[4]),
                "target_date": goal[5],
                "platforms": goal[6],
                "revenue_types": goal[7],
                "status": goal[8],
                "created_at": goal[9],
                "current_progress": progress,
                "completion_percentage": (progress / float(goal[4])) * 100 if goal[4] > 0 else 0
            })
        
        return goals_with_progress
        
    except Exception as e:
        logger.error(f"Get monetization goals failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get monetization goals"
        )


@router.post("/payouts", response_model=Dict[str, str])
async def request_payout(
    payout_request: PayoutRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Request a payout of earned revenue"""
    try:
        # Check available balance
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""
                SELECT COALESCE(SUM(amount_usd), 0) as available_balance
                FROM revenue_streams
                WHERE user_id = %s AND payment_status = 'paid' AND payout_status = 'available'
            """, (user['user_id'],))
            available_balance = result.fetchone()[0]
        
        # Convert requested amount to USD
        requested_amount_usd = await revenue_calculator.convert_to_usd(
            payout_request.amount, payout_request.currency
        )
        
        if requested_amount_usd > available_balance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient balance. Available: ${available_balance}, Requested: ${requested_amount_usd}"
            )
        
        payout_id = str(uuid.uuid4())
        
        # Create payout request
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                INSERT INTO payout_requests (payout_id, user_id, amount, currency,
                                           amount_usd, payment_method, payment_details,
                                           priority, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                payout_id, user['user_id'], payout_request.amount, payout_request.currency,
                requested_amount_usd, payout_request.payment_method, payout_request.payment_details,
                payout_request.priority, "pending", datetime.utcnow()
            ))
            await session.commit()
        
        # Schedule payout processing
        background_tasks.add_task(_process_payout, payout_id, payout_request, user)
        
        logger.info(f"Payout requested: {payout_id} for user {user['user_id']}")
        
        return {
            "payout_id": payout_id,
            "amount": str(payout_request.amount),
            "currency": payout_request.currency,
            "status": "pending",
            "message": "Payout request submitted successfully"
        }
        
    except Exception as e:
        logger.error(f"Request payout failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to request payout"
        )


@router.post("/licensing/deals", response_model=Dict[str, str])
async def create_licensing_deal(
    deal: LicensingDeal,
    user: dict = Depends(get_current_user)
):
    """Create a new licensing deal"""
    try:
        # Verify content ownership
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""
                SELECT content_id FROM user_content
                WHERE content_id = %s AND user_id = %s
            """, (deal.content_id, user['user_id']))
            
            if not result.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Content not found or access denied"
                )
        
        # Convert amounts to USD
        total_amount_usd = await revenue_calculator.convert_to_usd(deal.total_amount, "USD")
        advance_amount_usd = await revenue_calculator.convert_to_usd(deal.advance_amount, "USD")
        
        # Create licensing deal
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                INSERT INTO licensing_deals (deal_id, user_id, content_id, licensee_name,
                                           license_type, territory, duration_months,
                                           total_amount, advance_amount, total_amount_usd,
                                           advance_amount_usd, royalty_rate, payment_schedule,
                                           terms_conditions, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                deal.deal_id, user['user_id'], deal.content_id, deal.licensee_name,
                deal.license_type, deal.territory, deal.duration_months,
                deal.total_amount, deal.advance_amount, total_amount_usd,
                advance_amount_usd, deal.royalty_rate, deal.payment_schedule,
                deal.terms_conditions, "active", datetime.utcnow()
            ))
            await session.commit()
        
        # Generate licensing contract
        contract = await licensing_manager.generate_contract(deal, user)
        
        logger.info(f"Licensing deal created: {deal.deal_id} for user {user['user_id']}")
        
        return {
            "deal_id": deal.deal_id,
            "contract_url": contract['url'],
            "message": "Licensing deal created successfully"
        }
        
    except Exception as e:
        logger.error(f"Create licensing deal failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create licensing deal"
        )


@router.get("/reports/detailed", response_model=RevenueReport)
async def generate_revenue_report(
    start_date: datetime,
    end_date: datetime,
    report_type: str = Field(default="comprehensive", regex="^(summary|detailed|comprehensive|tax)$"),
    user: dict = Depends(get_current_user)
):
    """Generate detailed revenue report"""
    try:
        report_id = str(uuid.uuid4())
        
        # Get comprehensive revenue data
        async with database_manager.get_postgres_session() as session:
            # Total revenue
            result = await session.execute("""
                SELECT COALESCE(SUM(amount_usd), 0) as total_revenue
                FROM revenue_streams
                WHERE user_id = %s AND date_earned >= %s AND date_earned <= %s
            """, (user['user_id'], start_date, end_date))
            total_revenue = result.fetchone()[0]
            
            # Revenue by platform
            result = await session.execute("""
                SELECT platform, COALESCE(SUM(amount_usd), 0) as platform_revenue
                FROM revenue_streams
                WHERE user_id = %s AND date_earned >= %s AND date_earned <= %s
                GROUP BY platform
            """, (user['user_id'], start_date, end_date))
            revenue_by_platform = {row[0]: row[1] for row in result.fetchall()}
            
            # Revenue by type
            result = await session.execute("""
                SELECT revenue_type, COALESCE(SUM(amount_usd), 0) as type_revenue
                FROM revenue_streams
                WHERE user_id = %s AND date_earned >= %s AND date_earned <= %s
                GROUP BY revenue_type
            """, (user['user_id'], start_date, end_date))
            revenue_by_type = {row[0]: row[1] for row in result.fetchall()}
            
            # Top performing content
            result = await session.execute("""
                SELECT content_id, content_title, platform, COALESCE(SUM(amount_usd), 0) as content_revenue
                FROM revenue_streams
                WHERE user_id = %s AND date_earned >= %s AND date_earned <= %s
                GROUP BY content_id, content_title, platform
                ORDER BY content_revenue DESC
                LIMIT 20
            """, (user['user_id'], start_date, end_date))
            top_performing_content = [
                {
                    "content_id": row[0],
                    "title": row[1],
                    "platform": row[2],
                    "revenue": float(row[3])
                }
                for row in result.fetchall()
            ]
            
            # Payment summary
            result = await session.execute("""
                SELECT payment_status, COUNT(*) as count, COALESCE(SUM(amount_usd), 0) as total
                FROM revenue_streams
                WHERE user_id = %s AND date_earned >= %s AND date_earned <= %s
                GROUP BY payment_status
            """, (user['user_id'], start_date, end_date))
            payment_summary = {
                row[0]: {"count": row[1], "total": float(row[2])}
                for row in result.fetchall()
            }
        
        # Calculate growth metrics
        growth_metrics = await revenue_calculator.calculate_growth_metrics(
            user['user_id'], start_date, end_date
        )
        
        report = RevenueReport(
            report_id=report_id,
            user_id=user['user_id'],
            report_type=report_type,
            period_start=start_date,
            period_end=end_date,
            total_revenue=Decimal(str(total_revenue)),
            revenue_by_platform={k: Decimal(str(v)) for k, v in revenue_by_platform.items()},
            revenue_by_type={k: Decimal(str(v)) for k, v in revenue_by_type.items()},
            growth_metrics=growth_metrics,
            top_performing_content=top_performing_content,
            payment_summary=payment_summary,
            generated_at=datetime.utcnow()
        )
        
        # Store report for future reference
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                INSERT INTO revenue_reports (report_id, user_id, report_type, report_data,
                                           period_start, period_end, generated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                report_id, user['user_id'], report_type, report.dict(),
                start_date, end_date, datetime.utcnow()
            ))
            await session.commit()
        
        logger.info(f"Revenue report generated: {report_id} for user {user['user_id']}")
        
        return report
        
    except Exception as e:
        logger.error(f"Generate revenue report failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate revenue report"
        )


# Background task functions
async def _sync_platform_revenue(user_id: str, platform: str):
    """Sync revenue data from platform APIs"""
    try:
        # Get platform connection
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""
                SELECT encrypted_credentials FROM platform_connections
                WHERE user_id = %s AND platform = %s AND status = 'active'
            """, (user_id, platform))
            
            connection = result.fetchone()
            if not connection:
                return
        
        # Decrypt credentials
        credentials = await security_manager.decrypt_credentials(connection[0])
        
        # Fetch revenue data from platform
        revenue_data = await platform_apis.fetch_revenue_data(platform, credentials)
        
        # Store revenue streams
        async with database_manager.get_postgres_session() as session:
            for stream in revenue_data:
                stream_id = str(uuid.uuid4())
                amount_usd = await revenue_calculator.convert_to_usd(
                    stream['amount'], stream['currency']
                )
                
                await session.execute("""
                    INSERT INTO revenue_streams (stream_id, user_id, platform, content_id,
                                               revenue_type, amount, currency, amount_usd,
                                               date_earned, payment_status, metadata, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id, platform, content_id, date_earned) DO NOTHING
                """, (
                    stream_id, user_id, platform, stream['content_id'],
                    stream['revenue_type'], stream['amount'], stream['currency'], amount_usd,
                    stream['date_earned'], stream['payment_status'], stream.get('metadata', {}),
                    datetime.utcnow()
                ))
            await session.commit()
        
        logger.info(f"Revenue synced for platform {platform}, user {user_id}: {len(revenue_data)} streams")
        
    except Exception as e:
        logger.error(f"Revenue sync failed for platform {platform}, user {user_id}: {e}")


async def _process_payout(payout_id: str, payout_request: PayoutRequest, user: dict):
    """Process payout request"""
    try:
        # Update status to processing
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                UPDATE payout_requests 
                SET status = 'processing', started_at = %s
                WHERE payout_id = %s
            """, (datetime.utcnow(), payout_id))
            await session.commit()
        
        # Process payment through payment processor
        payment_result = await payment_processor.process_payout(
            payout_request, user
        )
        
        # Update payout status
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                UPDATE payout_requests 
                SET status = %s, transaction_id = %s, completed_at = %s
                WHERE payout_id = %s
            """, (
                payment_result['status'], payment_result.get('transaction_id'),
                datetime.utcnow(), payout_id
            ))
            
            # Mark revenue streams as paid out
            if payment_result['status'] == 'completed':
                await session.execute("""
                    UPDATE revenue_streams 
                    SET payout_status = 'paid_out', payout_id = %s
                    WHERE user_id = %s AND payout_status = 'available'
                      AND amount_usd <= %s
                """, (payout_id, user['user_id'], payout_request.amount))
            
            await session.commit()
        
        logger.info(f"Payout processed: {payout_id}, status: {payment_result['status']}")
        
    except Exception as e:
        logger.error(f"Payout processing failed: {e}")
        
        # Mark as failed
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                UPDATE payout_requests 
                SET status = 'failed', error_message = %s
                WHERE payout_id = %s
            """, (str(e), payout_id))
            await session.commit()


async def _update_goals_progress(user_id: str, platform: str, revenue_type: str, amount_usd: float):
    """Update progress towards monetization goals"""
    try:
        async with database_manager.get_postgres_session() as session:
            # Find matching goals
            result = await session.execute("""
                SELECT goal_id FROM monetization_goals
                WHERE user_id = %s AND status = 'active'
                  AND (%s = ANY(platforms) OR 'all' = ANY(platforms))
                  AND (%s = ANY(revenue_types) OR 'all' = ANY(revenue_types))
            """, (user_id, platform, revenue_type))
            
            matching_goals = [row[0] for row in result.fetchall()]
            
            # Update goal progress
            for goal_id in matching_goals:
                await session.execute("""
                    UPDATE monetization_goals 
                    SET current_progress = current_progress + %s,
                        last_updated = %s
                    WHERE goal_id = %s
                """, (amount_usd, datetime.utcnow(), goal_id))
            
            await session.commit()
        
        logger.debug(f"Updated {len(matching_goals)} goal(s) progress for user {user_id}")
        
    except Exception as e:
        logger.error(f"Update goals progress failed: {e}")


async def _calculate_goal_progress(user_id: str, goal_id: str, platforms: List[str], 
                                  revenue_types: List[str], created_at: datetime) -> float:
    """Calculate current progress towards a goal"""
    try:
        async with database_manager.get_postgres_session() as session:
            # Build dynamic query based on goal criteria
            platform_filter = "platform = ANY(%s)" if 'all' not in platforms else "TRUE"
            revenue_type_filter = "revenue_type = ANY(%s)" if 'all' not in revenue_types else "TRUE"
            
            query = f"""
                SELECT COALESCE(SUM(amount_usd), 0) as progress
                FROM revenue_streams
                WHERE user_id = %s AND date_earned >= %s
                  AND {platform_filter} AND {revenue_type_filter}
            """
            
            params = [user_id, created_at]
            if 'all' not in platforms:
                params.append(platforms)
            if 'all' not in revenue_types:
                params.append(revenue_types)
            
            result = await session.execute(query, params)
            progress = result.fetchone()[0]
        
        return float(progress)
        
    except Exception as e:
        logger.error(f"Calculate goal progress failed: {e}")
        return 0.0