# AFSP Security Implementation Checklist

## 🚨 CRITICAL PRIORITY - WEEKS 1-4 (MUST COMPLETE BEFORE PRODUCTION)

### PHASE 1: Authentication System Implementation (Week 1-2)

#### Week 1: Authentication Foundation
- [ ] **Install Authentication Dependencies**
  ```bash
  cd /workspaces/Backlogged-Books
  pip install fastapi-users[sqlalchemy]==12.1.2
  pip install python-jose[cryptography]==3.3.0
  pip install passlib[bcrypt]==1.7.4
  pip install python-multipart  # Already installed, verify version
  ```

- [ ] **Generate Production Secrets**
  ```bash
  # Generate and store in .env.prod file
  echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env.prod
  echo "JWT_SECRET_KEY=$(openssl rand -hex 32)" >> .env.prod
  echo "DATABASE_ENCRYPTION_KEY=$(openssl rand -hex 32)" >> .env.prod
  ```

- [ ] **Create User Model and Database Schema**
  - [ ] Create `afsp_app/app/models/__init__.py`
  - [ ] Create `afsp_app/app/models/user.py` with User model
  - [ ] Create `afsp_app/app/models/subscription.py` with subscription models
  - [ ] Update `afsp_app/app/database.py` to include user tables

#### Week 1 Tasks:
- [ ] **File: `afsp_app/app/models/user.py`**
  ```python
  from fastapi_users.db import SQLAlchemyBaseUserTableUUID
  from sqlalchemy import Column, String, Boolean, Integer, DateTime, Float
  from sqlalchemy.ext.declarative import declarative_base
  from datetime import datetime
  import uuid

  Base = declarative_base()

  class User(SQLAlchemyBaseUserTableUUID, Base):
      __tablename__ = "users"
      
      # Basic user fields (from fastapi-users)
      email: str = Column(String(320), unique=True, index=True, nullable=False)
      hashed_password: str = Column(String(1024), nullable=False)
      is_active: bool = Column(Boolean, default=True)
      is_verified: bool = Column(Boolean, default=False)
      is_superuser: bool = Column(Boolean, default=False)
      
      # Subscription management fields
      subscription_tier: str = Column(String(20), default="free")
      subscription_expires: datetime = Column(DateTime, nullable=True)
      files_processed_this_month: int = Column(Integer, default=0)
      max_files_per_month: int = Column(Integer, default=5)
      
      # Audit fields
      created_at: datetime = Column(DateTime, default=datetime.utcnow)
      last_login: datetime = Column(DateTime, nullable=True)
      last_active: datetime = Column(DateTime, default=datetime.utcnow)
  ```

- [ ] **File: `afsp_app/app/auth.py`** (Create new file)
  ```python
  from fastapi_users import FastAPIUsers
  from fastapi_users.authentication import JWTAuthentication
  from fastapi_users.db import SQLAlchemyUserDatabase
  from afsp_app.app.models.user import User
  from afsp_app.app.settings import Settings

  settings = Settings()

  SECRET = settings.JWT_SECRET_KEY

  jwt_authentication = JWTAuthentication(
      secret=SECRET,
      lifetime_seconds=3600,  # 1 hour
      tokenUrl="auth/jwt/login",
  )

  # Configure FastAPIUsers
  fastapi_users = FastAPIUsers(
      user_manager,
      [jwt_authentication],
      User,
      UserCreate,
      UserUpdate,
      UserDB,
  )
  ```

#### Week 2: Authentication Integration
- [ ] **Update `afsp_app/app/settings.py`**
  ```python
  # Add to existing Settings class
  JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
  SECRET_KEY: str = Field(..., env="SECRET_KEY")
  DATABASE_ENCRYPTION_KEY: str = Field(..., env="DATABASE_ENCRYPTION_KEY")
  ```

- [ ] **Update `afsp_app/app/main.py` - Add Authentication Routes**
  ```python
  # Add imports
  from afsp_app.app.auth import fastapi_users, jwt_authentication

  # Add after app creation, before existing routes
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
  app.include_router(
      fastapi_users.get_users_router(UserRead, UserUpdate),
      prefix="/users",
      tags=["users"],
  )
  ```

- [ ] **Database Migration Script**
  - [ ] Create `afsp_app/scripts/migrate_add_users.py`
  - [ ] Run migration to add user tables
  - [ ] Test user registration and login endpoints

