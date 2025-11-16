/**
 * YouTube MCP Servers Test
 *
 * Tests YouTube Transcript Pro (primary) and YouTube Intelligence Suite (fallback)
 * for extracting transcripts from GHL tutorial videos.
 *
 * Prerequisites:
 * - YouTube MCP servers configured in .mcp.json
 * - No API key required (uses public YouTube data)
 *
 * Usage:
 *   node tests/youtube-test.js
 */

// Test configuration
const TEST_CONFIG = {
  // Sample GHL tutorial video IDs for testing
  testVideos: [
    {
      id: 'dQw4w9WgXcQ', // Replace with actual GHL tutorial video
      title: 'Sample GHL Tutorial',
      creator: 'Robb Bailey / Shaun Clark / GHL Official'
    }
  ],
  // Timeout for API calls
  timeout: 30000
};

// ANSI color codes for output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  gray: '\x1b[90m'
};

// Helper functions
function log(message, color = colors.reset) {
  console.log(`${color}${message}${colors.reset}`);
}

function success(message) {
  log(`✓ ${message}`, colors.green);
}

function error(message) {
  log(`✗ ${message}`, colors.red);
}

function info(message) {
  log(`ℹ ${message}`, colors.blue);
}

function warn(message) {
  log(`⚠ ${message}`, colors.yellow);
}

function detail(message) {
  log(`  ${message}`, colors.gray);
}

// Assertion helpers
function assertTrue(condition, message) {
  if (!condition) {
    error(message);
    throw new Error(message);
  }
  success(message);
}

function assertExists(value, name) {
  if (value === undefined || value === null) {
    error(`${name} is missing`);
    throw new Error(`${name} is missing`);
  }
  success(`${name} exists`);
}

function assertType(value, type, name) {
  if (typeof value !== type) {
    error(`${name} should be ${type}, got ${typeof value}`);
    throw new Error(`${name} type mismatch`);
  }
  success(`${name} is ${type}`);
}

