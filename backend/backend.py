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
import requests
import yt_dlp as youtube_dl

# 1. Load environment variables
load_dotenv()
MODEL_URL = os.getenv("MODEL_URL")           # e.g. https://bucket/.../best_model.h5
MODEL_PATH = os.getenv("MODEL_PATH", "best_model.h5")

# 2. Ensure the model file exists locally, downloading if needed
if not os.path.exists(MODEL_PATH):
    if MODEL_URL:
        resp = requests.get(MODEL_URL)
        resp.raise_for_status()
        with open(MODEL_PATH, "wb") as f:
            f.write(resp.content)
        print(f"Downloaded model to {MODEL_PATH}")
    else:
        raise RuntimeError(f"Model not found at {MODEL_PATH} and no MODEL_URL provided")

# 3. Load the Keras model once
model = tf.keras.models.load_model(MODEL_PATH)
print("Model loaded successfully.")

# 4. App constants
IMAGE_HEIGHT, IMAGE_WIDTH = 64, 64
SEQUENCE_LENGTH = 20

# 5. FastAPI setup
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

def extract_frames(video_path: str) -> np.ndarray:
    vid = cv2.VideoCapture(video_path)
    total = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
    step = max(total // SEQUENCE_LENGTH, 1)
    frames = []
    for i in range(SEQUENCE_LENGTH):
        vid.set(cv2.CAP_PROP_POS_FRAMES, i * step)
        ok, frame = vid.read()
        if not ok:
            break
        frame = cv2.resize(frame, (IMAGE_HEIGHT, IMAGE_WIDTH)) / 255.0
        frames.append(frame)
    vid.release()
    return np.array(frames)

@app.post("/predict")
async def predict_action(file: UploadFile = File(...)):
    tmp = NamedTemporaryFile(delete=False)
    try:
        tmp.write(await file.read())
        tmp.close()
        frames = extract_frames(tmp.name)
        if len(frames) != SEQUENCE_LENGTH:
            return JSONResponse(status_code=400, content={"error": "Not enough frames extracted"})
        inp = np.expand_dims(frames, axis=0)
        pred = model.predict(inp)
        return {"predicted_class": int(np.argmax(pred))}
    finally:
        os.unlink(tmp.name)

@app.post("/predict-url")
async def predict_action_from_url(req: UrlRequest):
    ydl_opts = {
        "format": "best[ext=mp4]/best",
        "outtmpl": "temp_video.%(ext)s",
        "quiet": True,
        "no_warnings": True,
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(req.url, download=True)
            path = ydl.prepare_filename(info)
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": f"Download failed: {e}"})

    try:
        frames = extract_frames(path)
        if len(frames) != SEQUENCE_LENGTH:
            return JSONResponse(status_code=400, content={"error": "Not enough frames extracted"})
        inp = np.expand_dims(frames, axis=0)
        pred = model.predict(inp)
        return {"predicted_class": int(np.argmax(pred))}
    finally:
        if os.path.exists(path):
            os.remove(path)

if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)
