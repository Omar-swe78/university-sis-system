# Email Setup Guide

## Development Mode (Default)

The application is configured to run in development mode by default, which means:

- Email verification is simulated (logged to console)
- Users can sign in without email verification
- No actual emails are sent

## Production Email Setup

To enable actual email sending in production, you need to:

### 1. Set Environment Variables

Set the following environment variables with your actual email credentials:

```bash
# For Gmail
export SMTP_EMAIL="415webdev@gmail.com"
export SMTP_PASSWORD="xbeb yhzb hawz otyo"
export SMTP_SERVER="415webdev@gmail.com"
export SMTP_PORT="587"
export DEVELOPMENT_MODE="false"

# For Outlook/Hotmail
export SMTP_EMAIL="415webdev@gmail.com"
export SMTP_PASSWORD="xbeb yhzb hawz otyo"
export SMTP_SERVER="415webdev@gmail.com"
export SMTP_PORT="587"
export DEVELOPMENT_MODE="false"
```

### 2. Gmail App Password Setup

If using Gmail, you need to create an App Password:

1. Go to your Google Account settings
2. Enable 2-Factor Authentication
3. Go to Security → App passwords
4. Generate a new app password for "Mail"
5. Use this password as `SMTP_PASSWORD`

### 3. Alternative: Update config.py

You can also directly update the `config.py` file:

```python
# Replace these with your actual credentials
SMTP_EMAIL = 'nirvanafanboy03@gmail.com'
SMTP_PASSWORD = 'xbeb yhzb hawz otyo'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

# Set development mode to False
DEVELOPMENT_MODE = False
```

### 4. Test Email Functionality

After setup, test the email functionality by:

1. Creating a new account
2. Checking if verification email is received
3. Verifying the account through the email link

## Troubleshooting

### Common Issues:

1. **Authentication Error**: Check your email and password
2. **Connection Error**: Verify SMTP server and port
3. **Gmail Security**: Make sure to use App Password, not regular password
4. **Firewall**: Ensure port 587 is not blocked

### Debug Mode:

To see detailed email logs, check the console output when running the application.

## Security Notes

- Never commit real email credentials to version control
- Use environment variables for production deployments
- Consider using email service providers like SendGrid or Mailgun for better reliability 

---

Thank you for clarifying! Here’s a step-by-step diagnosis and solution for your SMTP (Gmail) email verification issue:

---

## 1. **Gmail App Passwords:**
You are using an app password (`xbeb yhzb hawz otyo`), which is correct.  
**Make sure:**
- 2-Step Verification is enabled on your Google account.
- The app password is generated for “Mail” and “Windows Computer” (or similar).

---

## 2. **SMTP Settings in `config.py`:**
Your config should look like this:
```python
SMTP_EMAIL = '415webdev@gmail.com'
SMTP_PASSWORD = 'xbeb yhzb hawz otyo'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
DEVELOPMENT_MODE = False
```
**If you use environment variables, make sure they are set and not being overridden.**

---

## 3. **Firewall/Network Issues:**
- Make sure your network/firewall allows outbound connections to `smtp.gmail.com:587`.

---

## 4. **Code: Add SMTP Debugging**
Let’s add SMTP debug output to see exactly what’s going wrong.  
**Edit `utils/email_utils.py`** in the `send_email` function:

Replace:
```python
server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
server.starttls()
server.login(SMTP_EMAIL, SMTP_PASSWORD)
server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
server.quit()
```
With:
```python
server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
server.set_debuglevel(1)  # <--- Add this line for debug output
server.starttls()
server.login(SMTP_EMAIL, SMTP_PASSWORD)
server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
server.quit()
```
This will print the full SMTP conversation to your terminal, so you can see exactly where it fails.

---

## 5. **Try Sending a Test Email**
After making the above change, try signing up again and watch the terminal for detailed SMTP output.  
**If you see an error like:**
- `SMTPAuthenticationError`: Double-check the app password and email.
- `smtplib.SMTPServerDisconnected` or `timeout`: Check your network/firewall.

---

## 6. **If You Still Have Issues**
Please copy and paste the full SMTP debug output (from the terminal) here.  
**This will help pinpoint the exact problem.**

---

### Here’s the code change for you:

```python
<code_block_to_apply_from>
```

---

**Make this change, try again, and let me know what the terminal prints!**  
If you want, I can make this code change for you automatically—just let me know! 