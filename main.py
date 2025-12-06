from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from downloader import download_douyin
import asyncio

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Douyin Downloader API by Rizal", docs_url="/docs")

app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

@app.get("/")
async def root():
    return {"message": "Douyin Downloader API aktif! Gunakan /download?url="}

@app.get("/download")
@limiter.limit("30/minute")  # anti spam + anti block
async def download(url: str):
    try:
        data = await download_douyin(url)
        return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))