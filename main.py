from telegram.ext import Application, MessageHandler, CommandHandler, filters

from config import TOKEN

from handler.document import handle_document
from handler.download import handle_download
from handler.export import handle_exportdb

def main():
    application = Application.builder().token(TOKEN).build()

    # Handler untuk dokumen
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    # Handler untuk download
    application.add_handler(CommandHandler("download", handle_download))

    # Handler untuk exportdb
    application.add_handler(CommandHandler("exportdb", handle_exportdb))

    # Jalankan bot
    application.run_polling()

if __name__ == '__main__':
    main()