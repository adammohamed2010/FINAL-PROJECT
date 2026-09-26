import hashlib
import os
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, TIMESTAMP, ForeignKey, Text
)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session
from sqlalchemy.sql import func


DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "Adam01555545813")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "3306")
DB_NAME = os.environ.get("DB_NAME", "finalproject2")

SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def hash_password(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    cart_items = relationship("CartItem", back_populates="customer", cascade="all, delete-orphan")
    wishlist_items = relationship("WishlistItem", back_populates="customer", cascade="all, delete-orphan")


class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    category = Column(String(50), nullable=False, default="Home & kitchen")
    listing_type = Column(String(10), nullable=False, default="sell")
    price_egp = Column(Float, nullable=True)
    price_label = Column(String(50), nullable=False)
    image_url = Column(Text, nullable=True)
    icon = Column(String(10), nullable=True)
    seller_name = Column(String(100), nullable=False, default="You")
    seller_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())


class CartItem(Base):
    __tablename__ = "cart_items"

    cart_item_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    created_at = Column(TIMESTAMP, server_default=func.now())

    customer = relationship("Customer", back_populates="cart_items")
    product = relationship("Product")


class WishlistItem(Base):
    __tablename__ = "wishlist_items"

    wishlist_item_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    customer = relationship("Customer", back_populates="wishlist_items")
    product = relationship("Product")


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    price_label = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    created_at = Column(TIMESTAMP, server_default=func.now())

    product = relationship("Product")


Base.metadata.create_all(bind=engine)


SEED_PRODUCTS = [
    dict(
        name="Hammered brass kettle", category="Home & kitchen", listing_type="sell",
        price_egp=450, price_label="450 EGP", seller_name="Om Hassan's Attic",
        image_url="https://images.unsplash.com/photo-1629440408433-a9e951bfbcd8?w=800&q=70&fm=jpg&fit=crop&auto=format",
        icon="🫖",
        description="Hand-hammered brass kettle, holds about a litre. A little tarnish near the handle from years of tea — gives it character. Pickup or delivery within Cairo.",
    ),
    dict(
        name="Polaroid SX-70, working", category="Electronics", listing_type="sell",
        price_egp=1200, price_label="1,200 EGP", seller_name="Karim R.",
        image_url="https://images.unsplash.com/photo-1584451495739-8ff83dc75ef6?w=800&q=70&fm=jpg&fit=crop&auto=format",
        icon="📷",
        description="Fully working Polaroid SX-70, recently serviced. Comes with one pack of film to get you started.",
    ),
    dict(
        name="Hand-loomed kilim rug", category="Home & kitchen", listing_type="trade",
        price_egp=None, price_label="Swap only", seller_name="Nour's Nook",
        image_url="https://images.unsplash.com/photo-1572123979839-3749e9973aba?w=800&q=70&fm=jpg&fit=crop&auto=format",
        icon="🧵",
        description="Hand-loomed kilim rug, roughly 1.5x2m. Looking to trade for kitchenware or plants.",
    ),
    dict(
        name="Mint pothos, rooted", category="Plants", listing_type="trade",
        price_egp=None, price_label="Cuttings ok", seller_name="Sara's Garden",
        image_url="https://images.unsplash.com/photo-1753967825586-e9af49bcfac6?w=800&q=70&fm=jpg&fit=crop&auto=format",
        icon="🌿",
        description="Healthy rooted pothos cutting, already in soil. Happy to trade for other plant cuttings.",
    ),
    dict(
        name="Enamel dutch oven, 5L", category="Home & kitchen", listing_type="sell",
        price_egp=950, price_label="950 EGP", seller_name="Youssef K.",
        image_url="https://images.unsplash.com/photo-1623008473501-a58a2783d81d?w=800&q=70&fm=jpg&fit=crop&auto=format",
        icon="🍲",
        description="5L enamel dutch oven, barely used. Great for stews and oven bread.",
    ),
    dict(
        name="Calligraphy print, framed", category="Art", listing_type="sell",
        price_egp=300, price_label="300 EGP", seller_name="Mostafa A.",
        image_url="https://images.unsplash.com/photo-1705294108409-c730a280d1e0?w=800&q=70&fm=jpg&fit=crop&auto=format",
        icon="✒️",
        description="Original Arabic calligraphy piece, framed and ready to hang. A4 size.",
    ),
]


