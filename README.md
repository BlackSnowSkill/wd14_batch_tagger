# BSS WD14 Batch Tagger

[![ComfyUI Registry](https://img.shields.io/badge/ComfyUI-Registry-blue)](https://registry.comfy.org/blacksnowskill/wd14-batch-tagger)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful ComfyUI custom node for automatic image tagging using WD14 (Waifu Diffusion 1.4) models with batch processing capabilities.

> **Available in ComfyUI Registry!** Install directly from [registry.comfy.org](https://registry.comfy.org/blacksnowskill/wd14-batch-tagger)

## Features

- **Multiple Model Support**: Compatible with 4 different WD14 v3 model architectures
- **Automatic Model Download**: Models are automatically downloaded from Hugging Face when needed
- **Progress Indication**: Real-time progress bar in ComfyUI interface
- **GPU Acceleration**: Optional CUDA support for faster processing
- **Batch Processing**: Efficient processing of multiple images from folders
- **Flexible Tagging**: Customizable thresholds and tag filtering
- **Multiple Formats**: Support for JPG, JPEG, PNG, and WEBP images
- **Tag Management**: Prepend custom tags and exclude unwanted tags

## Installation

### Manual Installation

1. Clone this repository into your ComfyUI custom nodes folder:
```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/blacksnowskill/wd14_batch_tagger.git
```

2. Install dependencies:
```bash
cd wd14_batch_tagger
pip install -r requirements.txt
```

3. Restart ComfyUI

### Via ComfyUI Registry (Recommended)

1. Open ComfyUI Manager
2. Go to the Registry tab
3. Search for "BSS WD14 Batch Tagger" or visit [registry.comfy.org](https://registry.comfy.org/blacksnowskill/wd14-batch-tagger)
4. Click Install
5. Restart ComfyUI

The node will be automatically installed with all dependencies.

### Via ComfyUI Manager (Legacy)

1. Open ComfyUI Manager
2. Search for "BSS WD14 Batch Tagger" or "wd14-batch-tagger"
3. Click Install
4. Restart ComfyUI

## Usage

### Node Overview

#### BSS Load Images from Folder 📂
Loads images from a specified folder and returns them as a batch for processing.

**Inputs:**
- `folder_path` (STRING): Path to folder containing images

**Outputs:**
- `images` (IMAGE): List of loaded images
- `filenames` (STRING): List of corresponding filenames
- `folder_path` (STRING): Original folder path

#### BSS WD14 Batch Tagger 🌿
Processes images using WD14 models and generates automatic tags.

**Inputs:**
- `image` (IMAGE): Input image to tag
- `filename` (STRING): Original filename
- `folder_path` (STRING): Output folder for tag files
- `model` (SELECT): WD14 model to use (automatically downloads if not available)
  - ✅ WD ViT Tagger v3 (wd-vit-tagger-v3) - *Available locally*
  - ⬇️ WD SwinV2 Tagger v3 (wd-swinv2-tagger-v3) - *Will download*
  - ⬇️ WD EVA02 Large Tagger v3 (wd-eva02-large-tagger-v3) - *Will download*
  - ⬇️ WD ConvNeXT Tagger v3 (wd-convnext-tagger-v3) - *Will download*
- `threshold` (FLOAT): Confidence threshold for tags (0.0-1.0, default: 0.35)
- `character_threshold` (FLOAT): Character-specific threshold (0.0-1.0, default: 0.85)
- `replace_underscore` (BOOLEAN): Replace underscores with spaces in tags
- `use_gpu` (BOOLEAN): Enable GPU acceleration
- `prepend_tags` (STRING): Custom tags to prepend to results
- `exclude_tags` (STRING): Tags to exclude from results (comma-separated)

**Outputs:**
- `tags` (STRING): Generated tags for the image

### Workflow Example

1. Use **BSS Load Images from Folder** to load images from your dataset
2. Connect the output to **BSS WD14 Batch Tagger** for each image
3. Configure model settings and thresholds
4. Run the workflow to generate tag files (.txt) in your specified folder

## Models

The node supports four pre-trained WD14 v3 models that are automatically downloaded from Hugging Face:

- **WD ViT Tagger v3**: Fast inference with good quality (default)
- **WD SwinV2 Tagger v3**: Balanced performance and speed
- **WD EVA02 Large Tagger v3**: Large model with excellent accuracy
- **WD ConvNeXT Tagger v3**: Modern architecture with good performance

### Model Download

Models are automatically downloaded from Hugging Face when first used. Models are cached locally in the `models/` folder and won't be re-downloaded unless manually deleted.

**Status Indicators:**
- ✅ **Available locally** - Model is already downloaded and ready to use
- ⬇️ **Will download** - Model will be automatically downloaded from Hugging Face when first used

**Note:** Status indicators update automatically when models are downloaded. You may need to refresh the node or restart ComfyUI to see updated status indicators.

### Progress Monitoring

The node provides real-time progress indication in the ComfyUI interface:

#### Progress Steps:
- **Model Download** (0-100%):
  - 0-10%: Starting download
  - 10-50%: Downloading model file
  - 50-90%: Downloading tags file
  - 90-100%: Download complete

- **Image Processing** (0-100%):
  - 0-20%: Preparing model
  - 20-40%: Loading model
  - 40-60%: Loading tags database
  - 60-80%: Processing image
  - 80-100%: Running AI inference

- **Image Loading** (0-100%):
  - Shows progress for each image being loaded from folder

#### Console Output:
Watch the ComfyUI console for detailed progress messages:
- `[BSS WD14] Progress: 25% - Downloading wd-vit-tagger-v3 model file...`
- `[BSS WD14] Progress: 75% - Processing image 'example.jpg'...`
- `[BSS WD14] Progress: 100% - Complete! Generated 15 tags for 'example.jpg'`

## Performance Tips

- **GPU Acceleration**: Enable `use_gpu` for significant speed improvements (requires CUDA-compatible GPU)
- **Batch Size**: Process images individually for optimal memory usage
- **Threshold Tuning**: Lower thresholds capture more tags but may include noise
- **Tag Filtering**: Use `exclude_tags` to remove unwanted common tags

## Requirements

- Python 3.8+
- ComfyUI
- CUDA-compatible GPU (optional, for GPU acceleration)

### Dependencies

- `onnxruntime>=1.16.0`
- `numpy>=1.24.0`
- `pillow>=9.0.0`
- `huggingface-hub>=0.16.0`

## Troubleshooting

### Common Issues

1. **Model Loading Errors**: Ensure model files are in the `models/` folder
2. **GPU Not Available**: The node will automatically fall back to CPU if GPU is unavailable
3. **Memory Issues**: Process smaller batches or use CPU-only mode for large images
4. **Empty Tag Files**: Check threshold settings and input image quality

### Logs

Check ComfyUI console output for detailed logging information. The node provides informative messages about processing status and any errors encountered.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on the WD14 (Waifu Diffusion 1.4) tagging models
- Built for the ComfyUI ecosystem
- Thanks to the open-source community for the foundational models and tools

## Author

**Blacksnowskill**
- GitHub: [@blacksnowskill](https://github.com/blacksnowskill)
- ComfyUI Community: [BSS](https://github.com/blacksnowskill)

---

*For support and updates, please visit the [GitHub repository](https://github.com/blacksnowskill/wd14_batch_tagger).*
