/**
 * Content Preview Component
 * @author Fahed Mlaiel <mlaiel@live.de>
 */

'use client';

import { useState } from 'react';

interface ContentPreviewProps {
  content: any;
  onClose: () => void;
}

export function ContentPreview({ content, onClose }: ContentPreviewProps) {
  const [activeTab, setActiveTab] = useState('essential');

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[80vh] overflow-hidden">
        <div className="flex justify-between items-center p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">Content Preview</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>
        
        <div className="p-6">
          <div className="flex space-x-4 mb-6 border-b">
            <button
              onClick={() => setActiveTab('essential')}
              className={`py-2 px-4 border-b-2 ${
                activeTab === 'essential' 
                  ? 'border-blue-500 text-blue-600' 
                  : 'border-transparent text-gray-500'
              }`}
            >
              Essential Information
            </button>
            <button
              onClick={() => setActiveTab('professional')}
              className={`py-2 px-4 border-b-2 ${
                activeTab === 'professional' 
                  ? 'border-blue-500 text-blue-600' 
                  : 'border-transparent text-gray-500'
              }`}
            >
              Professional Details
            </button>
          </div>

          <div className="space-y-4">
            {activeTab === 'essential' && (
              <div>
                <h3 className="font-medium text-gray-900 mb-2">Essential Information</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium">Name:</span> {content.name}
                  </div>
                  <div>
                    <span className="font-medium">Type:</span> {content.type}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ContentPreview;
