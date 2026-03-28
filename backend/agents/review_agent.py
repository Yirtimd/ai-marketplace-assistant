"""
Review Agent

Stateless agent for review sentiment analysis and reply drafting.
"""

from typing import Any, Dict, Optional

from config import get_logger

logger = get_logger(__name__)


class ReviewAgent:
    """
    Stateless review agent.

    Responsibilities:
    - Analyze sentiment
    - Generate reply draft
    - Prepare publish payload
    """

    def analyze_sentiment(self, review_text: str, rating: Optional[int] = None) -> Dict[str, Any]:
        """
        Analyze review sentiment using lightweight rules.
        """
        text = (review_text or "").lower()

        negative_markers = ["плохо", "ужас", "брак", "возврат", "не рекомендую", "bad", "broken"]
        positive_markers = ["отлично", "класс", "супер", "рекомендую", "good", "perfect"]

        negative_score = sum(1 for marker in negative_markers if marker in text)
        positive_score = sum(1 for marker in positive_markers if marker in text)

        if rating is not None:
            if rating <= 2:
                negative_score += 2
            elif rating >= 4:
                positive_score += 2

        if negative_score > positive_score:
            sentiment = "negative"
        elif positive_score > negative_score:
            sentiment = "positive"
        else:
            sentiment = "neutral"

        return {
            "sentiment": sentiment,
            "negative_score": negative_score,
            "positive_score": positive_score,
            "rating": rating,
            "status": "completed",
        }

    def generate_reply(
        self,
        review_text: str,
        sentiment: str,
        product_name: Optional[str] = None,
        shop_name: str = "Команда магазина",
    ) -> str:
        """
        Generate customer-friendly reply template.
        """
        item_part = f" по товару {product_name}" if product_name else ""

        if sentiment == "negative":
            return (
                f"Спасибо за отзыв{item_part}. Нам очень жаль, что у вас возникла проблема. "
                "Пожалуйста, напишите нам в личные сообщения с номером заказа — поможем решить вопрос "
                f"как можно быстрее. С уважением, {shop_name}."
            )

        if sentiment == "positive":
            return (
                f"Спасибо за ваш отзыв{item_part}! Очень рады, что вы остались довольны покупкой. "
                f"Будем рады видеть вас снова. С уважением, {shop_name}."
            )

        return (
            f"Спасибо за обратную связь{item_part}. Мы ценим ваше мнение и используем его "
            f"для улучшения сервиса. С уважением, {shop_name}."
        )

    def publish_reply(self, review_id: int, reply_text: str) -> Dict[str, Any]:
        """
        Prepare publish payload for external API/service layer.

        In Stage 6 this method does not call external APIs directly.
        """
        logger.info("ReviewAgent prepared reply for review_id=%s", review_id)
        return {
            "review_id": review_id,
            "reply_text": reply_text,
            "status": "ready_to_publish",
        }
