from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class PaymentStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"

class AdStatus(Enum):
    DRAFT = "draft"
    WAITING_PAYMENT = "waiting_payment"
    PAYMENT_PENDING = "payment_pending"
    APPROVED = "approved"
    ACTIVE = "active"
    COMPLETED = "completed"
    REJECTED = "rejected"

@dataclass
class AdContent:
    """Represents the content of an advertisement"""
    text: Optional[str] = None
    photo_file_id: Optional[str] = None
    video_file_id: Optional[str] = None
    caption: Optional[str] = None
    content_type: str = "text"  # text, photo, video

@dataclass
class Advertisement:
    """Represents a complete advertisement order"""
    id: str
    user_id: int
    username: Optional[str]
    content: AdContent
    package_id: str
    price: float
    status: AdStatus
    created_at: datetime
    payment_status: PaymentStatus
    approved_at: Optional[datetime] = None
    first_post_at: Optional[datetime] = None
    posts_count: int = 0
    total_posts: int = 0
    repost_frequency_days: int = 1
    next_repost_at: Optional[datetime] = None
    payment_memo: Optional[str] = None  # Unique memo for payment identification
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert advertisement to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "content": {
                "text": self.content.text,
                "photo_file_id": self.content.photo_file_id,
                "video_file_id": self.content.video_file_id,
                "caption": self.content.caption,
                "content_type": self.content.content_type
            },
            "package_id": self.package_id,
            "price": self.price,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "payment_status": self.payment_status.value,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "first_post_at": self.first_post_at.isoformat() if self.first_post_at else None,
            "posts_count": self.posts_count,
            "total_posts": self.total_posts,
            "repost_frequency_days": self.repost_frequency_days,
            "next_repost_at": self.next_repost_at.isoformat() if self.next_repost_at else None
        }

# In-memory storage for MVP
class InMemoryStorage:
    """Simple in-memory storage for advertisements"""
    
    def __init__(self):
        self.advertisements: Dict[str, Advertisement] = {}
        self.user_current_ad: Dict[int, str] = {}
    
    def save_ad(self, ad: Advertisement) -> None:
        """Save advertisement to storage"""
        self.advertisements[ad.id] = ad
        self.user_current_ad[ad.user_id] = ad.id
    
    def get_ad(self, ad_id: str) -> Optional[Advertisement]:
        """Get advertisement by ID"""
        return self.advertisements.get(ad_id)
    
    def get_user_current_ad(self, user_id: int) -> Optional[Advertisement]:
        """Get user's current advertisement"""
        ad_id = self.user_current_ad.get(user_id)
        if ad_id:
            return self.advertisements.get(ad_id)
        return None
    
    def get_ads_by_status(self, status: AdStatus) -> list[Advertisement]:
        """Get all advertisements with specific status"""
        return [ad for ad in self.advertisements.values() if ad.status == status]
    
    def get_active_ads(self) -> list[Advertisement]:
        """Get all active advertisements that need reposting"""
        return [ad for ad in self.advertisements.values() if ad.status == AdStatus.ACTIVE]
    
    def update_ad(self, ad_id: str, **kwargs) -> bool:
        """Update advertisement fields"""
        if ad_id in self.advertisements:
            ad = self.advertisements[ad_id]
            for key, value in kwargs.items():
                if hasattr(ad, key):
                    setattr(ad, key, value)
            return True
        return False
    
    def delete_ad(self, ad_id: str) -> bool:
        """Delete advertisement"""
        if ad_id in self.advertisements:
            ad = self.advertisements[ad_id]
            del self.advertisements[ad_id]
            if ad.user_id in self.user_current_ad:
                del self.user_current_ad[ad.user_id]
            return True
        return False

# Global storage instance
storage = InMemoryStorage()
