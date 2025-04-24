import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Home from './pages/Home';
import PromptInput from './pages/PromptInput';
import ImagePreviewPage from './pages/ImagePreviewPage';
import LineageView from './pages/LineageView';

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Router>
        <header className="border-b border-gray-200 bg-white py-4 shadow-sm">
          <div className="container mx-auto flex items-center px-4">
            <a href="/" className="text-xl font-bold text-indigo-600">
              ImageFlow
            </a>
            <div className="ml-8 hidden items-center space-x-6 text-sm font-medium md:flex">
              <a href="/" className="text-gray-900 hover:text-indigo-600">Projects</a>
              <a href="/create" className="text-gray-500 hover:text-indigo-600">Create</a>
            </div>
          </div>
        </header>
        
        <main className="pb-16">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/create" element={<PromptInput />} />
            <Route path="/edit/:parentId" element={<PromptInput />} />
            <Route path="/preview/:id" element={<ImagePreviewPage />} />
            <Route path="/lineage/:id" element={<LineageView />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
        
        <footer className="fixed bottom-0 left-0 right-0 border-t border-gray-200 bg-white py-3 text-center text-sm text-gray-500">
          <div className="container mx-auto px-4">
            <p>© 2025 ImageFlow - Image Generation and Management System</p>
          </div>
        </footer>
      </Router>
    </div>
  );
}

export default App;