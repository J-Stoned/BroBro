/**
 * Rate Limit MCP Tools
 *
 * Story 3.3: Rate Limiting & Error Handling
 * Provides tools to monitor and manage rate limiting state
 */

import { z } from 'zod';
import { rateLimiter } from '../utils/rate-limiter.js';
import { logger } from '../utils/logger.js';

/**
 * Get Rate Limit Status Tool
 *
 * Returns current rate limiting statistics including:
 * - Available burst tokens
 * - Daily quota remaining
 * - Queue status
 * - Total request counters
 */
export const getRateLimitStatusTool = {
  name: 'get_rate_limit_status',
  description: 'Get current rate limiting status including burst tokens available, daily quota remaining, and queue statistics.',
  schema: z.object({}),

  async handler(): Promise<string> {
    logger.debug('get_rate_limit_status tool invoked');

    const stats = rateLimiter.getStats();

    // Calculate percentages
    const burstUsagePercent = Math.round(
      ((stats.burstLimit - stats.burstTokens) / stats.burstLimit) * 100
    );
    const dailyUsagePercent = Math.round(
      (stats.dailyRequests / stats.dailyLimit) * 100
    );

    // Calculate time until reset
    const now = Date.now();
    const nextMidnight = stats.lastResetTime + 86400000; // +24 hours
    const hoursUntilReset = Math.floor((nextMidnight - now) / 3600000);
    const minutesUntilReset = Math.floor(((nextMidnight - now) % 3600000) / 60000);

    const response = {
      status: 'healthy',
      burst: {
        available: stats.burstTokens,
        limit: stats.burstLimit,
        used: stats.burstLimit - stats.burstTokens,
        usagePercent: burstUsagePercent,
        window: '10 seconds'
      },
      daily: {
        remaining: stats.dailyLimit - stats.dailyRequests,
        limit: stats.dailyLimit,
        used: stats.dailyRequests,
        usagePercent: dailyUsagePercent,
        resetsIn: `${hoursUntilReset}h ${minutesUntilReset}m`
      },
      queue: {
        length: stats.queueLength,
        status: stats.queueLength === 0 ? 'empty' : 'active'
      },
      statistics: {
        totalRequests: stats.totalRequests,
        throttledRequests: stats.throttledRequests,
        throttleRate: stats.totalRequests > 0
          ? `${Math.round((stats.throttledRequests / stats.totalRequests) * 100)}%`
          : '0%'
      },
      message: this.getStatusMessage(stats)
    };

    logger.info('Rate limit status retrieved', {
      burstTokens: stats.burstTokens,
      dailyRemaining: stats.dailyLimit - stats.dailyRequests,
      queueLength: stats.queueLength
    });

    return JSON.stringify(response, null, 2);
  },

  getStatusMessage(stats: any): string {
    const burstAvailable = stats.burstTokens;
    const dailyRemaining = stats.dailyLimit - stats.dailyRequests;

    if (burstAvailable === 0) {
      return 'BURST LIMIT REACHED - Requests are being queued';
    }

    if (dailyRemaining === 0) {
      return 'DAILY LIMIT REACHED - No more requests until midnight UTC';
    }

    if (burstAvailable < 10) {
      return 'WARNING - Approaching burst limit';
    }

    if (dailyRemaining < 1000) {
      return 'WARNING - Approaching daily limit';
    }

    return 'Rate limiting healthy - Operating normally';
  }
};

/**
 * Reset Rate Limits Tool (for testing)
 *
 * Resets all rate limiting counters and queues.
 * Should only be used in development/testing environments.
 */
export const resetRateLimitsTool = {
  name: 'reset_rate_limits',
  description: 'Reset all rate limiting counters and queues. FOR TESTING ONLY - Use with caution in production.',
  schema: z.object({
    confirm: z.boolean().describe('Must be true to confirm reset')
  }),

  async handler(args: { confirm: boolean }): Promise<string> {
    if (!args.confirm) {
      const response = {
        success: false,
        message: 'Reset cancelled - confirmation required',
        usage: 'Call with { confirm: true } to reset rate limits'
      };
      return JSON.stringify(response, null, 2);
    }

    logger.warn('Rate limits manually reset');

    rateLimiter.reset();

    const response = {
      success: true,
      message: 'Rate limits successfully reset',
      state: {
        burstTokens: 'Reset to full capacity',
        dailyQuota: 'Reset to full capacity',
        queue: 'Cleared',
        statistics: 'Reset to zero'
      },
      warning: 'This should only be used in development/testing environments'
    };

    return JSON.stringify(response, null, 2);
  }
};
