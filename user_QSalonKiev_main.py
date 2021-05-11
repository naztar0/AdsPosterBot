#!/usr/bin/env python
import constants as c

from aiogram import Bot, Dispatcher, executor, types, utils
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from asyncio import get_event_loop, sleep
from datetime import datetime
import pickle
import json

bot = Bot(c.token1)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


main_text = "Благодарим что обратились к нам 🤗\n" \
            "Наш [канал](https://t.me/QSalon_Kiev) очень эффективен 👍😊\n" \
            "Все обьявления проверяются модератором 😎\n\n" \
            "ОЗНАКОМТЕСЬ С ВИДЕО ИНСТРУКЦИЕЙ 2 мин 💁‍♂\nhttps://bit.ly/2DR3Auk\n\n" \
            "👉 *Выберете категорию вашего обьявления:*\n" \
            "1. Бьюти или фото услуги.\n" \
            "2. Диетологи, Спорт, Врачи, Курсы\n" \
            "3. Вакансии, сдача в салоне рабочих мест, реклама своего канала, другое."

sub_main_text = "*Выберете максимальную цену ваших услуг (оплата за материалы тоже включается):*\n" \
                "1. Модель ничего не платит.\n" \
                "2. Модель оплачивает сумму до 249 грн.\n" \
                "3. Модель оплачивает сумму от 250 грн."

comm_text = "Есть пожелание на какое время публикация? 🤔\n" \
            "Если нет то нажмите «Далее ➡»\n\n" \
            "Связь с администратором: @rivikate"

ad_text_text = "Напишите Ваше обьявление 🤗\n\n🖐🖐🖐 *ВАЖНО!!!* 🖐🖐🖐\n" \
               "*ЧТО ДОЛЖНО БЫТЬ В ОБЯЛЕНИИ:*\n\n" \
               "⚘ Немного о себе (салоне/организации)\n" \
               "⚘ Когда будет услуга?\n" \
               "⚘ Где будет ваша услуга?\n" \
               "⚘ Стоимость вашей услуги\n" \
               "🖐 Ваши контакты (кликабельные)\n" \
               "🖐 Ссылка на ваш телеграмм обязательна!"

media_text = "👉 Загрузите медиа файлы к вашей публикации (не больше 3 фото или 1 видео)\n\n" \
             "После загрузки всех медиафайлов нажмите «Далее ➡».\n\n" \
             "Если кнопка «Далее ➡» не видна нажмите\n🖐 СЛЕВА ОТ МИКРОФОНА КВАДРАТИК 🖐\nи она появится 💁‍♂😊"

low_motivation_text = "Добрый день 🤗 Вы уже 2 недели не публиковали свое обьявление на нашем канале «ищу модель» 😱😊\n\n" \
                      "Наша аудитория постоянно растет и много новых клиентов хотят увидеть именно вашу публикацию 🤔😉\n\n" \
                      "Попробуйте еще 😌"

post_cost_text = "Цена вашей публикации {}"
requisites_text = "*Реквизиты для оплаты:*\nПриватБанк `5221 1911 0065 3194` _Панченко А. О._ \n\nПосле оплаты загрузите, пожалуйста, скрин/фото вашей оплаты."
pay_url_button = "https://www.privat24.ua/rd/transfer_to_card/?hash=rd%2Ftransfer_to_card%2F%7B%22from%22%3A%22%22%2C%22to%22%3A%22{card}%22%2C%22amt%22%3A%22{cost}%22%2C%22ccy%22%3A%22UAH%22%7D"
bye_text = "Готово 🥳\nПосле проверки ваше объявление будет выложено 🌼\nЖелаем вам как можно больше клиентов, а мы вам в этом поможем 😉\nОбращайтесь к нам еще 🤗"
back_button = "⬅ Назад"
next_button = "Далее ➡"
complete_button = "✅ Закончить"
main_button = "🌼 Создать публикацию"


class Form(StatesGroup):
    pay_photo = State()
    media = State()
    text = State()
    comment = State()
    confirm = State()


async def send_message(func, **kwargs):
    try:
        return await func(**kwargs)
    except utils.exceptions.BotBlocked: return
    except utils.exceptions.UserDeactivated: return
    except utils.exceptions.ChatNotFound: return
    except utils.exceptions.BadRequest: return


