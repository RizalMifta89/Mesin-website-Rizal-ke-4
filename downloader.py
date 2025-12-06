import re
import random
import httpx
import tls_client
from fake_useragent import UserAgent
from curl_cffi import requests as cffi_requests

ua = UserAgent(browsers=['chrome', 'firefox', 'safari'], os='windows', platforms='pc')

def get_random_ua():
    with open("user_agents.txt", "r") as f:
        lines = f.read().strip().splitlines()
    return random.choice(lines)

def extract_video_id(url: str) -> str:
    patterns = [
        r'douyin\.com/video/(\d+)',
        r'douyin\.com/aweme/(\d+)',
        r'iesdouyin\.com.*?/(\d{19})',
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    raise ValueError("Video ID tidak ditemukan")

async def download_douyin(url: str) -> dict:
    video_id = extract_video_id(url)

    headers = {
        "User-Agent": get_random_ua(),
        "Referer": "https://www.douyin.com/",
        "Accept": "application/json",
        "Accept-Language": "id-ID,id;q=0.9,en;q=0.8",
    }

    # Gunakan tls-client (paling susah dideteksi 2025)
    session = tls_client.Session(
        client_identifier="chrome_131",
        random_tls_extension_order=True
    )

    # Bypass awal dengan curl-cffi (imitasi browser beneran)
    try:
        resp = cffi_requests.get(
            f"https://www.douyin.com/video/{video_id}",
            headers=headers,
            impersonate="chrome124",
            timeout=20
        )
    except:
        resp = session.get(f"https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id={video_id}&device_platform=webapp&aid=6383", headers=headers)

    # Fallback ke API publik yang masih hidup 2025
    api_url = f"https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id={video_id}&version_code=160904&device_platform=webapp&aid=6383"

    r = session.get(api_url, headers=headers, timeout=30)
    if r.status_code != 200:
        raise Exception("Blocked atau video private")

    data = r.json()

    item = data['aweme_detail']

    return {
        "desc": item.get("desc", ""),
        "cover": item["video"]["cover"]["url_list"][0],
        "no_watermark": item["video"]["play_addr"]["url_list"][0].replace("playwm", "play"),  # tanpa watermark
        "no_watermark_raw": item["video"]["bit_rate"][0]["play_addr"]["url_list"][0] if item["video"]["bit_rate"] else None,
        "watermark": item["video"]["play_addr"]["url_list"][0],
        "music": item["music"]["play_url"]["url_list"][0],
        "author": item["author"]["nickname"]
    }