def seed_if_empty():
    db = SessionLocal()
    try:
        if db.query(Product).count() == 0:
            for p in SEED_PRODUCTS:
                db.add(Product(**p))
            db.commit()
    finally:
        db.close()


seed_if_empty()


app = FastAPI()

frontend_path = Path(__file__).resolve().parent / "frontend.html"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class SignupIn(BaseModel):
    username: str
    email: str
    password: str


class LoginIn(BaseModel):
    username: str
    password: str


class ResetPasswordIn(BaseModel):
    username: str
    email: str
    new_password: str


class CartAddIn(BaseModel):
    customer_id: int
    product_id: int
    quantity: int = 1


class WishlistToggleIn(BaseModel):
    customer_id: int
    product_id: int


class CheckoutIn(BaseModel):
    customer_id: int


class ProductCreateIn(BaseModel):
    customer_id: int
    name: str
    description: str | None = None
    category: str | None = "Home & kitchen"
    listing_type: str = "sell"
    price_egp: float | None = None
    price_label: str
    image_url: str | None = None


def product_out(p: Product) -> dict:
    return {
        "id": p.product_id,
        "name": p.name,
        "category": p.category,
        "listing_type": p.listing_type,
        "price_label": p.price_label,
        "price_egp": p.price_egp,
        "image_url": p.image_url,
        "icon": p.icon,
        "seller_name": p.seller_name,
        "seller_id": p.seller_id,
        "description": p.description,
    }


@app.get("/")
def root():
    return FileResponse(frontend_path)


@app.get("/api/message")
def message():
    return {"message": "Hello from the FastAPI backend!"}


