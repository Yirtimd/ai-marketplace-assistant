"""
Mock data generator for Wildberries Sales, Orders and Stocks
"""

from datetime import datetime, timedelta
import random
from typing import List
from ..models.sale import Sale, Order, Stock
from .products import MOCK_PRODUCTS


WAREHOUSE_NAMES = [
    "Коледино",
    "Подольск",
    "Электросталь",
    "Санкт-Петербург",
    "Казань",
    "Екатеринбург",
    "Новосибирск",
]

REGIONS = [
    ("Московская область", "Центральный", "Россия"),
    ("Ленинградская область", "Северо-Западный", "Россия"),
    ("Свердловская область", "Уральский", "Россия"),
    ("Новосибирская область", "Сибирский", "Россия"),
]


def generate_sales(count: int = 200) -> List[Sale]:
    """Generate mock sales"""
    sales = []
    
    for i in range(1, count + 1):
        product = random.choice(MOCK_PRODUCTS)
        size = random.choice(product.sizes)
        
        region = random.choice(REGIONS)
        warehouse = random.choice(WAREHOUSE_NAMES)
        
        sale_date = datetime.now() - timedelta(days=random.randint(0, 90))
        
        discount_percent = random.randint(0, 50)
        total_price = size.price
        price_with_disc = size.discountedPrice
        promo_code_discount = random.randint(0, 500) if random.random() > 0.8 else 0
        
        for_pay = price_with_disc - promo_code_discount
        finished_price = price_with_disc
        
        sale = Sale(
            saleID=f"S{i:010d}",
            orderID=f"O{i:010d}",
            date=sale_date,
            lastChangeDate=sale_date + timedelta(hours=random.randint(1, 24)),
            supplierArticle=product.vendorCode,
            techSize=size.techSize,
            barcode=size.skus[0] if size.skus else f"SKU{i}",
            totalPrice=total_price,
            discountPercent=discount_percent,
            isSupply=True,
            isRealization=False,
            promoCodeDiscount=promo_code_discount,
            warehouseName=warehouse,
            countryName=region[2],
            oblastOkrugName=region[1],
            regionName=region[0],
            incomeID=random.randint(100000, 999999),
            saleId=f"S{i:010d}",
            odid=f"OD{i:010d}",
            subject=product.subjectName,
            category=product.subjectName,
            brand=product.brand,
            nmId=product.nmID,
            sticker=None,
            forPay=for_pay,
            finishedPrice=finished_price,
            priceWithDisc=price_with_disc
        )
        
        sales.append(sale)
    
    return sales


def generate_orders(count: int = 150) -> List[Order]:
    """Generate mock orders"""
    orders = []
    
    for i in range(1, count + 1):
        product = random.choice(MOCK_PRODUCTS)
        size = random.choice(product.sizes)
        
        region = random.choice(REGIONS)
        warehouse = random.choice(WAREHOUSE_NAMES)
        
        order_date = datetime.now() - timedelta(days=random.randint(0, 30))
        is_cancel = random.random() < 0.1
        cancel_date = order_date + timedelta(days=random.randint(1, 5)) if is_cancel else None
        
        discount_percent = random.randint(0, 50)
        total_price = size.price
        
        order = Order(
            orderID=f"O{i:010d}",
            date=order_date,
            lastChangeDate=cancel_date if cancel_date else order_date + timedelta(hours=random.randint(1, 48)),
            supplierArticle=product.vendorCode,
            techSize=size.techSize,
            barcode=size.skus[0] if size.skus else f"SKU{i}",
            totalPrice=total_price,
            discountPercent=discount_percent,
            warehouseName=warehouse,
            oblast=region[0],
            incomeID=random.randint(100000, 999999),
            nmId=product.nmID,
            subject=product.subjectName,
            category=product.subjectName,
            brand=product.brand,
            isCancel=is_cancel,
            cancelDate=cancel_date
        )
        
        orders.append(order)
    
    return orders


def generate_stocks() -> List[Stock]:
    """Generate mock stocks for all products"""
    stocks = []
    
    for product in MOCK_PRODUCTS:
        for size in product.sizes:
            warehouse = random.choice(WAREHOUSE_NAMES)
            quantity = random.randint(0, 100)
            
            stock = Stock(
                lastChangeDate=datetime.now() - timedelta(days=random.randint(0, 7)),
                supplierArticle=product.vendorCode,
                techSize=size.techSize,
                barcode=size.skus[0] if size.skus else f"SKU{product.nmID}",
                quantity=quantity,
                isSupply=True,
                isRealization=False,
                quantityFull=quantity + random.randint(0, 20),
                warehouseName=warehouse,
                nmId=product.nmID,
                subject=product.subjectName,
                category=product.subjectName,
                brand=product.brand,
                SCCode=f"SC{product.nmID}",
                Price=size.price,
                Discount=random.randint(0, 50),
                inWayToClient=random.randint(0, 10),
                inWayFromClient=random.randint(0, 5)
            )
            
            stocks.append(stock)
    
    return stocks


# Generate mock data
MOCK_SALES = generate_sales(200)
MOCK_ORDERS = generate_orders(150)
MOCK_STOCKS = generate_stocks()


def get_sales(date_from: datetime | None = None, date_to: datetime | None = None) -> List[Sale]:
    """Get sales with date filters"""
    sales = MOCK_SALES
    
    if date_from:
        sales = [s for s in sales if s.date >= date_from]
    
    if date_to:
        sales = [s for s in sales if s.date <= date_to]
    
    return sales


def get_orders(date_from: datetime | None = None, date_to: datetime | None = None) -> List[Order]:
    """Get orders with date filters"""
    orders = MOCK_ORDERS
    
    if date_from:
        orders = [o for o in orders if o.date >= date_from]
    
    if date_to:
        orders = [o for o in orders if o.date <= date_to]
    
    return orders


def get_stocks() -> List[Stock]:
    """Get all stocks"""
    return MOCK_STOCKS


def get_stocks_by_nm_id(nm_id: int) -> List[Stock]:
    """Get stocks for specific product"""
    return [s for s in MOCK_STOCKS if s.nmId == nm_id]
