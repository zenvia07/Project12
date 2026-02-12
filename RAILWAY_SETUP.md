# Railway Deployment - Environment Variables Setup

## ⚠️ IMPORTANT: You MUST add these environment variables in Railway!

The application requires these environment variables to be set in Railway's dashboard. Without them, the application will fail to start.

## How to Add Environment Variables in Railway:

1. Go to your Railway project dashboard
2. Click on your service (the deployed app)
3. Go to the **Variables** tab
4. Click **"New Variable"** or **"Raw Editor"** (for bulk adding)
5. Add each variable one by one, OR paste all variables from `py-api/RAILWAY_ENV_VARIABLES.txt`

## Required Environment Variables:

Copy these from `py-api/RAILWAY_ENV_VARIABLES.txt` and **REPLACE THE PLACEHOLDER VALUES** with your actual values:

```
MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?appName=Cluster0
MONGODB_DB_NAME=login_app
JWT_SECRET_KEY=your-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
ENVIRONMENT=production
API_PREFIX=/api
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
EMAIL_FROM=noreply@yourapp.com
RATE_LIMIT_PER_MINUTE=60
CACHE_TTL_SECONDS=300
```

## Critical Variables to Update:

1. **MONGODB_URI** - Your MongoDB Atlas connection string
2. **JWT_SECRET_KEY** - Generate a secure random key (use: `openssl rand -hex 32` or any random string)
3. **SMTP_USER** - Your email address
4. **SMTP_PASSWORD** - Your email app password (for Gmail, create an App Password)
5. **EMAIL_FROM** - The sender email address

## After Adding Variables:

1. Railway will automatically redeploy when you save the variables
2. Check the deployment logs to verify the application starts successfully
3. If you see errors about missing fields, double-check that all variables are set correctly

## Quick Test:

After adding variables, check the logs. You should see:
- `[SUCCESS] Connected to MongoDB: login_app`
- Application starting on the assigned port

If you see `Field required` errors, it means the environment variables are not set correctly in Railway.
