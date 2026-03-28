"""
Mock data generator for Wildberries Products
"""

from datetime import datetime, timedelta
import random
from typing import List
from ..models.product import (
    Product, Size, Photo, Characteristic,
    Category, Subject, Brand, SubjectCharacteristic,
    CharacteristicOption
)


# Brands
BRANDS = [
    Brand(id=1, name="Adidas"),
    Brand(id=2, name="Nike"),
    Brand(id=3, name="Puma"),
    Brand(id=4, name="Reebok"),
    Brand(id=5, name="New Balance"),
    Brand(id=6, name="Samsung"),
    Brand(id=7, name="Apple"),
    Brand(id=8, name="Xiaomi"),
    Brand(id=9, name="Sony"),
    Brand(id=10, name="LG"),
]


# Categories
CATEGORIES = [
    Category(id=1, name="Одежда", parentID=None),
    Category(id=2, name="Обувь", parentID=None),
    Category(id=3, name="Электроника", parentID=None),
    Category(id=4, name="Мужская одежда", parentID=1),
    Category(id=5, name="Женская одежда", parentID=1),
    Category(id=6, name="Мужская обувь", parentID=2),
    Category(id=7, name="Женская обувь", parentID=2),
]


# Subjects
SUBJECTS = [
    Subject(id=101, name="Кроссовки", parentID=2, parentName="Обувь"),
    Subject(id=102, name="Футболки", parentID=1, parentName="Одежда"),
    Subject(id=103, name="Джинсы", parentID=1, parentName="Одежда"),
    Subject(id=104, name="Смартфоны", parentID=3, parentName="Электроника"),
    Subject(id=105, name="Куртки", parentID=1, parentName="Одежда"),
    Subject(id=106, name="Платья", parentID=1, parentName="Одежда"),
    Subject(id=107, name="Ботинки", parentID=2, parentName="Обувь"),
]


# Subject characteristics
SUBJECT_CHARACTERISTICS = {
    101: [  # Кроссовки
        SubjectCharacteristic(
            id=1, name="Цвет", required=True, maxCount=1,
            options=[
                CharacteristicOption(id=1, name="Черный"),
                CharacteristicOption(id=2, name="Белый"),
                CharacteristicOption(id=3, name="Синий"),
                CharacteristicOption(id=4, name="Красный"),
            ]
        ),
        SubjectCharacteristic(
            id=2, name="Материал верха", required=True, maxCount=1,
            options=[
                CharacteristicOption(id=10, name="Текстиль"),
                CharacteristicOption(id=11, name="Натуральная кожа"),
                CharacteristicOption(id=12, name="Искусственная кожа"),
            ]
        ),
        SubjectCharacteristic(
            id=3, name="Пол", required=True, maxCount=1,
            options=[
                CharacteristicOption(id=20, name="Мужской"),
                CharacteristicOption(id=21, name="Женский"),
                CharacteristicOption(id=22, name="Унисекс"),
            ]
        ),
    ],
    102: [  # Футболки
        SubjectCharacteristic(
            id=4, name="Цвет", required=True, maxCount=1,
            options=[
                CharacteristicOption(id=1, name="Черный"),
                CharacteristicOption(id=2, name="Белый"),
                CharacteristicOption(id=5, name="Серый"),
            ]
        ),
        SubjectCharacteristic(
            id=5, name="Состав", required=True, maxCount=3,
            options=[
                CharacteristicOption(id=30, name="Хлопок"),
                CharacteristicOption(id=31, name="Полиэстер"),
                CharacteristicOption(id=32, name="Эластан"),
            ]
        ),
    ],
}


def generate_products(count: int = 50) -> List[Product]:
    """Generate mock products"""
    products = []
    
    for i in range(1, count + 1):
        subject = random.choice(SUBJECTS)
        brand = random.choice(BRANDS)
        
        # Generate sizes
        if subject.id == 101:  # Кроссовки
            size_values = ["38", "39", "40", "41", "42", "43", "44"]
        elif subject.id == 102:  # Футболки
            size_values = ["S", "M", "L", "XL", "XXL"]
        else:
            size_values = ["S", "M", "L", "XL"]
        
        base_price = random.randint(1000, 10000)
        discount = random.randint(0, 50)
        
        sizes = [
            Size(
                techSize=size,
                wbSize=size,
                price=base_price,
                discountedPrice=int(base_price * (100 - discount) / 100),
                skus=[f"SKU{i}{j}" for j in range(1, 3)]
            )
            for j, size in enumerate(size_values, 1)
        ]
        
        # Generate photos
        photos = [
            Photo(
                big=f"https://basket-01.wbbasket.ru/vol{i}/part{i}/images/big/{i}.jpg",
                small=f"https://basket-01.wbbasket.ru/vol{i}/part{i}/images/c246x328/{i}.jpg"
            )
            for _ in range(random.randint(2, 5))
        ]
        
        # Generate characteristics
        characteristics = [
            Characteristic(name="Цвет", value=random.choice(["Черный", "Белый", "Синий", "Красный"])),
            Characteristic(name="Бренд", value=brand.name),
            Characteristic(name="Страна производства", value=random.choice(["Китай", "Россия", "Турция"])),
        ]
        
        product = Product(
            nmID=10000 + i,
            imtID=20000 + i,
            nmUUID=f"uuid-{i:05d}",
            subjectID=subject.id,
            subjectName=subject.name,
            vendorCode=f"ART{i:05d}",
            brand=brand.name,
            title=f"{brand.name} {subject.name} {i}",
            description=f"Качественный {subject.name.lower()} от бренда {brand.name}. "
                        f"Отличное качество, современный дизайн. Размеры в наличии.",
            video=f"https://video.wildberries.ru/{i}.mp4" if random.random() > 0.7 else None,
            sizes=sizes,
            photos=photos,
            characteristics=characteristics,
            createdAt=datetime.now() - timedelta(days=random.randint(1, 365)),
            updatedAt=datetime.now() - timedelta(days=random.randint(0, 30))
        )
        
        products.append(product)
    
    return products


# Generate mock products
MOCK_PRODUCTS = generate_products(50)


def get_products(limit: int = 100, offset: int = 0) -> List[Product]:
    """Get products with pagination"""
    return MOCK_PRODUCTS[offset:offset + limit]


def get_product_by_id(nm_id: int) -> Product | None:
    """Get product by nmID"""
    for product in MOCK_PRODUCTS:
        if product.nmID == nm_id:
            return product
    return None


def get_product_by_vendor_code(vendor_code: str) -> Product | None:
    """Get product by vendor code"""
    for product in MOCK_PRODUCTS:
        if product.vendorCode == vendor_code:
            return product
    return None
