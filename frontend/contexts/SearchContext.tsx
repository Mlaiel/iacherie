/**
 * Search Context - Global search functionality context
 */

import { createContext, useContext, ReactNode, useState } from 'react';

interface SearchResult {
  id: string;
  type: 'content' | 'user' | 'project';
  title: string;
  description: string;
  url: string;
}

interface SearchContextType {
  query: string;
  results: SearchResult[];
  isSearching: boolean;
  recentSearches: string[];
  setQuery: (query: string) => void;
  search: (query: string) => Promise<void>;
  clearResults: () => void;
  addToRecent: (query: string) => void;
  clearRecent: () => void;
}

const SearchContext = createContext<SearchContextType | undefined>(undefined);

export function SearchProvider({ children }: { children: ReactNode }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);

  const search = async (searchQuery: string) => {
    setIsSearching(true);
    try {
      // Mock search - in real app would call API
      await new Promise(resolve => setTimeout(resolve, 500));
      setResults([
        {
          id: '1',
          type: 'content',
          title: `Content matching "${searchQuery}"`,
          description: 'Sample content description',
          url: '/content/1',
        },
      ]);
      addToRecent(searchQuery);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setIsSearching(false);
    }
  };

  const clearResults = () => {
    setResults([]);
    setQuery('');
  };

  const addToRecent = (query: string) => {
    if (query.trim()) {
      setRecentSearches(prev => [
        query,
        ...prev.filter(q => q !== query).slice(0, 4),
      ]);
    }
  };

  const clearRecent = () => {
    setRecentSearches([]);
  };

  return (
    <SearchContext.Provider value={{
      query,
      results,
      isSearching,
      recentSearches,
      setQuery,
      search,
      clearResults,
      addToRecent,
      clearRecent,
    }}>
      {children}
    </SearchContext.Provider>
  );
}

export const useSearch = () => {
  const context = useContext(SearchContext);
  if (!context) {
    throw new Error('useSearch must be used within a SearchProvider');
  }
  return context;
};
