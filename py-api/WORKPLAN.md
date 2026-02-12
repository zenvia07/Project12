# Login Page Project - Workplan
TASK :
=====
1. User Registration with the following fields: first_name, last_name, date_of_birth, email, phone_number, and password.
2. After registration, send an activation email to the registered email address.
3. Allow the user to log in only after account activation.
4. Provide options for Change Password and Forgot Password. Do not allow the new password to match any of the last three previously used passwords.
5. If a user attempts to log in with an incorrect password for three consecutive attempts, lock the user account.
6. Implement a Refresh Token mechanism for API authorization.
7. Add a cache layer for frequently used APIs.
8. Implement a rate limiter to prevent unnecessary multiple API hits.
9. Implement pagination for summary data APIs.
10. Maintain a proper project structure and Dockerize the application.
## Project Overview
A user-friendly login page with FastAPI backend and modern frontend, deployable on Vercel with database integration.
## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: MongoDB (MongoDB Atlas for production)
- **Authentication**: JWT tokens
- **Password Hashing**: bcrypt
- **Database Driver**: Motor (async MongoDB driver) or pymongo
- **Deployment**: Vercel Serverless Functions

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with CSS Grid/Flexbox
- **JavaScript**: Vanilla JS (or can use a framework)
- **API Communication**: Fetch API

---

## BACKEND WORKPLAN

### Phase 1: Project Setup & Structure
- [ ] Create project directory structure
- [ ] Initialize Python virtual environment
- [ ] Create `requirements.txt` with dependencies:
  - fastapi
  - uvicorn
  - motor (async MongoDB driver) or pymongo
  - bcrypt
  - python-jose (JWT)
  - python-multipart
  - pydantic
  - dnspython (for MongoDB connection string)
- [ ] Create `vercel.json` configuration for Vercel deployment
- [ ] Create `.env.example` for environment variables

### Phase 2: Database Setup
- [ ] Set up MongoDB connection (Motor async client)
- [ ] Create database connection utility
- [ ] Create User document schema/model:
  - _id (MongoDB ObjectId)
  - email (unique, indexed)
  - username (unique, indexed)
  - hashed_password
  - created_at (datetime)
  - is_active (boolean)
- [ ] Create database initialization script
- [ ] Set up MongoDB indexes (email, username)
- [ ] Create collection helper functions

### Phase 3: Authentication System
- [ ] Create password hashing utilities (bcrypt)
- [ ] Create JWT token generation/verification functions
- [ ] Create user registration endpoint (`POST /api/register`)
  - Validate input (email, username, password)
  - Check for existing users
  - Hash password
  - Save to database
  - Return success response
- [ ] Create login endpoint (`POST /api/login`)
  - Validate credentials
  - Verify password
  - Generate JWT token
  - Return token and user info
- [ ] Create protected route decorator/middleware
- [ ] Create user profile endpoint (`GET /api/me`) - protected

### Phase 4: API Endpoints
- [ ] Health check endpoint (`GET /api/health`)
- [ ] CORS configuration for frontend
- [ ] Error handling middleware
- [ ] Request validation with Pydantic models
- [ ] Response models

### Phase 5: Vercel Configuration
- [ ] Configure `vercel.json` for serverless functions
- [ ] Set up environment variables handling
- [ ] Test local Vercel deployment (`vercel dev`)
- [ ] Configure database connection for Vercel environment

---

## FRONTEND WORKPLAN

### Phase 1: Project Structure
- [ ] Create frontend directory structure
- [ ] Set up HTML file (`index.html`)
- [ ] Create CSS directory and main stylesheet
- [ ] Create JavaScript directory and main script
- [ ] Set up asset directories (images, icons)

### Phase 2: HTML Structure
- [ ] Create semantic HTML5 structure
- [ ] Build login form with:
  - Email/Username input
  - Password input
  - Submit button
  - Link to registration (if needed)
