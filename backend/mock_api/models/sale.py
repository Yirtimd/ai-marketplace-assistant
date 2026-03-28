"""
Pydantic models for Wildberries Sales and Reports API
"""

from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel, Field


class Sale(BaseModel):
    """Sale model"""
    saleID: str = Field(..., description="Sale ID")
    orderID: str = Field(..., description="Order ID") 
    date: datetime = Field(..., description="Sale date")
    lastChangeDate: datetime = Field(..., description="Last change date")
    supplierArticle: str = Field(..., description="Supplier article")
    techSize: str = Field(..., description="Technical size")
    barcode: str = Field(..., description="Barcode")
    totalPrice: float = Field(..., description="Total price")
    discountPercent: int = Field(..., description="Discount percent")
    isSupply: bool = Field(..., description="Is supply")
    isRealization: bool = Field(..., description="Is realization")
    promoCodeDiscount: float = Field(0, description="Promo code discount")
    warehouseName: str = Field(..., description="Warehouse name")
    countryName: str = Field(..., description="Country name")
    oblastOkrugName: str = Field(..., description="Oblast name")
    regionName: str = Field(..., description="Region name")
    incomeID: int = Field(..., description="Income ID")
    saleId: str = Field(..., description="Sale ID (old)")
    odid: str = Field(..., description="Order delivery ID")
    subject: str = Field(..., description="Subject")
    category: str = Field(..., description="Category")
    brand: str = Field(..., description="Brand")
    nmId: int = Field(..., description="Nomenclature ID")
    sticker: Optional[str] = Field(None, description="Sticker")
    forPay: float = Field(..., description="For pay")
    finishedPrice: float = Field(..., description="Finished price")
    priceWithDisc: float = Field(..., description="Price with discount")


class SalesReportResponse(BaseModel):
    """Response for sales report"""
    sales: List[Sale] = Field(default_factory=list, description="Sales list")
    total: int = Field(0, description="Total count")


class Order(BaseModel):
    """Order model"""
    orderID: str = Field(..., description="Order ID")
    date: datetime = Field(..., description="Order date")
    lastChangeDate: datetime = Field(..., description="Last change date")
    supplierArticle: str = Field(..., description="Supplier article")
    techSize: str = Field(..., description="Technical size")
    barcode: str = Field(..., description="Barcode")
    totalPrice: float = Field(..., description="Total price")
    discountPercent: int = Field(..., description="Discount percent")
    warehouseName: str = Field(..., description="Warehouse name")
    oblast: str = Field(..., description="Oblast")
    incomeID: int = Field(..., description="Income ID")
    nmId: int = Field(..., description="Nomenclature ID")
    subject: str = Field(..., description="Subject")
    category: str = Field(..., description="Category")
    brand: str = Field(..., description="Brand")
    isCancel: bool = Field(False, description="Is cancelled")
    cancelDate: Optional[datetime] = Field(None, description="Cancel date")


class OrdersReportResponse(BaseModel):
    """Response for orders report"""
    orders: List[Order] = Field(default_factory=list, description="Orders list")
    total: int = Field(0, description="Total count")


class Stock(BaseModel):
    """Stock model"""
    lastChangeDate: datetime = Field(..., description="Last change date")
    supplierArticle: str = Field(..., description="Supplier article")
    techSize: str = Field(..., description="Technical size")
    barcode: str = Field(..., description="Barcode")
    quantity: int = Field(..., description="Quantity")
    isSupply: bool = Field(..., description="Is supply")
    isRealization: bool = Field(..., description="Is realization")
    quantityFull: int = Field(..., description="Full quantity")
    warehouseName: str = Field(..., description="Warehouse name")
    nmId: int = Field(..., description="Nomenclature ID")
    subject: str = Field(..., description="Subject")
    category: str = Field(..., description="Category")
    brand: str = Field(..., description="Brand")
    SCCode: str = Field(..., description="SC Code")
    Price: float = Field(..., description="Price")
    Discount: int = Field(..., description="Discount")
    inWayToClient: int = Field(0, description="In way to client")
    inWayFromClient: int = Field(0, description="In way from client")


