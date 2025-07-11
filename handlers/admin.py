from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from config import config
from keyboards import get_admin_keyboard
from services.storage import storage
from services.github_integration import commit_review

router = Router()


@router.message(Command("admin"))
async def admin_handler(message: Message):
    if message.from_user.id in config.admin_ids:
        await message.answer("Добро пожаловать в админ-панель!")
    else:
        await message.answer("У вас нет прав для использования этой команды.")


@router.message(Command("moderate"))
async def moderate_handler(message: Message):
    if message.from_user.id not in config.admin_ids:
        await message.answer("У вас нет прав для использования этой команды.")
        return

    review = storage.get_pending_review()
    if review:
        review_id, company_name, rating, review_text, username = review
        text = (
            f"Новый отзыв о {company_name} от {username}:\n"
            f"Рейтинг: {rating}\n"
            f"Отзыв: {review_text}"
        )
        await message.answer(text, reply_markup=get_admin_keyboard(review_id))
    else:
        await message.answer("Нет отзывов для модерации.")


@router.callback_query(F.data.startswith("approve_"))
async def approve_handler(callback_query: CallbackQuery):
    if callback_query.from_user.id not in config.admin_ids:
        await callback_query.answer("У вас нет прав для использования этой команды.")
        return

    review_id = int(callback_query.data.split("_")[1])
    review_data = storage.get_review_by_id(review_id)
    storage.approve_review(review_id)
    commit_review(review_data)
    await callback_query.message.edit_text("Отзыв одобрен и отправлен в GitHub.")
    await callback_query.answer()


@router.callback_query(F.data.startswith("reject_"))
async def reject_handler(callback_query: CallbackQuery):
    if callback_query.from_user.id not in config.admin_ids:
        await callback_query.answer("У вас нет прав для использования этой команды.")
        return

    review_id = int(callback_query.data.split("_")[1])
    storage.reject_review(review_id)
    await callback_query.message.edit_text("Отзыв отклонен.")
    await callback_query.answer()