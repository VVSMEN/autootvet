"""
Wildberries API Client for fetching and responding to reviews
"""
import httpx
from typing import List, Dict, Optional
from loguru import logger
from datetime import datetime
import asyncio


class WildberriesAPI:
    """Client for Wildberries Seller API"""
    
    BASE_URL = "https://feedbacks-api.wildberries.ru/api/v1"
    RATE_LIMIT_DELAY = 0.34  # 3 requests per second = 0.333s delay
    
    def __init__(self, api_key: str):
        """Initialize Wildberries API client"""
        self.api_key = api_key
        self.headers = {
            "Authorization": api_key
        }
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
    
    async def _rate_limit(self):
        """Apply rate limiting"""
        await asyncio.sleep(self.RATE_LIMIT_DELAY)
    
    async def get_feedbacks(
        self,
        is_answered: bool = False,
        take: int = 5000,
        skip: int = 0
    ) -> List[Dict]:
        """
        Get feedbacks from Wildberries
        
        Args:
            is_answered: Filter by answered status
            take: Number of feedbacks to fetch (max 5000)
            skip: Number of feedbacks to skip
            
        Returns:
            List of feedback objects
        """
        try:
            await self._rate_limit()
            
            params = {
                "isAnswered": is_answered,
                "take": take,
                "skip": skip
            }
            
            response = await self.client.get(
                f"{self.BASE_URL}/feedbacks",
                headers=self.headers,
                params=params
            )
            
            response.raise_for_status()
            data = response.json()
            
            feedbacks = data.get("data", {}).get("feedbacks", [])
            logger.info(f"Fetched {len(feedbacks)} feedbacks from Wildberries")
            
            return feedbacks
            
        except Exception as e:
            logger.error(f"Error fetching Wildberries feedbacks: {e}")
            raise
    
    async def get_unanswered_feedbacks(self) -> List[Dict]:
        """Get all unanswered feedbacks"""
        return await self.get_feedbacks(is_answered=False)
    
    async def send_feedback_answer(
        self,
        feedback_id: str,
        text: str
    ) -> bool:
        """
        Send answer to a feedback
        
        Args:
            feedback_id: ID of the feedback
            text: Response text (2-5000 characters)
            
        Returns:
            True if successful
        """
        try:
            await self._rate_limit()
            
            if len(text) < 2 or len(text) > 5000:
                raise ValueError("Response text must be between 2 and 5000 characters")
            
            payload = {
                "id": feedback_id,
                "text": text
            }
            
            response = await self.client.post(
                f"{self.BASE_URL}/feedbacks/answer",
                headers=self.headers,
                json=payload
            )
            
            response.raise_for_status()
            logger.info(f"Successfully sent answer to feedback {feedback_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending feedback answer: {e}")
            raise
    
    async def test_connection(self) -> bool:
        """Test API connection"""
        try:
            await self.get_feedbacks(take=1)
            return True
        except Exception as e:
            logger.error(f"Wildberries API connection test failed: {e}")
            return False
    
    def parse_feedback(self, feedback: Dict) -> Dict:
        """
        Parse feedback object to standardized format
        
        Args:
            feedback: Raw feedback from API
            
        Returns:
            Standardized feedback dict
        """
        return {
            "external_id": feedback.get("id"),
            "rating": feedback.get("productValuation", 0),
            "text": feedback.get("text", ""),
            "product_name": feedback.get("productDetails", {}).get("productName"),
            "product_id": feedback.get("productDetails", {}).get("nmId"),
            "customer_name": feedback.get("userName"),
            "marketplace_created_at": datetime.fromisoformat(
                feedback.get("createdDate").replace("Z", "+00:00")
            ) if feedback.get("createdDate") else None,
            "is_answered": feedback.get("answer", {}).get("text") is not None
        }
