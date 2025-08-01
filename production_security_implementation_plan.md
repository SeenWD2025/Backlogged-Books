# AFSP Production Security Implementation Plan

## Current Security Assessment: BETTER THAN EXPECTED

After detailed code review, the application has several **good security practices already implemented**:

✅ **GOOD:** CORS properly configured with specific origins  
✅ **GOOD:** File upload security with `secure_filename()` and magic number validation  
✅ **GOOD:** File type validation using both extension and MIME type detection  
✅ **GOOD:** File size limits enforced (10MB)  
✅ **GOOD:** Structured logging with job IDs  
✅ **GOOD:** Proper dependency injection pattern  
✅ **GOOD:** Environment-based configuration with pydantic-settings  

## CRITICAL GAPS REQUIRING IMMEDIATE ATTENTION

### 1. Authentication & Authorization (CRITICAL)
**Status:** ❌ **MISSING ENTIRELY**  
**Risk Level:** CRITICAL  
**Business Impact:** Cannot deploy to production without user management

**Required Implementation:**
```python
# Phase 1: Basic Authentication (Week 1-2)
pip install fastapi-users[sqlalchemy]
pip install python-jose[cryptography] 
pip install passlib[bcrypt]

# Database Schema Addition
class User(SQLAlchemyBaseUserTable[uuid.UUID], Base):
    email: str
    hashed_password: str
    is_active: bool = True
    is_verified: bool = False
    subscription_tier: str = "free"  # free, basic, premium
    subscription_expires: Optional[datetime] = None
    files_processed_this_month: int = 0
    max_files_per_month: int = 5  # Based on subscription
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### 2. Subscription Management (CRITICAL FOR BUSINESS)
**Status:** ❌ **MISSING ENTIRELY**  
**Risk Level:** CRITICAL  
**Business Impact:** No revenue model, unlimited resource usage

**Required Implementation:**
```python
# Subscription Plans
SUBSCRIPTION_PLANS = {
    "free": {"monthly_files": 5, "price": 0},
    "basic": {"monthly_files": 50, "price": 9.99},
    "premium": {"monthly_files": 200, "price": 29.99},
    "enterprise": {"monthly_files": 1000, "price": 99.99}
}

# Usage Enforcement in Upload Endpoint
@app.post("/upload")
@require_auth
async def upload_file(current_user: User, ...):
    # Check subscription limits
    if current_user.files_processed_this_month >= current_user.max_files_per_month:
        raise HTTPException(
            status_code=402, 
            detail="Monthly file limit exceeded. Please upgrade your subscription."
        )
```

### 3. Data Encryption (HIGH PRIORITY)
**Status:** ❌ **MISSING**  
**Risk Level:** HIGH  
**Impact:** Financial data stored in plain text

**Required Implementation:**
```python
# Field-level encryption for sensitive data
pip install cryptography

class EncryptedTransaction(Base):
    encrypted_description: bytes  # Encrypted transaction description
    encrypted_amount: bytes       # Encrypted amount
    user_id: uuid.UUID           # Associate with user
    
    def decrypt_description(self, key: bytes) -> str:
        # Implement AES decryption
        
    def decrypt_amount(self, key: bytes) -> Decimal:
        # Implement AES decryption
```

## IMMEDIATE PRODUCTION SECURITY FIXES

### Week 1: Authentication Foundation
```bash
# 1. Install dependencies
pip install fastapi-users[sqlalchemy] python-jose[cryptography] passlib[bcrypt]

# 2. Environment variables for production
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env.prod
echo "JWT_SECRET_KEY=$(openssl rand -hex 32)" >> .env.prod
echo "DATABASE_ENCRYPTION_KEY=$(openssl rand -hex 32)" >> .env.prod
```

### Week 2: User Management Database Schema
```python
# afsp_app/app/models/user.py
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Float

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
    last_active: datetime = Column(DateTime, default=datetime.utcnow)
