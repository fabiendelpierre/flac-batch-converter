#!/usr/bin/env python3
"""
Get batch of music folders

Selects the specified number of folders from a given source path
(starting from the alphabetical top) and copies them to the specified
destination path. Safely handles special characters in folder names.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def get_folders(src_path):
    """
    Get sorted list of folders in src_path.

    Args:
        src_path (Path): Source directory path

    Returns:
        list: List of folder names sorted alphabetically
    """
    try:
        folders = sorted([
            item.name for item in src_path.iterdir()
            if item.is_dir()
        ])
        return folders
    except FileNotFoundError:
        print(f"Error: Source path '{src_path}' does not exist.", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied accessing '{src_path}'.", file=sys.stderr)
        sys.exit(1)


def copy_folders_with_rsync(src_path, dst_path, folder_names, verbose=False):
    """
    Copy folders using rsync. Handles special characters safely.

    Args:
        src_path (Path): Source directory path
        dst_path (Path): Destination directory path
        folder_names (list): List of folder names to copy
        verbose (bool): If True, use -av for verbose output, otherwise use -a
    """
    # Create destination if it doesn't exist
    dst_path.mkdir(parents=True, exist_ok=True)

    for folder_name in folder_names:
        src_folder = src_path / folder_name

        if not src_folder.exists():
            print(f"Warning: Folder '{folder_name}' not found, skipping.", file=sys.stderr)
            continue

        try:
            # Use rsync with --delete to match user's behavior
            # -a: archive mode (recursive, preserves permissions, etc.)
            # -v: verbose output (only if requested)
            rsync_args = ["rsync", "-av" if verbose else "-a", f"{src_folder}/", f"{dst_path}/{folder_name}/"]
            subprocess.run(
                rsync_args,
                check=True,
                capture_output=False
            )
            print(f"Copied: {folder_name}")
        except subprocess.CalledProcessError as e:
            print(f"Error copying '{folder_name}': {e}", file=sys.stderr)
            sys.exit(1)
        except FileNotFoundError:
            print("Error: rsync not found. Please install rsync.", file=sys.stderr)
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Copy a batch of folders from source to destination using rsync. "
                    "Safely handles special characters in folder names."
    )
    parser.add_argument(
        "source",
        type=Path,
        help="Source directory containing folders to copy"
    )
    parser.add_argument(
        "destination",
        type=Path,
        help="Destination directory where folders will be copied"
    )
    parser.add_argument(
        "-n", "--number",
        type=int,
        default=10,
        help="Number of folders to copy (default: 10)"
    )
    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="List the folders that would be copied without copying them"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output from rsync (use -av instead of -a)"
    )
    
    args = parser.parse_args()
    
    # Get available folders
    folders = get_folders(args.source)

    if not folders:
        print(f"No folders found in '{args.source}'.", file=sys.stderr)
        sys.exit(1)

    # Get batch
    batch = folders[:args.number]

    if args.list:
        print(f"Folders to copy ({len(batch)}):")
        for folder in batch:
            print(f"  - {folder}")
    else:
        if not batch:
            print("No folders to copy.")
            return

        print(f"Copying {len(batch)} folder(s) from '{args.source}' to '{args.destination}'...")
        copy_folders_with_rsync(args.source, args.destination, batch, verbose=args.verbose)
        print(f"Successfully copied {len(batch)} folder(s).")


if __name__ == "__main__":
    main()