### PHASE 2: Protect Upload Endpoint (Week 3)

- [ ] **Update Upload Endpoint with Authentication**
  ```python
  # In afsp_app/app/main.py, update upload_file function
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
              detail=f"Monthly limit of {current_user.max_files_per_month} files exceeded. Please upgrade your subscription."
          )
      
      # Existing upload logic...
      
      # Increment user's file count after successful upload
      current_user.files_processed_this_month += 1
      # Update user in database
  ```

- [ ] **Update All Protected Endpoints**
  - [ ] `/status/{job_id}` - require authentication
  - [ ] `/download/{job_id}` - require authentication + ownership check
  - [ ] `/jobs` - require authentication + filter by user

### PHASE 3: Subscription Management (Week 4)

- [ ] **Install Stripe Dependencies**
  ```bash
  pip install stripe==7.2.0
  ```

- [ ] **Create Subscription Service**
  - [ ] File: `afsp_app/app/services/subscription_service.py`
  - [ ] Implement Stripe checkout session creation
  - [ ] Implement webhook handling for subscription events
  - [ ] Create subscription plan management

- [ ] **Environment Variables for Stripe**
  ```bash
  echo "STRIPE_SECRET_KEY=sk_test_..." >> .env.prod
  echo "STRIPE_WEBHOOK_SECRET=whsec_..." >> .env.prod
  echo "STRIPE_PUBLISHABLE_KEY=pk_test_..." >> .env.prod
  ```

## 🔴 HIGH PRIORITY - WEEKS 5-6

### PHASE 4: Data Encryption Implementation

- [ ] **Install Encryption Dependencies**
  ```bash
  pip install cryptography==41.0.7
  pip install sqlcipher3==0.5.2  # For encrypted SQLite
  ```

- [ ] **Implement Field-Level Encryption**
  - [ ] Create `afsp_app/app/utils/encryption.py`
  - [ ] Update transaction models to support encrypted fields
  - [ ] Implement encryption/decryption for sensitive data

- [ ] **Database Encryption Migration**
  - [ ] Create migration script for existing data
  - [ ] Update database connection to use SQLCipher
  - [ ] Test data encryption/decryption functionality

### PHASE 5: Frontend Security Updates

- [ ] **Fix Frontend Vulnerabilities**
  ```bash
  cd frontend
  npm audit fix --force
  npm update react-scripts@latest
  npm update @testing-library/react@latest
  npm update axios@latest
  ```

- [ ] **Implement Authentication UI**
  - [ ] Create `frontend/src/components/auth/LoginForm.js`
  - [ ] Create `frontend/src/components/auth/RegisterForm.js`
  - [ ] Create `frontend/src/context/AuthContext.js`
  - [ ] Update `frontend/src/App.js` with protected routes

- [ ] **Update API Service for Authentication**
  ```javascript
  // Update frontend/src/services/api.js
  const apiClient = axios.create({
    baseURL: API_URL,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
    },
  });
  ```

## 🟡 MEDIUM PRIORITY - WEEKS 7-8

### PHASE 6: Production Infrastructure

- [ ] **Rate Limiting Implementation**
  ```bash
  pip install slowapi==0.1.9
  pip install redis==5.0.1
  ```

- [ ] **Update CORS for Production**
  ```python
  # In afsp_app/app/main.py
  app.add_middleware(
      CORSMiddleware,
      allow_origins=[
          "https://yourdomain.com",
          "https://app.yourdomain.com",
      ],
      allow_credentials=True,
      allow_methods=["GET", "POST"],
      allow_headers=["Authorization", "Content-Type"],
  )
  ```

- [ ] **Container Security Hardening**
  ```dockerfile
  # Update Dockerfile
  FROM python:3.11-slim

  # Create non-root user
  RUN groupadd -r afsp && useradd -r -g afsp afsp

  # Install dependencies as root
  RUN apt-get update && apt-get install -y \
      libmagic1 tesseract-ocr pkg-config \
      --no-install-recommends && \
      rm -rf /var/lib/apt/lists/*

  # Switch to non-root user
  USER afsp
  ```

### PHASE 7: Audit Logging & Compliance

- [ ] **Implement Audit Logging**
  - [ ] Create `afsp_app/app/models/audit_log.py`
  - [ ] Create audit logging decorator
  - [ ] Apply to all sensitive endpoints

