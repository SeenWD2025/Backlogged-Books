import uuid
from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, StringIDMixin
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy

from afsp_app.app.database import User, get_user_db
from afsp_app.app.settings import settings
from afsp_app.app.services.email_service import email_service

SECRET = settings.SECRET_KEY


class UserManager(StringIDMixin, BaseUserManager[User, str]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        """Handle user registration - send verification email or auto-verify based on environment."""
        print(f"User {user.id} has registered.")
        
        # Development bypass: auto-verify if configured
        if (settings.ENVIRONMENT == "development" and 
            settings.AUTO_VERIFY_IN_DEVELOPMENT):
            
            print(f"Development mode: Auto-verifying user {user.id}")
            # In development, auto-verify users
            # This will be handled by the registration endpoint
            
        elif settings.REQUIRE_EMAIL_VERIFICATION:
            # Production: send verification email
            print(f"Production mode: Sending verification email to {user.email}")
            await self.request_verify(user, request)

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """Send verification email when verification is requested."""
        print(f"Verification requested for user {user.id}. Verification token: {token}")
        
        # Send verification email
        success = await email_service.send_verification_email(
            email=user.email,
            verification_token=token,
            user_id=user.id
        )
        
        if success:
            print(f"Verification email sent successfully to {user.email}")
        else:
            print(f"Failed to send verification email to {user.email}")

    async def on_after_verify(
        self, user: User, request: Optional[Request] = None
    ):
        """Handle successful email verification."""
        print(f"User {user.id} has been verified successfully.")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
