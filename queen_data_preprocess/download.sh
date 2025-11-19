#!/usr/bin/env bash
set -euo pipefail

workdir="$1"
URL="$2"      #"https://github.com/facebookresearch/Neural_3D_Video/releases/download/v1.0/cook_spinach.zip"

# === Configuration ===
FILE="$(basename "$URL")"       # cook_spinach.zip
BASENAME="${FILE%.zip}"                      # e.g. cook_spinach
OUTDIR="${workdir}/${BASENAME}"               # e.g. ./data/cook_spinach

# === Dependency check ===
if ! command -v unzip >/dev/null 2>&1; then
  echo "Error: unzip is not installed. Please install it (e.g. apt install unzip or brew install unzip)." >&2
  exit 1
fi

if ! command -v curl >/dev/null 2>&1 && ! command -v wget >/dev/null 2>&1; then
  echo "Error: either curl or wget is required to download the file." >&2
  exit 1
fi

mkdir -p "$workdir"
cd "$workdir"

# === Download the archive ===
if command -v curl >/dev/null 2>&1; then
  echo "Downloading $URL using curl ..."
  curl -fSL "$URL" -o "$FILE"
else
  echo "Downloading $URL using wget ..."
  wget -q -O "$FILE" "$URL"
fi
echo "Download completed: $(pwd)/$FILE"

# === Extract the archive ===
echo "Extracting to $workdir ..."
unzip -o "$FILE" -d "$workdir" >/dev/null
echo "Extraction completed."

# === Delete pose files after extraction ===
# Find and remove any files containing 'pose' or 'poses' in their name (case-insensitive)
if find "$OUTDIR" -type f \( -iname '*pose*' -o -iname 'poses.*' \) -print -quit | grep -q .; then
  echo "Found the following pose/poses files to delete:"
  find "$OUTDIR" -type f \( -iname '*pose*' -o -iname 'poses.*' \) -print
  # Actually remove them
  find "$OUTDIR" -type f \( -iname '*pose*' -o -iname 'poses.*' \) -exec rm -v {} +
else
  echo "No pose/poses files found after extraction."
fi

echo "Data preparation completed. Data directory: $(realpath "$OUTDIR")"
