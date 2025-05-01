import React from 'react';

function About() {
  return (
    <div className="container mx-auto px-4 py-20 max-w-3xl">
      <h1 className="text-4xl font-bold mb-6 text-gray-800">About Our Human Action Recognition Project</h1>
      <p className="text-lg text-gray-700 leading-relaxed">
        This project focuses on human action recognition using advanced machine learning techniques, including convolutional neural networks (CNN) and long short-term memory (LSTM) models. Our approach leverages active learning to improve model accuracy and efficiency.
      </p>
      <p className="text-lg text-gray-700 leading-relaxed mt-4">
        The system processes video data to identify and classify various human actions, enabling applications in surveillance, healthcare, sports analysis, and human-computer interaction. By combining CNN and LSTM architectures, the model captures both spatial and temporal features of actions.
      </p>
      <p className="text-lg text-gray-700 leading-relaxed mt-4">
        Our goal is to provide a robust and scalable solution for real-time human activity recognition, facilitating enhanced automation and intelligent decision-making in diverse domains.
      </p>
    </div>
  );
}

export default About;
