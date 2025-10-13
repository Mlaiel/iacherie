"""
Medication Solidarity models for MedCare-AI
Help patients who can't afford medications
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from enum import Enum

class SolidarityUrgency(str, Enum):
    """Urgency of medication need"""
    CRITICAL = "critical"  # Life-threatening, needs immediate help
    URGENT = "urgent"      # Important treatment, should get within days
    NORMAL = "normal"      # Regular medication, can wait a bit

class SolidarityStatus(str, Enum):
    """Status of solidarity request"""
    OPEN = "open"
    PARTIALLY_FUNDED = "partially_funded"
    FULLY_FUNDED = "fully_funded"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class PaymentStatus(str, Enum):
    """Status of payment"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class DeliveryStatus(str, Enum):
    """Status of medication delivery"""
    PENDING = "pending"
    PURCHASED = "purchased"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"

class MedicationNeeded(BaseModel):
    """Details of medication needed"""
    name: str
    dosage: str
    quantity: int
    unit: str  # tablets, vials, boxes, etc.
    estimated_cost: Decimal
    is_critical: bool = False

class SolidarityRequestCreate(BaseModel):
    """Create medication solidarity request"""
    patient_id: UUID
    prescription_id: Optional[UUID] = None
    title: str = Field(min_length=10, max_length=255)
    description: str = Field(min_length=50)
    medications_needed: List[MedicationNeeded]
    urgency: SolidarityUrgency
    currency: str = "EUR"
    
class SolidarityRequest(BaseModel):
    """Complete solidarity request"""
    id: UUID
    patient_id: UUID
    prescription_id: Optional[UUID]
    title: str
    description: str
    medications_needed: List[Dict]
    total_estimated_cost: Decimal
    currency: str
    urgency: SolidarityUrgency
    delivery_address: Optional[Dict]  # Encrypted
    status: SolidarityStatus
    amount_raised: Decimal
    is_verified: bool
    verified_by_doctor_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ContributionCreate(BaseModel):
    """Create contribution to solidarity request"""
    contributor_id: UUID
    amount: Decimal = Field(gt=0)
    currency: str = "EUR"
    payment_method: str = "card"  # Default payment method
    message_to_patient: Optional[str] = None
    is_anonymous: bool = False

class Contribution(BaseModel):
    """Complete contribution"""
    id: UUID
    solidarity_request_id: UUID
    contributor_id: UUID
    amount: Decimal
    currency: str
    payment_method: str
    payment_status: PaymentStatus
    payment_transaction_id: Optional[str]
    message_to_patient: Optional[str]
    is_anonymous: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class DeliveryCreate(BaseModel):
    """Create delivery record"""
    volunteer_id: Optional[UUID] = None
    pharmacy_id: Optional[UUID] = None
    tracking_number: Optional[str] = None
    notes: Optional[str] = None

class Delivery(BaseModel):
    """Complete delivery record"""
    id: UUID
    solidarity_request_id: UUID
    volunteer_id: Optional[UUID]
    pharmacy_id: Optional[UUID]
    tracking_number: Optional[str]
    delivery_status: DeliveryStatus
    purchased_at: Optional[datetime]
    delivered_at: Optional[datetime]
    delivery_proof_url: Optional[str]
    notes: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class SolidarityRequestWithDetails(BaseModel):
    """Solidarity request with contributions and delivery info"""
    request: SolidarityRequest
    contributions: List[Contribution]
    delivery: Optional[Delivery]
    funding_percentage: float
    contributors_count: int
