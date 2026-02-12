# EmailJS Setup Guide

EmailJS is an email service that works via HTTP API (perfect for Railway deployment).

## Step 1: Create EmailJS Account

1. Go to https://www.emailjs.com/
2. Sign up for a free account (200 emails/month free)
3. Verify your email address

## Step 2: Create Email Service

1. In EmailJS dashboard, go to **Email Services**
2. Click **Add New Service**
3. Choose **Gmail** (or your preferred email provider)
4. Connect your Gmail account (zenvia07@gmail.com)
5. Copy the **Service ID** (e.g., `service_xxxxx`)

## Step 3: Create Email Template

1. Go to **Email Templates**
2. Click **Create New Template**
3. **Use the template from `EMAILJS_TEMPLATES.md`** (see that file for complete templates)

**Quick Template (Copy this):**

**Subject:**
```
{{subject}}
```

**Content (HTML):**
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .button {
            background-color: #6366f1;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 8px;
            display: inline-block;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <h2 style="color: #6366f1;">Hello {{to_name}},</h2>
    
    {{#message_html}}
    {{message_html}}
    {{/message_html}}
    
    {{#activation_url}}
    <div style="text-align: center; margin: 30px 0;">
        <a href="{{activation_url}}" class="button">Activate Account</a>
    </div>
    <p style="word-break: break-all; color: #666;">{{activation_url}}</p>
    {{/activation_url}}
    
    {{#reset_url}}
    <div style="text-align: center; margin: 30px 0;">
        <a href="{{reset_url}}" class="button">Reset Password</a>
    </div>
    <p style="word-break: break-all; color: #666;">{{reset_url}}</p>
    {{/reset_url}}
    
    <p style="color: #999; font-size: 12px; margin-top: 30px;">
        If you didn't request this, please ignore this email.
    </p>
</body>
</html>
```

4. **Paste into EmailJS template editor**
5. **Save the template**
6. Copy the **Template ID** (e.g., `template_xxxxx`)

**Note:** See `EMAILJS_TEMPLATES.md` for detailed templates with better formatting.

## Step 4: Get Public Key

1. Go to **Account** → **General**
2. Copy your **Public Key** (e.g., `xxxxxxxxxxxxx`)

## Step 5: Add to Railway Variables

Add these 3 variables to your Railway project:

1. **EMAILJS_SERVICE_ID** = Your Service ID (e.g., `service_xxxxx`)
2. **EMAILJS_TEMPLATE_ID** = Your Template ID (e.g., `template_xxxxx`)
3. **EMAILJS_PUBLIC_KEY** = Your Public Key (e.g., `xxxxxxxxxxxxx`)

## Step 6: Test

After adding the variables, Railway will redeploy automatically. Try registering a new account and check if you receive the activation email!

## Notes

- EmailJS free tier: 200 emails/month
- Works perfectly on Railway (HTTP API, no SMTP blocking)
- No need for SMTP credentials anymore
- Emails will be sent from your connected Gmail account