@app.post("/api/signup")
def signup(body: SignupIn, db: Session = Depends(get_db)):
    if db.query(Customer).filter(Customer.username == body.username).first():
        raise HTTPException(status_code=400, detail="Username already taken.")
    if db.query(Customer).filter(Customer.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already registered.")
    customer = Customer(
        username=body.username,
        email=body.email,
        password=hash_password(body.password),
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return {"id": customer.customer_id, "username": customer.username, "email": customer.email}


@app.post("/api/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.username == body.username).first()
    if not customer or customer.password != hash_password(body.password):
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    return {"id": customer.customer_id, "username": customer.username, "email": customer.email}


@app.post("/api/reset-password")
def reset_password(body: ResetPasswordIn, db: Session = Depends(get_db)):
    if len(body.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

    customer = (
        db.query(Customer)
        .filter(Customer.username == body.username, Customer.email == body.email)
        .first()
    )
    if not customer:
        raise HTTPException(status_code=400, detail="Username and email do not match.")

    customer.password = hash_password(body.new_password)
    db.commit()
    return {"message": "Password reset successfully."}


@app.get("/customers")
def list_customers(db: Session = Depends(get_db)):
    return db.query(Customer).all()


@app.get("/api/products")
def list_products(db: Session = Depends(get_db)):
    return [product_out(p) for p in db.query(Product).order_by(Product.product_id).all()]


@app.post("/api/products")
def create_product(body: ProductCreateIn, db: Session = Depends(get_db)):
    seller = db.query(Customer).filter(Customer.customer_id == body.customer_id).first()
    if not seller:
        raise HTTPException(status_code=404, detail="Customer not found.")
    if not body.name.strip():
        raise HTTPException(status_code=400, detail="Name is required.")
    if body.listing_type not in ("sell", "trade"):
        raise HTTPException(status_code=400, detail="Listing type must be 'sell' or 'trade'.")

    product = Product(
        name=body.name.strip(),
        category=(body.category or "Home & kitchen").strip(),
        listing_type=body.listing_type,
        price_egp=body.price_egp,
        price_label=body.price_label,
        image_url=body.image_url,
        icon=None if body.image_url else "📦",
        seller_name=seller.username,
        seller_id=seller.customer_id,
        description=body.description,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product_out(product)


@app.delete("/api/products/{product_id}")
def delete_product(product_id: int, customer_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    if product.seller_id != customer_id:
        raise HTTPException(status_code=403, detail="You can only delete your own listings.")

    db.query(CartItem).filter(CartItem.product_id == product_id).delete()
    db.query(WishlistItem).filter(WishlistItem.product_id == product_id).delete()
    db.query(Order).filter(Order.product_id == product_id).delete()
    db.delete(product)
    db.commit()
    return {"deleted": True}


@app.get("/api/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.product_id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found.")
    related = (
        db.query(Product)
        .filter(Product.category == p.category, Product.product_id != p.product_id)
        .limit(3)
        .all()
    )
    return {"product": product_out(p), "related": [product_out(r) for r in related]}


@app.get("/api/cart/{customer_id}")
def get_cart(customer_id: int, db: Session = Depends(get_db)):
    items = db.query(CartItem).filter(CartItem.customer_id == customer_id).all()
    out = []
    total = 0.0
    for it in items:
        p = it.product
        line_total = (p.price_egp or 0) * it.quantity
        total += line_total
        out.append({
            "cart_item_id": it.cart_item_id,
            "quantity": it.quantity,
            "product": product_out(p),
        })
    return {"items": out, "total_egp": total}


@app.post("/api/cart")
def add_to_cart(body: CartAddIn, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.product_id == body.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    existing = (
        db.query(CartItem)
        .filter(CartItem.customer_id == body.customer_id, CartItem.product_id == body.product_id)
        .first()
    )
    if existing:
        existing.quantity += body.quantity
    else:
        db.add(CartItem(customer_id=body.customer_id, product_id=body.product_id, quantity=body.quantity))
    db.commit()
    return get_cart(body.customer_id, db)


@app.delete("/api/cart/{cart_item_id}")
def remove_from_cart(cart_item_id: int, db: Session = Depends(get_db)):
    item = db.query(CartItem).filter(CartItem.cart_item_id == cart_item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found.")
    customer_id = item.customer_id
    db.delete(item)
    db.commit()
    return get_cart(customer_id, db)


@app.post("/api/cart/checkout")
def checkout(body: CheckoutIn, db: Session = Depends(get_db)):
    items = db.query(CartItem).filter(CartItem.customer_id == body.customer_id).all()
    if not items:
        raise HTTPException(status_code=400, detail="Cart is empty.")
    for it in items:
        db.add(Order(
            buyer_id=body.customer_id,
            product_id=it.product_id,
            quantity=it.quantity,
            price_label=it.product.price_label,
            status="pending",
        ))
        db.delete(it)
    db.commit()
    return get_bought(body.customer_id, db)


@app.get("/api/wishlist/{customer_id}")
def get_wishlist(customer_id: int, db: Session = Depends(get_db)):
    items = db.query(WishlistItem).filter(WishlistItem.customer_id == customer_id).all()
    return [product_out(it.product) for it in items]


@app.post("/api/wishlist/toggle")
def toggle_wishlist(body: WishlistToggleIn, db: Session = Depends(get_db)):
    existing = (
        db.query(WishlistItem)
        .filter(WishlistItem.customer_id == body.customer_id, WishlistItem.product_id == body.product_id)
        .first()
    )
    if existing:
        db.delete(existing)
        db.commit()
        return {"active": False}
    db.add(WishlistItem(customer_id=body.customer_id, product_id=body.product_id))
    db.commit()
    return {"active": True}


@app.get("/api/orders/bought/{customer_id}")
def get_bought(customer_id: int, db: Session = Depends(get_db)):
    orders = db.query(Order).filter(Order.buyer_id == customer_id).order_by(Order.order_id.desc()).all()
    return [{
        "order_id": o.order_id,
        "status": o.status,
        "quantity": o.quantity,
        "price_label": o.price_label,
        "product": product_out(o.product),
    } for o in orders]


@app.get("/api/orders/sold/{customer_id}")
def get_sold(customer_id: int, db: Session = Depends(get_db)):
    orders = (
        db.query(Order)
        .join(Product, Order.product_id == Product.product_id)
        .filter(Product.seller_id == customer_id)
        .order_by(Order.order_id.desc())
        .all()
    )
    return [{
        "order_id": o.order_id,
        "status": o.status,
        "quantity": o.quantity,
        "price_label": o.price_label,
        "product": product_out(o.product),
    } for o in orders]