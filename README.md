# FLAC Batch Converter

A Python script to batch convert FLAC audio files to MP3 format while preserving album directory structure.

The entire script was written by Copilot. For context: I ditched Windows a while back. In Windows, I was an avid user of dBpoweramp for batch conversions of audio file. I used it for decades. I now only have Mac and Linux machines. I needed a simple, cross-platform script that behaves in a specific way: start with a base path with a subfolder called `in`. Copy a bunch of FLAC albums in separate folders to the `in` folder. Run the conversion to MP3 and write them to another subfolder called `out` and replicate the album folders and put the MP3s in there. Do this with high parallelism to save time when processing hundreds of files.

This script does exactly that and nothing more, uses Python and works on macOS and Linux. It might even work on Windows, I don't know because I didn't test it in Windows.

## Features

- Batch conversion of FLAC files to MP3 format
- **Recursive directory scanning** - finds FLAC files at any depth
- **Preserves complete folder structure** - including multi-disc albums (CD1, CD2, etc.)
- **Automatically copies album artwork** (jpg, png, gif, etc.) at all directory levels
- Configurable bitrate/quality settings
- Support for Variable Bitrate (VBR) and Constant Bitrate (CBR)
- **True parallel processing** across multiple albums simultaneously
- Multi-threading support for individual file conversions
- Uses ffmpeg with LAME encoder for high-quality MP3 output

## Requirements

