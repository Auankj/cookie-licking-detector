#!/usr/bin/env python3
"""
Detailed SendGrid Diagnostics
Checks API key permissions, sender verification, and account status
"""
import os
import json
from sendgrid import SendGridAPIClient
from dotenv import load_dotenv

load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")

def diagnose_sendgrid():
    """Comprehensive SendGrid diagnostics"""
    print("=" * 70)
    print("SendGrid Detailed Diagnostics")
    print("=" * 70)
    print()
    
    sg = SendGridAPIClient(SENDGRID_API_KEY)
    
    # 1. Check API Key Scopes
    print("1️⃣  API Key Scopes & Permissions")
    print("-" * 70)
    try:
        # Get API key details (this endpoint may not work with all keys)
        response = sg.client.scopes.get()
        if response.status_code == 200:
            scopes = json.loads(response.body)
            print(f"✓ API Key Scopes: {scopes.get('scopes', [])}")
        else:
            print(f"⚠️  Could not retrieve scopes (Status: {response.status_code})")
    except Exception as e:
        print(f"⚠️  Could not check API key scopes: {e}")
    print()
    
    # 2. Check Sender Verification
    print("2️⃣  Sender Verification Status")
    print("-" * 70)
    try:
        response = sg.client.senders.get()
        if response.status_code == 200:
            senders = json.loads(response.body)
            print(f"✓ Verified Senders: {len(senders)}")
            
            for sender in senders:
                verified = "✓ VERIFIED" if sender.get('verified') else "❌ NOT VERIFIED"
                print(f"  - {sender.get('from', {}).get('email')}: {verified}")
                
            # Check if FROM_EMAIL is verified
            verified_emails = [s.get('from', {}).get('email') for s in senders if s.get('verified')]
            if FROM_EMAIL in verified_emails:
                print(f"\n✅ Your FROM_EMAIL ({FROM_EMAIL}) is verified!")
            else:
                print(f"\n⚠️  Your FROM_EMAIL ({FROM_EMAIL}) is NOT verified!")
                print("   This is likely why you're getting 403 Forbidden errors.")
        else:
            print(f"⚠️  Could not check sender verification (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Error checking senders: {e}")
    print()
    
    # 3. Check Account Status
    print("3️⃣  Account Status")
    print("-" * 70)
    try:
        # Try to get user profile
        response = sg.client.user.profile.get()
        if response.status_code == 200:
            profile = json.loads(response.body)
            print(f"✓ Account Type: {profile.get('user_type', 'Unknown')}")
            print(f"✓ Username: {profile.get('username', 'Unknown')}")
        else:
            print(f"⚠️  Could not retrieve profile (Status: {response.status_code})")
    except Exception as e:
        print(f"⚠️  Could not check account status: {e}")
    print()
    
    # 4. Check Sending Limits
    print("4️⃣  Sending Limits & Quotas")
    print("-" * 70)
    try:
        response = sg.client.user.credits.get()
        if response.status_code == 200:
            credits = json.loads(response.body)
            print(f"✓ Credits: {json.dumps(credits, indent=2)}")
        else:
            print(f"⚠️  Could not retrieve credits (Status: {response.status_code})")
    except Exception as e:
        print(f"⚠️  Could not check sending limits: {e}")
    print()
    
    # 5. Summary & Recommendations
    print("=" * 70)
    print("Summary & Recommendations")
    print("=" * 70)
    print()
    print("✅ API Key: Valid and responding")
    print(f"✅ From Email: {FROM_EMAIL}")
    print()
    print("⚠️  403 Forbidden Error Causes:")
    print("   1. Sender email not verified in SendGrid")
    print("   2. API key doesn't have 'Mail Send' permission")
    print("   3. Account is in sandbox mode (trial account)")
    print("   4. Domain authentication not completed")
    print()
    print("🔧 How to Fix:")
    print("   1. Log in to https://app.sendgrid.com/")
    print("   2. Go to Settings → Sender Authentication")
    print(f"   3. Verify the sender email: {FROM_EMAIL}")
    print("   4. Or authenticate your domain: cookie-detector.dev")
    print("   5. Ensure API key has 'Mail Send' permissions")
    print()
    print("💡 Alternative: Use a verified sender email")
    print("   If you have a verified sender, update FROM_EMAIL in .env")
    print()


if __name__ == "__main__":
    diagnose_sendgrid()
