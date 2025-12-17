# FLAC Batch Converter

A Python script to batch convert FLAC audio files to MP3 format while preserving album directory structure.

## Features

- Batch conversion of FLAC files to MP3 format
- Preserves album directory structure
- Configurable bitrate/quality settings
- Support for Variable Bitrate (VBR) and Constant Bitrate (CBR)
- Uses ffmpeg with LAME encoder for high-quality MP3 output

## Requirements

- Python 3.6 or higher
- ffmpeg with libmp3lame support

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

## Installation

1. Clone this repository:
```bash
git clone https://github.com/fabiendelpierre/flac-batch-converter.git
cd flac-batch-converter
```

2. Make the script executable (Linux/macOS):
```bash
chmod +x flac_batch_converter.py
```

## Usage

### Directory Structure

The script expects the following directory structure:

```
<base_path>/
├── in/
│   ├── Album1/
│   │   ├── track1.flac
│   │   ├── track2.flac
│   │   └── ...
│   ├── Album2/
│   │   ├── track1.flac
│   │   └── ...
│   └── ...
└── out/
    └── (converted files will be placed here)
```

### Basic Usage

Convert FLAC files using the default V0 preset (highest quality VBR):

```bash
python3 flac_batch_converter.py /path/to/music
```

or

```bash
./flac_batch_converter.py /path/to/music
```

### Advanced Usage

**Using V2 preset (high quality VBR):**
```bash
python3 flac_batch_converter.py /path/to/music --bitrate V2
```

**Using constant 320kbps bitrate:**
```bash
python3 flac_batch_converter.py /path/to/music --bitrate 320
```

**Using constant 192kbps bitrate:**
```bash
python3 flac_batch_converter.py /path/to/music --bitrate 192
```

### Command-Line Options

```
usage: flac_batch_converter.py [-h] [-b BITRATE] base_path

Batch convert FLAC files to MP3 format.

positional arguments:
  base_path             Base path containing 'in' and 'out' directories

optional arguments:
  -h, --help            show this help message and exit
  -b BITRATE, --bitrate BITRATE
                        Bitrate preset: V0-V9 for VBR (default: V0), or
                        constant bitrate like 320, 256, 192
```

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

# Convert with V0 preset
python3 flac_batch_converter.py /tmp/music

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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.