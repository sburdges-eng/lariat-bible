#!/usr/bin/env python3
"""
Audio Cataloger
Scan, catalog, and search audio files with automatic key/tempo detection.

Part of the Music Brain system.
"""

import argparse
import csv
import hashlib
import os
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional

# Audio analysis libraries
try:
    import librosa
    import numpy as np
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    print("Warning: librosa not installed. Install with: pip install librosa numpy")

# ============================================================================
# Configuration
# ============================================================================

# Default database path - can be overridden via set_db_path() or AUDIO_CATALOG_DB env var
_db_path = None

def get_db_path() -> Path:
    """Get the current database path, respecting environment and runtime config."""
    global _db_path
    if _db_path is not None:
        return _db_path
    env_path = os.environ.get('AUDIO_CATALOG_DB')
    if env_path:
        return Path(env_path).expanduser().resolve()
    return Path.home() / "Music-Brain" / "audio-cataloger" / "audio_catalog.db"

def set_db_path(path: str | Path) -> None:
    """Set a custom database path at runtime."""
    global _db_path
    _db_path = Path(path).expanduser().resolve()

SUPPORTED_FORMATS = {'.wav', '.aiff', '.aif', '.mp3', '.flac', '.ogg', '.m4a'}

# ============================================================================
# Utility Functions
# ============================================================================

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

# Key names for display
KEY_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
MODE_NAMES = ['minor', 'major']

# ============================================================================
# Database Functions
# ============================================================================

