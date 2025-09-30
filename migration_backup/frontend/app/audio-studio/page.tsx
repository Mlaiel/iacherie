'use client';
import Link from 'next/link';
import { ArrowLeft, Music, Play } from 'lucide-react';

export default function AudioStudioPage() {
  return (
    <div className="min-h-screen bg-purple-50">
      <div className="bg-white shadow border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center space-x-4">
            <Link href="/" className="text-gray-600 hover:text-purple-600">
              <ArrowLeft className="h-5 w-5" />
            </Link>
            <Music className="h-8 w-8 text-purple-600" />
            <h1 className="text-2xl font-bold">Audio Studio</h1>
          </div>
        </div>
      </div>
      
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Lecteur Audio</h2>
          <div className="space-y-4">
            <div className="bg-gray-100 rounded-lg p-4 h-32 flex items-center justify-center">
              <Play className="h-12 w-12 text-purple-600" />
            </div>
            <div className="flex items-center justify-center space-x-4">
              <button className="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700">
                Importer Audio
              </button>
              <button className="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700">
                Générer IA
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
