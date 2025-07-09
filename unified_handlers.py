#!/usr/bin/env python3
"""
Unified Handlers for I3lani Bot
Uses the unified journey engine for consistent flow across all languages
"""

from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from unified_journey import get_unified_step, get_next_journey_step, JourneyStep, validate_journey
from languages import get_text, get_user_language, LANGUAGES
from database import get_user_language as db_get_user_language, set_user_language
from enhanced_callback_handler import safe_callback_edit, safe_callback_answer
from modern_keyboard import create_modern_keyboard, create_modern_confirmation
from logger import log_info, log_error, StepNames

router = Router()

class UnifiedFlowHandler:
    """Handles unified user flow across all languages"""
    
    def __init__(self):
        self.current_steps = {}  # Track current step for each user
    
    async def process_step(self, user_id: int, step: JourneyStep, callback_query: CallbackQuery = None, 
                          message: Message = None, data: dict = None):
        """Process a unified step for any language"""
        # Get user language
        language = await db_get_user_language(user_id)
        if language not in LANGUAGES:
            language = 'en'
        
        # Get step content
        step_content = get_unified_step(step, language, user_id, data)
        
        # Track current step
        self.current_steps[user_id] = step
        
        # Build keyboard
        keyboard = self._build_step_keyboard(step_content, language)
        
        # Format message
        message_text = f"{step_content['title']}\n\n{step_content['description']}"
        
        # Send or edit message
        if callback_query:
            await safe_callback_edit(
                callback_query,
                text=message_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        elif message:
            await message.answer(
                message_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        
        # Step processed successfully
    
    def _build_step_keyboard(self, step_content: dict, language: str) -> InlineKeyboardMarkup:
        """Build keyboard for step content"""
        keyboard_rows = []
        
        # Build buttons from step content
        for button in step_content['buttons']:
            keyboard_rows.append([
                InlineKeyboardButton(
                    text=button['text'],
                    callback_data=button['action']
                )
            ])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    
    async def handle_callback(self, callback_query: CallbackQuery, state: FSMContext):
        """Handle callback with unified flow"""
        user_id = callback_query.from_user.id
        action = callback_query.data
        
        # Get current step
        current_step = self.current_steps.get(user_id, JourneyStep.MAIN_MENU)
        
        # Handle language changes
        if action.startswith('lang_'):
            language_code = action.split('_')[1]
            await set_user_language(user_id, language_code)
            log_info(StepNames.LANGUAGE_CHANGE, user_id, f"Language changed to: {language_code}")
            
            # Show main menu in new language
            await self.process_step(user_id, JourneyStep.MAIN_MENU, callback_query)
            return
        
        # Get next step
        next_step = get_next_journey_step(current_step, action)
        
        if next_step:
            await self.process_step(user_id, next_step, callback_query)
        else:
            # Handle special actions
            await self._handle_special_action(user_id, action, callback_query, state)
    
    async def _handle_special_action(self, user_id: int, action: str, 
                                   callback_query: CallbackQuery, state: FSMContext):
        """Handle special actions that don't have direct step mappings"""
        language = await db_get_user_language(user_id)
        
        if action == 'my_ads':
            await self._show_my_ads(user_id, callback_query, language)
        elif action == 'share_earn':
            await self._show_share_earn(user_id, callback_query, language)
        elif action == 'channel_partners':
            await self._show_channel_partners(user_id, callback_query, language)
        elif action == 'gaming_hub':
            await self._show_gaming_hub(user_id, callback_query, language)
        elif action == 'leaderboard':
            await self._show_leaderboard(user_id, callback_query, language)
        else:
            # Unknown action, go to main menu
            await self.process_step(user_id, JourneyStep.MAIN_MENU, callback_query)
    
    async def _show_my_ads(self, user_id: int, callback_query: CallbackQuery, language: str):
        """Show my ads dashboard"""
        text = get_text(language, 'my_ads_dashboard')
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(language, 'back_to_main'), callback_data='back_to_main')]
        ])
        await safe_callback_edit(callback_query, text=text, reply_markup=keyboard)
    
    async def _show_share_earn(self, user_id: int, callback_query: CallbackQuery, language: str):
        """Show share and earn portal"""
        text = get_text(language, 'share_earn_portal')
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(language, 'back_to_main'), callback_data='back_to_main')]
        ])
        await safe_callback_edit(callback_query, text=text, reply_markup=keyboard)
    
    async def _show_channel_partners(self, user_id: int, callback_query: CallbackQuery, language: str):
        """Show channel partners interface"""
        text = get_text(language, 'channel_partners_interface')
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(language, 'back_to_main'), callback_data='back_to_main')]
        ])
        await safe_callback_edit(callback_query, text=text, reply_markup=keyboard)
    
    async def _show_gaming_hub(self, user_id: int, callback_query: CallbackQuery, language: str):
        """Show gaming hub"""
        text = get_text(language, 'gaming_hub_interface')
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(language, 'back_to_main'), callback_data='back_to_main')]
        ])
        await safe_callback_edit(callback_query, text=text, reply_markup=keyboard)
    
    async def _show_leaderboard(self, user_id: int, callback_query: CallbackQuery, language: str):
        """Show leaderboard"""
        text = get_text(language, 'leaderboard_interface')
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(language, 'back_to_main'), callback_data='back_to_main')]
        ])
        await safe_callback_edit(callback_query, text=text, reply_markup=keyboard)

# Global handler instance
flow_handler = UnifiedFlowHandler()

@router.callback_query(F.data == "start_unified")
async def unified_start_handler(callback_query: CallbackQuery, state: FSMContext):
    """Unified start handler"""
    user_id = callback_query.from_user.id
    await flow_handler.process_step(user_id, JourneyStep.MAIN_MENU, callback_query)

@router.callback_query(F.data == "create_ad_unified")
async def unified_create_ad_handler(callback_query: CallbackQuery, state: FSMContext):
    """Unified create ad handler"""
    user_id = callback_query.from_user.id
    await flow_handler.process_step(user_id, JourneyStep.AD_CREATION_START, callback_query)

@router.callback_query(F.data == "settings_unified")
async def unified_settings_handler(callback_query: CallbackQuery, state: FSMContext):
    """Unified settings handler"""
    user_id = callback_query.from_user.id
    await flow_handler.process_step(user_id, JourneyStep.SETTINGS_MENU, callback_query)

@router.callback_query(F.data == "help_unified")
async def unified_help_handler(callback_query: CallbackQuery, state: FSMContext):
    """Unified help handler"""
    user_id = callback_query.from_user.id
    await flow_handler.process_step(user_id, JourneyStep.HELP_DISPLAY, callback_query)

@router.callback_query()
async def unified_callback_handler(callback_query: CallbackQuery, state: FSMContext):
    """Unified callback handler for all actions"""
    try:
        await flow_handler.handle_callback(callback_query, state)
    except Exception as e:
        user_id = callback_query.from_user.id
        language = await db_get_user_language(user_id)
        log_error(StepNames.ERROR_HANDLER, user_id, e, {"action": callback_query.data})
        
        # Show error and return to main menu
        await safe_callback_answer(callback_query, get_text(language, 'error_processing_request'))
        await flow_handler.process_step(user_id, JourneyStep.MAIN_MENU, callback_query)

def setup_unified_handlers(dp):
    """Setup unified handlers"""
    dp.include_router(router)
    
    # Validate journey consistency on startup
    validation_result = validate_journey()
    if validation_result['valid']:
        print("✅ Unified journey validation passed - consistent flow across all languages")
    else:
        print("❌ Unified journey validation failed:")
        for error in validation_result['errors']:
            print(f"  - {error}")