import logging
import asyncio
import aiogram
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import mysql.connector

# Konfigurasi database MySQL
db_config = {
    'user': 'username',
    'password': 'password',
    'host': 'localhost',
    'database': 'database_name'
}

# Inisialisasi bot
bot = Bot(token='YOUR_TELEGRAM_BOT_TOKEN')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Inisialisasi koneksi ke database MySQL
db_connection = mysql.connector.connect(**db_config)
db_cursor = db_connection.cursor()

# Pengaturan logging
logging.basicConfig(level=logging.INFO)


# Fungsi untuk membuat tabel medis jika belum ada
def create_medical_table():
    db_cursor.execute('''
        CREATE TABLE IF NOT EXISTS medical_records (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            username VARCHAR(255),
            name VARCHAR(255),
            age INT,
            gender VARCHAR(10),
            blood_sugar_level FLOAT,
            notes TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    db_connection.commit()


# Fungsi untuk menyimpan data medis ke database
def save_medical_record(user_id, username, name, age, gender, blood_sugar_level, notes):
    sql = '''
        INSERT INTO medical_records (user_id, username, name, age, gender, blood_sugar_level, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    '''
    values = (user_id, username, name, age, gender, blood_sugar_level, notes)
    db_cursor.execute(sql, values)
    db_connection.commit()


# Handler untuk command /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply('Halo! Selamat datang di Bot Rekam Medis Diabetes. Untuk memulai, silakan kirim informasi berikut:\n\nNama Anda:')
    await bot.register_next_step_handler(message, process_name_step)


# Handler untuk memproses langkah informasi nama
async def process_name_step(message: types.Message):
    message_text = message.text.strip()
    if message_text:
        message.chat.name = message_text
        await message.reply('Berapa usia Anda?')
        await bot.register_next_step_handler(message, process_age_step)
    else:
        await message.reply('Mohon masukkan nama Anda. Silakan ulangi langkah ini.')


# Handler untuk memproses langkah informasi usia
async def process_age_step(message: types.Message):
    message_text = message.text.strip()
    if message_text.isdigit():
        message.chat.age = int(message_text)
        await message.reply('Jenis kelamin Anda (Pria/Wanita)?')
        await bot.register_next_step_handler(message, process_gender_step)
    else:
        await message.reply('Mohon masukkan usia Anda dalam angka. Silakan ulangi langkah ini.')


# Handler untuk memproses langkah informasi jenis kelamin
async def process_gender_step(message: types.Message):
    message_text = message.text.strip().lower()
    if message_text in ['pria', 'wanita']:
        message.chat.gender = message_text
        await message.reply('Silakan kirim level gula darah Anda.')
        await bot.register_next_step_handler(message, process_blood_sugar_level_step)
    else:
        await message.reply('Mohon masukkan jenis kelamin Anda (Pria/Wanita). Silakan ulangi langkah ini.')

# Handler untuk memproses langkah informasi level gula darah
@dp.message_handler(regexp=r'^\d+(.\d+)?$')
async def process_blood_sugar_level_step(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    name = message.chat.name
    age = message.chat.age
    gender = message.chat.gender
    blood_sugar_level = message.text

# Simpan rekaman medis ke database
    save_medical_record(user_id, username, name, age, gender, blood_sugar_level, '')
    await message.reply('Data medis Anda telah direkam.')

#Handler untuk menerima catatan tambahan dari pengguna
@dp.message_handler(commands=['notes'])
async def request_notes(message: types.Message):
    await message.reply('Silakan kirim catatan tambahan untuk rekaman medis Anda.')

#Handler untuk menerima catatan tambahan dari pengguna
@dp.message_handler()
async def save_notes(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    notes = message.text

# Lakukan query ke database untuk mendapatkan rekaman medis terakhir
db_cursor.execute('SELECT id FROM medical_records WHERE user_id = %s ORDER BY timestamp DESC LIMIT 1', (user_id,))
record_id = db_cursor.fetchone()[0]

sql = '''
    UPDATE medical_records
    SET notes = %s
    WHERE id = %s
'''
values = (notes, record_id)
db_cursor.execute(sql, values)
db_connection.commit()

#Handler untuk menerima input yang tidak valid
@dp.message_handler()
async def handle_invalid_input(message: types.Message):
    await message.reply('Mohon maaf, input tidak valid. Silakan ikuti langkah-langkah untuk memasukkan informasi Anda dengan benar.')

#Handler untuk command /records
@dp.message_handler(commands=['records'])
async def show_medical_records(message: types.Message):
    user_id = message.from_user.id
    records = get_medical_records(user_id)

    if records:
        response = 'Berikut adalah rekaman medis Anda:\n\n'
    for record in records:
        response += f'ID: {record[0]}\n'
        response += f'Nama: {record[3]}\n'
        response += f'Usia: {record[4]}\n'
        response += f'Jenis Kelamin: {record[5]}\n'
        response += f'Level Gula Darah: {record[6]}\n'
        response += f'Catatan: {record[7]}\n'
        response += f'Timestamp: {record[8]}\n\n'

    else:
        message.reply(response)

    
#Handler untuk command /delete
@dp.message_handler(commands=['delete'])
async def delete_medical_record(message: types.Message):
    user_id = message.from_user.id
    records = get_medical_records(user_id)
    if records:
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        for record in records:
            record_id = record[0]
            timestamp = record[8].strftime('%Y-%m-%d %H:%M:%S')
            button_text = f'Rekaman #{record_id} ({timestamp})'
            callback_data = f'delete_record:{record_id}'
            keyboard.add(types.InlineKeyboardButton(button_text, callback_data=callback_data))
    
    await message.reply('Pilih rekaman medis yang ingin Anda hapus:', reply_markup=keyboard)
#handler untuk menghapus rekaman medis
@dp.callback_query_handler(lambda query: query.data.startswith('delete_record:'))
async def process_delete_record(callback_query: types.CallbackQuery):
    record_id = callback_query.data.split(':')[1]
    # Hapus rekaman medis dari database
sql = 'DELETE FROM medical_records WHERE id = %s'
values = (record_id,)
db_cursor.execute(sql, values)
db_connection.commit()

if name == 'main':
        create_medical_table()
        dp.loop.run_until_complete(dp.start_polling())