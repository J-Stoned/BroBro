/**
 * YouTube Transcript Extractor
 *
 * Extracts transcripts from GHL tutorial videos using YouTube MCP servers.
 *
 * Usage:
 *   node scripts/extract-yt-transcripts.js --source-config kb/youtube-sources.json --limit 100
 *   node scripts/extract-yt-transcripts.js --output kb/youtube-transcripts
 *
 * Options:
 *   --source-config <path>  Path to YouTube sources config JSON (default: kb/youtube-sources.json)
 *   --output <path>         Output directory (default: kb/youtube-transcripts)
 *   --limit <number>        Maximum videos to extract (default: 100)
 *
 * NOTE: This script requires YouTube MCP servers to be configured and running.
 *       See .mcp.json and README.md for setup instructions.
 */

import fs from 'fs/promises';
import path from 'path';
import { createLogger } from './utils/logger.js';

// Parse command-line arguments
function parseArgs() {
  const args = process.argv.slice(2);
  const config = {
    sourceConfig: 'kb/youtube-sources.json',
    output: 'kb/youtube-transcripts',
    limit: 100
  };

  for (let i = 0; i < args.length; i += 2) {
    const key = args[i].replace(/^--/, '');
    const value = args[i + 1];

    switch (key) {
      case 'source-config':
      case 'sourceConfig':
        config.sourceConfig = value;
        break;
      case 'output':
        config.output = value;
        break;
      case 'limit':
        config.limit = parseInt(value, 10);
        break;
    }
  }

  return config;
}

/**
 * Load YouTube sources configuration
 */
async function loadSourcesConfig(configPath, logger) {
  try {
    const content = await fs.readFile(configPath, 'utf-8');
    return JSON.parse(content);
  } catch (error) {
    // If config doesn't exist, return default configuration
    logger.warn(`Source config not found at ${configPath}, using defaults`);

    const defaultConfig = {
      creators: [
        {
          name: 'Robb Bailey',
          searchQueries: ['gohighlevel workflow', 'ghl automation'],
          maxVideos: 50
        },
        {
          name: 'Shaun Clark',
          searchQueries: ['gohighlevel tutorial', 'ghl setup'],
          maxVideos: 40
        },
        {
          name: 'GoHighLevel Official',
          searchQueries: ['gohighlevel', 'ghl features'],
          maxVideos: 60
        }
      ]
    };

    // Save default config for future use
    await fs.mkdir(path.dirname(configPath), { recursive: true });
    await fs.writeFile(configPath, JSON.stringify(defaultConfig, null, 2), 'utf-8');
    logger.success(`Created default config at ${configPath}`);

    return defaultConfig;
  }
}

/**
 * Search for videos using YouTube MCP
 */
async function searchVideos(query, maxResults, logger) {
  // NOTE: This is a placeholder implementation
  // Actual implementation requires YouTube MCP server integration via Claude Code
  //
  // In production, this would call YouTube Transcript Pro MCP 'search_videos' tool:
  //   const result = await mcp.tools.youtube_transcript_pro.search_videos({
  //     query,
  //     maxResults
  //   });
  //   return result; // Array of { videoId, title, creator }

  logger.warn('YouTube MCP integration not yet implemented - using placeholder');
  logger.detail('This script requires Claude Code MCP runtime to call YouTube servers');

  // Placeholder: Return sample video IDs
  return [
    { videoId: 'sample_video_1', title: `${query} - Tutorial 1`, creator: 'Sample Creator' },
    { videoId: 'sample_video_2', title: `${query} - Tutorial 2`, creator: 'Sample Creator' },
    { videoId: 'sample_video_3', title: `${query} - Tutorial 3`, creator: 'Sample Creator' }
  ].slice(0, Math.min(maxResults, 3));
}

/**
 * Get video info using YouTube MCP
 */
