#!/usr/bin/env node

/**
 * Curated Content Validator
 *
 * Validates best practices and snapshot reference content for Story 2.3.
 *
 * Checks:
 * - Markdown structure (required sections present)
 * - Required fields (best practices: category, effectiveness, etc.)
 * - Citation format compliance ([Source Type] Author - "Title" (Date) - URL)
 * - File naming conventions
 *
 * Usage:
 *   npm run validate:curated
 *   node scripts/validate-curated-content.js
 *   node scripts/validate-curated-content.js --path kb/best-practices
 *
 * CLI Arguments:
 *   --path      Path to validate (default: validate both kb/best-practices and kb/snapshots-reference)
 *   --verbose   Show detailed output
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// === CLI ARGUMENTS ===
const args = process.argv.slice(2);
const config = {
  path: args.find(a => a.startsWith('--path='))?.split('=')[1] || null,
  verbose: args.includes('--verbose'),
};

// === PATHS ===
const projectRoot = path.resolve(__dirname, '..');
const bestPracticesDir = path.join(projectRoot, 'kb/best-practices');
const snapshotsDir = path.join(projectRoot, 'kb/snapshots-reference');

// === VALIDATION STATE ===
const results = {
  totalFiles: 0,
  passed: 0,
  failed: 0,
  errors: [],
};

console.log(`
╔═══════════════════════════════════════════════════════════════════════════╗
║           Curated Content Validator (Story 2.3)                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

Validating:
  ${config.path || 'All curated content (best-practices + snapshots-reference)'}

Checks:
  ✓ Markdown structure (required sections)
  ✓ Required fields present
  ✓ Citation format: [Source Type] Author - "Title" (Date) - URL
  ✓ File naming conventions
`);

// === VALIDATION RULES ===

const CITATION_REGEX = /^\[([^\]]+)\]\s+([^-]+)\s+-\s+"([^"]+)"\s+\((\d{4}-\d{2}-\d{2})\)\s+-\s+(https?:\/\/.+)$/;

const BEST_PRACTICE_SECTIONS = [
  '# ',           // Title
  '## Category',
  '## Effectiveness',
  '## Description',
  '## Implementation Steps',
  '## Expected Outcomes',
  '## Source',
  '## Date Added'
];

const SNAPSHOT_SECTIONS = [
  '# ',           // Title
  '## Marketplace',
  '## Description',
  '## Key Features',
  '## Use Cases',
  '## Pricing',
  '## Requirements',
  '## Source'
];

/**
 * Validate citation format
 */
