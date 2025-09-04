/**
 * Event Emitter Library
 */

type EventHandler<T = any> = (data: T) => void;

class EventEmitter {
  private events: Map<string, EventHandler[]> = new Map();

  on<T = any>(event: string, handler: EventHandler<T>): void {
    if (!this.events.has(event)) {
      this.events.set(event, []);
    }
    this.events.get(event)!.push(handler);
  }

  off<T = any>(event: string, handler: EventHandler<T>): void {
    const handlers = this.events.get(event);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  once<T = any>(event: string, handler: EventHandler<T>): void {
    const onceHandler = (data: T) => {
      handler(data);
      this.off(event, onceHandler);
    };
    this.on(event, onceHandler);
  }

  emit<T = any>(event: string, data?: T): void {
    const handlers = this.events.get(event);
    if (handlers) {
      handlers.forEach(handler => handler(data));
    }
  }

  removeAllListeners(event?: string): void {
    if (event) {
      this.events.delete(event);
    } else {
      this.events.clear();
    }
  }

  listenerCount(event: string): number {
    return this.events.get(event)?.length || 0;
  }

  eventNames(): string[] {
    return Array.from(this.events.keys());
  }
}

export { EventEmitter };
export default EventEmitter;
