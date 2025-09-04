/**
 * Cache Library
 */

interface CacheItem<T> {
  value: T;
  expiry: number;
  created: number;
}

class Cache<T = any> {
  private storage: Map<string, CacheItem<T>> = new Map();
  private defaultTTL: number;

  constructor(defaultTTL: number = 300000) { // 5 minutes default
    this.defaultTTL = defaultTTL;
    this.startCleanupInterval();
  }

  set(key: string, value: T, ttl?: number): void {
    const now = Date.now();
    const expiry = now + (ttl || this.defaultTTL);
    
    this.storage.set(key, {
      value,
      expiry,
      created: now,
    });
  }

  get(key: string): T | null {
    const item = this.storage.get(key);
    
    if (!item) return null;
    
    if (Date.now() > item.expiry) {
      this.storage.delete(key);
      return null;
    }
    
    return item.value;
  }

  has(key: string): boolean {
    const item = this.storage.get(key);
    
    if (!item) return false;
    
    if (Date.now() > item.expiry) {
      this.storage.delete(key);
      return false;
    }
    
    return true;
  }

  delete(key: string): boolean {
    return this.storage.delete(key);
  }

  clear(): void {
    this.storage.clear();
  }

  size(): number {
    this.cleanup();
    return this.storage.size;
  }

  keys(): string[] {
    this.cleanup();
    return Array.from(this.storage.keys());
  }

  private cleanup(): void {
    const now = Date.now();
    for (const [key, item] of this.storage.entries()) {
      if (now > item.expiry) {
        this.storage.delete(key);
      }
    }
  }

  private startCleanupInterval(): void {
    setInterval(() => this.cleanup(), 60000); // Cleanup every minute
  }

  getStats(): { size: number; totalItems: number; expiredItems: number } {
    const totalItems = this.storage.size;
    this.cleanup();
    const activeItems = this.storage.size;
    
    return {
      size: activeItems,
      totalItems,
      expiredItems: totalItems - activeItems,
    };
  }
}

export { Cache };
export default Cache;
