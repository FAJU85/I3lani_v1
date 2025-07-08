"""
Admin UI Control Panel for I3lani Bot
Comprehensive interface for managing all bot text elements
"""

import logging
from typing import Dict, List, Optional
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import db, get_user_language
from ui_control_system import ui_control
from config import ADMIN_IDS
from languages import get_text

logger = logging.getLogger(__name__)
router = Router()

class UIControlStates(StatesGroup):
    """States for UI control management"""
    editing_text = State()
    importing_json = State()
    viewing_category = State()

class AdminUIControl:
    """Admin UI Control System"""
    
    def __init__(self):
        self.supported_languages = ['en', 'ar', 'ru']
        self.language_names = {
            'en': '🇺🇸 English',
            'ar': '🇸🇦 العربية',
            'ru': '🇷🇺 Русский'
        }
    
    async def show_main_ui_control_menu(self, callback_query: CallbackQuery, language: str):
        """Show main UI control menu"""
        stats = await db.get_ui_customization_stats()
        
        text = f"""
<b>🎨 UI Control Panel</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📊 Customization Statistics:</b>
• Total Customizations: <code>{stats.get('total_customizations', 0)}</code>
• Categories Modified: <code>{stats.get('categories_customized', 0)}</code>
• Text Keys Modified: <code>{stats.get('keys_customized', 0)}</code>
• Languages Customized: <code>{stats.get('languages_customized', 0)}</code>

<b>🔧 Available Actions:</b>
• Manage text by category
• Edit specific text elements
• Import/export configurations
• Reset to defaults
• View all customizations

<b>💡 What you can customize:</b>
• Button text (all languages)
• Welcome messages
• Error messages
• Success notifications
• Navigation elements
• Payment messages
        """
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📝 Edit Text by Category", callback_data="ui_edit_by_category"),
                InlineKeyboardButton(text="🔍 View All Customizations", callback_data="ui_view_all")
            ],
            [
                InlineKeyboardButton(text="📤 Export Config", callback_data="ui_export"),
                InlineKeyboardButton(text="📥 Import Config", callback_data="ui_import")
            ],
            [
                InlineKeyboardButton(text="🔄 Reset All", callback_data="ui_reset_all"),
                InlineKeyboardButton(text="📊 Statistics", callback_data="ui_stats")
            ],
            [
                InlineKeyboardButton(text="🌐 Language Management", callback_data="ui_language_mgmt"),
                InlineKeyboardButton(text="🔧 Quick Edit", callback_data="ui_quick_edit")
            ],
            [
                InlineKeyboardButton(text="◀️ Back to Admin", callback_data="admin_back")
            ]
        ])
        
        await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='HTML')
    
    async def show_category_selection(self, callback_query: CallbackQuery, language: str):
        """Show category selection menu"""
        categories = ui_control.get_available_categories()
        
        text = f"""
<b>📝 Select Text Category to Edit</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>Available Categories:</b>
        """
        
        keyboard_buttons = []
        category_descriptions = {
            'main_menu_buttons': '🏠 Main Menu Buttons',
            'welcome_messages': '👋 Welcome Messages',
            'navigation_buttons': '🧭 Navigation Buttons',
            'ad_creation': '📝 Ad Creation Messages',
            'payment_messages': '💳 Payment Messages',
            'error_messages': '❌ Error Messages',
            'success_messages': '✅ Success Messages'
        }
        
        for category in categories:
            description = category_descriptions.get(category, category.replace('_', ' ').title())
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=description,
                    callback_data=f"ui_category_{category}"
                )
            ])
        
        keyboard_buttons.append([
            InlineKeyboardButton(text="◀️ Back to UI Control", callback_data="ui_control_main")
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='HTML')
    
    async def show_category_texts(self, callback_query: CallbackQuery, category: str, language: str):
        """Show all texts in a category"""
        keys = ui_control.get_category_keys(category)
        
        category_names = {
            'main_menu_buttons': 'Main Menu Buttons',
            'welcome_messages': 'Welcome Messages',
            'navigation_buttons': 'Navigation Buttons',
            'ad_creation': 'Ad Creation Messages',
            'payment_messages': 'Payment Messages',
            'error_messages': 'Error Messages',
            'success_messages': 'Success Messages'
        }
        
        category_name = category_names.get(category, category.replace('_', ' ').title())
        
        text = f"""
<b>📝 {category_name}</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>Available Text Elements:</b>
        """
        
        keyboard_buttons = []
        for key in keys:
            # Get current text for preview
            current_text = await ui_control.get_text(category, key, language)
            preview = current_text[:30] + "..." if len(current_text) > 30 else current_text
            
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=f"✏️ {key}: {preview}",
                    callback_data=f"ui_edit_{category}_{key}"
                )
            ])
        
        keyboard_buttons.append([
            InlineKeyboardButton(text="◀️ Back to Categories", callback_data="ui_edit_by_category")
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='HTML')
    
    async def show_text_editor(self, callback_query: CallbackQuery, category: str, key: str, language: str):
        """Show text editor for specific element"""
        current_texts = {}
        for lang in self.supported_languages:
            current_texts[lang] = await ui_control.get_text(category, key, lang)
        
        text = f"""
<b>✏️ Edit Text Element</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>Category:</b> {category}
<b>Key:</b> {key}

<b>Current Text in All Languages:</b>

<b>🇺🇸 English:</b>
<code>{current_texts['en']}</code>

<b>🇸🇦 Arabic:</b>
<code>{current_texts['ar']}</code>

<b>🇷🇺 Russian:</b>
<code>{current_texts['ru']}</code>

<b>Select language to edit:</b>
        """
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇸 Edit English", callback_data=f"ui_edit_lang_{category}_{key}_en"),
                InlineKeyboardButton(text="🇸🇦 Edit Arabic", callback_data=f"ui_edit_lang_{category}_{key}_ar")
            ],
            [
                InlineKeyboardButton(text="🇷🇺 Edit Russian", callback_data=f"ui_edit_lang_{category}_{key}_ru")
            ],
            [
                InlineKeyboardButton(text="🔄 Reset to Default", callback_data=f"ui_reset_{category}_{key}"),
                InlineKeyboardButton(text="📋 Copy Text", callback_data=f"ui_copy_{category}_{key}")
            ],
            [
                InlineKeyboardButton(text="◀️ Back to Category", callback_data=f"ui_category_{category}")
            ]
        ])
        
        await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='HTML')
    
    async def start_text_editing(self, callback_query: CallbackQuery, category: str, key: str, language: str, state: FSMContext):
        """Start text editing process"""
        current_text = await ui_control.get_text(category, key, language)
        
        text = f"""
<b>✏️ Edit Text</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>Category:</b> {category}
<b>Key:</b> {key}
<b>Language:</b> {self.language_names[language]}

<b>Current Text:</b>
<code>{current_text}</code>

<b>Send new text:</b>
Type your new text message below. You can use HTML formatting:
• <b>bold</b>
• <i>italic</i>
• <code>code</code>
• <a href="url">link</a>

Type /cancel to cancel editing.
        """
        
        # Store editing context
        await state.set_data({
            'category': category,
            'key': key,
            'language': language,
            'original_text': current_text
        })
        await state.set_state(UIControlStates.editing_text)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="❌ Cancel", callback_data=f"ui_edit_{category}_{key}")
            ]
        ])
        
        await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='HTML')
    
    async def show_statistics(self, callback_query: CallbackQuery, language: str):
        """Show detailed UI customization statistics"""
        stats = await db.get_ui_customization_stats()
        all_customizations = await db.get_all_ui_customizations()
        
        text = f"""
<b>📊 UI Customization Statistics</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📈 Overall Statistics:</b>
• Total Customizations: <code>{stats.get('total_customizations', 0)}</code>
• Categories Modified: <code>{stats.get('categories_customized', 0)}</code>
• Text Keys Modified: <code>{stats.get('keys_customized', 0)}</code>
• Languages Customized: <code>{stats.get('languages_customized', 0)}</code>

<b>📋 Category Breakdown:</b>
        """
        
        category_breakdown = stats.get('category_breakdown', {})
        for category, count in category_breakdown.items():
            text += f"• {category}: <code>{count}</code> customizations\n"
        
        text += f"""
<b>🌐 Language Coverage:</b>
        """
        
        # Count customizations per language
        lang_stats = {}
        for category_data in all_customizations.values():
            for key_data in category_data.values():
                for lang in key_data.keys():
                    lang_stats[lang] = lang_stats.get(lang, 0) + 1
        
        for lang, count in lang_stats.items():
            lang_name = self.language_names.get(lang, lang)
            text += f"• {lang_name}: <code>{count}</code> customizations\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📤 Export All", callback_data="ui_export"),
                InlineKeyboardButton(text="🔄 Refresh Stats", callback_data="ui_stats")
            ],
            [
                InlineKeyboardButton(text="◀️ Back to UI Control", callback_data="ui_control_main")
            ]
        ])
        
        await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='HTML')

