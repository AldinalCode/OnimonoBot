from config import supabase

async def admins(user_id):
    """Periksa apakah pengguna adalah admin."""
    try:
        response = supabase.table('admins').select('*').eq('user_id', user_id).execute()
        return len(response.data) > 0
    except Exception as e:
        print("Error Supabase:", e)
        return False