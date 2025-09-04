/**
 * Logger Library
 */

enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3,
}

interface LogEntry {
  timestamp: Date;
  level: LogLevel;
  message: string;
  data?: any;
  category?: string;
}

class Logger {
  private level: LogLevel = LogLevel.INFO;
  private logs: LogEntry[] = [];
  private maxLogs: number = 1000;

  setLevel(level: LogLevel): void {
    this.level = level;
  }

  private log(level: LogLevel, message: string, data?: any, category?: string): void {
    if (level < this.level) return;

    const entry: LogEntry = {
      timestamp: new Date(),
      level,
      message,
      data,
      category,
    };

    this.logs.push(entry);
    
    if (this.logs.length > this.maxLogs) {
      this.logs.shift();
    }

    this.output(entry);
  }

  private output(entry: LogEntry): void {
    const prefix = `[${entry.timestamp.toISOString()}] ${LogLevel[entry.level]}`;
    const message = entry.category ? `${prefix} [${entry.category}]: ${entry.message}` : `${prefix}: ${entry.message}`;

    switch (entry.level) {
      case LogLevel.DEBUG:
        console.debug(message, entry.data);
        break;
      case LogLevel.INFO:
        console.info(message, entry.data);
        break;
      case LogLevel.WARN:
        console.warn(message, entry.data);
        break;
      case LogLevel.ERROR:
        console.error(message, entry.data);
        break;
    }
  }

  debug(message: string, data?: any, category?: string): void {
    this.log(LogLevel.DEBUG, message, data, category);
  }

  info(message: string, data?: any, category?: string): void {
    this.log(LogLevel.INFO, message, data, category);
  }

  warn(message: string, data?: any, category?: string): void {
    this.log(LogLevel.WARN, message, data, category);
  }

  error(message: string, data?: any, category?: string): void {
    this.log(LogLevel.ERROR, message, data, category);
  }

  getLogs(level?: LogLevel): LogEntry[] {
    return level !== undefined 
      ? this.logs.filter(log => log.level >= level)
      : [...this.logs];
  }

  clear(): void {
    this.logs = [];
  }
}

export { Logger, LogLevel, type LogEntry };
export default Logger;
