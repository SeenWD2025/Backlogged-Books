# Production Readiness Checklist

This checklist outlines the steps to implement user authentication, subscription management, and prepare the application for a production launch.

---

## Phase 1: Backend - User Authentication Setup

**Goal:** Implement a secure authentication system using `fastapi-users`.

- [ ] **1. Install Dependencies:**
  - Add `fastapi-users[sqlalchemy]` to `requirements.txt`.
  - Add `passlib[bcrypt]` for password hashing to `requirements.txt`.
  - Rebuild the backend container to install the new packages: `docker-compose up --build -d backend`.

- [ ] **2. Configure Settings:**
  - **File:** `afsp_app/app/settings.py`
  - **Action:** Add a `SECRET_KEY` for JWT token generation. Use a strong, randomly generated secret.

- [ ] **3. Update Database Model:**
  - **File:** `afsp_app/app/database.py`
  - **Action:**
    - Import `SQLAlchemyBaseUserTable` from `fastapi_users_db_sqlalchemy`.
    - Define a `User` table class that inherits from it, adding any custom fields if necessary (e.g., `subscription_tier`, `upload_count`).
    - Ensure the `User` table is created along with other tables at startup.

- [ ] **4. Define Data Schemas:**
  - **File:** `afsp_app/app/schemas.py`
  - **Action:**
    - Import `BaseUser`, `BaseUserCreate`, `BaseUserUpdate` from `fastapi-users`.
    - Create `UserRead`, `UserCreate`, and `UserUpdate` schemas inheriting from the base schemas.

- [ ] **5. Implement Authentication Logic:**
  - **File:** `afsp_app/app/auth.py` (Create this new file)
  - **Action:**
    - Set up the `AuthenticationBackend` with a JWT strategy.
    - Create the `get_user_manager` dependency.
    - Instantiate `FastAPIUsers` with the user manager and auth backend.

- [ ] **6. Integrate Auth Routes:**
  - **File:** `afsp_app/app/main.py`
  - **Action:**
    - Import the `fastapi_users` instance and the schemas from `auth.py`.
    - Include the authentication router: `app.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"])`.
    - Include the registration router: `app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"])`.
    - Include the user management router: `app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"])`.

- [ ] **7. Secure the Upload Endpoint:**
  - **File:** `afsp_app/app/main.py`
  - **Action:**
    - Import the `current_user` dependency: `fastapi_users.current_user()`.
    - Add the dependency to the `/upload` endpoint signature to require authentication.
    - **(Defer to Phase 3)** Add logic to check the user's `upload_count` against their `subscription_tier`.

---

## Phase 2: Frontend - User Authentication UI

**Goal:** Connect the React frontend to the new authentication system.

- [ ] **1. Create an Authentication Context:**
  - **File:** `frontend/src/context/AuthContext.js` (Create this new file)
  - **Action:**
    - Build a React context to manage user state, JWT token, and authentication status (`isAuthenticated`).
    - Provide `login`, `logout`, and `register` functions that will call the backend API.

- [x] **2. Update API Service:** ✅ **COMPLETED**
  - **File:** `frontend/src/services/api.js`
  - **Action:**
    - Add functions for `login(email, password)`, `register(...)`, and `getCurrentUser()`.
    - Use an Axios interceptor to automatically add the `Authorization: Bearer <token>` header to all authenticated requests.
  - **Status:** Complete HTTPS configuration, authentication functions implemented, automatic token management with interceptors, and token expiration handling with redirect logic.

- [ ] **3. Create Authentication Pages:**
  - **File:** `frontend/src/pages/LoginPage.js` (Create new file)
  - **File:** `frontend/src/pages/RegisterPage.js` (Create new file)
  - **Action:** Build simple forms for user login and registration.

