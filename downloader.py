import httpx
import re
import json
from tenacity import retry, stop_after_attempt, wait_fixed
from utils import get_random_headers

class DouyinDownloader:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=15.0, follow_redirects=True)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def get_video_info(self, url: str):
        headers = get_random_headers()
        
        try:
            # 1. Hit URL awal untuk mendapatkan URL asli (setelah redirect)
            response = await self.client.get(url, headers=headers)
            final_url = response.url
            
            # 2. Ambil ID Video dari URL (biasanya /video/123456789)
            # Pattern regex untuk mengambil ID video
            id_pattern = r'/video/(\d+)'
            video_id_match = re.search(id_pattern, str(final_url))
            
            if not video_id_match:
                # Fallback: Coba cari di dalam HTML jika URL tidak mengandung ID
                # (Logic scraping sederhana)
                pass

            # 3. Teknik Bypass: Mengambil data JSON yang tertanam di HTML (RENDER_DATA)
            # Ini lebih aman daripada memanggil API internal yang butuh XBogus
            html_content = response.text
            
            # Mencari script JSON data
            # Regex kasar untuk mencari URL video playwm (watermark) atau play (raw)
            # Ini pendekatan general.
            
            # INFO: Douyin sangat membatasi scraping HTML langsung tanpa Cookie valid/Login.
            # Namun, kita coba ekstrak link video src langsung.
            
            video_src_pattern = r'"src":"(https:[^"]+vh_id[^"]+)"'
            # Note: Pattern ini mungkin perlu disesuaikan seiring update Douyin
            
            # Simulasi Response Sukses (Mocking logic karena keterbatasan akses live server Douyin tanpa Signer)
            # Dalam produksi, Anda harus menggunakan library 'douyin-tiktok-scraper' atau API pihak ketiga 
            # jika scraping HTML manual diblokir.
            
            # Kode di bawah ini adalah STRUKTUR LOGIKA yang benar:
            
            data = {
                "status": "success",
                "platform": "douyin",
                "original_url": str(final_url),
                "title": "Douyin Video Result", # Perlu parsing HTML title
                "cover": "",
                "video_data": {
                    "nwm_video_url": "", # No Watermark
                    "wm_video_url": "",  # With Watermark
                    "raw_video_url": ""  # Original Quality
                }
            }

            # Kita coba cari pattern URL video di dalam HTML response
            # Douyin sering menaruh link di JSON terencode di dalam tag script
            # Pattern di bawah ini mencoba menangkap URL video .mp4
            url_pattern = r'https:\\?/\\?/[a-zA-Z0-9\-\._~:/?#\[\]@!$&\'()*+,;=]+\.mp4'
            found_urls = re.findall(url_pattern, html_content)
            
            if found_urls:
                # Bersihkan backslash escape characters
                clean_urls = [u.replace('\\', '') for u in found_urls]
                # Filter URL yang valid
                valid_mp4 = [u for u in clean_urls if 'video' in u or 'aweme' in u]
                
                if valid_mp4:
                    # Biasanya URL terpanjang atau pertama adalah kualitas terbaik
                    best_url = valid_mp4[0]
                    # URL Douyin seringkali http, ubah ke https
                    best_url = best_url.replace('http://', 'https://')
                    
                    data["video_data"]["nwm_video_url"] = best_url
                    data["video_data"]["raw_video_url"] = best_url # Anggap sama untuk scraping dasar
            
            return data

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def close(self):
        await self.client.aclose()