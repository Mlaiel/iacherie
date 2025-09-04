/**
 * Task Scheduler Library
 */

interface ScheduledTask {
  id: string;
  fn: () => void | Promise<void>;
  delay: number;
  repeat?: boolean;
  interval?: number;
  timeoutId?: NodeJS.Timeout | number;
  intervalId?: NodeJS.Timeout | number;
}

class Scheduler {
  private tasks: Map<string, ScheduledTask> = new Map();

  schedule(fn: () => void | Promise<void>, delay: number): string {
    const id = this.generateId();
    const task: ScheduledTask = { id, fn, delay };

    task.timeoutId = setTimeout(async () => {
      try {
        await fn();
      } catch (error) {
        console.error('Scheduled task error:', error);
      } finally {
        this.tasks.delete(id);
      }
    }, delay);

    this.tasks.set(id, task);
    return id;
  }

  repeat(fn: () => void | Promise<void>, interval: number, immediate = false): string {
    const id = this.generateId();
    const task: ScheduledTask = { id, fn, delay: 0, repeat: true, interval };

    if (immediate) {
      fn().catch(error => console.error('Repeated task error:', error));
    }

    task.intervalId = setInterval(async () => {
      try {
        await fn();
      } catch (error) {
        console.error('Repeated task error:', error);
      }
    }, interval);

    this.tasks.set(id, task);
    return id;
  }

  cancel(id: string): boolean {
    const task = this.tasks.get(id);
    if (!task) return false;

    if (task.timeoutId) {
      clearTimeout(task.timeoutId);
    }
    if (task.intervalId) {
      clearInterval(task.intervalId);
    }

    this.tasks.delete(id);
    return true;
  }

  cancelAll(): void {
    this.tasks.forEach(task => {
      if (task.timeoutId) clearTimeout(task.timeoutId);
      if (task.intervalId) clearInterval(task.intervalId);
    });
    this.tasks.clear();
  }

  getTaskCount(): number {
    return this.tasks.size;
  }

  getTasks(): ScheduledTask[] {
    return Array.from(this.tasks.values());
  }

  private generateId(): string {
    return `scheduler_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

export { Scheduler };
export default Scheduler;
