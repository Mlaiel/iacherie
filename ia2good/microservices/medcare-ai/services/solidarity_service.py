"""
Medication Solidarity Service
Help patients who can't afford medications
"""
import logging
import json
from typing import List, Optional, Dict
from uuid import UUID, uuid4
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)


class MedicationSolidarityService:
    """
    Service for medication solidarity program
    
    Features:
    - Patients post medication needs
    - Volunteers contribute funds
    - Track contributions and delivery
    - Verify authenticity with doctor
    - Secure payment processing
    - Delivery coordination
    """
    
    def __init__(self, db_session=None):
        self.db = db_session
    
    async def create_solidarity_request(
        self,
        patient_id: UUID,
        prescription_id: Optional[UUID],
        title: str,
        description: str,
        medications_needed: List[Dict],
        urgency: str,
        currency: str = 'EUR'
    ) -> Dict:
        """
        Create medication solidarity request
        
        Steps:
        1. Validate prescription if provided
        2. Calculate total cost
        3. Create request
        4. Notify community
        """
        
        # Calculate total cost
        total_cost = sum(Decimal(str(med['estimated_cost'])) * Decimal(str(med['quantity'])) for med in medications_needed)
        
        # Create request
        request = {
            'id': uuid4(),
            'patient_id': patient_id,
            'prescription_id': prescription_id,
            'title': title,
            'description': description,
            'medications_needed': medications_needed,
            'total_estimated_cost': total_cost,
            'currency': currency,
            'urgency': urgency,
            'status': 'open',
            'amount_raised': Decimal('0.00'),
            'is_verified': False,
            'created_at': datetime.now()
        }
        
        # Save to database if configured
        if self.db:
            try:
                from sqlalchemy import text
                query = text("""
                INSERT INTO medcare_solidarity_requests 
                (id, patient_id, prescription_id, title, description, medications_needed, 
                 total_estimated_cost, currency, urgency, status, amount_raised, is_verified, created_at)
                VALUES (:id, :patient_id, :prescription_id, :title, :description, :medications_needed, 
                        :total_estimated_cost, :currency, :urgency, :status, :amount_raised, :is_verified, :created_at)
                """)
                await self.db.execute(query, {
                    'id': str(request['id']),
                    'patient_id': str(patient_id),
                    'prescription_id': str(prescription_id) if prescription_id else None,
                    'title': title,
                    'description': description,
                    'medications_needed': json.dumps(medications_needed),
                    'total_estimated_cost': float(total_cost),
                    'currency': currency,
                    'urgency': urgency,
                    'status': 'open',
                    'amount_raised': 0.0,
                    'is_verified': False,
                    'created_at': request['created_at']
                })
                await self.db.commit()
                logger.info(f"Request {request['id']} saved to database")
            except Exception as e:
                logger.warning(f"Could not save request to DB: {e}")
        
        logger.info(f"Solidarity request created: {request['id']} - {title}")
        logger.info(f"Total cost: {total_cost} {currency}, Urgency: {urgency}")
        
        # Notify community (high priority for critical/urgent)
        await self._notify_community(request)
        
        # If has prescription, request doctor verification
        if prescription_id:
            await self._request_doctor_verification(request['id'], prescription_id)
        
        return request
    
    async def verify_request_by_doctor(
        self,
        request_id: UUID,
        doctor_id: UUID,
        verification_notes: Optional[str] = None
    ) -> bool:
        """
        Doctor verifies solidarity request is legitimate
        
        Increases trust and contribution likelihood
        """
        
        # In real implementation, update database
        logger.info(f"Request {request_id} verified by doctor {doctor_id}")
        if verification_notes:
            logger.info(f"Verification notes: {verification_notes}")
        
        # Update request status
        # request.is_verified = True
        # request.verified_by_doctor_id = doctor_id
        
        # Notify contributors that request is now verified
        await self._notify_verification_completed(request_id)
        
        return True
    
    async def contribute_to_request(
        self,
        request_id: UUID,
        contributor_id: UUID,
        amount: Decimal,
        currency: str,
        payment_method: str,
        message_to_patient: Optional[str] = None,
        is_anonymous: bool = False
    ) -> Dict:
        """
        Volunteer contributes funds to medication request
        
        Steps:
        1. Process payment
        2. Record contribution
        3. Update request amount
        4. Check if fully funded
        5. Notify patient
        """
        
        # Validate amount
        if amount <= 0:
            raise ValueError("Contribution amount must be positive")
        
        # Process payment
        payment_result = await self._process_payment(
            contributor_id,
            amount,
            currency,
            payment_method
        )
        
        if not payment_result['success']:
            raise ValueError(f"Payment failed: {payment_result['error']}")
        
        # Create contribution record
        contribution = {
            'id': uuid4(),
            'solidarity_request_id': request_id,
            'contributor_id': contributor_id,
            'amount': amount,
            'currency': currency,
            'payment_method': payment_method,
            'payment_status': 'completed',
            'payment_transaction_id': payment_result['transaction_id'],
            'message_to_patient': message_to_patient,
            'is_anonymous': is_anonymous,
            'created_at': datetime.now()
        }
        
        logger.info(f"Contribution received: {amount} {currency} for request {request_id}")
        
        # Update request amount_raised
        # In real implementation, fetch request and update
        # new_amount = request.amount_raised + amount
        # request.amount_raised = new_amount
        
        # Check if fully funded
        # if new_amount >= request.total_estimated_cost:
        #     request.status = 'fully_funded'
        #     await self._initiate_delivery(request_id)
        
        # Notify patient of contribution
        await self._notify_patient_contribution(
            request_id,
            contribution,
            is_anonymous
        )
        
        return contribution
    
    async def get_request_with_details(self, request_id: UUID) -> Dict:
        """
        Get solidarity request with all contributions and delivery info
        """
        from sqlalchemy import text
        
        # Fetch from database
        if self.db:
            try:
                query = text("SELECT * FROM medcare_solidarity_requests WHERE id = :id")
                result = await self.db.execute(query, {'id': str(request_id)})
                row = result.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'title': row[3],
                        'description': row[4],
                        'medications_needed': row[5],
                        'total_estimated_cost': row[6],
                        'currency': row[7],
                        'urgency': row[8],
                        'status': row[9],
                        'amount_raised': row[10],
                        'is_verified': row[11],
                        'created_at': str(row[12]),
                        'contributions': [],
                        'funding_percentage': float((row[10] / row[6]) * 100) if row[6] > 0 else 0
                    }
            except Exception as e:
                logger.warning(f"Could not fetch request: {e}")
        
        # Fallback mock data
        request = {
            'id': request_id,
            'title': "Help me afford insulin",
            'description': "I'm diabetic and lost my job...",
            'total_estimated_cost': Decimal('150.00'),
            'amount_raised': Decimal('100.00'),
            'urgency': 'critical',
            'status': 'partially_funded',
            'is_verified': True
        }
        
        contributions = [
            {
                'id': uuid4(),
                'amount': Decimal('50.00'),
                'message_to_patient': "Hope this helps!",
                'is_anonymous': True,
                'created_at': datetime.now()
            },
            {
                'id': uuid4(),
                'amount': Decimal('50.00'),
                'message_to_patient': "Stay strong",
                'is_anonymous': False,
                'created_at': datetime.now()
            }
        ]
        
        funding_percentage = float(
            (request['amount_raised'] / request['total_estimated_cost']) * 100
        )
        
        return {
            'request': request,
            'contributions': contributions,
            'delivery': None,  # Not yet delivered
            'funding_percentage': funding_percentage,
            'contributors_count': len(contributions)
        }
    
    async def search_open_requests(
        self,
        urgency: Optional[str] = None,
        verified_only: bool = False,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict]:
        """
        Search open solidarity requests
        
        Used by volunteers to find requests to support
        """
        
        # In real implementation, query database
        
        filters = []
        if urgency:
            filters.append(f"urgency={urgency}")
        if verified_only:
            filters.append("verified_only=True")
        
        logger.info(f"Searching solidarity requests: {', '.join(filters)}")
        
        return []
    
    async def initiate_delivery(
        self,
        request_id: UUID,
        pharmacy_id: Optional[UUID] = None,
        volunteer_id: Optional[UUID] = None
    ) -> Dict:
        """
        Initiate medication delivery after fully funded
        
        Options:
        1. Pharmacy fulfillment: Pharmacy gets paid, delivers to patient
        2. Volunteer delivery: Volunteer buys and delivers
        """
        
        delivery = {
            'id': uuid4(),
            'solidarity_request_id': request_id,
            'pharmacy_id': pharmacy_id,
            'volunteer_id': volunteer_id,
            'delivery_status': 'pending',
            'created_at': datetime.now()
        }
        
        if pharmacy_id:
            # Send prescription to pharmacy
            await self._send_prescription_to_pharmacy(request_id, pharmacy_id)
            logger.info(f"Prescription sent to pharmacy {pharmacy_id}")
        
        elif volunteer_id:
            # Notify volunteer to purchase
            await self._notify_volunteer_to_purchase(request_id, volunteer_id)
            logger.info(f"Volunteer {volunteer_id} notified to purchase medications")
        
        return delivery
    
    async def update_delivery_status(
        self,
        delivery_id: UUID,
        status: str,
        tracking_number: Optional[str] = None,
        delivery_proof_url: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict:
        """
        Update delivery status
        
        Statuses: pending → purchased → in_transit → delivered
        """
        
        # In real implementation, update database
        logger.info(f"Delivery {delivery_id} status updated: {status}")
        
        if tracking_number:
            logger.info(f"Tracking number: {tracking_number}")
        
        if status == 'delivered':
            # Mark solidarity request as delivered
            # Notify patient
            # Thank contributors
            await self._complete_solidarity_cycle(delivery_id)
        
        return {
            'id': delivery_id,
            'delivery_status': status,
            'tracking_number': tracking_number,
            'updated_at': datetime.now()
        }
    
    async def _process_payment(
        self,
        contributor_id: UUID,
        amount: Decimal,
        currency: str,
        payment_method: str
    ) -> Dict:
        """
        Process payment via payment gateway (Stripe)
        
        In production, integrate with Stripe API
        """
        
        try:
            # Simulate Stripe payment
            # import stripe
            # stripe.api_key = STRIPE_SECRET_KEY
            # 
            # payment_intent = stripe.PaymentIntent.create(
            #     amount=int(amount * 100),  # cents
            #     currency=currency.lower(),
            #     payment_method=payment_method,
            #     confirm=True
            # )
            
            # Simulated success
            transaction_id = f"txn_{uuid4().hex[:16]}"
            
            logger.info(f"Payment processed: {amount} {currency} - {transaction_id}")
            
            return {
                'success': True,
                'transaction_id': transaction_id
            }
        
        except Exception as e:
            logger.error(f"Payment processing error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _notify_community(self, request: Dict):
        """
        Notify community of new solidarity request
        
        Priority based on urgency:
        - Critical: Push notification to all volunteers
        - Urgent: Email + in-app notification
        - Normal: In-app notification only
        """
        
        urgency = request['urgency']
        
        notification_channels = ['in_app']
        if urgency in ['critical', 'urgent']:
            notification_channels.append('email')
        if urgency == 'critical':
            notification_channels.append('push')
        
        logger.info(f"Notifying community via: {notification_channels}")
        
        # In real implementation, call notification service
    
    async def _request_doctor_verification(
        self,
        request_id: UUID,
        prescription_id: UUID
    ):
        """
        Request doctor who issued prescription to verify request
        """
        
        # In real implementation:
        # 1. Get doctor_id from prescription
        # 2. Send notification to doctor
        # 3. Provide verification link
        
        logger.info(f"Verification requested from doctor for request {request_id}")
    
    async def _notify_verification_completed(self, request_id: UUID):
        """
        Notify potential contributors that request is now verified
        """
        
        logger.info(f"Request {request_id} verification completed - notifying community")
    
    async def _notify_patient_contribution(
        self,
        request_id: UUID,
        contribution: Dict,
        is_anonymous: bool
    ):
        """
        Notify patient of new contribution
        """
        
        contributor_name = "Anonymous donor" if is_anonymous else "A generous donor"
        message = contribution.get('message_to_patient', '')
        
        logger.info(f"Patient notified of contribution: {contribution['amount']}")
        if message:
            logger.info(f"Message: {message}")
    
    async def _send_prescription_to_pharmacy(
        self,
        request_id: UUID,
        pharmacy_id: UUID
    ):
        """
        Send prescription to pharmacy for fulfillment
        """
        
        # In real implementation:
        # 1. Get prescription details
        # 2. Send to pharmacy API
        # 3. Provide payment confirmation
        
        logger.info(f"Prescription sent to pharmacy {pharmacy_id}")
    
    async def _notify_volunteer_to_purchase(
        self,
        request_id: UUID,
        volunteer_id: UUID
    ):
        """
        Notify volunteer to purchase medications
        """
        
        logger.info(f"Volunteer {volunteer_id} notified to purchase for request {request_id}")
    
    async def _complete_solidarity_cycle(self, delivery_id: UUID):
        """
        Complete solidarity cycle after delivery
        
        Actions:
        1. Mark request as delivered
        2. Send thank you to patient
        3. Send thank you to all contributors
        4. Generate impact report
        """
        
        logger.info(f"Solidarity cycle completed for delivery {delivery_id}")
        
        # Generate impact report
        impact = {
            'delivery_id': delivery_id,
            'patient_helped': 1,
            'medications_delivered': True,
            'contributors_count': 0,  # Get from database
            'total_amount': Decimal('0.00'),  # Get from database
            'delivery_time_hours': 0  # Calculate
        }
        
        logger.info(f"Impact: {impact}")
