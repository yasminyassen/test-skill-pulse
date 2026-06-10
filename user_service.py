from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum, auto
from typing import Optional

PLATFORM_FEE_RATE   = Decimal("0.03")   # 3% رسوم المنصة
VIP_DISCOUNT_RATE   = Decimal("0.10")   # 10% خصم VIP
LOYALTY_THRESHOLD   = 5                 # طلبات لازمة للخصم
LOYALTY_DISCOUNT    = Decimal("50")     # جنيه خصم ولاء
VAT_RATE            = Decimal("0.14")   # 14% ضريبة

# ── Enums — بدل strings مجهولة ──────────────────────
class PaymentMethod(Enum):
    CARD      = "card"
    WALLET    = "wallet"
    INSTAPAY  = "instapay"

class Currency(Enum):
    USD = ("USD", Decimal("1.0"))
    EGP = ("EGP", Decimal("49.5"))
    SAR = ("SAR", Decimal("3.75"))
    def __init__(self, code: str, rate: Decimal): self.code=code; self.rate=rate

class CustomerTier(Enum):
    STANDARD = auto()
    VIP      = auto()

# ── Data Models ─────────────────────────────────────
@dataclass(frozen=True)
class OrderItem:
    product_id:  int
    name:        str
    unit_price:  Decimal
    quantity:    int

    @property
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity

@dataclass(frozen=True)
class PaymentContext:
    amount:          Decimal
    token:           str
    payment_method:  PaymentMethod
    customer_tier:   CustomerTier
    customer_age:    int
    region_code:     str
    order_count:     int
    currency:        Currency
    items:           list[OrderItem]
    apply_vat:       bool

@dataclass(frozen=True)
class PaymentBreakdown:
    base_amount:     Decimal
    platform_fee:    Decimal
    vip_discount:    Decimal
    loyalty_discount:Decimal
    items_total:     Decimal
    vat:             Decimal

    @property
    def grand_total(self) -> Decimal:
        return (self.base_amount
                - self.platform_fee
                - self.vip_discount
                - self.loyalty_discount
                + self.items_total
                + self.vat)

# ── Validation — Early Return بدل Nesting ───────────
def _validate_payment(ctx: PaymentContext) -> None:
    """ترمي ValueError بمسجة واضحة لو في مشكلة"""
    if ctx.amount <= 0:
        raise ValueError(f"Invalid amount: {ctx.amount}")
    if ctx.customer_age < 18:
        raise ValueError(f"Customer must be 18+, got {ctx.customer_age}")
    if not ctx.token:
        raise ValueError("Payment token is required")

# ── Pure Calculation Functions — كل واحدة تعمل حاجة واحدة ──
def _calc_platform_fee(amount: Decimal) -> Decimal:
    return (amount * PLATFORM_FEE_RATE).quantize(Decimal("0.01"))

def _calc_vip_discount(amount: Decimal, tier: CustomerTier) -> Decimal:
    if tier is not CustomerTier.VIP:
        return Decimal("0")
    return (amount * VIP_DISCOUNT_RATE).quantize(Decimal("0.01"))

def _calc_loyalty_discount(order_count: int) -> Decimal:
    if order_count > LOYALTY_THRESHOLD:
        return LOYALTY_DISCOUNT
    return Decimal("0")

def _calc_items_total(items: list[OrderItem], currency: Currency) -> Decimal:
    total = sum(item.subtotal for item in items)
    return (total * currency.rate).quantize(Decimal("0.01"))

def _calc_vat(items_total: Decimal, apply_vat: bool) -> Decimal:
    if not apply_vat:
        return Decimal("0")
    return (items_total * VAT_RATE).quantize(Decimal("0.01"))

# ── Public API — نقطة دخول واحدة واضحة ─────────────
def process_payment(ctx: PaymentContext) -> PaymentBreakdown:
    _validate_payment(ctx)

    fee      = _calc_platform_fee(ctx.amount)
    vip_disc = _calc_vip_discount(ctx.amount, ctx.customer_tier)
    loyalty  = _calc_loyalty_discount(ctx.order_count)
    items_t  = _calc_items_total(ctx.items, ctx.currency)
    vat      = _calc_vat(items_t, ctx.apply_vat)

    return PaymentBreakdown(
        base_amount=ctx.amount,
        platform_fee=fee,
        vip_discount=vip_disc,
        loyalty_discount=loyalty,
        items_total=items_t,
        vat=vat,
    )


if __name__ == "__main__":
    ctx = PaymentContext(
        amount=Decimal("500"),
        token="tok_123",
        payment_method=PaymentMethod.CARD,
        customer_tier=CustomerTier.VIP,
        customer_age=25,
        region_code="EG",
        order_count=6,
        currency=Currency.EGP,
        items=[OrderItem(1, "MacBook Case", Decimal("100"), 2)],
        apply_vat=True,
    )
    result = process_payment(ctx)
    print(f"Grand total: {result.grand_total} EGP")
    print(f"Platform fee: {result.platform_fee}")
    print(f"VIP discount: {result.vip_discount}")
