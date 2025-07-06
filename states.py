"""
FSM States for I3lani Telegram Bot
"""
from aiogram.fsm.state import State, StatesGroup


class AdCreationStates(StatesGroup):
    """States for ad creation flow"""
    language_selection = State()
    ad_content = State()
    channel_selection = State()
    duration_selection = State()
    payment_method = State()
    payment_confirmation = State()


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