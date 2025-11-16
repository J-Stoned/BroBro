/**
 * Logging Utility for Knowledge Base Pipeline
 *
 * Provides console logging with color coding and file logging with timestamps.
 *
 * Usage:
 *   import { logger } from './utils/logger.js';
 *   logger.info('Processing started');
 *   logger.warn('Rate limit approaching');
 *   logger.error('Failed to scrape page', error);
 *   logger.success('Completed successfully');
 */

import fs from 'fs/promises';
import path from 'path';

// ANSI color codes
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  dim: '\x1b[2m',

  // Foreground colors
  black: '\x1b[30m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m',
  gray: '\x1b[90m',

  // Background colors
  bgRed: '\x1b[41m',
  bgGreen: '\x1b[42m',
  bgYellow: '\x1b[43m',
  bgBlue: '\x1b[44m'
};

/**
 * Logger class with console and file logging capabilities
 */
class Logger {
  constructor(logFilePath = null) {
    this.logFilePath = logFilePath;
    this.startTime = Date.now();
  }

  /**
   * Set log file path for file logging
   */
  setLogFile(filePath) {
    this.logFilePath = filePath;
  }

  /**
   * Get timestamp string
   */
  getTimestamp() {
    return new Date().toISOString();
  }

  /**
   * Get elapsed time since logger creation
   */
  getElapsed() {
    const elapsed = Date.now() - this.startTime;
    const seconds = (elapsed / 1000).toFixed(2);
    return `${seconds}s`;
  }

  /**
   * Format message with timestamp and level
   */
  formatMessage(level, message, includeElapsed = false) {
    const timestamp = this.getTimestamp();
    const elapsed = includeElapsed ? ` [${this.getElapsed()}]` : '';
    return `[${timestamp}]${elapsed} [${level}] ${message}`;
  }

  /**
   * Write to log file if configured
   */
  async writeToFile(message) {
    if (!this.logFilePath) return;

    try {
      // Ensure directory exists
      const dir = path.dirname(this.logFilePath);
      await fs.mkdir(dir, { recursive: true });

      // Append to log file
      await fs.appendFile(this.logFilePath, message + '\n', 'utf-8');
    } catch (err) {
      // If file logging fails, just output to console
      console.error(`Failed to write to log file: ${err.message}`);
    }
  }

  /**
   * Log info message (blue)
   */
  info(message) {
    const formatted = this.formatMessage('INFO', message);
    console.log(`${colors.blue}ℹ ${message}${colors.reset}`);
    this.writeToFile(formatted);
  }

  /**
   * Log success message (green)
   */
  success(message) {
    const formatted = this.formatMessage('SUCCESS', message);
    console.log(`${colors.green}✓ ${message}${colors.reset}`);
    this.writeToFile(formatted);
  }

  /**
   * Log warning message (yellow)
   */
  warn(message) {
    const formatted = this.formatMessage('WARN', message);
    console.warn(`${colors.yellow}⚠ ${message}${colors.reset}`);
    this.writeToFile(formatted);
  }

  /**
   * Log error message (red)
   */
  error(message, err = null) {
    const errorDetails = err ? `\n${err.stack || err.message || err}` : '';
    const formatted = this.formatMessage('ERROR', message + errorDetails);
    console.error(`${colors.red}✗ ${message}${colors.reset}`);
    if (err) {
      console.error(`${colors.gray}${err.stack || err.message || err}${colors.reset}`);
    }
    this.writeToFile(formatted);
  }

  /**
   * Log debug message (gray, only in verbose mode)
   */
  debug(message) {
    if (!process.env.DEBUG) return;

    const formatted = this.formatMessage('DEBUG', message);
    console.log(`${colors.gray}• ${message}${colors.reset}`);
    this.writeToFile(formatted);
  }

  /**
   * Log progress (cyan with elapsed time)
   */
  progress(message) {
    const formatted = this.formatMessage('PROGRESS', message, true);
    console.log(`${colors.cyan}⟳ ${message} [${this.getElapsed()}]${colors.reset}`);
    this.writeToFile(formatted);
  }

  /**
   * Log step header (bright blue)
   */
  step(stepName) {
    const separator = '='.repeat(60);
    const formatted = this.formatMessage('STEP', stepName);
    console.log(`\n${colors.bright}${colors.blue}${separator}${colors.reset}`);
    console.log(`${colors.bright}${colors.blue}  ${stepName}${colors.reset}`);
    console.log(`${colors.bright}${colors.blue}${separator}${colors.reset}\n`);
    this.writeToFile(`\n${separator}\n${formatted}\n${separator}\n`);
  }

  /**
   * Log detail message (gray)
   */
  detail(message) {
    console.log(`${colors.gray}  ${message}${colors.reset}`);
    this.writeToFile(`  ${message}`);
  }

  /**
   * Log statistics summary
   */
  stats(stats) {
    const formatted = this.formatMessage('STATS', JSON.stringify(stats));
    console.log(`\n${colors.bright}${colors.cyan}Statistics:${colors.reset}`);
    Object.entries(stats).forEach(([key, value]) => {
      const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
      console.log(`${colors.cyan}  ${label}: ${colors.bright}${value}${colors.reset}`);
    });
    console.log('');
    this.writeToFile(formatted);
  }

  /**
   * Create a progress bar
   */
  progressBar(current, total, label = '') {
    const percentage = Math.round((current / total) * 100);
    const barLength = 40;
    const filled = Math.round((current / total) * barLength);
    const empty = barLength - filled;
    const bar = '█'.repeat(filled) + '░'.repeat(empty);

    const message = `${label} ${bar} ${current}/${total} (${percentage}%)`;

    // Use \r to overwrite the same line
    process.stdout.write(`\r${colors.cyan}⟳ ${message}${colors.reset}`);

    // New line when complete
    if (current === total) {
      process.stdout.write('\n');
      this.writeToFile(this.formatMessage('PROGRESS', message));
    }
  }

  /**
   * Clear last console line (for progress updates)
   */
  clearLine() {
    process.stdout.write('\r\x1b[K');
  }
}

/**
 * Create logger instance
 */
export function createLogger(logFilePath = null) {
  return new Logger(logFilePath);
}

/**
 * Default logger instance
 */
export const logger = new Logger();

/**
 * Export colors for custom formatting
 */
export { colors };
