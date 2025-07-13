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
    
    # Streamlined flow states
    upload_content = State()
    select_channels = State()
    calculate_pricing = State()
    
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
    payment_selection = State()
    payment_processing = State()
    error_state = State()
    confirmation_pending = State()
    custom_duration = State()
    waiting_wallet_address = State()


class CreateAd(StatesGroup):
    """Simplified ad creation states"""
    content_upload = State()
    channel_selection = State()
    duration_selection = State()
    payment_method = State()
    ton_payment = State()
    stars_payment = State()
    payment_confirmation = State()
    waiting_payment_confirmation = State()


class WalletStates(StatesGroup):
    """States for TON wallet address management"""
    # TON payment wallet collection
    payment_wallet_input = State()
    
    # Affiliate program wallet collection
    affiliate_wallet_input = State()
    
    # Channel addition wallet collection
    channel_wallet_input = State()
    
    # General wallet management
    wallet_update = State()
    wallet_verification = State()


class UserStates(StatesGroup):
    """General user states"""
    main_menu = State()
    settings = State()
    help = State()
    reporting_error = State()


class AdminStates(StatesGroup):
    """Admin panel states"""
    main_menu = State()
    channel_management = State()
    pricing_management = State()
    user_analytics = State()
    content_management = State()
    bulk_import_channels = State()
    add_channel = State()
    statistics = State()
    user_management = State()
    set_pricing = State()
    edit_channel = State()
    remove_channel = State()
    subscription_management = State()
    create_subscription = State()
    edit_subscription = State()
    remove_subscription = State()
    publishing_schedules = State()
    create_schedule = State()
    edit_schedule = State()
    bot_control = State()
    broadcast_message = State()
    usage_agreement = State()
    edit_agreement = State()