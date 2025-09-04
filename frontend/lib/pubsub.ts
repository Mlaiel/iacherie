/**
 * Publish-Subscribe Library
 */

type Subscriber<T = any> = (data: T) => void;

interface Subscription {
  unsubscribe: () => void;
}

class PubSub {
  private subscribers: Map<string, Set<Subscriber>> = new Map();

  publish<T = any>(topic: string, data?: T): void {
    const topicSubscribers = this.subscribers.get(topic);
    if (topicSubscribers) {
      topicSubscribers.forEach(subscriber => {
        try {
          subscriber(data);
        } catch (error) {
          console.error(`Error in subscriber for topic "${topic}":`, error);
        }
      });
    }
  }

  subscribe<T = any>(topic: string, subscriber: Subscriber<T>): Subscription {
    if (!this.subscribers.has(topic)) {
      this.subscribers.set(topic, new Set());
    }
    
    this.subscribers.get(topic)!.add(subscriber);

    return {
      unsubscribe: () => {
        const topicSubscribers = this.subscribers.get(topic);
        if (topicSubscribers) {
          topicSubscribers.delete(subscriber);
          if (topicSubscribers.size === 0) {
            this.subscribers.delete(topic);
          }
        }
      }
    };
  }

  once<T = any>(topic: string, subscriber: Subscriber<T>): Subscription {
    const onceSubscriber = (data: T) => {
      subscriber(data);
      subscription.unsubscribe();
    };

    const subscription = this.subscribe(topic, onceSubscriber);
    return subscription;
  }

  unsubscribe(topic: string, subscriber?: Subscriber): void {
    if (subscriber) {
      const topicSubscribers = this.subscribers.get(topic);
      if (topicSubscribers) {
        topicSubscribers.delete(subscriber);
        if (topicSubscribers.size === 0) {
          this.subscribers.delete(topic);
        }
      }
    } else {
      this.subscribers.delete(topic);
    }
  }

  clear(): void {
    this.subscribers.clear();
  }

  getTopics(): string[] {
    return Array.from(this.subscribers.keys());
  }

  getSubscriberCount(topic: string): number {
    return this.subscribers.get(topic)?.size || 0;
  }

  hasSubscribers(topic: string): boolean {
    return this.getSubscriberCount(topic) > 0;
  }
}

// Global instance
const globalPubSub = new PubSub();

export { PubSub, globalPubSub };
export default PubSub;
