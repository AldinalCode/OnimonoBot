from telegram import Update

from config import supabase
from lib.admins import admins
from lib.generateFileCode import generate_file_code

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

    # print(f'User ID: {user_id}, File Name: {file_name}, File ID: {file_id}')

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