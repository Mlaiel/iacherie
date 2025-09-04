/**
 * Middleware Library
 */

type MiddlewareFunction<T = any> = (
  context: T,
  next: () => Promise<void> | void
) => Promise<void> | void;

class MiddlewareStack<T = any> {
  private middlewares: MiddlewareFunction<T>[] = [];

  use(middleware: MiddlewareFunction<T>): void {
    this.middlewares.push(middleware);
  }

  async execute(context: T): Promise<void> {
    let index = 0;

    const next = async (): Promise<void> => {
      if (index >= this.middlewares.length) return;
      
      const middleware = this.middlewares[index++];
      await middleware(context, next);
    };

    await next();
  }

  clear(): void {
    this.middlewares = [];
  }

  remove(middleware: MiddlewareFunction<T>): boolean {
    const index = this.middlewares.indexOf(middleware);
    if (index > -1) {
      this.middlewares.splice(index, 1);
      return true;
    }
    return false;
  }

  size(): number {
    return this.middlewares.length;
  }

  getMiddlewares(): MiddlewareFunction<T>[] {
    return [...this.middlewares];
  }
}

export { MiddlewareStack, type MiddlewareFunction };
export default MiddlewareStack;
