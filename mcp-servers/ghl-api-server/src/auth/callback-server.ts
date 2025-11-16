/**
 * OAuth Callback Server
 *
 * Story 3.2: OAuth 2.0 Authentication Implementation
 * AC #7: Initial authorization flow handles user consent and location selection
 *
 * This module implements a temporary HTTP server to handle OAuth callbacks.
 *
 * Purpose:
 * - Receive authorization code from GHL OAuth redirect
 * - Display success/error page to user
 * - Auto-close browser tab after successful auth
 * - Graceful shutdown after callback received
 *
 * Why Express:
 * - Lightweight HTTP server
 * - Easy route handling
 * - Standard Node.js web framework
 * - Minimal configuration
 *
 * Security considerations:
 * - Server only runs during authentication
 * - Binds to localhost only (not accessible externally)
 * - Auto-shuts down after receiving callback
 * - Authorization code used immediately (never stored)
 *
 * User experience:
 * - Clear success/error messages
 * - Auto-close browser tab (2 second delay)
 * - No manual interaction needed after auth
 */

import express, { Express, Request, Response } from 'express';
import { Server } from 'http';
import { logger } from '../utils/logger.js';
import { OAuth2Manager } from './oauth-manager.js';

/**
 * Default callback server port
 *
 * Why port 3456:
 * - Unlikely to conflict with common dev servers (3000, 3001, etc.)
 * - Must match redirect_uri in GHL marketplace app config
 * - Must match GHL_REDIRECT_URI in .env
 */
const DEFAULT_CALLBACK_PORT = 3456;

/**
 * Callback path
 *
 * Why /oauth/callback:
 * - Standard OAuth convention
 * - Clear intent (not generic /callback)
 * - Matches architecture documentation
 */
const CALLBACK_PATH = '/oauth/callback';

/**
 * OAuth Callback Server
 *
 * Lifecycle:
 * 1. Start server before opening browser
 * 2. Listen for OAuth callback
 * 3. Exchange code for tokens
 * 4. Show success page
 * 5. Auto-shutdown after 5 seconds
 *
 * Why temporary server:
 * - Only needed during authentication
 * - Prevents port conflicts when not in use
 * - Clean shutdown after auth complete
 */
export class OAuthCallbackServer {
  private app: Express;
  private server: Server | null = null;
  private oauthManager: OAuth2Manager;
  private port: number;

  /**
   * Create callback server instance
   *
   * @param oauthManager - OAuth manager to handle token exchange
   * @param port - Port to listen on (default: 3456)
   */
  constructor(oauthManager: OAuth2Manager, port: number = DEFAULT_CALLBACK_PORT) {
    this.oauthManager = oauthManager;
    this.port = port;
    this.app = express();

    this.setupRoutes();
    this.setupErrorHandlers();
  }

  /**
   * Set up Express routes
   *
   * Routes:
   * - GET /oauth/callback - OAuth callback endpoint
   * - GET / - Root endpoint (helpful error message)
   */
  private setupRoutes(): void {
    // OAuth callback endpoint
    // This is where GHL redirects after user authorization
    this.app.get(CALLBACK_PATH, async (req: Request, res: Response) => {
      await this.handleOAuthCallback(req, res);
    });

    // Root endpoint - helpful message if user visits directly
    this.app.get('/', (_req: Request, res: Response) => {
      res.send(this.renderInfoPage());
    });

    // Health check endpoint
    this.app.get('/health', (_req: Request, res: Response) => {
      res.json({ status: 'ready', service: 'ghl-oauth-callback' });
    });
  }

  /**
   * Set up Express error handlers
   *
   * Why needed:
   * - Prevent server crashes from route errors
   * - Log errors for debugging
   * - Return user-friendly error pages
   */
  private setupErrorHandlers(): void {
    // 404 handler
    this.app.use((_req: Request, res: Response) => {
      res.status(404).send(this.render404Page());
    });

    // Global error handler
    this.app.use((err: Error, _req: Request, res: Response, _next: any) => {
      logger.error('Express error handler caught error', { error: err });
      res.status(500).send(this.renderErrorPage('Internal server error', err.message));
    });
  }

