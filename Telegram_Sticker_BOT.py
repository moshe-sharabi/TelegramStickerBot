import random
import sys
import logging
import telegram

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

TEMP_PHOTO = 'temp'

if len(sys.argv) > 1:
    token = sys.argv[1]

# TODO assign your token
# token = 'YOUR TELEGRAM TOKEN HERE'

updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def start(update, context):
    # update.message.reply_sticker(open('8.jpg', 'rb'))
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="אהלן אני הבוט שלך שיהפוך כל תמונה לסטיקר מגניב! 🤖"
                                  "\nשלח/י תמונה ואחזיר לך סטיקר!"
                                  "\nתוכל/י להוסיף טקסט בתאור התמונה שיופיע על הסטיקר")


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


def reply_sticker(update: telegram.update, context):
    m: telegram.Message = update.message
    p: telegram.PhotoSize = m.photo[-1]
    f: telegram.File = p.get_file()
    f.download(custom_path=TEMP_PHOTO)
    text = m.caption
    print(text)
    crop_image_circle(text)
    m.reply_sticker(open(TEMP_PHOTO + '.png', 'rb'))
    m.reply_text(random.choice(
        ['בכיף! תשלח/י עוד  👩🏻‍🚀', 'לשירותך תמיד  💂‍♂️', '🤩   I LIKE IT   🤩', 'Cooooooool 🙀',
         'מה שצריך, אני כאן  👨🏼‍💻']))


def crop_center(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))


def crop_image_circle(text):
    # Open the input image as numpy array, convert to RGB
    img = Image.open(TEMP_PHOTO).convert("RGB")
    h, w = img.size
    m = min(h, w)
    img = crop_center(img, m, m)

    npImage = np.array(img)

    # Create same size alpha layer with circle
    alpha = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(alpha)

    draw.pieslice([0, 0, m, m], 0, 360, fill=255)

    # Convert alpha Image to numpy array
    npAlpha = np.array(alpha)

    # Add alpha layer to RGB
    npImage = np.dstack((npImage, npAlpha))

    # Save with alpha
    i = Image.fromarray(npImage).resize((225, 225))
    d = ImageDraw.Draw(i)
    if text is not None:
        size = 35
        font = ImageFont.truetype("ariblk.ttf", size=size)
        length = d.textsize(text, font=font)[0]
        while length > 210 and size > 1:
            size -= 1
            font = ImageFont.truetype("ariblk.ttf", size=size)
            length = d.textsize(text, font=font)[0]
        if not text.isascii():
            text = "".join(reversed(list(text)))

        d.multiline_text((225 / 2 - length / 2, 160), text, font=font, align='center', stroke_width=6,
                         stroke_fill=(1, 1, 1))
    i.save(TEMP_PHOTO + '.png')


photo_handler = MessageHandler(Filters.photo, reply_sticker)
dispatcher.add_handler(photo_handler)


def caps(update, context):
    text_caps = ' '.join(context.args).upper()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="לא יודע מה שלחת לי עכשיו. אני יודע להתעסק רק עם תמונות")


unknown_handler = MessageHandler(Filters.all, unknown)
dispatcher.add_handler(unknown_handler)

pic_handler = MessageHandler(Filters.photo, reply_sticker)

updater.start_polling()
