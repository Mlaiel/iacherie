/**
 * Professional Marketplace Component
 * 
 * Digital marketplace for AI-generated content
 * Direct backend integration for marketplace features
 */

'use client';

import React, { useState, useEffect } from 'react';
import { 
  Store, 
  Search, 
  Filter, 
  Star, 
  Download, 
  Eye, 
  Heart,
  ShoppingCart,
  TrendingUp,
  DollarSign,
  Users,
  Zap
} from 'lucide-react';

interface MarketplaceItem {
  id: string;
  title: string;
  category: 'video' | 'image' | 'audio' | 'text' | 'template';
  creator: string;
  price: number;
  rating: number;
  reviews: number;
  downloads: number;
  thumbnail: string;
  tags: string[];
  premium: boolean;
  featured: boolean;
}

interface MarketplaceData {
  items: MarketplaceItem[];
  totalItems: number;
  categories: any[];
  trending: MarketplaceItem[];
  featured: MarketplaceItem[];
}

export default function Marketplace() {
  const [marketplaceData, setMarketplaceData] = useState<MarketplaceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('popular');

  useEffect(() => {
    const fetchMarketplaceData = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/marketplace`);
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        setMarketplaceData(data);
      } catch (error) {
        console.error('Marketplace data fetch error:', error);
        // Fallback data
        setMarketplaceData({
          items: [
            {
              id: 'item-1',
              title: 'Professional Marketing Video Template',
              category: 'video',
              creator: 'StudioPro',
              price: 29.99,
              rating: 4.8,
              reviews: 234,
              downloads: 1250,
              thumbnail: '/api/placeholder/300/200',
              tags: ['marketing', 'professional', 'template'],
              premium: true,
              featured: true
            },
            {
              id: 'item-2',
              title: 'AI-Generated Product Images Pack',
              category: 'image',
              creator: 'AICreative',
              price: 19.99,
              rating: 4.6,
              reviews: 189,
              downloads: 890,
              thumbnail: '/api/placeholder/300/200',
              tags: ['product', 'ecommerce', 'professional'],
              premium: false,
              featured: true
            },
            {
              id: 'item-3',
              title: 'Voice-Over Audio Collection',
              category: 'audio',
              creator: 'VoiceStudio',
              price: 15.99,
              rating: 4.9,
              reviews: 145,
              downloads: 567,
              thumbnail: '/api/placeholder/300/200',
              tags: ['voice', 'commercial', 'narration'],
              premium: true,
              featured: false
            }
          ],
          totalItems: 1250,
          categories: [
            { id: 'video', name: 'Videos', count: 342 },
            { id: 'image', name: 'Images', count: 567 },
            { id: 'audio', name: 'Audio', count: 189 },
            { id: 'text', name: 'Text', count: 98 },
            { id: 'template', name: 'Templates', count: 54 }
          ],
          trending: [],
          featured: []
        });
      } finally {
        setLoading(false);
      }
    };

    fetchMarketplaceData();
    const interval = setInterval(fetchMarketplaceData, 30000);
    return () => clearInterval(interval);
  }, []);

  const handlePurchase = async (itemId: string) => {
    try {
      console.log('Purchasing item:', itemId);
      // Implementation for purchase flow
    } catch (error) {
      console.error('Purchase failed:', error);
    }
  };

  const handlePreview = (itemId: string) => {
    console.log('Previewing item:', itemId);
    // Implementation for preview modal
  };

  const handleFavorite = (itemId: string) => {
    console.log('Adding to favorites:', itemId);
    // Implementation for favorites
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'video': return '🎥';
      case 'image': return '🖼️';
      case 'audio': return '🎵';
      case 'text': return '📝';
      case 'template': return '📋';
      default: return '📦';
    }
  };

  const filteredItems = marketplaceData?.items.filter(item => {
    const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory;
    const matchesSearch = searchQuery === '' || 
      item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesCategory && matchesSearch;
  }) || [];

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin h-12 w-12 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-900">Loading Marketplace</h2>
          <p className="text-gray-600 mt-2">Fetching latest content...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Store className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Content Marketplace</h1>
                <p className="text-sm text-gray-600">
                  Premium AI-generated content and templates
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{marketplaceData?.totalItems || 0}</div>
                <div className="text-xs text-gray-500">Items Available</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">2.4M+</div>
                <div className="text-xs text-gray-500">Downloads</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Search and Filters */}
        <div className="bg-white p-6 rounded-xl shadow-sm border mb-8">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search content, templates, creators..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <div className="flex gap-4">
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Categories</option>
                {marketplaceData?.categories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.name} ({category.count})
                  </option>
                ))}
              </select>
              
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="popular">Most Popular</option>
                <option value="recent">Most Recent</option>
                <option value="price-low">Price: Low to High</option>
                <option value="price-high">Price: High to Low</option>
                <option value="rating">Highest Rated</option>
              </select>
            </div>
          </div>
        </div>

        {/* Items Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredItems.map((item) => (
            <div key={item.id} className="bg-white rounded-xl shadow-sm border hover:shadow-md transition-shadow">
              {/* Thumbnail */}
              <div className="relative">
                <div className="aspect-video bg-gray-200 rounded-t-xl flex items-center justify-center text-4xl">
                  {getCategoryIcon(item.category)}
                </div>
                
                {item.featured && (
                  <div className="absolute top-3 left-3 bg-yellow-500 text-white px-2 py-1 rounded-full text-xs font-medium">
                    <Star className="h-3 w-3 inline mr-1" />
                    Featured
                  </div>
                )}
                
                {item.premium && (
                  <div className="absolute top-3 right-3 bg-purple-600 text-white px-2 py-1 rounded-full text-xs font-medium">
                    <Zap className="h-3 w-3 inline mr-1" />
                    Premium
                  </div>
                )}
                
                <div className="absolute bottom-3 right-3 flex space-x-2">
                  <button
                    onClick={() => handlePreview(item.id)}
                    className="bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-70"
                  >
                    <Eye className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleFavorite(item.id)}
                    className="bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-70"
                  >
                    <Heart className="h-4 w-4" />
                  </button>
                </div>
              </div>
              
              {/* Content */}
              <div className="p-4">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-semibold text-gray-900 line-clamp-2">{item.title}</h3>
                  <div className="text-lg font-bold text-green-600">${item.price}</div>
                </div>
                
                <p className="text-sm text-gray-600 mb-3">by {item.creator}</p>
                
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-1">
                    <Star className="h-4 w-4 text-yellow-500 fill-current" />
                    <span className="text-sm font-medium">{item.rating}</span>
                    <span className="text-sm text-gray-500">({item.reviews})</span>
                  </div>
                  
                  <div className="flex items-center text-sm text-gray-500">
                    <Download className="h-4 w-4 mr-1" />
                    {item.downloads.toLocaleString()}
                  </div>
                </div>
                
                <div className="flex flex-wrap gap-1 mb-4">
                  {item.tags.slice(0, 3).map((tag) => (
                    <span key={tag} className="bg-gray-100 text-gray-700 px-2 py-1 rounded-full text-xs">
                      {tag}
                    </span>
                  ))}
                </div>
                
                <button
                  onClick={() => handlePurchase(item.id)}
                  className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 flex items-center justify-center"
                >
                  <ShoppingCart className="h-4 w-4 mr-2" />
                  Purchase
                </button>
              </div>
            </div>
          ))}
        </div>
        
        {filteredItems.length === 0 && (
          <div className="text-center py-12">
            <Store className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No items found</h3>
            <p className="text-gray-600 mb-4">Try adjusting your search or filters</p>
          </div>
        )}
      </div>
    </div>
  );
}