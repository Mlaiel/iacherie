"""Campaigns API routes"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_

from api.dependencies import get_db, get_current_user
from api.schemas.campaigns import (
    CampaignCreate, CampaignUpdate, CampaignResponse,
    SignatureCreate, SignatureResponse,
    DonationCreate, DonationResponse,
    CampaignUpdateCreate, CampaignUpdateResponse,
    CampaignStats, CampaignFilters
)
from models.campaign import Campaign, Signature, Donation
from models.campaign import CampaignUpdate as CampaignUpdateModel

router = APIRouter()


def campaign_to_dict(campaign: Campaign) -> dict:
    """Convert Campaign model to dict for response"""
    return {
        'id': campaign.id,
        'type': campaign.type.value if hasattr(campaign.type, 'value') else campaign.type,
        'status': campaign.status.value if hasattr(campaign.status, 'value') else campaign.status,
        'title': campaign.title,
        'description': campaign.description,
        'story': campaign.story,
        'objectives': campaign.objectives,
        'goal': campaign.goal,
        'current_amount': campaign.current_amount or 0,
        'tags': campaign.tags or [],
        'creator_id': campaign.creator_id,
        'creator_type': campaign.creator_type,
        'organization_name': campaign.organization_name,
        'start_date': campaign.start_date,
        'end_date': campaign.end_date,
        'cover_image': campaign.cover_image,
        'images': campaign.images or [],
        'videos': campaign.videos or [],
        'beneficiary_name': campaign.beneficiary_name,
        'beneficiary_details': campaign.beneficiary_details,
        'funds_usage_plan': campaign.funds_usage_plan,
        'transparency_reports': campaign.transparency_reports or [],
        'target_authority': campaign.target_authority,
        'target_email': campaign.target_email,
        'petition_text': campaign.petition_text,
        'supporters_count': campaign.supporters_count or 0,
        'comments_count': campaign.comments_count or 0,
        'shares_count': campaign.shares_count or 0,
        'views_count': campaign.views_count or 0,
        'success_story': campaign.success_story,
        'impact_achieved': campaign.impact_achieved,
        'is_public': campaign.is_public,
        'is_featured': campaign.is_featured,
        'is_verified': campaign.is_verified,
        'created_at': campaign.created_at,
        'updated_at': campaign.updated_at,
        'published_at': campaign.published_at,
        'closed_at': campaign.closed_at,
    }


@router.post("/campaigns", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: CampaignCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Créer une nouvelle campagne (pétition ou fundraising)
    """
    # Create campaign
    new_campaign = Campaign(
        type=campaign_data.type,
        title=campaign_data.title,
        description=campaign_data.description,
        story=campaign_data.story,
        objectives=campaign_data.objectives,
        goal=campaign_data.goal,
        tags=campaign_data.tags,
        creator_id=UUID(current_user['id']),
        creator_type=campaign_data.creator_type,
        organization_name=campaign_data.organization_name,
        end_date=campaign_data.end_date,
        cover_image=campaign_data.cover_image,
        images=campaign_data.images,
        videos=campaign_data.videos,
        beneficiary_name=campaign_data.beneficiary_name,
        beneficiary_details=campaign_data.beneficiary_details,
        funds_usage_plan=campaign_data.funds_usage_plan,
        target_authority=campaign_data.target_authority,
        target_email=campaign_data.target_email,
        petition_text=campaign_data.petition_text,
        status='draft'
    )
    
    db.add(new_campaign)
    db.commit()
    db.refresh(new_campaign)
    
    return CampaignResponse(**campaign_to_dict(new_campaign))


@router.get("/campaigns", response_model=List[CampaignResponse])
async def list_campaigns(
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None),
    creator_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lister les campagnes avec filtres optionnels
    """
    query = db.query(Campaign).filter(Campaign.is_public == True)
    
    # Only show active campaigns by default
    if not status:
        query = query.filter(Campaign.status == 'active')
    
    # Filters
    if type:
        query = query.filter(Campaign.type == type)
    
    if status:
        query = query.filter(Campaign.status == status)
    
    if tags:
        query = query.filter(Campaign.tags.overlap(tags))
    
    if creator_type:
        query = query.filter(Campaign.creator_type == creator_type)
    
    # Order by most recent
    query = query.order_by(Campaign.created_at.desc())
    
    # Pagination
    campaigns = query.offset(skip).limit(limit).all()
    
    return [CampaignResponse(**campaign_to_dict(campaign)) for campaign in campaigns]


@router.get("/campaigns/trending", response_model=List[CampaignResponse])
async def get_trending_campaigns(
    type: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Obtenir les campagnes tendances (plus de supporters récents)
    """
    query = db.query(Campaign).filter(
        Campaign.is_public == True,
        Campaign.status == 'active'
    )
    
    if type:
        query = query.filter(Campaign.type == type)
    
    # Order by supporters count
    query = query.order_by(Campaign.supporters_count.desc()).limit(limit)
    
    campaigns = query.all()
    return [CampaignResponse(**campaign_to_dict(campaign)) for campaign in campaigns]


