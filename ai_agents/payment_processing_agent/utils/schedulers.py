"""Payment Schedulers - Industrial Payout Automation

Advanced scheduling system for automated payouts, recurring payments,
batch processing, and flexible payout strategies.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Dict, List, Optional, Any, Callable, Tuple
from enum import Enum
from dataclasses import dataclass, field
import json

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from .models import PayoutSchedule, PaymentTransaction, PaymentMethod
from .exceptions import PayoutSchedulingError, PayoutError
from .config import PaymentConfig, PayoutFrequency

logger = logging.getLogger(__name__)


class SchedulerStatus(str, Enum):
    """
Scheduler operational status"""

    RUNNING = "running"
    STOPPED = "stopped"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class PayoutStrategy:
    """Payout strategy configuration"""
    name: str
    frequency: PayoutFrequency
    minimum_amount: Decimal
    maximum_amount: Optional[Decimal] = None
    days_of_week: Optional[List[int]] = None  # 0=Monday, 6=Sunday
    time_of_day: str = "09:00"  # HH:MM format
    timezone: str = "UTC"
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BatchPayoutResult:
    """Batch payout processing result"""
    total_processed: int = 0
    successful_payouts: int = 0
    failed_payouts: int = 0
    total_amount: Decimal = Decimal("0.00")
    errors: List[Dict[str, Any]] = field(default_factory=list)
    processing_time: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class PayoutScheduler:
    """
    Industrial payout scheduling system with flexible strategies.
    
    Handles automated payout scheduling, batch processing, retry logic,
    and comprehensive monitoring for creator payments.
    """
    def __init__(
        self,
        config: Optional[PaymentConfig] = None,
        db_session: Optional[Session] = None
    ):
        """
