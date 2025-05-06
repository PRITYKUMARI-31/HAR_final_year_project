const API_BASE_URL = process.env.REACT_APP_API_URL;

console.log("API Base URL:", API_BASE_URL);

const actionClassMap = {
  0: 'BenchPress',
  1: 'GolfSwing',
  2: 'JugglingBalls',
  3: 'HighJump',
  4: 'Lunges',
  5: 'PizzaTossing',
};

export async function recognizeAction(videoFile) {
  const formData = new FormData();
  formData.append('file', videoFile);

  try {
    const response = await fetch(`${API_BASE_URL}/predict`, {
      method: 'POST',
      body: formData,
    });

    const contentType = response.headers.get("content-type");
    const data = contentType?.includes("application/json")
      ? await response.json()
      : { error: await response.text() };

    if (!response.ok) {
      throw new Error(data.error || 'Upload failed');
    }

    return actionClassMap[data.predicted_class] || 'Unknown Action';
  } catch (error) {
    console.error('Error in recognizeAction:', error);
    throw error;
  }
}

export async function recognizeActionFromUrl(youtubeUrl) {
  try {
    const response = await fetch(`${API_BASE_URL}/predict-url`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: youtubeUrl }),
    });

    const contentType = response.headers.get("content-type");
    const data = contentType?.includes("application/json")
      ? await response.json()
      : { error: await response.text() };

    if (!response.ok) {
      throw new Error(data.error || 'Request failed');
    }

    return actionClassMap[data.predicted_class] || 'Unknown Action';
  } catch (error) {
    console.error('Error in recognizeActionFromUrl:', error);
    throw error;
  }
}
