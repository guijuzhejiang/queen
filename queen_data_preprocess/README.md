# queen_data_preprocess

### Activate conda environment

Before running the script, ensure that you have activated the `queen` conda environment. This will ensure that all necessary dependencies are available.

```bash
conda activate queen
```

## How to use `download2render.sh`

This script automates the entire pipeline for data preprocessing, training, and rendering. It performs the following steps:
1. Downloads the specified dataset.
2. Executes multi-view data preprocessing (using `preprocess_multipleview.sh`).
3. Initiates the training process (using `train.py`).
4. Performs rendering (using `render_fvv.py`).

### Usage

```bash
./download2render.sh <workdir> <GPU_ID>
```

- `<workdir>`: The base path where the dataset will be downloaded and processed (e.g., `/yourdatapath/dynerf`). The script will create a subdirectory within this path for the specific dataset.
- `<GPU_ID>`: The CUDA device ID to use (e.g., `0`).

### Example

```bash
cd yourcodepath/queen
./queen_data_preprocess/download2render.sh /yourdatapath 0
```

### Output Location

Upon successful completion, the trained model and rendering results will be located in the `./output/<dataset_name>_trained` directory within your project root.

To download other datasets, modify the `URL` variable in the `download2render.sh` script.