def init_database():
    """Initialize SQLite database with schema."""
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audio_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filepath TEXT UNIQUE NOT NULL,
            filename TEXT NOT NULL,
            folder TEXT,
            extension TEXT,
            duration_seconds REAL,
            sample_rate INTEGER,
            channels INTEGER,
            estimated_bpm REAL,
            estimated_key TEXT,
            file_size_bytes INTEGER,
            content_hash TEXT,
            date_scanned TEXT,
            date_modified TEXT
        )
    ''')

    # Add content_hash column if it doesn't exist (for existing databases)
    try:
        cursor.execute('ALTER TABLE audio_files ADD COLUMN content_hash TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Create indexes for common searches
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_filename ON audio_files(filename)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_key ON audio_files(estimated_key)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_bpm ON audio_files(estimated_bpm)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_folder ON audio_files(folder)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_content_hash ON audio_files(content_hash)')

    conn.commit()
    conn.close()
    print(f"Database initialized at: {db_path}")

def get_connection():
    """Get database connection."""
    db_path = get_db_path()
    if not db_path.exists():
        init_database()
    return sqlite3.connect(db_path)

# ============================================================================
# Audio Analysis Functions
# ============================================================================

def analyze_audio_file(filepath):
    """
    Analyze an audio file to extract metadata and musical features.
    Returns a dictionary of attributes.
    """
    if not LIBROSA_AVAILABLE:
        return analyze_audio_basic(filepath)

    try:
        # Load audio file
        y, sr = librosa.load(filepath, sr=None, mono=True, duration=60)  # First 60 sec

        duration = librosa.get_duration(y=y, sr=sr)

        # Get full duration if file is longer
        full_duration = librosa.get_duration(path=filepath)

        # Estimate tempo
        tempo = None
        try:
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            tempo_estimate = librosa.feature.tempo(onset_envelope=onset_env, sr=sr)
            if len(tempo_estimate) > 0:
                tempo = float(tempo_estimate[0])
        except Exception:
            pass

        # Estimate key using Krumhansl-Schmuckler algorithm
        key = None
        try:
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
            chroma_mean = np.mean(chroma, axis=1)

            # Krumhansl-Schmuckler key profiles (normalized)
            major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
            minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

            # Test all 24 possible keys (12 major + 12 minor)
            # by rotating the profile to match each key and computing correlation
            best_corr = -1
            best_key_idx = 0
            best_mode = 'major'

            for i in range(12):
                # Rotate chroma to test against C-based profiles
                rotated_chroma = np.roll(chroma_mean, -i)

                # Compute Pearson correlation with each profile
                major_corr = np.corrcoef(rotated_chroma, major_profile)[0, 1]
                minor_corr = np.corrcoef(rotated_chroma, minor_profile)[0, 1]

                if major_corr > best_corr:
                    best_corr = major_corr
                    best_key_idx = i
                    best_mode = 'major'

                if minor_corr > best_corr:
                    best_corr = minor_corr
                    best_key_idx = i
                    best_mode = 'minor'

            key_name = KEY_NAMES[best_key_idx]
            key = f"{key_name} {best_mode}" if best_mode == 'major' else f"{key_name}m"

        except Exception:
            pass

        # Get channel count from original file
        try:
            import soundfile as sf
            info = sf.info(filepath)
            channels = info.channels
        except Exception:
            channels = 1

        return {
            'duration_seconds': round(full_duration, 2),
            'sample_rate': sr,
            'channels': channels,
            'estimated_bpm': round(tempo, 1) if tempo else None,
            'estimated_key': key
        }

    except Exception as e:
        print(f"  Error analyzing {filepath}: {e}")
        return analyze_audio_basic(filepath)

def analyze_audio_basic(filepath):
    """Basic analysis without librosa (fallback)."""
    try:
        import soundfile as sf
        info = sf.info(filepath)
        return {
            'duration_seconds': round(info.duration, 2),
            'sample_rate': info.samplerate,
            'channels': info.channels,
            'estimated_bpm': None,
            'estimated_key': None
        }
    except Exception:
        return {
            'duration_seconds': None,
            'sample_rate': None,
            'channels': None,
            'estimated_bpm': None,
            'estimated_key': None
        }

# ============================================================================
# Scanner Functions
# ============================================================================

def scan_folder(folder_path, recursive=True):
    """Scan a folder for audio files and catalog them."""
    folder = Path(folder_path).expanduser().resolve()

    if not folder.exists():
        print(f"Error: Folder not found: {folder}")
        return

    print(f"Scanning: {folder}")
    print(f"Recursive: {recursive}")
    print("-" * 50)

    init_database()
    conn = get_connection()
    cursor = conn.cursor()

    # Find audio files
    if recursive:
        audio_files = [f for f in folder.rglob('*') if f.suffix.lower() in SUPPORTED_FORMATS]
    else:
        audio_files = [f for f in folder.glob('*') if f.suffix.lower() in SUPPORTED_FORMATS]

    print(f"Found {len(audio_files)} audio files")
    print("-" * 50)

    scanned = 0
    skipped = 0
    errors = 0

    for i, filepath in enumerate(audio_files, 1):
        try:
            # Check if already in database with same modification time
            stat = filepath.stat()
            date_modified = datetime.fromtimestamp(stat.st_mtime).isoformat()

            cursor.execute(
                'SELECT date_modified FROM audio_files WHERE filepath = ?',
                (str(filepath),)
            )
            existing = cursor.fetchone()

            if existing and existing[0] == date_modified:
                skipped += 1
                continue

            # Analyze file
            print(f"[{i}/{len(audio_files)}] Analyzing: {filepath.name}")
            analysis = analyze_audio_file(str(filepath))

            # Compute content hash for duplicate detection
            try:
                content_hash = compute_content_hash(filepath)
            except Exception:
                content_hash = None

            # Insert or update
            cursor.execute('''
                INSERT OR REPLACE INTO audio_files
                (filepath, filename, folder, extension, duration_seconds, sample_rate,
                 channels, estimated_bpm, estimated_key, file_size_bytes, content_hash,
                 date_scanned, date_modified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(filepath),
                filepath.name,
                str(filepath.parent),
                filepath.suffix.lower(),
                analysis['duration_seconds'],
                analysis['sample_rate'],
                analysis['channels'],
                analysis['estimated_bpm'],
                analysis['estimated_key'],
                stat.st_size,
                content_hash,
                datetime.now().isoformat(),
                date_modified
            ))

            scanned += 1

            # Commit periodically
            if scanned % 10 == 0:
                conn.commit()

        except Exception as e:
            print(f"  Error: {e}")
            errors += 1

    conn.commit()
    conn.close()

    print("-" * 50)
    print(f"Scanned: {scanned}")
    print(f"Skipped (unchanged): {skipped}")
    print(f"Errors: {errors}")
    print(f"Database: {get_db_path()}")

# ============================================================================
# Search Functions
# ============================================================================

def search_catalog(query=None, key=None, bpm_min=None, bpm_max=None, limit=50):
    """Search the audio catalog."""
    conn = get_connection()
    cursor = conn.cursor()

    conditions = []
    params = []

    if query:
        conditions.append("(filename LIKE ? OR folder LIKE ?)")
        params.extend([f'%{query}%', f'%{query}%'])

    if key:
        conditions.append("estimated_key LIKE ?")
        params.append(f'%{key}%')

    if bpm_min is not None:
        conditions.append("estimated_bpm >= ?")
        params.append(bpm_min)

    if bpm_max is not None:
        conditions.append("estimated_bpm <= ?")
        params.append(bpm_max)

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    cursor.execute(f'''
        SELECT filename, folder, duration_seconds, estimated_bpm, estimated_key, filepath
        FROM audio_files
        WHERE {where_clause}
        ORDER BY filename
        LIMIT ?
    ''', params + [limit])

    results = cursor.fetchall()
    conn.close()

    return results

