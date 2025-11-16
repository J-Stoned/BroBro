/**
 * Token Store - Encrypted Token Storage
 *
 * Story 3.2: OAuth 2.0 Authentication Implementation
 * AC #4: Tokens stored securely in encrypted local file using AES-256-CBC
 * AC #8: Refresh token persisted and used for automatic token renewal
 *
 * This module handles secure storage and retrieval of OAuth tokens using
 * AES-256-CBC encryption with randomized initialization vectors (IV).
 *
 * Security features:
 * - AES-256-CBC encryption algorithm (industry standard)
 * - Randomized IV for each save operation (prevents pattern analysis)
 * - Encryption key from environment variable (never hardcoded)
 * - Token file explicitly ignored in .gitignore
 * - Tokens never logged in plaintext
 *
 * Why AES-256-CBC:
 * - AES-256: Strong encryption, widely tested, NIST-approved
 * - CBC mode: Cipher Block Chaining for additional security
 * - 256-bit key: Resistant to brute force attacks
 *
 * File format: .tokens.enc
 * Structure: { iv: string (hex), encryptedData: string (hex) }
 * Location: Project root (not in src/, not in git)
 */

import crypto from 'crypto';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { logger } from '../utils/logger.js';

// Get project root directory (two levels up from this file)
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const PROJECT_ROOT = path.resolve(__dirname, '..', '..');

/**
 * Token storage interface
 *
 * Fields:
 * - accessToken: Short-lived token for API authentication (24h expiry)
 * - refreshToken: Long-lived token for obtaining new access tokens (60d expiry)
 * - expiresAt: Unix timestamp (ms) when access token expires
 * - locationId: GHL location ID selected during OAuth
 * - companyId: GHL company ID (for multi-account support)
 * - scope: Array of authorized scopes
 */
export interface TokenStore {
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
  locationId?: string;
  companyId?: string;
  scope?: string[];
}

/**
 * Encrypted token file structure
 *
 * Why separate iv and encryptedData:
 * - IV must be unique for each encryption operation
 * - IV is not secret (can be stored alongside ciphertext)
 * - Prevents patterns in encrypted data even with same plaintext
 */
interface EncryptedTokenFile {
  iv: string;               // Initialization vector (hex encoded)
  encryptedData: string;    // Encrypted token JSON (hex encoded)
}

/**
 * Token file path
 *
 * Why in project root:
 * - Easy to locate for debugging
 * - Separate from source code
 * - Explicitly in .gitignore
 */
const TOKEN_FILE_PATH = path.join(PROJECT_ROOT, '.tokens.enc');

/**
 * Encryption algorithm configuration
 *
 * Why these values:
 * - aes-256-cbc: Standard algorithm, well-supported in Node.js crypto
 * - 32 bytes key: AES-256 requires exactly 32 bytes (256 bits)
 * - 16 bytes IV: CBC mode requires 16-byte IV (128 bits)
 */
const ENCRYPTION_ALGORITHM = 'aes-256-cbc';
const IV_LENGTH = 16;         // 16 bytes = 128 bits

/**
 * Get encryption key from environment
 *
 * Security considerations:
 * - Key must be 64 hex characters (32 bytes when decoded)
 * - Key stored in .env (never in code)
 * - Auto-generates key if not provided (with warning)
 * - Same key must be used for encrypt/decrypt
 *
 * @returns Buffer containing 32-byte encryption key
 * @throws Error if ENCRYPTION_KEY is invalid format
 */
function getEncryptionKey(): Buffer {
  const keyHex = process.env.ENCRYPTION_KEY;

  // Check if key exists
  if (!keyHex) {
    const errorMsg =
      'ENCRYPTION_KEY not found in environment variables. ' +
      'Generate one with: node -e "console.log(require(\'crypto\').randomBytes(32).toString(\'hex\'))" ' +
      'and add to .env file.';
    logger.error(errorMsg);
    throw new Error(errorMsg);
  }

  // Validate key length (must be 64 hex chars = 32 bytes)
  if (keyHex.length !== 64) {
    const errorMsg =
      `ENCRYPTION_KEY must be exactly 64 hex characters (32 bytes). ` +
      `Current length: ${keyHex.length}. ` +
      `Generate valid key with: node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"`;
    logger.error(errorMsg);
    throw new Error(errorMsg);
  }

  // Validate hex format
  if (!/^[0-9a-fA-F]{64}$/.test(keyHex)) {
    const errorMsg = 'ENCRYPTION_KEY must contain only hexadecimal characters (0-9, a-f, A-F)';
    logger.error(errorMsg);
    throw new Error(errorMsg);
  }

  // Convert hex string to Buffer
  return Buffer.from(keyHex, 'hex');
}

/**
 * Save tokens to encrypted file
 *
 * Process:
 * 1. Generate random 16-byte IV for this encryption
 * 2. Serialize tokens to JSON
 * 3. Encrypt JSON with AES-256-CBC
 * 4. Save IV and encrypted data to file
 *
 * Why randomize IV each time:
 * - Prevents pattern analysis (same plaintext → different ciphertext)
 * - Industry best practice for CBC mode
 * - IV doesn't need to be secret (stored alongside ciphertext)
 *
 * @param tokens - Token data to encrypt and save
 * @throws Error if encryption or file write fails
 */