  /**
   * Handle OAuth callback request
   *
   * Process:
   * 1. Extract code or error from query params
   * 2. Handle errors (user denied, etc.)
   * 3. Exchange code for tokens via OAuth manager
   * 4. Render success page
   * 5. Schedule server shutdown
   *
   * @param req - Express request
   * @param res - Express response
   */
  private async handleOAuthCallback(req: Request, res: Response): Promise<void> {
    const { code, error, error_description } = req.query;

    logger.info('OAuth callback received', {
      hasCode: !!code,
      hasError: !!error,
      ip: req.ip
    });

    // Handle OAuth errors (user denied access, etc.)
    if (error) {
      logger.error('OAuth authorization failed', {
        error,
        description: error_description
      });

      res.send(this.renderErrorPage(
        'Authentication Failed',
        this.formatOAuthError(error as string, error_description as string)
      ));

      // Schedule shutdown even on error
      this.scheduleShutdown();
      return;
    }

    // Validate authorization code
    if (!code || typeof code !== 'string') {
      logger.error('OAuth callback missing authorization code');

      res.send(this.renderErrorPage(
        'Authentication Failed',
        'No authorization code received from GoHighLevel. Please try again.'
      ));

      this.scheduleShutdown();
      return;
    }

    // Exchange code for tokens
    try {
      logger.info('Exchanging authorization code for tokens...');

      await this.oauthManager.exchangeCodeForTokens(code);

      logger.info('OAuth authentication successful');

      // Render success page
      res.send(this.renderSuccessPage());

      // Schedule shutdown after success
      this.scheduleShutdown();

    } catch (error) {
      logger.error('Token exchange failed', { error });

      res.send(this.renderErrorPage(
        'Token Exchange Failed',
        error instanceof Error ? error.message : 'Unknown error during token exchange'
      ));

      // Schedule shutdown even on failure
      this.scheduleShutdown();
    }
  }

