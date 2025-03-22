from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from supabase import create_client
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

# Konfigurasi Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Konfigurasi Telegram
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

async def admins(user_id):
    """Periksa apakah pengguna adalah admin."""
    try:
        response = supabase.table('admins').select('*').eq('user_id', user_id).execute()
        return len(response.data) > 0
    except Exception as e:
        print("Error Supabase:", e)
        return False

def generate_file_code(file_name):
    """Generate file_code berdasarkan nama file dan kode unik."""
    # Potong ekstensi file
    base_name = file_name.rsplit('.', 1)[0]  # Ambil nama tanpa ekstensi
    unique_code = str(uuid.uuid4())[:6].upper()  # Generate kode unik 6 karakter (uppercase)
    return f"{base_name}-{unique_code}"

async def handle_document(update: Update, context):
    user_id = update.message.from_user.id

    # Periksa apakah pengguna adalah admin
    if not await admins(user_id):
        await update.message.reply_text("Anda bukan admin.")
        return

    # Ambil informasi file dari pesan
    document = update.message.document
    file_id = document.file_id
    file_name = document.file_name

    print(f'User ID: {user_id}, File Name: {file_name}, File ID: {file_id}')

    # Cek apakah file_id sudah ada di database
    try:
        response = supabase.table('file_storage').select('*').eq('file_id', file_id).execute()
        if response.data:
            # Jika file sudah ada, ambil data dari database
            file_data = response.data[0]
            file_code = file_data['file_code']
            await update.message.reply_text(
                f"File sudah ada di database:\n"
                f"Nama File: {file_name}\n"
                f"File Code: {file_code}\n"
                f"File ID: {file_id}"
            )
            return
    except Exception as e:
        print("Error Supabase:", e)
        await update.message.reply_text("Terjadi kesalahan saat memeriksa database.")
        return

    # Jika file belum ada, simpan ke database
    file_code = generate_file_code(file_name)  # Generate file_code
    try:
        response = supabase.table('file_storage').insert({
            "file_code": file_code,
            "file_id": file_id
        }).execute()

        # Periksa apakah respons valid
        if not response.data:
            print("Error Supabase: Tidak ada data dalam respons.")
            await update.message.reply_text("Gagal menyimpan file. Silakan coba lagi.")
            return

        # Jika berhasil
        await update.message.reply_text(
            f"File berhasil disimpan:\n"
            f"Nama File: {file_name}\n"
            f"File Code: {file_code}\n"
            f"File ID: {file_id}"
        )
    except Exception as e:
        print("Error saat menyimpan ke Supabase:", e)
        await update.message.reply_text("Terjadi kesalahan saat menyimpan file.")

async def handle_download(update: Update, context):
    """Handler untuk mengunduh file berdasarkan file_code."""
    
    # Ambil file_code dari pesan
    if not context.args:
        await update.message.reply_text("Gunakan perintah /download <file_code>")
        return
    
    file_code = context.args[0]
    print(f"File Code: {file_code}")

    # Cari file berdasarkan file_code
    try:
        response = supabase.table('file_storage').select('*').eq('file_code', file_code).execute()
        if not response.data:
            await update.message.reply_text("File tidak ditemukan.")
            return
        
        # Ambil data file
        file_data = response.data[0]
        file_id = file_data['file_id']
        print(f"File ID: {file_id}")

        # Kirim file ke pengguna
        await update.message.reply_document(document=file_id)
        await update.message.reply_text("Download di Onimono.Com")
    except Exception as e:
        print("Error saat mengunduh file:", e)
        await update.message.reply_text("Terjadi kesalahan saat mengunduh file.")

def main():
    application = Application.builder().token(TOKEN).build()

    # Handler untuk dokumen
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    # Handler untuk download
    application.add_handler(CommandHandler("download", handle_download))

    # Jalankan bot
    application.run_polling()

if __name__ == '__main__':
    main()