async function getVideoInfo(videoId, logger, useFallback = false) {
  // NOTE: This is a placeholder implementation
  //
  // In production, primary server (YouTube Transcript Pro):
  //   const info = await mcp.tools.youtube_transcript_pro.get_video_info({ videoId });
  //
  // Fallback server (YouTube Intelligence Suite):
  //   const info = await mcp.tools.youtube_intelligence.get_video_info({ videoId });

  logger.debug(`Getting video info for ${videoId} (fallback: ${useFallback})`);

  // Placeholder response
  return {
    title: `Sample Video ${videoId}`,
    creator: 'Sample Creator',
    duration: 600, // seconds
    publishDate: new Date().toISOString()
  };
}

/**
 * Get transcript using YouTube MCP (with fallback)
 */
async function getTranscript(videoId, logger) {
  try {
    // Try primary server first (YouTube Transcript Pro)
    logger.debug(`Extracting transcript from ${videoId} using Transcript Pro`);

    // NOTE: Placeholder implementation
    // const transcript = await mcp.tools.youtube_transcript_pro.get_transcript({ videoId });

    const transcript = {
      text: `This is a placeholder transcript for video ${videoId}.\n\nIt would contain the full video transcript here.`,
      language: 'en'
    };

    return { transcript, server: 'youtube-transcript-pro' };
  } catch (error) {
    // Fallback to YouTube Intelligence Suite
    logger.warn(`Transcript Pro failed for ${videoId}, trying Intelligence Suite`);

    try {
      // NOTE: Placeholder implementation
      // const transcript = await mcp.tools.youtube_intelligence.get_transcript({ videoId });

      const transcript = {
        text: `Fallback transcript for video ${videoId} from Intelligence Suite.\n\nFull transcript content here.`,
        language: 'en'
      };

      return { transcript, server: 'youtube-intelligence' };
    } catch (fallbackError) {
      throw new Error(`Both YouTube servers failed: ${error.message}, ${fallbackError.message}`);
    }
  }
}

/**
 * Get timed transcript with timestamps
 */
async function getTimedTranscript(videoId, logger) {
  // NOTE: Placeholder implementation
  // const timed = await mcp.tools.youtube_transcript_pro.get_timed_transcript({ videoId });

  logger.debug(`Getting timed transcript for ${videoId}`);

  return [
    { text: 'Introduction to GoHighLevel', start: 0, duration: 5 },
    { text: 'Setting up your first workflow', start: 5, duration: 10 },
    { text: 'Adding triggers and actions', start: 15, duration: 8 }
  ];
}

/**
 * Save transcript to disk
 */
async function saveTranscript(outputDir, videoId, metadata, transcript, timedTranscript) {
  const byCreatorDir = path.join(outputDir, 'by-creator', metadata.creator.replace(/\s+/g, '-').toLowerCase());
  const byTopicDir = path.join(outputDir, 'by-topic', 'ghl-tutorials');

  // Ensure directories exist
  await fs.mkdir(byCreatorDir, { recursive: true });
  await fs.mkdir(byTopicDir, { recursive: true });

  const fileName = `${videoId}.json`;

  // Prepare data
  const data = {
    videoId,
    metadata,
    transcript: transcript.text,
    language: transcript.language,
    timedTranscript,
    extractedAt: new Date().toISOString()
  };

  // Save to both directories (by-creator and by-topic)
  await fs.writeFile(path.join(byCreatorDir, fileName), JSON.stringify(data, null, 2), 'utf-8');
  await fs.writeFile(path.join(byTopicDir, fileName), JSON.stringify(data, null, 2), 'utf-8');

  return path.join(byCreatorDir, fileName);
}

/**
 * Log failed extraction
 */
async function logFailedExtraction(outputDir, videoId, error) {
  const failedLogPath = path.join(outputDir, 'failed.log');
  const logEntry = `[${new Date().toISOString()}] ${videoId} - ${error.message}\n`;

  await fs.mkdir(outputDir, { recursive: true });
  await fs.appendFile(failedLogPath, logEntry, 'utf-8');
}

/**
 * Create index file with all extracted videos
 */
