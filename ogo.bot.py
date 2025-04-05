# -*- coding: utf-8 -*-
import os
import cv2
import numpy as np
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes
from telegram.ext import filters

async def remove_watermark(image_path, watermark_paths, output_path):
    image = cv2.imread(image_path)

    for watermark_path in watermark_paths:
        watermark = cv2.imread(watermark_path, cv2.IMREAD_GRAYSCALE)
        result = cv2.matchTemplate(image, watermark, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        locations = np.where(result >= threshold)
        
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        for pt in zip(*locations[::-1]):
            cv2.rectangle(mask, pt, (pt[0] + watermark.shape[1], pt[1] + watermark.shape[0]), 255, -1)

        image = cv2.inpaint(image, mask, 3, cv2.INPAINT_TELEA)

    cv2.imwrite(output_path, image)

async def handle_images(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    photos = update.message.photo
    num_photos = len(photos)

    if num_photos < 1 or num_photos > 10:
        await update.message.reply_text("Пожалуйста, отправь от 1 до 10 изображений.")
        return

    temp_dir = f'bot_v1.0/{user_id}_images'
    os.makedirs(temp_dir, exist_ok=True)

    file_paths = []
    for idx, photo in enumerate(photos):
        file = await photo.get_file()
        file_path = f'{temp_dir}/{user_id}_image_{idx}.jpg'
        await file.download_to_drive(file_path)
        file_paths.append(file_path)

    watermark_paths = [
        'bot_v1.0/govno1.jpg',
        'bot_v1.0/govno2.jpg',
    ]

    output_paths = []
    for file_path in file_paths:
        output_path = file_path.replace(".jpg", "_no_watermark.jpg")
        await remove_watermark(file_path, watermark_paths, output_path)
        output_paths.append(output_path)

    for output_path in output_paths:
        with open(output_path, 'rb') as f:
            await update.message.reply_photo(photo=f)

    for file_path in file_paths + output_paths:
        os.remove(file_path)
    os.rmdir(temp_dir)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Привет! Отправь от 1 до 10 изображений, и я удалю с них вотермарки.')

def main():
    TOKEN = '7262519810:AAFuahAZEK9BUmCZRx3GTUgw7f3VKvg64WA'

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_images))

    app.run_polling()

if __name__ == '__main__':
    main()

