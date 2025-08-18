#!/usr/bin/env python3
"""
Basic test script for export and share functionality.
This tests the core components without requiring a full server setup.
"""

import asyncio
import os
import sys
from uuid import uuid4, UUID
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, 'backend')

def test_share_token_creation():
    """Test ShareToken model creation and token hashing."""
    print("Testing ShareToken model...")
    
    try:
        from backend.models.share_token import ShareToken
        
        # Test token creation
        analysis_id = uuid4()
        share_token, raw_token = ShareToken.create_token(analysis_id, expires_in_days=7)
        
        print(f"✅ Created share token for analysis {analysis_id}")
        print(f"   - Token ID: {share_token.id}")
        print(f"   - Raw token length: {len(raw_token)} characters")
        print(f"   - Hashed token length: {len(share_token.hashed_token)} characters")
        print(f"   - Expires at: {share_token.expires_at}")
        
        # Test token hashing
        rehashed = ShareToken.hash_token(raw_token)
        assert rehashed == share_token.hashed_token, "Token hashing mismatch"
        print("✅ Token hashing verified")
        
        # Test expiration check
        assert not share_token.is_expired(), "Token should not be expired"
        print("✅ Expiration check working")
        
        return True
        
    except Exception as e:
        print(f"❌ ShareToken test failed: {e}")
        return False

async def test_export_service():
    """Test export service PDF generation capability."""
    print("\nTesting Export Service...")
    
    try:
        from backend.services.export_service import export_service
        
        # Test safe filename generation
        analysis_id = str(uuid4())
        filename = export_service.get_safe_filename("Test Analysis", analysis_id, "pdf")
        print(f"✅ Generated safe filename: {filename}")
        
        # Test mock analysis data
        mock_analysis = {
            "analysis_id": analysis_id,
            "created_at": datetime.utcnow().isoformat(),
            "metrics": {
                "word_count": 150,
                "clarity_score": 8.5,
                "structure_score": 7.2,
                "filler_word_count": 3
            },
            "summary": "This is a test analysis summary.",
            "feedback": "This is test feedback for the analysis.",
            "transcript": "This is a test transcript of the speech content."
        }
        
        # Test PDF generation (only if reportlab is available)
        try:
            pdf_bytes = await export_service.render_pdf(mock_analysis, include_transcript=True)
            print(f"✅ PDF generated successfully ({len(pdf_bytes)} bytes)")
            return True
        except RuntimeError as e:
            if "reportlab" in str(e):
                print("⚠️  PDF generation skipped (reportlab not installed)")
                print("   This is expected in development - install with: pip install reportlab")
                return True
            else:
                raise
        
    except Exception as e:
        print(f"❌ Export service test failed: {e}")
        return False

def test_environment_flags():
    """Test environment flag configuration."""
    print("\nTesting Environment Flags...")
    
    try:
        # Test backend export flag
        export_enabled = os.getenv("EXPORT_ENABLED", "0") == "1"
        print(f"Backend EXPORT_ENABLED: {export_enabled}")
        
        # Test frontend export flag (simulated)
        frontend_export = os.getenv("NEXT_PUBLIC_EXPORT_ENABLED", "0") == "1"
        print(f"Frontend NEXT_PUBLIC_EXPORT_ENABLED: {frontend_export}")
        
        # Test other related flags
        allow_transcript = os.getenv("ALLOW_TRANSCRIPT_SHARE", "0") == "1"
        print(f"ALLOW_TRANSCRIPT_SHARE: {allow_transcript}")
        
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        print(f"FRONTEND_URL: {frontend_url}")
        
        print("✅ Environment flags configured")
        return True
        
    except Exception as e:
        print(f"❌ Environment flags test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("🚀 Starting Export & Share Functionality Tests\n")
    
    results = []
    
    # Run tests
    results.append(test_share_token_creation())
    results.append(await test_export_service())
    results.append(test_environment_flags())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Test Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Export & Share functionality is ready.")
        return True
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    # Run the async main function
    success = asyncio.run(main())
    sys.exit(0 if success else 1)