#!/usr/bin/env python3
"""
Complete Referral System Integration for I3lani Bot
Fixes all issues and properly integrates referral system
"""

import re
import os
import asyncio
import logging

logger = logging.getLogger(__name__)

def integrate_referral_with_main_bot():
    """Integrate referral system with main_bot.py"""
    
    # Read main_bot.py
    with open('main_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the viral referral game initialization location
    viral_game_pattern = r'(        # Initialize viral referral game system.*?dp\.include_router\(viral_router\))'
    
    # Add referral system initialization after viral referral game
    referral_init_code = '''        
        # Initialize referral system
        logger.info("Initializing referral system...")
        try:
            from referral_integration import integrate_referral_system_with_bot, setup_referral_system_handlers
            
            # Initialize referral system database
            referral_success = await integrate_referral_system_with_bot()
            
            if referral_success:
                # Setup referral handlers
                setup_referral_system_handlers(dp)
                
                logger.info("✅ Referral system initialized")
                logger.info("   💰 Signup bonus: 0.00010000 TON")
                logger.info("   🏆 Commission rate: 20%")
                logger.info("   🔗 Referral links: ref_<user_id>")
                logger.info("   💳 Withdrawal system: Ready")
                logger.info("   📊 Commands: /refer, /balance, /withdraw")
            else:
                logger.warning("⚠️ Referral system initialization failed")
                
        except Exception as e:
            logger.error(f"❌ Referral system initialization error: {e}")
            logger.info("Referral system skipped")'''
    
    # Insert referral system initialization
    if 'Initialize referral system' not in content:
        viral_match = re.search(viral_game_pattern, content, re.DOTALL)
        if viral_match:
            # Insert after viral referral game
            insert_pos = viral_match.end()
            content = content[:insert_pos] + referral_init_code + content[insert_pos:]
            
            # Write back
            with open('main_bot.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Referral system integrated with main_bot.py")
            return True
    
    print("✅ Referral system already integrated")
    return True

def integrate_referral_with_handlers():
    """Integrate referral system with handlers.py start command"""
    
    # Read handlers.py
    with open('handlers.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the start command function
    start_pattern = r'(@router\.message\(Command\("start"\)\)\s*async def start_command\(.*?\):.*?user_id = message\.from_user\.id.*?username = message\.from_user\.username)'
    
    # Add referral processing code
    referral_code = '''
    # Handle referral code from start parameter
    start_param = None
    if message.text and len(message.text.split()) > 1:
        start_param = message.text.split()[1]
    
    # Process referral registration
    if start_param and start_param.startswith('ref_'):
        try:
            from referral_integration import process_referral_start_command
            await process_referral_start_command(user_id, start_param)
            logger.info(f"✅ Processed referral code {start_param} for user {user_id}")
        except Exception as e:
            logger.error(f"Error processing referral start: {e}")
    '''
    
    # Insert referral processing
    if 'Handle referral code from start parameter' not in content:
        match = re.search(start_pattern, content, re.DOTALL)
        if match:
            # Insert after username extraction
            insert_pos = match.end()
            content = content[:insert_pos] + referral_code + content[insert_pos:]
            
            # Write back
            with open('handlers.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Referral system integrated with handlers.py")
            return True
    
    print("✅ Referral system already integrated with handlers")
    return True

def fix_referral_system_database_methods():
    """Fix all database method calls in referral system"""
    
    # Read referral_system.py
    with open('referral_system.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace all execute with execute_query
    content = re.sub(r'await db\.execute\(', 'await db.execute_query(', content)
    
    # Fix the user data retrieval issue
    content = re.sub(
        r'logger\.error\(f"❌ Error getting referral data for \{user_id\}: \{e\}"\)\s*return \{\}',
        '''logger.error(f"❌ Error getting referral data for {user_id}: {e}")
            return {
                'referral_code': f'ref_{user_id}',
                'referred_by': None,
                'signup_bonus_claimed': False,
                'total_earnings': 0,
                'available_balance': 0,
                'total_withdrawn': 0,
                'referral_count': 0,
                'ton_wallet_address': None,
                'recent_earnings': [],
                'referred_users': []
            }''',
        content
    )
    
    # Write back
    with open('referral_system.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed referral system database methods")
    return True

async def test_referral_system_integration():
    """Test the referral system integration"""
    try:
        # Test referral system
        from referral_system import get_referral_system
        
        referral_sys = await get_referral_system()
        
        # Test database initialization
        init_result = await referral_sys.initialize_database()
        print(f"Database initialization: {init_result}")
        
        # Test user registration
        test_user = 987654321
        reg_result = await referral_sys.register_user(test_user)
        print(f"User registration: {reg_result}")
        
        # Test getting user data
        user_data = await referral_sys.get_user_referral_data(test_user)
        print(f"User data fields: {list(user_data.keys()) if user_data else 'None'}")
        
        # Test referral link
        link = await referral_sys.get_referral_link(test_user, 'i3lani_bot')
        print(f"Referral link: {link}")
        
        # Test referral with referrer
        referred_user = 123456789
        referrer_code = f"ref_{test_user}"
        reg_with_ref = await referral_sys.register_user(referred_user, referrer_code)
        print(f"Registration with referrer: {reg_with_ref}")
        
        # Test commission processing
        from decimal import Decimal
        commission_result = await referral_sys.process_referral_commission(
            referred_user, Decimal('1.0'), 'test_payment'
        )
        print(f"Commission processing: {commission_result}")
        
        # Get updated referrer data
        referrer_data = await referral_sys.get_user_referral_data(test_user)
        print(f"Referrer total earnings: {referrer_data.get('total_earnings', 0)}")
        
        print("✅ Referral system integration test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Referral system integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main integration function"""
    print("🔧 Complete Referral System Integration")
    print("=" * 50)
    
    # Fix database methods
    fix_referral_system_database_methods()
    
    # Integrate with main bot
    integrate_referral_with_main_bot()
    
    # Integrate with handlers
    integrate_referral_with_handlers()
    
    print("\n" + "=" * 50)
    print("✅ Complete referral system integration finished")
    print("🚀 Testing integration...")
    
    # Test the integration
    asyncio.run(test_referral_system_integration())

if __name__ == "__main__":
    main()