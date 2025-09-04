import { useState, useCallback, useMemo } from 'react';
import { useDebounce } from './useDebounce';

export const useSearch = <T>(items: T[], searchKey: keyof T, delay = 300) => {
  const [query, setQuery] = useState('');
  const debouncedQuery = useDebounce(query, delay);

  const filteredItems = useMemo(() => {
    if (!debouncedQuery) return items;
    return items.filter(item => 
      String(item[searchKey]).toLowerCase().includes(debouncedQuery.toLowerCase())
    );
  }, [items, searchKey, debouncedQuery]);

  const clearSearch = useCallback(() => setQuery(''), []);

  return { query, setQuery, filteredItems, clearSearch };
};
