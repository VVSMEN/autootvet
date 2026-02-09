"""
Database models using SQLAlchemy
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User account"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, nullable=True, index=True)
    email = Column(String, unique=True, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    marketplace_accounts = relationship("MarketplaceAccount", back_populates="user", cascade="all, delete-orphan")
    llm_configs = relationship("LLMConfig", back_populates="user", cascade="all, delete-orphan")
    review_rules = relationship("ReviewRule", back_populates="user", cascade="all, delete-orphan")


class MarketplaceAccount(Base):
    """Marketplace API connection"""
    __tablename__ = "marketplace_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    marketplace = Column(String, nullable=False)  # "wildberries" | "ozon"
    api_key_encrypted = Column(Text, nullable=False)
    client_id = Column(String, nullable=True)  # For Ozon
    shop_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_sync = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="marketplace_accounts")
    reviews = relationship("Review", back_populates="marketplace_account", cascade="all, delete-orphan")


class LLMConfig(Base):
    """LLM provider configuration"""
    __tablename__ = "llm_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider = Column(String, nullable=False)  # "openai" | "gigachat" | etc
    api_key_encrypted = Column(Text, nullable=False)
    model = Column(String, nullable=True)
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=200)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="llm_configs")


class ReviewRule(Base):
    """Rules for automatic review responses"""
    __tablename__ = "review_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    min_rating = Column(Integer, default=1)
    max_rating = Column(Integer, default=5)
    keywords_include = Column(JSON, nullable=True)  # List of keywords
    keywords_exclude = Column(JSON, nullable=True)  # List of keywords
    require_moderation = Column(Boolean, default=True)
    custom_prompt = Column(Text, nullable=True)
    tone = Column(String, default="friendly")  # "friendly" | "professional" | "apologetic"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="review_rules")


class Review(Base):
    """Review from marketplace"""
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    marketplace_account_id = Column(Integer, ForeignKey("marketplace_accounts.id"), nullable=False)
    external_id = Column(String, nullable=False, index=True)  # ID in WB/Ozon
    rating = Column(Integer, nullable=False)
    text = Column(Text, nullable=True)
    product_name = Column(String, nullable=True)
    product_id = Column(String, nullable=True)
    customer_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    marketplace_created_at = Column(DateTime, nullable=True)
    
    # Processing status
    processed = Column(Boolean, default=False)
    response_text = Column(Text, nullable=True)
    response_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)
    moderation_status = Column(String, default="pending")  # "pending" | "approved" | "rejected" | "auto"
    
    # Cost tracking
    tokens_used = Column(Integer, nullable=True)
    cost_rub = Column(Float, nullable=True)
    
    # Relationships
    marketplace_account = relationship("MarketplaceAccount", back_populates="reviews")
