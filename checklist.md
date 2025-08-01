# 🚀 REALISTIC QUICK START: Authentication in 3-5 Days




### Step 1: Install Dependencies
```bash
cd /workspaces/Backlogged-Books
pip install fastapi-users[sqlalchemy]==12.1.2
pip install python-jose[cryptography]==3.3.0  
pip install passlib[bcrypt]==1.7.4
pip freeze > requirements.txt  # Update requirements
```

### Step 2: Generate Secrets 
```bash
# Create production environment file
echo "SECRET_KEY=$(openssl rand -hex 32)" > .env.prod
echo "JWT_SECRET_KEY=$(openssl rand -hex 32)" >> .env.prod
echo "DATABASE_ENCRYPTION_KEY=$(openssl rand -hex 32)" >> .env.prod
```

### Step 3: Create User Model
Create `afsp_app/app/models/__init__.py`:
```python
# Empty file to make it a package
```

Create `afsp_app/app/models/user.py`:
```python
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import Column, String, Boolean, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"
    
    email: str = Column(String(320), unique=True, index=True, nullable=False)
    hashed_password: str = Column(String(1024), nullable=False)
    is_active: bool = Column(Boolean, default=True)
    is_verified: bool = Column(Boolean, default=False)
    is_superuser: bool = Column(Boolean, default=False)
    
    # Subscription fields
    subscription_tier: str = Column(String(20), default="free")
    subscription_expires: datetime = Column(DateTime, nullable=True)
    files_processed_this_month: int = Column(Integer, default=0)
    max_files_per_month: int = Column(Integer, default=5)
    
    # Audit fields
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    last_login: datetime = Column(DateTime, nullable=True)
```

##  Authentication Setup

### Step 4: Update Settings 
Update `afsp_app/app/settings.py` - add these fields to the Settings class:
```python
# Add to existing Settings class
JWT_SECRET_KEY: str = Field(default="your-jwt-secret-key-here", env="JWT_SECRET_KEY")
SECRET_KEY: str = Field(default="your-secret-key-here", env="SECRET_KEY")
```

### Step 5: Create Authentication Module
Create `afsp_app/app/auth.py`:
```python
import uuid
from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase

from afsp_app.app.models.user import User
from afsp_app.app.settings import Settings

settings = Settings()

SECRET = settings.JWT_SECRET_KEY

class UserManager(BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")

def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
```

## Database Integration 

### Step 6: Update Database Manager 
Update `afsp_app/app/database.py` to include user database:
```python
# Add these imports at the top
from fastapi_users.db import SQLAlchemyUserDatabase
from afsp_app.app.models.user import User

# Add this method to DatabaseManager class
async def get_user_db(self):
    """Get user database for fastapi-users."""
    with self.get_connection() as conn:
        yield SQLAlchemyUserDatabase(conn, User)
```

### Step 7: Database Migration 
Create `afsp_app/scripts/create_user_tables.py`:
```python
import sqlite3
from afsp_app.app.config import DATABASE_PATH

def create_user_tables():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            is_verified BOOLEAN DEFAULT 0,
            is_superuser BOOLEAN DEFAULT 0,
            subscription_tier TEXT DEFAULT 'free',
            subscription_expires DATETIME,
            files_processed_this_month INTEGER DEFAULT 0,
            max_files_per_month INTEGER DEFAULT 5,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME
        )
    ''')
    
    conn.commit()
    conn.close()
    print("User tables created successfully!")

if __name__ == "__main__":
    create_user_tables()
```

Run the migration:
```bash
cd /workspaces/Backlogged-Books
python afsp_app/scripts/create_user_tables.py
```

## Integrate with Main App

### Step 8: Update Main Application 
Update `afsp_app/app/main.py` - add these imports at the top:
```python
from afsp_app.app.auth import auth_backend, fastapi_users, current_active_user
from afsp_app.app.models.user import User
```

Add authentication routes after the CORS middleware setup:
```python
# Add these routes after app.add_middleware(...) and before existing endpoints

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
```

### Step 9: Protect Upload Endpoint 
Update the upload_file function signature to require authentication:
```python
@app.post("/upload", response_model=UploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    csv_format: Literal["3-column", "4-column"] = Form("3-column"),
    date_format: Literal["MM/DD/YYYY", "DD/MM/YYYY"] = Form("MM/DD/YYYY"),
    current_user: User = Depends(current_active_user),  # ADD THIS LINE
    db: DatabaseManager = Depends(get_db_manager),
):
    # Add subscription check at the beginning
    if current_user.files_processed_this_month >= current_user.max_files_per_month:
        raise HTTPException(
            status_code=402,
            detail=f"Monthly limit of {current_user.max_files_per_month} files exceeded"
        )
    
    # ... existing upload logic ...
    
    # After successful job creation, increment user's count
    # TODO: Add user update logic here
```

## IMMEDIATE TESTING

### Test the Implementation
```bash
# Start the application
cd /workspaces/Backlogged-Books
source venv/bin/activate
uvicorn afsp_app.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Test Endpoints
1. **Check if auth endpoints exist:**
   ```bash
   curl http://localhost:8000/docs
   # Should see /auth/register and /auth/jwt/login endpoints
   ```

2. **Test user registration:**
   ```bash
   curl -X POST "http://localhost:8000/auth/register" \
        -H "Content-Type: application/json" \
        -d '{"email": "test@example.com", "password": "testpassword123"}'
   ```

3. **Test login:**
   ```bash
   curl -X POST "http://localhost:8000/auth/jwt/login" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=test@example.com&password=testpassword123"
   ```

### Expected Results
- ✅ Registration should return user details
- ✅ Login should return access token  
- ✅ Upload endpoint should now require authentication
- ✅ Swagger docs should show authentication options


## Add Stripe Payments 
After completing Week 1:
1. Set up Stripe integration 
2. Create subscription plans 
3. Add payment UI to frontend 
4. Test full payment flow

**Week 2 Result:** Revenue-generating application!

##  Deploy to Production 

1. Fix frontend vulnerabilities (`npm audit fix`)
2. Set up HTTPS/SSL
3. Deploy to production server
4. Launch! 🚀

## 🎯 THE REALISTIC TRUTH

**Your app is already 80% secure.** You just need:
- ✅ Basic authentication 
- ✅ Payment processing  
- ✅ HTTPS deployment

Launch fast, iterate based on real users, add advanced security as you grow.
