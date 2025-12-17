#!/usr/bin/env python3
"""
FLAC Batch Converter - Convert FLAC files to MP3 format in batch.

This script converts FLAC audio files to MP3 format, preserving the directory
structure. It processes albums stored in subdirectories within an 'in' folder
and outputs converted files to corresponding subdirectories in an 'out' folder.
"""

import argparse
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import ffmpeg


def find_flac_files(base_path):
    """
    Find all FLAC files recursively in the input directory.
    
    Args:
        base_path (Path): The base path containing 'in' folder
        
    Returns:
        list: List of tuples (flac_file_path, relative_path_from_in) where
              relative_path_from_in is the path relative to the 'in' folder
    """
    in_path = base_path / "in"
    
    if not in_path.exists():
        print(f"Error: Input directory '{in_path}' does not exist.", file=sys.stderr)
        sys.exit(1)
    
    flac_files = []
    
    # Recursively find all FLAC files with case-insensitive matching
    # Use a set to avoid duplicates and then sort
    found_files = set()
    for pattern in ["**/*.[Ff][Ll][Aa][Cc]"]:
        for flac_file in in_path.glob(pattern):
            if flac_file.is_file():
                found_files.add(flac_file)
    
    # Convert to list with relative paths and sort
    for flac_file in sorted(found_files):
        relative_path = flac_file.relative_to(in_path)
        flac_files.append((flac_file, relative_path))
    
    return flac_files


def create_output_directory(base_path, relative_path):
    """
    Create the output directory preserving the relative path structure.
    
    Args:
        base_path (Path): The base path containing 'out' folder
        relative_path (Path): Relative path from 'in' folder to preserve structure
        
    Returns:
        Path: Path to the output directory
    """
    out_path = base_path / "out" / relative_path.parent
    out_path.mkdir(parents=True, exist_ok=True)
    return out_path


def copy_image_files_recursive(base_path):
    """
    Copy all image files (album art) from source to destination directory recursively.
    
    Args:
        base_path (Path): The base path containing 'in' and 'out' folders
        
    Returns:
        int: Number of image files copied
    """
    in_path = base_path / "in"
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif']
    copied_count = 0
    
    # Find all image files recursively
    for image_file in in_path.rglob("*"):
        if image_file.is_file() and image_file.suffix.lower() in image_extensions:
            # Get relative path from 'in' folder
            relative_path = image_file.relative_to(in_path)
            dest_file = base_path / "out" / relative_path
            
            # Create destination directory if it doesn't exist
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                shutil.copy2(image_file, dest_file)
                copied_count += 1
            except Exception as e:
                print(f"  Warning: Failed to copy {image_file.name} to {dest_file}: {e}", file=sys.stderr)
    
    return copied_count


