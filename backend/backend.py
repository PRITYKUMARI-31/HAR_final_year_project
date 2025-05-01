from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn
import numpy as np
import tensorflow as tf
import cv2
import os
from tempfile import NamedTemporaryFile
import yt_dlp as youtube_dl

# Load .env file
load_dotenv()
MODEL_PATH = os.getenv("MODEL_PATH", "best_model.h5")
if not os.path.exists(MODEL_PATH):
    raise ValueError(f"Model file not found at {MODEL_PATH}")

IMAGE_HEIGHT, IMAGE_WIDTH = 64, 64
SEQUENCE_LENGTH = 20
model = tf.keras.models.load_model(MODEL_PATH)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UrlRequest(BaseModel):
    url: str

@app.get("/healthz")
def health_check():
    return {"status": "ok"}

@app.exception_handler(Exception)
async def handle_all_exceptions(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": "Internal server error", "detail": str(exc)})

@app.post("/predict")
async def predict_action(file: UploadFile = File(...)):
    temp = NamedTemporaryFile(delete=False)
    try:
        temp.write(await file.read())
        temp.close()
        frames = extract_frames(temp.name)
        if len(frames) != SEQUENCE_LENGTH:
            return JSONResponse(status_code=400, content={"error": "Not enough frames extracted from video."})
        inp = np.expand_dims(frames, axis=0)
        pred = model.predict(inp)
        return {"predicted_class": int(np.argmax(pred))}
    finally:
        if os.path.exists(temp.name):
            os.remove(temp.name)

@app.post("/predict-url")
async def predict_action_from_url(request: UrlRequest):
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': 'temp_video.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=True)
            video_path = ydl.prepare_filename(info)
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": f"Error downloading video: {str(e)}"})
    try:
        frames = extract_frames(video_path)
        if len(frames) != SEQUENCE_LENGTH:
            return JSONResponse(status_code=400, content={"error": "Not enough frames extracted from video."})
        inp = np.expand_dims(frames, axis=0)
        pred = model.predict(inp)
        return {"predicted_class": int(np.argmax(pred))}
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)

def extract_frames(video_path):
    frames = []
    vid = cv2.VideoCapture(video_path)
    total = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
    step = max(total // SEQUENCE_LENGTH, 1)
    for i in range(SEQUENCE_LENGTH):
        vid.set(cv2.CAP_PROP_POS_FRAMES, i * step)
        success, frame = vid.read()
        if not success:
            break
        frame = cv2.resize(frame, (IMAGE_HEIGHT, IMAGE_WIDTH)) / 255.0
        frames.append(frame)
    vid.release()
    return np.array(frames)

if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)
