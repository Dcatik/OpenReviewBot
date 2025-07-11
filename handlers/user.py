from aiogram import F, Router, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from keyboards import get_rating_keyboard, get_admin_keyboard
from services.storage import storage
from services.ai_moderation import check_review
from config import config

router = Router()


class AddReview(StatesGroup):
    waiting_for_company_name = State()
    waiting_for_rating = State()
    waiting_for_review_text = State()


@router.message(Command("start"))
async def start_handler(message: Message):
    storage.add_user(message.from_user.id, message.from_user.username)
    await message.answer(
        "Добро пожаловать в бота для отзывов о работодателях!\n"
        "Вот доступные команды:\n"
        "/help - показать это сообщение\n"
        "/companies - показать список компаний\n"
        "/reviews &lt;company&gt; - показать отзывы о компании\n"
        "/add_review - добавить новый отзыв"
    )


@router.message(Command("help"))
async def help_handler(message: Message):
    await message.answer(
        "Вот доступные команды:\n"
        "/help - показать это сообщение\n"
        "/companies - показать список компаний\n"
        "/reviews &lt;company&gt; - показать отзывы о компании\n"
        "/add_review - добавить новый отзыв"
    )


@router.message(Command("companies"))
async def companies_handler(message: Message):
    recommendations = storage.get_company_recommendations()
    if recommendations:
        text = "Список компаний с рекомендациями:\n"
        for company_name, avg_rating in recommendations:
            if avg_rating > 0.5:
                recommendation = "👍"
            elif avg_rating < -0.5:
                recommendation = "👎"
            else:
                recommendation = "🤷"
            text += f"- {company_name}: {recommendation}\n"
    else:
        text = "Нет компаний с отзывами."
    await message.answer(text)


@router.message(Command("reviews"))
async def reviews_handler(message: Message):
    try:
        company_name = message.text.split(maxsplit=1)[1]
        reviews = storage.get_reviews_by_company_name(company_name)
        if reviews:
            text = f"Отзывы о {company_name}:\n" + "\n\n".join(
               f"Рейтинг: {review[3]}\nОтзыв: {review[4]}" for review in reviews
           )
        else:
            text = f"Отзывы о {company_name} не найдены."
        await message.answer(text)
    except IndexError:
        await message.answer("Пожалуйста, укажите название компании, например, /reviews &lt;company&gt;")


@router.message(Command("add_review"))
async def add_review_handler(message: Message, state: FSMContext):
    await state.set_state(AddReview.waiting_for_company_name)
    await message.answer("Пожалуйста, введите название компании:")


@router.message(StateFilter(AddReview.waiting_for_company_name))
async def company_name_handler(message: Message, state: FSMContext):
    await state.update_data(company_name=message.text)
    await state.set_state(AddReview.waiting_for_rating)
    await message.answer("Пожалуйста, оцените компанию:", reply_markup=get_rating_keyboard())


@router.callback_query(StateFilter(AddReview.waiting_for_rating), F.data.startswith("rating_"))
async def rating_handler(callback_query: CallbackQuery, state: FSMContext):
    await state.update_data(rating=int(callback_query.data.split("_")[1]))
    await state.set_state(AddReview.waiting_for_review_text)
    await callback_query.message.answer("Пожалуйста, введите ваш отзыв:")
    await callback_query.answer()


@router.message(StateFilter(AddReview.waiting_for_review_text))
async def review_text_handler(message: Message, state: FSMContext, bot: Bot):
    moderation_result = await check_review(message.text)
    if not moderation_result["allowed"]:
        await message.answer(
            f"Ваш отзыв не был принят по причине: {moderation_result['reason']}"
        )
        await state.clear()
        return

    data = await state.get_data()
    company_name = data["company_name"]
    rating = data["rating"]
    review_text = message.text

    company_id = storage.get_or_create_company(company_name)
    review_id = storage.add_review(
        company_id, message.from_user.id, rating, review_text
    )

    await state.clear()
    await message.answer("Спасибо! Ваш отзыв был отправлен на модерацию.")

    for admin_id in config.admin_ids:
        text = (
            f"Новый отзыв о {company_name} от {message.from_user.username}:\n"
            f"Рейтинг: {rating}\n"
            f"Отзыв: {review_text}"
        )
        await bot.send_message(
            admin_id, text, reply_markup=get_admin_keyboard(review_id)
        )