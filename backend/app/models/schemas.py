"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Marketplace Account Schemas
class MarketplaceAccountCreate(BaseModel):
    marketplace: str = Field(..., pattern="^(wildberries|ozon)$")
    api_key: str = Field(..., min_length=10)
    client_id: Optional[str] = None  # For Ozon
    shop_name: str = Field(..., min_length=1)


class MarketplaceAccountResponse(BaseModel):
    id: int
    marketplace: str
    shop_name: str
    is_active: bool
    created_at: datetime
    last_sync: Optional[datetime]

    class Config:
        from_attributes = True


# LLM Config Schemas
class LLMConfigCreate(BaseModel):
    provider: str = Field(..., pattern="^(openai|anthropic|google|gigachat|yandexgpt|perplexity|ollama)$")
    api_key: str = Field(..., min_length=5)
    model: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(default=200, ge=50, le=500)


class LLMConfigResponse(BaseModel):
    id: int
    provider: str
    model: Optional[str]
    temperature: float
    max_tokens: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Review Rule Schemas
class ReviewRuleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    min_rating: int = Field(default=1, ge=1, le=5)
    max_rating: int = Field(default=5, ge=1, le=5)
    keywords_include: Optional[List[str]] = None
    keywords_exclude: Optional[List[str]] = None
    require_moderation: bool = Field(default=True)
    custom_prompt: Optional[str] = None
    tone: str = Field(default="friendly", pattern="^(friendly|professional|apologetic)$")


class ReviewRuleResponse(BaseModel):
    id: int
    name: str
    min_rating: int
    max_rating: int
    keywords_include: Optional[List[str]]
    keywords_exclude: Optional[List[str]]
    require_moderation: bool
    custom_prompt: Optional[str]
    tone: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Review Schemas
class ReviewResponse(BaseModel):
    id: int
    marketplace_account_id: int
    external_id: str
    rating: int
    text: Optional[str]
    product_name: Optional[str]
    customer_name: Optional[str]
    created_at: datetime
    processed: bool
    response_text: Optional[str]
    response_sent: bool
    sent_at: Optional[datetime]
    moderation_status: str
    tokens_used: Optional[int]
    cost_rub: Optional[float]

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
    reviews_by_rating: dict
    reviews_by_marketplace: dict
