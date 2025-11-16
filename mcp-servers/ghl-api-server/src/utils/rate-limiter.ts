/**
 * Rate Limiter - GHL API Rate Limiting
 *
 * Story 3.3: Rate Limiting & Error Handling
 * AC #1: Rate limiter enforces max 100 requests per 10 seconds
 * AC #2: Daily limit tracker enforces max 200,000 requests per day
 * AC #3: Requests queued with exponential backoff when limits approached
 *
 * This module implements token bucket rate limiting for GHL API compliance.
 *
 * Rate Limits (per GHL API documentation):
 * - Burst: 100 requests per 10 seconds (sliding window)
 * - Daily: 200,000 requests per day (UTC reset)
 *
 * Why Token Bucket Algorithm:
 * - Allows burst traffic up to limit (better UX than fixed rate)
 * - Smooths out request spikes
 * - Industry standard (used by AWS, Stripe, etc.)
 * - Easy to reason about and test
 *
 * Queue Behavior:
 * - Requests queue when burst limit reached
 * - Exponential backoff: 1s, 2s, 4s, 8s (max 30s)
 * - Max queue size: 1000 requests
 * - Queue timeout: 60 seconds per request
 */

import { logger } from './logger.js';

/**
 * Rate limiter configuration options
 */
export interface RateLimiterConfig {
  /** Burst limit (requests per window) */
  burstLimit?: number;
  /** Burst window size in milliseconds */
  burstWindow?: number;
  /** Daily request limit */
  dailyLimit?: number;
  /** Maximum queue size */
  maxQueueSize?: number;
  /** Maximum wait time for queued requests (ms) */
  queueTimeout?: number;
  /** Base delay for exponential backoff (ms) */
  baseDelay?: number;
  /** Maximum delay for exponential backoff (ms) */
  maxDelay?: number;
}

/**
 * Queued request interface
 */
interface QueuedRequest<T> {
  fn: () => Promise<T>;
  resolve: (value: T) => void;
  reject: (error: Error) => void;
  timestamp: number;
  retries: number;
}

/**
 * Rate limiter statistics
 */
export interface RateLimiterStats {
  burstTokens: number;
  burstLimit: number;
  dailyRequests: number;
  dailyLimit: number;
  queueLength: number;
  totalRequests: number;
  throttledRequests: number;
  lastResetTime: number;
}

/**
 * Token Bucket Rate Limiter
 *
 * Implements dual-layer rate limiting:
 * 1. Burst limiting with token bucket (100 req/10s)
 * 2. Daily quota tracking (200k req/day)
 */
export class RateLimiter {
  // Configuration
  private burstLimit: number;
  private burstWindow: number;
  private dailyLimit: number;
  private maxQueueSize: number;
  private queueTimeout: number;
  private baseDelay: number;
  private maxDelay: number;

  // Burst limiting state
  private requestTimestamps: number[] = [];

  // Daily quota state
  private dailyRequests: number = 0;
  private lastResetTime: number = this.getMidnightUTC();

  // Queue management
  private queue: QueuedRequest<any>[] = [];
  private isProcessingQueue: boolean = false;

  // Statistics
  private totalRequests: number = 0;
  private throttledRequests: number = 0;

  constructor(config: RateLimiterConfig = {}) {
    this.burstLimit = config.burstLimit ?? 100;
    this.burstWindow = config.burstWindow ?? 10000; // 10 seconds
    this.dailyLimit = config.dailyLimit ?? 200000;
    this.maxQueueSize = config.maxQueueSize ?? 1000;
    this.queueTimeout = config.queueTimeout ?? 60000; // 60 seconds
    this.baseDelay = config.baseDelay ?? 1000; // 1 second
    this.maxDelay = config.maxDelay ?? 30000; // 30 seconds

    logger.info('Rate limiter initialized', {
      burstLimit: this.burstLimit,
      burstWindow: `${this.burstWindow}ms`,
      dailyLimit: this.dailyLimit,
      maxQueueSize: this.maxQueueSize
    });
  }

  /**
   * Execute function with rate limiting
   *
   * This is the main entry point for rate-limited API calls.
   * It checks limits, queues if necessary, and executes the function.
   *
   * @param fn Function to execute
   * @returns Promise resolving to function result
   */
  async execute<T>(fn: () => Promise<T>): Promise<T> {
    // Check if we can execute immediately
    if (this.canExecuteNow()) {
      return await this.executeImmediately(fn);
    }

    // Queue the request
    return await this.queueRequest(fn);
  }

  /**
   * Check if request can execute immediately
   */
  private canExecuteNow(): boolean {
    this.cleanupOldRequests();
    this.resetDailyCounterIfNeeded();

    const burstAvailable = this.requestTimestamps.length < this.burstLimit;
    const dailyAvailable = this.dailyRequests < this.dailyLimit;

    return burstAvailable && dailyAvailable;
  }

  /**
   * Execute request immediately (no queuing)
   */
  private async executeImmediately<T>(fn: () => Promise<T>): Promise<T> {
    this.recordRequest();
    this.totalRequests++;

    logger.debug('Executing request immediately', {
      burstUsed: this.requestTimestamps.length,
      burstLimit: this.burstLimit,
      dailyUsed: this.dailyRequests,
      dailyLimit: this.dailyLimit
    });

    return await fn();
  }

