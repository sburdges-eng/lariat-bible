# Media Scanner Guide

A comprehensive guide for using the offline media scanner tool to catalog audio and video files.

## Overview

The Media Scanner (`tools/media_scan.py`) is an offline utility that:
- Catalogs audio and video files in a directory
- Extracts key metadata using ffprobe
- Generates lightweight content hashes for duplicate detection
- Writes results to a CSV file for analysis

**Privacy Note**: This tool runs entirely offline. No media data is transmitted anywhere.

## Prerequisites

### Install FFmpeg

The scanner requires `ffprobe`, which is included with FFmpeg.

**macOS (Homebrew):**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
1. Download from https://ffmpeg.org/download.html
2. Extract and add the `bin` folder to your system PATH

**Verify installation:**
```bash
ffprobe -version
```

## Basic Usage

### Scan a Directory

```bash
python tools/media_scan.py /path/to/media/folder
```

This creates a timestamped CSV file (e.g., `media_scan_20241124_143022.csv`) in the current directory.

### Specify Output File

```bash
python tools/media_scan.py /path/to/media -o inventory.csv
```

### Non-Recursive Scan

Scan only the specified directory (no subdirectories):

```bash
python tools/media_scan.py /path/to/media --no-recursive
```

### Verbose Output

Show detailed progress for each file:

```bash
python tools/media_scan.py /path/to/media -v
```

## Understanding the Output

### CSV Columns

| Column | Description |
|--------|-------------|
| `file_path` | Absolute path to the file |
| `file_name` | File name with extension |
| `media_type` | Either "audio" or "video" |
| `file_size_bytes` | File size in bytes |
| `file_size_human` | Human-readable size (e.g., "1.5 GB") |
| `duration_seconds` | Duration in seconds |
| `duration_human` | Human-readable duration (HH:MM:SS) |
| `format_name` | Container format (e.g., "MP4") |
| `bit_rate` | Overall bitrate (e.g., "1500 kbps") |
| `video_codec` | Video codec (e.g., "h264", "hevc") |
| `video_resolution` | Resolution (e.g., "1920x1080") |
| `video_frame_rate` | Frame rate (e.g., "29.97 fps") |
| `audio_codec` | Audio codec (e.g., "aac", "mp3") |
| `audio_sample_rate` | Sample rate (e.g., "48 kHz") |
| `audio_channels` | Number of audio channels |
| `content_hash` | 16-character hash for duplicate detection |
| `created_date` | File creation timestamp |
| `modified_date` | File modification timestamp |
| `scan_timestamp` | When the scan was performed |

### Supported File Types

**Audio:**
- MP3, WAV, FLAC, AAC, M4A, OGG, WMA, AIFF

**Video:**
- MP4, MKV, AVI, MOV, WMV, FLV, WebM, M4V, MPEG, MPG

### Duplicate Detection

The scanner uses a lightweight hashing strategy for efficient duplicate detection:
- Hashes the first 64KB, middle 64KB, and last 64KB of each file
- Combines with file size for additional uniqueness
- Much faster than full-file hashing while still effective

Files with matching `content_hash` values are likely duplicates.

### Scan Summary

After scanning, you'll see a summary:

```
============================================================
SCAN SUMMARY
============================================================
Total files scanned: 150
Files with errors:   2
Results written to:  media_scan_20241124_143022.csv

Audio files:         45
Video files:         105
Total size:          125.3 GB
Total duration:      48:32:15

Potential duplicates found: 3 group(s)

  Duplicate group 1 (hash: a1b2c3d4e5f6g7h8):
    - /media/videos/clip.mp4
    - /media/backup/clip_copy.mp4
============================================================
```

## Troubleshooting

### "ffprobe is not installed or not in PATH"

**Solution:** Install FFmpeg (see Prerequisites above) and ensure it's in your system PATH.

Test with:
```bash
which ffprobe  # macOS/Linux
where ffprobe  # Windows
```

### "Warning: ffprobe failed for [file]"

**Possible causes:**
- Corrupted media file
- Unsupported container format
- File permissions issue

**Solution:** The scanner will continue processing other files. Check if the file plays in a media player.

### "Warning: ffprobe timed out for [file]"

**Possible causes:**
- Very large file on slow storage
- Network drive with high latency
- File system issues

**Solution:** The default timeout is 30 seconds. For very large files, ensure you're scanning from local storage.

### Scan is very slow

**Possible causes:**
- Scanning from network storage
- Very large number of files
- Slow disk

**Solutions:**
1. Copy files to local storage before scanning
2. Use `--no-recursive` to scan specific folders
3. Run verbose mode (`-v`) to identify slow files

### "Permission denied" errors

**Solution:** Ensure you have read access to the media files:
```bash
# Check permissions
ls -la /path/to/file

# Fix permissions (if you own the files)
chmod +r /path/to/file
```

### CSV file has encoding issues

The scanner uses UTF-8 encoding. If you see encoding issues in Excel:
1. Open Excel
2. Go to Data > From Text/CSV
3. Select the file and choose UTF-8 encoding

### Hash collisions (false duplicate detection)

The lightweight hash is optimized for speed over uniqueness. In rare cases, different files may have matching hashes.

**To verify duplicates:**
```bash
# Compare file sizes
ls -la file1.mp4 file2.mp4

# Compare full checksums
sha256sum file1.mp4 file2.mp4
```

## Example Workflows

### Inventory Existing Media

```bash
# Full inventory of media library
python tools/media_scan.py ~/Videos -o video_inventory.csv
python tools/media_scan.py ~/Music -o music_inventory.csv
```

### Find Duplicates

```bash
# Scan and review duplicates
python tools/media_scan.py /media/archive -v

# The summary will list duplicate groups
```

### Audit Training Videos

```bash
# Scan training materials folder
python tools/media_scan.py /path/to/training -o training_audit.csv

# Open CSV in spreadsheet to review durations and formats
```

### Pre-Migration Check

Before moving media to new storage:
```bash
# Create inventory before migration
python tools/media_scan.py /old/storage -o pre_migration.csv

# After migration
python tools/media_scan.py /new/storage -o post_migration.csv

# Compare file counts and hashes to verify complete transfer
```

## Tips

1. **Use verbose mode for debugging** - The `-v` flag shows which file is being processed, helpful for identifying problem files.

2. **Scan during off-hours** - Large scans can be I/O intensive. Schedule for times with low disk activity.

3. **Keep scan results** - Store CSV files for historical comparison and audit trails.

4. **Filter in spreadsheet** - Open the CSV in Excel or Google Sheets to sort, filter, and analyze results.

5. **Script regular scans** - Add to cron/Task Scheduler for periodic inventory updates.
