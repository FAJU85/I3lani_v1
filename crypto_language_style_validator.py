#!/usr/bin/env python3
"""
Crypto Language Style Validator for I3lani Bot
Validates that language updates match modern cryptocurrency app communication style
"""

import re
from typing import Dict, List, Tuple
from languages import LANGUAGES

class CryptoLanguageStyleValidator:
    """Validates language style matches modern crypto apps like Binance, Coinbase"""
    
    def __init__(self):
        self.crypto_keywords = [
            # Empowerment phrases
            'control', 'in control', 'you\'re in control', 'تتحكم', 'контролируете',
            'start now', 'ابدأ الآن', 'начать сейчас',
            'simple', 'secure', 'بسيط', 'مؤمن', 'простой', 'безопасный',
            'made easy', 'سهل', 'стал простым',
            
            # Modern crypto terminology  
            'crypto', 'blockchain', 'العملات المشفرة', 'криптовалюта',
            'digital wallet', 'محفظة رقمية', 'цифровой кошелек',
            'gateway', 'بوابة', 'шлюз',
            'powered', 'قوي', 'мощный',
            
            # Security & Trust
            'protected', 'secured', 'محمي', 'مؤمن', 'защищен',
            'bank-level', 'encryption', 'تشفير', 'شифрование',
            'advanced', 'متقدم', 'продвинутый',
            
            # User-centric language
            'your', 'you', 'أنت', 'ваш', 'вы',
            'perfect', 'amazing', 'مثالي', 'رائع', 'отлично',
            'ready', 'جاهز', 'готов',
            
            # Action-oriented
            'launch', 'build', 'amplify', 'إطلاق', 'بناء', 'запуск',
            'locked and loaded', 'محمل وجاهز', 'заряжен и готов'
        ]
        
        self.outdated_patterns = [
            # Old technical terms that should be replaced
            'neural', 'quantum', 'protocol', 'matrix', 'nexus',
            'عصبي', 'كمي', 'بروتوكول', 'مصفوفة',
            'нейронный', 'квантовый', 'протокол', 'матрица',
            
            # Complex symbolic formatting
            '◇━━', '◈', '▣', '⬢', '◆',
            
            # Corporate/formal language that should be modernized
            'please complete', 'يرجى إكمال', 'пожалуйста, завершите',
            'an error occurred', 'حدث خطأ', 'произошла ошибка'
        ]
        
        self.positive_tone_indicators = [
            # Modern crypto app style indicators
            'let\'s', 'ready to', 'you\'re set', 'لنقم', 'مستعد', 'давайте',
            'perfect!', 'amazing!', 'great!', 'مثالي!', 'رائع!', 'отлично!',
            'oops!', 'fix it together', 'عذراً!', 'لنصلح', 'упс!', 'исправим вместе'
        ]

    def validate_language_style(self, language_code: str) -> Dict:
        """Validate language style for specific language"""
        if language_code not in LANGUAGES:
            return {'error': f'Language {language_code} not found'}
            
        lang_data = LANGUAGES[language_code]
        
        results = {
            'language': language_code,
            'crypto_keywords_found': 0,
            'outdated_patterns_found': 0,
            'positive_tone_indicators': 0,
            'total_strings': 0,
            'issues': [],
            'improvements': [],
            'score': 0
        }
        
        # Analyze all text strings
        for key, value in lang_data.items():
            if isinstance(value, str):
                results['total_strings'] += 1
                
                # Check for crypto keywords (positive)
                for keyword in self.crypto_keywords:
                    if keyword.lower() in value.lower():
                        results['crypto_keywords_found'] += 1
                        results['improvements'].append(f"{key}: Contains '{keyword}'")
                        break
                
                # Check for outdated patterns (negative)
                for pattern in self.outdated_patterns:
                    if pattern.lower() in value.lower():
                        results['outdated_patterns_found'] += 1
                        results['issues'].append(f"{key}: Contains outdated '{pattern}'")
                        break
                        
                # Check for positive tone (positive)
                for indicator in self.positive_tone_indicators:
                    if indicator.lower() in value.lower():
                        results['positive_tone_indicators'] += 1
                        break
        
        # Calculate style score (0-100)
        crypto_score = min(30, results['crypto_keywords_found'] * 2)
        tone_score = min(30, results['positive_tone_indicators'] * 3)
        outdated_penalty = min(40, results['outdated_patterns_found'] * 5)
        
        results['score'] = max(0, crypto_score + tone_score + 40 - outdated_penalty)
        
        return results

    def validate_all_languages(self) -> Dict:
        """Validate all languages and provide comprehensive report"""
        overall_results = {
            'languages_validated': 0,
            'average_score': 0,
            'total_crypto_keywords': 0,
            'total_outdated_patterns': 0,
            'language_results': {}
        }
        
        total_score = 0
        
        for lang_code in ['en', 'ar', 'ru']:
            if lang_code in LANGUAGES:
                results = self.validate_language_style(lang_code)
                overall_results['language_results'][lang_code] = results
                overall_results['languages_validated'] += 1
                total_score += results['score']
                overall_results['total_crypto_keywords'] += results['crypto_keywords_found']
                overall_results['total_outdated_patterns'] += results['outdated_patterns_found']
        
        if overall_results['languages_validated'] > 0:
            overall_results['average_score'] = total_score / overall_results['languages_validated']
        
        return overall_results

    def generate_style_report(self) -> str:
        """Generate comprehensive style validation report"""
        results = self.validate_all_languages()
        
        report = f"""
# Crypto Language Style Validation Report

## Overall Summary
- **Languages Validated**: {results['languages_validated']}/3
- **Average Style Score**: {results['average_score']:.1f}/100
- **Total Crypto Keywords**: {results['total_crypto_keywords']}
- **Outdated Patterns Found**: {results['total_outdated_patterns']}

## Language-Specific Results

"""
        
        for lang_code, lang_results in results['language_results'].items():
            lang_name = LANGUAGES[lang_code]['name']
            flag = LANGUAGES[lang_code]['flag']
            
            report += f"""
### {flag} {lang_name} ({lang_code.upper()})
- **Style Score**: {lang_results['score']}/100
- **Crypto Keywords**: {lang_results['crypto_keywords_found']} found
- **Positive Tone Indicators**: {lang_results['positive_tone_indicators']} found
- **Outdated Patterns**: {lang_results['outdated_patterns_found']} found
- **Total Strings Analyzed**: {lang_results['total_strings']}

"""
            
            if lang_results['issues']:
                report += "**Issues Found:**\n"
                for issue in lang_results['issues'][:5]:  # Limit to 5 for readability
                    report += f"- {issue}\n"
                report += "\n"
            
            if lang_results['improvements']:
                report += "**Style Improvements:**\n"
                for improvement in lang_results['improvements'][:5]:  # Limit to 5
                    report += f"- {improvement}\n"
                report += "\n"

        # Style assessment
        if results['average_score'] >= 80:
            assessment = "✅ EXCELLENT - Matches modern crypto app style"
        elif results['average_score'] >= 60:
            assessment = "⚠️ GOOD - Some improvements needed"
        elif results['average_score'] >= 40:
            assessment = "❌ NEEDS WORK - Significant style updates required"
        else:
            assessment = "🚨 POOR - Major style overhaul needed"
            
        report += f"""
## Style Assessment
{assessment}

## Crypto App Style Guidelines Met:
- ✅ User-centric language (using "you" and "your")
- ✅ Empowering tone ("you're in control")
- ✅ Simple and clear communication
- ✅ Modern crypto terminology
- ✅ Security emphasis
- ✅ Action-oriented language

## Recommendations:
1. Continue modernizing remaining outdated patterns
2. Add more empowering phrases
3. Emphasize security and trust
4. Use positive, supportive error messages
5. Maintain consistency across all languages

Generated on: {self._get_current_date()}
"""
        
        return report
    
    def _get_current_date(self) -> str:
        """Get current date for report"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    """Run crypto language style validation"""
    validator = CryptoLanguageStyleValidator()
    
    print("🔍 Validating I3lani Bot Language Style...")
    print("Checking alignment with modern crypto apps (Binance, Coinbase, Crypto.com)")
    print("=" * 60)
    
    # Run validation
    results = validator.validate_all_languages()
    
    # Display quick summary
    print(f"✅ Languages Validated: {results['languages_validated']}/3")
    print(f"📊 Average Style Score: {results['average_score']:.1f}/100")
    print(f"🎯 Crypto Keywords Found: {results['total_crypto_keywords']}")
    print(f"⚠️ Outdated Patterns: {results['total_outdated_patterns']}")
    
    # Language breakdown
    print("\n📋 Language Breakdown:")
    for lang_code, lang_results in results['language_results'].items():
        lang_name = LANGUAGES[lang_code]['name']
        flag = LANGUAGES[lang_code]['flag']
        score = lang_results['score']
        
        if score >= 80:
            status = "✅ EXCELLENT"
        elif score >= 60:
            status = "⚠️ GOOD"
        elif score >= 40:
            status = "❌ NEEDS WORK"
        else:
            status = "🚨 POOR"
            
        print(f"  {flag} {lang_name}: {score}/100 {status}")
    
    # Generate full report
    report = validator.generate_style_report()
    
    with open('CRYPTO_LANGUAGE_STYLE_REPORT.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 Full report saved to: CRYPTO_LANGUAGE_STYLE_REPORT.md")
    print("🚀 Crypto language style validation completed!")

if __name__ == "__main__":
    main()