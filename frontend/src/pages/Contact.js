import React from 'react';

function Contact() {
  return (
    <>
      <div className="container mx-auto px-4 py-20 max-w-3xl text-center">
        <h1 className="text-4xl font-bold mb-6 text-gray-800">Contact Us</h1>
        <p className="text-lg text-gray-700 leading-relaxed">
          We are a team of 4 members under the guidance of<p className='font-bold'>Dr. Abhimanyu Sahu</p> from <p className='font-bold text-blue-600'>Motilal Nehru National Institute of Technology, Allahabad-Batch(2021-2025)</p>
        </p>
        <p className="text-lg text-gray-700 leading-relaxed mt-4">
          For any inquiries or feedback, please reach out to us via email or phone.
        </p>
        <p className="text-lg text-gray-700 leading-relaxed mt-2">
         <p className='font-bold'>Team Members:</p>
          madhvendra.20214086@mnnit.ac.in 
          <br />prity.20214293@mnnit.ac.in
          <br /> sabit.20214093@mnnit.ac.in
          <br /> mohit.20214133@mnnit.ac.in

        </p>
       
      </div>
    </>
  );
}

export default Contact;
