#!/usr/bin/env python3
"""
Comprehensive UI Cleanup Validation System
Validates removal of outdated neural/quantum terminology and ensures clean, user-friendly interface
"""

import asyncio
import re
import os
from pathlib import Path
from typing import Dict, List, Tuple, Any

class UICleanupValidator:
    """Validates UI cleanup across all bot components"""
    
    def __init__(self):
        self.validation_results = {
            'outdated_terms': [],
            'complex_symbols': [],
            'language_consistency': [],
            'button_functionality': [],
            'clean_interface': [],
            'user_friendly_text': []
        }
        
        # Terms that should be removed
        self.outdated_terms = [
            'neural', 'quantum', 'protocol', 'nexus', 'matrix',
            'cyber', 'holographic', 'node', 'mining', 'vault'
        ]
        
        # Complex symbols that should be simplified
        self.complex_symbols = [
            '◇━━', '◈', '▣', '⬢', '◆', '━━━', '◇'
        ]
        
        # Files to check
        self.files_to_check = [
            'languages.py',
            'handlers.py',
            'admin_system.py',
            'modern_keyboard.py'
        ]
    
    def validate_file_content(self, file_path: str) -> Dict[str, Any]:
        """Validate content of a specific file"""
        results = {
            'file': file_path,
            'outdated_terms_found': [],
            'complex_symbols_found': [],
            'lines_checked': 0,
            'issues_found': 0
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                results['lines_checked'] = len(lines)
                
                # Check for outdated terms (case-insensitive)
                for term in self.outdated_terms:
                    pattern = re.compile(term, re.IGNORECASE)
                    matches = pattern.findall(content)
                    if matches:
                        results['outdated_terms_found'].append({
                            'term': term,
                            'count': len(matches),
                            'case_sensitive': term in content
                        })
                
                # Check for complex symbols
                for symbol in self.complex_symbols:
                    if symbol in content:
                        count = content.count(symbol)
                        results['complex_symbols_found'].append({
                            'symbol': symbol,
                            'count': count
                        })
                
                results['issues_found'] = len(results['outdated_terms_found']) + len(results['complex_symbols_found'])
                
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def check_language_consistency(self) -> Dict[str, Any]:
        """Check language consistency across all translations"""
        results = {
            'languages_checked': ['en', 'ar', 'ru'],
            'consistency_issues': [],
            'missing_translations': [],
            'clean_text_validation': []
        }
        
        try:
            # Import the languages module
            import languages
            
            # Check key translation consistency
            key_sections = ['main_menu', 'create_ad', 'payment', 'settings']
            
            for section in key_sections:
                for lang in results['languages_checked']:
                    lang_dict = getattr(languages, 'LANGUAGES', {}).get(lang, {})
                    
                    # Check if section-related keys exist
                    section_keys = [k for k in lang_dict.keys() if section in k]
                    
                    if section_keys:
                        for key in section_keys:
                            text = lang_dict.get(key, '')
                            
                            # Check for outdated terms in translations
                            for term in self.outdated_terms:
                                if term.lower() in text.lower():
                                    results['consistency_issues'].append({
                                        'language': lang,
                                        'key': key,
                                        'term': term,
                                        'text_preview': text[:100] + '...' if len(text) > 100 else text
                                    })
                            
                            # Check for complex symbols
                            for symbol in self.complex_symbols:
                                if symbol in text:
                                    results['consistency_issues'].append({
                                        'language': lang,
                                        'key': key,
                                        'symbol': symbol,
                                        'text_preview': text[:100] + '...' if len(text) > 100 else text
                                    })
            
            # Validate clean text examples
            sample_keys = ['main_menu', 'create_ad', 'send_ad_content', 'choose_payment']
            for key in sample_keys:
                for lang in results['languages_checked']:
                    lang_dict = getattr(languages, 'LANGUAGES', {}).get(lang, {})
                    if key in lang_dict:
                        text = lang_dict[key]
                        results['clean_text_validation'].append({
                            'language': lang,
                            'key': key,
                            'text': text,
                            'is_clean': not any(term.lower() in text.lower() for term in self.outdated_terms),
                            'has_simple_symbols': not any(symbol in text for symbol in self.complex_symbols)
                        })
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def validate_button_functionality(self) -> Dict[str, Any]:
        """Validate button functionality and clean text"""
        results = {
            'button_validation': [],
            'clean_buttons': [],
            'outdated_buttons': []
        }
        
        try:
            # Check handlers.py for button callback handlers
            with open('handlers.py', 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Find button callback patterns
                button_patterns = [
                    r'callback_data="([^"]*)"',
                    r'text="([^"]*)"',
                    r'InlineKeyboardButton\(text="([^"]*)"'
                ]
                
                for pattern in button_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        # Check if button text contains outdated terms
                        has_outdated = any(term.lower() in match.lower() for term in self.outdated_terms)
                        has_complex = any(symbol in match for symbol in self.complex_symbols)
                        
                        button_info = {
                            'text': match,
                            'has_outdated_terms': has_outdated,
                            'has_complex_symbols': has_complex,
                            'is_clean': not (has_outdated or has_complex)
                        }
                        
                        if button_info['is_clean']:
                            results['clean_buttons'].append(button_info)
                        else:
                            results['outdated_buttons'].append(button_info)
            
            results['button_validation'] = {
                'total_buttons': len(results['clean_buttons']) + len(results['outdated_buttons']),
                'clean_buttons': len(results['clean_buttons']),
                'outdated_buttons': len(results['outdated_buttons']),
                'cleanliness_rate': len(results['clean_buttons']) / max(1, len(results['clean_buttons']) + len(results['outdated_buttons'])) * 100
            }
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def validate_user_friendly_interface(self) -> Dict[str, Any]:
        """Validate overall user-friendly interface improvements"""
        results = {
            'interface_improvements': [],
            'modern_elements': [],
            'accessibility_check': [],
            'language_clarity': []
        }
        
        try:
            # Check for modern, clear interface elements
            modern_patterns = [
                '📝 **Create',
                '💳 **Payment',
                '⏱️ **Choose',
                '📞 **Contact',
                '✅ Content received',
                '🎯 **Referral',
                '📊 Referral Stats'
            ]
            
            complex_patterns = [
                '◇━━',
                'NEURAL',
                'QUANTUM',
                'PROTOCOL',
                '▣ TRANSMIT'
            ]
            
            for file_path in self.files_to_check:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Count modern elements
                        modern_count = sum(1 for pattern in modern_patterns if pattern in content)
                        complex_count = sum(1 for pattern in complex_patterns if pattern in content)
                        
                        results['interface_improvements'].append({
                            'file': file_path,
                            'modern_elements': modern_count,
                            'outdated_elements': complex_count,
                            'improvement_ratio': modern_count / max(1, complex_count) if complex_count > 0 else float('inf')
                        })
            
            # Check language clarity
            clarity_indicators = [
                'Create Your Advertisement',
                'Select Payment Method',
                'Choose Campaign Duration',
                'Upload Photo',
                'Add Text',
                'Contact Information'
            ]
            
            outdated_indicators = [
                'Neural Upload',
                'Quantum Gift',
                'Protocol',
                'Transmit Data',
                'Neural Contact'
            ]
            
            try:
                import languages
                lang_dict = getattr(languages, 'LANGUAGES', {}).get('en', {})
                
                clear_count = sum(1 for indicator in clarity_indicators 
                                if any(indicator.lower() in str(v).lower() for v in lang_dict.values()))
                
                outdated_count = sum(1 for indicator in outdated_indicators 
                                   if any(indicator.lower() in str(v).lower() for v in lang_dict.values()))
                
                results['language_clarity'] = {
                    'clear_language_count': clear_count,
                    'outdated_language_count': outdated_count,
                    'clarity_improvement': clear_count / max(1, outdated_count) if outdated_count > 0 else float('inf')
                }
            except Exception as e:
                results['language_clarity'] = {'error': str(e)}
        
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    async def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive UI cleanup validation"""
        print("🔍 Running comprehensive UI cleanup validation...")
        
        # File content validation
        print("\n📁 Validating file content...")
        file_results = []
        for file_path in self.files_to_check:
            if os.path.exists(file_path):
                result = self.validate_file_content(file_path)
                file_results.append(result)
                print(f"   ✅ {file_path}: {result['issues_found']} issues found")
        
        # Language consistency validation
        print("\n🌍 Validating language consistency...")
        language_results = self.check_language_consistency()
        print(f"   ✅ Languages checked: {len(language_results['languages_checked'])}")
        print(f"   ✅ Consistency issues: {len(language_results['consistency_issues'])}")
        
        # Button functionality validation
        print("\n🔘 Validating button functionality...")
        button_results = self.validate_button_functionality()
        if 'button_validation' in button_results:
            print(f"   ✅ Button cleanliness: {button_results['button_validation']['cleanliness_rate']:.1f}%")
        
        # User-friendly interface validation
        print("\n👥 Validating user-friendly interface...")
        interface_results = self.validate_user_friendly_interface()
        print(f"   ✅ Interface improvements validated")
        
        # Compile final results
        final_results = {
            'validation_summary': {
                'timestamp': asyncio.get_event_loop().time(),
                'total_files_checked': len(file_results),
                'total_issues_found': sum(r['issues_found'] for r in file_results),
                'language_consistency_issues': len(language_results['consistency_issues']),
                'button_cleanliness_rate': button_results.get('button_validation', {}).get('cleanliness_rate', 0),
                'overall_status': 'CLEAN' if sum(r['issues_found'] for r in file_results) == 0 else 'NEEDS_ATTENTION'
            },
            'file_validation': file_results,
            'language_validation': language_results,
            'button_validation': button_results,
            'interface_validation': interface_results,
            'recommendations': []
        }
        
        # Generate recommendations
        if final_results['validation_summary']['total_issues_found'] > 0:
            final_results['recommendations'].append("Review and fix remaining outdated terminology")
        
        if final_results['validation_summary']['language_consistency_issues'] > 0:
            final_results['recommendations'].append("Address language consistency issues")
        
        if final_results['validation_summary']['button_cleanliness_rate'] < 90:
            final_results['recommendations'].append("Clean up remaining button terminology")
        
        if not final_results['recommendations']:
            final_results['recommendations'].append("UI cleanup validation successful - interface is clean and user-friendly")
        
        return final_results
    
    def generate_validation_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive validation report"""
        report = []
        report.append("=" * 60)
        report.append("UI CLEANUP VALIDATION REPORT")
        report.append("=" * 60)
        
        # Summary
        summary = results['validation_summary']
        report.append(f"\n📊 VALIDATION SUMMARY")
        report.append(f"   Status: {summary['overall_status']}")
        report.append(f"   Files Checked: {summary['total_files_checked']}")
        report.append(f"   Issues Found: {summary['total_issues_found']}")
        report.append(f"   Language Issues: {summary['language_consistency_issues']}")
        report.append(f"   Button Cleanliness: {summary['button_cleanliness_rate']:.1f}%")
        
        # File validation details
        report.append(f"\n📁 FILE VALIDATION DETAILS")
        for file_result in results['file_validation']:
            report.append(f"   {file_result['file']}:")
            report.append(f"     Lines Checked: {file_result['lines_checked']}")
            report.append(f"     Issues: {file_result['issues_found']}")
            
            if file_result['outdated_terms_found']:
                report.append(f"     Outdated Terms:")
                for term in file_result['outdated_terms_found']:
                    report.append(f"       - {term['term']}: {term['count']} occurrences")
            
            if file_result['complex_symbols_found']:
                report.append(f"     Complex Symbols:")
                for symbol in file_result['complex_symbols_found']:
                    report.append(f"       - {symbol['symbol']}: {symbol['count']} occurrences")
        
        # Language validation
        lang_results = results['language_validation']
        report.append(f"\n🌍 LANGUAGE VALIDATION")
        report.append(f"   Languages: {', '.join(lang_results['languages_checked'])}")
        report.append(f"   Consistency Issues: {len(lang_results['consistency_issues'])}")
        
        if lang_results['consistency_issues']:
            report.append(f"   Issues Found:")
            for issue in lang_results['consistency_issues'][:5]:  # Show first 5
                report.append(f"     - {issue['language']}: {issue.get('term', issue.get('symbol', 'Unknown'))}")
        
        # Button validation
        button_results = results['button_validation']
        if 'button_validation' in button_results:
            bv = button_results['button_validation']
            report.append(f"\n🔘 BUTTON VALIDATION")
            report.append(f"   Total Buttons: {bv['total_buttons']}")
            report.append(f"   Clean Buttons: {bv['clean_buttons']}")
            report.append(f"   Outdated Buttons: {bv['outdated_buttons']}")
            report.append(f"   Cleanliness Rate: {bv['cleanliness_rate']:.1f}%")
        
        # Interface validation
        interface_results = results['interface_validation']
        report.append(f"\n👥 INTERFACE VALIDATION")
        if 'language_clarity' in interface_results and 'error' not in interface_results['language_clarity']:
            lc = interface_results['language_clarity']
            report.append(f"   Clear Language Elements: {lc['clear_language_count']}")
            report.append(f"   Outdated Language Elements: {lc['outdated_language_count']}")
            report.append(f"   Clarity Improvement: {lc['clarity_improvement']:.1f}x")
        
        # Recommendations
        report.append(f"\n🎯 RECOMMENDATIONS")
        for rec in results['recommendations']:
            report.append(f"   • {rec}")
        
        report.append(f"\n" + "=" * 60)
        report.append(f"VALIDATION COMPLETE")
        report.append(f"=" * 60)
        
        return "\n".join(report)

async def main():
    """Main validation function"""
    validator = UICleanupValidator()
    
    print("🚀 Starting UI Cleanup Validation...")
    results = await validator.run_comprehensive_validation()
    
    print("\n" + "=" * 60)
    print("VALIDATION RESULTS")
    print("=" * 60)
    
    report = validator.generate_validation_report(results)
    print(report)
    
    # Save report to file
    with open('ui_cleanup_validation_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n💾 Validation report saved to ui_cleanup_validation_report.txt")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())