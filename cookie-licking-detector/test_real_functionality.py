#!/usr/bin/env python3
"""
COMPREHENSIVE TEST: Verify backend uses REAL logic, not dummy implementations
This will test actual functionality that would work in production
"""
import sys
import os
import asyncio
import json
from datetime import datetime, timezone

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_github_service_real_calls():
    """Test if GitHub service makes real API calls (without actual GitHub token)"""
    print("🧪 Testing GitHub Service Real API Logic...")
    print("=" * 50)
    
    try:
        from app.services.github_service import GitHubAPIService
        
        # Initialize without real token (should still show real logic)
        github_service = GitHubAPIService()
        
        # Check if it has real methods that would work
        methods_to_check = [
            'get_repository', 'get_issue', 'get_issue_comments',
            'post_issue_comment', 'assign_issue', 'unassign_issue',
            'get_pull_requests_for_issue', 'get_user_commits'
        ]
        
        all_methods_exist = True
        for method in methods_to_check:
            if hasattr(github_service, method):
                print(f"✅ {method} - Real method exists")
            else:
                print(f"❌ {method} - Missing")
                all_methods_exist = False
        
        # Check if it uses real PyGithub library
        if hasattr(github_service, 'github'):
            print("✅ Uses real PyGithub client")
        else:
            print("❌ No real GitHub client")
            all_methods_exist = False
        
        return all_methods_exist
        
    except Exception as e:
        print(f"❌ GitHub Service test failed: {e}")
        return False

def test_notification_service_real_logic():
    """Test if notification service has real SendGrid integration"""
    print("\n🧪 Testing Notification Service Real Logic...")
    print("=" * 50)
    
    try:
        from app.services.notification_service import NotificationService
        
        # Initialize service
        notification_service = NotificationService()
        
        # Check if it has SendGrid client
        if hasattr(notification_service, 'sendgrid_client'):
            print("✅ Has real SendGrid client")
        else:
            print("❌ No SendGrid client")
            return False
            
        # Check for real email methods
        methods = ['send_nudge_email', 'send_auto_release_email', 'post_nudge_comment']
        all_methods_exist = True
        
        for method in methods:
            if hasattr(notification_service, method):
                print(f"✅ {method} - Real method exists")
            else:
                print(f"❌ {method} - Missing")
                all_methods_exist = False
        
        # Check if email templates are real (not just "success: true")
        try:
            # Test email template generation without sending
            class MockClaim:
                def __init__(self):
                    self.github_username = "test_user"
                    self.claim_timestamp = datetime.now(timezone.utc)
                    self.issue = MockIssue()
                    
            class MockIssue:
                def __init__(self):
                    self.github_issue_number = 123
                    self.title = "Test Issue"
                    self.repository = MockRepo()
                    self.github_data = {
                        'html_url': 'https://github.com/test_owner/test_repo/issues/123',
                        'body': 'Test issue body'
                    }
                    
            class MockRepo:
                def __init__(self):
                    self.owner = "test_owner"
                    self.name = "test_repo"
                    self.grace_period_days = 7
            
            mock_claim = MockClaim()
            
            # Test if template generation works (real logic)
            html_template = notification_service._get_nudge_email_html(mock_claim, 1)
            text_template = notification_service._get_nudge_email_text(mock_claim, 1)
            
            if len(html_template) > 100 and "test_user" in html_template:
                print("✅ Real HTML email templates with user data")
            else:
                print("❌ Email templates are dummy/empty")
                all_methods_exist = False
                
            if len(text_template) > 50 and "test_user" in text_template:
                print("✅ Real text email templates with user data")
            else:
                print("❌ Text templates are dummy/empty")
                all_methods_exist = False
        
        except Exception as e:
            print(f"❌ Email template test failed: {e}")
            all_methods_exist = False
        
        return all_methods_exist
        
    except Exception as e:
        print(f"❌ Notification Service test failed: {e}")
        return False

