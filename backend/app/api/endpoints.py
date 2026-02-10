"""
API endpoints for AutoOtvet
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.models import MarketplaceAccount, LLMConfig, ReviewRule, Review, User
from app.api.schemas import (
    MarketplaceAccountCreate, MarketplaceAccountUpdate, MarketplaceAccountResponse,
    LLMConfigCreate, LLMConfigUpdate, LLMConfigResponse,
    ReviewRuleCreate, ReviewRuleResponse, ReviewResponse, StatsResponse
)
from app.core.security import crypto_service

router = APIRouter()


def get_current_user(db: Session):
    """Helper to get first user (for testing, in production use auth)"""
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=400, detail="No users in system. Please create a user first.")
    return user


@router.get("/marketplace-accounts", response_model=List[MarketplaceAccountResponse])
async def list_marketplace_accounts(db: Session = Depends(get_db)):
    accounts = db.query(MarketplaceAccount).all()
    return accounts


@router.post("/marketplace-accounts", response_model=MarketplaceAccountResponse, status_code=201)
async def create_marketplace_account(account: MarketplaceAccountCreate, db: Session = Depends(get_db)):
    user = get_current_user(db)
    encrypted_key = crypto_service.encrypt(account.api_key)
    db_account = MarketplaceAccount(
        user_id=user.id,
        marketplace=account.marketplace,
        shop_name=account.shop_name,
        api_key_encrypted=encrypted_key,
        is_active=account.is_active
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


@router.get("/marketplace-accounts/{account_id}", response_model=MarketplaceAccountResponse)
async def get_marketplace_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(MarketplaceAccount).filter(MarketplaceAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.put("/marketplace-accounts/{account_id}", response_model=MarketplaceAccountResponse)
async def update_marketplace_account(account_id: int, account: MarketplaceAccountUpdate, db: Session = Depends(get_db)):
    db_account = db.query(MarketplaceAccount).filter(MarketplaceAccount.id == account_id).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    update_data = account.model_dump(exclude_unset=True)
    if "api_key" in update_data:
        update_data["api_key_encrypted"] = crypto_service.encrypt(update_data.pop("api_key"))
    for field, value in update_data.items():
        setattr(db_account, field, value)
    db.commit()
    db.refresh(db_account)
    return db_account


@router.delete("/marketplace-accounts/{account_id}", status_code=204)
async def delete_marketplace_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(MarketplaceAccount).filter(MarketplaceAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    db.delete(account)
    db.commit()
    return None


@router.get("/llm-configs", response_model=List[LLMConfigResponse])
async def list_llm_configs(db: Session = Depends(get_db)):
    configs = db.query(LLMConfig).all()
    return configs


@router.post("/llm-configs", response_model=LLMConfigResponse, status_code=201)
async def create_llm_config(config: LLMConfigCreate, db: Session = Depends(get_db)):
    user = get_current_user(db)
    encrypted_key = crypto_service.encrypt(config.api_key)
    db_config = LLMConfig(
        user_id=user.id,
        provider=config.provider,
        model=config.model,
        api_key_encrypted=encrypted_key,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        is_active=config.is_active
    )
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config


@router.get("/review-rules", response_model=List[ReviewRuleResponse])
async def list_review_rules(db: Session = Depends(get_db)):
    rules = db.query(ReviewRule).order_by(ReviewRule.created_at.desc()).all()
    return rules


@router.post("/review-rules", response_model=ReviewRuleResponse, status_code=201)
async def create_review_rule(rule: ReviewRuleCreate, db: Session = Depends(get_db)):
    """Create new review rule"""
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=400, detail="No users in system")
    db_rule = ReviewRule(user_id=user.id, **rule.model_dump())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule


@router.get("/reviews", response_model=List[ReviewResponse])
async def list_reviews(limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    reviews = db.query(Review).order_by(Review.created_at.desc()).limit(limit).offset(offset).all()
    return reviews


@router.get("/reviews/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: int, db: Session = Depends(get_db)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    from sqlalchemy import func
    total_reviews = db.query(func.count(Review.id)).scalar() or 0
    processed_reviews = db.query(func.count(Review.id)).filter(Review.processed == True).scalar() or 0
    pending_moderation = db.query(func.count(Review.id)).filter(Review.moderation_status == "pending").scalar() or 0
    auto_sent = db.query(func.count(Review.id)).filter(Review.moderation_status == "auto").scalar() or 0
    avg_rating = db.query(func.avg(Review.rating)).scalar() or 0.0
    total_cost = db.query(func.sum(Review.cost_rub)).scalar() or 0.0
    reviews_by_rating = {}
    for rating in range(1, 6):
        count = db.query(func.count(Review.id)).filter(Review.rating == rating).scalar() or 0
        reviews_by_rating[str(rating)] = count
    reviews_by_marketplace = {}
    marketplace_stats = db.query(MarketplaceAccount.marketplace, func.count(Review.id)).join(Review).group_by(MarketplaceAccount.marketplace).all()
    for marketplace, count in marketplace_stats:
        reviews_by_marketplace[marketplace] = count
    return StatsResponse(
        total_reviews=total_reviews,
        processed_reviews=processed_reviews,
        pending_moderation=pending_moderation,
        auto_sent=auto_sent,
        average_rating=float(avg_rating),
        total_cost_rub=float(total_cost),
        reviews_by_rating=reviews_by_rating,
        reviews_by_marketplace=reviews_by_marketplace
    )
