"""
Test Enhanced Channel Detection System
"""

import asyncio
import logging
from enhanced_channel_detection import get_enhanced_detector, get_detection_router

logger = logging.getLogger(__name__)

async def test_enhanced_detection():
    """Test enhanced channel detection system"""
    
    print("🔍 Testing Enhanced Channel Detection System")
    print("=" * 50)
    
    try:
        # Test detector initialization
        detector = get_enhanced_detector()
        print(f"✅ Enhanced detector initialized: {detector}")
        
        # Test router initialization  
        router = get_detection_router()
        print(f"✅ Detection router initialized: {router}")
        
        # Test detection stats
        stats = detector.get_detection_stats()
        print(f"📊 Detection stats: {stats}")
        
        # Test category determination
        categories = [
            ("Tech Store", "Buy the latest technology products"),
            ("Breaking News", "Latest news updates"),
            ("Programming Hub", "Learn coding and development"),
            ("Shopping Mall", "Best deals and offers"),
            ("General Chat", "Random discussions")
        ]
        
        print("\n🏷️ Testing channel category detection:")
        for title, desc in categories:
            category = detector._determine_channel_category(title, desc)
            print(f"   {title} → {category}")
        
        print("\n✅ Enhanced channel detection system is ready!")
        print("\n🎯 How it works:")
        print("   1. my_chat_member handler detects bot status changes")
        print("   2. When bot becomes admin with posting rights:")
        print("      - Channel info is automatically extracted")
        print("      - Subscriber count is retrieved")
        print("      - Category is determined intelligently")
        print("      - Channel is added to database")
        print("      - Welcome message is sent")
        print("      - Admins are notified")
        print("   3. When bot loses admin rights:")
        print("      - Channel is marked as inactive")
        print("      - Admins are notified")
        
        print("\n🚀 Testing automatic detection:")
        print("   - Add @I3lani_bot as admin to any channel")
        print("   - Give it 'Post Messages' permission")
        print("   - Channel will be detected automatically")
        print("   - Check admin panel for new channel")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing enhanced detection: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_enhanced_detection())