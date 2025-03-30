from telegram import Update

from config import supabase

async def handle_download(update: Update, context):
    """Handler untuk mengunduh file berdasarkan file_code."""
    
    # Ambil file_code dari pesan
    if not context.args:
        await update.message.reply_text("Gunakan perintah /download <file_code>")
        return
    
    #Memberitahukan pengguna bahwa unduhan sedang diproses
    await update.message.reply_text("Mengunduh file...")
    
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