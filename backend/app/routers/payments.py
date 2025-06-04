"""
Payments router for Polar integration.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
from pydantic import BaseModel
from loguru import logger
from polar_sdk.webhooks import WebhookVerificationError

from app.database import get_db
from app.services.payments import payment_service
from app.core.deps import get_current_user
from app.models.user import User


# Create router
router = APIRouter()


# Pydantic models for request/response
class CheckoutRequest(BaseModel):
    """Request model for creating checkout session."""
    product_id: str
    success_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CheckoutResponse(BaseModel):
    """Response model for checkout session."""
    checkout_id: str
    checkout_url: str
    status: str


class CustomerPortalResponse(BaseModel):
    """Response model for customer portal."""
    portal_url: str


@router.post("/create-checkout-session", response_model=CheckoutResponse)
async def create_checkout_session(
    request: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a checkout session for the current user.
    
    Args:
        request: Checkout request data
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Checkout session details
    """
    try:
        # Create checkout session with user information
        result = await payment_service.create_checkout_session(
            product_id=request.product_id,
            customer_email=current_user.email,
            customer_external_id=str(current_user.id),  # Link to our user
            success_url=request.success_url or "http://localhost:3000/payments/success",
            metadata={
                "user_id": str(current_user.id),
                "user_email": current_user.email,
                **(request.metadata or {})
            }
        )
        
        logger.info(f"Created checkout session for user {current_user.email}")
        return CheckoutResponse(**result)
        
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create checkout session: {str(e)}"
        )


@router.get("/checkout/{checkout_id}")
async def get_checkout_details(
    checkout_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get details of a checkout session.
    
    Args:
        checkout_id: Checkout session ID
        current_user: Authenticated user
        
    Returns:
        Checkout session details
    """
    try:
        details = await payment_service.get_checkout_details(checkout_id)
        
        # Verify that this checkout belongs to the current user
        # This can be done by checking metadata or customer info
        
        return details
        
    except Exception as e:
        logger.error(f"Error getting checkout details: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Checkout not found: {str(e)}"
        )


@router.post("/customer-portal", response_model=CustomerPortalResponse)
async def create_customer_portal_session(
    current_user: User = Depends(get_current_user)
):
    """
    Create a customer portal session for the current user.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        Customer portal URL
    """
    try:
        # TODO: We need to store/retrieve the Polar customer ID
        # For now, this will need to be implemented based on how we map users to Polar customers
        
        # This is a placeholder - in reality, we'd need to:
        # 1. Store Polar customer IDs in our user table, or
        # 2. Look up the customer by external_id, or
        # 3. Create a customer if one doesn't exist
        
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Customer portal integration requires customer ID mapping implementation"
        )
        
        # When implemented, it would look like:
        # polar_customer_id = await get_polar_customer_id(current_user.id)
        # portal_url = await payment_service.create_customer_portal_session(polar_customer_id)
        # return CustomerPortalResponse(portal_url=portal_url)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating customer portal session: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create customer portal session: {str(e)}"
        )


@router.post("/webhook/polar")
async def handle_polar_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle incoming Polar webhooks.
    
    Args:
        request: FastAPI request object
        db: Database session
        
    Returns:
        Success response
    """
    try:
        # Get raw payload and headers
        payload = await request.body()
        headers = dict(request.headers)
        
        # Validate and parse the webhook
        event = payment_service.validate_webhook(payload, headers)
        
        # Process the webhook event
        await payment_service.process_webhook_event(event, db)
        
        logger.info(f"Successfully processed webhook: {event.get('type')}")
        return {"status": "processed"}
        
    except WebhookVerificationError:
        logger.error("Webhook verification failed - invalid signature")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid webhook signature"
        )
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed"
        )


@router.get("/user/premium-status")
async def get_user_premium_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get the premium status of the current user.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        User premium status
    """
    return {
        "user_id": str(current_user.id),
        "email": current_user.email,
        "is_premium": current_user.is_premium,
        "premium_features": {
            "unlimited_prompts": current_user.is_premium,
            "advanced_exports": current_user.is_premium,
            "priority_support": current_user.is_premium
        }
    }


@router.get("/products")
async def get_available_products():
    """
    Get available products/plans.
    
    This endpoint could be enhanced to fetch products from Polar API
    or return static product information.
    
    Returns:
        Available products/plans
    """
    # For now, return static product information
    # In a real implementation, you might fetch this from Polar API
    return {
        "products": [
            {
                "id": "vibe-coding-premium",
                "name": "VibeCoding Premium",
                "description": "Unlock unlimited prompts, advanced exports, and priority support",
                "price": "$9.99",
                "currency": "USD",
                "interval": "month",
                "features": [
                    "Unlimited AI-generated prompts",
                    "Advanced export formats (PDF, Markdown, etc.)",
                    "Priority customer support",
                    "Early access to new features"
                ]
            }
        ]
    }