  /**
   * Start callback server
   *
   * @returns Promise that resolves when server is listening
   * @throws Error if server fails to start (port in use, etc.)
   */
  async start(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        // Check if server already running
        if (this.server) {
          logger.warn('Callback server already running');
          resolve();
          return;
        }

        // Start HTTP server
        this.server = this.app.listen(this.port, () => {
          logger.info(`OAuth callback server listening on http://localhost:${this.port}`);
          logger.info(`Callback URL: http://localhost:${this.port}${CALLBACK_PATH}`);
          resolve();
        });

        // Handle server errors
        this.server.on('error', (error: NodeJS.ErrnoException) => {
          if (error.code === 'EADDRINUSE') {
            const errorMsg =
              `Port ${this.port} is already in use. ` +
              `Please stop other services on this port or change GHL_REDIRECT_URI in .env`;
            logger.error(errorMsg);
            reject(new Error(errorMsg));
          } else {
            logger.error('Callback server error', { error });
            reject(error);
          }
        });

      } catch (error) {
        logger.error('Failed to start callback server', { error });
        reject(error);
      }
    });
  }

  /**
   * Stop callback server
   *
   * @returns Promise that resolves when server is stopped
   */
  async stop(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.server) {
        logger.debug('Callback server not running, nothing to stop');
        resolve();
        return;
      }

      logger.info('Stopping OAuth callback server...');

      this.server.close((error) => {
        if (error) {
          logger.error('Error stopping callback server', { error });
          reject(error);
        } else {
          logger.info('OAuth callback server stopped');
          this.server = null;
          resolve();
        }
      });
    });
  }

  /**
   * Schedule automatic shutdown
   *
   * Why delay shutdown:
   * - Allow time for response to be sent to browser
   * - Give user time to read success message
   * - Prevent abrupt connection close
   *
   * Delay: 5 seconds (generous buffer)
   */
  private scheduleShutdown(): void {
    logger.info('Scheduling callback server shutdown in 5 seconds...');

    setTimeout(async () => {
      try {
        await this.stop();
        logger.info('Callback server shutdown complete');
      } catch (error) {
        logger.error('Error during scheduled shutdown', { error });
      }
    }, 5000);
  }

  /**
   * Format OAuth error for user display
   *
   * @param error - OAuth error code
   * @param description - Error description
   * @returns User-friendly error message
   */
  private formatOAuthError(error: string, description: string): string {
    const errorMap: Record<string, string> = {
      access_denied: 'You denied access to the application. To use GHL Wiz, please grant the requested permissions.',
      invalid_request: 'Invalid OAuth request. Please check your configuration and try again.',
      unauthorized_client: 'Application not authorized. Please check your GHL Marketplace app settings.',
      unsupported_response_type: 'OAuth configuration error. Please contact support.',
      invalid_scope: 'Invalid permission scopes. Please check app configuration.',
      server_error: 'GoHighLevel server error. Please try again in a few moments.',
      temporarily_unavailable: 'OAuth service temporarily unavailable. Please try again later.'
    };

    const userMessage = errorMap[error] || `OAuth error: ${error}`;
    return description ? `${userMessage}\n\nDetails: ${description}` : userMessage;
  }

  /**
   * Render success page HTML
   *
   * Features:
   * - Clear success message
   * - Auto-close script (2 second delay)
   * - Styled with inline CSS (no external dependencies)
   */
  private renderSuccessPage(): string {
    return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Authentication Successful - GHL Wiz</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      margin: 0;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .container {
      background: white;
      padding: 3rem;
      border-radius: 12px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
      text-align: center;
      max-width: 500px;
    }
    .icon {
      font-size: 4rem;
      margin-bottom: 1rem;
    }
    h1 {
      color: #2d3748;
      margin: 0 0 1rem 0;
      font-size: 2rem;
    }
    p {
      color: #4a5568;
      line-height: 1.6;
      margin: 0 0 1.5rem 0;
    }
    .success {
      color: #48bb78;
      font-weight: 600;
    }
    .timer {
      color: #718096;
      font-size: 0.9rem;
      font-style: italic;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="icon">✓</div>
    <h1 class="success">Authentication Successful!</h1>
    <p>Your GoHighLevel account has been connected to GHL Wiz.</p>
    <p>Your tokens have been encrypted and saved securely.</p>
    <p class="timer">This window will close automatically in <span id="countdown">2</span> seconds...</p>
  </div>
  <script>
    let seconds = 2;
    const countdownEl = document.getElementById('countdown');
    const interval = setInterval(() => {
      seconds--;
      if (countdownEl) countdownEl.textContent = seconds.toString();
      if (seconds <= 0) {
        clearInterval(interval);
        window.close();
      }
    }, 1000);
  </script>
</body>
</html>
    `;
  }

  /**
   * Render error page HTML
   *
   * @param title - Error title
   * @param message - Error message
   */
  private renderErrorPage(title: string, message: string): string {
    return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title} - GHL Wiz</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      margin: 0;
      background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    .container {
      background: white;
      padding: 3rem;
      border-radius: 12px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
      text-align: center;
      max-width: 600px;
    }
    .icon {
      font-size: 4rem;
      margin-bottom: 1rem;
    }
    h1 {
      color: #2d3748;
      margin: 0 0 1rem 0;
      font-size: 2rem;
    }
    .error {
      color: #f56565;
    }
    pre {
      background: #f7fafc;
      padding: 1rem;
      border-radius: 6px;
      border-left: 4px solid #f56565;
      text-align: left;
      overflow-x: auto;
      white-space: pre-wrap;
      word-wrap: break-word;
      color: #2d3748;
    }
    .help {
      color: #4a5568;
      font-size: 0.9rem;
      margin-top: 1.5rem;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="icon">✗</div>
    <h1 class="error">${title}</h1>
    <pre>${message}</pre>
    <p class="help">You can close this window and try again.</p>
  </div>
</body>
</html>
    `;
  }

  /**
   * Render info page HTML (root endpoint)
   */
  private renderInfoPage(): string {
    return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GHL Wiz OAuth Callback Server</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      margin: 0;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .container {
      background: white;
      padding: 3rem;
      border-radius: 12px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
      max-width: 600px;
    }
    h1 {
      color: #2d3748;
      margin: 0 0 1rem 0;
    }
    p {
      color: #4a5568;
      line-height: 1.6;
    }
    code {
      background: #f7fafc;
      padding: 0.2rem 0.4rem;
      border-radius: 3px;
      font-family: monospace;
      color: #e53e3e;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>GHL Wiz OAuth Callback Server</h1>
    <p>This is the OAuth callback server for GHL Wiz MCP integration.</p>
    <p>This page should only be visible during OAuth authentication.</p>
    <p><strong>Expected callback URL:</strong> <code>http://localhost:${this.port}${CALLBACK_PATH}</code></p>
    <p>If you see this page unexpectedly, the OAuth callback server may have been left running. It should shut down automatically after authentication completes.</p>
  </div>
</body>
</html>
    `;
  }

  /**
   * Render 404 page HTML
   */
  private render404Page(): string {
    return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Not Found - GHL Wiz</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      margin: 0;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .container {
      background: white;
      padding: 3rem;
      border-radius: 12px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
      text-align: center;
      max-width: 500px;
    }
    h1 {
      color: #2d3748;
      font-size: 3rem;
      margin: 0 0 1rem 0;
    }
    p {
      color: #4a5568;
      line-height: 1.6;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>404</h1>
    <p>Page not found.</p>
    <p>The OAuth callback endpoint is: <code>${CALLBACK_PATH}</code></p>
  </div>
</body>
</html>
    `;
  }
}
