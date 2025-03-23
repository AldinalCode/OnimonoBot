import uuid

def generate_file_code(file_name):
    """Generate file_code berdasarkan nama file dan kode unik."""
    # Potong ekstensi file
    base_name = file_name.rsplit('.', 1)[0]  # Ambil nama tanpa ekstensi
    unique_code = str(uuid.uuid4())[:6].upper()  # Generate kode unik 6 karakter (uppercase)
    return f"{base_name}-{unique_code}"