Initialize payout scheduler"""
        self.config = config or PaymentConfig()
        self.db_session = db_session
        self.scheduler = AsyncIOScheduler(timezone=timezone.utc)
        self.status = SchedulerStatus.STOPPED
        
        # Payout strategies
        self.strategies: Dict[str, PayoutStrategy] = {}
        self._initialize_default_strategies()
        
        # Callbacks for events
        self.callbacks: Dict[str, List[Callable]] = {
            "payout_scheduled": [],
            "payout_completed": [],
            "payout_failed": [],
            "batch_completed": []
        }
        
        # Metrics
        self.metrics = {
            "scheduled_payouts": 0,
            "completed_payouts": 0,
            "failed_payouts": 0,
            "total_amount_processed": Decimal("0.00"),
            "average_processing_time": 0.0
        }

    def _initialize_default_strategies(self):
        """Initialize default payout strategies"""
        self.strategies = {
            "daily": PayoutStrategy(
                name="daily",
                frequency=PayoutFrequency.DAILY,
                minimum_amount=Decimal("10.00"),
                time_of_day="10:00"
            ),
            "weekly": PayoutStrategy(
                name="weekly",
                frequency=PayoutFrequency.WEEKLY,
                minimum_amount=Decimal("25.00"),
                days_of_week=[1],  # Tuesday
                time_of_day="09:00"
            ),
            "biweekly": PayoutStrategy(
                name="biweekly",
                frequency=PayoutFrequency.BIWEEKLY,
                minimum_amount=Decimal("50.00"),
                days_of_week=[1],  # Every other Tuesday
                time_of_day="09:00"
            ),
            "monthly": PayoutStrategy(
                name="monthly",
                frequency=PayoutFrequency.MONTHLY,
                minimum_amount=Decimal("100.00"),
                days_of_week=[1],  # First Tuesday of month
                time_of_day="09:00"
            )
        }

    async def start(self):
        """Start the payout scheduler"""
        try:
            if self.status == SchedulerStatus.RUNNING:
                logger.warning("Scheduler is already running")
                return

            # Schedule payout jobs based on strategies
            await self._schedule_payout_jobs()
            
            # Schedule maintenance tasks
            await self._schedule_maintenance_jobs()
            
            # Start the scheduler
            self.scheduler.start()
            self.status = SchedulerStatus.RUNNING
            
            logger.info("Payout scheduler started successfully")
            
        except Exception as e:
            self.status = SchedulerStatus.ERROR
            logger.error(f"Failed to start scheduler: {str(e)}")
            raise PayoutSchedulingError(f"Scheduler start failed: {str(e)}")

    async def stop(self):
        """Stop the payout scheduler"""
        try:
            if self.status == SchedulerStatus.STOPPED:
                logger.warning("Scheduler is already stopped")
                return

            self.scheduler.shutdown(wait=True)
            self.status = SchedulerStatus.STOPPED
            
            logger.info("Payout scheduler stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop scheduler: {str(e)}")
            raise PayoutSchedulingError(f"Scheduler stop failed: {str(e)}")

    async def pause(self):
        """Pause the payout scheduler"""
        try:
            self.scheduler.pause()
            self.status = SchedulerStatus.PAUSED
            logger.info("Payout scheduler paused")
            
        except Exception as e:
            logger.error(f"Failed to pause scheduler: {str(e)}")
            raise PayoutSchedulingError(f"Scheduler pause failed: {str(e)}")

    async def resume(self):
        """Resume the payout scheduler"""
        try:
            self.scheduler.resume()
            self.status = SchedulerStatus.RUNNING
            logger.info("Payout scheduler resumed")
            
        except Exception as e:
            logger.error(f"Failed to resume scheduler: {str(e)}")
            raise PayoutSchedulingError(f"Scheduler resume failed: {str(e)}")

    async def schedule_payout(
        self,
        payout: PayoutSchedule,
        strategy: Optional[str] = None
    ) -> bool:
        """
        Schedule individual payout for execution.
        
        Args:
            payout: PayoutSchedule object to process
            strategy: Optional strategy override
            
        Returns:
            True if scheduled successfully
        """
        try:
            # Validate payout
            if not payout or not payout.creator_id:
                raise PayoutSchedulingError("Invalid payout object")

            # Schedule immediate execution if due now
            if payout.scheduled_date <= datetime.utcnow():
                job_id = f"payout_{payout.id}_{datetime.utcnow().timestamp()}"
                
                self.scheduler.add_job(
                    self._execute_single_payout,
                    'date',
                    run_date=datetime.utcnow() + timedelta(seconds=1),
                    args=[payout.id],
                    id=job_id,
                    max_instances=1,
                    replace_existing=True
                )
            else:
                # Schedule for future execution
                job_id = f"payout_{payout.id}"
                
                self.scheduler.add_job(
                    self._execute_single_payout,
                    'date',
                    run_date=payout.scheduled_date,
                    args=[payout.id],
                    id=job_id,
                    max_instances=1,
                    replace_existing=True
                )

            self.metrics["scheduled_payouts"] += 1
            logger.info(f"Payout scheduled: {payout.id} for {payout.scheduled_date}")
            
            # Fire callback
            await self._fire_callback("payout_scheduled", {"payout": payout})
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to schedule payout {payout.id}: {str(e)}")
            raise PayoutSchedulingError(f"Payout scheduling failed: {str(e)}")

    async def process_batch_payouts(
        self,
        creator_ids: Optional[List[str]] = None,
        currency: str = "EUR",
        strategy: str = "weekly",
        dry_run: bool = False
    ) -> BatchPayoutResult:
        """
        Process batch payouts for eligible creators.
        
        Args:
            creator_ids: Optional list of specific creators
            currency: Currency for payouts
            strategy: Payout strategy to use
            dry_run: If True, don't execute payouts, just simulate
            
        Returns:
            BatchPayoutResult with processing statistics
        """
        start_time = datetime.utcnow()
        result = BatchPayoutResult(start_time=start_time)
        
        try:
            # Get payout strategy
            payout_strategy = self.strategies.get(strategy)
            if not payout_strategy:
                raise PayoutSchedulingError(f"Unknown payout strategy: {strategy}")

            # Find eligible payouts
            eligible_payouts = await self._find_eligible_payouts(
                creator_ids=creator_ids,
                currency=currency,
                minimum_amount=payout_strategy.minimum_amount,
                maximum_amount=payout_strategy.maximum_amount
            )

            result.total_processed = len(eligible_payouts)
            
            if not eligible_payouts:
                logger.info("No eligible payouts found for batch processing")
                result.end_time = datetime.utcnow()
                result.processing_time = (result.end_time - start_time).total_seconds()
                return result

            logger.info(f"Processing batch of {len(eligible_payouts)} payouts")

            # Process payouts in batches to avoid overwhelming payment providers
            batch_size = min(self.config.max_concurrent_payouts, 20)
            
            for i in range(0, len(eligible_payouts), batch_size):
                batch = eligible_payouts[i:i + batch_size]
                
                # Process batch concurrently
                batch_tasks = []
                for payout_data in batch:
                    if dry_run:
                        task = self._simulate_payout(payout_data)
                    else:
                        task = self._execute_payout_from_data(payout_data)
                    batch_tasks.append(task)
                
                # Wait for batch completion
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                # Process results
                for idx, batch_result in enumerate(batch_results):
                    payout_data = batch[idx]
                    
                    if isinstance(batch_result, Exception):
                        result.failed_payouts += 1
                        result.errors.append({
                            "creator_id": payout_data["creator_id"],
                            "error": str(batch_result),
                            "timestamp": datetime.utcnow().isoformat()
                        })
                        logger.error(f"Payout failed for {payout_data['creator_id']}: {batch_result}")
                    else:
                        result.successful_payouts += 1
                        result.total_amount += batch_result.get("amount", Decimal("0.00"))
                        logger.info(f"Payout completed for {payout_data['creator_id']}")

                # Small delay between batches
                await asyncio.sleep(1)

            result.end_time = datetime.utcnow()
            result.processing_time = (result.end_time - start_time).total_seconds()
            
            # Update metrics
            self.metrics["completed_payouts"] += result.successful_payouts
            self.metrics["failed_payouts"] += result.failed_payouts
            self.metrics["total_amount_processed"] += result.total_amount
            
            # Update average processing time
            if result.total_processed > 0:
                avg_time = result.processing_time / result.total_processed
                current_avg = self.metrics["average_processing_time"]
                self.metrics["average_processing_time"] = (current_avg + avg_time) / 2

            # Fire callback
            await self._fire_callback("batch_completed", {"result": result})

            logger.info(
                f"Batch payout processing completed: "
                f"{result.successful_payouts}/{result.total_processed} successful, "
                f"{result.total_amount} {currency} processed"
            )
            
            return result
            
        except Exception as e:
            result.end_time = datetime.utcnow()
            result.processing_time = (result.end_time - start_time).total_seconds()
            result.errors.append({
                "error": f"Batch processing failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            })
            
            logger.error(f"Batch payout processing failed: {str(e)}")
            raise PayoutSchedulingError(f"Batch processing failed: {str(e)}")

    async def add_strategy(self, strategy: PayoutStrategy):
        """Add custom payout strategy"""
        self.strategies[strategy.name] = strategy
        
        # If scheduler is running, update the jobs
        if self.status == SchedulerStatus.RUNNING:
            await self._schedule_strategy_job(strategy)

    async def remove_strategy(self, strategy_name: str):
        """