  /**
   * Queue request for later execution
   */
  private async queueRequest<T>(fn: () => Promise<T>): Promise<T> {
    if (this.queue.length >= this.maxQueueSize) {
      this.throttledRequests++;
      throw new Error(
        `Rate limit queue full (${this.maxQueueSize} requests). ` +
        `Please try again in ${Math.ceil(this.burstWindow / 1000)} seconds.`
      );
    }

    this.throttledRequests++;

    logger.warn('Request queued due to rate limiting', {
      queueLength: this.queue.length + 1,
      burstUsed: this.requestTimestamps.length,
      dailyUsed: this.dailyRequests
    });

    return new Promise<T>((resolve, reject) => {
      this.queue.push({
        fn,
        resolve,
        reject,
        timestamp: Date.now(),
        retries: 0
      });

      // Start processing queue if not already running
      if (!this.isProcessingQueue) {
        this.processQueue();
      }
    });
  }

  /**
   * Process queued requests with exponential backoff
   */
  private async processQueue(): Promise<void> {
    if (this.isProcessingQueue) {
      return; // Already processing
    }

    this.isProcessingQueue = true;

    while (this.queue.length > 0) {
      // Check if we can execute the next request
      if (!this.canExecuteNow()) {
        // Calculate delay based on current state
        const delay = this.calculateBackoffDelay(0);
        logger.debug('Queue processing delayed', {
          delay: `${delay}ms`,
          queueLength: this.queue.length
        });
        await this.sleep(delay);
        continue;
      }

      // Get next request from queue
      const request = this.queue.shift();
      if (!request) break;

      // Check for timeout
      const waitTime = Date.now() - request.timestamp;
      if (waitTime > this.queueTimeout) {
        request.reject(new Error(
          `Request timed out after ${Math.ceil(waitTime / 1000)}s in queue`
        ));
        logger.warn('Queued request timed out', { waitTime: `${waitTime}ms` });
        continue;
      }

      // Execute request
      try {
        const result = await this.executeImmediately(request.fn);
        request.resolve(result);
        logger.debug('Queued request executed successfully', {
          waitTime: `${waitTime}ms`,
          remainingQueue: this.queue.length
        });
      } catch (error) {
        // Check if we should retry
        if (this.shouldRetry(error, request.retries)) {
          request.retries++;
          const retryDelay = this.calculateBackoffDelay(request.retries);
          logger.info('Retrying queued request', {
            attempt: request.retries + 1,
            delay: `${retryDelay}ms`
          });
          await this.sleep(retryDelay);
          this.queue.unshift(request); // Put back at front of queue
        } else {
          request.reject(error instanceof Error ? error : new Error(String(error)));
          logger.error('Queued request failed after retries', { error });
        }
      }
    }

    this.isProcessingQueue = false;
    logger.debug('Queue processing complete');
  }

  /**
   * Record a request execution
   */
  private recordRequest(): void {
    const now = Date.now();
    this.requestTimestamps.push(now);
    this.dailyRequests++;
  }

  /**
   * Clean up old requests outside the burst window
   */
  private cleanupOldRequests(): void {
    const now = Date.now();
    const cutoff = now - this.burstWindow;
    this.requestTimestamps = this.requestTimestamps.filter(ts => ts > cutoff);
  }

  /**
   * Reset daily counter at UTC midnight
   */
  private resetDailyCounterIfNeeded(): void {
    const currentMidnight = this.getMidnightUTC();

    if (currentMidnight > this.lastResetTime) {
      logger.info('Resetting daily request counter', {
        previousCount: this.dailyRequests,
        previousReset: new Date(this.lastResetTime).toISOString()
      });
      this.dailyRequests = 0;
      this.lastResetTime = currentMidnight;
    }
  }

  /**
   * Get UTC midnight timestamp for today
   */
  private getMidnightUTC(): number {
    const now = new Date();
    const midnight = new Date(Date.UTC(
      now.getUTCFullYear(),
      now.getUTCMonth(),
      now.getUTCDate(),
      0, 0, 0, 0
    ));
    return midnight.getTime();
  }

  /**
   * Calculate exponential backoff delay
   */
  private calculateBackoffDelay(attempt: number): number {
    const delay = this.baseDelay * Math.pow(2, attempt);
    return Math.min(delay, this.maxDelay);
  }

  /**
   * Determine if error is retryable
   */
  private shouldRetry(error: unknown, retries: number): boolean {
    const maxRetries = 3;
    if (retries >= maxRetries) {
      return false;
    }

    // Retry on transient errors
    if (error instanceof Error) {
      const message = error.message.toLowerCase();
      return (
        message.includes('timeout') ||
        message.includes('network') ||
        message.includes('econnreset') ||
        message.includes('econnrefused') ||
        message.includes('5') // 5xx errors
      );
    }

    return false;
  }

  /**
   * Sleep utility
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Get current rate limiter statistics
   */
  getStats(): RateLimiterStats {
    this.cleanupOldRequests();
    this.resetDailyCounterIfNeeded();

    return {
      burstTokens: this.burstLimit - this.requestTimestamps.length,
      burstLimit: this.burstLimit,
      dailyRequests: this.dailyRequests,
      dailyLimit: this.dailyLimit,
      queueLength: this.queue.length,
      totalRequests: this.totalRequests,
      throttledRequests: this.throttledRequests,
      lastResetTime: this.lastResetTime
    };
  }

  /**
   * Reset rate limiter state (for testing)
   */
  reset(): void {
    this.requestTimestamps = [];
    this.dailyRequests = 0;
    this.lastResetTime = this.getMidnightUTC();
    this.queue = [];
    this.isProcessingQueue = false;
    this.totalRequests = 0;
    this.throttledRequests = 0;
    logger.info('Rate limiter reset');
  }
}

// Export singleton instance
export const rateLimiter = new RateLimiter();
