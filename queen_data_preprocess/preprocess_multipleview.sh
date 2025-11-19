#!/usr/bin/env bash

# Usage example：
#   ./preprocess_multipleview.sh /yourdatapath/dynerf/coffee_martini 1

# Allow the command to exit if it fails.
set -e

# parameters: The first is the workdir, and the second is the CUDA ID.
if [ $# -lt 2 ]; then
  echo "[ERROR] Missing arguments."
  echo "Usage: ./preprocess_multipleview.sh <workdir> <GPU_ID>"
  echo "Example: ./preprocess_multipleview.sh /yourdatapath/dynerf/coffee_martini 1"
  exit
fi

workdir="$1"
CUDA_ID="$2"

# Configure CUDA devices
export CUDA_VISIBLE_DEVICES="$CUDA_ID"
workdir_4dg="${workdir}_4DG"
echo "==== preprocess start ===="
echo "workdir = $workdir"
echo "outputdir = $workdir_4dg"
echo "CUDA_VISIBLE_DEVICES = $CUDA_VISIBLE_DEVICES"
echo "--------------------------"

## Step 1: Copy working directory
echo "[1/7] Copying workdir to $workdir_4dg ..."
if [ -d "$workdir_4dg" ]; then
  echo "[INFO] Target folder $workdir_4dg already exists. Skipping copy."
else
  cp -r "$workdir" "$workdir_4dg"
  echo "[OK] Copied to $workdir_4dg"
fi
echo "[OK] Step 2-1 finished."
echo "--------------------------"

# Step 2：Extract video frames
echo "[2/7] Extracting frames: python queen_data_preprocess/scripts/preprocess_dynerf.py --datadir \"$workdir_4dg\""
#python queen_data_preprocess/scripts/preprocess_dynerf.py --datadir "$workdir_4dg"
python queen_data_preprocess/scripts/extract_videos.py --datadir "$workdir_4dg" -n 10
if [ $? -ne 0 ]; then
  echo "[ERROR] Step 2-2 failed: preprocess_dynerf.py"
  exit
fi
echo "[OK] Step 2-2 finished."
echo "--------------------------"

# Step 3：Run COLMAP to generate image_colmap #extract_first_frame.py
echo "[3/7] generate image_colmap: python queen_data_preprocess/scripts/extract_first_frame.py \"$workdir_4dg\""
python queen_data_preprocess/scripts/extract_first_frame.py "$workdir_4dg"
if [ $? -ne 0 ]; then
  echo "[ERROR] Step 2-3 failed: extract_first_frame.py"
  exit
fi
echo "[OK] Step 2-3 finished."
echo "--------------------------"

# Step 4: generate poses_bounds.npy
echo "[4/7] generate poses_bounds.npy use:imgs2poses.py"
mkdir -p "$workdir_4dg/pose/images"
cp -r "$workdir_4dg/image_colmap/"* "$workdir_4dg/pose/images/"
python queen_data_preprocess/scripts/imgs2poses.py "$workdir_4dg/pose/"
mv "$workdir_4dg/pose/poses_bounds.npy" "$workdir_4dg/poses_bounds.npy"
if [ $? -ne 0 ]; then
  echo "[ERROR] Step 2-4 failed: imgs2poses.py"
  exit
fi
echo "[OK] Step 2-4 finished."
echo "--------------------------"

# Step 5：Run COLMAP to generate point clouds
echo "[5/7] Running COLMAP: bash queen_data_preprocess/colmap.sh \"$workdir_4dg\" llff"
bash queen_data_preprocess/colmap.sh "$workdir_4dg" llff "$CUDA_ID"
if [ $? -ne 0 ]; then
  echo "[ERROR] Step 2-5 failed: colmap.sh"
  exit
fi
echo "[OK] Step 2-5 finished."
echo "--------------------------"

# Step 6：Downsampled point cloud
FUSED="$workdir_4dg/colmap/dense/workspace/fused.ply"
OUT="$workdir_4dg/points3D_downsample2.ply"
echo "[6/7] Downsampling point cloud: python queen_data_preprocess/scripts/downsample_point.py \"$FUSED\" \"$OUT\""
python queen_data_preprocess/scripts/downsample_point.py "$FUSED" "$OUT"
if [ $? -ne 0 ]; then
  echo "[ERROR] Step 2-6 failed: downsample_point.py"
  exit
fi
echo "[OK] Step 2-6 finished."
echo "--------------------------"

# Step 7: Delete mp4 files
echo "[7/7] Cleaning up video files (*.mp4) in $workdir_4dg ..."
find "$workdir_4dg" -type f -name "*.mp4" -exec rm -f {} \;
echo "[OK] Removed all .mp4 files."
echo "[OK] Step 2-7 finished."
echo "--------------------------"

echo "==== preprocess completed successfully ===="
echo "Working directory: $workdir_4dg"
echo "Generated downsampled point cloud: $OUT"
