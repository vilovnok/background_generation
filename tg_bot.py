import os
import json
import logging
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
from PIL import Image
import torch
from library.insert_everything import InsertEvetything

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

TELEGRAM_BOT_TOKEN = ""
PROMPT_GENERATOR = 'llama'

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

CHOOSE_LOCATION, CHOOSE_COUNT, UPLOAD_IMAGE = range(3)
executor = ThreadPoolExecutor()

def temp_func(img: Image.Image, results_count: int, progress_callback, generation_location="all"):
    test_img = "test_imgs/handled_chair.webp"
    for i in range(20):
        time.sleep(1)
        progress_callback(i + 1, 20)
    return [Image.open(test_img) for _ in range(results_count)]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [[InlineKeyboardButton(text, callback_data=data)] for text, data in [
        ("Внутри дома", "indoor"),
        ("Вне дома", "outdoor"),
        ("Определить автоматически", "automatic"),
        ("Подойдет любой вариант", "all")
    ]]
    await update.message.reply_text("Выберите аргумент пайплайна:", reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSE_LOCATION

async def choose_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["location"] = query.data
    await query.edit_message_text(f"Вы выбрали: {query.data}. Сколько картинок вы хотите увидеть? (Максимум 20)")
    return CHOOSE_COUNT

async def choose_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        count = int(update.message.text)
        if count > 20:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Введите число от 1 до 20.")
        return CHOOSE_COUNT
    context.user_data["count"] = count
    await update.message.reply_text("Загрузите картинку:")
    return UPLOAD_IMAGE

async def upload_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    photo = update.message.photo[-1]
    photo_file = await photo.get_file()
    await photo_file.download_to_drive("temp_image.jpg")
    img = Image.open("temp_image.jpg")
    results_count = context.user_data["count"]
    location = context.user_data["location"]
    msg = "Начинаю обработку. Ваша обработка в очереди, среднее время обработки около 1.5 минут."
    progress_msg = await update.message.reply_text(msg)

    def progress_callback(progress, total):
        asyncio.run_coroutine_threadsafe(progress_msg.edit_text(f"Прогресс: {progress}/{total}"), context.application.loop)

    loop = asyncio.get_event_loop()
    result_images = await loop.run_in_executor(executor, PIPELINE, img, results_count, progress_callback, location)

    for i, result in enumerate(result_images):
        path = f"result_{i}.jpg"
        result.save(path)
        await update.message.reply_photo(photo=open(path, 'rb'))
        os.remove(path)

    torch.cuda.empty_cache()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Отменено. Вы можете начать заново, отправив /start.")
    return ConversationHandler.END

def build_pipeline():
    with open('data.json') as f:
        data = json.load(f)
    return InsertEvetything(data, prompt_generator=PROMPT_GENERATOR)

PIPELINE = build_pipeline()

def main():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE_LOCATION: [CallbackQueryHandler(choose_location)],
            CHOOSE_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_count)],
            UPLOAD_IMAGE: [MessageHandler(filters.PHOTO, upload_image)],
        },
        fallbacks=[CallbackQueryHandler(cancel, pattern='cancel')],
    )
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()