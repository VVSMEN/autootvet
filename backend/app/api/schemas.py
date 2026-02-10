"""
Pydantic schemas for API
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


# Marketplace Account Schemas
class MarketplaceAccountBase(BaseModel):
    marketplace: str = Field(..., description="Marketplace name (wildberries, ozon, yandex)")
    shop_name: str = Field(..., description="Shop name")
    api_key: str = Field(..., description="API key for marketplace")
    is_active: bool = Field(default=True, description="Is account active")


class MarketplaceAccountCreate(MarketplaceAccountBase):
    pass


class MarketplaceAccountUpdate(BaseModel):
    marketplace: Optional[str] = None
    shop_name: Optional[str] = None
    api_key: Optional[str] = None
    is_active: Optional[bool] = None


class MarketplaceAccountResponse(BaseModel):
    id: int
    marketplace: str
    shop_name: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# LLM Config Schemas
class LLMConfigBase(BaseModel):
    provider: str = Field(..., description="LLM provider (openai, anthropic, etc)")
    model: str = Field(..., description="Model name")
    api_key: str = Field(..., description="API key for LLM provider")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=500, ge=1, le=4000)
    is_active: bool = Field(default=True)


class LLMConfigCreate(LLMConfigBase):
    pass


class LLMConfigUpdate(BaseModel):
    provider: Optional[str] = None
    model: Optional[str] = None
    api_key: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    is_active: Optional[bool] = None


class LLMConfigResponse(BaseModel):
    id: int
    provider: str
    model: str
    temperature: float
    max_tokens: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Review Rule Schemas (обновлено под реальную модель БД)
class ReviewRuleBase(BaseModel):
    name: str = Field(..., description="Rule name")
    min_rating: int = Field(default=1, ge=1, le=5)
    max_rating: int = Field(default=5, ge=1, le=5)
    keywords_include: Optional[List[str]] = Field(default=None, description="Keywords to include")
    keywords_exclude: Optional[List[str]] = Field(default=None, description="Keywords to exclude")
    require_moderation: bool = Field(default=True)
    custom_prompt: Optional[str] = Field(default=None, description="Custom prompt for LLM")
    tone: str = Field(default="friendly", description="Response tone: friendly, professional, apologetic")
    is_active: bool = Field(default=True)


class ReviewRuleCreate(ReviewRuleBase):
    pass


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
    review_id: str
    rating: int
    review_text: str
    customer_name: Optional[str] = None
    product_name: Optional[str] = None
    generated_response: Optional[str] = None
    moderation_status: str
    processed: bool
    cost_rub: float
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
    reviews_by_rating: dict
    reviews_by_marketplace: dict
