/**
 * @fileoverview Marketplace Dashboard - Product listing and sales management
 * @author Fahed Mlaiel <mlaiel@live.de>
 */

'use client';

import React, { useState, useCallback } from 'react';
import { MarketplaceProduct } from '@/core/types';
import { Currency, MarketplaceCategory } from '@/core/enums';

interface MarketplaceDashboardProps {
  onProductCreate?: (product: Partial<MarketplaceProduct>) => void;
  onProductUpdate?: (id: string, updates: Partial<MarketplaceProduct>) => void;
  className?: string;
}

export const MarketplaceDashboard: React.FC<MarketplaceDashboardProps> = ({
  onProductCreate,
  onProductUpdate,
  className = '',
}) => {
  const [products, setProducts] = useState<MarketplaceProduct[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<MarketplaceCategory | ''>('');

  const createSampleProduct = useCallback(() => {
    const newProduct: MarketplaceProduct = {
      id: `product_${Date.now()}`,
      contentId: 'sample_content',
      title: 'Sample Digital Asset',
      description: 'High-quality digital content for creators',
      price: 29.99,
      currency: Currency.USD,
      category: MarketplaceCategory.STOCK_MEDIA,
      tags: ['digital', 'creative', 'professional'],
      seller: 'Creator Studio',
      rating: 4.5,
      downloads: 0,
    };

    setProducts(prev => [...prev, newProduct]);
    onProductCreate?.(newProduct);
  }, [onProductCreate]);

  const formatCurrency = (amount: number, currency: Currency = Currency.USD) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
    }).format(amount);
  };

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <span
        key={i}
        className={`text-sm ${
          i < Math.floor(rating) ? 'text-yellow-400' : 'text-gray-300'
        }`}
      >
        ★
      </span>
    ));
  };

  return (
    <div className={`marketplace-dashboard ${className}`}>
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Marketplace</h2>
          <p className="text-gray-600">Manage your digital products and sales</p>
        </div>
        <button
          onClick={createSampleProduct}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          + Add Product
        </button>
      </div>

      {/* Filter */}
      <div className="mb-6">
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value as MarketplaceCategory | '')}
          className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">All Categories</option>
          {Object.values(MarketplaceCategory).map((category) => (
            <option key={category} value={category}>
              {category.replace('_', ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase())}
            </option>
          ))}
        </select>
      </div>

      {/* Products Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {products
          .filter(product => !selectedCategory || product.category === selectedCategory)
          .map((product) => (
          <div key={product.id} className="bg-white rounded-lg shadow-md overflow-hidden">
            {/* Product Image Placeholder */}
            <div className="h-48 bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <span className="text-white text-4xl">🎨</span>
            </div>
            
            {/* Product Info */}
            <div className="p-4">
              <h3 className="font-semibold text-gray-900 mb-2">{product.title}</h3>
              <p className="text-gray-600 text-sm mb-3 line-clamp-2">{product.description}</p>
              
              {/* Rating and Downloads */}
              <div className="flex justify-between items-center mb-3">
                <div className="flex items-center space-x-1">
                  {renderStars(product.rating)}
                  <span className="text-sm text-gray-600 ml-1">({product.rating})</span>
                </div>
                <span className="text-sm text-gray-600">{product.downloads} downloads</span>
              </div>
              
              {/* Price and Category */}
              <div className="flex justify-between items-center mb-3">
                <span className="text-lg font-bold text-gray-900">
                  {formatCurrency(product.price, product.currency as Currency)}
                </span>
                <span className="text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded">
                  {product.category.replace('_', ' ')}
                </span>
              </div>
              
              {/* Tags */}
              <div className="flex flex-wrap gap-1 mb-3">
                {product.tags.slice(0, 3).map((tag) => (
                  <span
                    key={tag}
                    className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded"
                  >
                    {tag}
                  </span>
                ))}
              </div>
              
              {/* Actions */}
              <div className="flex space-x-2">
                <button
                  onClick={() => onProductUpdate?.(product.id, { price: product.price * 0.9 })}
                  className="flex-1 bg-gray-100 text-gray-800 px-3 py-2 rounded text-sm hover:bg-gray-200 transition-colors"
                >
                  Edit
                </button>
                <button
                  onClick={() => setProducts(prev => prev.filter(p => p.id !== product.id))}
                  className="flex-1 bg-red-100 text-red-800 px-3 py-2 rounded text-sm hover:bg-red-200 transition-colors"
                >
                  Remove
                </button>
              </div>
            </div>
          </div>
        ))}
        
        {/* Empty State */}
        {products.length === 0 && (
          <div className="col-span-full text-center py-12">
            <div className="text-6xl mb-4">🏪</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No products yet</h3>
            <p className="text-gray-600 mb-4">Start by adding your first product to the marketplace</p>
            <button
              onClick={createSampleProduct}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Add Your First Product
            </button>
          </div>
        )}
      </div>
    </div>
  );
};