# Global admin UI control instance
admin_ui_control = AdminUIControl()

# Handler registrations
@router.callback_query(F.data == "ui_control_main")
async def ui_control_main_handler(callback_query: CallbackQuery):
    """Handle main UI control menu"""
    user_id = callback_query.from_user.id
    if user_id not in ADMIN_IDS:
        await callback_query.answer("❌ Access denied", show_alert=True)
        return
    
    language = await get_user_language(user_id)
    await admin_ui_control.show_main_ui_control_menu(callback_query, language)

@router.callback_query(F.data == "ui_edit_by_category")
async def ui_edit_by_category_handler(callback_query: CallbackQuery):
    """Handle category selection"""
    user_id = callback_query.from_user.id
    if user_id not in ADMIN_IDS:
        await callback_query.answer("❌ Access denied", show_alert=True)
        return
    
    language = await get_user_language(user_id)
    await admin_ui_control.show_category_selection(callback_query, language)

@router.callback_query(F.data.startswith("ui_category_"))
async def ui_category_handler(callback_query: CallbackQuery):
    """Handle category text display"""
    user_id = callback_query.from_user.id
    if user_id not in ADMIN_IDS:
        await callback_query.answer("❌ Access denied", show_alert=True)
        return
    
    category = callback_query.data.replace("ui_category_", "")
    language = await get_user_language(user_id)
    await admin_ui_control.show_category_texts(callback_query, category, language)

