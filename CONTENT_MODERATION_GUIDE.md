# Content Moderation System Guide

## Overview

The I3lani Bot now includes a comprehensive content moderation system with a six-strike policy that ensures compliance with Telegram rules, international regulations, ethical standards, human rights, and Saudi Arabian regulations.

## Six-Strike Policy

### How It Works

1. **Strikes 1-5**: User receives warning and opportunity to edit content
2. **Strike 6**: Permanent ban and ad cancellation without compensation

### Violation Categories

**Content Standards:**
- Hate speech or discriminatory content
- Adult or sexual content  
- Illegal activities or substances
- Violent or harmful content
- Spam or excessive promotional content
- Fraudulent or misleading information

**Cultural Compliance:**
- Religious compliance violations
- Cultural compliance violations
- Political content violations

**International Standards:**
- Human rights violations
- Child rights violations
- Privacy/data protection violations
- Financial regulation violations
- Copyright infringement

**Saudi Arabian Regulations:**
- Anti-Islamic content
- Alcohol/pork promotion
- Political opposition content

## Admin Management

### Content Moderation Panel

Access through `/admin` → Content Moderation:

- **Violation Statistics**: Real-time violation counts and categories
- **Active Warnings**: Users with current strikes
- **Banned Users**: Permanently banned accounts
- **Violation History**: Detailed violation logs
- **Moderation Settings**: System configuration
- **Manual Review**: Admin review of flagged content

### Violation Reports Dashboard

Comprehensive analytics including:
- Daily violation statistics
- Violation category breakdown
- Strike distribution across users
- Rejection rates and trends

## User Experience

### Content Submission Flow

1. User creates ad content
2. System automatically scans for violations
3. If violations found:
   - User receives detailed warning
   - Edit opportunity provided
   - Strike recorded
4. If no violations:
   - Content approved
   - Ad proceeds to payment

### Warning System

Users receive detailed violation explanations including:
- Specific violation categories
- Remaining chances (out of 6)
- Clear guidelines for compliance
- Edit or cancel options

### Edit Opportunities

After receiving a violation warning, users can:
- **Edit Ad**: Modify content to comply with guidelines
- **Cancel Ad**: Cancel the ad creation
- **View Rules**: Review complete publishing guidelines
- **Contact Support**: Get assistance with compliance

## Technical Implementation

### Database Tables

- `user_moderation_status`: Track user strikes and status
- `content_violations`: Log specific violations
- `moderation_logs`: Complete audit trail
- `banned_users`: Permanently banned accounts

### Violation Detection

The system uses pattern matching and keyword analysis to detect:
- Hate speech patterns
- Adult content keywords
- Illegal activity references
- Cultural/religious violations
- Spam indicators
- Violence/harm content

### Compliance Checks

**Telegram Guidelines**: Community standards enforcement
**International Regulations**: GDPR, human rights, financial laws
**Ethical Standards**: Fairness, respect, dignity
**Human Rights**: No discrimination, exploitation, trafficking
**Saudi Arabian Laws**: Religious, cultural, political compliance

## Benefits

### For Users
- Clear guidelines and expectations
- Multiple opportunities to correct violations
- Transparent strike system
- Educational warnings

### For Administrators
- Automated violation detection
- Comprehensive reporting
- Manual review capabilities
- Audit trail maintenance

### For Platform
- Regulatory compliance
- Reduced liability
- Quality content assurance
- Community standards enforcement

## Contact

For content moderation questions or appeals:
- Support: @I3lani_support
- Admin review available for disputed violations
- Clear guidelines provided for all policies

---

*Last updated: July 08, 2025*
*System version: 1.0*