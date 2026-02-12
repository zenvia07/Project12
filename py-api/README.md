# Login API - FastAPI Backend

A comprehensive user authentication and management API built with FastAPI, MongoDB, and JWT authentication.

## Features

✅ **User Registration** - Register with first_name, last_name, date_of_birth, email, phone_number, and password  
✅ **Email Activation** - Activation email sent after registration  
✅ **Secure Login** - Login only after account activation  
✅ **Password Management** - Change password and forgot password (prevents reusing last 3 passwords)  
✅ **Account Security** - Account lockout after 3 failed login attempts  
✅ **JWT Authentication** - Access tokens and refresh tokens  
✅ **Rate Limiting** - Prevents API abuse  
✅ **Caching** - Cache layer for frequently used APIs  
✅ **Pagination** - Paginated responses for list endpoints  
✅ **Modern Frontend** - Beautiful, responsive UI with vanilla JavaScript  

## Technology Stack

- **Framework**: FastAPI (Python)
- **Database**: MongoDB (MongoDB Atlas)
- **Authentication**: JWT tokens (python-jose)
- **Password Hashing**: bcrypt
- **Database Driver**: Motor (async MongoDB driver)
- **Deployment**: Docker, Vercel Serverless Functions

## Project Structure

```
py-api/
├── backend/
│   └── app/
│       ├── __init__.py
│       ├── main.py              # FastAPI application
│       ├── database.py          # MongoDB connection
│       ├── models.py            # Database models
│       ├── schemas.py           # Pydantic schemas
│       ├── auth.py              # Authentication utilities
│       ├── email_service.py     # Email sending service
│       ├── dependencies.py      # FastAPI dependencies
│       ├── middleware.py        # Rate limiting & caching
│       ├── db_helpers.py        # Database helper functions
│       └── routers/
│           ├── auth.py          # Authentication routes
│           └── users.py         # User management routes
├── frontend/
│   ├── index.html               # Main HTML file
│   ├── css/
│   │   └── style.css            # Modern CSS styling
│   ├── js/
│   │   └── main.js              # Frontend JavaScript
│   └── assets/                  # Static assets
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker configuration
├── docker-compose.yml           # Docker Compose configuration
├── vercel.json                  # Vercel deployment config
└── .env                         # Environment variables
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?appName=Cluster0
MONGODB_DB_NAME=login_app
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@yourapp.com
```

### 3. Run Locally

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Then open your browser and visit: **http://localhost:8000**

The frontend will be served automatically!

### 4. Run with Docker

```bash
docker-compose up --build
```

## API Endpoints

### Authentication

- `POST /api/register` - Register a new user
- `POST /api/activate` - Activate user account
- `POST /api/login` - User login
- `POST /api/refresh` - Refresh access token
- `POST /api/change-password` - Change password (requires auth)
- `POST /api/forgot-password` - Request password reset
- `POST /api/reset-password` - Reset password with token
- `GET /api/me` - Get current user info (requires auth)

### Users

- `GET /api/profile` - Get user profile (requires auth)
- `GET /api/list` - List users with pagination (requires auth)

### Health

- `GET /` - Root endpoint
- `GET /api/health` - Health check

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Security Features

- **Password Hashing**: bcrypt with salt
- **JWT Tokens**: Secure token-based authentication
- **Account Lockout**: Automatic lockout after 3 failed login attempts
- **Password History**: Prevents reusing last 3 passwords
- **Rate Limiting**: Prevents brute force attacks
- **Email Verification**: Account activation required before login

## Database

The application uses MongoDB with the following collections:

- **users**: User accounts with authentication data

Indexes are automatically created on:
- `email` (unique)
- `phone_number` (unique, sparse)
- `is_active`
- `created_at`

## Development

### Running Tests

```bash
# Test database connection
python test_db_simple.py
```

### Code Structure

- **Models** (`models.py`): MongoDB document schemas
- **Schemas** (`schemas.py`): Request/response validation
- **Auth** (`auth.py`): Password hashing and JWT utilities
- **Routers** (`routers/`): API endpoint handlers
- **Database** (`database.py`): MongoDB connection and setup

## Deployment

### Vercel

1. Install Vercel CLI: `npm i -g vercel`
2. Deploy: `vercel`
3. Set environment variables in Vercel dashboard

### Docker

```bash
docker build -t login-api .
docker run -p 8000:8000 --env-file .env login-api
```

## License

MIT
