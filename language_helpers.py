#!/usr/bin/env python3
"""
Language Wrapper Functions
Easy access to automatic language system
"""

from automatic_language_system import get_user_language_auto, localize_text_auto

async def get_language(user_id: int) -> str:
    """Get user language (wrapper)"""
    return await get_user_language_auto(user_id)

async def get_localized_text(user_id: int, text_key: str, **kwargs) -> str:
    """Get localized text (wrapper)"""
    return await localize_text_auto(user_id, text_key, **kwargs)

async def get_text_for_user(user_id: int, key: str, **kwargs) -> str:
    """Get text for user in their language"""
    language = await get_language(user_id)
    
    from languages import get_text
    text = get_text(language, key)
    
    if kwargs:
        text = text.format(**kwargs)
    
    return text
