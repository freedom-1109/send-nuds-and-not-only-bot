import logging
from APIs import TG_API, google_API
from aiogram import Dispatcher, Bot, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Text
from serpapi import GoogleSearch

""" логирование сообщений, не понял как пользоваться))) """
logging.basicConfig(level=logging.INFO)

"""Initialize bot and dispatcher"""
bot = Bot(token=TG_API)
dp = Dispatcher(bot)

""" создание клавиатур """
start_kb = InlineKeyboardMarkup(row_width=1)
start_kb.add(InlineKeyboardButton(text="Показать картинку", callback_data='showPicture'))

back_to_menu_kb = InlineKeyboardMarkup(row_width=2)
back_to_menu_kb.row(InlineKeyboardButton(text="Назад в меню", callback_data='backToMenu'),
                    InlineKeyboardButton(text="Хочу еще!", callback_data='giveMore'))

back_to_menu_kb_short = InlineKeyboardMarkup(row_width=1)
back_to_menu_kb_short.add(InlineKeyboardButton(text="Назад в меню", callback_data='backToMenu'))
""" конец создания клавиатур """

""" переменные отвечающие за включение функций"""
text_of_picture_catcher = False
data, picID = None, 0


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(f"Привет, Вы можете посмотреть картинку по запросу:", reply_markup=start_kb)


@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    await message.answer(
        f"Для работы бота нужно всего лишь нажимать на кнопку, такую как чуть ниже, и выполнить указания из появившегося сообщения",
        reply_markup=back_to_menu_kb)


@dp.message_handler(commands=['author'])
async def author(message: types.Message):
    await message.answer(f"Я Николай Набоков @nnabokov, разработчик данного бота", reply_markup=back_to_menu_kb)


@dp.callback_query_handler(Text('showPicture'))
async def message_catcher_activator(callback: types.CallbackQuery):
    global text_of_picture_catcher
    text_of_picture_catcher = True
    await bot.send_message(chat_id=callback.message.chat.id, text='введите текст для поиска картинки:', reply_markup=back_to_menu_kb_short)
    await callback.answer()


@dp.message_handler()
async def message_catcher(message: types.Message):
    global text_of_picture_catcher
    if text_of_picture_catcher:
        text_of_picture_catcher = False
        request = str(message.text)
        params = {
            "q": request,
            "tbm": "isch",
            "ijn": "0",
            "api_key": google_API,
            "safe": "off"
        }

        search = GoogleSearch(params)

        global data, picID
        data = search.get_json()["images_results"]
        picID = 0
        try:
            await bot.send_photo(chat_id=message.chat.id, photo=data[picID]["original"],
                                 reply_markup=back_to_menu_kb)
        except:
            await bot.send_message(chat_id=message.chat.id, text='оригинал этой картинки не получилось достать :(')
            await bot.send_photo(chat_id=message.chat.id, photo=data[picID]["thumbnail"],
                                 reply_markup=back_to_menu_kb)


@dp.callback_query_handler(Text('giveMore'))
async def morePicSendler(callback: types.CallbackQuery):
    global data, picID
    picID += 1
    if picID < len(data):
        try:
            await bot.send_photo(chat_id=callback.message.chat.id, photo=data[picID]["original"],
                                 reply_markup=back_to_menu_kb)
        except:
            await bot.send_message(chat_id=callback.message.chat.id, text='оригинал этой картинки не получилось достать :(')
            await bot.send_photo(chat_id=callback.message.chat.id, photo=data[picID]["thumbnail"],
                                 reply_markup=back_to_menu_kb)
    else:
        await bot.send_message(chat_id=callback.message.chat.id, text='картинки закончились((:',
                               reply_markup=back_to_menu_kb_short)
    await callback.answer()


""" возвращает в главное меню """


@dp.callback_query_handler(Text('backToMenu'))
async def backToMenu(callback: types.CallbackQuery):
    global text_of_picture_catcher
    text_of_picture_catcher = False
    await bot.send_message(
        chat_id=callback.message.chat.id,
        text=f"Рад снова Вас видеть\nВы можете посмотреть картинку по запросу: ",
        reply_markup=start_kb
    )
    await callback.answer()


if __name__ == '__main__':
    """ запуск бота """
    executor.start_polling(dp, skip_updates=True)