async def make_post(message, data):
    key = types.InlineKeyboardMarkup()

    first_name = str(message.from_user.first_name).replace('_', '\\_').replace('*', '\\*').replace('`', '\\`').replace('[', '\\[')
    username = str(message.from_user.username).replace('_', '\\_').replace('*', '\\*').replace('`', '\\`').replace('[', '\\[')
    comm = str(data['comm']).replace('_', '\\_').replace('*', '\\*').replace('`', '\\`').replace('[', '\\[')
    for admin in c.admins1:
        await send_message(bot.send_photo, chat_id=admin, photo=data['pay_photo'],
                           caption=f"Оплата: [{first_name}](tg://user?id={message.from_user.id})\n"
                           f"@{username}\n\nКомментарий: {comm}", parse_mode=types.ParseMode.MARKDOWN)
        if data['photo']:
            if len(data['photo']) == 1:
                key.add(types.InlineKeyboardButton("Опубликовать", callback_data="post"))
                await send_message(bot.send_photo, chat_id=admin, photo=data['photo'][0], caption=data['text'], reply_markup=key)
            else:
                key.add(types.InlineKeyboardButton("Опубликовать", callback_data="post_group"))
                photos = [types.InputMediaPhoto(data['photo'][0], caption=data['text'])] \
                    + [types.InputMediaPhoto(x) for x in data['photo'][1:]]
                m = await send_message(bot.send_media_group, chat_id=admin, media=photos)
                photo_group = json.dumps({"photo_group": [x.photo[-1].file_id for x in m]})
                await send_message(bot.send_message, chat_id=admin, text=f"{data['text']}\n\n{photo_group}", reply_markup=key)
        elif data['video']:
            key.add(types.InlineKeyboardButton("Опубликовать", callback_data="post"))
            await send_message(bot.send_video, chat_id=admin, video=data['video'], caption=data['text'], reply_markup=key)


async def confirm_post(message, data):
    if data['photo']:
        if len(data['photo']) == 1:
            await bot.send_photo(message.chat.id, data['photo'][0], caption=data['text'])
        else:
            photos = [types.InputMediaPhoto(data['photo'][0], caption=data['text'])] \
                + [types.InputMediaPhoto(x) for x in data['photo'][1:]]
            await bot.send_media_group(message.chat.id, photos)
    elif data['video']:
        await bot.send_video(message.chat.id, data['video'], caption=data['text'])


async def choose_service(message, cost_text, cost):
    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key.add(back_button)
    pay_key = types.InlineKeyboardMarkup()
    pay_key.add(types.InlineKeyboardButton("Приват24", url=pay_url_button.format(card='5221191100653194', cost=cost)))
    await message.answer(post_cost_text.format(cost_text), reply_markup=key)
    await message.answer(requisites_text, reply_markup=pay_key, parse_mode=types.ParseMode.MARKDOWN)
    await Form.pay_photo.set()


async def back_function(message, state):
    if message.text in (back_button, '/start'):
        await state.update_data({'photo': None})
        await Form.media.set()
        key = types.ReplyKeyboardMarkup(resize_keyboard=True)
        key.add(next_button)
        key.add(back_button)
        await message.answer("Отменено, начнём ввод данных сначала...", reply_markup=key)
        await message.answer(media_text)
        return True


def main_key():
    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key.add(main_button)
    return key


async def main_inline_keys(message):
    key = types.InlineKeyboardMarkup()
    but_1 = types.InlineKeyboardButton("1", callback_data="item_1")
    but_2 = types.InlineKeyboardButton("2", callback_data="item_2")
    but_3 = types.InlineKeyboardButton("3", callback_data="item_3")
    key.add(but_1, but_2, but_3)
    await message.answer(main_text, parse_mode=types.ParseMode.MARKDOWN, reply_markup=key, disable_web_page_preview=True)


@dp.message_handler(commands=['start'])
async def message_handler(message: types.Message):
    await bot.send_video(message.chat.id, c.tutorial_video_id_1)
    await main_inline_keys(message)


