"""
Enhanced Database Models for Telegram Ad Bot
Supports multi-channel advertising, dynamic pricing, and admin management
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime
import os
import uuid

Base = declarative_base()

# Association table for order-channel many-to-many relationship
order_channels = Table(
    'order_channels', Base.metadata,
    Column('order_id', String, ForeignKey('orders.id')),
    Column('channel_id', String, ForeignKey('channels.id'))
)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    first_name = Column(String(100))
    last_name = Column(String(100))
    language_code = Column(String(10), default='en')
    created_at = Column(DateTime, default=datetime.utcnow)
    is_admin = Column(Boolean, default=False)
    
    # Relationships
    orders = relationship("Order", back_populates="user")

class Channel(Base):
    __tablename__ = 'channels'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    channel_id = Column(String(100), unique=True)  # Telegram channel ID
    name = Column(String(200))
    description = Column(Text)
    subscribers_count = Column(Integer, default=0)
    price_per_month = Column(Float, default=0.099)  # TON price per month
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Admin settings
    category = Column(String(100))  # Business, Tech, Crypto, etc.
    
    # Relationships
    orders = relationship("Order", secondary=order_channels, back_populates="channels")

class Bundle(Base):
    __tablename__ = 'bundles'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200))
    description = Column(Text)
    months = Column(Integer)  # Duration in months
    bonus_months = Column(Integer, default=0)  # Free bonus months
    discount_percent = Column(Float, default=0.0)  # Discount percentage
    min_channels = Column(Integer, default=1)
    max_channels = Column(Integer, default=10)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey('users.id'))
    
    # Payment info
    payment_memo = Column(String(20), unique=True)  # INV_[random]
    wallet_address = Column(String(100))
    total_amount_ton = Column(Float)
    total_amount_usd = Column(Float)
    payment_status = Column(String(20), default='pending')  # pending, confirmed, expired
    payment_tx_hash = Column(String(100))  # TON transaction hash
    
    # Order details
    duration_months = Column(Integer)
    bonus_months = Column(Integer, default=0)
    bundle_id = Column(String, ForeignKey('bundles.id'), nullable=True)
    
    # Ad content
    ad_content = Column(JSON)  # Flexible content storage
    content_type = Column(String(20))  # text, photo, video
    
    # Scheduling
    posts_per_month = Column(Integer, default=30)  # Posts per month per channel
    next_post_date = Column(DateTime)
    posts_completed = Column(Integer, default=0)
    posts_total = Column(Integer)
    
    # Status
    status = Column(String(20), default='draft')  # draft, paid, active, completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    expires_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    channels = relationship("Channel", secondary=order_channels, back_populates="orders")
    bundle = relationship("Bundle")

class AdminSettings(Base):
    __tablename__ = 'admin_settings'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True)
    value = Column(Text)
    description = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(Integer, ForeignKey('users.id'))

class PaymentTracking(Base):
    __tablename__ = 'payment_tracking'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String, ForeignKey('orders.id'))
    memo = Column(String(20), unique=True)
    expected_amount = Column(Float)
    received_amount = Column(Float, default=0.0)
    tx_hash = Column(String(100))
    confirmed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    order = relationship("Order")

class CurrencyRate(Base):
    __tablename__ = 'currency_rates'
    
    id = Column(Integer, primary_key=True)
    base_currency = Column(String(10), default='TON')
    target_currency = Column(String(10))  # USD, SAR, RUB
    rate = Column(Float)
    updated_at = Column(DateTime, default=datetime.utcnow)

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={"sslmode": "require", "connect_timeout": 10}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_default_data():
    """Initialize default channels and admin settings"""
    from sqlalchemy.orm import Session
    db = Session(bind=engine)
    
    # Default channels
    if not db.query(Channel).first():
        default_channels = [
            {
                'channel_id': '@i3lani_channel',
                'name': 'I3lani Official',
                'description': 'Main advertising channel',
                'subscribers_count': 1000,
                'category': 'Business'
            },
            {
                'channel_id': '@i3lani_crypto',
                'name': 'I3lani Crypto',
                'description': 'Cryptocurrency news and ads',
                'subscribers_count': 500,
                'category': 'Crypto'
            }
        ]
        
        for channel_data in default_channels:
            channel = Channel(**channel_data)
            db.add(channel)
    
    # Default bundles
    if not db.query(Bundle).first():
        default_bundles = [
            {
                'name': 'Starter Bundle',
                'description': 'Perfect for small businesses',
                'months': 1,
                'bonus_months': 0,
                'discount_percent': 0.0
            },
            {
                'name': 'Growth Bundle',
                'description': 'Popular choice - 3 months + 1 free',
                'months': 3,
                'bonus_months': 1,
                'discount_percent': 10.0
            },
            {
                'name': 'Business Bundle',
                'description': 'Best value - 6 months + 2 free',
                'months': 6,
                'bonus_months': 2,
                'discount_percent': 20.0
            },
            {
                'name': 'Enterprise Bundle',
                'description': 'Maximum savings - 12 months + 3 free',
                'months': 12,
                'bonus_months': 3,
                'discount_percent': 25.0
            }
        ]
        
        for bundle_data in default_bundles:
            bundle = Bundle(**bundle_data)
            db.add(bundle)
    
    # Default admin settings
    if not db.query(AdminSettings).first():
        default_settings = [
            {
                'key': 'ton_wallet_address',
                'value': os.getenv('TON_WALLET_ADDRESS', ''),
                'description': 'TON wallet address for receiving payments'
            },
            {
                'key': 'payment_timeout_minutes',
                'value': '30',
                'description': 'Payment timeout in minutes'
            },
            {
                'key': 'auto_approval_enabled',
                'value': 'true',
                'description': 'Enable automatic payment approval'
            }
        ]
        
        for setting_data in default_settings:
            setting = AdminSettings(**setting_data)
            db.add(setting)
    
    db.commit()
    db.close()