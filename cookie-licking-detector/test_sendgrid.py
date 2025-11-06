#!/usr/bin/env python3
"""
Test SendGrid API Key and Email Configuration
Checks if SendGrid is responding and can send emails
"""
import os
import sys
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

# Load configuration from .env
from dotenv import load_dotenv
load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")

def test_sendgrid_connection():
    """Test basic SendGrid API connection"""
    print("=" * 60)
    print("SendGrid Connection Test")
    print("=" * 60)
    
    # Check if API key is configured
    if not SENDGRID_API_KEY:
        print("❌ SENDGRID_API_KEY not found in .env file")
        return False
    
    print(f"✓ API Key: {SENDGRID_API_KEY[:10]}...{SENDGRID_API_KEY[-10:]}")
    print(f"✓ From Email: {FROM_EMAIL}")
    print()
    
    try:
        # Initialize SendGrid client
        print("Initializing SendGrid client...")
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        print("✓ SendGrid client initialized successfully")
        print()
        
        # Test API key validity by checking API key scopes
        print("Testing API key validity...")
        response = sg.client.api_keys._(SENDGRID_API_KEY.split('.')[1]).get()
        
        if response.status_code == 200:
            print(f"✓ API key is valid (Status: {response.status_code})")
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            
    except Exception as e:
        error_message = str(e)
        print(f"❌ Error validating API key: {error_message}")
        
        # Parse error for more details
        if "401" in error_message or "Unauthorized" in error_message:
            print("\n💡 The API key appears to be invalid or expired.")
            print("   Please check your SendGrid account and generate a new API key.")
        elif "403" in error_message or "Forbidden" in error_message:
            print("\n💡 The API key doesn't have the required permissions.")
            print("   Please ensure your API key has 'Mail Send' permissions.")
        
        return False
    
    print()
    return True


def test_send_email(to_email: str = None):
    """Test sending an actual email"""
    print("=" * 60)
    print("SendGrid Email Send Test")
    print("=" * 60)
    
    if not to_email:
        to_email = input("Enter test email address (or press Enter to skip): ").strip()
        
    if not to_email:
        print("⏭️  Skipping email send test")
        return True
    
    print(f"\nSending test email to: {to_email}")
    
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        
        # Create test email
        message = Mail(
            from_email=Email(FROM_EMAIL, "Cookie-Licking Detector Test"),
            to_emails=To(to_email),
            subject="🍪 SendGrid Test Email - Cookie-Licking Detector",
            html_content=Content("text/html", """
                <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h1 style="color: #4299e1;">🍪 SendGrid Test Successful!</h1>
                    <p>This is a test email from the Cookie-Licking Detector system.</p>
                    <p>If you're reading this, your SendGrid configuration is working correctly! ✅</p>
                    <hr>
                    <p style="color: #718096; font-size: 14px;">
                        Sent from Cookie-Licking Detector test script
                    </p>
                </body>
                </html>
            """),
            plain_text_content=Content("text/plain", """
                🍪 SendGrid Test Successful!
                
                This is a test email from the Cookie-Licking Detector system.
                If you're reading this, your SendGrid configuration is working correctly! ✅
                
                ---
                Sent from Cookie-Licking Detector test script
            """)
        )
        
        # Send email
        print("Sending email...")
        response = sg.send(message)
        
        print()
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code in [200, 201, 202]:
            print(f"\n✅ Email sent successfully!")
            print(f"   Status: {response.status_code}")
            print(f"   Check {to_email} for the test email")
            return True
        else:
            print(f"\n⚠️  Unexpected status code: {response.status_code}")
            print(f"   Response Body: {response.body}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error sending email: {e}")
        return False


def main():
    """Run all SendGrid tests"""
    print("\n🔍 Testing SendGrid Configuration\n")
    
    # Test 1: Connection and API key validity
    connection_ok = test_sendgrid_connection()
    
    if not connection_ok:
        print("\n" + "=" * 60)
        print("⚠️  SendGrid connection test failed")
        print("Please fix the issues above before testing email sending")
        print("=" * 60)
        sys.exit(1)
    
    # Test 2: Send test email (optional)
    print()
    email_ok = test_send_email()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Connection Test: {'✅ PASS' if connection_ok else '❌ FAIL'}")
    print(f"Email Send Test: {'✅ PASS' if email_ok else '⏭️  SKIPPED'}")
    print("=" * 60)
    
    if connection_ok:
        print("\n✅ SendGrid is configured and responding!")
        print("Your API key is valid and can be used for sending emails.")
    else:
        print("\n❌ SendGrid configuration has issues")
        print("Please review the errors above and fix your configuration.")
        sys.exit(1)


if __name__ == "__main__":
    main()
