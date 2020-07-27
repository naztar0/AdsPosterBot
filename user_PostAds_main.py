#!/usr/bin/env python
import constants as c

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage


bot = Bot(c.token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


main_text = "Благодарим что обратились к нам 🤗\n" \
            "Наш [канал](https://t.me/QSalon_Kiev) очень эффективен, а цены невысокие 👌\n" \
            "Все обьявления проверяются модератором 😎\n\n" \
            "*Выберете категорию вашего обьявления:*\n" \
            "1. Бьюти или фото услуги.\n" \
            "2. Диетологи, Спорт, Врачи, Курсы\n" \
            "3. Вакансии, сдача в салоне рабочих мест, реклама своего канала, другое."

sub_main_text = "*Выберете максимальную цену ваших услуг (оплата за материалы тоже включается):*\n" \
                "1. Модель ничего не платит.\n" \
                "2. Модель оплачивает сумму до 249 грн.\n" \
                "3. Модель оплачивает сумму от 250 грн."

comm_text = "Возможно у вас есть дополнительные пожелания? 🤔\n" \
            "Напишите их сюда или нажмите\n«Далее ➡»\n\n" \
            "Связь с администратором: @katrin_model"

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
    when = State()
    where = State()
    text = State()
    media = State()
    comment = State()
    confirm = State()


async def make_post(message, data):
    key = types.InlineKeyboardMarkup()

    first_name = str(message.from_user.first_name).replace('_', '\\_').replace('*', '\\*').replace('`', '\\`').replace('[', '\\[')
    username = str(message.from_user.username).replace('_', '\\_').replace('*', '\\*').replace('`', '\\`').replace('[', '\\[')
    comm = str(data['comm']).replace('_', '\\_').replace('*', '\\*').replace('`', '\\`').replace('[', '\\[')
    await bot.send_photo(c.admin, data['pay_photo'],
                         f"Оплата: [{first_name}](tg://user?id={message.from_user.id})\n"
                         f"@{username}\n\nКомментарий: {comm}", parse_mode=types.ParseMode.MARKDOWN)
    text = f"{data['text']}\n\n🗓 Когда\n{data['when']}\n\n📍 Где?\n{data['where']}"
    if data['photo']:
        if len(data['photo']) == 1:
            key.add(types.InlineKeyboardButton("Опубликовать", callback_data="post"))
            await bot.send_photo(c.admin, data['photo'][0], caption=text, reply_markup=key)
        else:
            key.add(types.InlineKeyboardButton("Опубликовать", callback_data="post_group"))
            photos = [types.InputMediaPhoto(data['photo'][0], caption=text)] \
                + [types.InputMediaPhoto(x) for x in data['photo'][1:]]
            m = await bot.send_media_group(c.admin, photos)
            await bot.send_message(c.admin, f'{text}\n\n{{"photo_group": {[x.photo[-1].file_id for x in m]}}}', reply_markup=key)
    elif data['video']:
        key.add(types.InlineKeyboardButton("Опубликовать", callback_data="post"))
        await bot.send_video(c.admin, data['video'], caption=text, reply_markup=key)


async def confirm_post(message, data):
    text = f"{data['text']}\n\n🗓 Когда\n{data['when']}\n\n📍 Где?\n{data['where']}"
    if data['photo']:
        if len(data['photo']) == 1:
            await bot.send_photo(message.chat.id, data['photo'][0], caption=text)
        else:
            photos = [types.InputMediaPhoto(data['photo'][0], caption=text)] \
                + [types.InputMediaPhoto(x) for x in data['photo'][1:]]
            await bot.send_media_group(message.chat.id, photos)
    elif data['video']:
        await bot.send_video(message.chat.id, data['video'], caption=text)


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
        await Form.when.set()
        key = types.ReplyKeyboardMarkup(resize_keyboard=True)
        key.add(back_button)
        await message.answer("Отменено, начнём ввод данных сначала...", reply_markup=key)
        await message.answer("Когда будет ваша услуга?")
        return True
    return False


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
    await main_inline_keys(message)


@dp.message_handler(commands=['start'], state=Form.pay_photo)
async def message_handler(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Отменено", reply_markup=main_key())
    await main_inline_keys(message)


@dp.message_handler(commands=['reset'], state=Form)
async def message_handler(message: types.Message, state: FSMContext):
    if message.chat.id == c.admin:
        await state.finish()
        await message.answer("Полный сброс", reply_markup=main_key())
        await main_inline_keys(message)
    else:
        await message.answer("Не доступно")


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

    async with state.proxy() as data:
        data['pay_photo'] = message.photo[-1].file_id
    await Form.next()
    await message.answer("Теперь помогите нам создать и выложить обьявление которое приведет вам клиентов 👌")
    await message.answer("Когда будет ваша услуга?")


@dp.message_handler(content_types=['text'], state=Form.when)
async def photo_handler(message: types.Message, state: FSMContext):
    if await back_function(message, state):
        return

    async with state.proxy() as data:
        data['when'] = message.text
    await Form.next()
    await message.answer("Где будет ваша услуга?")


@dp.message_handler(content_types=['text'], state=Form.where)
async def photo_handler(message: types.Message, state: FSMContext):
    if await back_function(message, state):
        return

    async with state.proxy() as data:
        data['where'] = message.text
    await Form.next()
    await message.answer("Основной текст обьявления, немного о себе и не забудьте указать ваши контакты:")


@dp.message_handler(content_types=['text'], state=Form.text)
async def photo_handler(message: types.Message, state: FSMContext):
    if await back_function(message, state):
        return

    async with state.proxy() as data:
        data['text'] = message.text
    await Form.next()
    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key.add(next_button)
    key.add(back_button)
    await message.answer("Загрузите медиа файлы к вашей публикации (не больше 3 фото или 1 видео)", reply_markup=key)


@dp.message_handler(content_types=types.ContentType.ANY, state=Form.media)
async def media_handler(message: types.Message, state: FSMContext):
    if await back_function(message, state):
        return

    if message.text == next_button:
        async with state.proxy() as data:
            data['video'] = None
            try:
                if not data['photo']:
                    raise KeyError
            except KeyError:
                await message.answer("Медиа файл обязателен!")
                return
        await Form.next()
        await message.answer(comm_text)

    elif message.photo:
        async with state.proxy() as data:
            data['video'] = None
            try:
                if data['photo'] is None:
                    raise KeyError
                if len(data['photo']) != 3:
                    data['photo'].append(message.photo[-1].file_id)
                else:
                    await message.answer("Не больше 3-х фото!")
            except KeyError:
                data['photo'] = [message.photo[-1].file_id]

    elif message.video:
        async with state.proxy() as data:
            try:
                if data['photo'] is None:
                    raise KeyError
                await message.answer("Только фото или видео, вы уже добавили фото!")
                return
            except KeyError:
                data['video'] = message.video.file_id
                data['photo'] = None
        await Form.next()
        await message.answer(comm_text)

    else:
        if message.document:
            await message.reply("Отправьте изображение как фотографию, а не как файл!")
        else:
            await message.reply("Это не фото или видео!")


@dp.message_handler(content_types=['text'], state=Form.comment)
async def message_handler(message: types.Message, state: FSMContext):
    if await back_function(message, state):
        return

    comm = "-"
    if message.text == next_button:
        await message.answer("Комментарии пропущены")
    else:
        comm = message.text
    async with state.proxy() as data:
        data['comm'] = comm
    await confirm_post(message, data)
    await Form.next()
    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key.add(complete_button)
    key.add(back_button)
    await message.answer("Предварительный просмотр публикации")
    await message.answer("ДЛЯ ПУБЛИКАЦИИ НАЖМИТЕ «✅ ЗАКОНЧИТЬ»", reply_markup=key)


@dp.message_handler(content_types=['text'], state=Form.confirm)
async def message_handler(message: types.Message, state: FSMContext):
    if await back_function(message, state):
        return

    elif message.text == complete_button:
        async with state.proxy() as data:
            pass
        await state.finish()
        await message.answer(bye_text, reply_markup=main_key())
        await make_post(message, data)


@dp.callback_query_handler(lambda callback_query: True)
async def callback_inline(callback_query: types.CallbackQuery):
    text_data = callback_query.data
    if text_data == "post":
        text = callback_query.message.caption
        photo = callback_query.message.photo
        video = callback_query.message.video
        if photo:
            await bot.send_photo(c.group, photo[-1].file_id, caption=text)
        elif video:
            await bot.send_video(c.group, video.file_id, caption=text)
        await callback_query.message.answer("Опубликовано!")
    elif text_data == "post_group":
        data = str(callback_query.message.text)
        i = data.find('{"photo_group":')
        text = data[:i]
        photo_data = eval(data[i:])['photo_group']
        photos = [types.InputMediaPhoto(photo_data[0], caption=text)] \
            + [types.InputMediaPhoto(x) for x in photo_data[1:]]
        await bot.send_media_group(c.group, photos)
        await callback_query.message.answer("Опубликовано!")
    else:
        if text_data == "item_1":
            key = types.InlineKeyboardMarkup()
            but_1 = types.InlineKeyboardButton("1", callback_data="sub_item_1")
            but_2 = types.InlineKeyboardButton("2", callback_data="sub_item_2")
            but_3 = types.InlineKeyboardButton("3", callback_data="sub_item_3")
            key.add(but_1, but_2, but_3)
            await callback_query.message.answer(sub_main_text, parse_mode=types.ParseMode.MARKDOWN, reply_markup=key)
        elif text_data == "sub_item_1":
            await choose_service(callback_query.message, "символические 20 грн 💁‍♂", 20)
        elif text_data == "sub_item_2":
            await choose_service(callback_query.message, "всего 40 грн 🌺", 40)
        elif text_data == "sub_item_3":
            await choose_service(callback_query.message, "всего 80 грн 🌺", 80)
        elif text_data == "item_2":
            await choose_service(callback_query.message, "всего 150 грн 🌺", 150)
        elif text_data == "item_3":
            await choose_service(callback_query.message, "300 грн. Мы вам гарантируем до 2000 просмотров за пару дней 🥳", 300)
        await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