@router.callback_query(F.data.startswith("ui_edit_") & ~F.data.startswith("ui_edit_lang_"))
async def ui_edit_handler(callback_query: CallbackQuery):
    """Handle text element editing"""
    user_id = callback_query.from_user.id
    if user_id not in ADMIN_IDS:
        await callback_query.answer("❌ Access denied", show_alert=True)
        return
    
    data_parts = callback_query.data.replace("ui_edit_", "").split("_", 1)
    category = data_parts[0]
    key = data_parts[1]
    language = await get_user_language(user_id)
    
    await admin_ui_control.show_text_editor(callback_query, category, key, language)

@router.callback_query(F.data.startswith("ui_edit_lang_"))
async def ui_edit_lang_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle language-specific text editing"""
    user_id = callback_query.from_user.id
    if user_id not in ADMIN_IDS:
        await callback_query.answer("❌ Access denied", show_alert=True)
        return
    
    data_parts = callback_query.data.replace("ui_edit_lang_", "").split("_")
    category = data_parts[0]
    key = data_parts[1]
    language = data_parts[2]
    
    await admin_ui_control.start_text_editing(callback_query, category, key, language, state)

@router.message(UIControlStates.editing_text)
async def process_text_edit(message: Message, state: FSMContext):
    """Process new text input"""
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        await message.answer("❌ Access denied")
        return
    
    if message.text == "/cancel":
        await state.clear()
        await message.answer("✅ Text editing cancelled")
        return
    
    data = await state.get_data()
    category = data['category']
    key = data['key']
    language = data['language']
    new_text = message.text
    
    # Save new text
    success = await ui_control.set_text(category, key, language, new_text)
    
    if success:
        await message.answer(f"""
✅ <b>Text Updated Successfully!</b>

<b>Category:</b> {category}
<b>Key:</b> {key}
<b>Language:</b> {admin_ui_control.language_names[language]}

<b>New Text:</b>
<code>{new_text}</code>

The changes will take effect immediately across the bot.
        """, parse_mode='HTML')
    else:
        await message.answer("❌ Failed to save text. Please try again.")
    
    await state.clear()

@router.callback_query(F.data == "ui_stats")
async def ui_stats_handler(callback_query: CallbackQuery):
    """Handle statistics display"""
    user_id = callback_query.from_user.id
    if user_id not in ADMIN_IDS:
        await callback_query.answer("❌ Access denied", show_alert=True)
        return
    
    language = await get_user_language(user_id)
    await admin_ui_control.show_statistics(callback_query, language)

@router.callback_query(F.data == "ui_export")
async def ui_export_handler(callback_query: CallbackQuery):
    """Handle configuration export"""
    user_id = callback_query.from_user.id
    if user_id not in ADMIN_IDS:
        await callback_query.answer("❌ Access denied", show_alert=True)
        return
    
    export_data = await ui_control.export_customizations()
    
    await callback_query.message.edit_text(f"""
<b>📤 Configuration Export</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>Export Data (JSON):</b>
<pre>{export_data}</pre>

<b>Usage:</b>
Copy this JSON data and save it as a backup or use it to import configurations to another bot instance.
    """, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Back to UI Control", callback_data="ui_control_main")]
    ]))

@router.callback_query(F.data.startswith("ui_reset_"))
async def ui_reset_handler(callback_query: CallbackQuery):
    """Handle text reset to default"""
    user_id = callback_query.from_user.id
    if user_id not in ADMIN_IDS:
        await callback_query.answer("❌ Access denied", show_alert=True)
        return
    
    data_parts = callback_query.data.replace("ui_reset_", "").split("_", 1)
    category = data_parts[0]
    key = data_parts[1]
    
    # Reset all languages for this key
    reset_count = 0
    for lang in admin_ui_control.supported_languages:
        if await ui_control.reset_text(category, key, lang):
            reset_count += 1
    
    await callback_query.answer(f"✅ Reset {reset_count} language variations to default")
    
    # Refresh the editor
    language = await get_user_language(user_id)
    await admin_ui_control.show_text_editor(callback_query, category, key, language)