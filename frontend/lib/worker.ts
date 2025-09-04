/**
 * Web Worker Library
 */

interface WorkerTask<T = any, R = any> {
  id: string;
  data: T;
  resolve: (result: R) => void;
  reject: (error: Error) => void;
}

class WorkerManager<T = any, R = any> {
  private worker: Worker;
  private tasks: Map<string, WorkerTask<T, R>> = new Map();

  constructor(workerScript: string | (() => void)) {
    if (typeof workerScript === 'string') {
      this.worker = new Worker(workerScript);
    } else {
      // Create worker from function
      const blob = new Blob([`(${workerScript.toString()})()`], {
        type: 'application/javascript'
      });
      this.worker = new Worker(URL.createObjectURL(blob));
    }

    this.worker.onmessage = (event) => {
      const { id, result, error } = event.data;
      const task = this.tasks.get(id);
      
      if (task) {
        this.tasks.delete(id);
        if (error) {
          task.reject(new Error(error));
        } else {
          task.resolve(result);
        }
      }
    };

    this.worker.onerror = (error) => {
      console.error('Worker error:', error);
    };
  }

  execute(data: T): Promise<R> {
    return new Promise((resolve, reject) => {
      const id = this.generateId();
      const task: WorkerTask<T, R> = { id, data, resolve, reject };
      
      this.tasks.set(id, task);
      this.worker.postMessage({ id, data });
    });
  }

  terminate(): void {
    this.worker.terminate();
    this.tasks.clear();
  }

  private generateId(): string {
    return `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  getPendingTaskCount(): number {
    return this.tasks.size;
  }
}

export { WorkerManager };
export default WorkerManager;
