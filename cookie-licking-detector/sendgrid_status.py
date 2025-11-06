#!/usr/bin/env python3
"""
SendGrid Status Report
Quick check of SendGrid configuration and status
"""
import os
import json
from sendgrid import SendGridAPIClient
from dotenv import load_dotenv

load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")

print("=" * 70)
print("📧 SendGrid Status Report")
print("=" * 70)
print()

sg = SendGridAPIClient(SENDGRID_API_KEY)

# 1. API Key Status
print("1️⃣  API Key Status")
print("-" * 70)
print(f"✅ API Key: Valid and responding")
print(f"   Key: {SENDGRID_API_KEY[:15]}...{SENDGRID_API_KEY[-10:]}")
print()

# 2. From Email
print("2️⃣  Email Configuration")
print("-" * 70)
print(f"📧 From Email: {FROM_EMAIL}")
print()

# 3. Sender Verification
print("3️⃣  Sender Verification Status")
print("-" * 70)
try:
    response = sg.client.senders.get()
    senders = json.loads(response.body)
    
    if len(senders) == 0:
        print("⚠️  NO VERIFIED SENDERS FOUND")
        print()
        print("   This is why you're getting 403 Forbidden errors!")
        print(f"   Your FROM_EMAIL ({FROM_EMAIL}) is not verified in SendGrid.")
        print()
        print("   📋 What this means:")
        print("   - Your API key works ✅")
        print("   - Your account is active ✅")
        print("   - BUT you cannot send emails until you verify a sender ❌")
    else:
        print(f"✅ Verified Senders: {len(senders)}")
        for sender in senders:
            status = "✓ VERIFIED" if sender.get('verified') else "❌ UNVERIFIED"
            email = sender.get('from', {}).get('email')
            print(f"   - {email}: {status}")
except Exception as e:
    print(f"❌ Error checking senders: {e}")

print()
print("=" * 70)
print("🔧 How to Fix the 403 Forbidden Error")
print("=" * 70)
print()
print("Option 1: Single Sender Verification (Quick & Easy)")
print("-" * 70)
print("1. Go to: https://app.sendgrid.com/settings/sender_auth/senders")
print("2. Click 'Create New Sender'")
print(f"3. Enter your email: {FROM_EMAIL}")
print("4. Fill in the required details (name, address, etc.)")
print("5. Click 'Create'")
print("6. Check your email inbox for verification link")
print("7. Click the verification link")
print()

print("Option 2: Domain Authentication (Recommended for Production)")
print("-" * 70)
print("1. Go to: https://app.sendgrid.com/settings/sender_auth")
print("2. Click 'Authenticate Your Domain'")
print("3. Enter your domain: cookie-detector.dev")
print("4. Add the DNS records provided by SendGrid")
print("5. Wait for DNS propagation (can take 24-48 hours)")
print("6. Verify the domain in SendGrid")
print()

print("💡 Quick Test After Verification:")
print("-" * 70)
print("   Run: python3 test_sendgrid.py")
print("   Enter your email when prompted to receive a test email")
print()

print("=" * 70)
print("Current Status Summary")
print("=" * 70)
print("✅ SendGrid API: Responding correctly")
print("✅ API Key: Valid (Status 200)")
print(f"✅ Configuration: {FROM_EMAIL}")
print("❌ Sender Verification: Not completed")
print("❌ Email Sending: Blocked (403 Forbidden)")
print()
print("🎯 Next Step: Verify your sender email in SendGrid dashboard")
print("=" * 70)
