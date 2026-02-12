# EmailJS Email Templates

Copy these templates into your EmailJS dashboard.

## Template 1: Activation Email Template

**Template Name:** Account Activation

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
        .footer {
            color: #999;
            font-size: 12px;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }
    </style>
</head>
<body>
    <h2 style="color: #6366f1;">Hello {{to_name}},</h2>
    
    <p>Thank you for registering with our service!</p>
    
    <p>Please activate your account by clicking the button below:</p>
    
    <div style="text-align: center; margin: 30px 0;">
        <a href="{{activation_url}}" class="button">Activate Account</a>
    </div>
    
    <p>Or copy and paste this link into your browser:</p>
    <p style="word-break: break-all; color: #666; background: #f5f5f5; padding: 10px; border-radius: 4px;">
        {{activation_url}}
    </p>
    
    <p style="color: #999; font-size: 12px;">This link will expire in 24 hours.</p>
    
    <div class="footer">
        <p>If you didn't create this account, please ignore this email.</p>
        <p>Best regards,<br>Login API Team</p>
    </div>
</body>
</html>
```

**Content (Plain Text):**
```
Hello {{to_name}},

Thank you for registering with our service!

Please activate your account by clicking the link below:

{{activation_url}}

This link will expire in 24 hours.

If you didn't create this account, please ignore this email.

Best regards,
Login API Team
```

---

## Template 2: Password Reset Email Template

**Template Name:** Password Reset

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
        .footer {
            color: #999;
            font-size: 12px;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }
    </style>
</head>
<body>
    <h2 style="color: #6366f1;">Hello {{to_name}},</h2>
    
    <p>You requested to reset your password. Click the button below to reset it:</p>
    
    <div style="text-align: center; margin: 30px 0;">
        <a href="{{reset_url}}" class="button">Reset Password</a>
    </div>
    
    <p>Or copy and paste this link:</p>
    <p style="word-break: break-all; color: #666; background: #f5f5f5; padding: 10px; border-radius: 4px;">
        {{reset_url}}
    </p>
    
    <p style="color: #999; font-size: 12px;">This link will expire in 1 hour.</p>
    
    <div class="footer">
        <p>If you didn't request this, please ignore this email and your password will remain unchanged.</p>
    </div>
</body>
</html>
```

**Content (Plain Text):**
```
Hello {{to_name}},

You requested to reset your password. Click the link below to reset it:

{{reset_url}}

This link will expire in 1 hour.

If you didn't request this, please ignore this email and your password will remain unchanged.
```

---

## How to Use in EmailJS:

### Option 1: Single Template (Recommended - Simpler)

Create ONE template that handles both activation and password reset:

**Template Name:** Account Emails

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
        .footer {
            color: #999;
            font-size: 12px;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
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
    <p>Or copy and paste this link:</p>
    <p style="word-break: break-all; color: #666; background: #f5f5f5; padding: 10px; border-radius: 4px;">
        {{activation_url}}
    </p>
    {{/activation_url}}
    
    {{#reset_url}}
    <div style="text-align: center; margin: 30px 0;">
        <a href="{{reset_url}}" class="button">Reset Password</a>
    </div>
    <p>Or copy and paste this link:</p>
    <p style="word-break: break-all; color: #666; background: #f5f5f5; padding: 10px; border-radius: 4px;">
        {{reset_url}}
    </p>
    {{/reset_url}}
    
    <div class="footer">
        <p>If you didn't request this, please ignore this email.</p>
        <p>Best regards,<br>Login API Team</p>
    </div>
</body>
</html>
```

**Note:** EmailJS uses Handlebars syntax. The `{{#variable}}...{{/variable}}` checks if the variable exists before displaying it.

---

## Quick Setup Steps:

1. **Go to EmailJS Dashboard** → Email Templates
2. **Click "Create New Template"**
3. **Copy the template above** (Option 1 - Single Template is easiest)
4. **Paste into EmailJS template editor**
5. **Save the template**
6. **Copy the Template ID** (starts with `template_`)
7. **Add to Railway:** `EMAILJS_TEMPLATE_ID` = your template ID

**That's it!** The code will automatically use `message_html` for the content and `activation_url` or `reset_url` for the buttons.
