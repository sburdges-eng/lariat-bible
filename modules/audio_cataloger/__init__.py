"""
Audio Cataloger Module

Scan, catalog, and search audio files with automatic key/tempo detection.
Part of the Music Brain system.
"""

from .audio_cataloger import (
    # Configuration
    get_db_path,
    set_db_path,
    # Database
    init_database,
    get_connection,
    # Scanning
    scan_folder,
    analyze_audio_file,
    compute_content_hash,
    # Search & Query
    search_catalog,
    list_all,
    find_duplicates,
    # Export
    export_results,
    export_to_csv,
    # Statistics
    show_stats,
)

__all__ = [
    # Configuration
    'get_db_path',
    'set_db_path',
    # Database
    'init_database',
    'get_connection',
    # Scanning
    'scan_folder',
    'analyze_audio_file',
    'compute_content_hash',
    # Search & Query
    'search_catalog',
    'list_all',
    'find_duplicates',
    # Export
    'export_results',
    'export_to_csv',
    # Statistics
    'show_stats',
]
