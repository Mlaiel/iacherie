/**
 * State Management Library
 */

type StateListener<T> = (state: T) => void;
type StateSelector<T, R> = (state: T) => R;

class StateManager<T> {
  private state: T;
  private listeners: Set<StateListener<T>> = new Set();

  constructor(initialState: T) {
    this.state = initialState;
  }

  getState(): T {
    return this.state;
  }

  setState(newState: Partial<T> | ((prevState: T) => Partial<T>)): void {
    const updates = typeof newState === 'function' ? newState(this.state) : newState;
    this.state = { ...this.state, ...updates };
    this.notifyListeners();
  }

  subscribe(listener: StateListener<T>): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  select<R>(selector: StateSelector<T, R>): R {
    return selector(this.state);
  }

  private notifyListeners(): void {
    this.listeners.forEach(listener => listener(this.state));
  }

  reset(state: T): void {
    this.state = state;
    this.notifyListeners();
  }

  getListenerCount(): number {
    return this.listeners.size;
  }
}

export { StateManager };
export default StateManager;
