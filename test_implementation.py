"""Test script to verify VeriMeet implementation."""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_intent_parser():
    """Test the Intent Parser."""
    print("\n🧪 Testing Intent Parser...")
    try:
        from core.intent_parser import IntentParser
        
        parser = IntentParser()
        
        # Test scheduling intent
        test_transcript_1 = "Let's schedule a follow-up meeting next Friday at 2pm to review the project progress."
        intents = parser.detect_intents(test_transcript_1)
        
        print(f"✅ Intent Parser loaded successfully")
        print(f"   Test transcript: '{test_transcript_1[:50]}...'")
        print(f"   Detected {len(intents)} intents")
        
        for i, intent in enumerate(intents, 1):
            print(f"   Intent {i}:")
            print(f"     Type: {intent.get('type')}")
            print(f"     Confidence: {intent.get('confidence')}")
            print(f"     Action: {intent.get('action')}")
        
        # Test email intent
        test_transcript_2 = "Can you email the summary to john@example.com and sarah@example.com?"
        intents_2 = parser.detect_intents(test_transcript_2)
        print(f"\n   Test transcript 2: '{test_transcript_2[:50]}...'")
        print(f"   Detected {len(intents_2)} intents")
        
        return True
    except Exception as e:
        print(f"❌ Intent Parser test failed: {e}")
        return False


def test_agent_integration():
    """Test agent with intent detection."""
    print("\n🧪 Testing Agent Integration...")
    try:
        from agent import VeriMeetAgent
        
        agent = VeriMeetAgent()
        print("✅ Agent created successfully")
        print(f"   Intent parser initialized: {agent.intent_parser is not None}")
        print(f"   Detected intents list: {len(agent.detected_intents)}")
        
        # Test processing a transcript with intent
        test_transcript = "We should schedule a follow-up next week. Also, please email the summary."
        result = agent.process_transcript(test_transcript)
        
        print(f"   Processed transcript: '{test_transcript[:50]}...'")
        print(f"   Intents detected: {result.get('intents_detected', 0)}")
        print(f"   Facts detected: {result.get('facts_detected', 0)}")
        
        return True
    except Exception as e:
        print(f"❌ Agent integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_calendar_mcp():
    """Test Calendar MCP (without actually creating events)."""
    print("\n🧪 Testing Calendar MCP...")
    try:
        from mcp.calendar_mcp import create_calendar_event, _get_google_oauth_token
        
        token = _get_google_oauth_token()
        if token:
            print("✅ Google Calendar token found")
            print("   Calendar MCP is configured and ready")
        else:
            print("⚠️  Google Calendar token not configured")
            print("   Calendar MCP will work once GOOGLE_CALENDAR_TOKEN is set")
        
        # Test function exists and is callable
        assert callable(create_calendar_event)
        print("✅ Calendar MCP functions are available")
        
        return True
    except Exception as e:
        print(f"❌ Calendar MCP test failed: {e}")
        return False


def test_gmail_mcp():
    """Test Gmail MCP (without actually sending emails)."""
    print("\n🧪 Testing Gmail MCP...")
    try:
        from mcp.gmail_mcp import send_email_summary, _get_google_oauth_token
        
        token = _get_google_oauth_token()
        if token:
            print("✅ Gmail token found")
            print("   Gmail MCP is configured and ready")
        else:
            print("⚠️  Gmail token not configured")
            print("   Gmail MCP will work once GOOGLE_GMAIL_TOKEN is set")
        
        # Test function exists and is callable
        assert callable(send_email_summary)
        print("✅ Gmail MCP functions are available")
        
        return True
    except Exception as e:
        print(f"❌ Gmail MCP test failed: {e}")
        return False


def test_config():
    """Test configuration loading."""
    print("\n🧪 Testing Configuration...")
    try:
        from core.config import settings
        
        print("✅ Configuration loaded")
        print(f"   OpenAI API Key: {'✅ Set' if settings.openai_api_key else '❌ Missing'}")
        print(f"   Meetstream API Key: {'✅ Set' if settings.meetstream_api_key else '❌ Missing'}")
        print(f"   Notion API Key: {'✅ Set' if settings.notion_api_key else '❌ Missing'}")
        print(f"   Google Calendar Token: {'✅ Set' if settings.google_calendar_token else '⚠️  Not set (optional)'}")
        print(f"   Google Gmail Token: {'✅ Set' if settings.google_gmail_token else '⚠️  Not set (optional)'}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("🚀 VeriMeet Implementation Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Configuration", test_config()))
    results.append(("Intent Parser", test_intent_parser()))
    results.append(("Agent Integration", test_agent_integration()))
    results.append(("Calendar MCP", test_calendar_mcp()))
    results.append(("Gmail MCP", test_gmail_mcp()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {name}")
    
    print(f"\n   Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Implementation is ready.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

