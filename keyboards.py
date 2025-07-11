from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_rating_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="👍", callback_data="rating_1"),
            InlineKeyboardButton(text="🤷", callback_data="rating_0"),
            InlineKeyboardButton(text="👎", callback_data="rating_-1"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_admin_keyboard(review_id: int):
    buttons = [
        [
            InlineKeyboardButton(text="✅ Approve", callback_data=f"approve_{review_id}"),
            InlineKeyboardButton(text="❌ Reject", callback_data=f"reject_{review_id}"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)