function validateCitation(content, filePath) {
  const errors = [];

  // Find Source section
  const sourceMatch = content.match(/## Source\s*\n\s*(.+)/);
  if (!sourceMatch) {
    errors.push('Missing or empty ## Source section');
    return errors;
  }

  const citation = sourceMatch[1].trim();

  if (!CITATION_REGEX.test(citation)) {
    errors.push(`Invalid citation format. Found: "${citation}"`);
    errors.push('Expected: [Source Type] Author/Site - "Title" (YYYY-MM-DD) - URL');

    // Provide helpful hints
    if (!citation.startsWith('[')) {
      errors.push('Hint: Citation must start with [Source Type]');
    }
    if (!citation.includes('"')) {
      errors.push('Hint: Title must be in quotes');
    }
    if (!citation.match(/\(\d{4}-\d{2}-\d{2}\)/)) {
      errors.push('Hint: Date must be in format (YYYY-MM-DD)');
    }
    if (!citation.match(/https?:\/\//)) {
      errors.push('Hint: Must include full URL');
    }
  }

  return errors;
}

/**
 * Validate best practice structure
 */
function validateBestPractice(content, filePath) {
  const errors = [];

  // Check required sections
  BEST_PRACTICE_SECTIONS.forEach(section => {
    if (!content.includes(section)) {
      errors.push(`Missing required section: ${section}`);
    }
  });

  // Check effectiveness value
  const effectivenessMatch = content.match(/## Effectiveness\s*\n\s*(.+)/);
  if (effectivenessMatch) {
    const value = effectivenessMatch[1].trim();
    if (!['proven', 'experimental', 'emerging'].includes(value)) {
      errors.push(`Invalid effectiveness value: "${value}". Must be: proven, experimental, or emerging`);
    }
  }

  // Check category
  const categoryMatch = content.match(/## Category\s*\n\s*(.+)/);
  if (categoryMatch) {
    const category = categoryMatch[1].trim().toLowerCase();
    const validCategories = [
      'lead nurturing',
      'appointment automation',
      'form optimization',
      'saas mode setup',
      'workflow design patterns',
      'funnel conversion optimization'
    ];

    if (!validCategories.some(vc => category.includes(vc))) {
      errors.push(`Category "${category}" doesn't match target categories (lead nurturing, appointment automation, form optimization, saas mode setup, workflow design patterns, funnel conversion optimization)`);
    }
  }

  // Validate citation
  const citationErrors = validateCitation(content, filePath);
  errors.push(...citationErrors);

  return errors;
}

/**
 * Validate snapshot profile structure
 */
function validateSnapshot(content, filePath) {
  const errors = [];

  // Check required sections
  SNAPSHOT_SECTIONS.forEach(section => {
    if (!content.includes(section)) {
      errors.push(`Missing required section: ${section}`);
    }
  });

  // Check marketplace value
  const marketplaceMatch = content.match(/## Marketplace\s*\n\s*(.+)/);
  if (marketplaceMatch) {
    const value = marketplaceMatch[1].trim().toLowerCase();
    if (!['extendly', 'ghl central', 'official marketplace'].includes(value)) {
      errors.push(`Invalid marketplace: "${value}". Must be: Extendly, GHL Central, or Official Marketplace`);
    }
  }

  // Check key features (minimum 3)
  const featuresSection = content.match(/## Key Features\s*\n([\s\S]+?)(?=\n##|$)/);
  if (featuresSection) {
    const features = featuresSection[1].match(/^-\s+.+$/gm) || [];
    if (features.length < 3) {
      errors.push(`Key Features must have at least 3 items (found ${features.length})`);
    }
  }

  // Check use cases (minimum 2)
  const useCasesSection = content.match(/## Use Cases\s*\n([\s\S]+?)(?=\n##|$)/);
  if (useCasesSection) {
    const useCases = useCasesSection[1].match(/^-\s+.+$/gm) || [];
    if (useCases.length < 2) {
      errors.push(`Use Cases must have at least 2 items (found ${useCases.length})`);
    }
  }

  // Validate citation
  const citationErrors = validateCitation(content, filePath);
  errors.push(...citationErrors);

  return errors;
}

/**
 * Validate a single file
 */
function validateFile(filePath, type) {
  results.totalFiles++;

  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const filename = path.basename(filePath);

    let errors = [];

    if (type === 'best-practice') {
      errors = validateBestPractice(content, filePath);
    } else if (type === 'snapshot') {
      errors = validateSnapshot(content, filePath);
    }

    if (errors.length === 0) {
      results.passed++;
      if (config.verbose) {
        console.log(`✓ PASS: ${filename}`);
      }
    } else {
      results.failed++;
      console.log(`\n✗ FAIL: ${filename}`);
      errors.forEach(err => console.log(`  - ${err}`));

      results.errors.push({
        file: filename,
        path: filePath,
        errors: errors
      });
    }

  } catch (error) {
    results.failed++;
    console.log(`\n✗ ERROR: ${path.basename(filePath)}`);
    console.log(`  - Failed to read file: ${error.message}`);

    results.errors.push({
      file: path.basename(filePath),
      path: filePath,
      errors: [`Failed to read file: ${error.message}`]
    });
  }
}

/**
 * Scan directory for markdown files
 */
function scanDirectory(dirPath, type) {
  if (!fs.existsSync(dirPath)) {
    console.log(`\n⚠️  Directory not found: ${dirPath}`);
    console.log(`   (This is expected if content hasn't been curated yet)\n`);
    return;
  }

  const files = fs.readdirSync(dirPath, { recursive: true })
    .filter(file => file.endsWith('.md'))
    .map(file => path.join(dirPath, file));

  if (files.length === 0) {
    console.log(`\n⚠️  No markdown files found in: ${dirPath}`);
    console.log(`   (This is expected if content hasn't been curated yet)\n`);
    return;
  }

  console.log(`\n📁 Validating ${files.length} files in: ${path.basename(dirPath)}`);
  files.forEach(file => validateFile(file, type));
}

/**
 * Generate validation report
 */
function generateReport() {
  console.log(`\n╔═══════════════════════════════════════════════════════════════════════════╗`);
  console.log(`║                    Validation Report                                     ║`);
  console.log(`╚═══════════════════════════════════════════════════════════════════════════╝\n`);

  console.log(`Total Files:   ${results.totalFiles}`);
  console.log(`Passed:        ${results.passed} ✓`);
  console.log(`Failed:        ${results.failed} ✗`);

  if (results.totalFiles > 0) {
    const passRate = ((results.passed / results.totalFiles) * 100).toFixed(1);
    console.log(`Pass Rate:     ${passRate}%`);
  }

  if (results.failed > 0) {
    console.log(`\n❌ Validation FAILED - Fix errors above`);
    process.exit(1);
  } else if (results.totalFiles === 0) {
    console.log(`\n⚠️  No content files found to validate`);
    console.log(`   Create curated content files before running validation\n`);
    process.exit(0);
  } else {
    console.log(`\n✅ All content files passed validation!`);
    process.exit(0);
  }
}

// === MAIN ===
function main() {
  if (config.path) {
    // Validate specific path
    const fullPath = path.join(projectRoot, config.path);
    const type = config.path.includes('best-practices') ? 'best-practice' : 'snapshot';
    scanDirectory(fullPath, type);
  } else {
    // Validate both directories
    console.log(`\n📋 Validating Best Practices...`);
    scanDirectory(bestPracticesDir, 'best-practice');

    console.log(`\n📦 Validating Snapshot Profiles...`);
    scanDirectory(snapshotsDir, 'snapshot');
  }

  generateReport();
}

main();
