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

# Load environment variables
load_dotenv()
MODEL_URL = os.getenv("MODEL_URL")
MODEL_PATH = os.getenv("MODEL_PATH", "best_model.h5")

# Download model if not found locally
if not os.path.exists(MODEL_PATH):
    if MODEL_URL:
        print(f"[INFO] Downloading model from {MODEL_URL}...")
        try:
            response = requests.get(MODEL_URL)
            response.raise_for_status()
            with open(MODEL_PATH, "wb") as f:
                f.write(response.content)
            print(f"[INFO] Model downloaded and saved to {MODEL_PATH}")
        except Exception as e:
            raise RuntimeError(f"Failed to download model: {str(e)}")
    else:
        raise RuntimeError(f"Model not found at {MODEL_PATH} and no MODEL_URL provided.")

# Load the model
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    print("[INFO] Model loaded successfully.")
except Exception as e:
    raise RuntimeError(f"Failed to load model: {str(e)}")

# Constants
IMAGE_HEIGHT, IMAGE_WIDTH = 64, 64
SEQUENCE_LENGTH = 20

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for all origins (configure appropriately in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check route
@app.get("/healthz")
def health_check():
    return {"status": "ok"}

# Error handler
@app.exception_handler(Exception)
async def handle_all_exceptions(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": "Internal server error", "detail": str(exc)})

# Request body for URL predictions
class UrlRequest(BaseModel):
    url: str

# Frame extractor
def extract_frames(video_path: str) -> np.ndarray:
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    step = max(total_frames // SEQUENCE_LENGTH, 1)
    frames = []

    for i in range(SEQUENCE_LENGTH):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i * step)
        success, frame = cap.read()
        if not success:
            break
        frame = cv2.resize(frame, (IMAGE_HEIGHT, IMAGE_WIDTH)) / 255.0
        frames.append(frame)

    cap.release()
    return np.array(frames)

# Upload video file for prediction
@app.post("/predict")
async def predict_action(file: UploadFile = File(...)):
    temp_file = NamedTemporaryFile(delete=False)
    try:
        temp_file.write(await file.read())
        temp_file.close()
        frames = extract_frames(temp_file.name)
        if len(frames) != SEQUENCE_LENGTH:
            return JSONResponse(status_code=400, content={"error": "Not enough frames extracted from the video."})

        input_tensor = np.expand_dims(frames, axis=0)
        prediction = model.predict(input_tensor)
        predicted_class = int(np.argmax(prediction))
        return {"predicted_class": predicted_class}
    finally:
        os.unlink(temp_file.name)

# Predict action from YouTube URL
@app.post("/predict-url")
async def predict_action_from_url(request: UrlRequest):
    ydl_opts = {
        "format": "best[ext=mp4]/best",
        "outtmpl": "temp_video.%(ext)s",
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=True)
            video_path = ydl.prepare_filename(info)
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": f"Failed to download video: {str(e)}"})

    try:
        frames = extract_frames(video_path)
        if len(frames) != SEQUENCE_LENGTH:
            return JSONResponse(status_code=400, content={"error": "Not enough frames extracted from the video."})

        input_tensor = np.expand_dims(frames, axis=0)
        prediction = model.predict(input_tensor)
        predicted_class = int(np.argmax(prediction))
        return {"predicted_class": predicted_class}
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)

# Uvicorn entry point
if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)
