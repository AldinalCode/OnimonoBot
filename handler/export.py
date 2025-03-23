from telegram import Update
from io import BytesIO
from datetime import datetime
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

from lib.admins import admins
from config import supabase

async def handle_exportdb(update: Update, context):
    """Handler untuk perintah /exportdb."""

    # Periksa apakah update valid
    if update is None or update.message is None:
        print("Update tidak mengandung pesan.")
        return

    user_id = update.message.from_user.id

    # Hanya admin yang bisa menggunakan perintah ini
    if not await admins(user_id):
        await update.message.reply_text("Anda bukan admin.")
        return

    # Ambil argumen dari perintah
    args = context.args
    if not args:
        await update.message.reply_text(
            "Gunakan format:\n"
            "/exportdb date YYYYMMDD\n"
            "/exportdb date YYYYMMDD YYYYMMDD\n"
            "/exportdb contains [teks]\n"
            "/exportdb contains [teks] date YYYYMMDD\n"
            "/exportdb contains [teks] date YYYYMMDD YYYYMMDD"
        )
        return

    # Memberitahu pengguna bahwa proses sedang berlangsung
    await update.message.reply_text("Sedang mengekspor database...")

    try:
        # Inisialisasi variabel
        text_filter = None
        start_local = None
        end_local = None
        start_date_str = None
        end_date_str = None

        # Cek jenis perintah
        if args[0] == "contains":
            # Perintah dengan filter teks
            if len(args) < 2:
                await update.message.reply_text("Gunakan format:\n/exportdb contains [teks]")
                return
            
            text_filter = args[1]

            # Cek apakah ada filter tanggal
            if len(args) >= 4 and args[2] == 'date':
                # Parsing tanggal lokal
                start_date_str = args[3]
                print("Start Date Str:", start_date_str)
                start_local = datetime.strptime(start_date_str, "%Y%m%d").date()

                # Gunakan waktu lokal
                start_local = datetime.combine(start_local, datetime.min.time())

                # Jika ada rentang tanggal (YYYYMMDD YYYYMMDD)
                if len(args) == 5 and args[4].isdigit():
                    # Parsing tanggal lokal
                    end_date_str = args[4]
                    end_local = datetime.strptime(end_date_str, "%Y%m%d").date()

                    # Gunakan waktu lokal
                    end_local = datetime.combine(end_local, datetime.max.time())
                # Jika tidak ada rentang tanggal, gunakan tanggal awal
                elif len(args) == 4:
                    end_date_str = start_date_str
                    end_local = start_local.replace(hour=23, minute=59, second=59)
                
                else:
                    #Jika Tidak ada filter tanggal, error
                    await update.message.reply_text("Gunakan format:\n/exportdb contains [teks] date YYYYMMDD\n/exportdb contains [teks] date YYYYMMDD YYYYMMDD")
                    return
            # Jika setelah 'contains' ada kata selain 'date', error
            elif len(args) > 2 and args[2] != 'date':
                await update.message.reply_text("Gunakan format:\n/exportdb contains [teks] date YYYYMMDD\n/exportdb contains [teks] date YYYYMMDD YYYYMMDD")
                return
            
            else:
                # Jika tidak ada filter tanggal, gunakan semua data
                start_local = datetime(1970, 1, 1)
                end_local = datetime.now()
        
        elif args[0] == "date":
            # Perintah dengan filter tanggal
            if len(args) < 2:
                await update.message.reply_text("Gunakan format:\n/exportdb date YYYYMMDD\n/exportdb date YYYYMMDD YYYYMMDD")
                return

            # Parsing tanggal lokal
            start_date_str = args[1]
            start_local = datetime.strptime(start_date_str, "%Y%m%d").date()

            # Gunakan waktu lokal
            start_local = datetime.combine(start_local, datetime.min.time())

            # Jika ada rentang tanggal (YYYYMMDD YYYYMMDD)
            if len(args) == 3 and args[2].isdigit():
                # Parsing tanggal lokal
                end_date_str = args[2]
                end_local = datetime.strptime(end_date_str, "%Y%m%d").date()

                # Gunakan waktu lokal
                end_local = datetime.combine(end_local, datetime.max.time())
            # Jika tidak ada rentang tanggal, gunakan tanggal awal
            elif len(args) == 2:
                end_local = start_local.replace(hour=23, minute=59, second=59)
                end_date_str = start_date_str
            else:
                #Jika Tidak ada filter tanggal, error
                await update.message.reply_text("Gunakan format:\n/exportdb date YYYYMMDD\n/exportdb date YYYYMMDD YYYYMMDD")
                return
        
        elif args[0] == "all":
            # Perintah tanpa filter
            start_local = datetime(1970, 1, 1)
            end_local = datetime.now()
        
        else:
            await update.message.reply_text(
                "Gunakan format:\n"
                "/exportdb date YYYYMMDD\n"
                "/exportdb date YYYYMMDD YYYYMMDD\n"
                "/exportdb contains [teks]\n"
                "/exportdb contains [teks] date YYYYMMDD\n"
                "/exportdb contains [teks] date YYYYMMDD YYYYMMDD"
            )
            return

        # Query ke Supabase
        query = supabase.table('file_storage').select('*')

        # Filter berdasarkan teks
        if text_filter:
            query = query.ilike('file_code', f"%{text_filter}%")
        
        # Filter berdasarkan tanggal
        if start_local and end_local:
            query = query.gte('created_at', start_local.isoformat()).lte('created_at', end_local.isoformat())

        print(f"Start: {start_date_str}, End: {end_date_str}, Filter: {text_filter}")
        print("Start Local:", start_local, "End Local:", end_local)
        # Eksekusi query
        response = query.execute()

        # Jika tidak ada data
        if not response.data or not isinstance(response.data, list):
            await update.message.reply_text("Tidak ada data yang ditemukan.")
            return

        # Konversi ke DataFrame
        df = pd.DataFrame(response.data)

        # Format tanggal ke lokal
        df['created_at'] = df['created_at'].apply(lambda x: datetime.fromisoformat(x).strftime("%d-%m-%Y %H:%M:%S"))

        # Tambahkan kolom URL
        df['URL'] = "https://www.onimono.com/p/download.html?fileCode=" + df['file_code']

        # Ganti nama kolom (header) ke bahasa Indonesia
        df = df.rename(columns={
            'created_at': 'Tanggal',
            'file_code': 'Kode File',
            'file_id': 'ID File',
            'URL': 'Link Unduh'
        })

        # Pilih kolom yang relevan
        df = df[['Tanggal', 'Kode File', 'ID File', 'Link Unduh']]

        # Urutkan data berdasarkan tanggal
        df = df.sort_values(by='Tanggal')

        # Jika ada command 'Contains' urutkan berdasarkan Kode File
        if text_filter:
            df = df.sort_values(by='Kode File')

        # Buat file Excel
        wb = Workbook()
        ws = wb.active
        ws.title = "Data Onimono"

        # Tulis data ke worksheet dengan header
        for r in dataframe_to_rows(df, index=False, header=True):
            ws.append(r)

        # Sesuaikan lebar kolom
        for column in ws.columns:
            max_length = max(len(str(cell.value)) for cell in column if cell.value is not None)
            ws.column_dimensions[column[0].column_letter].width = max_length + 2

        # Simpan ke BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)

        # Tentukan nama file sesuai dengan filter
        if text_filter and start_date_str and end_date_str:
            filename = f"Data Onimono - Contains {text_filter} - {start_date_str} to {end_date_str}.xlsx"
        elif text_filter and start_date_str:
            filename = f"Data Onimono - Contains {text_filter} - {start_date_str}.xlsx"
        elif text_filter:
            filename = f"Data Onimono - Contains {text_filter}.xlsx"
        elif start_date_str and end_date_str:
            filename = f"Data Onimono - {start_date_str} to {end_date_str}.xlsx"
        elif start_date_str:
            filename = f"Data Onimono - {start_date_str}.xlsx"
        else:
            filename = "Data Onimono.xlsx"

        # Kirim file Excel
        await update.message.reply_document(
            document=output.getvalue(),
            filename=filename
        )
        print(f"Args: {args}, Start Local: {start_local}, End Local: {end_local}, Text Filter: {text_filter}")

    except ValueError:
        await update.message.reply_text("Format tanggal salah. Gunakan YYYYMMDD.")
        print(f"Args: {args}, Start Local: {start_local}, End Local: {end_local}, Text Filter: {text_filter}")
    except Exception as e:
        print("Error saat mengekspor database:", e)
        print(f"Args: {args}, Start Local: {start_local}, End Local: {end_local}, Text Filter: {text_filter}")
        await update.message.reply_text(f"Terjadi kesalahan saat mengekspor database: {str(e)}")