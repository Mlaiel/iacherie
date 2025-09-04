/**
 * Advanced Storage Library
 */

interface StorageOptions {
  prefix?: string;
  serializer?: {
    stringify: (value: any) => string;
    parse: (value: string) => any;
  };
  ttl?: number; // Time to live in milliseconds
}

interface StorageItem {
  value: any;
  timestamp: number;
  ttl?: number;
}

class AdvancedStorage {
  private prefix: string;
  private serializer: Required<StorageOptions>['serializer'];
  private storage: Storage;

  constructor(storage: Storage = localStorage, options: StorageOptions = {}) {
    this.storage = storage;
    this.prefix = options.prefix || '';
    this.serializer = options.serializer || {
      stringify: JSON.stringify,
      parse: JSON.parse
    };
  }

  set(key: string, value: any, ttl?: number): boolean {
    try {
      const item: StorageItem = {
        value,
        timestamp: Date.now(),
        ttl
      };
      
      const serialized = this.serializer.stringify(item);
      this.storage.setItem(this.getKey(key), serialized);
      return true;
    } catch {
      return false;
    }
  }

  get<T = any>(key: string, defaultValue?: T): T | undefined {
    try {
      const serialized = this.storage.getItem(this.getKey(key));
      if (!serialized) return defaultValue;

      const item: StorageItem = this.serializer.parse(serialized);
      
      // Check if item has expired
      if (item.ttl && (Date.now() - item.timestamp) > item.ttl) {
        this.remove(key);
        return defaultValue;
      }

      return item.value as T;
    } catch {
      return defaultValue;
    }
  }

  has(key: string): boolean {
    const value = this.get(key);
    return value !== undefined;
  }

  remove(key: string): boolean {
    try {
      this.storage.removeItem(this.getKey(key));
      return true;
    } catch {
      return false;
    }
  }

  clear(): boolean {
    try {
      if (this.prefix) {
        // Only clear items with our prefix
        const keysToRemove: string[] = [];
        for (let i = 0; i < this.storage.length; i++) {
          const key = this.storage.key(i);
          if (key && key.startsWith(this.prefix)) {
            keysToRemove.push(key);
          }
        }
        keysToRemove.forEach(key => this.storage.removeItem(key));
      } else {
        this.storage.clear();
      }
      return true;
    } catch {
      return false;
    }
  }

  keys(): string[] {
    const keys: string[] = [];
    for (let i = 0; i < this.storage.length; i++) {
      const key = this.storage.key(i);
      if (key && key.startsWith(this.prefix)) {
        keys.push(key.substring(this.prefix.length));
      }
    }
    return keys;
  }

  size(): number {
    return this.keys().length;
  }

  private getKey(key: string): string {
    return this.prefix + key;
  }

  // Cleanup expired items
  cleanup(): number {
    const keys = this.keys();
    let removedCount = 0;

    keys.forEach(key => {
      const value = this.get(key);
      if (value === undefined) {
        removedCount++;
      }
    });

    return removedCount;
  }
}

export { AdvancedStorage };
export default AdvancedStorage;
