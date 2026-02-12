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
3. Choose a template or start from scratch
4. Set up your template with these variables:
   - `{{to_email}}` - Recipient email
   - `{{to_name}}` - Recipient name
   - `{{subject}}` - Email subject
   - `{{message_html}}` - HTML email content
   - `{{activation_url}}` - Activation link (for activation emails)
   - `{{reset_url}}` - Reset link (for password reset emails)

**Example Template:**
```
Subject: {{subject}}

Hello {{to_name}},

{{message_html}}
```

5. Copy the **Template ID** (e.g., `template_xxxxx`)

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