def print_search_results(results):
    """Print search results in a readable format."""
    if not results:
        print("No results found.")
        return

    print(f"\nFound {len(results)} files:\n")
    print(f"{'Filename':<40} {'Duration':<10} {'BPM':<8} {'Key':<10}")
    print("-" * 70)

    for filename, folder, duration, bpm, key, filepath in results:
        dur_str = f"{duration:.1f}s" if duration else "?"
        bpm_str = f"{bpm:.0f}" if bpm else "?"
        key_str = key or "?"

        # Truncate long filenames
        name_display = filename[:38] + ".." if len(filename) > 40 else filename

        print(f"{name_display:<40} {dur_str:<10} {bpm_str:<8} {key_str:<10}")

def export_results(results, output_path):
    """Export search results to markdown."""
    output = Path(output_path).expanduser()

    with open(output, 'w') as f:
        f.write("# Audio Catalog Search Results\n\n")
        f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(f"| Filename | Duration | BPM | Key |\n")
        f.write(f"|----------|----------|-----|-----|\n")

        for filename, folder, duration, bpm, key, filepath in results:
            dur_str = f"{duration:.1f}s" if duration else "?"
            bpm_str = f"{bpm:.0f}" if bpm else "?"
            key_str = key or "?"
            f.write(f"| {filename} | {dur_str} | {bpm_str} | {key_str} |\n")

    print(f"Exported to: {output}")

def find_duplicates() -> dict[str, list[str]]:
    """
    Find potential duplicate files based on content hash.

    Returns a dictionary mapping hash to list of file paths.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT content_hash, GROUP_CONCAT(filepath, '|||')
        FROM audio_files
        WHERE content_hash IS NOT NULL
        GROUP BY content_hash
        HAVING COUNT(*) > 1
    ''')

    duplicates = {}
    for row in cursor.fetchall():
        content_hash, paths_str = row
        paths = paths_str.split('|||')
        duplicates[content_hash] = paths

    conn.close()
    return duplicates

def print_duplicates(duplicates: dict[str, list[str]]) -> None:
    """Print duplicate files in a readable format."""
    if not duplicates:
        print("No duplicates found.")
        return

    total_groups = len(duplicates)
    total_files = sum(len(paths) for paths in duplicates.values())
    wasted_files = total_files - total_groups  # Files that could be removed

    print(f"\nFound {total_groups} duplicate group(s) ({wasted_files} redundant files):\n")

    for i, (hash_val, paths) in enumerate(duplicates.items(), 1):
        print(f"Duplicate group {i} (hash: {hash_val}):")
        for path in paths:
            print(f"  - {path}")
        print()

def export_to_csv(output_path: str, query: str = None, key: str = None,
                  bpm_min: float = None, bpm_max: float = None) -> None:
    """Export catalog results to CSV format."""
    conn = get_connection()
    cursor = conn.cursor()

    conditions = []
    params = []

    if query:
        conditions.append("(filename LIKE ? OR folder LIKE ?)")
        params.extend([f'%{query}%', f'%{query}%'])

    if key:
        conditions.append("estimated_key LIKE ?")
        params.append(f'%{key}%')

    if bpm_min is not None:
        conditions.append("estimated_bpm >= ?")
        params.append(bpm_min)

    if bpm_max is not None:
        conditions.append("estimated_bpm <= ?")
        params.append(bpm_max)

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    cursor.execute(f'''
        SELECT filepath, filename, folder, extension, duration_seconds,
               sample_rate, channels, estimated_bpm, estimated_key,
               file_size_bytes, content_hash, date_scanned, date_modified
        FROM audio_files
        WHERE {where_clause}
        ORDER BY folder, filename
    ''', params)

    output = Path(output_path).expanduser()

    with open(output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'filepath', 'filename', 'folder', 'extension', 'duration_seconds',
            'sample_rate', 'channels', 'estimated_bpm', 'estimated_key',
            'file_size_bytes', 'content_hash', 'date_scanned', 'date_modified'
        ])

        count = 0
        for row in cursor.fetchall():
            writer.writerow(row)
            count += 1

    conn.close()
    print(f"Exported {count} files to: {output}")

def show_stats():
    """Show catalog statistics."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM audio_files')
    total = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(DISTINCT folder) FROM audio_files')
    folders = cursor.fetchone()[0]

    cursor.execute('SELECT SUM(file_size_bytes) FROM audio_files')
    total_size = cursor.fetchone()[0] or 0

    cursor.execute('SELECT estimated_key, COUNT(*) FROM audio_files WHERE estimated_key IS NOT NULL GROUP BY estimated_key ORDER BY COUNT(*) DESC LIMIT 5')
    top_keys = cursor.fetchall()

    cursor.execute('SELECT AVG(estimated_bpm) FROM audio_files WHERE estimated_bpm IS NOT NULL')
    avg_bpm = cursor.fetchone()[0]

    conn.close()

    print("\n📊 Audio Catalog Statistics\n")
    print(f"Total files: {total:,}")
    print(f"Folders: {folders:,}")
    print(f"Total size: {total_size / (1024**3):.2f} GB")

    if avg_bpm:
        print(f"Average BPM: {avg_bpm:.0f}")

    if top_keys:
        print(f"\nTop keys:")
        for key, count in top_keys:
            print(f"  {key}: {count} files")

