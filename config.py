from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

# Konfigurasi Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Konfigurasi Telegram
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)