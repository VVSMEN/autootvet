"""
LLM Service for generating review responses using multiple providers
"""
from typing import Optional, Dict
from litellm import completion
from loguru import logger
from app.core.config import settings


class LLMService:
    """Service for interacting with various LLM providers"""
    
    # Model mapping for different providers
    PROVIDER_MODELS = {
        "openai": "gpt-4o-mini",
        "anthropic": "claude-3-5-haiku-20241022",
        "google": "gemini/gemini-2.0-flash-exp",
        "gigachat": "gigachat/GigaChat",
        "yandexgpt": "yandex/yandexgpt-lite",
        "perplexity": "perplexity/sonar",
        "ollama": "ollama/llama2"
    }
    
    # Cost per 1M tokens (input, output) in RUB
    PROVIDER_COSTS = {
        "openai": (15.0, 60.0),  # $0.15/$0.6 * 100 RUB
        "anthropic": (25.0, 125.0),  # $0.25/$1.25 * 100 RUB
        "google": (7.5, 30.0),  # $0.075/$0.3 * 100 RUB
        "gigachat": (160.0, 96.0),  # GigaChat Lite
        "yandexgpt": (200.0, 120.0),  # YandexGPT 3 Lite
        "perplexity": (20.0, 20.0),  # Perplexity Sonar $0.2/$0.2 * 100 RUB
        "ollama": (0.0, 0.0)  # Free local
    }
    
    def __init__(self, provider: Optional[str] = None):
        """Initialize LLM service with provider"""
        self.provider = provider or settings.LLM_PROVIDER
        self.model = self._get_model()
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS
        
    def _get_model(self) -> str:
        """Get model name for current provider"""
        if settings.LLM_MODEL:
            return settings.LLM_MODEL
        return self.PROVIDER_MODELS.get(self.provider, "gpt-4o-mini")
    
    def generate_response(
        self,
        review_text: str,
        rating: int,
        product_name: str,
        custom_prompt: Optional[str] = None,
        tone: str = "friendly",
        customer_name: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Generate response to a review
        
        Args:
            review_text: Text of the review
            rating: Rating (1-5 stars)
            product_name: Name of the product
            custom_prompt: Additional instructions
            tone: Tone of response (friendly/professional/apologetic)
            customer_name: Name of customer (if available)
            
        Returns:
            Dict with response_text, tokens_used, cost_rub
        """
        try:
            # Build system prompt
            system_prompt = self._build_system_prompt(tone)
            
            # Build user prompt
            user_prompt = self._build_user_prompt(
                review_text=review_text,
                rating=rating,
                product_name=product_name,
                custom_prompt=custom_prompt,
                customer_name=customer_name
            )
            
            logger.info(f"Generating response using {self.provider} ({self.model})")
            
            # Call LLM
            response = completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            response_text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            cost_rub = self._calculate_cost(
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens
            )
            
            logger.info(f"Generated response: {len(response_text)} chars, {tokens_used} tokens, {cost_rub:.2f} RUB")
            
            return {
                "response_text": response_text,
                "tokens_used": tokens_used,
                "cost_rub": cost_rub
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    def _build_system_prompt(self, tone: str) -> str:
        """Build system prompt based on tone"""
        base_prompt = """Ты менеджер магазина на маркетплейсе. 
Твоя задача — вежливо и профессионально ответить на отзыв покупателя.

Правила ответа:
- Отвечай кратко (до 200 символов)
- Используй эмодзи умеренно (1-2 максимум)
- Благодари за покупку
- На негативные отзывы извиняйся и предлагай решение
- На позитивные отзывы выражай благодарность
"""
        
        tone_additions = {
            "friendly": "\nТон: дружелюбный и теплый, как общение с другом.",
            "professional": "\nТон: профессиональный и деловой, без лишних эмоций.",
            "apologetic": "\nТон: извиняющийся, предлагающий решение проблемы."
        }
        
        return base_prompt + tone_additions.get(tone, tone_additions["friendly"])
    
    def _build_user_prompt(
        self,
        review_text: str,
        rating: int,
        product_name: str,
        custom_prompt: Optional[str],
        customer_name: Optional[str]
    ) -> str:
        """Build user prompt with review details"""
        prompt = f"""Товар: {product_name}
Рейтинг: {rating}/5 звёзд
"""
        
        if customer_name:
            prompt += f"Покупатель: {customer_name}\n"
        
        prompt += f"\nОтзыв покупателя:\n{review_text}\n"
        
        if custom_prompt:
            prompt += f"\nДополнительные инструкции:\n{custom_prompt}\n"
        
        prompt += "\nСгенерируй ответ на этот отзыв:"
        
        return prompt
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost in RUB based on token usage"""
        if self.provider not in self.PROVIDER_COSTS:
            return 0.0
        
        input_cost_per_1m, output_cost_per_1m = self.PROVIDER_COSTS[self.provider]
        
        input_cost = (input_tokens / 1_000_000) * input_cost_per_1m
        output_cost = (output_tokens / 1_000_000) * output_cost_per_1m
        
        return input_cost + output_cost
    
    def test_connection(self) -> bool:
        """Test if LLM provider is accessible"""
        try:
            response = completion(
                model=self.model,
                messages=[{"role": "user", "content": "Привет! Ответь одним словом: ОК"}],
                max_tokens=10
            )
            return bool(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"LLM connection test failed: {e}")
            return False


# Global instance
llm_service = LLMService()