def list_all(limit=100):
    """List all cataloged files."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT filename, folder, duration_seconds, estimated_bpm, estimated_key, filepath
        FROM audio_files
        ORDER BY folder, filename
        LIMIT ?
    ''', (limit,))

    results = cursor.fetchall()
    conn.close()

    print_search_results(results)

# ============================================================================
# CLI Interface
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Audio Cataloger - Scan and search audio files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s scan ~/Music/Samples           Scan a folder
  %(prog)s search kick                     Search by keyword
  %(prog)s search --key Am                 Search by key
  %(prog)s search --bpm-min 118 --bpm-max 122   Search by BPM range
  %(prog)s stats                           Show statistics
  %(prog)s list                            List all files
  %(prog)s duplicates                      Find duplicate files
  %(prog)s export catalog.csv             Export to CSV
  %(prog)s --db-path ./my.db scan ~/Music  Use custom database

Environment:
  AUDIO_CATALOG_DB    Path to SQLite database (overrides default)
        '''
    )

    # Global options
    parser.add_argument(
        '--db-path',
        type=str,
        help='Path to SQLite database file (overrides AUDIO_CATALOG_DB env var)'
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan folder for audio files')
    scan_parser.add_argument('folder', help='Folder path to scan')
    scan_parser.add_argument('--no-recursive', action='store_true', help='Don\'t scan subfolders')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search the catalog')
    search_parser.add_argument('query', nargs='?', help='Search term')
    search_parser.add_argument('--key', help='Filter by key (e.g., Am, C major)')
    search_parser.add_argument('--bpm-min', type=float, help='Minimum BPM')
    search_parser.add_argument('--bpm-max', type=float, help='Maximum BPM')
    search_parser.add_argument('--limit', type=int, default=50, help='Max results')
    search_parser.add_argument('--export', help='Export to markdown file')

    # Stats command
    subparsers.add_parser('stats', help='Show catalog statistics')

    # List command
    list_parser = subparsers.add_parser('list', help='List all files')
    list_parser.add_argument('--limit', type=int, default=100, help='Max files to show')

    # Duplicates command
    subparsers.add_parser('duplicates', help='Find duplicate files by content hash')

    # Export command
    export_parser = subparsers.add_parser('export', help='Export catalog to CSV')
    export_parser.add_argument('output', help='Output CSV file path')
    export_parser.add_argument('--query', help='Filter by search term')
    export_parser.add_argument('--key', help='Filter by key')
    export_parser.add_argument('--bpm-min', type=float, help='Minimum BPM')
    export_parser.add_argument('--bpm-max', type=float, help='Maximum BPM')

    # Init command
    subparsers.add_parser('init', help='Initialize database')

    args = parser.parse_args()

    # Handle custom database path
    if args.db_path:
        set_db_path(args.db_path)

    if args.command == 'scan':
        scan_folder(args.folder, recursive=not args.no_recursive)

    elif args.command == 'search':
        if not args.query and not args.key and args.bpm_min is None and args.bpm_max is None:
            print("Please provide a search term or filter (--key, --bpm-min, --bpm-max)")
            return

        results = search_catalog(
            query=args.query,
            key=args.key,
            bpm_min=args.bpm_min,
            bpm_max=args.bpm_max,
            limit=args.limit
        )

        if args.export:
            export_results(results, args.export)
        else:
            print_search_results(results)

    elif args.command == 'stats':
        show_stats()

    elif args.command == 'list':
        list_all(args.limit)

    elif args.command == 'duplicates':
        duplicates = find_duplicates()
        print_duplicates(duplicates)

    elif args.command == 'export':
        export_to_csv(
            args.output,
            query=args.query,
            key=args.key,
            bpm_min=args.bpm_min,
            bpm_max=args.bpm_max
        )

    elif args.command == 'init':
        init_database()

    else:
        parser.print_help()

if __name__ == '__main__':
    main()
