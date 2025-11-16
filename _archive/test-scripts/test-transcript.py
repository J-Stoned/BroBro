from youtube_transcript_api import YouTubeTranscriptApi

# Test with a known video (first video from the channel)
video_id = "h34lSDMrC0o"  # Master GoHighLevel Calendars FAST

try:
    api = YouTubeTranscriptApi()
    print(f"Testing video: {video_id}")

    # List available transcripts
    transcript_list = api.list(video_id)
    print(f"Available transcripts: {transcript_list}")

    # Try to fetch
    result = api.fetch(video_id)
    print(f"Success! Got {len(result)} segments")
    print(f"First segment: {result[0]}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