- [ ] **GDPR Compliance Features**
  - [ ] Implement data export endpoint
  - [ ] Implement data deletion endpoint
  - [ ] Create privacy policy and terms of service
  - [ ] Implement consent management

## 🟢 NICE TO HAVE - WEEKS 9-10+

### PHASE 8: Advanced Security Features

- [ ] **Multi-Factor Authentication**
  ```bash
  pip install pyotp==2.9.0
  pip install qrcode==7.4.2
  ```

- [ ] **Advanced Monitoring**
  - [ ] Implement security event monitoring
  - [ ] Set up alerting for suspicious activities
  - [ ] Create security dashboard

- [ ] **Professional Security Assessment**
  - [ ] Schedule penetration testing
  - [ ] Implement automated security scanning
  - [ ] SOC 2 compliance preparation

## TESTING CHECKLIST

### Security Testing Tasks
- [ ] **Authentication Testing**
  - [ ] Test user registration flow
  - [ ] Test login/logout functionality
  - [ ] Test JWT token expiration
  - [ ] Test password reset flow

- [ ] **Authorization Testing**
  - [ ] Test file access controls (users can only access their files)
  - [ ] Test subscription limit enforcement
  - [ ] Test admin vs regular user permissions

- [ ] **Input Validation Testing**
  - [ ] Test file upload restrictions
  - [ ] Test malicious file upload prevention
  - [ ] Test SQL injection prevention
  - [ ] Test XSS prevention

- [ ] **Rate Limiting Testing**
  - [ ] Test upload rate limits
  - [ ] Test API rate limits
  - [ ] Test DDoS protection

### Integration Testing
- [ ] **End-to-End User Flows**
  - [ ] User registration → email verification → first upload
  - [ ] Subscription upgrade → increased limits → file processing
  - [ ] File upload → processing → download with authentication

## DEPLOYMENT CHECKLIST

### Production Environment Setup
- [ ] **SSL/HTTPS Configuration**
  - [ ] Obtain SSL certificates (Let's Encrypt or commercial)
  - [ ] Configure nginx with security headers
  - [ ] Test HTTPS redirect

- [ ] **Environment Variables**
  - [ ] Set all production secrets
  - [ ] Configure database encryption keys
  - [ ] Set Stripe production keys

- [ ] **Database Setup**
  - [ ] Set up production database with encryption
  - [ ] Run all migration scripts
  - [ ] Set up automated backups

- [ ] **Monitoring & Logging**
  - [ ] Configure log aggregation
  - [ ] Set up health checks
  - [ ] Configure alerting

### Pre-Launch Security Verification
- [ ] **Final Security Checklist**
  - [ ] All endpoints require authentication ✓
  - [ ] File access is restricted to owners ✓
  - [ ] Subscription limits are enforced ✓
  - [ ] Sensitive data is encrypted ✓
  - [ ] Audit logging is working ✓
  - [ ] Rate limiting is active ✓
  - [ ] HTTPS is enforced ✓
  - [ ] Security headers are set ✓

## ESTIMATED TIMELINE

### Critical Path (8-10 weeks)
- **Weeks 1-2:** Authentication system
- **Weeks 3-4:** Subscription management  
- **Weeks 5-6:** Data encryption & frontend security
- **Weeks 7-8:** Production infrastructure
- **Weeks 9-10:** Testing & compliance

### Resource Requirements
- **Developer Time:** 400-500 hours
- **DevOps Time:** 100-150 hours
- **Security Review:** 40-60 hours
- **Testing:** 80-120 hours

## SUCCESS CRITERIA

### Week 4 Milestone (MVP Security)
- [ ] Users can register and login
- [ ] Upload endpoint requires authentication
- [ ] Basic subscription limits enforced
- [ ] Frontend vulnerabilities resolved

### Week 8 Milestone (Production Ready)
- [ ] All data encrypted at rest
- [ ] Rate limiting implemented
- [ ] Audit logging active
- [ ] Production infrastructure ready

### Week 10 Milestone (Compliance Ready)
- [ ] GDPR compliance features
- [ ] Security testing complete
- [ ] Monitoring and alerting active
- [ ] Documentation complete

This checklist provides a clear roadmap for implementing all security recommendations from the application review. Each task is specific and actionable, with code examples and clear acceptance criteria.