def convert_flac_to_mp3(flac_file, output_file, bitrate_preset="V0", threads=0):
    """
    Convert a single FLAC file to MP3 format using ffmpeg-python.
    
    Args:
        flac_file (Path): Path to the input FLAC file
        output_file (Path): Path to the output MP3 file
        bitrate_preset (str): LAME bitrate preset (default: "V0")
        threads (int): Number of threads for ffmpeg (default: 0 = auto)
        
    Returns:
        tuple: (flac_file, success) where success is True if conversion was successful
    """
    try:
        # Parse the preset
        if bitrate_preset.upper().startswith("V"):
            # Variable bitrate preset (V0-V9)
            quality = bitrate_preset[1:]
            # Validate that quality is a single digit 0-9
            if not (quality.isdigit() and len(quality) == 1 and 0 <= int(quality) <= 9):
                print(f"Error: Invalid VBR preset '{bitrate_preset}'. Use V0-V9.", file=sys.stderr)
                return (flac_file, False)
            
            # Use ffmpeg-python for VBR conversion with multi-threading
            stream = ffmpeg.input(str(flac_file), thread_queue_size=512)
            stream = ffmpeg.output(stream, str(output_file), **{
                'codec:a': 'libmp3lame',
                'q:a': quality,
                'threads': threads
            })
            ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
        else:
            # Constant bitrate (e.g., "320", "256", "192")
            stream = ffmpeg.input(str(flac_file), thread_queue_size=512)
            stream = ffmpeg.output(stream, str(output_file), **{
                'codec:a': 'libmp3lame',
                'b:a': f'{bitrate_preset}k',
                'threads': threads
            })
            ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
        
        return (flac_file, True)
    
    except ffmpeg.Error as e:
        # Extract error message from stderr if available
        if hasattr(e, 'stderr') and e.stderr:
            error_msg = e.stderr.decode() if isinstance(e.stderr, bytes) else str(e.stderr)
        else:
            error_msg = str(e)
        print(f"Error converting {flac_file.name}: {error_msg}", file=sys.stderr)
        return (flac_file, False)
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
    
    parser.add_argument(
        "-t", "--threads",
        type=int,
        default=0,
        help="Number of threads for ffmpeg to use (default: 0 = auto-detect optimal number)"
    )
    
    parser.add_argument(
        "-j", "--jobs",
        type=int,
        default=1,
        help="Number of parallel conversion jobs (default: 1 = sequential processing)"
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
    
    # Find all FLAC files recursively
    print(f"Scanning for FLAC files recursively in: {base_path / 'in'}")
    flac_files_list = find_flac_files(base_path)
    
    if not flac_files_list:
        print("No FLAC files found.", file=sys.stderr)
        sys.exit(0)
    
    # Count total files and get unique directories
    total_files = len(flac_files_list)
    unique_dirs = set(relative_path.parent for _, relative_path in flac_files_list)
    
    print(f"Found {total_files} FLAC file(s) in {len(unique_dirs)} folder(s)")
    print(f"Using bitrate preset: {args.bitrate}")
    threads_msg = "auto" if args.threads == 0 else str(args.threads)
    print(f"Using threads per job: {threads_msg}")
    print(f"Using parallel jobs: {args.jobs}")
    print()
    
    # Prepare all conversion tasks
    all_conversion_tasks = []
    
    for flac_file, relative_path in flac_files_list:
        # Create output directory preserving structure
        output_dir = create_output_directory(base_path, relative_path)
        mp3_filename = flac_file.stem + ".mp3"
        output_file = output_dir / mp3_filename
        
        # Use the parent directory as the display path for grouping
        display_path = str(relative_path.parent) if str(relative_path.parent) != '.' else ""
        
        all_conversion_tasks.append((display_path, flac_file, output_file, mp3_filename))
    
    # Convert files
    converted = 0
    failed = 0
    images_copied = 0
    
    # Process files in parallel or sequentially
    if args.jobs > 1:
        # Parallel processing across all albums
        with ThreadPoolExecutor(max_workers=args.jobs) as executor:
            # Submit all conversion tasks
            future_to_file = {}
            for album_name, flac_file, output_file, mp3_filename in all_conversion_tasks:
                future = executor.submit(
                    convert_flac_to_mp3,
                    flac_file,
                    output_file,
                    args.bitrate,
                    args.threads
                )
                future_to_file[future] = (album_name, flac_file, mp3_filename)
            
            # Process results as they complete
            current_dir = None
            for future in as_completed(future_to_file):
                display_path, flac_file, mp3_filename = future_to_file[future]
                
                # Print directory name if switching to a new directory
                if current_dir != display_path:
                    if current_dir is not None:
                        print()
                    print(f"Processing: {display_path}")
                    current_dir = display_path
                
                try:
                    result_file, success = future.result()
                    print(f"  Converting: {flac_file.name} -> {mp3_filename}... {'✓' if success else '✗'}")
                    if success:
                        converted += 1
                    else:
                        failed += 1
                except Exception as e:
                    print(f"  Converting: {flac_file.name} -> {mp3_filename}... ✗")
                    print(f"  Unexpected error: {e}", file=sys.stderr)
                    failed += 1
    else:
        # Sequential processing (original behavior)
        current_dir = None
        for display_path, flac_file, output_file, mp3_filename in all_conversion_tasks:
            # Print directory header when switching directories
            if current_dir != display_path:
                print(f"Processing: {display_path}")
                current_dir = display_path
            
            print(f"  Converting: {flac_file.name} -> {mp3_filename}...", end=" ", flush=True)
            result_file, success = convert_flac_to_mp3(flac_file, output_file, args.bitrate, args.threads)
            if success:
                print("✓")
                converted += 1
            else:
                print("✗")
                failed += 1
    
    # Copy image files recursively
    print()
    print("Copying album artwork...")
    images_copied = copy_image_files_recursive(base_path)
    if images_copied > 0:
        print(f"  Copied {images_copied} image file(s)")
    
    # Summary
    print()
    print("=" * 50)
    print(f"Conversion complete!")
    print(f"  Audio files converted: {converted}/{total_files}")
    print(f"  Failed: {failed}")
    print(f"  Image files copied: {images_copied}")
    print("=" * 50)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