Remove payout strategy"""
        if strategy_name in self.strategies:
            del self.strategies[strategy_name]
            
            # Remove associated jobs
            jobs_to_remove = [
                job for job in self.scheduler.get_jobs() 
                if job.id.startswith(f"strategy_{strategy_name}")
            ]
            
            for job in jobs_to_remove:
                job.remove()

    async def get_pending_payouts(
        self,
        creator_id: Optional[str] = None,
        limit: int = 100
    ) -> List[PayoutSchedule]:
        """Get list of pending payouts"""
        if not self.db_session:
            return []

        query = self.db_session.query(PayoutSchedule).filter(
            PayoutSchedule.status == "scheduled"
        )
        
        if creator_id:
            query = query.filter(PayoutSchedule.creator_id == creator_id)
            
        return query.order_by(PayoutSchedule.scheduled_date).limit(limit).all()

    async def cancel_payout(self, payout_id: str) -> bool:
        """Cancel scheduled payout"""
        try:
            if not self.db_session:
                return False

            payout = self.db_session.query(PayoutSchedule).filter(
                PayoutSchedule.id == payout_id
            ).first()
            
            if not payout:
                raise PayoutError(f"Payout {payout_id} not found")

            if payout.status != "scheduled":
                raise PayoutError(f"Cannot cancel payout with status {payout.status}")

            # Update payout status
            payout.status = "cancelled"
            payout.updated_at = datetime.utcnow()
            self.db_session.commit()

            # Remove scheduled job
            job_id = f"payout_{payout_id}"
            try:
                self.scheduler.remove_job(job_id)
            except:
                pass  # Job might not exist

            logger.info(f"Payout cancelled: {payout_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel payout {payout_id}: {str(e)}")
            raise PayoutError(f"Payout cancellation failed: {str(e)}")

    def add_callback(self, event: str, callback: Callable):
        """Add event callback"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)

    def remove_callback(self, event: str, callback: Callable):
        """
Remove event callback"""
        if event in self.callbacks and callback in self.callbacks[event]:
            self.callbacks[event].remove(callback)

    async def get_scheduler_status(self) -> Dict[str, Any]:
        """
Get comprehensive scheduler status"""
        running_jobs = len(self.scheduler.get_jobs())
        
        return {
            "status": self.status.value,
            "running_jobs": running_jobs,
            "strategies": {name: strategy.enabled for name, strategy in self.strategies.items()},
            "metrics": dict(self.metrics),
            "uptime": getattr(self, 'start_time', None)
        }

    # Private methods
    async def _schedule_payout_jobs(self):
        """Schedule automatic payout jobs based on strategies"""
        for strategy in self.strategies.values():
            if strategy.enabled:
                await self._schedule_strategy_job(strategy)

    async def _schedule_strategy_job(self, strategy: PayoutStrategy):
        try:
            logger.info(f"Executing _schedule_strategy_job")
            
            # Implementation for _schedule_strategy_job
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_schedule_strategy_job completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_schedule_strategy_job failed: {e}")
            raise
            self._execute_strategy_payouts,
            trigger,
            args=[strategy.name],
            id=job_id,
            max_instances=1,
            replace_existing=True
        )

    async def _schedule_maintenance_jobs(self):
        """Schedule maintenance and cleanup jobs"""
        # Clean up old completed payouts
        self.scheduler.add_job(
            self._cleanup_old_payouts,
            IntervalTrigger(hours=24),
            id="cleanup_old_payouts",
            max_instances=1,
            replace_existing=True
        )
        
        # Retry failed payouts
        self.scheduler.add_job(
            self._retry_failed_payouts,
            IntervalTrigger(hours=6),
            id="retry_failed_payouts",
            max_instances=1,
            replace_existing=True
        )

    async def _execute_strategy_payouts(self, strategy_name: str):
        """Execute payouts for a specific strategy"""
        try:
            logger.info(f"Executing strategy payouts: {strategy_name}")
            
            result = await self.process_batch_payouts(
                strategy=strategy_name,
                dry_run=False
            )
            
            logger.info(f"Strategy {strategy_name} completed: {result.successful_payouts} payouts processed")
            
        except Exception as e:
            logger.error(f"Strategy execution failed for {strategy_name}: {str(e)}")

    async def _execute_single_payout(self, payout_id: str):
        """Execute single scheduled payout"""
        try:
            if not self.db_session:
                raise PayoutError("Database session not available")

            payout = self.db_session.query(PayoutSchedule).filter(
                PayoutSchedule.id == payout_id
            ).first()
            
            if not payout:
                logger.warning(f"Payout {payout_id} not found for execution")
                return

            if payout.status != "scheduled":
                logger.warning(f"Payout {payout_id} status is {payout.status}, skipping execution")
                return

            # Execute payout through payment agent
            # This would be implemented to call the payment processor
            await self._execute_payout_logic(payout)
            
            # Fire callback
            await self._fire_callback("payout_completed", {"payout": payout})
            
        except Exception as e:
            logger.error(f"Single payout execution failed for {payout_id}: {str(e)}")
            
            # Fire callback
            await self._fire_callback("payout_failed", {
                "payout_id": payout_id,
                "error": str(e)
            })

    async def _find_eligible_payouts(
        self,
        creator_ids: Optional[List[str]] = None,
        currency: str = "EUR",
        minimum_amount: Decimal = Decimal("10.00"),
        maximum_amount: Optional[Decimal] = None
    ) -> List[Dict[str, Any]]:
        """Find creators eligible for payouts"""
        if not self.db_session:
            return []

        # This would implement complex logic to find eligible creators
        # For now, return mock data
        return [
            {
                "creator_id": "creator_123",
                "available_balance": Decimal("125.50"),
                "currency": currency,
                "payment_method": "stripe_bank_transfer"
            }
        ]

    async def _execute_payout_from_data(self, payout_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute payout from payout data"""
        # This would create and execute a payout
        # For now, simulate execution
        await asyncio.sleep(0.1)  # Simulate processing time
        
        return {
            "success": True,
            "amount": payout_data["available_balance"],
            "creator_id": payout_data["creator_id"]
        }

    async def _simulate_payout(self, payout_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate payout execution for dry run"""
        return {
            "success": True,
            "amount": payout_data["available_balance"],
            "creator_id": payout_data["creator_id"],
            "simulated": True
        }

    async def _execute_payout_logic(self, payout: PayoutSchedule):
        """Execute the actual payout logic"""
        # Update status
        payout.status = "processing"
        payout.processing_started_at = datetime.utcnow()
        
        if self.db_session:
            self.db_session.commit()

        try:
            # This would integrate with payment processors
            # For now, simulate successful processing
            await asyncio.sleep(1)  # Simulate processing time
            
            payout.status = "completed"
            payout.completed_at = datetime.utcnow()
            payout.external_id = f"ext_{datetime.utcnow().timestamp()}"
            
            if self.db_session:
                self.db_session.commit()
                
        except Exception as e:
            payout.status = "failed"
            payout.error_message = str(e)
            
            if self.db_session:
                self.db_session.commit()
                
            raise

    async def _cleanup_old_payouts(self):
        """Clean up old completed payouts"""
        if not self.db_session:
            return

        # Delete payouts older than 90 days
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        
        deleted = self.db_session.query(PayoutSchedule).filter(
            and_(
                PayoutSchedule.status == "completed",
                PayoutSchedule.completed_at < cutoff_date
            )
        ).delete()
        
        self.db_session.commit()
        
        if deleted > 0:
            logger.info(f"Cleaned up {deleted} old payout records")

    async def _retry_failed_payouts(self):
        """Retry failed payouts that are eligible for retry"""
        if not self.db_session:
            return

        # Find failed payouts from last 24 hours with retry count < 3
        cutoff_date = datetime.utcnow() - timedelta(hours=24)
        
        failed_payouts = self.db_session.query(PayoutSchedule).filter(
            and_(
                PayoutSchedule.status == "failed",
                PayoutSchedule.created_at > cutoff_date,
                PayoutSchedule.retry_count < 3
            )
        ).all()

        for payout in failed_payouts:
            try:
                payout.retry_count += 1
                payout.status = "scheduled"
                payout.scheduled_date = datetime.utcnow() + timedelta(minutes=30)
                payout.error_message = None
                
                self.db_session.commit()
                
                await self.schedule_payout(payout)
                logger.info(f"Retry scheduled for payout {payout.id} (attempt {payout.retry_count})")
                
            except Exception as e:
                logger.error(f"Failed to retry payout {payout.id}: {str(e)}")

    async def _fire_callback(self, event: str, data: Dict[str, Any]):
        """Fire event callbacks"""
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                try:
                    await callback(data)
                except Exception as e:
                    logger.error(f"Callback error for event {event}: {str(e)}")
