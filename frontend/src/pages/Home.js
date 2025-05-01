import React from 'react';
import { useNavigate } from 'react-router-dom';

function Home() {
  const navigate = useNavigate();

  return (
    <div
      className="relative h-screen text-white flex flex-col justify-center items-center px-4"
      style={{
        backgroundImage:
          "url('https://images.pexels.com/photos/3184291/pexels-photo-3184291.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940')",
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }}
    >
      {/* Dark overlay */}
      <div className="absolute inset-0 bg-black opacity-60 z-0"></div>

      {/* Main content */}
      <main className="relative z-10 max-w-3xl text-center mt-32">
        <h1 className="text-6xl font-extrabold mb-6">Human Action Recognition</h1>
        <p className="text-xl mb-10">
          Our project uses advanced machine learning techniques, including CNN and LSTM models with active learning, to accurately recognize human actions from video data. This enables applications in surveillance, healthcare, sports analysis, and more.
        </p>
        <button
          onClick={() => navigate('/recognition')}
          className="bg-blue-600 px-6 py-3 rounded text-white text-lg font-semibold hover:bg-blue-700 transition"
        >
          Upload Page
        </button>
      </main>
    </div>
  );
}

export default Home;
