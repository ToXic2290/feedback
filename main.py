import logging
from aiogram import Bot, Dispatcher, executor, types
from config import API_TOKEN, admin
import keyboard as kb
import functions as func
import sqlite3
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import Throttled

storage = MemoryStorage()
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)
connection = sqlite3.connect('data.db')
q = connection.cursor()

class st(StatesGroup):
	item = State()
	item2 = State()
	item3 = State()
	item4 = State()

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
	func.join(chat_id=message.chat.id)
	q.execute(f"SELECT block FROM users WHERE user_id = {message.chat.id}")
	result = q.fetchone()
	if result[0] == 0:
		if message.chat.id == admin:
			await message.answer('👋🏻*Добро пожаловать!*', parse_mode= 'Markdown', reply_markup=kb.menu)
		else:
			await message.answer('👋🏻*Привет! Это бот обратной связи с @ToXicUse.*\n\n*💦Напиши мне свой вопрос и я отправлю его создателю!*\n\n*‼️За спам/флуд - ЧС!*', parse_mode= 'Markdown')
	else:
		await message.answer('🌝')

@dp.message_handler(content_types=['text'], text='💈Админка💈')
async def handfler(message: types.Message, state: FSMContext):
	func.join(chat_id=message.chat.id)
	q.execute(f"SELECT block FROM users WHERE user_id = {message.chat.id}")
	result = q.fetchone()
	if result[0] == 0:
		if message.chat.id == admin:
			await message.answer('*🌴 Дарова заебал, це админ панель, делай че хочешь тут и давай всем пиздюлей!*', parse_mode= 'Markdown', reply_markup=kb.adm)


@dp.message_handler(content_types=['text'], text='↩️ Назад')
async def handledr(message: types.Message, state: FSMContext):
	await message.answer('👋🏻*Добро пожаловать!*', parse_mode= 'Markdown', reply_markup=kb.menu)

@dp.message_handler(content_types=['text'], text='👿 ЧС')
async def handlaer(message: types.Message, state: FSMContext):
	func.join(chat_id=message.chat.id)
	q.execute(f"SELECT block FROM users WHERE user_id = {message.chat.id}")
	result = q.fetchone()
	if result[0] == 0:
		if message.chat.id == admin:
			q.execute(f"SELECT * FROM users WHERE block == 1")
			result = q.fetchall()
			sl = []
			for index in result:
				i = index[0]
				sl.append(i)

			ids = '\n'.join(map(str, sl))
			await message.answer(f'<b>🆔 пользователей в ЧС:</b>\n{ids}', parse_mode= 'HTML')


@dp.message_handler(content_types=['text'], text='✅ Добавить в ЧС')
async def hanadler(message: types.Message, state: FSMContext):
	func.join(chat_id=message.chat.id)
	q.execute(f"SELECT block FROM users WHERE user_id = {message.chat.id}")
	result = q.fetchone()
	if result[0] == 0:
		if message.chat.id == admin:
			await message.answer('<b>📝 Введи ID пользователя, которого нужно заблокировать.</b>\n\n↩️<b>Для отмены нажми кнопку ниже.</b>', parse_mode= 'HTML', reply_markup=kb.back)
			await st.item3.set()

@dp.message_handler(content_types=['text'], text='❎ Убрать из ЧС')
async def hfandler(message: types.Message, state: FSMContext):
	func.join(chat_id=message.chat.id)
	q.execute(f"SELECT block FROM users WHERE user_id = {message.chat.id}")
	result = q.fetchone()
	if result[0] == 0:
		if message.chat.id == admin:
			await message.answer('<b>📝 Введи ID пользователя, которого нужно разблокировать.</b>\n\n↩️<b>Для отмены нажми кнопку ниже.</b>', parse_mode= 'HTML', reply_markup=kb.back)
			await st.item4.set()

@dp.message_handler(content_types=['text'], text='💬 Рассылка')
async def hangdler(message: types.Message, state: FSMContext):
	func.join(chat_id=message.chat.id)
	q.execute(f"SELECT block FROM users WHERE user_id = {message.chat.id}")
	result = q.fetchone()
	if result[0] == 0:
		if message.chat.id == admin:
			await message.answer('<b>📝 Введи текст для рассылки.</b>\n\n↩️<b>Для отмены нажми на кнопку ниже.</b>', parse_mode= 'HTML', reply_markup=kb.back)
			await st.item.set()

@dp.message_handler(content_types=['text'])
@dp.throttled(func.antiflood, rate=3)
async def h(message: types.Message, state: FSMContext):
	func.join(chat_id=message.chat.id)
	q.execute(f"SELECT block FROM users WHERE user_id = {message.chat.id}")
	result = q.fetchone()
	if result[0] == 0:
		if message.chat.id == admin:
			pass
		else:
			await message.answer('✅ *Сообщение отправлено!*', parse_mode= 'Markdown')
			await bot.send_message(admin, f"<b>💬Получен новый вопрос!💬</b>\n\n<b>🔗От:</b> {message.from_user.mention}\n🆔<b>ID</b>: <code>{message.chat.id}</code>\n<b>📝Сообщение:</b> {message.text}", reply_markup=kb.fun(message.chat.id), parse_mode='HTML')
	else:
		await message.answer('._.')