- Python 3.8 or higher
- ffmpeg with libmp3lame support
- [uv](https://docs.astral.sh/uv/) package manager (recommended)

### Installing ffmpeg

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**macOS (using Homebrew):**
```bash
brew install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.

### Installing uv

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Or install via pip:
```bash
pip install uv
```

## Installation

1. Clone this repository:
```bash
git clone https://github.com/fabiendelpierre/flac-batch-converter.git
cd flac-batch-converter
```

2. Install dependencies using uv:
```bash
uv sync
```

This will create a virtual environment and install all required Python dependencies (including `ffmpeg-python`).

## Usage

### Directory Structure

The script recursively scans for FLAC files and preserves the complete directory structure:

```
<base_path>/
├── in/
│   ├── Album1/
│   │   ├── track1.flac
│   │   ├── track2.flac
│   │   └── cover.jpg
│   ├── Album2 - Multi-Disc/
│   │   ├── cover.jpg
│   │   ├── CD1/
│   │   │   ├── track1.flac
│   │   │   └── track2.flac
│   │   └── CD2/
│   │       ├── track1.flac
│   │       └── track2.flac
│   └── ...
└── out/
    └── (converted files with preserved structure)
```

**Key Features:**
- **Recursive scanning**: Finds FLAC files at any depth
- **Structure preservation**: Maintains exact folder hierarchy in output
- **Multi-disc support**: Handles albums with CD1, CD2, Disc1, Disc2, etc. subfolders
- **Image preservation**: Copies artwork at all levels of the directory tree

### Basic Usage

Convert FLAC files using the default V0 preset (highest quality VBR):

```bash
uv run flac_batch_converter.py /path/to/music
```

Or, if you want to use the virtual environment directly:

```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python flac_batch_converter.py /path/to/music
```

### Advanced Usage

**Using V2 preset (high quality VBR):**
```bash
uv run flac_batch_converter.py /path/to/music --bitrate V2
```

**Using constant 320kbps bitrate:**
```bash
uv run flac_batch_converter.py /path/to/music --bitrate 320
```

**Using constant 192kbps bitrate:**
```bash
uv run flac_batch_converter.py /path/to/music --bitrate 192
```

**Using multi-threading for faster conversion:**
```bash
# Specify number of threads (e.g., 4 threads)
uv run flac_batch_converter.py /path/to/music --threads 4

# Or use auto-detection (default, lets FFmpeg choose optimal thread count)
uv run flac_batch_converter.py /path/to/music --threads 0
```

**Using parallel processing to convert multiple files simultaneously:**
```bash
# Convert 4 files at once (recommended for systems with 4+ CPU cores)
uv run flac_batch_converter.py /path/to/music --jobs 4

# Combine parallel jobs with per-job threading for maximum performance
uv run flac_batch_converter.py /path/to/music --jobs 4 --threads 2

# Process all files in parallel (use with caution on systems with limited RAM)
uv run flac_batch_converter.py /path/to/music --jobs 8
```

### Command-Line Options

```
usage: flac_batch_converter.py [-h] [-b BITRATE] [-t THREADS] [-j JOBS] base_path

Batch convert FLAC files to MP3 format.

positional arguments:
  base_path             Base path containing 'in' and 'out' directories

optional arguments:
  -h, --help            show this help message and exit
  -b BITRATE, --bitrate BITRATE
                        Bitrate preset: V0-V9 for VBR (default: V0), or
                        constant bitrate like 320, 256, 192
  -t THREADS, --threads THREADS
                        Number of threads for ffmpeg to use (default: 0 = 
                        auto-detect optimal number)
  -j JOBS, --jobs JOBS  Number of parallel conversion jobs (default: 1 = 
                        sequential processing)
```

### Performance Tuning

The script offers two levels of parallelism for optimal performance:

1. **`--threads` (FFmpeg threading)**: Controls how many CPU threads FFmpeg uses *within* each conversion job. This helps individual files convert faster. Default is `0` (auto-detect).

2. **`--jobs` (Parallel jobs)**: Controls how many files are converted *simultaneously* **across all albums**. This is true parallelism - multiple files from different albums being processed at the same time. Default is `1` (sequential).

**Key improvement**: Parallel processing now works across all albums, not one album at a time. With `--jobs 8` and folders containing 6 files each, the script will start processing files from the next folder while finishing the first, maximizing CPU utilization.

**Recommendations:**
- For systems with 4+ CPU cores: Use `--jobs 4` or `--jobs 8` for significant speed improvements
- Combine both for maximum performance: `--jobs 4 --threads 2`
- Be mindful of RAM usage with high `--jobs` values, especially with large FLAC files
- Start with `--jobs` equal to the number of CPU cores on your system

**Album Artwork:**
- Image files (jpg, png, gif, bmp, webp, tiff) are automatically copied from source to destination folders
- Useful for preserving album cover art for music library imports

## Bitrate Presets

### Variable Bitrate (VBR) - LAME V presets

- **V0**: ~245 kbps (highest quality VBR, transparent)
- **V1**: ~225 kbps (very high quality)
- **V2**: ~190 kbps (high quality, recommended)
- **V3**: ~175 kbps
- **V4**: ~165 kbps (medium quality)
- **V5**: ~130 kbps
- **V6**: ~115 kbps
- **V7**: ~100 kbps
- **V8**: ~85 kbps
- **V9**: ~65 kbps (lowest quality)

### Constant Bitrate (CBR)

Common values: 320, 256, 192, 128 (in kbps)

## Example

```bash
# Create directory structure
mkdir -p /tmp/music/in/MyAlbum
mkdir -p /tmp/music/out

# Place FLAC files in /tmp/music/in/MyAlbum/

# Convert with V0 preset (sequential)
uv run flac_batch_converter.py /tmp/music

# Convert with parallel processing (4 files at once)
uv run flac_batch_converter.py /tmp/music --jobs 4

# Output will be in /tmp/music/out/MyAlbum/
```

## Output

The script will:
1. Scan the `in/` directory for album subdirectories containing FLAC files
2. Create corresponding album subdirectories in the `out/` directory
3. Convert each FLAC file to MP3 format
4. Display progress and a summary upon completion

Example output:
```
Scanning for FLAC files in: /tmp/music/in
Found 12 FLAC file(s) across 2 album(s)
Using bitrate preset: V0

Processing album: MyAlbum
  Converting: track1.flac -> track1.mp3... ✓
  Converting: track2.flac -> track2.mp3... ✓
  ...

==================================================
Conversion complete!
  Successful: 12
  Failed: 0
  Total: 12
==================================================
```

## License

This project is licensed under the GNU GPLv3 - see the [LICENSE](LICENSE) file for details.