@router.get("/campaigns/featured", response_model=List[CampaignResponse])
async def get_featured_campaigns(
    db: Session = Depends(get_db)
):
    """
    Obtenir les campagnes mises en avant
    """
    campaigns = db.query(Campaign).filter(
        Campaign.is_featured == True,
        Campaign.is_public == True,
        Campaign.status == 'active'
    ).order_by(Campaign.created_at.desc()).limit(10).all()
    
    return [CampaignResponse(**campaign_to_dict(campaign)) for campaign in campaigns]


@router.get("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Obtenir les détails d'une campagne
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Increment views
    campaign.views_count = (campaign.views_count or 0) + 1
    db.commit()
    
    return CampaignResponse(**campaign_to_dict(campaign))


@router.put("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: UUID,
    campaign_data: CampaignUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mettre à jour une campagne (créateur ou admin uniquement)
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Check ownership
    if str(campaign.creator_id) != current_user['id'] and 'admin' not in current_user.get('roles', []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this campaign"
        )
    
    # Update fields
    update_data = campaign_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(campaign, field, value)
    
    campaign.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(campaign)
    
    return CampaignResponse(**campaign_to_dict(campaign))


@router.put("/campaigns/{campaign_id}/publish", response_model=CampaignResponse)
async def publish_campaign(
    campaign_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Publier une campagne (la rendre active)
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Check ownership
    if str(campaign.creator_id) != current_user['id'] and 'admin' not in current_user.get('roles', []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to publish this campaign"
        )
    
    campaign.status = 'active'
    campaign.published_at = datetime.utcnow()
    campaign.start_date = datetime.utcnow()
    campaign.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(campaign)
    
    return CampaignResponse(**campaign_to_dict(campaign))


# ===== SIGNATURES (Petitions) =====

@router.post("/campaigns/{campaign_id}/sign", response_model=SignatureResponse, status_code=status.HTTP_201_CREATED)
async def sign_petition(
    campaign_id: UUID,
    signature_data: SignatureCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Signer une pétition
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    if campaign.type != 'petition':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This campaign is not a petition"
        )
    
    if campaign.status != 'active':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot sign inactive petition"
        )
    
    # Check if already signed
    existing = db.query(Signature).filter(
        Signature.campaign_id == campaign_id,
        or_(
            Signature.user_id == UUID(current_user['id']),
            Signature.email == signature_data.email
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already signed this petition"
        )
    
    # Create signature
    new_signature = Signature(
        campaign_id=campaign_id,
        user_id=UUID(current_user['id']),
        full_name=signature_data.full_name,
        email=signature_data.email,
        city=signature_data.city,
        country=signature_data.country,
        message=signature_data.message,
        is_public=signature_data.is_public,
        is_anonymous=signature_data.is_anonymous,
        is_verified=True  # Auto-verify if authenticated user
    )
    
    db.add(new_signature)
    
    # Update campaign
    campaign.current_amount = (campaign.current_amount or 0) + 1
    campaign.supporters_count = (campaign.supporters_count or 0) + 1
    
    # Check if goal reached
    if campaign.current_amount >= campaign.goal and campaign.status == 'active':
        campaign.status = 'successful'
    
    db.commit()
    db.refresh(new_signature)
    
    return SignatureResponse(
        id=new_signature.id,
        campaign_id=new_signature.campaign_id,
        user_id=new_signature.user_id,
        full_name=new_signature.full_name,
        email=new_signature.email,
        city=new_signature.city,
        country=new_signature.country,
        message=new_signature.message,
        is_public=new_signature.is_public,
        is_anonymous=new_signature.is_anonymous,
        is_verified=new_signature.is_verified,
        created_at=new_signature.created_at
    )


@router.get("/campaigns/{campaign_id}/signatures", response_model=List[SignatureResponse])
async def get_signatures(
    campaign_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Obtenir les signatures d'une pétition (uniquement les publiques)
    """
    signatures = db.query(Signature).filter(
        Signature.campaign_id == campaign_id,
        Signature.is_public == True
    ).order_by(Signature.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        SignatureResponse(
            id=sig.id,
            campaign_id=sig.campaign_id,
            user_id=sig.user_id,
            full_name=sig.full_name if not sig.is_anonymous else "Anonymous",
            email=sig.email if not sig.is_anonymous else "",
            city=sig.city,
            country=sig.country,
            message=sig.message,
            is_public=sig.is_public,
            is_anonymous=sig.is_anonymous,
            is_verified=sig.is_verified,
            created_at=sig.created_at
        )
        for sig in signatures
    ]


# ===== DONATIONS (Fundraising) =====

@router.post("/campaigns/{campaign_id}/donate", response_model=DonationResponse, status_code=status.HTTP_201_CREATED)
async def donate_to_campaign(
    campaign_id: UUID,
    donation_data: DonationCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Faire un don à une campagne de fundraising
    
    Note: Payment processing is deferred as per user request
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    if campaign.type != 'fundraising':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This campaign is not a fundraising campaign"
        )
    
    if campaign.status != 'active':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot donate to inactive campaign"
        )
    
    # Create donation
    new_donation = Donation(
        campaign_id=campaign_id,
        user_id=UUID(current_user['id']),
        amount=donation_data.amount,
        currency=donation_data.currency,
        donor_name=donation_data.donor_name or current_user.get('full_name'),
        donor_email=donation_data.donor_email or current_user.get('email'),
        message=donation_data.message,
        is_public=donation_data.is_public,
        is_anonymous=donation_data.is_anonymous,
        tax_receipt_requested=donation_data.tax_receipt_requested,
        payment_status='completed',  # Temporary: auto-complete until payment integration
        completed_at=datetime.utcnow()
    )
    
    db.add(new_donation)
    
    # Update campaign
    campaign.current_amount = (campaign.current_amount or 0) + donation_data.amount
    campaign.supporters_count = (campaign.supporters_count or 0) + 1
    
    # Check if goal reached
    if campaign.current_amount >= campaign.goal and campaign.status == 'active':
        campaign.status = 'successful'
    
    db.commit()
    db.refresh(new_donation)
    
    return DonationResponse(
        id=new_donation.id,
        campaign_id=new_donation.campaign_id,
        user_id=new_donation.user_id,
        amount=new_donation.amount,
        currency=new_donation.currency,
        donor_name=new_donation.donor_name,
        donor_email=new_donation.donor_email,
        message=new_donation.message,
        is_public=new_donation.is_public,
        is_anonymous=new_donation.is_anonymous,
        payment_status=new_donation.payment_status,
        tax_receipt_requested=new_donation.tax_receipt_requested,
        tax_receipt_sent=new_donation.tax_receipt_sent,
        created_at=new_donation.created_at,
        completed_at=new_donation.completed_at
    )


@router.get("/campaigns/{campaign_id}/donations", response_model=List[DonationResponse])
async def get_donations(
    campaign_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Obtenir les dons d'une campagne de fundraising (uniquement les publics)
    """
    donations = db.query(Donation).filter(
        Donation.campaign_id == campaign_id,
        Donation.is_public == True,
        Donation.payment_status == 'completed'
    ).order_by(Donation.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        DonationResponse(
            id=don.id,
            campaign_id=don.campaign_id,
            user_id=don.user_id,
            amount=don.amount if not don.is_anonymous else 0,
            currency=don.currency,
            donor_name=don.donor_name if not don.is_anonymous else "Anonymous",
            donor_email=don.donor_email if not don.is_anonymous else "",
            message=don.message,
            is_public=don.is_public,
            is_anonymous=don.is_anonymous,
            payment_status=don.payment_status,
            tax_receipt_requested=don.tax_receipt_requested,
            tax_receipt_sent=don.tax_receipt_sent,
            created_at=don.created_at,
            completed_at=don.completed_at
        )
        for don in donations
    ]


# ===== CAMPAIGN UPDATES =====

@router.post("/campaigns/{campaign_id}/updates", response_model=CampaignUpdateResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign_update(
    campaign_id: UUID,
    update_data: CampaignUpdateCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Poster une mise à jour pour une campagne (créateur uniquement)
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Check ownership
    if str(campaign.creator_id) != current_user['id'] and 'admin' not in current_user.get('roles', []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only campaign creator can post updates"
        )
    
    # Create update
    new_update = CampaignUpdateModel(
        campaign_id=campaign_id,
        author_id=UUID(current_user['id']),
        title=update_data.title,
        content=update_data.content,
        media_urls=update_data.media_urls,
        update_type=update_data.update_type,
        funds_used=update_data.funds_used,
        funds_usage_details=update_data.funds_usage_details,
        receipts=update_data.receipts,
        notify_supporters=update_data.notify_supporters
    )
    
    db.add(new_update)
    db.commit()
    db.refresh(new_update)
    
    return CampaignUpdateResponse(
        id=new_update.id,
        campaign_id=new_update.campaign_id,
        author_id=new_update.author_id,
        title=new_update.title,
        content=new_update.content,
        media_urls=new_update.media_urls or [],
        update_type=new_update.update_type,
        funds_used=new_update.funds_used,
        funds_usage_details=new_update.funds_usage_details,
        receipts=new_update.receipts or [],
        notify_supporters=new_update.notify_supporters,
        created_at=new_update.created_at
    )


@router.get("/campaigns/{campaign_id}/updates", response_model=List[CampaignUpdateResponse])
async def get_campaign_updates(
    campaign_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Obtenir les mises à jour d'une campagne
    """
    updates = db.query(CampaignUpdateModel).filter(
        CampaignUpdateModel.campaign_id == campaign_id
    ).order_by(CampaignUpdateModel.created_at.desc()).all()
    
    return [
        CampaignUpdateResponse(
            id=u.id,
            campaign_id=u.campaign_id,
            author_id=u.author_id,
            title=u.title,
            content=u.content,
            media_urls=u.media_urls or [],
            update_type=u.update_type,
            funds_used=u.funds_used,
            funds_usage_details=u.funds_usage_details,
            receipts=u.receipts or [],
            notify_supporters=u.notify_supporters,
            created_at=u.created_at
        )
        for u in updates
    ]


@router.get("/campaigns/{campaign_id}/stats", response_model=CampaignStats)
async def get_campaign_stats(
    campaign_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Obtenir les statistiques d'une campagne
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Calculate percentage
    percentage = (campaign.current_amount / campaign.goal * 100) if campaign.goal > 0 else 0
    
    # Calculate days remaining
    days_remaining = None
    if campaign.end_date:
        delta = campaign.end_date - datetime.utcnow()
        days_remaining = max(0, delta.days)
    
    # Calculate average contribution (for fundraising)
    average_contribution = None
    if campaign.type == 'fundraising' and campaign.supporters_count > 0:
        average_contribution = campaign.current_amount / campaign.supporters_count
    
    return CampaignStats(
        total_supporters=campaign.supporters_count or 0,
        current_amount=campaign.current_amount or 0,
        goal=campaign.goal,
        percentage=round(percentage, 2),
        days_remaining=days_remaining,
        average_contribution=round(average_contribution, 2) if average_contribution else None
    )


@router.get("/campaigns/my/created", response_model=List[CampaignResponse])
async def get_my_campaigns(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtenir les campagnes créées par l'utilisateur courant
    """
    campaigns = db.query(Campaign).filter(
        Campaign.creator_id == UUID(current_user['id'])
    ).order_by(Campaign.created_at.desc()).all()
    
    return [CampaignResponse(**campaign_to_dict(campaign)) for campaign in campaigns]


@router.get("/campaigns/my/supported", response_model=List[CampaignResponse])
async def get_supported_campaigns(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtenir les campagnes supportées par l'utilisateur (signées ou donné)
    """
    user_id = UUID(current_user['id'])
    
    # Get signed petitions
    signatures = db.query(Signature).filter(Signature.user_id == user_id).all()
    signed_ids = [s.campaign_id for s in signatures]
    
    # Get donated fundraising
    donations = db.query(Donation).filter(Donation.user_id == user_id).all()
    donated_ids = [d.campaign_id for d in donations]
    
    # Combine
    all_ids = list(set(signed_ids + donated_ids))
    
    if not all_ids:
        return []
    
    campaigns = db.query(Campaign).filter(Campaign.id.in_(all_ids)).order_by(Campaign.updated_at.desc()).all()
    
    return [CampaignResponse(**campaign_to_dict(campaign)) for campaign in campaigns]
