import re
from fake_useragent import UserAgent

# Inisialisasi User Agent Rotator
ua = UserAgent()

def get_random_headers():
    """Menghasilkan headers acak agar terlihat seperti manusia"""
    return {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.douyin.com/",
        "Upgrade-Insecure-Requests": "1"
    }

def clean_douyin_url(text: str) -> str:
    """Mengambil hanya URL dari teks yang bercampur tulisan China"""
    # Regex pattern untuk menangkap URL douyin (v.douyin atau www.douyin)
    pattern = r"(https?://(?:v|www)\.douyin\.com/[A-Za-z0-9/]+)"
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    return text # Kembalikan aslinya jika tidak ketemu pattern (nanti divalidasi lagi)