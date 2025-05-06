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

# Load environment variables
load_dotenv()

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "best_model.h5")
CLASS_NAMES_PATH = os.path.join(BASE_DIR, "class_names.txt")

# Load model
if not os.path.exists(MODEL_PATH):
    raise RuntimeError(f"Model not found at {MODEL_PATH}")
model = tf.keras.models.load_model(MODEL_PATH)
print("[INFO] Model loaded successfully.")

# Load class names
if not os.path.exists(CLASS_NAMES_PATH):
    raise RuntimeError(f"class_names.txt not found at {CLASS_NAMES_PATH}")
with open(CLASS_NAMES_PATH, "r") as f:
    CLASS_NAMES = [line.strip() for line in f.readlines()]

# Constants
IMAGE_HEIGHT, IMAGE_WIDTH = 64, 64
SEQUENCE_LENGTH = 20

# Initialize FastAPI
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://action-recognition-frontend.onrender.com",
        "http://localhost:3000" 
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check route
@app.get("/healthz")
def health_check():
    return {"status": "ok"}

# Global error handler
@app.exception_handler(Exception)
async def handle_all_exceptions(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": "Internal server error", "detail": str(exc)})

# Pydantic model
class UrlRequest(BaseModel):
    url: str

# Frame extraction
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

# Prediction from file
@app.post("/predict")
async def predict_action(file: UploadFile = File(...)):
    tmp = NamedTemporaryFile(delete=False)
    try:
        tmp.write(await file.read())
        tmp.close()
        frames = extract_frames(tmp.name)
        if len(frames) != SEQUENCE_LENGTH:
            return JSONResponse(status_code=400, content={"error": "Not enough frames extracted from the video."})
        input_tensor = np.expand_dims(frames, axis=0)
        prediction = model.predict(input_tensor)
        predicted_index = int(np.argmax(prediction))
        return {
            "predicted_class": predicted_index,
            "label": CLASS_NAMES[predicted_index]
        }
    finally:
        os.unlink(tmp.name)

# Prediction from URL
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
            video_path = ydl.prepare_filename(info)
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": f"Failed to download video: {str(e)}"})

    try:
        frames = extract_frames(video_path)
        if len(frames) != SEQUENCE_LENGTH:
            return JSONResponse(status_code=400, content={"error": "Not enough frames extracted from the video."})
        input_tensor = np.expand_dims(frames, axis=0)
        prediction = model.predict(input_tensor)
        predicted_index = int(np.argmax(prediction))
        return {
            "predicted_class": predicted_index,
            "label": CLASS_NAMES[predicted_index]
        }
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)

# Local entry
if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)
