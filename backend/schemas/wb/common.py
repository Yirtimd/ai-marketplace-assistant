"""
Common schemas for Wildberries API
"""

from pydantic import BaseModel


class Category(BaseModel):
    """Product category"""
    id: int
    name: str
    parentId: int = 0


class Subject(BaseModel):
    """Product subject (предмет)"""
    id: int
    name: str
    parentId: int
    isVisible: bool = True


class Brand(BaseModel):
    """Brand"""
    id: int
    name: str