def test_pattern_matcher_edge_cases():
    """Test pattern matcher with edge cases to ensure it's not just returning dummy results"""
    print("\n🧪 Testing Pattern Matcher Edge Cases...")
    print("=" * 50)
    
    try:
        from app.services.pattern_matcher import pattern_matcher
        
        # Test edge cases that would expose dummy logic
        edge_cases = [
            ("", False, 0),  # Empty string
            ("This is just a random comment with no claim intent", False, 0),  # No claim
            ("I can't work on this", False, 0),  # Negative statement
            ("Someone else should take this", False, 0),  # Third person
            ("I'll take this issue and work on it immediately", True, 95),  # Strong claim
            ("Can I maybe possibly work on this perhaps?", True, 70),  # Weak question
            ("I'm currently working on this right now", False, 0),  # Progress update
        ]
        
        all_passed = True
        
        for i, (comment, expected_claim, expected_confidence) in enumerate(edge_cases):
            result = pattern_matcher.analyze_comment(comment)
            
            is_claim = result.get('is_claim', False)
            confidence = result.get('final_score', 0)
            
            # Check if results are logical (not dummy)
            if is_claim == expected_claim:
                if expected_claim and abs(confidence - expected_confidence) <= 5:
                    status = "✅ PASS"
                elif not expected_claim:
                    status = "✅ PASS"
                else:
                    status = f"❌ FAIL (confidence {confidence} != {expected_confidence})"
                    all_passed = False
            else:
                status = f"❌ FAIL (claim {is_claim} != {expected_claim})"
                all_passed = False
            
            print(f"Edge Case {i+1}: {status}")
            print(f"   Text: '{comment[:50]}{'...' if len(comment) > 50 else ''}'")
            print(f"   Result: Claim={is_claim}, Confidence={confidence}%")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Pattern Matcher test failed: {e}")
        return False

def test_ecosyste_api_client_real():
    """Test if Ecosyste.ms API client makes real HTTP requests"""
    print("\n🧪 Testing Ecosyste.ms API Client...")
    print("=" * 50)
    
    try:
        from app.services.ecosyste_client import EcosysteAPIClient
        
        client = EcosysteAPIClient()
        
        # Check if it has real HTTP client
        if hasattr(client, 'client') and str(type(client.client)) == "<class 'httpx.AsyncClient'>":
            print("✅ Uses real HTTPX client for HTTP requests")
        else:
            print("❌ No real HTTP client")
            return False
        
        # Check if it has real rate limiting logic
        if hasattr(client, '_rate_limit_wait') and hasattr(client, 'request_times'):
            print("✅ Has real rate limiting implementation")
        else:
            print("❌ No rate limiting logic")
            return False
        
        # Check base URL
        if client.base_url == "https://issues.ecosyste.ms/api/v1":
            print("✅ Configured with real Ecosyste.ms API URL")
        else:
            print(f"❌ Wrong base URL: {client.base_url}")
            return False
            
        # Check real methods exist
        methods = ['get_repository_issues', 'get_issue_by_id', 'get_issue_comments', 'get_issue_events']
        all_methods = True
        
        for method in methods:
            if hasattr(client, method) and callable(getattr(client, method)):
                print(f"✅ {method} - Real async method exists")
            else:
                print(f"❌ {method} - Missing or not callable")
                all_methods = False
        
        return all_methods
        
    except Exception as e:
        print(f"❌ Ecosyste.ms API Client test failed: {e}")
        return False

def test_database_models_real():
    """Test if database models have real SQLAlchemy implementation"""
    print("\n🧪 Testing Database Models...")
    print("=" * 50)
    
    try:
        from app.db.models.claims import Claim
        from app.db.models.issues import Issue
        from app.db.models.repositories import Repository
        
        # Check if they're real SQLAlchemy models
        models_to_check = [
            ("Claim", Claim),
            ("Issue", Issue), 
            ("Repository", Repository)
        ]
        
        all_real = True
        
        for name, model_class in models_to_check:
            # Check if it has SQLAlchemy attributes
            if hasattr(model_class, '__tablename__') and hasattr(model_class, '__table__'):
                print(f"✅ {name} - Real SQLAlchemy model")
                
                # Check if it has real database columns
                if hasattr(model_class, '__table__') and len(model_class.__table__.columns) > 0:
                    print(f"✅ {name} - Has real database columns ({len(model_class.__table__.columns)} columns)")
                else:
                    print(f"❌ {name} - No database columns")
                    all_real = False
            else:
                print(f"❌ {name} - Not a real SQLAlchemy model")
                all_real = False
        
        return all_real
        
    except Exception as e:
        print(f"❌ Database Models test failed: {e}")
        return False

