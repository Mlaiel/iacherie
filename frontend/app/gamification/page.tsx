'use client';
import Link from 'next/link';
import { ArrowLeft, Trophy } from 'lucide-react';
import { useEffect, useState } from 'react';

export default function GamificationPage() {
  const [isClient, setIsClient] = useState(false);
  
  useEffect(() => {
    setIsClient(true);
  }, []);

  // Éviter l'erreur d'hydration en affichant un placeholder jusqu'au chargement client
  if (!isClient) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="bg-white shadow border-b">
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex items-center space-x-4">
              <Link href="/" className="text-gray-600 hover:text-blue-600">
                <ArrowLeft className="h-5 w-5" />
              </Link>
              <Trophy className="h-8 w-8 text-amber-600" />
              <h1 className="text-2xl font-bold">Gamification</h1>
            </div>
          </div>
        </div>
        
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Chargement...</h2>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center space-x-4">
            <Link href="/" className="text-gray-600 hover:text-blue-600">
              <ArrowLeft className="h-5 w-5" />
            </Link>
            <Trophy className="h-8 w-8 text-amber-600" />
            <h1 className="text-2xl font-bold">Gamification</h1>
          </div>
        </div>
      </div>
      
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Statistiques</h2>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">12</div>
              <div className="text-sm text-gray-600">Niveau</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">2847</div>
              <div className="text-sm text-gray-600">XP</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600">156</div>
              <div className="text-sm text-gray-600">Rang</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