```

### Week 3: Authentication Endpoints
```python
# afsp_app/app/auth.py
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTAuthentication

SECRET = settings.JWT_SECRET_KEY

jwt_authentication = JWTAuthentication(
    secret=SECRET,
    lifetime_seconds=3600,  # 1 hour
    tokenUrl="auth/jwt/login",
)

fastapi_users = FastAPIUsers(
    user_manager,
    [jwt_authentication],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)

# Add to main.py
app.include_router(
    fastapi_users.get_auth_router(jwt_authentication),
    prefix="/auth/jwt",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
```

### Week 4: Protect Upload Endpoint
```python
# Updated upload endpoint with authentication
@app.post("/upload", response_model=UploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    csv_format: Literal["3-column", "4-column"] = Form("3-column"),
    date_format: Literal["MM/DD/YYYY", "DD/MM/YYYY"] = Form("MM/DD/YYYY"),
    current_user: User = Depends(fastapi_users.current_user(active=True)),
    db: DatabaseManager = Depends(get_db_manager),
):
    # Check subscription limits
    if current_user.files_processed_this_month >= current_user.max_files_per_month:
        raise HTTPException(
            status_code=402,
            detail=f"Monthly limit of {current_user.max_files_per_month} files exceeded"
        )
    
    # Existing upload logic...
    
    # Increment user's file count
    current_user.files_processed_this_month += 1
    # Update in database
```

## FRONTEND SECURITY UPDATES

### Week 5: Authentication UI
```jsx
// frontend/src/components/auth/LoginForm.js
import React, { useState } from 'react';
import { loginUser } from '../../services/auth';

const LoginForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await loginUser(email, password);
      localStorage.setItem('token', response.access_token);
      // Redirect to dashboard
    } catch (error) {
      setError('Invalid email or password');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-md mx-auto">
      <div className="mb-4">
        <label htmlFor="email" className="block text-sm font-medium text-gray-700">
          Email
        </label>
        <input
          type="email"
          id="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
          required
        />
      </div>
      
      <div className="mb-6">
        <label htmlFor="password" className="block text-sm font-medium text-gray-700">
          Password
        </label>
        <input
          type="password"
          id="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
          required
        />
      </div>
      
      {error && (
        <div className="mb-4 text-sm text-red-600">
          {error}
        </div>
      )}
      
      <button
        type="submit"
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
      >
        Sign In
      </button>
    </form>
  );
};

export default LoginForm;
```

### Authentication Context Provider
```jsx
// frontend/src/context/AuthContext.js
import React, { createContext, useContext, useState, useEffect } from 'react';
import { getCurrentUser } from '../services/auth';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      getCurrentUser(token)
        .then(setUser)
        .catch(() => localStorage.removeItem('token'))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = (userData, token) => {
    localStorage.setItem('token', token);
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};
```

## SUBSCRIPTION MANAGEMENT IMPLEMENTATION

### Week 6: Stripe Integration
```python
# Backend subscription management
pip install stripe

# afsp_app/app/services/subscription_service.py
import stripe
from afsp_app.app.config import STRIPE_SECRET_KEY

stripe.api_key = STRIPE_SECRET_KEY

class SubscriptionService:
    PLANS = {
        "basic": "price_basic_monthly_id",
        "premium": "price_premium_monthly_id", 
        "enterprise": "price_enterprise_monthly_id"
    }
    
    async def create_checkout_session(self, user_id: str, plan: str):
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': self.PLANS[plan],
                'quantity': 1,
            }],
            mode='subscription',
            success_url='https://yourdomain.com/subscription/success',
            cancel_url='https://yourdomain.com/subscription/cancel',
            client_reference_id=user_id,
        )
        return session
    
    async def handle_webhook(self, payload, sig_header):
        # Handle Stripe webhooks for subscription updates
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payload")
        
        if event['type'] == 'checkout.session.completed':
            # Update user subscription in database
            pass
