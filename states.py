"""
FSM States for I3lani Telegram Bot
"""
from aiogram.fsm.state import State, StatesGroup


class AdCreationStates(StatesGroup):
    """States for enhanced ad creation flow"""
    # Enhanced flow steps
    select_category = State()
    select_subcategory = State()
    select_location = State()
    enter_ad_details = State()
    upload_photos = State()
    provide_contact_info = State()
    preview_ad = State()
    confirm_or_edit = State()
    
    # Legacy states (kept for compatibility)
    language_selection = State()
    ad_content = State()
    channel_selection = State()
    duration_selection = State()
    payment_method = State()
    payment_confirmation = State()
    
    # Additional states
    waiting_for_content = State()
    waiting_for_channels = State()
    waiting_for_duration = State()
    waiting_for_payment = State()


class UserStates(StatesGroup):
    """General user states"""
    main_menu = State()
    settings = State()
    help = State()


class AdminStates(StatesGroup):
    """Admin panel states"""
    main_menu = State()
    channel_management = State()
    pricing_management = State()
    user_analytics = State()
    content_management = State()