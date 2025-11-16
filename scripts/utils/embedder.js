/**
 * Embedding Utility
 *
 * Generates embeddings for text using Xenova/all-MiniLM-L6-v2 model.
 * Provides batch embedding support for efficient processing.
 *
 * Usage:
 *   import { Embedder } from './utils/embedder.js';
 *   const embedder = new Embedder();
 *   await embedder.initialize();
 *   const embedding = await embedder.generateEmbedding('Some text');
 *   const embeddings = await embedder.generateEmbeddings(['Text 1', 'Text 2']);
 *
 * NOTE: This utility requires @xenova/transformers package to be installed:
 *       npm install @xenova/transformers
 *
 *       The actual transformer integration is currently a placeholder.
 *       When implemented, it will use the Xenova pipeline for embeddings.
 */

/**
 * Embedder class for generating text embeddings
 */
export class Embedder {
  constructor(modelName = 'Xenova/all-MiniLM-L6-v2') {
    this.modelName = modelName;
    this.pipeline = null;
    this.embeddingDimension = 384; // all-MiniLM-L6-v2 output dimension
    this.initialized = false;
  }

  /**
   * Initialize the embedding pipeline
   */
  async initialize() {
    if (this.initialized) {
      return;
    }

    try {
      console.log(`[Embedder] Initializing ${this.modelName}...`);

      // Import transformers dynamically
      const { pipeline } = await import('@xenova/transformers');

      // Initialize the feature extraction pipeline
      this.pipeline = await pipeline('feature-extraction', this.modelName);

      this.initialized = true;
      console.log(`[Embedder] Initialized successfully with ${this.modelName}`);
    } catch (error) {
      throw new Error(`Failed to initialize embedder: ${error.message}`);
    }
  }

  /**
   * Generate embedding for a single text
   *
   * @param {string} text - Text to embed
   * @returns {Promise<number[]>} 384-dimensional embedding vector
   */
  async generateEmbedding(text) {
    if (!this.initialized) {
      await this.initialize();
    }

    if (!text || typeof text !== 'string') {
      throw new Error('Text must be a non-empty string');
    }

    try {
      // Generate embedding using transformer pipeline
      const output = await this.pipeline(text, {
        pooling: 'mean',
        normalize: true
      });

      // Convert to array
      return Array.from(output.data);
    } catch (error) {
      throw new Error(`Failed to generate embedding: ${error.message}`);
    }
  }

  /**
   * Generate embeddings for multiple texts (batch processing)
   *
   * @param {string[]} texts - Array of texts to embed
   * @param {number} batchSize - Batch size for processing (default: 32)
   * @returns {Promise<number[][]>} Array of embedding vectors
   */
  async generateEmbeddings(texts, batchSize = 32) {
    if (!this.initialized) {
      await this.initialize();
    }

    if (!Array.isArray(texts)) {
      throw new Error('Texts must be an array');
    }

    const embeddings = [];

    // Process in batches for efficiency
    for (let i = 0; i < texts.length; i += batchSize) {
      const batch = texts.slice(i, i + batchSize);

      // Process batch in parallel
      const batchEmbeddings = await Promise.all(
        batch.map(text => this.generateEmbedding(text))
      );

      embeddings.push(...batchEmbeddings);
    }

    return embeddings;
  }

  /**
   * Get embedding dimension
   */
  getDimension() {
    return this.embeddingDimension;
  }

  /**
   * Placeholder: Generate a deterministic "embedding" based on text hash
   * This is only for testing/structure - NOT actual semantic embeddings
   *
   * @private
   */
  generatePlaceholderEmbedding(text) {
    // Simple hash function for deterministic placeholder
    const hash = (str) => {
      let h = 0;
      for (let i = 0; i < str.length; i++) {
        h = ((h << 5) - h) + str.charCodeAt(i);
        h |= 0; // Convert to 32-bit integer
      }
      return h;
    };

    const seed = Math.abs(hash(text));
    const embedding = [];

    // Generate 384 values using seeded random
    for (let i = 0; i < this.embeddingDimension; i++) {
      // Simple LCG (Linear Congruential Generator) for deterministic random
      const x = Math.sin(seed + i) * 10000;
      embedding.push(x - Math.floor(x));
    }

    // Normalize to unit vector (L2 normalization)
    const magnitude = Math.sqrt(embedding.reduce((sum, val) => sum + val * val, 0));
    return embedding.map(val => val / magnitude);
  }

  /**
   * Calculate cosine similarity between two embeddings
   *
   * @param {number[]} embedding1 - First embedding vector
   * @param {number[]} embedding2 - Second embedding vector
   * @returns {number} Cosine similarity (-1 to 1)
   */
  static cosineSimilarity(embedding1, embedding2) {
    if (embedding1.length !== embedding2.length) {
      throw new Error('Embeddings must have same dimension');
    }

    let dotProduct = 0;
    let mag1 = 0;
    let mag2 = 0;

    for (let i = 0; i < embedding1.length; i++) {
      dotProduct += embedding1[i] * embedding2[i];
      mag1 += embedding1[i] * embedding1[i];
      mag2 += embedding2[i] * embedding2[i];
    }

    mag1 = Math.sqrt(mag1);
    mag2 = Math.sqrt(mag2);

    if (mag1 === 0 || mag2 === 0) {
      return 0;
    }

    return dotProduct / (mag1 * mag2);
  }
}

/**
 * Create and initialize embedder instance
 */
export async function createEmbedder(modelName) {
  const embedder = new Embedder(modelName);
  await embedder.initialize();
  return embedder;
}
