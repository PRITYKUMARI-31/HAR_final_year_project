const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000'; // Match backend URL

// Map class index to label
const actionClassMap = {
  0: 'Walking',
  1: 'Running',
  2: 'Jumping',
  3: 'Sitting',
  4: 'Standing',
  // Extend if needed
};

// Upload video file
export async function recognizeAction(videoFile) {
  const formData = new FormData();
  formData.append('file', videoFile);

  try {
    const response = await fetch(API_BASE_URL + '/predict', {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Request failed');
    }

    const actionName = actionClassMap[data.predicted_class] || 'Unknown Action';
    return actionName;
  } catch (error) {
    console.error('Error in recognizeAction:', error);
    throw error;
  }
}

// Predict from YouTube URL
export async function recognizeActionFromUrl(youtubeUrl) {
  try {
    const response = await fetch(API_BASE_URL + '/predict-url', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: youtubeUrl }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || data.error || 'Request failed');
    }

    const actionName = actionClassMap[data.predicted_class] || 'Unknown Action';
    return actionName;
  } catch (error) {
    console.error('Error in recognizeActionFromUrl:', error);
    throw error;
  }
}
