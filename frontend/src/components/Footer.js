import React from 'react';

function Footer() {
  return (
    <footer className="bg-gray-800 text-white py-4 mt-10">
      <div className="container mx-auto px-4 text-center">
        &copy; {new Date().getFullYear()} Human Action Recognition Project. All rights reserved.
      </div>
    </footer>
  );
}

export default Footer;