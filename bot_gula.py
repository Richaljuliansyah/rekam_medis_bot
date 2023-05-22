from io import BytesIO
import os
import mysql.connector
import logging
import matplotlib.pyplot as plt
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
    database="mydatabase"
)

# Inisialisasi bot
bot = Bot(token="6174942077:AAGJ-8GzxIa_OfwNIF9owPTZGcTbgW-H9dY")
dp = Dispatcher(bot, storage=MemoryStorage())


# State untuk pengisian/edit profil
class ProfileStates(StatesGroup):
    NAMA = State()
    USIA = State()
    JENIS_KELAMIN = State()
    EMAIL = State()
    NOMOR_TELEPON = State()
    RIWAYAT_MEDIS = State()


# State untuk pengisian rekam medis
class RekamMedisStates(StatesGroup):
    GULA_DARAH_SEWAKTU = State()
    GULA_DARAH_PUASA = State()
    KOLESTEROL = State()
    TEKANAN_DARAH = State()
    BERAT_BADAN = State()
    TINGGI_BADAN = State()
    CATATAN = State()
    DELETE_ID = State()


# Command /start
@dp.message_handler(Command("start"))
async def start(message: types.Message):
    await message.reply("Halo! Selamat datang di Bot Rekam Medis Diabetes. Silakan pilih menu yang tersedia.",
                        reply_markup=menu_keyboard())


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

@dp.message_handler(state=ProfileStates.USIA)
async def process_edit_usia(message: types.Message, state: FSMContext):
    usia = message.text
    if not usia.isdigit():
        await message.reply("Usia harus berupa angka. Silakan masukkan usia yang valid.")
        return
    
    # Melakukan validasi usia lainnya
    # ...
    
    async with state.proxy() as data:
        data['usia'] = usia

    await message.reply("Silakan masukkan jenis kelamin:")
    await ProfileStates.JENIS_KELAMIN.set()



# Menangani input jenis kelamin saat edit profil
@dp.message_handler(state=ProfileStates.JENIS_KELAMIN)
async def process_edit_jenis_kelamin(message: types.Message, state: FSMContext):
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

    await message.reply("Silakan masukkan riwayat medis:")
    await ProfileStates.RIWAYAT_MEDIS.set()


# Menangani input riwayat medis saat edit profil
@dp.message_handler(state=ProfileStates.RIWAYAT_MEDIS)
async def process_edit_riwayat_medis(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['riwayat_medis'] = message.text

# Fungsi untuk menyimpan data ke database

    user_id = message.from_user.id
    nama = data['nama']
    usia = data['usia']
    jenis_kelamin = data['jenis_kelamin']
    email = data['email']
    nomor_telepon = data['nomor_telepon']
    riwayat_medis = data['riwayat_medis']

    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="mydatabase"
        )
        mycursor = mydb.cursor()

        # Periksa apakah profil pengguna sudah ada
        check_sql = "SELECT * FROM users WHERE user_id = %s"
        check_val = (user_id,)
        mycursor.execute(check_sql, check_val)
        existing_profile = mycursor.fetchone()

        if existing_profile:
            # Profil sudah ada, lakukan operasi UPDATE
            update_sql = "UPDATE users SET nama = %s, usia = %s, jenis_kelamin = %s, email = %s, nomor_telepon = %s, riwayat_medis = %s WHERE user_id = %s"
            update_val = (nama, usia, jenis_kelamin, email, nomor_telepon, riwayat_medis, user_id)
            mycursor.execute(update_sql, update_val)
            mydb.commit()
        else:
            # Profil belum ada, lakukan operasi INSERT
            insert_sql = "INSERT INTO users (user_id, nama, usia, jenis_kelamin, email, nomor_telepon, riwayat_medis) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            insert_val = (user_id, nama, usia, jenis_kelamin, email, nomor_telepon, riwayat_medis)
            mycursor.execute(insert_sql, insert_val)
            mydb.commit()

        mycursor.close()
        mydb.close()
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Kembali", callback_data="back_to_menu"))

        await message.reply("Profil Berhasil diupdate!", reply_markup=keyboard)
        await state.finish()

    except mysql.connector.Error as error:
        print("Error while connecting to MySQL:", error)
        await bot.send_message(message.from_user.id, "Terjadi kesalahan saat menghubungkan ke database!")
