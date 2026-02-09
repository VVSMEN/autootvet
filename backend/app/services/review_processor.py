"""
Review Processor - main business logic for processing reviews
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from loguru import logger
from datetime import datetime

from app.db.models import MarketplaceAccount, Review, ReviewRule, User
from app.services.wildberries_api import WildberriesAPI
from app.services.ozon_api import OzonAPI
from app.services.llm_service import LLMService
from app.core.config import settings


class ReviewProcessor:
    """Main processor for fetching and responding to reviews"""
    
    def __init__(self, db: Session):
        """Initialize review processor"""
        self.db = db
        self.llm_service = LLMService()
    
    async def process_all_accounts(self):
        """Process reviews for all active marketplace accounts"""
        accounts = self.db.query(MarketplaceAccount).filter(
            MarketplaceAccount.is_active == True
        ).all()
        
        logger.info(f"Processing {len(accounts)} active marketplace accounts")
        
        for account in accounts:
            try:
                await self.process_account(account)
            except Exception as e:
                logger.error(f"Error processing account {account.id}: {e}")
    
    async def process_account(self, account: MarketplaceAccount):
        """
        Process reviews for a single marketplace account
        
        Args:
            account: MarketplaceAccount instance
        """
        logger.info(f"Processing account: {account.shop_name} ({account.marketplace})")
        
        # Fetch new reviews
        new_reviews = await self._fetch_new_reviews(account)
        
        if not new_reviews:
            logger.info(f"No new reviews for {account.shop_name}")
            return
        
        logger.info(f"Found {len(new_reviews)} new reviews")
        
        # Get user's review rules
        rules = self.db.query(ReviewRule).filter(
            ReviewRule.user_id == account.user_id,
            ReviewRule.is_active == True
        ).first()
        
        if not rules:
            logger.warning(f"No active rules found for user {account.user_id}")
            return
        
        # Process each review
        for review_data in new_reviews:
            try:
                await self._process_single_review(account, review_data, rules)
            except Exception as e:
                logger.error(f"Error processing review: {e}")
    
    async def _fetch_new_reviews(self, account: MarketplaceAccount) -> List[Dict]:
        """
        Fetch new unanswered reviews from marketplace
        
        Args:
            account: MarketplaceAccount instance
            
        Returns:
            List of new review data
        """
        # Decrypt API key (we'll implement encryption later)
        api_key = account.api_key_encrypted  # TODO: decrypt
        
        if account.marketplace == "wildberries":
            api = WildberriesAPI(api_key)
            try:
                raw_reviews = await api.get_unanswered_feedbacks()
                reviews = [api.parse_feedback(r) for r in raw_reviews]
            finally:
                await api.close()
                
        elif account.marketplace == "ozon":
            client_id = account.client_id
            api = OzonAPI(client_id, api_key)
            try:
                raw_reviews = await api.get_unanswered_reviews()
                reviews = [api.parse_review(r) for r in raw_reviews]
            finally:
                await api.close()
        else:
            logger.error(f"Unknown marketplace: {account.marketplace}")
            return []
        
        # Filter out already processed reviews
        existing_ids = {r.external_id for r in self.db.query(Review.external_id).filter(
            Review.marketplace_account_id == account.id
        ).all()}
        
        new_reviews = [r for r in reviews if r["external_id"] not in existing_ids]
        
        # Update last sync time
        account.last_sync = datetime.utcnow()
        self.db.commit()
        
        return new_reviews
    
    async def _process_single_review(
        self,
        account: MarketplaceAccount,
        review_ Dict,
        rules: ReviewRule
    ):
        """
        Process a single review
        
        Args:
            account: MarketplaceAccount instance
            review_ Parsed review data
            rules: ReviewRule instance
        """
        # Create review record
        review = Review(
            marketplace_account_id=account.id,
            external_id=review_data["external_id"],
            rating=review_data["rating"],
            text=review_data["text"],
            product_name=review_data["product_name"],
            product_id=review_data["product_id"],
            customer_name=review_data["customer_name"],
            marketplace_created_at=review_data["marketplace_created_at"]
        )
        self.db.add(review)
        self.db.commit()
        
        logger.info(f"Created review record: {review.id} (rating: {review.rating})")
        
        # Check if review should be processed
        if not self._should_process_review(review, rules):
            logger.info(f"Review {review.id} doesn't match rules, skipping")
            return
        
        # Generate response using LLM
        try:
            response_data = self.llm_service.generate_response(
                review_text=review.text or "Без текста",
                rating=review.rating,
                product_name=review.product_name or "товар",
                custom_prompt=rules.custom_prompt,
                tone=rules.tone,
                customer_name=review.customer_name
            )
            
            review.response_text = response_data["response_text"]
            review.tokens_used = response_data["tokens_used"]
            review.cost_rub = response_data["cost_rub"]
            review.processed = True
            
            # Determine moderation status
            if rules.require_moderation or review.rating <= 3:
                review.moderation_status = "pending"
                logger.info(f"Review {review.id} sent for moderation")
                # TODO: Send to Telegram for moderation
            else:
                review.moderation_status = "auto"
                if settings.AUTO_SEND_RESPONSES:
                    await self._send_response(account, review)
                    logger.info(f"Review {review.id} auto-sent")
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error generating response for review {review.id}: {e}")
            raise
    
    def _should_process_review(self, review: Review, rules: ReviewRule) -> bool:
        """
        Check if review matches processing rules
        
        Args:
            review: Review instance
            rules: ReviewRule instance
            
        Returns:
            True if review should be processed
        """
        # Check rating range
        if not (rules.min_rating <= review.rating <= rules.max_rating):
            logger.debug(f"Review rating {review.rating} outside range {rules.min_rating}-{rules.max_rating}")
            return False
        
        review_text = (review.text or "").lower()
        
        # Check include keywords
        if rules.keywords_include:
            if not any(kw.lower() in review_text for kw in rules.keywords_include):
                logger.debug(f"Review doesn't contain required keywords")
                return False
        
        # Check exclude keywords
        if rules.keywords_exclude:
            if any(kw.lower() in review_text for kw in rules.keywords_exclude):
                logger.debug(f"Review contains excluded keywords")
                return False
        
        return True
    
    async def _send_response(self, account: MarketplaceAccount, review: Review):
        """
        Send response to marketplace
        
        Args:
            account: MarketplaceAccount instance
            review: Review instance with response_text
        """
        api_key = account.api_key_encrypted  # TODO: decrypt
        
        try:
            if account.marketplace == "wildberries":
                api = WildberriesAPI(api_key)
                try:
                    await api.send_feedback_answer(review.external_id, review.response_text)
                finally:
                    await api.close()
                    
            elif account.marketplace == "ozon":
                client_id = account.client_id
                api = OzonAPI(client_id, api_key)
                try:
                    await api.send_review_answer(int(review.external_id), review.response_text)
                finally:
                    await api.close()
            
            review.response_sent = True
            review.sent_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Response sent for review {review.id}")
            
        except Exception as e:
            logger.error(f"Error sending response for review {review.id}: {e}")
            raise
