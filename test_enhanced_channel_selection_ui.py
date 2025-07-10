"""
Test Enhanced Channel Selection UI
Validates the modern toggle design with 🟢/⚪️ indicators
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from live_channel_stats import LiveChannelStats
from database import Database
from languages import get_text

class TestEnhancedChannelUI:
    """Test suite for enhanced channel selection UI"""
    
    def __init__(self):
        self.db = Database()
        self.test_results = []
        
    async def test_toggle_indicator_design(self):
        """Test 1: Toggle indicator design (🟢/⚪️)"""
        print("\n🎯 Testing Toggle Indicator Design...")
        
        # Mock LiveChannelStats for testing
        live_stats = LiveChannelStats(None, self.db)
        
        # Test channel data
        test_channel = {
            'name': 'Test Channel',
            'live_subscribers': 1500,
            'subscribers': 1500,
            'channel_id': 'test_channel_1'
        }
        
        # Test selected state (should show 🟢)
        selected_text = live_stats.create_channel_button_text(test_channel, True, 'en')
        unselected_text = live_stats.create_channel_button_text(test_channel, False, 'en')
        
        selected_correct = selected_text.startswith('🟢')
        unselected_correct = unselected_text.startswith('⚪️')
        
        results = []
        if selected_correct and unselected_correct:
            results.append({'test': 'Toggle Indicators', 'status': 'PASS', 'details': 'Correct 🟢/⚪️ design'})
            print("✅ Toggle indicators working correctly")
        else:
            results.append({'test': 'Toggle Indicators', 'status': 'FAIL', 'details': f'Selected: {selected_text[:5]}, Unselected: {unselected_text[:5]}'})
            print(f"❌ Toggle indicators incorrect - Selected: {selected_text[:5]}, Unselected: {unselected_text[:5]}")
        
        return results
    
    async def test_subscriber_count_display(self):
        """Test 2: Subscriber count below channel name"""
        print("\n📊 Testing Subscriber Count Display...")
        
        live_stats = LiveChannelStats(None, self.db)
        
        test_cases = [
            {'subscribers': 1500, 'expected_format': '1.5K'},
            {'subscribers': 1000000, 'expected_format': '1.0M'},
            {'subscribers': 500, 'expected_format': '500'},
            {'subscribers': 0, 'expected_format': 'No data'}
        ]
        
        results = []
        for case in test_cases:
            test_channel = {
                'name': 'Test Channel',
                'live_subscribers': case['subscribers'],
                'subscribers': case['subscribers'],
                'channel_id': 'test_channel'
            }
            
            button_text = live_stats.create_channel_button_text(test_channel, False, 'en')
            lines = button_text.split('\n')
            
            # Check if subscriber count is on second line
            if len(lines) >= 2:
                second_line = lines[1].strip()
                if case['expected_format'] in second_line:
                    results.append({'test': f'Subscriber Count ({case["subscribers"]})', 'status': 'PASS', 'details': f'Correct format: {second_line}'})
                    print(f"✅ {case['subscribers']} subscribers displayed correctly")
                else:
                    results.append({'test': f'Subscriber Count ({case["subscribers"]})', 'status': 'FAIL', 'details': f'Format: {second_line}'})
                    print(f"❌ {case['subscribers']} subscribers format incorrect: {second_line}")
            else:
                results.append({'test': f'Subscriber Count ({case["subscribers"]})', 'status': 'FAIL', 'details': 'No second line found'})
                print(f"❌ {case['subscribers']} subscribers - no second line")
        
        return results
    
    async def test_multilingual_support(self):
        """Test 3: RTL/LTR support for different languages"""
        print("\n🌍 Testing Multilingual Support...")
        
        live_stats = LiveChannelStats(None, self.db)
        
        test_channel = {
            'name': 'Test Channel Name',
            'live_subscribers': 1500,
            'subscribers': 1500,
            'channel_id': 'test_channel'
        }
        
        languages = ['en', 'ar', 'ru']
        results = []
        
        for lang in languages:
            button_text = live_stats.create_channel_button_text(test_channel, True, lang)
            
            # Check if text contains appropriate language elements
            if lang == 'ar':
                # Arabic should have Arabic subscriber label
                if 'مشترك' in button_text:
                    results.append({'test': f'Arabic Support', 'status': 'PASS', 'details': 'Arabic subscriber label found'})
                    print(f"✅ Arabic support working - contains 'مشترك'")
                else:
                    results.append({'test': f'Arabic Support', 'status': 'FAIL', 'details': 'No Arabic subscriber label'})
                    print(f"❌ Arabic support missing - no 'مشترك' found")
            elif lang == 'ru':
                # Russian should have Russian subscriber label
                if 'подписчиков' in button_text:
                    results.append({'test': f'Russian Support', 'status': 'PASS', 'details': 'Russian subscriber label found'})
                    print(f"✅ Russian support working - contains 'подписчиков'")
                else:
                    results.append({'test': f'Russian Support', 'status': 'FAIL', 'details': 'No Russian subscriber label'})
                    print(f"❌ Russian support missing - no 'подписчиков' found")
            else:
                # English should have English subscriber label
                if 'subscribers' in button_text:
                    results.append({'test': f'English Support', 'status': 'PASS', 'details': 'English subscriber label found'})
                    print(f"✅ English support working - contains 'subscribers'")
                else:
                    results.append({'test': f'English Support', 'status': 'FAIL', 'details': 'No English subscriber label'})
                    print(f"❌ English support missing - no 'subscribers' found")
        
        return results
    
    async def test_long_channel_names(self):
        """Test 4: Long channel name handling"""
        print("\n📏 Testing Long Channel Name Handling...")
        
        live_stats = LiveChannelStats(None, self.db)
        
        long_channel = {
            'name': 'This is a very long channel name that should be truncated properly',
            'live_subscribers': 1000,
            'subscribers': 1000,
            'channel_id': 'long_channel'
        }
        
        results = []
        for lang in ['en', 'ar', 'ru']:
            button_text = live_stats.create_channel_button_text(long_channel, False, lang)
            lines = button_text.split('\n')
            
            if len(lines) >= 1:
                first_line = lines[0]
                # Check if name is truncated (contains ellipsis)
                if '…' in first_line and len(first_line) <= 50:  # Reasonable button text length
                    results.append({'test': f'Long Name ({lang})', 'status': 'PASS', 'details': f'Truncated: {first_line}'})
                    print(f"✅ Long name truncation working for {lang}")
                else:
                    results.append({'test': f'Long Name ({lang})', 'status': 'FAIL', 'details': f'Not truncated: {first_line}'})
                    print(f"❌ Long name not truncated for {lang}: {first_line}")
            else:
                results.append({'test': f'Long Name ({lang})', 'status': 'FAIL', 'details': 'No button text generated'})
                print(f"❌ No button text for {lang}")
        
        return results
    
    async def test_mobile_friendly_spacing(self):
        """Test 5: Mobile-friendly spacing and layout"""
        print("\n📱 Testing Mobile-Friendly Layout...")
        
        live_stats = LiveChannelStats(None, self.db)
        
        test_channel = {
            'name': 'Mobile Test Channel',
            'live_subscribers': 2500,
            'subscribers': 2500,
            'channel_id': 'mobile_test'
        }
        
        button_text = live_stats.create_channel_button_text(test_channel, True, 'en')
        lines = button_text.split('\n')
        
        results = []
        
        # Test 1: Two-line layout
        if len(lines) == 2:
            results.append({'test': 'Two-Line Layout', 'status': 'PASS', 'details': 'Correct two-line structure'})
            print("✅ Two-line layout working")
        else:
            results.append({'test': 'Two-Line Layout', 'status': 'FAIL', 'details': f'Found {len(lines)} lines'})
            print(f"❌ Layout has {len(lines)} lines instead of 2")
        
        # Test 2: Proper spacing
        if len(lines) >= 2:
            second_line = lines[1]
            if second_line.startswith('    '):  # Should have indentation
                results.append({'test': 'Proper Spacing', 'status': 'PASS', 'details': 'Subscriber count properly indented'})
                print("✅ Proper spacing working")
            else:
                results.append({'test': 'Proper Spacing', 'status': 'FAIL', 'details': f'Second line: "{second_line}"'})
                print(f"❌ Spacing incorrect: '{second_line}'")
        
        # Test 3: Mobile-friendly length
        total_length = len(button_text)
        if total_length <= 100:  # Reasonable mobile button text length
            results.append({'test': 'Mobile-Friendly Length', 'status': 'PASS', 'details': f'Length: {total_length} chars'})
            print(f"✅ Mobile-friendly length: {total_length} chars")
        else:
            results.append({'test': 'Mobile-Friendly Length', 'status': 'FAIL', 'details': f'Too long: {total_length} chars'})
            print(f"❌ Text too long for mobile: {total_length} chars")
        
        return results
    
    async def test_toggle_behavior_flow(self):
        """Test 6: Toggle behavior flow simulation"""
        print("\n🔄 Testing Toggle Behavior Flow...")
        
        live_stats = LiveChannelStats(None, self.db)
        
        test_channel = {
            'name': 'Toggle Test Channel',
            'live_subscribers': 800,
            'subscribers': 800,
            'channel_id': 'toggle_test'
        }
        
        # Simulate toggle sequence: unselected → selected → unselected
        states = [False, True, False]
        expected_indicators = ['⚪️', '🟢', '⚪️']
        
        results = []
        for i, (state, expected) in enumerate(zip(states, expected_indicators)):
            button_text = live_stats.create_channel_button_text(test_channel, state, 'en')
            
            if button_text.startswith(expected):
                results.append({'test': f'Toggle Step {i+1}', 'status': 'PASS', 'details': f'Correct indicator: {expected}'})
                print(f"✅ Toggle step {i+1} working: {expected}")
            else:
                results.append({'test': f'Toggle Step {i+1}', 'status': 'FAIL', 'details': f'Expected {expected}, got {button_text[:2]}'})
                print(f"❌ Toggle step {i+1} failed: expected {expected}, got {button_text[:2]}")
        
        return results
    
    async def run_all_tests(self):
        """Run all enhancement tests"""
        print("🧪 ENHANCED CHANNEL SELECTION UI TESTS")
        print("=" * 60)
        
        # Run all test functions
        all_results = []
        test_functions = [
            self.test_toggle_indicator_design,
            self.test_subscriber_count_display,
            self.test_multilingual_support,
            self.test_long_channel_names,
            self.test_mobile_friendly_spacing,
            self.test_toggle_behavior_flow
        ]
        
        for test_func in test_functions:
            try:
                results = await test_func()
                all_results.extend(results)
            except Exception as e:
                print(f"❌ Test {test_func.__name__} failed with error: {e}")
                all_results.append({
                    'test': test_func.__name__,
                    'status': 'ERROR',
                    'details': str(e)
                })
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in all_results if r['status'] == 'PASS')
        failed = sum(1 for r in all_results if r['status'] == 'FAIL')
        errors = sum(1 for r in all_results if r['status'] == 'ERROR')
        total = len(all_results)
        
        print(f"✅ PASSED: {passed}/{total}")
        print(f"❌ FAILED: {failed}/{total}")
        print(f"⚠️  ERRORS: {errors}/{total}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"🎯 SUCCESS RATE: {success_rate:.1f}%")
        
        # Detailed results
        print("\n📊 DETAILED RESULTS:")
        for result in all_results:
            status_emoji = "✅" if result['status'] == 'PASS' else ("❌" if result['status'] == 'FAIL' else "⚠️")
            print(f"{status_emoji} {result['test']}: {result['details']}")
        
        return all_results

async def main():
    """Main test runner"""
    test_suite = TestEnhancedChannelUI()
    results = await test_suite.run_all_tests()
    
    # Return success if all tests pass
    passed = sum(1 for r in results if r['status'] == 'PASS')
    total = len(results)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Enhanced channel selection UI is working correctly.")
        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    asyncio.run(main())