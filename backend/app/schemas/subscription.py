"""Subscription schemas for the application."""
from typing import Optional
from datetime import datetime
import uuid
from pydantic import BaseModel, Field, ConfigDict


class SubscriptionBase(BaseModel):
    """Base schema for Subscription."""
    plan_name: Optional[str] = None
    status: Optional[str] = None


class SubscriptionCreate(SubscriptionBase):
    """Schema for creating a Subscription."""
    user_id: uuid.UUID
    polar_subscription_id: Optional[str] = None


class SubscriptionUpdate(BaseModel):
    """Schema for updating a Subscription."""
    polar_subscription_id: Optional[str] = None
    plan_name: Optional[str] = None
    status: Optional[str] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None


class SubscriptionInDBBase(SubscriptionBase):
    """Base schema for Subscription in DB."""
    id: uuid.UUID
    user_id: uuid.UUID
    polar_subscription_id: Optional[str] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class Subscription(SubscriptionInDBBase):
    """Schema for Subscription response."""
    pass