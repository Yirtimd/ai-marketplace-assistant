"""
Wildberries response normalizer.

Provides a single adapter layer for mock/real WB payload differences.
"""

from typing import Any, Dict, List, Optional


def _extract_list(response: Dict[str, Any], keys: List[str]) -> List[Dict[str, Any]]:
    """Return first list payload found by candidate keys."""
    for key in keys:
        value = response.get(key)
        if isinstance(value, list):
            return value
    return []


def _pick(source: Dict[str, Any], keys: List[str], default: Any = None) -> Any:
    """Return first non-None value by alias keys."""
    for key in keys:
        if key in source and source[key] is not None:
            return source[key]
    return default


def extract_products(response: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Normalize products list from WB response."""
    return _extract_list(response, ["cards", "data", "products", "items"])


def extract_sales(response: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Normalize sales list from WB response."""
    return _extract_list(response, ["data", "sales", "items", "results"])


def extract_feedbacks(response: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Normalize feedbacks list from WB response."""
    return _extract_list(response, ["data", "feedbacks", "items", "results"])


def normalize_sale_record(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Map a raw sale record to canonical internal keys."""
    return {
        "sale_id": _pick(raw, ["saleID", "saleId", "id"]),
        "order_id": _pick(raw, ["orderID", "orderId"]),
        "nm_id": _pick(raw, ["nmID", "nmId"]),
        "vendor_code": _pick(raw, ["vendorCode"]),
        "sale_date": _pick(raw, ["date", "saleDate", "createdAt"]),
        "quantity": _pick(raw, ["quantity"], 0),
        "price": _pick(raw, ["price"], 0),
        "discount": _pick(raw, ["discount", "discountPercent"], 0),
        "total_price": _pick(raw, ["totalPrice", "finishedPrice", "priceWithDisc"], 0),
        "warehouse_name": _pick(raw, ["warehouseName"]),
        "oblast": _pick(raw, ["oblast", "oblastOkrugName"]),
        "region": _pick(raw, ["region", "regionName"]),
    }


def normalize_feedback_record(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Map a raw feedback record to canonical internal keys."""
    answer_payload = raw.get("answer") or {}
    return {
        "feedback_id": _pick(raw, ["id", "feedbackId"]),
        "nm_id": _pick(raw, ["nmId", "nmID"]),
        "text": _pick(raw, ["text"], ""),
        "rating": _pick(raw, ["rating", "productValuation"]),
        "user_name": _pick(raw, ["userName"], "Покупатель"),
        "created_date": _pick(raw, ["createdAt", "createdDate"]),
        "is_answered": bool(_pick(raw, ["isAnswered"], False)),
        "answer_text": _pick(answer_payload, ["text"]),
        "answered_at": _pick(answer_payload, ["createdAt", "createdDate"]),
    }

