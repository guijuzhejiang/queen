#!/usr/bin/env bash

# Usage example：
# bash queen_data_preprocess/preprocess2render.sh /yourdatapath/dynerf/coffee_martini 0

# Allow the command to exit if it fails
set -e

# Parameters: The first is the work directory, and the second is the CUDA ID
if [ $# -lt 2 ]; then
  echo "[ERROR] Missing arguments."
  echo "Usage: bash queen_data_preprocess/preprocess2render.sh <workdir> <GPU_ID>"
  echo "Example: bash queen_data_preprocess/preprocess2render.sh /yourdatapath/dynerf 0"
  exit 1
fi

workdir="$1"            # e.g. /home/zzg/data/CV/dynerf/Take_183926
CUDA_ID="$2"

# Set the CUDA devices
export CUDA_VISIBLE_DEVICES="$CUDA_ID"

echo "==== Preprocessing and Training Start ===="
echo "Work directory = $workdir"
echo "CUDA_VISIBLE_DEVICES = $CUDA_VISIBLE_DEVICES"
echo "--------------------------"

# Step 1: Execute the data preprocessing script
echo "[1/3] Executing data preprocessing script..."
bash queen_data_preprocess/preprocess_multipleview.sh "$workdir" "$CUDA_ID"
if [ $? -ne 0 ]; then
  echo "[ERROR] Step 1 failed: queen_data_preprocess/preprocess_multipleview.sh"
  exit 1
fi
echo "[OK] Step 1 completed."
echo "--------------------------"

# Step 2: Execute the training
echo "[2/3] Executing training: python train.py"
workdir_4dg="${workdir}_4DG"
data_name=$(basename "$workdir_4dg")
python train.py --config configs/dynerf.yaml --log_compressed --log_ply -s "$workdir_4dg" -m ./output/"$data_name"_trained
if [ $? -ne 0 ]; then
  echo "[ERROR] Step 2 failed: train.py"
  exit 1
fi
echo "[OK] Step 2 completed."
echo "--------------------------"

# Step 3: Execute the rending
echo "[3/3] Executing rending: python render_fvv.py"
python render_fvv.py --config configs/dynerf.yaml -s "$workdir_4dg" -m ./output/"$data_name"_trained
if [ $? -ne 0 ]; then
  echo "[ERROR] Step 3 failed: render_fvv.py"
  exit 1
fi
echo "[OK] Step 3 completed."
echo "--------------------------"

echo "==== Preprocessing and Training completed successfully ===="
echo "Trained results directory: ./output/${data_name}_trained"
