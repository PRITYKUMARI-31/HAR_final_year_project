import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

function Navbar({ overlay }) {
  const navigate = useNavigate();

  return (
    <nav
      className={`${
        overlay ? 'absolute top-0 left-0 w-full bg-transparent' : 'bg-white shadow-md'
      } z-20`}
    >
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <div
          className={`text-2xl font-bold cursor-pointer ${
            overlay ? 'text-white' : 'text-blue-600'
          }`}
          onClick={() => navigate('/')}
        >
          HAR App
        </div>
        <div className="space-x-6">
          <Link
            to="/"
            className={`hover:text-blue-600 transition ${
              overlay ? 'text-white' : 'text-gray-700'
            }`}
          >
            Home
          </Link>
          <Link
            to="/about"
            className={`hover:text-blue-600 transition ${
              overlay ? 'text-white' : 'text-gray-700'
            }`}
          >
            About
          </Link>
          <Link
            to="/contact"
            className={`hover:text-blue-600 transition ${
              overlay ? 'text-white' : 'text-gray-700'
            }`}
          >
            Contact
          </Link>
          <button
            onClick={() => navigate('/recognition')}
            className={`px-4 py-2 rounded hover:bg-blue-700 transition ${
              overlay ? 'bg-blue-600 text-white' : 'bg-blue-600 text-white'
            }`}
          >
            Upload Page
          </button>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
