#!/usr/bin/env python3
"""
FLAC Batch Converter - Convert FLAC files to MP3 format in batch.

This script converts FLAC audio files to MP3 format, preserving the directory
structure. It processes albums stored in subdirectories within an 'in' folder
and outputs converted files to corresponding subdirectories in an 'out' folder.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def find_flac_files(base_path):
    """
    Find all FLAC files in the input directory organized by album folders.
    
    Args:
        base_path (Path): The base path containing 'in' folder
        
    Returns:
        dict: Dictionary mapping album names to lists of FLAC file paths
    """
    in_path = base_path / "in"
    
    if not in_path.exists():
        print(f"Error: Input directory '{in_path}' does not exist.", file=sys.stderr)
        sys.exit(1)
    
    albums = {}
    
    # Iterate through album directories
    for album_dir in in_path.iterdir():
        if album_dir.is_dir():
            flac_files = list(album_dir.glob("*.flac"))
            if flac_files:
                albums[album_dir.name] = flac_files
    
    return albums


def create_output_directory(base_path, album_name):
    """
    Create the output directory for an album if it doesn't exist.
    
    Args:
        base_path (Path): The base path containing 'out' folder
        album_name (str): Name of the album (subdirectory)
        
    Returns:
        Path: Path to the output directory for this album
    """
    out_path = base_path / "out" / album_name
    out_path.mkdir(parents=True, exist_ok=True)
    return out_path


def convert_flac_to_mp3(flac_file, output_file, bitrate_preset="V0"):
    """
    Convert a single FLAC file to MP3 format using ffmpeg.
    
    Args:
        flac_file (Path): Path to the input FLAC file
        output_file (Path): Path to the output MP3 file
        bitrate_preset (str): LAME bitrate preset (default: "V0")
        
    Returns:
        bool: True if conversion was successful, False otherwise
    """
    try:
        # Parse the preset
        if bitrate_preset.upper().startswith("V"):
            # Variable bitrate preset (V0-V9)
            quality = bitrate_preset[1:]
            cmd = [
                "ffmpeg",
                "-i", str(flac_file),
                "-codec:a", "libmp3lame",
                "-q:a", quality,
                "-y",  # Overwrite output file if it exists
                str(output_file)
            ]
        else:
            # Constant bitrate (e.g., "320", "256", "192")
            cmd = [
                "ffmpeg",
                "-i", str(flac_file),
                "-codec:a", "libmp3lame",
                "-b:a", f"{bitrate_preset}k",
                "-y",
                str(output_file)
            ]
        
        # Run ffmpeg with suppressed output
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"Error converting {flac_file.name}: {e.stderr.decode()}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("Error: ffmpeg is not installed or not in PATH.", file=sys.stderr)
        print("Please install ffmpeg to use this script.", file=sys.stderr)
        sys.exit(1)


def main():
    """Main function to orchestrate the batch conversion."""
    parser = argparse.ArgumentParser(
        description="Batch convert FLAC files to MP3 format.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert using V0 preset (highest quality VBR)
  %(prog)s /path/to/music
  
  # Convert using V2 preset (high quality VBR)
  %(prog)s /path/to/music --bitrate V2
  
  # Convert using constant 320kbps bitrate
  %(prog)s /path/to/music --bitrate 320
        """
    )
    
    parser.add_argument(
        "base_path",
        type=str,
        help="Base path containing 'in' and 'out' directories"
    )
    
    parser.add_argument(
        "-b", "--bitrate",
        type=str,
        default="V0",
        help="Bitrate preset: V0-V9 for VBR (default: V0), or constant bitrate like 320, 256, 192"
    )
    
    args = parser.parse_args()
    
    # Convert to Path object
    base_path = Path(args.base_path).resolve()
    
    if not base_path.exists():
        print(f"Error: Base path '{base_path}' does not exist.", file=sys.stderr)
        sys.exit(1)
    
    # Ensure out directory exists
    out_path = base_path / "out"
    out_path.mkdir(exist_ok=True)
    
    # Find all FLAC files organized by album
    print(f"Scanning for FLAC files in: {base_path / 'in'}")
    albums = find_flac_files(base_path)
    
    if not albums:
        print("No FLAC files found in album directories.", file=sys.stderr)
        sys.exit(0)
    
    # Count total files
    total_files = sum(len(files) for files in albums.values())
    print(f"Found {total_files} FLAC file(s) across {len(albums)} album(s)")
    print(f"Using bitrate preset: {args.bitrate}")
    print()
    
    # Convert files
    converted = 0
    failed = 0
    
    for album_name, flac_files in albums.items():
        print(f"Processing album: {album_name}")
        
        # Create output directory for this album
        album_out_path = create_output_directory(base_path, album_name)
        
        for flac_file in flac_files:
            # Generate output filename
            mp3_filename = flac_file.stem + ".mp3"
            output_file = album_out_path / mp3_filename
            
            print(f"  Converting: {flac_file.name} -> {mp3_filename}...", end=" ")
            
            if convert_flac_to_mp3(flac_file, output_file, args.bitrate):
                print("✓")
                converted += 1
            else:
                print("✗")
                failed += 1
    
    # Summary
    print()
    print("=" * 50)
    print(f"Conversion complete!")
    print(f"  Successful: {converted}")
    print(f"  Failed: {failed}")
    print(f"  Total: {total_files}")
    print("=" * 50)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