- [ ] Add form validation attributes
- [ ] Create registration form (optional)
- [ ] Add loading states placeholders
- [ ] Add error message containers

### Phase 3: CSS Styling
- [ ] Reset/normalize CSS
- [ ] Create responsive layout (mobile-first)
- [ ] Design login form:
  - Centered layout
  - Card-based design
  - Modern input fields
  - Button styling
  - Hover/focus states
- [ ] Add animations and transitions
- [ ] Create error/success message styles
- [ ] Add loading spinner styles
- [ ] Ensure accessibility (focus states, contrast)

### Phase 4: JavaScript Functionality
- [ ] Create API service module:
  - Base URL configuration
  - Login function
  - Registration function (if needed)
  - Token storage (localStorage)
  - Error handling
- [ ] Create form validation:
  - Client-side validation
  - Email format validation
  - Password strength (optional)
  - Real-time feedback
- [ ] Create form submission handler:
  - Prevent default form submission
  - Show loading state
  - Call API
  - Handle success/error responses
  - Redirect on success
- [ ] Create UI state management:
  - Show/hide error messages
  - Toggle password visibility
  - Loading indicators
- [ ] Add token management:
  - Store token on login
  - Check for existing token on page load
  - Redirect if already logged in

### Phase 5: User Experience Enhancements
- [ ] Add form field animations
- [ ] Implement password visibility toggle
- [ ] Add "Remember me" functionality
- [ ] Create success/error toast notifications
- [ ] Add loading states for better UX
- [ ] Implement auto-redirect after login
- [ ] Add keyboard navigation support

### Phase 6: Integration & Testing
- [ ] Connect frontend to backend API
- [ ] Test login flow end-to-end
- [ ] Test error scenarios
- [ ] Test responsive design on multiple devices
- [ ] Cross-browser testing
- [ ] Accessibility testing

---

## DEPLOYMENT WORKPLAN

### Phase 1: Vercel Setup
- [ ] Create Vercel account (if needed)
- [ ] Install Vercel CLI
- [ ] Configure `vercel.json`:
  - Build settings
  - Serverless function routes
  - Environment variables
  - Headers and CORS

### Phase 2: Database Setup (Production)
- [ ] Set up MongoDB Atlas account (free tier available)
- [ ] Create MongoDB cluster
- [ ] Configure database connection string (MONGODB_URI)
- [ ] Set up database user and password
- [ ] Configure IP whitelist (or allow all for Vercel)
- [ ] Test database connection
- [ ] Create indexes in MongoDB Atlas

### Phase 3: Environment Variables
- [ ] Set up environment variables in Vercel dashboard:
  - MONGODB_URI (MongoDB connection string)
  - MONGODB_DB_NAME (database name)
  - JWT_SECRET_KEY
  - JWT_ALGORITHM
- [ ] Configure for both development and production

### Phase 4: Deployment
- [ ] Deploy backend to Vercel
- [ ] Deploy frontend (static files)
- [ ] Test deployed application
- [ ] Configure custom domain (optional)

---

## PROJECT STRUCTURE

```
Project/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── auth.py
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       └── users.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── assets/
├── vercel.json
├── .gitignore
└── README.md
```

---

## NEXT STEPS

1. **Start with Backend Phase 1**: Set up project structure and dependencies
2. **Then Backend Phase 2**: Create database models
3. **Then Backend Phase 3**: Implement authentication
4. **Then Frontend Phase 1-3**: Build UI
5. **Then Frontend Phase 4**: Add functionality
6. **Finally**: Deploy and test

---

## NOTES

- Vercel supports Python serverless functions via `vercel.json`
- MongoDB Atlas offers a free tier (M0 cluster) perfect for development and small production apps
- Use Motor (async) for better performance with FastAPI, or pymongo (sync) for simplicity
- JWT tokens should be stored securely (httpOnly cookies recommended for production)
- Add rate limiting for login attempts (security)
- Consider adding email verification for production use
- MongoDB connection pooling is handled automatically by Motor/pymongo
