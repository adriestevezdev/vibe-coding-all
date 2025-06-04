"""
Payments service for Polar integration.
"""
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from loguru import logger
from polar_sdk.webhooks import validate_event, WebhookVerificationError

from app.core.polar_client import polar_client
from app.models.user import User


class PaymentService:
    """Service for handling Polar payments and subscriptions."""
    
    def __init__(self):
        """Initialize the payment service."""
        self.polar = polar_client.get_client()
        self.webhook_secret = polar_client.webhook_secret
    
    async def create_checkout_session(
        self,
        product_id: str,
        customer_email: Optional[str] = None,
        customer_external_id: Optional[str] = None,
        success_url: str = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a checkout session with Polar.
        
        Args:
            product_id: Polar product ID
            customer_email: Customer email address
            customer_external_id: External customer ID (user ID from our system)
            success_url: URL to redirect to after successful payment
            metadata: Additional metadata for the checkout
            
        Returns:
            Dict containing checkout_id, checkout_url, and status
            
        Raises:
            Exception: If checkout creation fails
        """
        try:
            checkout_data = {
                "product_id": product_id,
                "allow_discount_codes": True,
            }
            
            # Add customer information if provided
            if customer_email:
                checkout_data["customer_email"] = customer_email
            
            if customer_external_id:
                checkout_data["customer_external_id"] = customer_external_id
            
            if success_url:
                checkout_data["success_url"] = success_url
            
            if metadata:
                checkout_data["metadata"] = metadata
            
            logger.info(f"Creating checkout session for product {product_id}")
            checkout = self.polar.checkouts.create(request=checkout_data)
            
            return {
                "checkout_id": checkout.id,
                "checkout_url": checkout.url,
                "status": "created"
            }
            
        except Exception as e:
            logger.error(f"Error creating checkout session: {str(e)}")
            raise Exception(f"Failed to create checkout session: {str(e)}")
    
    async def get_checkout_details(self, checkout_id: str) -> Dict[str, Any]:
        """
        Get details of a checkout session.
        
        Args:
            checkout_id: Checkout session ID
            
        Returns:
            Dict with checkout details
            
        Raises:
            Exception: If checkout retrieval fails
        """
        try:
            checkout = self.polar.checkouts.get(checkout_id)
            
            return {
                "checkout_id": checkout.id,
                "status": checkout.status,
                "customer_id": getattr(checkout, 'customer_id', None),
                "product_id": getattr(checkout, 'product_id', None),
                "amount": getattr(checkout, 'amount', None),
                "currency": getattr(checkout, 'currency', None),
                "metadata": getattr(checkout, 'metadata', {})
            }
            
        except Exception as e:
            logger.error(f"Error getting checkout details: {str(e)}")
            raise Exception(f"Failed to get checkout details: {str(e)}")
    
    def validate_webhook(self, payload: bytes, headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Validate and parse a Polar webhook.
        
        Args:
            payload: Raw webhook payload
            headers: Request headers
            
        Returns:
            Parsed webhook event
            
        Raises:
            WebhookVerificationError: If webhook validation fails
        """
        try:
            event = validate_event(
                payload=payload,
                headers=headers,
                secret=self.webhook_secret
            )
            logger.info(f"Validated webhook event: {event.get('type')}")
            return event
            
        except WebhookVerificationError as e:
            logger.error(f"Webhook validation failed: {e}")
            raise e
    
    async def process_webhook_event(self, event: Dict[str, Any], db: AsyncSession) -> None:
        """
        Process a validated webhook event.
        
        Args:
            event: Validated webhook event
            db: Database session
        """
        event_type = event.get("type")
        data = event.get("data", {})
        
        logger.info(f"Processing webhook event: {event_type}")
        
        if event_type == "checkout.created":
            await self._handle_checkout_created(data, db)
        elif event_type == "checkout.updated":
            await self._handle_checkout_updated(data, db)
        elif event_type == "subscription.created":
            await self._handle_subscription_created(data, db)
        elif event_type == "subscription.updated":
            await self._handle_subscription_updated(data, db)
        elif event_type == "subscription.active":
            await self._handle_subscription_active(data, db)
        elif event_type == "subscription.canceled":
            await self._handle_subscription_canceled(data, db)
        else:
            logger.warning(f"Unhandled webhook event type: {event_type}")
    
    async def _handle_checkout_created(self, data: Dict[str, Any], db: AsyncSession) -> None:
        """Handle checkout created event."""
        checkout_id = data.get("id")
        logger.info(f"Checkout created: {checkout_id}")
        # Add any specific logic for checkout creation if needed
    
    async def _handle_checkout_updated(self, data: Dict[str, Any], db: AsyncSession) -> None:
        """Handle checkout updated event."""
        checkout_id = data.get("id")
        status = data.get("status")
        
        logger.info(f"Checkout {checkout_id} updated to status: {status}")
        
        if status == "confirmed":
            await self._process_successful_payment(data, db)
    
    async def _handle_subscription_created(self, data: Dict[str, Any], db: AsyncSession) -> None:
        """Handle subscription created event."""
        subscription_id = data.get("id")
        customer_id = data.get("customer_id")
        
        logger.info(f"Subscription created: {subscription_id} for customer: {customer_id}")
        
        # Activate premium access for the customer
        await self._activate_premium_access(customer_id, db)
    
    async def _handle_subscription_updated(self, data: Dict[str, Any], db: AsyncSession) -> None:
        """Handle subscription updated event."""
        subscription_id = data.get("id")
        status = data.get("status")
        customer_id = data.get("customer_id")
        
        logger.info(f"Subscription {subscription_id} updated to status: {status}")
        
        if status in ["active", "trialing"]:
            await self._activate_premium_access(customer_id, db)
        elif status in ["canceled", "incomplete_expired", "past_due"]:
            await self._deactivate_premium_access(customer_id, db)
    
    async def _handle_subscription_active(self, data: Dict[str, Any], db: AsyncSession) -> None:
        """Handle subscription active event."""
        subscription_id = data.get("id")
        customer_id = data.get("customer_id")
        
        logger.info(f"Subscription activated: {subscription_id}")
        await self._activate_premium_access(customer_id, db)
    
    async def _handle_subscription_canceled(self, data: Dict[str, Any], db: AsyncSession) -> None:
        """Handle subscription canceled event."""
        subscription_id = data.get("id")
        customer_id = data.get("customer_id")
        
        logger.info(f"Subscription canceled: {subscription_id}")
        await self._deactivate_premium_access(customer_id, db)
    
    async def _process_successful_payment(self, checkout_data: Dict[str, Any], db: AsyncSession) -> None:
        """
        Process a successful payment.
        
        Args:
            checkout_data: Checkout data from webhook
            db: Database session
        """
        customer_external_id = checkout_data.get("customer_external_id")
        customer_id = checkout_data.get("customer_id")
        
        # If we have an external ID (user ID from our system), activate premium
        if customer_external_id:
            await self._activate_premium_by_user_id(customer_external_id, db)
        elif customer_id:
            await self._activate_premium_access(customer_id, db)
        
        logger.info(f"Processed successful payment for checkout: {checkout_data.get('id')}")
    
    async def _activate_premium_access(self, polar_customer_id: str, db: AsyncSession) -> None:
        """
        Activate premium access for a Polar customer.
        
        Args:
            polar_customer_id: Polar customer ID
            db: Database session
        """
        try:
            # For now, we'll need to implement customer ID mapping
            # This could be done through metadata or external_id field
            logger.info(f"Activating premium access for Polar customer: {polar_customer_id}")
            
            # TODO: Implement customer ID mapping between Polar and our system
            # This might involve storing Polar customer IDs in our user table
            # or using the external_id field when creating customers
            
        except Exception as e:
            logger.error(f"Error activating premium access: {e}")
    
    async def _activate_premium_by_user_id(self, user_id: str, db: AsyncSession) -> None:
        """
        Activate premium access for a user by their internal ID.
        
        Args:
            user_id: Internal user ID
            db: Database session
        """
        try:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalars().first()
            
            if user:
                user.is_premium = True
                await db.commit()
                logger.info(f"Activated premium access for user: {user.email}")
            else:
                logger.warning(f"User not found with ID: {user_id}")
                
        except Exception as e:
            logger.error(f"Error activating premium access for user {user_id}: {e}")
            await db.rollback()
    
    async def _deactivate_premium_access(self, polar_customer_id: str, db: AsyncSession) -> None:
        """
        Deactivate premium access for a Polar customer.
        
        Args:
            polar_customer_id: Polar customer ID
            db: Database session
        """
        try:
            logger.info(f"Deactivating premium access for Polar customer: {polar_customer_id}")
            
            # TODO: Implement customer ID mapping and deactivation logic
            
        except Exception as e:
            logger.error(f"Error deactivating premium access: {e}")
    
    async def create_customer_portal_session(self, customer_id: str) -> str:
        """
        Create a customer portal session.
        
        Args:
            customer_id: Polar customer ID
            
        Returns:
            Portal URL
            
        Raises:
            Exception: If portal session creation fails
        """
        try:
            session = self.polar.customer_portal.customer_sessions.create(
                request={"customer_id": customer_id}
            )
            
            # Generate portal URL
            base_url = "https://sandbox.polar.sh" if polar_client._client.server_url == "sandbox" else "https://polar.sh"
            portal_url = f"{base_url}/customer-portal?customer_session_token={session.token}"
            
            logger.info(f"Created customer portal session for customer: {customer_id}")
            return portal_url
            
        except Exception as e:
            logger.error(f"Error creating customer portal session: {str(e)}")
            raise Exception(f"Failed to create customer portal session: {str(e)}")


# Global service instance
payment_service = PaymentService()