/**
 * Logger Utility
 *
 * Provides structured logging with timestamp and severity levels.
 *
 * Design decisions:
 * - ISO 8601 timestamps for consistent time representation
 * - Four severity levels (DEBUG, INFO, WARN, ERROR)
 * - Simple implementation using console methods for stdio compatibility
 * - No external dependencies to keep bundle small
 * - Environment-aware log level filtering
 */

export enum LogLevel {
  DEBUG = 'DEBUG',
  INFO = 'INFO',
  WARN = 'WARN',
  ERROR = 'ERROR'
}

/**
 * Log level priority for filtering
 */
const LOG_LEVEL_PRIORITY: Record<LogLevel, number> = {
  [LogLevel.DEBUG]: 0,
  [LogLevel.INFO]: 1,
  [LogLevel.WARN]: 2,
  [LogLevel.ERROR]: 3
};

/**
 * Logger class providing structured logging functionality
 *
 * Why singleton pattern:
 * - Ensures consistent log level across the application
 * - Single configuration point for logging behavior
 * - Lightweight - no state management needed
 */
class Logger {
  private minimumLevel: LogLevel;

  constructor() {
    // Read log level from environment, default to INFO
    const envLevel = process.env.LOG_LEVEL as LogLevel;
    this.minimumLevel = envLevel && LOG_LEVEL_PRIORITY[envLevel] !== undefined
      ? envLevel
      : LogLevel.INFO;
  }

  /**
   * Core logging method
   *
   * @param level - Severity level of the log message
   * @param message - Human-readable message
   * @param args - Additional context (objects, errors, etc.)
   */
  log(level: LogLevel, message: string, ...args: any[]): void {
    // Filter messages below minimum level
    if (LOG_LEVEL_PRIORITY[level] < LOG_LEVEL_PRIORITY[this.minimumLevel]) {
      return;
    }

    // Format: [TIMESTAMP] [LEVEL] message
    const timestamp = new Date().toISOString();
    const formattedMessage = `[${timestamp}] [${level}] ${message}`;

    // Use appropriate console method based on severity
    // Why different methods: Enables filtering in dev tools and logs
    switch (level) {
      case LogLevel.ERROR:
        console.error(formattedMessage, ...args);
        break;
      case LogLevel.WARN:
        console.warn(formattedMessage, ...args);
        break;
      case LogLevel.DEBUG:
      case LogLevel.INFO:
      default:
        console.log(formattedMessage, ...args);
        break;
    }
  }

  /**
   * Log debug information (verbose, for development)
   * Example: logger.debug('Token loaded from cache', { expiresAt: 1234567890 })
   */
  debug(message: string, ...args: any[]): void {
    this.log(LogLevel.DEBUG, message, ...args);
  }

  /**
   * Log informational messages (normal operation)
   * Example: logger.info('MCP server started successfully')
   */
  info(message: string, ...args: any[]): void {
    this.log(LogLevel.INFO, message, ...args);
  }

  /**
   * Log warnings (recoverable issues)
   * Example: logger.warn('Rate limit approaching', { used: 95, limit: 100 })
   */
  warn(message: string, ...args: any[]): void {
    this.log(LogLevel.WARN, message, ...args);
  }

  /**
   * Log errors (failures requiring attention)
   * Example: logger.error('OAuth token refresh failed', error)
   */
  error(message: string, ...args: any[]): void {
    this.log(LogLevel.ERROR, message, ...args);
  }

  /**
   * Set minimum log level at runtime
   * Useful for dynamic log level adjustment during debugging
   */
  setLevel(level: LogLevel): void {
    this.minimumLevel = level;
    this.info(`Log level changed to ${level}`);
  }

  /**
   * Get current minimum log level
   */
  getLevel(): LogLevel {
    return this.minimumLevel;
  }
}

/**
 * Singleton logger instance
 * Export as const to ensure immutable reference
 */
export const logger = new Logger();
