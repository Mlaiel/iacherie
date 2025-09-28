'use client';
import Link from 'next/link';
import { ArrowLeft, Globe, ArrowRight } from 'lucide-react';

export default function TranslationPage() {
  return (
    <div className="min-h-screen bg-blue-50">
      <div className="bg-white shadow border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center space-x-4">
            <Link href="/" className="text-gray-600 hover:text-blue-600">
              <ArrowLeft className="h-5 w-5" />
            </Link>
            <Globe className="h-8 w-8 text-blue-600" />
            <h1 className="text-2xl font-bold">Traduction IA</h1>
          </div>
        </div>
      </div>
      
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Traducteur 644 langues</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
            <div>
              <label className="block text-sm font-medium mb-2">Langue source</label>
              <select className="w-full p-3 border rounded-lg">
                <option>Français</option>
                <option>Anglais</option>
                <option>Espagnol</option>
              </select>
              <textarea 
                placeholder="Texte à traduire..."
                className="w-full p-3 border rounded-lg mt-4 resize-none"
                rows={4}
              />
            </div>
            
            <div className="flex justify-center">
              <ArrowRight className="h-8 w-8 text-blue-600" />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Langue cible</label>
              <select className="w-full p-3 border rounded-lg">
                <option>Anglais</option>
                <option>Français</option>
                <option>Espagnol</option>
              </select>
              <div className="w-full p-3 border rounded-lg mt-4 min-h-24 bg-gray-50">
                <p className="text-gray-500">Traduction apparaîtra ici...</p>
              </div>
            </div>
          </div>
          
          <button className="w-full mt-6 bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700">
            Traduire
          </button>
        </div>
      </div>
    </div>
  );
}
