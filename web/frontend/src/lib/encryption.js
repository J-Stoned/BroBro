/**
 * Encryption Utilities - Epic 11: Story 11.2
 * AES-256-GCM encryption for API keys using Web Crypto API
 */

/**
 * Generate a random encryption key
 * Uses PBKDF2 to derive a key from a passphrase
 */
async function deriveKey(passphrase) {
  const encoder = new TextEncoder();
  const passphraseKey = await crypto.subtle.importKey(
    'raw',
    encoder.encode(passphrase),
    { name: 'PBKDF2' },
    false,
    ['deriveBits', 'deriveKey']
  );

  // Use salt stored in localStorage or generate new one
  let salt = localStorage.getItem('ghl_whiz_salt');
  if (!salt) {
    const saltBuffer = crypto.getRandomValues(new Uint8Array(16));
    salt = Array.from(saltBuffer).map(b => b.toString(16).padStart(2, '0')).join('');
    localStorage.setItem('ghl_whiz_salt', salt);
  }

  const saltBuffer = new Uint8Array(salt.match(/.{2}/g).map(byte => parseInt(byte, 16)));

  return crypto.subtle.deriveKey(
    {
      name: 'PBKDF2',
      salt: saltBuffer,
      iterations: 100000,
      hash: 'SHA-256'
    },
    passphraseKey,
    { name: 'AES-GCM', length: 256 },
    false,
    ['encrypt', 'decrypt']
  );
}

/**
 * Encrypt data using AES-256-GCM
 * @param {string} plaintext - Data to encrypt
 * @returns {Promise<string>} Base64 encoded encrypted data with IV
 */
export async function encrypt(plaintext) {
  try {
    // Use a device-specific passphrase (fingerprint)
    const passphrase = await getDeviceFingerprint();
    const key = await deriveKey(passphrase);

    // Generate random IV
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const encoder = new TextEncoder();
    const data = encoder.encode(plaintext);

    // Encrypt
    const encrypted = await crypto.subtle.encrypt(
      { name: 'AES-GCM', iv },
      key,
      data
    );

    // Combine IV and encrypted data
    const combined = new Uint8Array(iv.length + encrypted.byteLength);
    combined.set(iv, 0);
    combined.set(new Uint8Array(encrypted), iv.length);

    // Convert to base64
    return btoa(String.fromCharCode(...combined));
  } catch (error) {
    console.error('Encryption error:', error);
    throw new Error('Failed to encrypt data');
  }
}

/**
 * Decrypt data using AES-256-GCM
 * @param {string} ciphertext - Base64 encoded encrypted data
 * @returns {Promise<string>} Decrypted plaintext
 */
export async function decrypt(ciphertext) {
  try {
    const passphrase = await getDeviceFingerprint();
    const key = await deriveKey(passphrase);

    // Decode base64
    const combined = new Uint8Array(
      atob(ciphertext).split('').map(c => c.charCodeAt(0))
    );

    // Extract IV and encrypted data
    const iv = combined.slice(0, 12);
    const data = combined.slice(12);

    // Decrypt
    const decrypted = await crypto.subtle.decrypt(
      { name: 'AES-GCM', iv },
      key,
      data
    );

    const decoder = new TextDecoder();
    return decoder.decode(decrypted);
  } catch (error) {
    console.error('Decryption error:', error);
    throw new Error('Failed to decrypt data');
  }
}

/**
 * Generate a device fingerprint for encryption key derivation
 * Uses browser and device characteristics
 */
async function getDeviceFingerprint() {
  const components = [
    navigator.userAgent,
    navigator.language,
    new Date().getTimezoneOffset(),
    screen.width,
    screen.height,
    screen.colorDepth
  ].join('|');

  // Hash the fingerprint
  const encoder = new TextEncoder();
  const data = encoder.encode(components);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

/**
 * Store encrypted API key in localStorage
 */
export async function storeApiKey(apiKey, locationId) {
  try {
    const encrypted = await encrypt(JSON.stringify({ apiKey, locationId }));
    localStorage.setItem('ghl_whiz_credentials', encrypted);
    return true;
  } catch (error) {
    console.error('Failed to store API key:', error);
    return false;
  }
}

/**
 * Retrieve and decrypt API key from localStorage
 */
export async function getApiKey() {
  try {
    const encrypted = localStorage.getItem('ghl_whiz_credentials');
    if (!encrypted) return null;

    const decrypted = await decrypt(encrypted);
    return JSON.parse(decrypted);
  } catch (error) {
    console.error('Failed to retrieve API key:', error);
    return null;
  }
}

/**
 * Remove stored API key
 */
export function clearApiKey() {
  localStorage.removeItem('ghl_whiz_credentials');
  localStorage.removeItem('ghl_whiz_salt');
}

/**
 * Check if API key is stored
 */
export function hasStoredApiKey() {
  return localStorage.getItem('ghl_whiz_credentials') !== null;
}
