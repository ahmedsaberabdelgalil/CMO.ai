from app.db.session import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum, Numeric, Date, BIGINT
import enum

# ============================================================
# ENUMS (custom types)
# ============================================================

class UserRole(enum.Enum):
    owner = 'owner'
    admin = 'admin'
    member = 'member'

class StrategyStatus(enum.Enum):
    draft = 'draft'
    active = 'active'
    archived = 'archived'

class PlanType(enum.Enum):
    weekly = 'weekly'
    monthly = 'monthly'

class ContentType(enum.Enum):
    post = 'post'
    video = 'video'
    blog = 'blog'
    email = 'email'
    ad = 'ad'

class ContentStatus(enum.Enum):
    Draft = 'Draft'
    Ready = 'Ready'
    Published = 'Published'

class PlatformType(enum.Enum):
    Instagram = 'Instagram'
    TikTok = 'TikTok'
    LinkedIn = 'LinkedIn'
    YouTube = 'YouTube'
    Email = 'Email'
    Twitter = 'Twitter'

class CampaignStatus(enum.Enum):
    Draft = 'Draft'
    In_Progress = 'In Progress'
    Completed = 'Completed'

class AssetType(enum.Enum):
    image = 'image'
    video = 'video'
    copy = 'copy'

class PlanName(enum.Enum):
    Starter = 'Starter'
    Pro = 'Pro'
    Enterprise = 'Enterprise'

