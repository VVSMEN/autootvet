"""
API endpoints for AutoOtvet
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from loguru import logger

from app.db.database import get_db
from app.db.models import MarketplaceAccount, LLMConfig, ReviewRule, Review
from app.api.schemas import (
    MarketplaceAccountCreate,
    MarketplaceAccountResponse,
    LLMConfigCreate,
    LLMConfigResponse,
    ReviewRuleCreate,
    ReviewRuleResponse,
    ReviewResponse,
    StatsResponse
)
from app.core.security import crypto_service

router = APIRouter()


# Marketplace Accounts Endpoints
@router.post("/marketplace-accounts", response_model=MarketplaceAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_marketplace_account(
    account: MarketplaceAccountCreate,
    db: Session = Depends(get_db)
):
    """Create new marketplace account"""
    # Encrypt API key
    encrypted_key = crypto_service.encrypt(account.api_key)
    
    db_account = MarketplaceAccount(
        marketplace=account.marketplace,
        account_name=account.account_name,
        api_key=encrypted_key,
        is_active=account.is_active
    )
    
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    
    logger.info(f"Created marketplace account: {account.account_name} ({account.marketplace})")
    return db_account


@router.get("/marketplace-accounts", response_model=List[MarketplaceAccountResponse])
async def list_marketplace_accounts(db: Session = Depends(get_db)):
    """List all marketplace accounts"""
    accounts = db.query(MarketplaceAccount).all()
    return accounts


@router.get("/marketplace-accounts/{account_id}", response_model=MarketplaceAccountResponse)
async def get_marketplace_account(account_id: int, db: Session = Depends(get_db)):
    """Get single marketplace account"""
    account = db.query(MarketplaceAccount).filter(MarketplaceAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.delete("/marketplace-accounts/{account_id}")
async def delete_marketplace_account(account_id: int, db: Session = Depends(get_db)):
    """Delete marketplace account"""
    account = db.query(MarketplaceAccount).filter(MarketplaceAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    db.delete(account)
    db.commit()
    
    logger.info(f"Deleted marketplace account: {account.account_name}")
    return {"message": "Account deleted successfully"}


# LLM Config Endpoints
@router.post("/llm-configs", response_model=LLMConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_llm_config(
    config: LLMConfigCreate,
    db: Session = Depends(get_db)
):
    """Create new LLM configuration"""
    # Encrypt API key if provided
    encrypted_key = crypto_service.encrypt(config.api_key) if config.api_key else None
    
    db_config = LLMConfig(
        name=config.name,
        provider=config.provider,
        model_name=config.model_name,
        api_key=encrypted_key,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        is_active=config.is_active
    )
    
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    logger.info(f"Created LLM config: {config.name}")
    return db_config


@router.get("/llm-configs", response_model=List[LLMConfigResponse])
async def list_llm_configs(db: Session = Depends(get_db)):
    """List all LLM configurations"""
    configs = db.query(LLMConfig).all()
    return configs


@router.get("/llm-configs/{config_id}", response_model=LLMConfigResponse)
async def get_llm_config(config_id: int, db: Session = Depends(get_db)):
    """Get single LLM configuration"""
    config = db.query(LLMConfig).filter(LLMConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    return config


@router.delete("/llm-configs/{config_id}")
async def delete_llm_config(config_id: int, db: Session = Depends(get_db)):
    """Delete LLM configuration"""
    config = db.query(LLMConfig).filter(LLMConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    
    db.delete(config)
    db.commit()
    
    logger.info(f"Deleted LLM config: {config.name}")
    return {"message": "Config deleted successfully"}


# Review Rules Endpoints
@router.post("/review-rules", response_model=ReviewRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_review_rule(
    rule: ReviewRuleCreate,
    db: Session = Depends(get_db)
):
    """Create new review rule"""
    db_rule = ReviewRule(
        rating=rule.rating,
        condition_type=rule.condition_type,
        keywords=rule.keywords,
        auto_response_enabled=rule.auto_response_enabled,
        response_template=rule.response_template,
        telegram_notification=rule.telegram_notification,
        priority=rule.priority
    )
    
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    
    logger.info(f"Created review rule for rating {rule.rating}")
    return db_rule


@router.get("/review-rules", response_model=List[ReviewRuleResponse])
async def list_review_rules(db: Session = Depends(get_db)):
    """List all review rules"""
    rules = db.query(ReviewRule).order_by(ReviewRule.priority.desc()).all()
    return rules


@router.get("/review-rules/{rule_id}", response_model=ReviewRuleResponse)
async def get_review_rule(rule_id: int, db: Session = Depends(get_db)):
    """Get single review rule"""
    rule = db.query(ReviewRule).filter(ReviewRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.delete("/review-rules/{rule_id}")
async def delete_review_rule(rule_id: int, db: Session = Depends(get_db)):
    """Delete review rule"""
    rule = db.query(ReviewRule).filter(ReviewRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    db.delete(rule)
    db.commit()
    
    logger.info(f"Deleted review rule {rule_id}")
    return {"message": "Rule deleted successfully"}


# Reviews Endpoints
@router.get("/reviews", response_model=List[ReviewResponse])
async def list_reviews(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get all reviews with pagination"""
    reviews = db.query(Review).order_by(Review.created_at.desc()).limit(limit).offset(offset).all()
    return reviews


@router.get("/reviews/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: int, db: Session = Depends(get_db)):
    """Get single review by ID"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


# Stats Endpoint
@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    """Get statistics"""
    from sqlalchemy import func

    total_reviews = db.query(func.count(Review.id)).scalar() or 0
    processed_reviews = db.query(func.count(Review.id)).filter(Review.processed == True).scalar() or 0
    pending_moderation = db.query(func.count(Review.id)).filter(Review.moderation_status == "pending").scalar() or 0
    auto_sent = db.query(func.count(Review.id)).filter(Review.moderation_status == "auto").scalar() or 0

    avg_rating = db.query(func.avg(Review.rating)).scalar() or 0.0
    total_cost = db.query(func.sum(Review.cost_rub)).scalar() or 0.0

    # Reviews by rating
    reviews_by_rating = {}
    for rating in range(1, 6):
        count = db.query(func.count(Review.id)).filter(Review.rating == rating).scalar() or 0
        reviews_by_rating[str(rating)] = count

    # Reviews by marketplace
    reviews_by_marketplace = {}
    marketplace_stats = db.query(
        MarketplaceAccount.marketplace,
        func.count(Review.id)
    ).join(Review).group_by(MarketplaceAccount.marketplace).all()

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
