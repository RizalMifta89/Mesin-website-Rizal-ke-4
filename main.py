from fastapi import FastAPI, Query
from fastapi.responses import RedirectResponse
from pydantic import HttpUrl
import asyncio
from downloader import analyze_douyin

app = FastAPI(title="Douyin Downloader API by Rizal")

@app.get("/")
async def home():
    return {"message": "Douyin Downloader API siap!"}

@app.get("/analyze")
async def analyze(url: str = Query(...)):
    try:
        info = await analyze_douyin(url)
        return info
    except Exception as e:
        return {"error": str(e)}

@app.get("/download")
async def download(url: str = Query(...), type: str = "nowm"):
    try:
        info = await analyze_douyin(url)
        
        if type == "nowm" and info["no_watermark"]:
            return RedirectResponse(info["no_watermark"])
        elif type == "raw" and info["raw"]:
            return RedirectResponse(info["raw"])
        elif type == "nowm_sd" and info["no_watermark_sd"]:
_ByPass
            return RedirectResponse(info["no_watermark_sd"])
        elif type == "music":
            return RedirectResponse(info["music"])
        else:
            return {"error": "Link untuk tipe ini tidak tersedia"}
    except Exception as e:
        return {"error": str(e)}