async function createIndex(outputDir, videos) {
  const indexPath = path.join(outputDir, 'index.json');

  const index = {
    totalVideos: videos.length,
    lastUpdated: new Date().toISOString(),
    creators: {},
    videos: videos.map(v => ({
      videoId: v.videoId,
      title: v.title,
      creator: v.creator,
      duration: v.duration,
      publishDate: v.publishDate
    }))
  };

  // Group by creator
  videos.forEach(v => {
    if (!index.creators[v.creator]) {
      index.creators[v.creator] = 0;
    }
    index.creators[v.creator]++;
  });

  await fs.writeFile(indexPath, JSON.stringify(index, null, 2), 'utf-8');
  return indexPath;
}

/**
 * Main extraction function
 */
async function main() {
  const config = parseArgs();
  const logPath = path.join(config.output, 'extract.log');
  const logger = createLogger(logPath);

  logger.step('YouTube Transcript Extractor');
  logger.info(`Source config: ${config.sourceConfig}`);
  logger.info(`Output: ${config.output}`);
  logger.info(`Limit: ${config.limit}`);

  try {
    // Load sources configuration
    logger.step('Step 1: Load sources configuration');
    const sourcesConfig = await loadSourcesConfig(config.sourceConfig, logger);
    logger.success(`Loaded ${sourcesConfig.creators.length} creator configurations`);

    // Search for videos
    logger.step('Step 2: Search for videos');
    const allVideos = [];
    let totalSearched = 0;

    for (const creator of sourcesConfig.creators) {
      logger.info(`Searching for videos from ${creator.name}`);

      for (const query of creator.searchQueries) {
        const maxResults = Math.min(creator.maxVideos, config.limit - totalSearched);
        if (maxResults <= 0) break;

        const videos = await searchVideos(query, maxResults, logger);
        allVideos.push(...videos);
        totalSearched += videos.length;

        logger.detail(`Found ${videos.length} videos for query: "${query}"`);

        if (totalSearched >= config.limit) break;
      }

      if (totalSearched >= config.limit) break;
    }

    logger.success(`Found ${allVideos.length} videos to extract`);

    // Extract transcripts
    logger.step('Step 3: Extract transcripts');
    let successCount = 0;
    let failedCount = 0;
    const extractedVideos = [];

    for (let i = 0; i < allVideos.length; i++) {
      const video = allVideos[i];
      const videoNum = i + 1;

      try {
        logger.progressBar(videoNum, allVideos.length, 'Extracting');

        // Get video info
        const info = await getVideoInfo(video.videoId, logger);

        // Get transcript (with fallback)
        const { transcript, server } = await getTranscript(video.videoId, logger);

        // Get timed transcript
        const timedTranscript = await getTimedTranscript(video.videoId, logger);

        // Save to disk
        const filePath = await saveTranscript(config.output, video.videoId, info, transcript, timedTranscript);

        logger.debug(`Saved: ${filePath} (server: ${server})`);

        extractedVideos.push({ ...info, videoId: video.videoId });
        successCount++;
      } catch (error) {
        logger.error(`Failed to extract ${video.videoId}`, error);
        await logFailedExtraction(config.output, video.videoId, error);
        failedCount++;
      }
    }

    // Create index
    logger.step('Step 4: Create index');
    const indexPath = await createIndex(config.output, extractedVideos);
    logger.success(`Created index at ${indexPath}`);

    // Final statistics
    logger.step('Summary');
    logger.stats({
      total_videos: allVideos.length,
      successful: successCount,
      failed: failedCount,
      output_directory: config.output,
      elapsed_time: logger.getElapsed()
    });

    if (failedCount > 0) {
      logger.warn(`${failedCount} videos failed - see failed.log for details`);
    } else {
      logger.success('All transcripts extracted successfully!');
    }

    process.exit(failedCount > 0 ? 1 : 0);
  } catch (error) {
    logger.error('Extraction failed', error);
    process.exit(1);
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1].replace(/\\/g, '/')}`) {
  main();
}

export { searchVideos, getVideoInfo, getTranscript, getTimedTranscript, saveTranscript };
