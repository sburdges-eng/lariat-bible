#!/usr/bin/env python3
"""
Media Scanner Tool for The Lariat Bible

An offline ffprobe-based scanner that catalogs audio/video files,
captures key metadata, and writes a CSV with lightweight hashes
for duplicate detection.

No media data is transmitted - all processing happens locally.
"""

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


# Supported media extensions
AUDIO_EXTENSIONS = {'.mp3', '.wav', '.flac', '.aac', '.m4a', '.ogg', '.wma', '.aiff'}
VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpeg', '.mpg'}
MEDIA_EXTENSIONS = AUDIO_EXTENSIONS | VIDEO_EXTENSIONS

# CSV output columns
CSV_COLUMNS = [
    'file_path',
    'file_name',
    'media_type',
    'file_size_bytes',
    'file_size_human',
    'duration_seconds',
    'duration_human',
    'format_name',
    'bit_rate',
    'video_codec',
    'video_resolution',
    'video_frame_rate',
    'audio_codec',
    'audio_sample_rate',
    'audio_channels',
    'content_hash',
    'created_date',
    'modified_date',
    'scan_timestamp'
]


def check_ffprobe() -> bool:
    """Check if ffprobe is available on the system."""
    try:
        subprocess.run(
            ['ffprobe', '-version'],
            capture_output=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def format_duration(seconds: Optional[float]) -> str:
    """Convert seconds to human-readable duration (HH:MM:SS)."""
    if seconds is None:
        return 'N/A'
    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def format_file_size(size_bytes: int) -> str:
    """Convert bytes to human-readable file size."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"


def compute_content_hash(file_path: Path, chunk_size: int = 65536) -> str:
    """
    Compute a lightweight hash for duplicate detection.

    Uses a sampling strategy: hash the first chunk, middle chunk,
    and last chunk of the file combined with file size. This is
    much faster than hashing the entire file while still being
    effective for duplicate detection.
    """
    file_size = file_path.stat().st_size
    hasher = hashlib.sha256()

    # Include file size in hash for additional uniqueness
    hasher.update(str(file_size).encode())

    with open(file_path, 'rb') as f:
        # Read first chunk
        hasher.update(f.read(chunk_size))

        # Read middle chunk (if file is large enough)
        if file_size > chunk_size * 3:
            f.seek(file_size // 2)
            hasher.update(f.read(chunk_size))

        # Read last chunk (if file is large enough)
        if file_size > chunk_size * 2:
            f.seek(-chunk_size, 2)
            hasher.update(f.read(chunk_size))

    return hasher.hexdigest()[:16]  # Return first 16 chars for brevity


def get_media_metadata(file_path: Path) -> dict:
    """
    Extract metadata from a media file using ffprobe.

    Returns a dictionary with all relevant metadata fields.
    """
    metadata = {
        'file_path': str(file_path.absolute()),
        'file_name': file_path.name,
        'media_type': 'audio' if file_path.suffix.lower() in AUDIO_EXTENSIONS else 'video',
        'file_size_bytes': 0,
        'file_size_human': 'N/A',
        'duration_seconds': None,
        'duration_human': 'N/A',
        'format_name': 'N/A',
        'bit_rate': 'N/A',
        'video_codec': 'N/A',
        'video_resolution': 'N/A',
        'video_frame_rate': 'N/A',
        'audio_codec': 'N/A',
        'audio_sample_rate': 'N/A',
        'audio_channels': 'N/A',
        'content_hash': 'N/A',
        'created_date': 'N/A',
        'modified_date': 'N/A',
        'scan_timestamp': datetime.now().isoformat()
    }

    try:
        # Get file stats
        stat = file_path.stat()
        metadata['file_size_bytes'] = stat.st_size
        metadata['file_size_human'] = format_file_size(stat.st_size)
        metadata['modified_date'] = datetime.fromtimestamp(stat.st_mtime).isoformat()

        # Try to get creation date (platform-dependent)
        try:
            metadata['created_date'] = datetime.fromtimestamp(stat.st_ctime).isoformat()
        except AttributeError:
            pass

        # Compute content hash
        metadata['content_hash'] = compute_content_hash(file_path)

    except OSError as e:
        print(f"  Warning: Could not read file stats for {file_path}: {e}", file=sys.stderr)
        return metadata

    # Run ffprobe to get media metadata
    try:
        result = subprocess.run(
            [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                str(file_path)
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            print(f"  Warning: ffprobe failed for {file_path}", file=sys.stderr)
            return metadata

        probe_data = json.loads(result.stdout)

        # Extract format information
        fmt = probe_data.get('format', {})
        metadata['format_name'] = fmt.get('format_long_name', fmt.get('format_name', 'N/A'))

        if 'duration' in fmt:
            metadata['duration_seconds'] = float(fmt['duration'])
            metadata['duration_human'] = format_duration(metadata['duration_seconds'])

        if 'bit_rate' in fmt:
            bit_rate = int(fmt['bit_rate'])
            metadata['bit_rate'] = f"{bit_rate // 1000} kbps"

        # Extract stream information
        for stream in probe_data.get('streams', []):
            codec_type = stream.get('codec_type')

            if codec_type == 'video':
                metadata['video_codec'] = stream.get('codec_name', 'N/A')
                width = stream.get('width')
                height = stream.get('height')
                if width and height:
                    metadata['video_resolution'] = f"{width}x{height}"

                # Frame rate
                fps = stream.get('r_frame_rate', '')
                if fps and '/' in fps:
                    num, den = fps.split('/')
                    if int(den) > 0:
                        metadata['video_frame_rate'] = f"{int(num) / int(den):.2f} fps"
                elif fps:
                    metadata['video_frame_rate'] = f"{fps} fps"

            elif codec_type == 'audio':
                metadata['audio_codec'] = stream.get('codec_name', 'N/A')
                sample_rate = stream.get('sample_rate')
                if sample_rate:
                    metadata['audio_sample_rate'] = f"{int(sample_rate) // 1000} kHz"
                metadata['audio_channels'] = stream.get('channels', 'N/A')

    except subprocess.TimeoutExpired:
        print(f"  Warning: ffprobe timed out for {file_path}", file=sys.stderr)
    except json.JSONDecodeError as e:
        print(f"  Warning: Could not parse ffprobe output for {file_path}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"  Warning: Error processing {file_path}: {e}", file=sys.stderr)

    return metadata


def find_media_files(directory: Path, recursive: bool = True) -> list[Path]:
    """Find all media files in the given directory."""
    media_files = []

    if recursive:
        for ext in MEDIA_EXTENSIONS:
            media_files.extend(directory.rglob(f'*{ext}'))
            media_files.extend(directory.rglob(f'*{ext.upper()}'))
    else:
        for ext in MEDIA_EXTENSIONS:
            media_files.extend(directory.glob(f'*{ext}'))
            media_files.extend(directory.glob(f'*{ext.upper()}'))

    # Remove duplicates and sort
    media_files = sorted(set(media_files))
    return media_files


def find_duplicates(results: list[dict]) -> dict[str, list[str]]:
    """
    Find potential duplicate files based on content hash.

    Returns a dictionary mapping hash to list of file paths.
    """
    hash_map = {}
    for result in results:
        content_hash = result.get('content_hash', 'N/A')
        if content_hash != 'N/A':
            if content_hash not in hash_map:
                hash_map[content_hash] = []
            hash_map[content_hash].append(result['file_path'])

    # Filter to only show actual duplicates
    return {h: paths for h, paths in hash_map.items() if len(paths) > 1}


def scan_directory(
    directory: Path,
    output_file: Path,
    recursive: bool = True,
    verbose: bool = False
) -> tuple[int, int, dict]:
    """
    Scan a directory for media files and write results to CSV.

    Returns tuple of (files_scanned, files_with_errors, duplicates_dict).
    """
    print(f"Scanning directory: {directory}")
    print(f"Recursive: {recursive}")
    print(f"Output file: {output_file}")
    print()

    # Find all media files
    media_files = find_media_files(directory, recursive)
    total_files = len(media_files)

    if total_files == 0:
        print("No media files found.")
        return 0, 0, {}

    print(f"Found {total_files} media file(s)")
    print()

    results = []
    errors = 0

    # Process each file
    for i, file_path in enumerate(media_files, 1):
        if verbose:
            print(f"[{i}/{total_files}] Processing: {file_path.name}")
        else:
            # Simple progress indicator
            print(f"\rProcessing: {i}/{total_files} files...", end='', flush=True)

        try:
            metadata = get_media_metadata(file_path)
            results.append(metadata)
        except Exception as e:
            errors += 1
            print(f"\n  Error processing {file_path}: {e}", file=sys.stderr)

    if not verbose:
        print()  # New line after progress indicator

    # Write results to CSV
    print(f"\nWriting results to {output_file}...")

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(results)

    # Find duplicates
    duplicates = find_duplicates(results)

    # Print summary
    print()
    print("=" * 60)
    print("SCAN SUMMARY")
    print("=" * 60)
    print(f"Total files scanned: {total_files}")
    print(f"Files with errors:   {errors}")
    print(f"Results written to:  {output_file}")

    # Calculate totals
    total_size = sum(r['file_size_bytes'] for r in results)
    total_duration = sum(r['duration_seconds'] or 0 for r in results)
    audio_count = sum(1 for r in results if r['media_type'] == 'audio')
    video_count = sum(1 for r in results if r['media_type'] == 'video')

    print()
    print(f"Audio files:         {audio_count}")
    print(f"Video files:         {video_count}")
    print(f"Total size:          {format_file_size(total_size)}")
    print(f"Total duration:      {format_duration(total_duration)}")

    if duplicates:
        print()
        print(f"Potential duplicates found: {len(duplicates)} group(s)")
        for i, (hash_val, paths) in enumerate(duplicates.items(), 1):
            print(f"\n  Duplicate group {i} (hash: {hash_val}):")
            for path in paths:
                print(f"    - {path}")

    print("=" * 60)

    return total_files, errors, duplicates


def main():
    parser = argparse.ArgumentParser(
        description='Scan media files and generate a metadata catalog.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/media
  %(prog)s /path/to/media -o inventory.csv
  %(prog)s /path/to/media --no-recursive -v

This tool runs entirely offline - no data is transmitted.
        """
    )

    parser.add_argument(
        'directory',
        type=Path,
        help='Directory to scan for media files'
    )

    parser.add_argument(
        '-o', '--output',
        type=Path,
        default=None,
        help='Output CSV file path (default: media_scan_YYYYMMDD_HHMMSS.csv)'
    )

    parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='Do not scan subdirectories'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed progress for each file'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )

    args = parser.parse_args()

    # Validate directory
    if not args.directory.exists():
        print(f"Error: Directory does not exist: {args.directory}", file=sys.stderr)
        sys.exit(1)

    if not args.directory.is_dir():
        print(f"Error: Path is not a directory: {args.directory}", file=sys.stderr)
        sys.exit(1)

    # Check for ffprobe
    if not check_ffprobe():
        print("Error: ffprobe is not installed or not in PATH.", file=sys.stderr)
        print("Please install FFmpeg: https://ffmpeg.org/download.html", file=sys.stderr)
        sys.exit(1)

    # Generate default output filename if not specified
    if args.output is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        args.output = Path(f'media_scan_{timestamp}.csv')

    # Run the scan
    try:
        files_scanned, errors, duplicates = scan_directory(
            args.directory,
            args.output,
            recursive=not args.no_recursive,
            verbose=args.verbose
        )

        # Exit with error code if there were issues
        if errors > 0:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nScan interrupted by user.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"\nFatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
