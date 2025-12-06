import httpx
import re
import json
import tls_client
from fake_useragent import UserAgent
from urllib.parse import urlparse, parse_qs

ua = UserAgent(browsers=['chrome', 'firefox'], os=['windows', 'macos', 'linux'])

def get_session():
    session = tls_client.Session(
        client_identifier="chrome_124",  # paling aman 2025
        random_tls_extension_order=True
    )
    session.headers.update({
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Dest": "document",
        "Upgrade-Insecure-Requests": "1",
    })
    return session

async def analyze_douyin(url: str):
    session = get_session()
    
    # Redirect sampai dapat aweme_id
    resp = session.get(url, follow_redirects=True)
    real_url = str(resp.url)

    aweme_id = None
    if "/video/" in real_url:
        aweme_id = re.search(r"/video/(\d+)", real_url)
    elif "/photo/" in real_url:
        aweme_id = re.search(r"/photo/(\d+)", real_url)
    
    if not aweme_id:
        raise ValueError("Link Douyin tidak valid atau sudah dihapus")

    aweme_id = aweme_id.group(1)

    # API resmi Douyin (bypass X-Bogus, dll pakai tls-client)
    api_url = f"https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id={aweme_id}&device_platform=webapp&aid=6383"
    
    resp = session.get(api_url, timeout=20)
    data = resp.json()

    if data.get("status_code") != 0:
        raise ValueError("Video tidak ditemukan / private")

    aweme = data["aweme_detail"]

    return {
        "aweme_id": aweme_id,
        "desc": aweme.get("desc", ""),
        "author": aweme["author"]["nickname"],
        "cover": aweme["video"]["cover"]["url_list"][0],
        "no_watermark": aweme["video"]["play_addr"]["url_list"][0].replace("playwm", "play"),
        "raw": aweme["video"]["origin_play_addr"]["url_list"][0] if aweme["video"].get("origin_play_addr") else None,
        "no_watermark_sd": aweme["video"]["play_addr_lowbr"]["url_list"][0].replace("playwm", "play") if aweme["video"].get("play_addr_lowbr") else None,
        "music": aweme["music"]["play_url"]["url_list"][0]
    }