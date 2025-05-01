from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn
import numpy as np
import tensorflow as tf
import cv2
import os
from tempfile import NamedTemporaryFile
import yt_dlp as youtube_dl

# Load .env file for environment variables
load_dotenv()

# Retrieve model path from environment variable or default to "best_model.h5"
MODEL_PATH = os.getenv("MODEL_PATH", "best_model.h5")
if not os.path.exists(MODEL_PATH):
    raise ValueError(f"Model file not found at {MODEL_PATH}")

# Constants for image resizing and sequence length
IMAGE_HEIGHT, IMAGE_WIDTH = 64, 64
SEQUENCE_LENGTH = 20

# Load the pre-trained model
model = tf.keras.models.load_model(MODEL_PATH)

# Initialize FastAPI app
app = FastAPI()

# Enable CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for testing purposes, refine for production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for URL input
class UrlRequest(BaseModel):
    url: str

# Endpoint to predict action from uploaded video file
@app.post("/predict")
async def predict_action(file: UploadFile = File(...)):
    temp = NamedTemporaryFile(delete=False)
    try:
        # Write the uploaded video file to a temporary location
        temp.write(await file.read())
        temp.close()

        frames = extract_frames(temp.name)
        if len(frames) != SEQUENCE_LENGTH:
            raise HTTPException(status_code=400, detail="Not enough frames extracted from video.")
        
        # Prepare input for the model and predict
        inp = np.expand_dims(frames, axis=0)
        pred = model.predict(inp)
        predicted_class = int(np.argmax(pred))  # Get the index of the highest predicted class
        return {"predicted_class": predicted_class}

    finally:
        # Ensure the temporary file is deleted
        if os.path.exists(temp.name):
            os.remove(temp.name)

# Endpoint to predict action from YouTube video URL
@app.post("/predict-url")
async def predict_action_from_url(request: UrlRequest):
    ydl_opts = {
        'format': 'best[ext=mp4]/best',  # Fetch the best MP4 format
        'outtmpl': 'temp_video.%(ext)s',  # Template for output video file name
        'quiet': True,
        'no_warnings': True,
    }

    try:
        # Download the video from the provided URL
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(request.url, download=True)
            video_path = ydl.prepare_filename(info_dict)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error downloading video: {e}")

    try:
        frames = extract_frames(video_path)
        if len(frames) != SEQUENCE_LENGTH:
            raise HTTPException(status_code=400, detail="Not enough frames extracted from video.")
        
        # Prepare input for the model and predict
        inp = np.expand_dims(frames, axis=0)
        pred = model.predict(inp)
        predicted_class = int(np.argmax(pred))  # Get the index of the highest predicted class
        return {"predicted_class": predicted_class}

    finally:
        # Clean up by deleting the downloaded video
        if os.path.exists(video_path):
            os.remove(video_path)

# Function to extract frames from a video file
def extract_frames(video_path):
    frames = []
    vid = cv2.VideoCapture(video_path)

    # Get total frame count in the video
    total_frames = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
    step = max(total_frames // SEQUENCE_LENGTH, 1)

    # Extract frames at intervals
    for i in range(SEQUENCE_LENGTH):
        vid.set(cv2.CAP_PROP_POS_FRAMES, i * step)
        success, frame = vid.read()
        if not success:
            break
        # Resize and normalize frame
        frame = cv2.resize(frame, (IMAGE_HEIGHT, IMAGE_WIDTH)) / 255.0
        frames.append(frame)
    
    vid.release()
    return np.array(frames)

# Entry point for running the app with uvicorn
if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)
