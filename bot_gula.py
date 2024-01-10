from io import BytesIO
import os
import mysql.connector
import logging
import matplotlib.pyplot as plt
import json
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)

# Koneksi ke MySQL
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="mydatabase3"
)

# Inisialisasi bot
bot = Bot(token="6760519530:AAHJPOBpwKzLidnVnehnrUSM3QFNAyYzik4")
dp = Dispatcher(bot, storage=MemoryStorage())

# State untuk pengisian/edit profil
class ProfileStates(StatesGroup):
    NAMA = State()
    USIA = State()
    JENIS_KELAMIN = State()
    EMAIL = State()
    NOMOR_TELEPON = State()
    BERAT_BADAN = State()
    TINGGI_BADAN = State()
    ALAMAT = State()

# State untuk pengisian rekam medis
class RekamMedisStates(StatesGroup):
    GULA_DARAH_SEWAKTU = State()
    GULA_DARAH_PUASA = State()
    TEKANAN_DARAH_SISTOLIK = State()
    TEKANAN_DARAH_DIASTOLIK = State()
    DELETE_ID = State()

@dp.message_handler(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id

    # Periksa apakah pengguna telah terdaftar
    id = check_id(user_id)

    if id:
        await message.reply("Halo! Selamat datang di Bot Rekam Medis Diabetes. Silakan pilih menu yang tersedia.",
                            reply_markup=menu_keyboard())
    else:
        await message.reply("Anda belum terdaftar. Silakan melakukan registrasi di web terlebih dahulu.")

def check_id(user_id):
    mycursor = mydb.cursor()
    sql = "SELECT id FROM users WHERE user_id = %s"
    val = (user_id,)
    mycursor.execute(sql, val)
    result = mycursor.fetchone()
    mycursor.close()

    if result and result[0] == 1:
        return True
    else:
        return False
    
def register_user(user_id):
    mycursor = mydb.cursor()
    sql = "INSERT INTO users (user_id, id) VALUES (%s, 1)"
    val = (user_id,)
    mycursor.execute(sql, val)
    mydb.commit()
    mycursor.close()

# Keyboard untuk menu
def menu_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Profil", callback_data="profile_menu"))
    keyboard.add(types.InlineKeyboardButton(text="Rekam Medis", callback_data="rekam_medis_menu"))
    keyboard.add(types.InlineKeyboardButton(text="Insight", callback_data="insight"))
    return keyboard

# Command /profile
@dp.callback_query_handler(text='profile_menu')
async def profile_menu(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Menu Profil", reply_markup=profile_keyboard())

# Keyboard untuk menu profil
def profile_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Edit/Isi Profile", callback_data="edit_profile"))
    keyboard.add(types.InlineKeyboardButton(text="Lihat Profile", callback_data="view_profile"))
    keyboard.add(types.InlineKeyboardButton(text="Kembali", callback_data="back_to_menu"))
    return keyboard

# Command /backtomenu
@dp.callback_query_handler(text='back_to_menu')
async def back_to_menu(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Kembali ke menu utama", reply_markup=menu_keyboard())


# Command /editprofile
@dp.callback_query_handler(text='edit_profile')
async def edit_profile(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Silakan masukkan nama:")
    await ProfileStates.NAMA.set()

# Menangani input nama saat edit profil
@dp.message_handler(state=ProfileStates.NAMA)
async def process_edit_nama(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['nama'] = message.text

    await message.reply("Silakan masukkan usia:")
    await ProfileStates.USIA.set()

# Menangani input usia saat edit profil
@dp.message_handler(state=ProfileStates.USIA)
async def process_edit_usia(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['usia'] = message.text

    await message.reply("Silakan masukkan jenis kelamin:")
    await ProfileStates.JENIS_KELAMIN.set()

# Menangani input jenis kelamin saat edit profil
@dp.message_handler(state=ProfileStates.JENIS_KELAMIN)
async def process_edit_jk(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['jenis_kelamin'] = message.text

    await message.reply("Silakan masukkan email:")
    await ProfileStates.EMAIL.set()

# Menangani input email saat edit profil
@dp.message_handler(state=ProfileStates.EMAIL)
async def process_edit_email(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['email'] = message.text

    await message.reply("Silakan masukkan nomor telepon:")
    await ProfileStates.NOMOR_TELEPON.set()

# Menangani input nomor telepon saat edit profil
@dp.message_handler(state=ProfileStates.NOMOR_TELEPON)
async def process_edit_nomor_telepon(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['nomor_telepon'] = message.text

    await message.reply("Silakan masukkan berat badan:")
    await ProfileStates.BERAT_BADAN.set()

# Menangani input berat badan saat edit profil
@dp.message_handler(state=ProfileStates.BERAT_BADAN)
async def process_edit_berat_badan(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['berat_badan'] = message.text

    await message.reply("Silakan masukkan tinggi badan:")
    await ProfileStates.TINGGI_BADAN.set()

# Menangani input tinggi badan saat edit profil
@dp.message_handler(state=ProfileStates.TINGGI_BADAN)
async def process_edit_tinggi_badan(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['tinggi_badan'] = message.text

    await message.reply("Silakan masukkan alamat:")
    await ProfileStates.ALAMAT.set()

# Menangani input alamat saat edit profil
@dp.message_handler(state=ProfileStates.ALAMAT)
async def process_edit_alamat(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['alamat'] = message.text

    # Update data profil ke database
    update_profile_data(message.from_user.id, data)

    await message.reply("Profil berhasil diperbarui.")

    # Kembali ke menu profil
    await bot.send_message(message.chat.id, "Menu Profil", reply_markup=profile_keyboard())
# Fungsi untuk menyimpan atau memperbarui data profil ke database
def update_profile_data(user_id, data):
    mycursor = mydb.cursor()
    sql = "UPDATE pasien SET nama=%s, usia=%s, jenis_kelamin=%s, email=%s, nomor_telepon=%s, berat_badan=%s, tinggi_badan=%s, alamat=%s WHERE user_id=%s"
    val = (data['nama'], data['usia'], data['jenis_kelamin'], data['email'], data['nomor_telepon'], data['berat_badan'], data['tinggi_badan'], data['alamat'], user_id)
    mycursor.execute(sql, val)
    mydb.commit()
    
# Command /viewprofile
@dp.callback_query_handler(text='view_profile')
async def view_profile(callback_query: types.CallbackQuery):
    profile_data = get_profile_data(callback_query.from_user.id)
    if profile_data:
        profile_text = f"Nama: {profile_data['nama']}\n"
        profile_text += f"Usia: {profile_data['usia']}\n"
        profile_text += f"Jenis Kelamin: {profile_data['jenis_kelamin']}\n"
        profile_text += f"Email: {profile_data['email']}\n"
        profile_text += f"Nomor Telepon: {profile_data['nomor_telepon']}\n"
        profile_text += f"Berat Badan: {profile_data['berat_badan']}\n"
        profile_text += f"Tinggi Badan: {profile_data['tinggi_badan']}\n"
        profile_text += f"Alamat: {profile_data['alamat']}"

        await bot.send_message(callback_query.from_user.id, profile_text)
    else:
        await bot.send_message(callback_query.from_user.id, "Profil tidak ditemukan.")

    # Kembali ke menu profil
    await bot.send_message(callback_query.from_user.id, "Menu Profil", reply_markup=profile_keyboard())

# Fungsi untuk mendapatkan data profil dari database
def get_profile_data(user_id):
    mycursor = mydb.cursor()
    sql = "SELECT * FROM pasien WHERE user_id = %s"
    val = (user_id,)
    mycursor.execute(sql, val)
    result = mycursor.fetchone()
    if result:
        profile_data = {
            'nama': result[1],
            'usia': result[2],
            'jenis_kelamin': result[3],
            'email': result[4],
            'nomor_telepon': result[5],
            'berat_badan': result[6],
            'tinggi_badan': result[7],
            'alamat': result[8]
        }
        return profile_data
    else:
        return None

# States untuk rekam medis baru
class RekamMedisStates(StatesGroup):
    GULA_DARAH_SEWAKTU = State()
    GULA_DARAH_PUASA = State()
    TEKANAN_DARAH_SISTOLIK = State()
    TEKANAN_DARAH_DIASTOLIK = State()
    CATATAN = State()


# Command /rekammedis
@dp.callback_query_handler(text='rekam_medis_menu')
async def rekam_medis_menu(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Menu Rekam Medis", reply_markup=rekam_medis_keyboard())


# Keyboard untuk menu rekam medis
def rekam_medis_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Rekam Medis Baru", callback_data="new_rekam_medis"))
    keyboard.add(types.InlineKeyboardButton(text="Lihat Rekam Medis", callback_data="view_rekam_medis"))
    keyboard.add(types.InlineKeyboardButton(text="Hapus Rekam Medis", callback_data="delete_rekam_medis"))
    keyboard.add(types.InlineKeyboardButton(text="Kembali", callback_data="back_to_menu"))
    return keyboard


# Command /newrekammedis
@dp.callback_query_handler(text='new_rekam_medis')
async def new_rekam_medis(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Silakan masukkan gula darah sewaktu:")
    await RekamMedisStates.GULA_DARAH_SEWAKTU.set()


# Menangani input gula darah sewaktu saat rekam medis baru
@dp.message_handler(state=RekamMedisStates.GULA_DARAH_SEWAKTU)
async def process_new_gula_darah_sewaktu(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['gula_darah_sewaktu'] = message.text

    await message.reply("Silakan masukkan gula darah puasa:")
    await RekamMedisStates.GULA_DARAH_PUASA.set()


# Menangani input gula darah puasa saat rekam medis baru
@dp.message_handler(state=RekamMedisStates.GULA_DARAH_PUASA)
async def process_new_gula_darah_puasa(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['gula_darah_puasa'] = message.text

    await message.reply("Silakan masukkan tekanan darah sistolik:")
    await RekamMedisStates.TEKANAN_DARAH_SISTOLIK.set()


# Menangani input tekanan darah sistolik saat rekam medis baru
@dp.message_handler(state=RekamMedisStates.TEKANAN_DARAH_SISTOLIK)
async def process_new_tekanan_darah_sistolik(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['tekanan_darah_sistolik'] = message.text

    await message.reply("Silakan masukkan tekanan darah diastolik:")
    await RekamMedisStates.TEKANAN_DARAH_DIASTOLIK.set()


# Menangani input tekanan darah diastolik saat rekam medis baru
@dp.message_handler(state=RekamMedisStates.TEKANAN_DARAH_DIASTOLIK)
async def process_new_tekanan_darah_diastolik(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['tekanan_darah_diastolik'] = message.text

    await message.reply("Silakan masukkan catatan:")
    await RekamMedisStates.CATATAN.set()

# Menangani input catatan saat rekam medis baru
@dp.message_handler(state=RekamMedisStates.CATATAN)
async def process_new_catatan(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['catatan'] = message.text

    # Simpan data rekam medis ke database
    save_rekam_medis_data(message.from_user.id, data)

    await message.reply("Rekam medis berhasil disimpan.")

    # Kembali ke menu rekam medis
    await bot.send_message(message.chat.id, "Menu Rekam Medis", reply_markup=rekam_medis_keyboard())



# Fungsi untuk menyimpan data rekam medis ke database
def save_rekam_medis_data(user_id, data):
    mycursor = mydb.cursor()
    sql = "INSERT INTO report (user_id, gula_darah_sewaktu, gula_darah_puasa, tekanan_darah_sistolik, tekanan_darah_diastolik, catatan) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (user_id, data['gula_darah_sewaktu'], data['gula_darah_puasa'], data['tekanan_darah_sistolik'], data['tekanan_darah_diastolik'], data['catatan'])
    mycursor.execute(sql, val)
    mydb.commit()


# Command /viewrekammedis
@dp.callback_query_handler(text='view_rekam_medis')
async def view_rekam_medis(callback_query: types.CallbackQuery):
    rekam_medis_data = get_rekam_medis_data(callback_query.from_user.id)
    if rekam_medis_data:
        rekam_medis_text = "Rekam Medis:\n\n"
        for data in rekam_medis_data:
            rekam_medis_text += f"ID: {data[0]}\n"
            rekam_medis_text += f"Gula Darah Sewaktu: {data[2]}\n"
            rekam_medis_text += f"Gula Darah Puasa: {data[3]}\n"
            rekam_medis_text += f"Tekanan Darah Sistolik: {data[4]}\n"
            rekam_medis_text += f"Tekanan Darah Diastolik: {data[5]}\n"
            rekam_medis_text += f"Catatan: {data[6]}\n\n"

        await bot.send_message(callback_query.from_user.id, rekam_medis_text)
    else:
        await bot.send_message(callback_query.from_user.id, "Tidak ada data rekam medis.")

# Fungsi untuk mengambil data rekam medis dari database
def get_rekam_medis_data(user_id):
    mycursor = mydb.cursor()
    sql = "SELECT * FROM report WHERE user_id = %s"
    val = (user_id,)
    mycursor.execute(sql, val)
    result = mycursor.fetchall()
    mycursor.close()

    return result


# Fungsi untuk menghapus data rekam medis dari database
def delete_rekam_medis_data(user_id, delete_id):
    mycursor = mydb.cursor()
    sql = "DELETE FROM report WHERE user_id = %s AND id = %s"
    val = (user_id, delete_id)
    mycursor.execute(sql, val)
    mydb.commit()
    return mycursor.rowcount > 0


# Command /insight
@dp.callback_query_handler(text='insight')
async def insight(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    mycursor = mydb.cursor()
    sql = "SELECT gula_darah_sewaktu, gula_darah_puasa, tekanan_darah_diastolik, tekanan_darah_sistolik FROM report WHERE user_id = %s"
    val = (user_id,)
    mycursor.execute(sql, val)
    results = mycursor.fetchall()
    mycursor.close()

    if results:
        # Memproses data dan membuat grafik
        create_chart('Gula Darah Sewaktu', results, 140, 'gula_darah_sewaktu_chart.png')
        create_chart('Gula Darah Puasa', results, 140, 'gula_darah_puasa_chart.png')
        create_chart('Tekanan Darah Diastolik', results, 100, 'tekanan_darah_diastolik_chart.png')
        create_chart('Tekanan Darah Sistolik', results, 140, 'tekanan_darah_sistolik_chart.png')

        # Mengirim grafik ke pengguna
        with open('gula_darah_sewaktu_chart.png', 'rb') as photo:
            await bot.send_photo(callback_query.from_user.id, photo)
        with open('gula_darah_puasa_chart.png', 'rb') as photo:
            await bot.send_photo(callback_query.from_user.id, photo)
        with open('tekanan_darah_diastolik_chart.png', 'rb') as photo:
            await bot.send_photo(callback_query.from_user.id, photo)
        with open('tekanan_darah_sistolik_chart.png', 'rb') as photo:
            await bot.send_photo(callback_query.from_user.id, photo)

        # Menghapus file gambar setelah dikirim
        os.remove('gula_darah_sewaktu_chart.png')
        os.remove('gula_darah_puasa_chart.png')
        os.remove('tekanan_darah_diastolik_chart.png')
        os.remove('tekanan_darah_sistolik_chart.png')

        await bot.send_message(callback_query.from_user.id, "Menu Utama", reply_markup=menu_keyboard())
    else:
        await bot.send_message(callback_query.from_user.id, "Data rekam medis tidak ditemukan!")

# Fungsi untuk membuat grafik
def create_chart(parameter, data, normal_limit, filename):
    data_column_index = 0  # Ganti dengan indeks kolom yang sesuai dengan parameter
    values = [float(row[data_column_index]) for row in data]
    labels = [parameter, 'Others']
    percentages = [(value / sum(values)) * 100 for value in values]

    # Buat diagram
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(
        percentages,
        labels=labels,
        autopct='%1.1f%%',
        startangle=90,
        colors=['skyblue', 'lightgrey'],
        wedgeprops=dict(width=0.4),
    )

    # Tambahkan angka pada setiap sektor
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_size(8)  # Atur ukuran huruf agar muat

    # Tambahkan batas normal
    ax.axhline(y=normal_limit, color='r', linestyle='--', label=f'Batas Normal {parameter}')

    ax.set_title(f'{parameter} Overview')
    ax.axis('equal')
    ax.legend()

    # Simpan diagram ke file
    plt.savefig(filename)
    plt.close()


# Command /backtomenu
@dp.callback_query_handler(text='back_to_menu')
async def back_to_menu(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Kembali ke menu utama", reply_markup=menu_keyboard)

# Memulai bot
print("program system anda berhasil dijalankan")
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