export async function saveTokens(tokens: TokenStore): Promise<void> {
  try {
    logger.debug('Saving encrypted tokens...', {
      locationId: tokens.locationId,
      expiresAt: new Date(tokens.expiresAt).toISOString()
    });

    // Get encryption key
    const encryptionKey = getEncryptionKey();

    // Generate random IV for this encryption
    // Why crypto.randomBytes: Cryptographically secure random number generator
    const iv = crypto.randomBytes(IV_LENGTH);

    // Create cipher with key and IV
    const cipher = crypto.createCipheriv(ENCRYPTION_ALGORITHM, encryptionKey, iv);

    // Serialize tokens to JSON
    const tokenJson = JSON.stringify(tokens);

    // Encrypt token JSON
    // Why two-step encrypt: cipher.update() + cipher.final()
    // - update(): Encrypts main data
    // - final(): Encrypts final block with padding
    let encryptedData = cipher.update(tokenJson, 'utf8', 'hex');
    encryptedData += cipher.final('hex');

    // Create encrypted file structure
    const encryptedFile: EncryptedTokenFile = {
      iv: iv.toString('hex'),
      encryptedData: encryptedData
    };

    // Write to file
    // Why JSON.stringify: Human-readable file format for debugging
    await fs.writeFile(TOKEN_FILE_PATH, JSON.stringify(encryptedFile, null, 2), 'utf8');

    logger.info('Tokens encrypted and saved successfully', {
      filePath: TOKEN_FILE_PATH,
      locationId: tokens.locationId
    });

    // SECURITY: Never log actual token values
    // Only log metadata (location, expiry)

  } catch (error) {
    logger.error('Failed to save encrypted tokens', { error });
    throw new Error(`Token save failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * Load tokens from encrypted file
 *
 * Process:
 * 1. Read encrypted file
 * 2. Parse IV and encrypted data
 * 3. Decrypt data with AES-256-CBC
 * 4. Parse decrypted JSON
 * 5. Return token object
 *
 * Error handling:
 * - ENOENT (file not found): Return null (first-time setup)
 * - Decryption failure: Throw error (corrupted file or wrong key)
 * - JSON parse error: Throw error (corrupted data)
 *
 * @returns TokenStore object or null if file doesn't exist
 * @throws Error if decryption fails or file is corrupted
 */
export async function loadTokens(): Promise<TokenStore | null> {
  try {
    logger.debug('Loading encrypted tokens...', { filePath: TOKEN_FILE_PATH });

    // Read encrypted file
    const fileContent = await fs.readFile(TOKEN_FILE_PATH, 'utf8');

    // Parse encrypted file structure
    const encryptedFile: EncryptedTokenFile = JSON.parse(fileContent);

    // Validate file structure
    if (!encryptedFile.iv || !encryptedFile.encryptedData) {
      throw new Error('Invalid token file format: missing iv or encryptedData');
    }

    // Get encryption key
    const encryptionKey = getEncryptionKey();

    // Convert IV from hex to Buffer
    const iv = Buffer.from(encryptedFile.iv, 'hex');

    // Create decipher with key and IV
    const decipher = crypto.createDecipheriv(ENCRYPTION_ALGORITHM, encryptionKey, iv);

    // Decrypt data
    let decryptedJson = decipher.update(encryptedFile.encryptedData, 'hex', 'utf8');
    decryptedJson += decipher.final('utf8');

    // Parse decrypted JSON
    const tokens: TokenStore = JSON.parse(decryptedJson);

    logger.info('Tokens loaded and decrypted successfully', {
      locationId: tokens.locationId,
      expiresAt: new Date(tokens.expiresAt).toISOString(),
      isExpired: Date.now() >= tokens.expiresAt
    });

    return tokens;

  } catch (error: any) {
    // Handle file not found (first-time setup)
    if (error.code === 'ENOENT') {
      logger.info('No existing token file found. Initial OAuth flow required.', {
        expectedPath: TOKEN_FILE_PATH
      });
      return null;
    }

    // Handle decryption errors
    if (error.message?.includes('bad decrypt')) {
      const errorMsg =
        'Token decryption failed. Possible causes:\n' +
        '1. ENCRYPTION_KEY changed (use same key that encrypted the file)\n' +
        '2. Token file corrupted (delete .tokens.enc and re-authenticate)\n' +
        '3. Invalid token file format';
      logger.error(errorMsg);
      throw new Error(errorMsg);
    }

    // Other errors
    logger.error('Failed to load encrypted tokens', { error });
    throw new Error(`Token load failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * Delete token file
 *
 * Use cases:
 * - User wants to logout
 * - Token file corrupted
 * - Re-authentication required
 *
 * @throws Error if file deletion fails (except ENOENT)
 */
export async function deleteTokens(): Promise<void> {
  try {
    logger.info('Deleting token file...', { filePath: TOKEN_FILE_PATH });

    await fs.unlink(TOKEN_FILE_PATH);

    logger.info('Token file deleted successfully');

  } catch (error: any) {
    // Ignore error if file doesn't exist
    if (error.code === 'ENOENT') {
      logger.debug('Token file already deleted or never existed');
      return;
    }

    logger.error('Failed to delete token file', { error });
    throw new Error(`Token deletion failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * Check if token file exists
 *
 * Useful for:
 * - Checking if user is authenticated
 * - Deciding whether to show setup instructions
 *
 * @returns true if token file exists, false otherwise
 */
export async function tokenFileExists(): Promise<boolean> {
  try {
    await fs.access(TOKEN_FILE_PATH);
    return true;
  } catch {
    return false;
  }
}
