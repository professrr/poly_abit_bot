from aiogram import types
from pymongo import MongoClient
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from misc import dp, bot
from . import unreal_engine
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.utils.markdown import text, bold, italic, code, pre

client = MongoClient('mongodb://mongodb11:27017/')

class Position(StatesGroup):
    waiting_for_enter_fio = State()
    waiting_for_approve_priklad = State()
    waiting_for_approve_isit = State()
    waiting_for_approve_insert = State()


async def congrats():
    client = MongoClient('mongodb://mongodb11:27017/')
    for user in unreal_engine.getAllUsers(client):
        print(user['watcher_id'])
        await bot.send_message(user['watcher_id'],'Поздравляем с успешным поступлением!)\n:)')
        await bot.send_photo(user['watcher_id'],'https://cs11.pikabu.ru/post_img/2019/03/08/6/1552037556176615454.jpg')

# bot.send_message(753309208, 'Доступен новый функционал\nНажми сюда /here')    

# @dp.message_handler(state="*")
# async def findhim(message: types.Message, state: FSMContext):
#     if message.from_user.id == 753309208:
#         print(message.from_user.url)
#         print(message.from_user.first_name)
#         print(message.from_user.last_name)

@dp.message_handler(commands=['start'], state="*")
async def cmd_start(message: types.Message, state: FSMContext):
    global client
    user = unreal_engine.getNamesByUser(message.from_user.id, client)
    if user:
        await message.reply("У вас есть сохраненное наблюдение\nЛови доступ к меню\n👉🏼 /menu", reply_markup=types.ReplyKeyboardRemove())
        await Position.waiting_for_enter_fio.set()
        await Position.waiting_for_approve_priklad.set()
        await Position.waiting_for_approve_isit.set()
        await Position.waiting_for_approve_insert.set()
        commands = [types.BotCommand(command="/menu", description="Главное меню")]
        await bot.set_my_commands(commands)       
    else:
        await message.reply("Для продолжения введите ФИО\n(можно с ошибками, напр. некита фодоров)", reply_markup=types.ReplyKeyboardRemove())
        await Position.waiting_for_enter_fio.set()

@dp.message_handler(state=Position.waiting_for_enter_fio, content_types=types.ContentTypes.TEXT)
async def fio(message: types.Message, state: FSMContext):
    global client
    max = unreal_engine.showRelatedNames(message.text, client)
    # print(max["230"]["name"])
    button_name_230 = KeyboardButton(max["230"]["name"])
    format_button = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(button_name_230) 
    # button_name_229 = KeyboardButton(max["229"]["name"])
    await state.update_data(max = max)
    await message.reply("Найдено максимальное совпадение для Прикладной Инфы:", reply_markup=format_button)
    await Position.waiting_for_approve_priklad.set()

@dp.message_handler(state=Position.waiting_for_approve_priklad, content_types=types.ContentTypes.TEXT)
async def approve_fio_1(message: types.Message, state: FSMContext):
    max = await state.get_data()
    button_name_229 = KeyboardButton(max["max"]["229"]["name"])
    format_button = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(button_name_229) 
    await message.reply("Так теперь для ИСиТа найдено вот это:", reply_markup=format_button)
    await Position.waiting_for_approve_isit.set()

@dp.message_handler(state=Position.waiting_for_approve_isit, content_types=types.ContentTypes.TEXT)
async def approve_fio_2(message: types.Message, state: FSMContext):
    global client
    max = await state.get_data()
    await message.reply(unreal_engine.initialInsertUser(message.from_user, max, client))
    await Position.waiting_for_approve_insert.set()

@dp.message_handler(state=Position.waiting_for_approve_insert, commands=['menu'])
async def menu(message: types.Message, state: FSMContext):
    global client
    user = unreal_engine.getNamesByUser(message.from_user.id, client)
    inline_btn_1 = InlineKeyboardButton('🤡 Прикладная информатика', callback_data='button1')
    inline_btn_2 = InlineKeyboardButton('🗿 ИСиТ', callback_data='button2')
    inline_btn_3 = InlineKeyboardButton('👀 Посмореть кто за мной бздит', callback_data='button3')
    await message.reply("Наблюдение за:\n1. "+user["watch_info"]["230"]["name"]+"\n2. "+user["watch_info"]["229"]["name"], reply_markup=InlineKeyboardMarkup().add(inline_btn_1).add(inline_btn_2).add(inline_btn_3))


@dp.callback_query_handler(lambda c: c.data == 'button1', state=Position.waiting_for_approve_insert)
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    global client
    calc = unreal_engine.calculate(230, "🤡 Прикладная информатика",callback_query.from_user.id, client)
    await bot.answer_callback_query(callback_query.id)
    # place
    # name
    # sum
    # math
    # it
    # rus
    # extra
    # approve
    # hit
    # counter_yes
    # counter_maybe
    # counter_maybe_maybe
    # poly_date
    # server_date
    msg = text(bold(calc['group_name']),'\nВремя запроса: '+calc['server_date']+'\nАпдейт политеха: '+calc['poly_date']+'\nМесто (только с согласиями): '+str(calc['counter_yes'])+'\nМесто (согл. + без согл.): '+str(calc['counter_maybe'])+'\nМесто (согл. + без согл. + согл.др.направ.): '+str(calc['counter_maybe_maybe'])+'\nЗаявление: '+calc['approve']+'\nПопадание: '+calc['hit']+'\nСумма баллов: '+calc['sum']+'\nФИО: '+calc['name']+'\nМесто в таблице политеха(не нужно): '+calc['place'])
    await bot.send_message(callback_query.from_user.id, msg)

@dp.callback_query_handler(lambda c: c.data == 'button2', state=Position.waiting_for_approve_insert)
async def process_callback_button2(callback_query: types.CallbackQuery, state: FSMContext):
    global client
    calc = unreal_engine.calculate(229, "🗿 ИСиТ", callback_query.from_user.id, client)
    await bot.answer_callback_query(callback_query.id)
    msg = text(bold(calc['group_name']),'\nВремя запроса: '+calc['server_date']+'\nАпдейт политеха: '+calc['poly_date']+'\nМесто (только с согласиями): '+str(calc['counter_yes'])+'\nМесто (согл. + без согл.): '+str(calc['counter_maybe'])+'\nМесто (согл. + без согл. + согл.др.направ.): '+str(calc['counter_maybe_maybe'])+'\nЗаявление: '+calc['approve']+'\nПопадание: '+calc['hit']+'\nСумма баллов: '+calc['sum']+'\nФИО: '+calc['name']+'\nМесто в таблице политеха(не нужно): '+calc['place'])
    await bot.send_message(callback_query.from_user.id, msg)

@dp.callback_query_handler(lambda c: c.data == 'button3', state=Position.waiting_for_approve_insert)
async def process_callback_button3(callback_query: types.CallbackQuery, state: FSMContext):
    global client
    calc = unreal_engine.countSubs(callback_query.from_user.id, client)
    string = 'Список следящих за таким же ФИО:\n'
    for user in calc:
        # print(dir(user))
        # print(str(user['watcher_first_name']))
        # print(str(user['watcher_last_name']))
        # print(str(user['watcher_username']))
        string = string + '• ' + str(user['watcher_first_name']) + ' ' + str(user['watcher_last_name']) + ' (@' + str(user['watcher_username']) + ')\n'
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, string)