- [x] **4. Update Application Routing:** ✅ **COMPLETED**
  - **File:** `frontend/src/App.js`
  - **Action:**
    - Wrap the entire application with the `AuthProvider` from `AuthContext.js`.
    - Add routes for `/login` and `/register`.
    - Create a `ProtectedRoute` component that checks `isAuthenticated` from the context and redirects to `/login` if the user is not authenticated.
    - Wrap the `/upload` and `/jobs` routes with `ProtectedRoute`.
  - **Status:** Complete authentication routing implemented with AuthProvider wrapping, login/register routes, ProtectedRoute component with authentication checking and redirect logic, and all protected routes (/upload, /jobs, /jobs/:jobId, /settings) properly wrapped.

- [ ] **5. Update UI Elements:**
  - **File:** `frontend/src/components/Header.js`
  - **Action:**
    - Use the `AuthContext` to conditionally display "Login" and "Register" links or a "Logout" button and user information.

---

## Phase 3: Backend - Subscription & Payment System

**Goal:** Integrate Stripe for subscription payments.

- [ ] **1. Install Stripe SDK:**
  - Add `stripe` to `requirements.txt`.
  - Rebuild the backend container.

- [ ] **2. Configure Stripe:**
  - **File:** `afsp_app/app/settings.py`
  - **Action:** Add your Stripe API keys (`STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`) and Price IDs for your subscription plans.

- [ ] **3. Create Stripe Service:**
  - **File:** `afsp_app/app/services/stripe_service.py` (Create new file)
  - **Action:** Implement a function to create a Stripe Checkout session for a given user and price ID.

- [ ] **4. Create Payment Endpoints:**
  - **File:** `afsp_app/app/main.py`
  - **Action:**
    - Add a protected endpoint `/create-checkout-session` that takes a Price ID and creates a Stripe Checkout session.
    - Add a public endpoint `/stripe-webhook` to receive events from Stripe.

- [ ] **5. Implement Webhook Logic:**
  - **File:** `afsp_app/app/main.py` (in the webhook endpoint)
  - **Action:**
    - Verify the webhook signature to ensure it's from Stripe.
    - Handle the `checkout.session.completed` event.
    - When the event is received, update the user's record in the database with their new `subscription_tier` and reset their `upload_count`.

---

## Phase 4: Frontend - Subscription UI

**Goal:** Allow users to view and manage their subscriptions.

- [ ] **1. Create Subscription Page:**
  - **File:** `frontend/src/pages/SubscriptionPage.js` (Create new file)
  - **Action:**
    - Display the available subscription plans (e.g., Free, Basic, Premium).
    - Each plan should have a "Subscribe" or "Upgrade" button that calls the `/create-checkout-session` endpoint and redirects the user to the Stripe Checkout page.

- [ ] **2. Create Profile Page:**
  - **File:** `frontend/src/pages/ProfilePage.js` (Create new file)
  - **Action:**
    - Display the user's current subscription tier.
    - Show their current usage (e.g., "You have used 3 of 5 uploads this month").

- [ ] **3. Update Routing and Navigation:**
  - **File:** `frontend/src/App.js` & `frontend/src/components/Header.js`
  - **Action:** Add routes and links for the new `/subscriptions` and `/profile` pages.

---

## Phase 5: Final Review and Deployment

**Goal:** Ensure the application is robust and ready for launch.

- [ ] **1. Full End-to-End Testing:**
  - **Action:** Manually test the entire user journey:
    1. Register a new account.
    2. Log in.
    3. Verify access to protected pages.
    4. Go to the subscription page and purchase a plan.
    5. Verify the subscription status is updated on the profile page.
    6. Upload files and confirm usage limits are working.
    7. Log out.

- [ ] **2. Environment Variable Configuration:**
  - **Action:** Create a final `.env` file for production with real `SECRET_KEY` and `STRIPE` keys. Ensure this file is in `.gitignore` and managed securely.

- [ ] **3. Deploy to Production:**
  - **Action:** Use the `docker-compose.prod.yml` file to build and deploy the application to your production server.

- [ ] **4. Final Sanity Check:**
  - **Action:** Access the live URL and perform a quick test of the core features (login, upload) to ensure everything is working as expected.
