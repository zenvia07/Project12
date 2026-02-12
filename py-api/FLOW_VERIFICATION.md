# Registration and Activation Flow Verification

## Complete Flow

### Step 1: User Fills Signup Form
- User enters: first_name, last_name, date_of_birth, email, phone_number, password
- Form data is collected in `frontend/js/main.js` → `handleRegister()`

### Step 2: Data Stored in Database
- Data is sent to `/api/register` endpoint
- Backend validates the data
- User document is created in MongoDB with:
  - All form fields (first_name, last_name, date_of_birth, email, phone_number)
  - Hashed password
  - is_active: False (not activated yet)
  - Activation token generated
- **Location**: `backend/app/routers/auth.py` → `register()` → `create_user()`

### Step 3: Activation Email Sent
- Email is sent to the email address stored in the database
- Email contains activation link with token
- **Location**: `backend/app/email_service.py` → `send_activation_email()`
- Email sent TO: The email from the database (user's registered email)
- Email sent FROM: zenvia07@gmail.com (SMTP account)

### Step 4: User Clicks Activation Link
- User receives email and clicks activation link
- Link format: `http://localhost:3000/?token={activation_token}`
- Frontend detects token in URL and shows activation page

### Step 5: Account Activation
- Frontend calls `/api/activate` with the token
- Backend validates token and activates account
- Account status changed: `is_active: True`

### Step 6: Redirect to Login Page
- After successful activation, user is redirected to login page
- URL parameters are cleared
- Login form is displayed
- **Location**: `frontend/js/main.js` → `activateAccount()` → `showLoginContainer()`

## Code Flow

```
1. User fills form → handleRegister()
2. POST /api/register → register()
3. create_user() → Saves to MongoDB
4. send_activation_email() → Sends email to database email
5. User clicks link → activateAccount()
6. POST /api/activate → activate_account()
7. activate_user() → Sets is_active: True
8. showLoginContainer() → Shows login page
```

## Verification Points

✅ Form data is stored in database
✅ Email is sent to the email stored in database
✅ After activation, user is redirected to login page
✅ All fields from signup form are saved
✅ Activation token is generated and stored
✅ Account is inactive until activation