#view 

@dp.callback_query_handler(text='view_profile')
async def view_profile(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    mycursor = mydb.cursor()
    sql = "SELECT nama, usia, jenis_kelamin, email, nomor_telepon, riwayat_medis FROM users WHERE user_id = %s"
    val = (user_id,)
    mycursor.execute(sql, val)
    result = mycursor.fetchone()
    mycursor.close()

    if result:
        nama, usia, jenis_kelamin, email, nomor_telepon, riwayat_medis = result
        profile_info = f"Nama: {nama}\nUsia: {usia}\nJenis Kelamin: {jenis_kelamin}\nEmail: {email}\nNomor Telepon: {nomor_telepon}\nRiwayat Medis: {riwayat_medis}"
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Kembali", callback_data="back_to_menu"))
        await bot.send_message(callback_query.from_user.id, profile_info, reply_markup=keyboard)

    else:
        await bot.send_message(callback_query.from_user.id, "Profil tidak ditemukan!")

# Command /rekammedis
@dp.callback_query_handler(text='rekam_medis_menu')
async def rekam_medis_menu(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Menu Rekam Medis", reply_markup=rekam_medis_keyboard())


# Keyboard untuk menu rekam medis
def rekam_medis_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Tambah Rekam Medis", callback_data="add_rekam_medis"))
    keyboard.add(types.InlineKeyboardButton(text="Lihat Rekam Medis", callback_data="view_rekam_medis"))
    keyboard.add(types.InlineKeyboardButton(text="Hapus Rekam Medis", callback_data="delete_rekam_medis"))
    keyboard.add(types.InlineKeyboardButton(text="Kembali", callback_data="back_to_menu"))
    return keyboard

# Command /addrekammedis
@dp.callback_query_handler(text='add_rekam_medis')
async def add_rekam_medis(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Silakan masukkan gula darah sewaktu:")
    await RekamMedisStates.GULA_DARAH_SEWAKTU.set()

# Menangani input gula darah sewaktu saat tambah rekam medis
@dp.message_handler(state=RekamMedisStates.GULA_DARAH_SEWAKTU)
async def process_add_gula_darah_sewaktu(message: types.Message, state: FSMContext):
    gula_darah_sewaktu = message.text.strip()
    if not gula_darah_sewaktu.isdigit():
        await message.reply("Masukkan gula darah sewaktu dalam bentuk angka. Silakan coba lagi.")
        return

    async with state.proxy() as data:
        data['gula_darah_sewaktu'] = gula_darah_sewaktu

    await message.reply("Silakan masukkan gula darah puasa:")
    await RekamMedisStates.GULA_DARAH_PUASA.set()


# Menangani input gula darah puasa saat tambah rekam medis
@dp.message_handler(state=RekamMedisStates.GULA_DARAH_PUASA)
async def process_add_gula_darah_puasa(message: types.Message, state: FSMContext):
    gula_darah_puasa = message.text.strip()
    if not gula_darah_puasa.isdigit():
        await message.reply("Masukkan gula darah puasa dalam bentuk angka. Silakan coba lagi.")
        return

    async with state.proxy() as data:
        data['gula_darah_puasa'] = gula_darah_puasa

    await message.reply("Silakan masukkan kadar kolesterol:")
    await RekamMedisStates.KOLESTEROL.set()


# Menangani input kadar kolesterol saat tambah rekam medis
@dp.message_handler(state=RekamMedisStates.KOLESTEROL)
async def process_add_kolesterol(message: types.Message, state: FSMContext):
    kadar_kolesterol = message.text.strip()
    if not kadar_kolesterol.isdigit():
        await message.reply("Masukkan kadar kolesterol dalam bentuk angka. Silakan coba lagi.")
        return

    async with state.proxy() as data:
        data['kolesterol'] = kadar_kolesterol

    await message.reply("Silakan masukkan tekanan darah:")
    await RekamMedisStates.TEKANAN_DARAH.set()


# Menangani input tekanan darah saat tambah rekam medis
@dp.message_handler(state=RekamMedisStates.TEKANAN_DARAH)
async def process_add_tekanan_darah(message: types.Message, state: FSMContext):
    tekanan_darah = message.text.strip()
    if not tekanan_darah.isdigit():
        await message.reply("Masukkan tekanan darah dalam bentuk angka. Silakan coba lagi.")
        return

    async with state.proxy() as data:
        data['tekanan_darah'] = tekanan_darah

    await message.reply("Silakan masukkan berat badan:")
    await RekamMedisStates.BERAT_BADAN.set()


# Menangani input berat badan saat tambah rekam medis
@dp.message_handler(state=RekamMedisStates.BERAT_BADAN)
async def process_add_berat_badan(message: types.Message, state: FSMContext):
    berat_badan = message.text.strip()
    if not berat_badan.isdigit():
        await message.reply("Masukkan berat badan dalam bentuk angka. Silakan coba lagi.")
        return

    async with state.proxy() as data:
        data['berat_badan'] = berat_badan

    await message.reply("Silakan masukkan tinggi badan:")
    await RekamMedisStates.TINGGI_BADAN.set()


# Menangani input tinggi badan saat tambah rekam medis
@dp.message_handler(state=RekamMedisStates.TINGGI_BADAN)
async def process_add_tinggi_badan(message: types.Message, state: FSMContext):
    tinggi_badan = message.text.strip()
    if not tinggi_badan.isdigit():
        await message.reply("Masukkan tinggi badan dalam bentuk angka. Silakan coba lagi.")
        return

    async with state.proxy() as data:
        data['tinggi_badan'] = tinggi_badan

    await message.reply("Silakan masukkan catatan:")
    await RekamMedisStates.CATATAN.set()


# Menangani input catatan saat tambah rekam medis
@dp.message_handler(state=RekamMedisStates.CATATAN)
async def process_add_catatan(message: types.Message, state: FSMContext):
    catatan = message.text.strip()
    if not catatan:
        await message.reply("Masukkan catatan. Silakan coba lagi.")
        return

    async with state.proxy() as data:
        data['catatan'] = catatan

    # Simpan data rekam medis ke database
    user_id = message.from_user.id
    gula_darah_sewaktu = data['gula_darah_sewaktu']
    gula_darah_puasa = data['gula_darah_puasa']
    kadar_kolesterol = data['kolesterol']
    tekanan_darah = data['tekanan_darah']
    berat_badan = data['berat_badan']
    tinggi_badan = data['tinggi_badan']
    catatan = data['catatan']

    mycursor = mydb.cursor()
    sql = """
        INSERT INTO rekam_medis
        (user_id, gula_darah_sewaktu, gula_darah_puasa, kadar_kolesterol, tekanan_darah, berat_badan, tinggi_badan, catatan)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    val = (user_id, gula_darah_sewaktu, gula_darah_puasa, kadar_kolesterol, tekanan_darah, berat_badan, tinggi_badan, catatan)
    mycursor.execute(sql, val)
    mydb.commit()
    mycursor.close()

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Lihat Rekam Medis", callback_data="view_rekam_medis"))
    keyboard.add(types.InlineKeyboardButton(text="Kembali", callback_data="back_to_menu"))
    await message.reply("Rekam medis berhasil ditambahkan!", reply_markup=keyboard)
    await state.finish()

# Command /hapusseluruhrekammedis
@dp.callback_query_handler(text='delete_rekam_medis')
async def delete_rekam_medis(callback_query: types.CallbackQuery):
    # Hapus seluruh riwayat rekam medis dari database
    try:
        cursor = mydb.cursor()
        query = "DELETE FROM rekam_medis"
        cursor.execute(query)
        mydb.commit()
        await bot.send_message(callback_query.from_user.id, "Seluruh riwayat rekam medis berhasil dihapus.")
    except mysql.connector.Error as error:
        await bot.send_message(callback_query.from_user.id, "Terjadi kesalahan saat menghapus riwayat rekam medis.")

# Menangani input ID rekam medis saat menghapus rekam medis
@dp.message_handler(state=RekamMedisStates.DELETE_ID)
async def process_delete_id(message: types.Message, state: FSMContext):
    delete_id = message.text

    # Hapus rekam medis dari database berdasarkan ID
    try:
        cursor = mydb.cursor()
        query = "DELETE FROM rekam_medis WHERE id = %s"
        cursor.execute(query, (delete_id,))
        mydb.commit()
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Kembali", callback_data="back_to_menu"))
        await message.reply("Riwayat rekam medis berhasil dihapus.", reply_markup=keyboard)
    except mysql.connector.Error as error:
        await message.reply("Terjadi kesalahan saat menghapus rekam medis.", reply_markup=keyboard)

    await state.finish()


# Command /viewrekammedis
@dp.callback_query_handler(text='view_rekam_medis')
async def view_rekam_medis(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    mycursor = mydb.cursor()
    sql = "SELECT gula_darah_sewaktu, gula_darah_puasa, kadar_kolesterol, tekanan_darah, berat_badan, tinggi_badan, catatan FROM rekam_medis WHERE user_id = %s"
    val = (user_id,)
    mycursor.execute(sql, val)
    results = mycursor.fetchall()
    mycursor.close()

    if results:
        rekam_medis_info = ""
        for row in results:
            gula_darah_sewaktu, gula_darah_puasa, kadar_kolesterol, tekanan_darah, berat_badan, tinggi_badan, catatan = row
            rekam_medis_info += f"Gula Darah Sewaktu: {gula_darah_sewaktu}\nGula Darah Puasa: {gula_darah_puasa}\nKadar Kolesterol: {kadar_kolesterol}\nTekanan Darah: {tekanan_darah}\nBerat Badan: {berat_badan}\nTinggi Badan: {tinggi_badan}\nCatatan: {catatan}\n\n"
        
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Kembali", callback_data="back_to_menu"))
        await bot.send_message(callback_query.from_user.id, rekam_medis_info, reply_markup=keyboard)
    else:
        await bot.send_message(callback_query.from_user.id, "Rekam medis tidak ditemukan!")


# Command /insight
@dp.callback_query_handler(text='insight')
async def insight(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    mycursor = mydb.cursor()
    sql = "SELECT gula_darah_sewaktu, gula_darah_puasa FROM rekam_medis WHERE user_id = %s"
    val = (user_id,)
    mycursor.execute(sql, val)
    results = mycursor.fetchall()
    mycursor.close()

    if results:
        gula_darah_sewaktu = []
        gula_darah_puasa = []
        for row in results:
            gula_darah_sewaktu.append(float(row[0]))
            gula_darah_puasa.append(float(row[1]))

        plt.figure(figsize=(10, 5))
        plt.plot(gula_darah_sewaktu, label="Gula Darah Sewaktu")
        plt.plot(gula_darah_puasa, label="Gula Darah Puasa")
        plt.xlabel("Rekam Medis ke-")
        plt.ylabel("Kadar Gula Darah (mg/dL)")
        plt.title("Grafik Kadar Gula Darah")
        plt.legend()
        plt.savefig("grafik.png")
        with open("grafik.png", "rb") as file:
            await bot.send_photo(callback_query.from_user.id, photo=file)
        os.remove("grafik.png")
        await bot.send_message(callback_query.from_user.id, "presentase statik rekam medis")
    else:
        await bot.send_message(callback_query.from_user.id, "Data rekam medis tidak ditemukan!")


# Command /backtomenu
@dp.callback_query_handler(text='back_to_menu')
async def back_to_menu(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Kembali ke menu utama", reply_markup=menu_keyboard())



# Memulai bot
print("program system anda berhasil dijalankan")
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
