/**
 * Semantic Chunking Utility
 *
 * Chunks markdown documents while preserving structure and code blocks.
 * Uses simple tokenization approximation (~0.75 words per token).
 *
 * Usage:
 *   import { chunkDocument } from './utils/chunker.js';
 *   const chunks = chunkDocument(markdown, { title: 'Doc Title', url: '...' });
 */

/**
 * Simple tokenization approximation
 * Assumes ~0.75 words per token (GPT-style tokenization approximation)
 */
function estimateTokens(text) {
  const words = text.trim().split(/\s+/).filter(w => w.length > 0);
  return Math.ceil(words.length * 0.75);
}

/**
 * Extract markdown structure elements
 */
function parseMarkdownStructure(markdown) {
  const lines = markdown.split('\n');
  const elements = [];
  let currentElement = null;
  let inCodeBlock = false;
  let codeBlockContent = [];
  let codeBlockStart = 0;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();

    // Code block boundaries
    if (trimmed.startsWith('```')) {
      if (!inCodeBlock) {
        // Start of code block
        inCodeBlock = true;
        codeBlockContent = [line];
        codeBlockStart = i;
      } else {
        // End of code block
        codeBlockContent.push(line);
        elements.push({
          type: 'code',
          content: codeBlockContent.join('\n'),
          lineStart: codeBlockStart,
          lineEnd: i
        });
        inCodeBlock = false;
        codeBlockContent = [];
      }
      continue;
    }

    // Inside code block - accumulate
    if (inCodeBlock) {
      codeBlockContent.push(line);
      continue;
    }

    // Heading
    const headingMatch = trimmed.match(/^(#{1,6})\s+(.+)$/);
    if (headingMatch) {
      elements.push({
        type: 'heading',
        level: headingMatch[1].length,
        content: line,
        text: headingMatch[2],
        lineStart: i,
        lineEnd: i
      });
      continue;
    }

    // Empty line - paragraph boundary
    if (trimmed === '') {
      if (currentElement && currentElement.type === 'paragraph') {
        elements.push(currentElement);
        currentElement = null;
      }
      continue;
    }

    // Regular text - accumulate into paragraph
    if (!currentElement || currentElement.type !== 'paragraph') {
      currentElement = {
        type: 'paragraph',
        content: line,
        lineStart: i,
        lineEnd: i
      };
    } else {
      currentElement.content += '\n' + line;
      currentElement.lineEnd = i;
    }
  }

  // Add final element if exists
  if (currentElement) {
    elements.push(currentElement);
  }

  // Handle unclosed code block
  if (inCodeBlock) {
    elements.push({
      type: 'code',
      content: codeBlockContent.join('\n'),
      lineStart: codeBlockStart,
      lineEnd: lines.length - 1
    });
  }

  return elements;
}

/**
 * Chunk a document semantically
 *
 * @param {string} markdown - Markdown content
 * @param {object} metadata - Document metadata (title, url, category, etc.)
 * @param {object} options - Chunking options
 * @returns {Array} Array of chunks with metadata
 */
export function chunkDocument(markdown, metadata = {}, options = {}) {
  const {
    chunkSize = 512,        // Target chunk size in tokens
    overlap = 0.10,         // Overlap percentage (default 10%)
    minChunkSize = 100      // Minimum chunk size in tokens
  } = options;

  const overlapTokens = Math.ceil(chunkSize * overlap);
  const elements = parseMarkdownStructure(markdown);
  const chunks = [];

  let currentChunk = [];
  let currentTokens = 0;
  let currentSection = null;
  let overlapBuffer = [];

  for (const element of elements) {
    const elementTokens = estimateTokens(element.content);

    // Update section context (track last heading)
    if (element.type === 'heading') {
      currentSection = element.text;
    }

    // Code blocks are always kept as single chunks (never split)
    if (element.type === 'code') {
      // If current chunk has content, finalize it first
      if (currentChunk.length > 0) {
        chunks.push(createChunk(currentChunk, chunks.length, currentSection, metadata));

        // Set overlap buffer from end of current chunk
        const overlapElements = getOverlapElements(currentChunk, overlapTokens);
        overlapBuffer = overlapElements;
        currentChunk = [];
        currentTokens = 0;
      }

      // Add code block as standalone chunk
      chunks.push(createChunk([element], chunks.length, currentSection, metadata));
      overlapBuffer = []; // No overlap after code blocks
      continue;
    }

    // Check if adding this element exceeds chunk size
    if (currentTokens + elementTokens > chunkSize && currentChunk.length > 0) {
      // Finalize current chunk
      chunks.push(createChunk(currentChunk, chunks.length, currentSection, metadata));

      // Set overlap buffer from end of current chunk
      const overlapElements = getOverlapElements(currentChunk, overlapTokens);
      overlapBuffer = overlapElements;

      // Start new chunk with overlap
      currentChunk = [...overlapBuffer];
      currentTokens = overlapBuffer.reduce((sum, el) => sum + estimateTokens(el.content), 0);
    }

    // Add element to current chunk
    currentChunk.push(element);
    currentTokens += elementTokens;
  }

  // Add final chunk if it meets minimum size
  if (currentChunk.length > 0 && currentTokens >= minChunkSize) {
    chunks.push(createChunk(currentChunk, chunks.length, currentSection, metadata));
  }

  return chunks;
}

/**
 * Get elements for overlap buffer
 */
function getOverlapElements(elements, targetOverlapTokens) {
  const overlap = [];
  let tokens = 0;

  // Take elements from the end until we reach target overlap
  for (let i = elements.length - 1; i >= 0; i--) {
    const element = elements[i];
    const elementTokens = estimateTokens(element.content);

    // Don't include headings or code in overlap
    if (element.type === 'heading' || element.type === 'code') {
      break;
    }

    overlap.unshift(element);
    tokens += elementTokens;

    if (tokens >= targetOverlapTokens) {
      break;
    }
  }

  return overlap;
}

/**
 * Create chunk object with metadata
 */
function createChunk(elements, chunkIndex, section, documentMetadata) {
  const content = elements.map(el => el.content).join('\n\n');
  const tokens = estimateTokens(content);

  return {
    content,
    tokens,
    metadata: {
      chunkIndex,
      documentTitle: documentMetadata.title || 'Untitled',
      documentUrl: documentMetadata.url || '',
      category: documentMetadata.category || 'general',
      section: section || 'Introduction',
      hasCode: elements.some(el => el.type === 'code'),
      elementCount: elements.length,
      ...documentMetadata
    }
  };
}

/**
 * Get chunking statistics
 */
export function getChunkingStats(chunks) {
  const tokenCounts = chunks.map(c => c.tokens);
  const totalTokens = tokenCounts.reduce((sum, t) => sum + t, 0);

  return {
    totalChunks: chunks.length,
    totalTokens,
    avgTokensPerChunk: Math.round(totalTokens / chunks.length),
    minTokens: Math.min(...tokenCounts),
    maxTokens: Math.max(...tokenCounts),
    chunksWithCode: chunks.filter(c => c.metadata.hasCode).length
  };
}