class StocksReportResponse(BaseModel):
    """Response for stocks report"""
    stocks: List[Stock] = Field(default_factory=list, description="Stocks list")
    total: int = Field(0, description="Total count")


class ReportDetailByPeriod(BaseModel):
    """Report detail by period"""
    realizationreport_id: int = Field(..., description="Report ID")
    date_from: date = Field(..., description="Date from")
    date_to: date = Field(..., description="Date to")
    create_dt: datetime = Field(..., description="Created datetime")
    suppliercontract_code: Optional[str] = Field(None, description="Contract code")
    rrd_id: int = Field(..., description="RRD ID")
    gi_id: int = Field(..., description="GI ID")
    subject_name: str = Field(..., description="Subject name")
    nm_id: int = Field(..., description="NM ID")
    brand_name: str = Field(..., description="Brand name")
    sa_name: str = Field(..., description="SA name")
    ts_name: str = Field(..., description="TS name")
    barcode: str = Field(..., description="Barcode")
    doc_type_name: str = Field(..., description="Document type")
    quantity: int = Field(..., description="Quantity")
    retail_price: float = Field(..., description="Retail price")
    retail_amount: float = Field(..., description="Retail amount")
    sale_percent: int = Field(..., description="Sale percent")
    commission_percent: float = Field(..., description="Commission percent")
    office_name: str = Field(..., description="Office name")
    supplier_oper_name: str = Field(..., description="Supplier operation")
    order_dt: datetime = Field(..., description="Order datetime")
    sale_dt: datetime = Field(..., description="Sale datetime")
    rr_dt: datetime = Field(..., description="RR datetime")
    shk_id: int = Field(..., description="SHK ID")
    retail_price_withdisc_rub: float = Field(..., description="Retail price with discount")
    delivery_amount: int = Field(0, description="Delivery amount")
    return_amount: int = Field(0, description="Return amount")
    delivery_rub: float = Field(0, description="Delivery rub")
    gi_box_type_name: str = Field(..., description="Box type")
    product_discount_for_report: float = Field(..., description="Product discount")
    supplier_promo: float = Field(0, description="Supplier promo")
    rid: int = Field(..., description="RID")
    ppvz_spp_prc: float = Field(..., description="PPVZ SPP PRC")
    ppvz_kvw_prc_base: float = Field(..., description="PPVZ KVW PRC base")
    ppvz_kvw_prc: float = Field(..., description="PPVZ KVW PRC")
    sup_rating_prc_up: float = Field(0, description="Supplier rating PRC up")
    is_kgvp_v2: float = Field(0, description="Is KGVP v2")
    ppvz_sales_commission: float = Field(..., description="PPVZ sales commission")
    ppvz_for_pay: float = Field(..., description="PPVZ for pay")
    ppvz_reward: float = Field(..., description="PPVZ reward")
    acquiring_fee: float = Field(..., description="Acquiring fee")
    acquiring_bank: str = Field(..., description="Acquiring bank")
    ppvz_vw: float = Field(..., description="PPVZ VW")
    ppvz_vw_nds: float = Field(..., description="PPVZ VW NDS")
    ppvz_office_id: int = Field(..., description="PPVZ office ID")
    ppvz_office_name: str = Field(..., description="PPVZ office name")
    ppvz_supplier_id: int = Field(..., description="PPVZ supplier ID")
    ppvz_supplier_name: str = Field(..., description="PPVZ supplier name")
    ppvz_inn: str = Field(..., description="PPVZ INN")
    declaration_number: str = Field("", description="Declaration number")
    bonus_type_name: str = Field("", description="Bonus type")
    sticker_id: str = Field("", description="Sticker ID")
    site_country: str = Field(..., description="Site country")
    penalty: float = Field(0, description="Penalty")
    additional_payment: float = Field(0, description="Additional payment")
    rebill_logistic_cost: float = Field(0, description="Rebill logistic cost")
    rebill_logistic_org: str = Field("", description="Rebill logistic org")
    kiz: str = Field("", description="KIZ")
    storage_fee: float = Field(0, description="Storage fee")
    deduction: float = Field(0, description="Deduction")
    acceptance: float = Field(0, description="Acceptance")
    srid: str = Field(..., description="SRID")
