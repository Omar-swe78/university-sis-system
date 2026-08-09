import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import url_for, request
from config import SMTP_EMAIL, SMTP_PASSWORD, SMTP_SERVER, SMTP_PORT, DEVELOPMENT_MODE

def send_email(subject, body, to_email):
    """Send email using SMTP configuration"""
    # In development mode, if using placeholder credentials, skip actual email sending
    if DEVELOPMENT_MODE and (SMTP_EMAIL == 'your_email@gmail.com' or SMTP_PASSWORD == 'your_app_password'):
        print(f"[DEV MODE] Email would be sent to {to_email}")
        print(f"[DEV MODE] Subject: {subject}")
        print(f"[DEV MODE] Body: {body}")
        return True
    
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
        server.quit()
        
        print(f"Email sent successfully to {to_email}")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication Error: {e}")
        print("Please check your email credentials in config.py or environment variables")
        return False
    except smtplib.SMTPException as e:
        print(f"SMTP Error: {e}")
        return False
    except Exception as e:
        print(f"Email sending error: {e}")
        return False

def send_verification_email(user):
    """Send account verification email"""
    try:
        verify_link = request.url_root.rstrip('/') + url_for('auth.verify_email', token=user.verify_token)
        
        subject = 'Verify your UniversityApp account'
        body = f"""Hello {user.name},

Thank you for signing up for UniversityApp!

Please verify your account by clicking the link below:
{verify_link}

This link will expire in 24 hours for security reasons.

If you did not sign up for this account, please ignore this email.

Best regards,
University Management System Team"""
        
        return send_email(subject, body, user.email)
    except Exception as e:
        print(f"Verification email error: {e}")
        return False

def send_password_reset_email(user, reset_token):
    """Send password reset email"""
    try:
        reset_link = request.url_root.rstrip('/') + url_for('auth.reset_password', token=reset_token)
        
        subject = 'Reset your UniversityApp password'
        body = f"""Hello {user.name},

You have requested to reset your password for UniversityApp.

Please click the link below to reset your password:
{reset_link}

This link will expire in 1 hour for security reasons.

If you did not request this password reset, please ignore this email.

Best regards,
University Management System Team"""
        
        return send_email(subject, body, user.email)
    except Exception as e:
        print(f"Password reset email error: {e}")
        return False

def send_notification_email(to_email, subject, message):
    """Send general notification email"""
    try:
        body = f"""Hello,

{message}

Best regards,
University Management System Team"""
        
        return send_email(subject, body, to_email)
    except Exception as e:
        print(f"Notification email error: {e}")
        return False

