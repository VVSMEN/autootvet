"""
Ozon Seller API Client for fetching and responding to reviews
"""
import httpx
from typing import List, Dict, Optional
from loguru import logger
from datetime import datetime


class OzonAPI:
    """Client for Ozon Seller API"""
    
    BASE_URL = "https://api-seller.ozon.ru"
    
    def __init__(self, client_id: str, api_key: str):
        """Initialize Ozon API client"""
        self.client_id = client_id
        self.api_key = api_key
        self.headers = {
            "Client-Id": client_id,
            "Api-Key": api_key,
            "Content-Type": "application/json"
        }
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
    
    async def get_reviews(
        self,
        limit: int = 100,
        offset: int = 0,
        with_answer: Optional[bool] = None
    ) -> List[Dict]:
        """
        Get product reviews from Ozon
        
        Args:
            limit: Number of reviews to fetch (max 1000)
            offset: Offset for pagination
            with_answer: Filter by answer status (True/False/None)
            
        Returns:
            List of review objects
        """
        try:
            payload = {
                "limit": limit,
                "offset": offset
            }
            
            if with_answer is not None:
                payload["with_answer"] = with_answer
            
            response = await self.client.post(
                f"{self.BASE_URL}/v1/product/review/list",
                headers=self.headers,
                json=payload
            )
            
            response.raise_for_status()
            data = response.json()
            
            reviews = data.get("result", {}).get("reviews", [])
            logger.info(f"Fetched {len(reviews)} reviews from Ozon")
            
            return reviews
            
        except Exception as e:
            logger.error(f"Error fetching Ozon reviews: {e}")
            raise
    
    async def get_unanswered_reviews(self) -> List[Dict]:
        """Get all unanswered reviews"""
        return await self.get_reviews(with_answer=False)
    
    async def send_review_answer(
        self,
        review_id: int,
        text: str
    ) -> bool:
        """
        Send answer to a review
        
        Args:
            review_id: ID of the review
            text: Response text
            
        Returns:
            True if successful
        """
        try:
            payload = {
                "review_id": review_id,
                "text": text
            }
            
            response = await self.client.post(
                f"{self.BASE_URL}/v1/product/review/answer",
                headers=self.headers,
                json=payload
            )
            
            response.raise_for_status()
            logger.info(f"Successfully sent answer to Ozon review {review_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending Ozon review answer: {e}")
            raise
    
    async def test_connection(self) -> bool:
        """Test API connection"""
        try:
            await self.get_reviews(limit=1)
            return True
        except Exception as e:
            logger.error(f"Ozon API connection test failed: {e}")
            return False
    
    def parse_review(self, review: Dict) -> Dict:
        """
        Parse review object to standardized format
        
        Args:
            review: Raw review from API
            
        Returns:
            Standardized review dict
        """
        return {
            "external_id": str(review.get("id")),
            "rating": review.get("rating", 0),
            "text": review.get("text", ""),
            "product_name": review.get("product_name"),
            "product_id": str(review.get("product_id")),
            "customer_name": review.get("user", {}).get("name"),
            "marketplace_created_at": datetime.fromisoformat(
                review.get("created_at").replace("Z", "+00:00")
            ) if review.get("created_at") else None,
            "is_answered": bool(review.get("answer"))
        }
