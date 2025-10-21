# BSS WD14 Batch Tagger

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Automatic image tagging using WD14 models with batch processing for ComfyUI.

## Features

- **4 WD14 v3 Models**: ViT, SwinV2, EVA02, ConvNeXT
- **Auto Download**: Models download automatically from Hugging Face
- **GPU Support**: CUDA acceleration for faster processing
- **Batch Processing**: Process multiple images from folders
- **Format Support**: JPG, JPEG, PNG, WEBP
- **Custom Tags**: Add/remove tags as needed

## Installation

### Via ComfyUI Manager

1. Open ComfyUI Manager
2. Go to Registry tab
3. Search for "BSS WD14 Batch Tagger"
4. Click Install
5. Restart ComfyUI

### Manual Installation

```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/BlackSnowSkill/wd14_batch_tagger.git
cd wd14_batch_tagger
pip install -r requirements.txt
```

## Usage

### Nodes

**BSS Load Images from Folder 📂**
- Loads images from a folder for batch processing

**BSS WD14 Batch Tagger 🌿**
- Tags images using WD14 models
- Saves tags to .txt files

### Basic Workflow

1. Use **BSS Load Images from Folder** to load your images
2. Connect to **BSS WD14 Batch Tagger** for each image
3. Set output folder for tag files
4. Run the workflow

### Settings

- **Model**: Choose WD14 model (auto-downloads if needed)
- **Threshold**: Tag confidence (0.35 default)
- **GPU**: Enable for faster processing
- **Prepend/Exclude**: Add custom tags or remove unwanted ones

## Models

- **WD ViT Tagger v3**: Fast, good quality (default)
- **WD SwinV2 Tagger v3**: Balanced speed/quality
- **WD EVA02 Large Tagger v3**: Best accuracy
- **WD ConvNeXT Tagger v3**: Modern architecture

Models download automatically on first use.

## Requirements

- Python 3.8+
- ComfyUI
- CUDA GPU (optional)

## Support

- **GitHub**: [Issues](https://github.com/BlackSnowSkill/wd14_batch_tagger/issues)
- **Civitai**: [Profile](https://civitai.com/user/llikswonskcalb)
- **Boosty**: [Support](https://boosty.to/blacksnowskill)

## License

MIT License - see LICENSE file for details.

---

**Author**: Blacksnowskill