@dp.callback_query_handler(lambda call: True)
async def cal(call, state: FSMContext):
	if 'ans' in call.data:
		a = call.data.index('-ans')
		ids = call.data[:a]
		await call.message.answer('🖊 *Введи ответ:*', parse_mode= 'Markdown', reply_markup=kb.back)
		await st.item2.set()
		await state.update_data(uid=ids)
	elif 'ignor' in call.data:
		await call.answer('Удалено!')
		await bot.delete_message(call.message.chat.id, call.message.message_id)
		await state.finish()

@dp.message_handler(state=st.item2)
async def proc(message: types.Message, state: FSMContext):
	if message.text == '↩️ Отмена':
		await message.answer('↩️ *Отмена! Возвращаю назад!*', parse_mode= 'Markdown', reply_markup=kb.menu)
		await state.finish()
	else:
		await message.answer('✅ *Сообщение отправлено!*', parse_mode= 'Markdown', reply_markup=kb.menu)
		data = await state.get_data()
		id = data.get("uid")
		await state.finish()
		await bot.send_message(id, '<b>☂️ Вам поступил ответ от создателя!</b>\n\n<b>📝Текст:</b> {}'.format(message.text), parse_mode= 'HTML')

@dp.message_handler(state=st.item)
async def process_name(message: types.Message, state: FSMContext):
	q.execute(f'SELECT user_id FROM users')
	row = q.fetchall()
	connection.commit()
	text = message.text
	if message.text == '↩️ Отмена':
		await message.answer('↩️*Отмена! Возвращаю назад!*', parse_mode= 'Markdown', reply_markup=kb.adm)
		await state.finish()
	else:
		info = row
		await message.answer('📣*Рассылка начата!*', parse_mode= 'Markdown', reply_markup=kb.adm)
		for i in range(len(info)):
			try:
				await bot.send_message(info[i][0], str(text))
			except:
				pass
		await message.answer('*☑️ Рассылка завершена!*', parse_mode= 'Markdown', reply_markup=kb.adm)
		await state.finish()

@dp.message_handler(state=st.item3)
async def proce(message: types.Message, state: FSMContext):
	if message.text == '↩️ Отмена':
		await message.answer('↩️*Отмена! Возвращаю назад!*', parse_mode= 'Markdown', reply_markup=kb.adm)
		await state.finish()
	else:
		if message.text.isdigit():
			q.execute(f"SELECT block FROM users WHERE user_id = {message.text}")
			result = q.fetchall()
			connection.commit()
			if len(result) == 0:
				await message.answer('⛔️ *Такой пользователь не найден в базе данных!*', parse_mode= 'Markdown', reply_markup=kb.adm)
				await state.finish()
			else:
				a = result[0]
				id = a[0]
				if id == 0:
					q.execute(f"UPDATE users SET block = 1 WHERE user_id = {message.text}")
					connection.commit()
					await message.answer('☑️ *Пользователь успешно добавлен в ЧС!*', parse_mode= 'Markdown', reply_markup=kb.adm)
					await state.finish()
					await bot.send_message(message.text, '‼️*Ты добавлен в ЧС*‼️', parse_mode= 'Markdown')
				else:
					await message.answer('*⁉️Данный пользовательно уже добавлен в ЧС!*', parse_mode= 'Markdown', reply_markup=kb.adm)
					await state.finish()
		else:
			await message.answer('❌ *Неверный ID!*', parse_mode= 'Markdown')

@dp.message_handler(state=st.item4)
async def proc(message: types.Message, state: FSMContext):
	if message.text == '↩️ Отмена':
		await message.answer('↩️ *Отмена! Возвращаю назад!*', parse_mode= 'Markdown', reply_markup=kb.adm)
		await state.finish()
	else:
		if message.text.isdigit():
			q.execute(f"SELECT block FROM users WHERE user_id = {message.text}")
			result = q.fetchall()
			connection.commit()
			if len(result) == 0:
				await message.answer('❌ *Такой пользователь не найден в базе данных!*', parse_mode= 'Markdown', reply_markup=kb.adm)
				await state.finish()
			else:
				a = result[0]
				id = a[0]
				if id == 1:
					q.execute(f"UPDATE users SET block = 0 WHERE user_id = {message.text}")
					connection.commit()
					await message.answer('*🌸 Пользователь успешно разбанен!*', parse_mode= 'Markdown', reply_markup=kb.adm)
					await state.finish()
					await bot.send_message(message.text, '*🌸Ты был разблокирован!*', parse_mode= 'Markdown')
				else:
					await message.answer('🌝', reply_markup=kb.adm)
					await state.finish()
		else:
			await message.answer('❌ *Неверный ID!*', parse_mode= 'Markdown')


if __name__ == '__main__':
	executor.start_polling(dp, skip_updates=True)