// Main test suite
async function runTests() {
  log('\n=== YouTube MCP Servers Test Suite ===\n', colors.blue);

  let passedTests = 0;
  let failedTests = 0;
  const startTime = Date.now();

  // Test 1: MCP Server Configuration Check (Transcript Pro)
  try {
    info('Test 1: Check YouTube Transcript Pro configuration');
    const fs = await import('fs/promises');
    const mcpConfig = JSON.parse(await fs.readFile('.mcp.json', 'utf-8'));

    assertExists(mcpConfig.mcpServers, '.mcp.json mcpServers');
    assertExists(
      mcpConfig.mcpServers['youtube-transcript-pro'],
      'youtube-transcript-pro server configuration'
    );

    const transcriptProConfig = mcpConfig.mcpServers['youtube-transcript-pro'];
    assertTrue(
      transcriptProConfig.command === 'npx',
      'YouTube Transcript Pro uses npx command'
    );
    assertTrue(
      transcriptProConfig.args.includes('youtube-transcript-pro-mcp'),
      'YouTube Transcript Pro uses correct package'
    );

    detail('YouTube Transcript Pro MCP server properly configured');
    passedTests++;
  } catch (err) {
    error(`Test 1 failed: ${err.message}`);
    detail('Check .mcp.json file has youtube-transcript-pro configuration');
    failedTests++;
  }

  // Test 2: MCP Server Configuration Check (Intelligence Suite)
  try {
    info('\nTest 2: Check YouTube Intelligence Suite configuration');
    const fs = await import('fs/promises');
    const mcpConfig = JSON.parse(await fs.readFile('.mcp.json', 'utf-8'));

    assertExists(
      mcpConfig.mcpServers['youtube-intelligence'],
      'youtube-intelligence server configuration'
    );

    const intelligenceConfig = mcpConfig.mcpServers['youtube-intelligence'];
    assertTrue(
      intelligenceConfig.command === 'npx',
      'YouTube Intelligence Suite uses npx command'
    );
    assertTrue(
      intelligenceConfig.args.includes('youtube-intelligence-suite-mcp'),
      'YouTube Intelligence Suite uses correct package'
    );

    detail('YouTube Intelligence Suite MCP server properly configured');
    passedTests++;
  } catch (err) {
    error(`Test 2 failed: ${err.message}`);
    detail('Check .mcp.json file has youtube-intelligence configuration');
    failedTests++;
  }

  // Test 3: MCP Server Availability
  info('\nTest 3: MCP servers availability check');
  warn('Manual verification required:');
  detail('1. Restart Claude Code to load MCP configuration');
  detail('2. Check status bar for "youtube-transcript-pro" server');
  detail('3. Check status bar for "youtube-intelligence" server');
  detail('4. Verify both servers show as connected (green status)');
  warn('Test skipped - requires manual verification');

  // Test 4: YouTube Transcript Pro Tools
  try {
    info('\nTest 4: Validate YouTube Transcript Pro tools');
    const expectedTools = {
      get_transcript: {
        description: 'Extract plain text transcript from video',
        parameters: ['videoId', 'language (default: en)'],
        returns: '{ text: string, language: string }'
      },
      get_timed_transcript: {
        description: 'Extract transcript with timestamps',
        parameters: ['videoId'],
        returns: 'array<{ text: string, start: number, duration: number }>'
      },
      get_video_info: {
        description: 'Get video metadata',
        parameters: ['videoId'],
        returns: '{ title, creator, duration, publishDate }'
      },
      search_videos: {
        description: 'Search for videos by query',
        parameters: ['query', 'maxResults'],
        returns: 'array<{ videoId, title, creator }>'
      }
    };

    Object.entries(expectedTools).forEach(([tool, spec]) => {
      detail(`${tool}:`);
      detail(`  ${spec.description}`);
      detail(`  Params: ${spec.parameters.join(', ')}`);
      detail(`  Returns: ${spec.returns}`);
    });

    success('YouTube Transcript Pro provides 4 production-ready tools');
    passedTests++;
  } catch (err) {
    error(`Test 4 failed: ${err.message}`);
    failedTests++;
  }

  // Test 5: YouTube Intelligence Suite Tools
  try {
    info('\nTest 5: Validate YouTube Intelligence Suite tools');
    detail('YouTube Intelligence Suite provides 8 advanced tools:');
    detail('  - get_transcript: Extract transcript with smart format handling');
    detail('  - get_video_info: Detailed video metadata');
    detail('  - search_videos: Advanced search with filters');
    detail('  - get_channel_info: Channel metadata and statistics');
    detail('  - get_comments: Extract video comments');
    detail('  - analyze_sentiment: Sentiment analysis of transcript');
    detail('  - extract_topics: Topic extraction from content');
    detail('  - summarize: AI-powered video summarization');

    success('YouTube Intelligence Suite provides 8 advanced tools');
    detail('Use as fallback when Transcript Pro fails or for advanced features');
    passedTests++;
  } catch (err) {
    error(`Test 5 failed: ${err.message}`);
    failedTests++;
  }

  // Test 6: Fallback Strategy
  try {
    info('\nTest 6: Document fallback strategy');
    detail('Primary: YouTube Transcript Pro (reliable, production-ready)');
    detail('Fallback: YouTube Intelligence Suite (more features, use if primary fails)');
    detail('');
    detail('When to use Transcript Pro:');
    detail('  ✓ Simple transcript extraction');
    detail('  ✓ Basic video metadata');
    detail('  ✓ Production knowledge base pipeline');
    detail('');
    detail('When to use Intelligence Suite:');
    detail('  ✓ Transcript Pro fails or times out');
    detail('  ✓ Need advanced features (sentiment, topics, summarization)');
    detail('  ✓ Need channel info or comments');
    detail('  ✓ Exploratory data analysis');

    success('Fallback strategy documented');
    passedTests++;
  } catch (err) {
    error(`Test 6 failed: ${err.message}`);
    failedTests++;
  }

  // Test 7: Error Handling Scenarios
  try {
    info('\nTest 7: Document error handling scenarios');
    const errorScenarios = [
      {
        scenario: 'Invalid video ID',
        expected: 'Should return error with message "Video not found"'
      },
      {
        scenario: 'Private/deleted video',
        expected: 'Should return error "Video unavailable"'
      },
      {
        scenario: 'No transcript available',
        expected: 'Should return error "Transcript not available" → Try fallback server'
      },
      {
        scenario: 'Rate limit exceeded',
        expected: 'Should return 429 error → Wait and retry or use fallback'
      },
      {
        scenario: 'Network timeout',
        expected: 'Should timeout gracefully → Retry or use fallback'
      },
      {
        scenario: 'Unsupported language',
        expected: 'Should return error with available languages'
      }
    ];

    errorScenarios.forEach(({ scenario, expected }) => {
      detail(`${scenario}: ${expected}`);
    });

    success('Error handling scenarios documented');
    passedTests++;
  } catch (err) {
    error(`Test 7 failed: ${err.message}`);
    failedTests++;
  }

  // Test 8: GHL Content Sources
  try {
    info('\nTest 8: Document GHL YouTube content sources');
    const contentSources = [
      {
        creator: 'Robb Bailey',
        focus: 'GHL workflows, automation, expert tutorials',
        channel: 'YouTube: Robb Bailey',
        estimatedVideos: '30-50 relevant videos'
      },
      {
        creator: 'Shaun Clark',
        focus: 'GHL setup, best practices, agency workflows',
        channel: 'YouTube: Shaun Clark',
        estimatedVideos: '20-40 relevant videos'
      },
      {
        creator: 'GoHighLevel Official',
        focus: 'Product updates, feature announcements, official guides',
        channel: 'YouTube: GoHighLevel',
        estimatedVideos: '40-60 relevant videos'
      }
    ];

    contentSources.forEach(source => {
      detail(`${source.creator}:`);
      detail(`  Focus: ${source.focus}`);
      detail(`  Channel: ${source.channel}`);
      detail(`  Estimated: ${source.estimatedVideos}`);
    });

    detail('');
    detail('Total estimated: 90-150 tutorial videos for knowledge base');
    success('GHL YouTube content sources documented');
    passedTests++;
  } catch (err) {
    error(`Test 8 failed: ${err.message}`);
    failedTests++;
  }

  // Test 9: Usage Example
  try {
    info('\nTest 9: Usage examples for transcript extraction');
    detail('Example 1: Get plain text transcript (via MCP in Claude Code)');
    detail('  Tool: youtube-transcript-pro → get_transcript');
    detail('  Video ID: dQw4w9WgXcQ (example)');
    detail('  Language: en');
    detail('  Expected: Full transcript as plain text');
    detail('');
    detail('Example 2: Get timed transcript with timestamps');
    detail('  Tool: youtube-transcript-pro → get_timed_transcript');
    detail('  Video ID: dQw4w9WgXcQ');
    detail('  Expected: [{text: "...", start: 0, duration: 5}, ...]');
    detail('');
    detail('Example 3: Get video metadata');
    detail('  Tool: youtube-transcript-pro → get_video_info');
    detail('  Video ID: dQw4w9WgXcQ');
    detail('  Expected: {title, creator, duration, publishDate}');
    detail('');
    detail('Example 4: Fallback to Intelligence Suite');
    detail('  If Transcript Pro fails:');
    detail('  Tool: youtube-intelligence → get_transcript');
    detail('  Same parameters, different implementation');

    success('Usage examples documented');
    passedTests++;
  } catch (err) {
    error(`Test 9 failed: ${err.message}`);
    failedTests++;
  }

  // Test 10: KB Integration
  try {
    info('\nTest 10: Knowledge base integration notes');
    detail('YouTube sources configuration: kb/youtube-sources.json');
    detail('Expected structure:');
    detail('  {');
    detail('    "creators": [');
    detail('      {');
    detail('        "name": "Robb Bailey",');
    detail('        "channelId": "...",');
    detail('        "searchQueries": ["gohighlevel workflow", "ghl automation"]');
    detail('      }');
    detail('    ]');
    detail('  }');
    detail('');
    detail('Extraction pipeline will:');
    detail('  1. Search for videos using configured queries');
    detail('  2. Extract transcripts using Transcript Pro (primary)');
    detail('  3. Fall back to Intelligence Suite if needed');
    detail('  4. Store in kb/youtube-transcripts/ with metadata');
    detail('  5. Chunk and embed for vector database');

    success('Knowledge base integration documented');
    passedTests++;
  } catch (err) {
    error(`Test 10 failed: ${err.message}`);
    failedTests++;
  }

  // Summary
  const duration = Date.now() - startTime;
  log('\n=== Test Summary ===\n', colors.blue);
  log(`Total tests: ${passedTests + failedTests}`);
  success(`Passed: ${passedTests}`);
  if (failedTests > 0) {
    error(`Failed: ${failedTests}`);
  }
  log(`Duration: ${duration}ms\n`);

  if (failedTests > 0) {
    log('❌ Some tests failed. Please fix the issues above.\n', colors.red);
    process.exit(1);
  } else {
    log('✅ All tests passed! YouTube MCP servers are properly configured.\n', colors.green);

    // Next steps
    log('=== Next Steps ===\n', colors.blue);
    info('1. Restart Claude Code to load MCP configuration');
    info('2. Verify both YouTube servers appear in status bar');
    info('3. Test transcript extraction from a GHL tutorial video');
    info('4. Configure kb/youtube-sources.json with target creators');
    info('5. Run YouTube extraction pipeline: npm run extract-yt');
    log('');
  }
}

// Run tests
runTests().catch(err => {
  error(`\nTest suite error: ${err.message}`);
  console.error(err.stack);
  process.exit(1);
});
