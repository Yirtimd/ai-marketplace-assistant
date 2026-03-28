"""
Content Agent

Stateless agent for product content generation and SEO optimization.
"""

from typing import Any, Dict, List

from config import get_logger

logger = get_logger(__name__)


class ContentAgent:
    """
    Stateless content agent.

    Responsibilities:
    - Build product descriptions
    - Prepare image/video generation payloads
    - Optimize text for SEO
    """

    def generate_product_description(
        self,
        product_data: Dict[str, Any],
        max_length: int = 700,
    ) -> Dict[str, Any]:
        """
        Generate deterministic product description draft.
        """
        title = product_data.get("title", "Товар")
        category = product_data.get("category", "маркетплейса")
        features = product_data.get("features", [])

        feature_text = "; ".join(str(feature) for feature in features[:5]) if features else "качественные материалы"
        description = (
            f"{title} — практичный выбор в категории {category}. "
            f"Ключевые преимущества: {feature_text}. "
            "Подходит для ежедневного использования и помогает экономить время."
        )
        description = description[:max_length]

        return {
            "title": title,
            "description": description,
            "bullets": [str(feature) for feature in features[:5]],
            "status": "completed",
        }

    def generate_product_images(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare image generation task payload.
        """
        return {
            "task_type": "image_generation",
            "prompt": f"Product photo for {product_data.get('title', 'product')} in clean marketplace style",
            "status": "queued_for_ai_service",
        }

    def generate_product_video(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare short video generation task payload.
        """
        return {
            "task_type": "video_generation",
            "prompt": f"15-second product video for {product_data.get('title', 'product')}",
            "status": "queued_for_ai_service",
        }

    def optimize_seo(
        self,
        title: str,
        description: str,
        keywords: List[str],
    ) -> Dict[str, Any]:
        """
        Apply lightweight SEO improvements.
        """
        clean_keywords = [keyword.strip() for keyword in keywords if keyword and keyword.strip()]

        seo_title = title
        if clean_keywords and clean_keywords[0].lower() not in seo_title.lower():
            seo_title = f"{title} | {clean_keywords[0]}"

        seo_description = description
        for keyword in clean_keywords[:3]:
            if keyword.lower() not in seo_description.lower():
                seo_description += f" {keyword}."

        logger.info("ContentAgent generated SEO payload with %s keywords", len(clean_keywords))

        return {
            "seo_title": seo_title[:120],
            "seo_description": seo_description[:1000],
            "keywords_used": clean_keywords[:10],
            "status": "completed",
        }