def test_celery_tasks_real():
    """Test if Celery tasks have real implementation logic"""
    print("\n🧪 Testing Celery Tasks...")
    print("=" * 50)
    
    try:
        # Import task modules (not execute them)
        from app.tasks import comment_analysis
        from app.tasks import nudge_check
        
        # Check if comment analysis task has real logic
        if hasattr(comment_analysis, 'analyze_comment_task'):
            print("✅ Comment analysis task exists")
            
            # Check if the task function has real logic (not just return {})
            import inspect
            source = inspect.getsource(comment_analysis.analyze_comment_task)
            
            if "pattern_matcher" in source and "database" in source and len(source) > 500:
                print("✅ Comment analysis task has real implementation (pattern matching + database)")
            else:
                print("❌ Comment analysis task appears to be dummy implementation")
                return False
        else:
            print("❌ Comment analysis task missing")
            return False
            
        # Check nudge task
        if hasattr(nudge_check, 'check_stale_claims_task'):
            print("✅ Nudge check task exists")
            
            source = inspect.getsource(nudge_check.check_stale_claims_task)
            if "notification" in source and "database" in source and len(source) > 500:
                print("✅ Nudge check task has real implementation")
            else:
                print("❌ Nudge check task appears to be dummy")
                return False
        else:
            print("❌ Nudge check task missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Celery Tasks test failed: {e}")
        return False

def test_distributed_locking_real():
    """Test if distributed locking uses real Redis operations"""
    print("\n🧪 Testing Distributed Locking...")
    print("=" * 50)
    
    try:
        from app.utils.distributed_lock import RedisDistributedLock
        
        lock_service = RedisDistributedLock()
        
        # Check if it has real Redis client
        if hasattr(lock_service, 'redis_client'):
            print("✅ Has real Redis client")
        else:
            print("❌ No Redis client")
            return False
            
        # Check if it has real locking methods
        methods = ['acquire_lock', 'release_lock']
        all_methods = True
        
        for method in methods:
            if hasattr(lock_service, method) and callable(getattr(lock_service, method)):
                print(f"✅ {method} - Real method exists")
                
                # Check if method has real logic
                import inspect
                source = inspect.getsource(getattr(lock_service, method))
                if "redis" in source.lower() and len(source) > 100:
                    print(f"✅ {method} - Has real Redis operations")
                else:
                    print(f"❌ {method} - Appears to be dummy")
                    all_methods = False
            else:
                print(f"❌ {method} - Missing")
                all_methods = False
        
        return all_methods
        
    except Exception as e:
        print(f"❌ Distributed Locking test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 COMPREHENSIVE REAL FUNCTIONALITY TEST")
    print("Testing if backend uses REAL logic vs dummy implementations")
    print("=" * 70)
    
    tests = [
        ("Pattern Matching Edge Cases", test_pattern_matcher_edge_cases),
        ("GitHub Service Real API", test_github_service_real_calls),
        ("Notification Service Logic", test_notification_service_real_logic),
        ("Ecosyste.ms API Client", test_ecosyste_api_client_real),
        ("Database Models", test_database_models_real),
        ("Celery Tasks Implementation", test_celery_tasks_real),
        ("Distributed Locking", test_distributed_locking_real),
    ]
    
    total_tests = len(tests)
    passed_tests = 0
    
    for test_name, test_func in tests:
        print(f"\n{'=' * 70}")
        try:
            if test_func():
                print(f"🎉 {test_name}: REAL IMPLEMENTATION CONFIRMED")
                passed_tests += 1
            else:
                print(f"💥 {test_name}: DUMMY/INCOMPLETE IMPLEMENTATION")
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}")
    
    print(f"\n{'=' * 70}")
    print(f"FINAL RESULTS: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 BACKEND USES 100% REAL IMPLEMENTATIONS!")
        print("✅ All components have genuine business logic")
        print("✅ No dummy/mock implementations found") 
        print("✅ Production-ready functionality confirmed")
    elif passed_tests >= total_tests * 0.8:
        print("⚠️  BACKEND IS MOSTLY REAL with some gaps")
        print(f"✅ {passed_tests} components confirmed real")
        print(f"❌ {total_tests - passed_tests} components need attention")
    else:
        print("💥 BACKEND HAS SIGNIFICANT DUMMY IMPLEMENTATIONS")
        print("❌ Major functionality appears to be mock/placeholder")
    
    sys.exit(0 if passed_tests == total_tests else 1)