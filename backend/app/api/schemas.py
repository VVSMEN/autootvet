"""
Pydantic schemas for API requests/responses
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime


# Marketplace Account Schemas
class MarketplaceAccountCreate(BaseModel):
    marketplace: str = Field(..., description="Marketplace name (wildberries, ozon, yandex)")
    account_name: str = Field(..., description="Account display name")
    api_key: str = Field(..., description="API key for marketplace")
    is_active: bool = Field(default=True)


class MarketplaceAccountResponse(BaseModel):
    id: int
    marketplace: str
    account_name: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# LLM Config Schemas
class LLMConfigCreate(BaseModel):
    name: str = Field(..., description="Configuration name")
    provider: str = Field(..., description="LLM provider (openai, anthropic, etc)")
    model_name: str = Field(..., description="Model name")
    api_key: Optional[str] = Field(None, description="API key for LLM provider")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=500, ge=1)
    is_active: bool = Field(default=True)


class LLMConfigResponse(BaseModel):
    id: int
    name: str
    provider: str
    model_name: str
    temperature: float
    max_tokens: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Review Rule Schemas
class ReviewRuleCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating (1-5)")
    condition_type: str = Field(..., description="Condition type (contains, not_contains, equals)")
    keywords: Optional[str] = Field(None, description="Keywords for condition (comma-separated)")
    auto_response_enabled: bool = Field(default=False)
    response_template: Optional[str] = Field(None, description="Template for auto-response")
    telegram_notification: bool = Field(default=True)
    priority: int = Field(default=0, description="Rule priority (higher = processed first)")


class ReviewRuleResponse(BaseModel):
    id: int
    rating: int
    condition_type: str
    keywords: Optional[str]
    auto_response_enabled: bool
    response_template: Optional[str]
    telegram_notification: bool
    priority: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Review Schemas
class ReviewResponse(BaseModel):
    id: int
    marketplace_account_id: int
    external_id: str
    rating: int
    review_text: Optional[str]
    reviewer_name: Optional[str]
    product_name: Optional[str]
    response_text: Optional[str]
    processed: bool
    moderation_status: str
    llm_used: Optional[str]
    cost_rub: Optional[float]
    created_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Stats Schema
class StatsResponse(BaseModel):
    total_reviews: int
    processed_reviews: int
    pending_moderation: int
    auto_sent: int
    average_rating: float
    total_cost_rub: float
    reviews_by_rating: Dict[str, int]
    reviews_by_marketplace: Dict[str, int]