@dp.message_handler(commands=['start'], state=Form.pay_photo)
async def message_handler(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Отменено", reply_markup=main_key())
    await main_inline_keys(message)


@dp.message_handler(commands=['reset'], state=Form)
async def message_handler(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Полный сброс", reply_markup=main_key())
    await main_inline_keys(message)


@dp.message_handler(content_types=['text'])
async def message_handler(message: types.Message):
    if message.text == main_button:
        await main_inline_keys(message)
    elif message.text == back_button:
        await message.answer("Отменено", reply_markup=main_key())


@dp.message_handler(content_types=['text', 'photo'], state=Form.pay_photo)
async def photo_handler(message: types.Message, state: FSMContext):
    if not message.photo:
        if message.text == back_button:
            await state.finish()
            await message.answer("Отменено", reply_markup=main_key())
        return

    await state.update_data({'pay_photo': message.photo[-1].file_id})
    await Form.next()
    await message.answer("Теперь помогите нам создать и выложить обьявление которое приведет вам клиентов 👌")
    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key.add(next_button)
    key.add(back_button)
    await message.answer(media_text, reply_markup=key)


@dp.message_handler(content_types=types.ContentType.ANY, state=Form.media)
async def media_handler(message: types.Message, state: FSMContext):
    if await back_function(message, state):
        return

    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key.add(back_button)

    data = await state.get_data()
    if message.text == next_button:
        await state.update_data({'video': None})
        if not data.get('photo'):
            await message.answer("Медиа файл обязателен!")
            return
        await Form.next()
        await message.answer(ad_text_text, parse_mode="Markdown", reply_markup=key)

    elif message.photo:
        await state.update_data({'video': None})
        if data.get('photo'):
            if len(data['photo']) != 3:
                data['photo'].append(message.photo[-1].file_id)
            else:
                data['photo'] = None
                await message.answer("Не больше 3-х фото 🌼")
        else:
            data['photo'] = [message.photo[-1].file_id]
        await state.update_data({'photo': data['photo']})

    elif message.video:
        if data.get('photo'):
            await message.answer("Только фото или видео, вы уже добавили фото!")
            return
        await state.update_data({'video': message.video.file_id, 'photo': None})
        await Form.next()
        await message.answer(ad_text_text, parse_mode="Markdown", reply_markup=key)

    else:
        if message.document:
            await message.reply("Отправьте изображение как фотографию, а не как файл")
        else:
            await message.reply("Это не фото или видео")


@dp.message_handler(content_types=['text'], state=Form.text)
async def text_handler(message: types.Message, state: FSMContext):
    if await back_function(message, state):
        return

    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key.add(next_button)
    key.add(back_button)
    if len(message.text) > 980:
        await message.answer("Текст слишком длинный")
        return
    await state.update_data({'text': message.text})
    await Form.next()

    await message.answer(comm_text, reply_markup=key)


@dp.message_handler(content_types=['text'], state=Form.comment)
async def message_handler(message: types.Message, state: FSMContext):
    if await back_function(message, state):
        return

    comm = "-"
    if message.text == next_button:
        await message.answer("Комментарии пропущены")
    else:
        comm = message.text
    await state.update_data({'comm': comm})
    data = await state.get_data()
    await confirm_post(message, data)
    await Form.next()
    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key.add(complete_button)
    key.add(back_button)
    await message.answer("Предварительный просмотр публикации\n\n"
                         "ДЛЯ ПУБЛИКАЦИИ НАЖМИТЕ «✅ ЗАКОНЧИТЬ»", reply_markup=key)


@dp.message_handler(content_types=['text'], state=Form.confirm)
async def message_handler(message: types.Message, state: FSMContext):
    if await back_function(message, state):
        return

    elif message.text == complete_button:
        data = await state.get_data()
        await state.finish()
        await message.answer(bye_text, reply_markup=main_key())
        await make_post(message, data)
        with open(c.last_activity1, 'rt') as f:
            data = json.load(f)
        data[str(message.chat.id)] = int(datetime.now().timestamp())
        with open(c.last_activity1, 'wt') as f:
            json.dump(data, f)


def pickle_read(file):
    with open(file, 'rb') as f:
        try:
            return pickle.load(f)
        except Exception as e:
            return e


async def publish_to_channel(data):
    if len(data) == 3:
        text, photo, video = data
        if photo:
            await bot.send_photo(c.group1, photo, caption=text)
        elif video:
            await bot.send_video(c.group1, video, caption=text)
    else:
        text, photo_data = data
        photos = [types.InputMediaPhoto(photo_data[0], caption=text)] \
            + [types.InputMediaPhoto(x) for x in photo_data[1:]]
        await bot.send_media_group(c.group1, photos)


async def post_postponed_loop():
    while True:
        if 9 <= datetime.now().hour <= 23:
            last_publish_time: int = pickle_read(c.last_publish_time_1)
            if isinstance(last_publish_time, Exception):
                continue
            now = int(datetime.timestamp(datetime.now()))
            if now - last_publish_time > 1200:  # 1200 - 20 min
                postponed_posts: list = pickle_read(c.postponed_posts_1)
                if isinstance(postponed_posts, Exception):
                    continue
                if postponed_posts:
                    await publish_to_channel(postponed_posts.pop(0))
                    with open(c.last_publish_time_1, 'wb') as f:
                        pickle.dump(now, f)
                    with open(c.postponed_posts_1, 'wb') as f:
                        pickle.dump(postponed_posts, f)
        await sleep(200)  # 200 ~ 3 min


async def postpone_post(data):
    while True:
        postponed_posts: list = pickle_read(c.postponed_posts_1)
        if not isinstance(postponed_posts, Exception):
            break
    postponed_posts.append(data)
    with open(c.postponed_posts_1, 'wb') as f:
        pickle.dump(postponed_posts, f)


async def low_motivation_loop():
    while True:
        if 9 <= datetime.now().hour <= 23:
            now = int(datetime.now().timestamp())
            timer = now - 1209600  # 2 weeks
            with open(c.last_activity1, 'rt') as f:
                data = json.load(f)
            for user in data:
                if data[user] < timer:
                    data[user] = now
                    await send_message(bot.send_message, chat_id=int(user), text=low_motivation_text)
                    await sleep(.05)
            with open(c.last_activity1, 'wt') as f:
                json.dump(data, f)
        await sleep(43200)  # 1/2 day


@dp.callback_query_handler(lambda callback_query: True)
async def callback_inline(callback_query: types.CallbackQuery):
    text_data = callback_query.data
    if text_data == "post":
        try: await bot.edit_message_reply_markup(callback_query.message.chat.id, callback_query.message.message_id)
        except utils.exceptions.MessageNotModified: pass
        text = callback_query.message.caption
        photo = callback_query.message.photo
        video = callback_query.message.video
        if photo: photo = photo[-1].file_id
        if video: video = video.file_id
        await postpone_post((text, photo, video))
    elif text_data == "post_group":
        try: await bot.edit_message_reply_markup(callback_query.message.chat.id, callback_query.message.message_id)
        except utils.exceptions.MessageNotModified: pass
        data = str(callback_query.message.text)
        i = data.find('{"photo_group":')
        text = data[:i]
        photo_data = json.loads(data[i:])['photo_group']
        await postpone_post((text, photo_data))
    else:
        if text_data == "item_1":
            key = types.InlineKeyboardMarkup()
            but_1 = types.InlineKeyboardButton("1", callback_data="sub_item_1")
            but_2 = types.InlineKeyboardButton("2", callback_data="sub_item_2")
            but_3 = types.InlineKeyboardButton("3", callback_data="sub_item_3")
            key.add(but_1, but_2, but_3)
            await callback_query.message.answer(sub_main_text, parse_mode=types.ParseMode.MARKDOWN, reply_markup=key)
        elif text_data == "sub_item_1":
            await choose_service(callback_query.message, "символические 28 грн 💁‍♂", 28)
        elif text_data == "sub_item_2":
            await choose_service(callback_query.message, "всего 48 грн 🌺", 48)
        elif text_data == "sub_item_3":
            await choose_service(callback_query.message, "всего 95 грн 🌺", 95)
        elif text_data == "item_2":
            await choose_service(callback_query.message, "всего 140 грн 🌺", 140)
        elif text_data == "item_3":
            await choose_service(callback_query.message, "237 грн. Мы вам гарантируем до 2000 просмотров за пару дней 🥳", 237)
        try: await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
        except utils.exceptions.MessageCantBeDeleted: pass
        except utils.exceptions.MessageToDeleteNotFound: pass


if __name__ == "__main__":
    loop = get_event_loop()
    loop.create_task(post_postponed_loop())
    loop.create_task(low_motivation_loop())
    executor.start_polling(dp, skip_updates=True)