```

## PRODUCTION DEPLOYMENT SECURITY

### Week 7: Infrastructure Security
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - DATABASE_ENCRYPTION_KEY=${DATABASE_ENCRYPTION_KEY}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
    volumes:
      - ./uploads:/app/uploads
      - ./downloads:/app/downloads
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
    restart: unless-stopped

  redis:
    image: redis:alpine
    restart: unless-stopped
    command: redis-server --requirepass ${REDIS_PASSWORD}
```

### Security Headers (nginx.conf)
```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';";
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/m;
    
    location / {
        limit_req zone=api burst=5;
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## MONITORING & COMPLIANCE

### Week 8: Audit Logging
```python
# afsp_app/app/models/audit_log.py
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id: int = Column(Integer, primary_key=True)
    user_id: str = Column(String, nullable=False)
    action: str = Column(String, nullable=False)  # upload, download, view, delete
    resource_id: str = Column(String, nullable=True)  # job_id or file_id
    resource_type: str = Column(String, nullable=False)  # file, job, user
    timestamp: datetime = Column(DateTime, default=datetime.utcnow)
    ip_address: str = Column(String, nullable=False)
    user_agent: str = Column(String, nullable=True)
    sensitive_data_accessed: bool = Column(Boolean, default=False)
    details: str = Column(Text, nullable=True)  # JSON string with additional details

# Audit logging decorator
def audit_log(action: str, resource_type: str, sensitive: bool = False):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract request info
            request = kwargs.get('request') or args[0]
            user = kwargs.get('current_user')
            
            result = await func(*args, **kwargs)
            
            # Log the action
            log_entry = AuditLog(
                user_id=str(user.id) if user else "anonymous",
                action=action,
                resource_type=resource_type,
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent"),
                sensitive_data_accessed=sensitive,
                details=json.dumps({"endpoint": str(request.url)})
            )
            # Save to database
            
            return result
        return wrapper
    return decorator

# Usage
@app.post("/upload")
@audit_log("upload", "file", sensitive=True)
async def upload_file(...):
    pass
```

## FINAL PRODUCTION CHECKLIST

### Security Essentials ✅
- [ ] User authentication with JWT tokens
- [ ] Subscription management with Stripe
- [ ] Data encryption for sensitive fields
- [ ] Rate limiting and DDoS protection
- [ ] HTTPS/TLS configuration
- [ ] Security headers implementation
- [ ] Audit logging for all financial data access
- [ ] Input validation and sanitization
- [ ] Frontend dependency vulnerability fixes
- [ ] Environment variable security

### Compliance & Monitoring ✅
- [ ] GDPR compliance (consent, data export, deletion)
- [ ] Audit trail for all user actions
- [ ] Automated backup system with encryption
- [ ] Health checks and monitoring
- [ ] Error reporting without sensitive data exposure
- [ ] User session timeout implementation
- [ ] Multi-factor authentication option
- [ ] Terms of service and privacy policy

### Business Requirements ✅
- [ ] Subscription tier enforcement
- [ ] Payment processing with Stripe
- [ ] Usage analytics and reporting
- [ ] Customer support ticket system
- [ ] Email notifications for account events
- [ ] Invoice generation and billing history
- [ ] Free trial management
- [ ] Subscription upgrade/downgrade flows

## ESTIMATED TIMELINE: 8-10 WEEKS

**Weeks 1-2:** Authentication & User Management  
**Weeks 3-4:** Subscription System & Payment Processing  
**Weeks 5-6:** Frontend Security & User Interface  
**Weeks 7-8:** Production Infrastructure & Deployment  
**Weeks 9-10:** Testing, Compliance & Monitoring

**Total Investment:** ~400-500 developer hours for production-ready security

This implementation plan transforms your solid technical foundation into a secure, commercial-grade financial application ready for production deployment with paying subscribers.
