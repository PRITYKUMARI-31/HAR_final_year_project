import React, { useState, useRef } from 'react';
import { recognizeAction, recognizeActionFromUrl } from '../services';

function RecognitionPage() {
  const [videoSrc, setVideoSrc] = useState(null);
  const [videoFile, setVideoFile] = useState(null);
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [actionName, setActionName] = useState('');
  const videoRef = useRef(null);

  const handleVideoUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const videoURL = URL.createObjectURL(file);
      setVideoSrc(videoURL);
      setVideoFile(file);
      setActionName('');
      setYoutubeUrl('');
    }
  };

  const handleYoutubeUrlChange = (event) => {
    setYoutubeUrl(event.target.value);
    setActionName('');
    setVideoSrc(null);
    setVideoFile(null);
  };

  const recognizeActionHandler = async () => {
    if (videoFile) {
      setActionName('Recognizing...');
      try {
        const result = await recognizeAction(videoFile);
        setActionName(result);
      } catch (error) {
        alert('Error recognizing action: ' + error.message);
        setActionName('');
      }
    } else if (youtubeUrl) {
      setActionName('Recognizing...');
      try {
        const result = await recognizeActionFromUrl(youtubeUrl);
        setActionName(result);
      } catch (error) {
        alert('Error recognizing action: ' + error.message);
        setActionName('');
      }
    } else {
      alert('Please upload a video or enter a YouTube URL.');
    }
  };

  return (
    <div className="container mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold mb-6 text-center">Human Action Recognition</h1>
      <div className="flex flex-col items-center space-y-6">
        <input
          type="file"
          accept="video/*"
          onChange={handleVideoUpload}
          className="mb-4"
        />
        <input
          type="text"
          placeholder="Paste YouTube video URL here"
          value={youtubeUrl}
          onChange={handleYoutubeUrlChange}
          className="mb-4 px-4 py-2 border rounded w-full max-w-md"
        />
        {videoSrc && (
          <video
            ref={videoRef}
            src={videoSrc}
            controls
            autoPlay
            className="rounded-lg shadow-lg"
            style={{ width: '640px', height: '360px', objectFit: 'contain' }}
          />
        )}
        <button
          onClick={recognizeActionHandler}
          className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 transition"
        >
          actionName
        </button>
        {actionName && (
          <p className="mt-4 text-xl font-semibold text-gray-800">
            Recognized Action: {actionName}
          </p>
        )}
      </div>
    </div>
  );
}

export default RecognitionPage;
