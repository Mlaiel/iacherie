'use client';
import Link from 'next/link';
import { ArrowLeft, Brain, Sparkles, Send, Loader2, Copy, Trash2 } from 'lucide-react';
import { useState, useEffect } from 'react';

export default function AIStudioPage() {
  const [prompt, setPrompt] = useState('');
  const [contentType, setContentType] = useState('image');
  const [result, setResult] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [aiServices, setAiServices] = useState<string[]>([]);
  const [selectedService, setSelectedService] = useState('image-generation');

  // Téléchargement optimisé via lien direct - plus de complexité JS

  useEffect(() => {
    fetchAIServices();
  }, []);

  const fetchAIServices = async () => {
    // FORCER LES SERVICES ACTIFS IMMEDIATEMENT - TOUS LES SERVICES IA
    const defaultServices = [
      'content-generation',   // 📝 Génération de contenu/articles
      'text-analysis',        // 🔍 Analyse de texte/sentiment  
      'translation',          // 🌍 Traduction 644 langues
      'summarization',        // 📄 Résumé automatique
      'audio-generation',     // 🎵 Génération audio/musique
      'image-generation',     // 🖼️ Génération d'images IA
      'video-generation',     // 🎬 Génération vidéo IA
      'code-generation'       // 💻 Génération de code
    ];
    setAiServices(defaultServices);
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'}/api/ai/services`);
      if (response.ok) {
        const data = await response.json();
        setAiServices(data.services || defaultServices);
      }
    } catch (error) {
      console.log('Backend services check failed, using default services:', error);
      // Garder les services par défaut déjà définis
    }
  };

  const generateContent = async () => {
    if (!prompt.trim()) return;
    
    setLoading(true);
    try {
      // APPEL À L'API FRONTEND QUI SE CONNECTE AU BACKEND RÉEL
      const response = await fetch('/api/ai/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: prompt,
          type: selectedService,
          options: {
            max_length: 500,
            temperature: 0.7,
            model: 'gpt-4'
          }
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.data) {
          // Traitement spécifique selon le type de contenu
          if (data.data.content_type === 'image' || data.data.content_type === 'image-generation') {
            // Pour les images, afficher l'image et les métadonnées
            setResult(`✅ Image générée avec succès !\n\n🎨 ${data.data.generated_content}\n📐 Dimensions: ${data.data.dimensions}\n⚡ Temps: ${data.data.processing_time}\n🤖 Agent: ${data.data.agent_used}\n📥 ID: ${data.data.id}\n\n[IMAGE_URL:${data.data.image_url || data.data.image_data}]\n[DOWNLOAD_URL:${data.data.download_url}]\n[CONTENT_TYPE:${data.data.content_type}]`);
          } else if (data.data.content_type === 'audio' || data.data.content_type === 'audio-generation') {
            // Pour l'audio
            setResult(`✅ Audio généré avec succès !\n\n🎵 ${data.data.generated_content}\n⏱️ Durée: ${data.data.duration}\n🎚️ Format: ${data.data.format}\n⚡ Temps: ${data.data.processing_time}\n🤖 Agent: ${data.data.agent_used}\n📥 ID: ${data.data.id}\n\n[AUDIO_URL:${data.data.audio_url}]\n[DOWNLOAD_URL:${data.data.download_url}]\n[CONTENT_TYPE:${data.data.content_type}]`);
          } else if (data.data.content_type === 'video' || data.data.content_type === 'video-generation') {
            // Pour la vidéo
            setResult(`✅ Vidéo générée avec succès !\n\n🎬 ${data.data.generated_content}\n📺 Résolution: ${data.data.resolution}\n⏱️ Durée: ${data.data.duration}\n⚡ Temps: ${data.data.processing_time}\n🤖 Agent: ${data.data.agent_used}\n📥 ID: ${data.data.id}\n\n[VIDEO_URL:${data.data.video_url}]\n[THUMBNAIL_URL:${data.data.thumbnail_url}]\n[DOWNLOAD_URL:${data.data.download_url}]\n[CONTENT_TYPE:${data.data.content_type}]`);
          } else if (data.data.content_type === 'text-analysis') {
            // Pour l'analyse de texte
            setResult(`✅ Analyse de texte terminée !\n\n🔍 ${data.data.generated_content}\n📊 Résultats: ${data.data.analysis_results || 'Analyse complète'}\n⚡ Temps: ${data.data.processing_time}\n🤖 Agent: ${data.data.agent_used}\n📥 ID: ${data.data.id}\n\n[CONTENT_TYPE:${data.data.content_type}]`);
          } else if (data.data.content_type === 'translation') {
            // Pour la traduction
            setResult(`✅ Traduction réalisée !\n\n🌍 ${data.data.generated_content}\n🔄 De: ${data.data.source_language || 'Auto'} → Vers: ${data.data.target_language || 'Français'}\n⚡ Temps: ${data.data.processing_time}\n🤖 Agent: ${data.data.agent_used}\n📥 ID: ${data.data.id}\n\n[CONTENT_TYPE:${data.data.content_type}]`);
          } else if (data.data.content_type === 'summarization') {
            // Pour le résumé
            setResult(`✅ Résumé généré !\n\n📄 ${data.data.generated_content}\n📊 Mots originaux: ${data.data.original_words || 'N/A'} → Résumé: ${data.data.summary_words || 'N/A'}\n⚡ Temps: ${data.data.processing_time}\n🤖 Agent: ${data.data.agent_used}\n📥 ID: ${data.data.id}\n\n[CONTENT_TYPE:${data.data.content_type}]`);
          } else if (data.data.content_type === 'code-generation') {
            // Pour la génération de code
            setResult(`✅ Code généré !\n\n💻 ${data.data.generated_content}\n⚙️ Langage: ${data.data.programming_language || 'Python'}\n📊 Lignes: ${data.data.lines_count || 'N/A'}\n⚡ Temps: ${data.data.processing_time}\n🤖 Agent: ${data.data.agent_used}\n📥 ID: ${data.data.id}\n\n[CONTENT_TYPE:${data.data.content_type}]`);
          } else {
            // Pour le texte et autres types
            setResult(`✅ Contenu généré avec succès !\n\n${data.data.generated_content}\n\n⚡ Temps: ${data.data.processing_time}\n🤖 Agent: ${data.data.agent_used}\n📥 ID: ${data.data.id || 'N/A'}\n\n[DOWNLOAD_URL:${data.data.download_url || '#'}]\n[CONTENT_TYPE:${data.data.content_type}]`);
          }
        } else {
          setResult(`❌ Erreur: ${data.error || 'Réponse invalide'}`);
        }
      } else {
        const errorData = await response.json();
        setResult(`❌ Erreur API: ${errorData.error || 'Erreur inconnue'}`);
      }
    } catch (error) {
      setResult(`❌ Erreur de connexion: ${error instanceof Error ? error.message : 'Erreur inconnue'}`);
    } finally {
      setLoading(false);
    }
  };



  const copyToClipboard = () => {
    navigator.clipboard.writeText(result);
  };

  return (
    <div className="min-h-screen bg-indigo-50">
      <div className="bg-white shadow border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center space-x-4">
            <Link href="/" className="text-gray-600 hover:text-indigo-600">
              <ArrowLeft className="h-5 w-5" />
            </Link>
            <Brain className="h-8 w-8 text-indigo-600" />
            <h1 className="text-2xl font-bold">IA Studio Pro</h1>
            <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">
              {aiServices.length} services actifs
            </span>
          </div>
        </div>
      </div>
      
      <div className="max-w-7xl mx-auto px-6 py-8 grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Panneau de configuration */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Sparkles className="h-6 w-6 text-indigo-600 mr-2" />
            Configuration IA
          </h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Service IA</label>
              <select 
                value={selectedService}
                onChange={(e) => setSelectedService(e.target.value)}
                className="w-full p-3 border rounded-lg"
              >
                <option value="content-generation">📝 Content Generation - Écrire articles, posts, blogs</option>
                <option value="text-analysis">🔍 Text Analysis - Analyser sentiment, émotions, mots-clés</option>
                <option value="translation">🌍 Translation - Traduire entre 644 langues</option>
                <option value="summarization">📄 Summarization - Résumer longs textes/documents</option>
                <option value="audio-generation">🎵 Audio Generation - Créer musique, voix, sons</option>
                <option value="image-generation">🖼️ Image Generation - Générer images IA créatives</option>
                <option value="video-generation">🎬 Video Generation - Créer vidéos IA animées</option>
                <option value="code-generation">💻 Code Generation - Générer code Python, JS, etc.</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Prompt</label>
              <textarea 
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Décrivez ce que vous voulez créer..."
                className="w-full p-4 border rounded-lg resize-none"
                rows={6}
              />
            </div>
            
            <button 
              onClick={generateContent}
              disabled={loading || !prompt.trim()}
              className="w-full bg-indigo-600 text-white py-3 px-6 rounded-lg hover:bg-indigo-700 flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  <span>Génération en cours...</span>
                </>
              ) : (
                <>
                  <Send className="h-5 w-5" />
                  <span>Générer avec IA</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Panneau de résultat */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Résultat généré</h2>
          <div className="min-h-64 p-4 border rounded-lg bg-gray-50">
            {result ? (
              <div>
                {(() => {
                  // Extraction des différents types d'URLs et métadonnées
                  const imageUrlMatch = result.match(/\[IMAGE_URL:(.*?)\]/);
                  const audioUrlMatch = result.match(/\[AUDIO_URL:(.*?)\]/);
                  const videoUrlMatch = result.match(/\[VIDEO_URL:(.*?)\]/);
                  const thumbnailUrlMatch = result.match(/\[THUMBNAIL_URL:(.*?)\]/);
                  const downloadUrlMatch = result.match(/\[DOWNLOAD_URL:(.*?)\]/);
                  const contentTypeMatch = result.match(/\[CONTENT_TYPE:(.*?)\]/);
                  
                  // Nettoyer le texte des balises
                  let cleanText = result
                    .replace(/\[IMAGE_URL:.*?\]/g, '')
                    .replace(/\[AUDIO_URL:.*?\]/g, '')
                    .replace(/\[VIDEO_URL:.*?\]/g, '')
                    .replace(/\[THUMBNAIL_URL:.*?\]/g, '')
                    .replace(/\[DOWNLOAD_URL:.*?\]/g, '')
                    .replace(/\[CONTENT_TYPE:.*?\]/g, '')
                    .trim();
                  
                  const downloadUrl = downloadUrlMatch ? downloadUrlMatch[1] : null;
                  const contentType = contentTypeMatch ? contentTypeMatch[1] : 'text';
                  
                  // Bouton de téléchargement direct optimisé
                  const DownloadButton = () => downloadUrl && downloadUrl !== '#' ? (
                    <a 
                      href={downloadUrl}
                      download
                      className="inline-flex items-center px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium transition-colors no-underline"
                    >
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      📥 Télécharger {contentType.toUpperCase()}
                    </a>
                  ) : null;
                  
                  // AFFICHAGE IMAGE
                  if (imageUrlMatch) {
                    const imageUrl = imageUrlMatch[1];
                    
                    return (
                      <div className="space-y-4">
                        <div className="whitespace-pre-wrap text-gray-800 mb-4">
                          {cleanText}
                        </div>
                        <div className="text-center">
                          <img 
                            src={imageUrl}
                            alt="Image générée par IA"
                            className="max-w-full h-auto mx-auto rounded-lg shadow-lg border"
                            style={{ maxHeight: '400px' }}
                            onError={(e) => {
                              console.log('Image load error:', imageUrl);
                              e.currentTarget.outerHTML = `<div class="bg-gradient-to-br from-purple-400 to-blue-500 rounded-lg p-8 text-center text-white">
                                <p class="text-lg">🖼️ Image générée par IA</p>
                                <p class="text-sm opacity-75 mt-2">IA Chéries Professional</p>
                              </div>`;
                            }}
                          />
                          <div className="flex justify-center space-x-4 mt-4">
                            <a href={imageUrl} target="_blank" rel="noopener noreferrer" 
                               className="text-blue-600 hover:text-blue-800 underline text-sm">
                              🔍 Voir en grand
                            </a>
                            <DownloadButton />
                          </div>
                        </div>
                      </div>
                    );
                  }
                  
                  // AFFICHAGE AUDIO
                  if (audioUrlMatch) {
                    const audioUrl = audioUrlMatch[1];
                    
                    return (
                      <div className="space-y-4">
                        <div className="whitespace-pre-wrap text-gray-800 mb-4">
                          {cleanText}
                        </div>
                        <div className="bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg p-6 text-white text-center">
                          <div className="text-4xl mb-2">🎵</div>
                          <h3 className="text-lg font-semibold mb-4">Audio généré par IA</h3>
                          <audio controls className="w-full max-w-md mx-auto mb-4">
                            <source src={audioUrl} type="audio/mpeg" />
                            Votre navigateur ne supporte pas l'audio HTML5.
                          </audio>
                          <div className="flex justify-center">
                            <DownloadButton />
                          </div>
                        </div>
                      </div>
                    );
                  }
                  
                  // AFFICHAGE VIDEO
                  if (videoUrlMatch) {
                    const videoUrl = videoUrlMatch[1];
                    const thumbnailUrl = thumbnailUrlMatch ? thumbnailUrlMatch[1] : null;
                    
                    return (
                      <div className="space-y-4">
                        <div className="whitespace-pre-wrap text-gray-800 mb-4">
                          {cleanText}
                        </div>
                        <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-6 text-white text-center">
                          <div className="text-4xl mb-2">🎬</div>
                          <h3 className="text-lg font-semibold mb-4">Vidéo générée par IA</h3>
                          <video controls className="w-full max-w-2xl mx-auto rounded-lg mb-4" poster={thumbnailUrl || undefined}>
                            <source src={videoUrl} type="video/mp4" />
                            Votre navigateur ne supporte pas la vidéo HTML5.
                          </video>
                          <div className="flex justify-center space-x-4">
                            <a href={videoUrl} target="_blank" rel="noopener noreferrer"
                               className="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors">
                              🎥 Ouvrir la vidéo
                            </a>
                            <DownloadButton />
                          </div>
                        </div>
                      </div>
                    );
                  }
                  
                  // AFFICHAGE TEXTE ET AUTRES CONTENUS
                  return (
                    <div className="space-y-4">
                      <div className="whitespace-pre-wrap text-gray-800">
                        {cleanText}
                      </div>
                      {downloadUrl && downloadUrl !== '#' && (
                        <div className="flex justify-center pt-4">
                          <DownloadButton />
                        </div>
                      )}
                      {contentType === 'blog' && (
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-4">
                          <div className="flex items-center text-blue-800">
                            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                              <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <span className="font-medium">Article professionnel généré</span>
                          </div>
                          <p className="text-blue-600 text-sm mt-1">
                            Prêt pour publication • Optimisé SEO • Format Markdown
                          </p>
                        </div>
                      )}
                      {contentType === 'script' && (
                        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 mt-4">
                          <div className="flex items-center text-purple-800">
                            <span className="font-medium">🎬 Script professionnel généré</span>
                          </div>
                          <p className="text-purple-600 text-sm mt-1">
                            Format Fountain • Prêt pour production • Timing estimé
                          </p>
                        </div>
                      )}
                    </div>
                  );
                  
                  // Essayer de parser comme JSON (ancien format - fallback)
                  try {
                    const parsed = JSON.parse(result);
                    
                    // Vérifier différents chemins pour les données d'image
                    const imageData = parsed.generated_content || parsed.image_base64 || parsed.data?.generated_content || parsed.data?.image_base64;
                    const imageUrl = parsed.image_url || parsed.data?.image_url;
                    
                    // Si c'est une image avec du base64 ou URL
                    if ((imageData && imageData.startsWith('data:image/')) || imageUrl) {
                      return (
                        <div className="text-center space-y-4">
                          <p className="text-green-600 font-semibold">✅ Image générée par IA</p>
                          <img 
                            src={imageData || imageUrl}
                            alt="Image générée par IA"
                            className="max-w-full h-auto mx-auto rounded-lg shadow-lg"
                            style={{ maxHeight: '400px' }}
                          />
                          <p className="text-sm text-gray-600">
                            Image générée | Source: API IA
                          </p>
                        </div>
                      );
                    }
                    
                    // Afficher le JSON formaté
                    return (
                      <div className="whitespace-pre-wrap text-gray-800">
                        {JSON.stringify(parsed, null, 2)}
                      </div>
                    );
                  } catch (e) {
                    // Afficher comme texte normal
                    return <div className="whitespace-pre-wrap text-gray-800">{result}</div>;
                  }
                })()}
              </div>
            ) : (
              <div className="text-gray-500 italic text-center">
                Le contenu généré apparaîtra ici...
                <br />
                <Brain className="h-12 w-12 mx-auto mt-4 text-gray-300" />
              </div>
            )}
          </div>
          
          {result && (
            <div className="mt-4 flex space-x-2">
              <button 
                onClick={copyToClipboard}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                <Copy className="h-4 w-4" />
                <span>Copier</span>
              </button>
              <button 
                onClick={() => setResult('')}
                className="flex items-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
              >
                <Trash2 className="h-4 w-4" />
                <span>Effacer</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
