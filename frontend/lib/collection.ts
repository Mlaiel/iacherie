/**
 * Advanced Collection Library
 */

class Collection<T> {
  private items: T[] = [];

  constructor(items: T[] = []) {
    this.items = [...items];
  }

  add(item: T): Collection<T> {
    this.items.push(item);
    return this;
  }

  remove(predicate: (item: T) => boolean): Collection<T> {
    this.items = this.items.filter(item => !predicate(item));
    return this;
  }

  find(predicate: (item: T) => boolean): T | undefined {
    return this.items.find(predicate);
  }

  filter(predicate: (item: T) => boolean): Collection<T> {
    return new Collection(this.items.filter(predicate));
  }

  map<U>(mapper: (item: T) => U): Collection<U> {
    return new Collection(this.items.map(mapper));
  }

  reduce<U>(reducer: (acc: U, item: T) => U, initialValue: U): U {
    return this.items.reduce(reducer, initialValue);
  }

  sort(compareFn?: (a: T, b: T) => number): Collection<T> {
    return new Collection([...this.items].sort(compareFn));
  }

  groupBy<K extends string | number>(keySelector: (item: T) => K): Map<K, Collection<T>> {
    const groups = new Map<K, Collection<T>>();
    
    this.items.forEach(item => {
      const key = keySelector(item);
      if (!groups.has(key)) {
        groups.set(key, new Collection());
      }
      groups.get(key)!.add(item);
    });
    
    return groups;
  }

  take(count: number): Collection<T> {
    return new Collection(this.items.slice(0, count));
  }

  skip(count: number): Collection<T> {
    return new Collection(this.items.slice(count));
  }

  reverse(): Collection<T> {
    return new Collection([...this.items].reverse());
  }

  distinct(keySelector?: (item: T) => any): Collection<T> {
    if (!keySelector) {
      return new Collection([...new Set(this.items)]);
    }
    
    const seen = new Set();
    const result: T[] = [];
    
    this.items.forEach(item => {
      const key = keySelector(item);
      if (!seen.has(key)) {
        seen.add(key);
        result.push(item);
      }
    });
    
    return new Collection(result);
  }

  count(predicate?: (item: T) => boolean): number {
    if (!predicate) return this.items.length;
    return this.items.filter(predicate).length;
  }

  isEmpty(): boolean {
    return this.items.length === 0;
  }

  first(): T | undefined {
    return this.items[0];
  }

  last(): T | undefined {
    return this.items[this.items.length - 1];
  }

  toArray(): T[] {
    return [...this.items];
  }

  forEach(callback: (item: T, index: number) => void): void {
    this.items.forEach(callback);
  }

  some(predicate: (item: T) => boolean): boolean {
    return this.items.some(predicate);
  }

  every(predicate: (item: T) => boolean): boolean {
    return this.items.every(predicate);
  }

  static from<T>(items: T[]): Collection<T> {
    return new Collection(items);
  }
}

export { Collection };
export default Collection;
