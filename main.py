from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from downloader import DouyinDownloader
from utils import clean_douyin_url

app = FastAPI()

# Konfigurasi CORS agar frontend bisa mengakses backend ini
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Dalam produksi, ganti "*" dengan domain frontend Anda
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLRequest(BaseModel):
    url: str

@app.get("/")
def read_root():
    return {"message": "Douyin Downloader API is Running - Powered by Gemini"}

@app.post("/api/process")
async def process_video(request: URLRequest):
    # 1. Bersihkan URL dari tulisan China
    clean_url = clean_douyin_url(request.url)
    
    if not clean_url:
        raise HTTPException(status_code=400, detail="URL tidak valid")

    # 2. Proses Download
    downloader = DouyinDownloader()
    try:
        result = await downloader.get_video_info(clean_url)
        if result.get("status") == "error":
             raise HTTPException(status_code=500, detail=result.get("message"))
        return result
    finally:
        await downloader.close()