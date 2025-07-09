#!/usr/bin/env python3
"""
Test Simple Interface - Verify neural network terminology is removed
"""

import asyncio
import sys
import os
from database import Database
from languages import get_text
from handlers import create_regular_main_menu_text, create_regular_main_menu_keyboard

async def test_simple_interface():
    """Test that interface shows simple, user-friendly text"""
    print("🧪 Testing Simple Interface (No Neural Network Terms)")
    print("=" * 60)
    
    # Test data
    test_user_id = 123456789
    test_languages = ['en', 'ar', 'ru']
    
    # Initialize database
    db = Database()
    await db.init_db()
    
    results = []
    
    for language in test_languages:
        print(f"\n🌐 Testing {language.upper()} language:")
        
        # Test main menu text
        try:
            menu_text = await create_regular_main_menu_text(language, test_user_id)
            
            # Check for neural network terms that should NOT be present
            forbidden_terms = [
                'Neural', 'neural', 'NEURAL',
                'Quantum', 'quantum', 'QUANTUM', 
                'Dynamic Interface', 'dynamic interface',
                'Protocol', 'protocol', 'PROTOCOL',
                'Matrix', 'matrix', 'MATRIX',
                'I3lani Dynamic Interface',
                '◇━━', '━━◇', '◈', '▣'
            ]
            
            found_forbidden = []
            for term in forbidden_terms:
                if term in menu_text:
                    found_forbidden.append(term)
            
            if found_forbidden:
                print(f"   ❌ Found forbidden terms: {found_forbidden}")
                results.append({
                    'language': language,
                    'status': 'FAIL',
                    'issue': f'Contains neural terms: {found_forbidden}'
                })
            else:
                print(f"   ✅ Clean, simple text - no neural network terms")
                results.append({
                    'language': language,
                    'status': 'PASS',
                    'details': 'Simple, user-friendly interface'
                })
                
            # Show preview of text
            preview = menu_text[:100].replace('\n', ' ')
            print(f"   📝 Preview: {preview}...")
            
        except Exception as e:
            print(f"   ❌ Error testing {language}: {e}")
            results.append({
                'language': language,
                'status': 'ERROR',
                'error': str(e)
            })
    
    # Generate report
    print(f"\n📊 SIMPLE INTERFACE TEST REPORT")
    print("=" * 60)
    
    passed = len([r for r in results if r['status'] == 'PASS'])
    failed = len([r for r in results if r['status'] == 'FAIL'])
    errors = len([r for r in results if r['status'] == 'ERROR'])
    
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️  Errors: {errors}")
    
    if failed > 0:
        print(f"\n❌ FAILED TESTS:")
        for result in results:
            if result['status'] == 'FAIL':
                print(f"   • {result['language']}: {result['issue']}")
    
    if passed == len(test_languages):
        print(f"\n🎉 SUCCESS: All languages show simple, user-friendly interface!")
        print(f"✅ Neural network terminology removed")
        print(f"✅ Interface is clean and professional")
        print(f"✅ Users will see simple, clear language")
    else:
        print(f"\n⚠️  Some languages still contain neural network terminology")
        
    await db.close()

if __name__ == "__main__":
    asyncio.run(test_simple_interface())