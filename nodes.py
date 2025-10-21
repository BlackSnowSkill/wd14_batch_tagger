import os
import numpy as np
from PIL import Image
from pathlib import Path
import csv
import onnxruntime as ort
from typing import Tuple, List, Dict, Any, Optional
import logging
from huggingface_hub import hf_hub_download
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ComfyUI progress system integration
def update_progress(progress: float, message: str = ""):
    """Update progress for ComfyUI interface."""
    # This will be handled by ComfyUI's built-in progress system
    # The progress value should be between 0.0 and 1.0
    print(f"[BSS WD14] Progress: {int(progress * 100)}% - {message}")

# Global progress manager for batch processing
class BatchProgressManager:
    def __init__(self):
        self.pbar = None
        self.current_image = 0
        self.total_images = 0
        self.model_loaded = False
        
    def init_progress(self, total_images: int):
        """Initialize progress bar for batch processing."""
        import comfy.utils
        self.total_images = total_images
        self.current_image = 0
        self.model_loaded = False
        self.pbar = comfy.utils.ProgressBar(total_images)
        
    def update_image_progress(self, message: str = ""):
        """Update progress for current image."""
        if self.pbar:
            self.pbar.update(1)
            if message:
                logger.info(f"Image {self.current_image + 1}/{self.total_images} - {message}")
    
    def next_image(self):
        """Move to next image."""
        self.current_image += 1

# Global progress manager instance
batch_progress = BatchProgressManager()

# Global model cache
model_cache = {
    'session': None,
    'tags': None,
    'model_name': None,
    'input_name': None,
    'input_size': None
}

# Model configurations with Hugging Face repository info
MODEL_CONFIGS = {
    "wd-vit-tagger-v3": {
        "repo_id": "SmilingWolf/wd-vit-tagger-v3",
        "filename": "model.onnx",
        "csv_filename": "selected_tags.csv",
        "display_name": "WD ViT Tagger v3"
    },
    "wd-swinv2-tagger-v3": {
        "repo_id": "SmilingWolf/wd-swinv2-tagger-v3", 
        "filename": "model.onnx",
        "csv_filename": "selected_tags.csv",
        "display_name": "WD SwinV2 Tagger v3"
    },
    "wd-eva02-large-tagger-v3": {
        "repo_id": "SmilingWolf/wd-eva02-large-tagger-v3",
        "filename": "model.onnx", 
        "csv_filename": "selected_tags.csv",
        "display_name": "WD EVA02 Large Tagger v3"
    },
    "wd-convnext-tagger-v3": {
        "repo_id": "SmilingWolf/wd-convnext-tagger-v3",
        "filename": "model.onnx",
        "csv_filename": "selected_tags.csv", 
        "display_name": "WD ConvNeXT Tagger v3"
    }
}

def ensure_model_available(model_name: str) -> Tuple[bool, str, str]:
    """
    Ensure model and CSV files are available, download from Hugging Face if needed.
    
    Args:
        model_name: Name of the model to check/download
        
    Returns:
        Tuple of (success, model_path, csv_path)
    """
    if model_name not in MODEL_CONFIGS:
        logger.error(f"Unknown model: {model_name}")
        return False, "", ""
        
    model_dir = Path(__file__).parent / "models"
    model_dir.mkdir(exist_ok=True)
    
    config = MODEL_CONFIGS[model_name]
    model_path = model_dir / f"{model_name}.onnx"
    csv_path = model_dir / f"{model_name}.csv"
    
    # Check if both files exist
    if model_path.exists() and csv_path.exists():
        logger.info(f"Model {model_name} already available")
        return True, str(model_path), str(csv_path)
    
    # Download from Hugging Face with progress indication
    try:
        logger.info(f"Downloading {model_name} from Hugging Face...")
        update_progress(0, f"Starting download of {model_name}...")
        
        # Download ONNX model
        if not model_path.exists():
            update_progress(0.1, f"Downloading {model_name} model file...")
            hf_hub_download(
                repo_id=config["repo_id"],
                filename=config["filename"],
                local_dir=str(model_dir),
                local_dir_use_symlinks=False
            )
            # Rename to our naming convention
            downloaded_model = model_dir / config["filename"]
            if downloaded_model.exists():
                downloaded_model.rename(model_path)
            update_progress(0.5, f"Model file downloaded successfully!")
        
        # Download CSV tags
        if not csv_path.exists():
            update_progress(0.5, f"Downloading {model_name} tags file...")
            hf_hub_download(
                repo_id=config["repo_id"],
                filename=config["csv_filename"],
                local_dir=str(model_dir),
                local_dir_use_symlinks=False
            )
            # Rename to our naming convention
            downloaded_csv = model_dir / config["csv_filename"]
            if downloaded_csv.exists():
                downloaded_csv.rename(csv_path)
            update_progress(0.9, f"Tags file downloaded successfully!")
        
        update_progress(1.0, f"Download complete! {model_name} ready to use.")
        logger.info(f"Successfully downloaded {model_name}")
        return True, str(model_path), str(csv_path)
        
    except Exception as e:
        logger.error(f"Failed to download {model_name}: {e}")
        return False, "", ""

def get_available_models() -> List[str]:
    """
    Get list of all available models (both local and downloadable).
    
    Returns:
        List of all available model names
    """
    # Always return all models from config, regardless of local availability
    return list(MODEL_CONFIGS.keys())

def load_model_once(model_name: str, use_gpu: bool) -> bool:
    """
    Load model and tags once for batch processing.
    
    Args:
        model_name: Name of the model to load
        use_gpu: Whether to use GPU acceleration
        
    Returns:
        True if model loaded successfully, False otherwise
    """
    global model_cache
    
    # Check if model is already loaded
    if model_cache['model_name'] == model_name and model_cache['session'] is not None:
        return True
    
    try:
        # Ensure model is available (download if needed)
        success, model_path, csv_path = ensure_model_available(model_name)
        if not success:
            logger.error(f"Failed to ensure model availability: {model_name}")
            return False
        
        # Initialize ONNX session with GPU support
        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"] if use_gpu else ["CPUExecutionProvider"]
        
        try:
            sess = ort.InferenceSession(model_path, providers=providers)
        except Exception as e:
            logger.warning(f"GPU not available, falling back to CPU: {e}")
            sess = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
            
        input_name = sess.get_inputs()[0].name
        input_size = sess.get_inputs()[0].shape[1]

        # Load tags from CSV
        if not Path(csv_path).exists():
            logger.error(f"CSV file not found: {csv_path}")
            return False
            
        tags = []
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if len(row) > 1:
                    tags.append(row[1])
        
        # Cache the model and tags
        model_cache['session'] = sess
        model_cache['tags'] = tags
        model_cache['model_name'] = model_name
        model_cache['input_name'] = input_name
        model_cache['input_size'] = input_size
        
        logger.info(f"Model {model_name} loaded and cached successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error loading model {model_name}: {e}")
        return False

class BSS_LoadImagesFolder:
    """
    Load images from a folder and return them as a batch.
    Supports JPG, JPEG, PNG, and WEBP formats.
    Author: Blacksnowskill
    """
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "folder_path": ("STRING", {"multiline": False, "default": ""})
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("images", "filenames", "folder_path")
    OUTPUT_IS_LIST = (True, True, False)
    FUNCTION = "load_images"
    CATEGORY = "BSS/Image Processing"
    
    # ComfyUI progress bar support
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("inf")
    
    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        return True

    def load_images(self, folder_path: str) -> Tuple[List[np.ndarray], List[str], str]:
        """
        Load images from specified folder path.
        
        Args:
            folder_path: Path to folder containing images
            
        Returns:
            Tuple of (images, filenames, folder_path)
        """
        if not folder_path or not os.path.exists(folder_path):
            logger.error(f"Invalid folder path: {folder_path}")
            return [], [], folder_path
            
        # Support JPG, JPEG, PNG, and WEBP formats
        supported_extensions = (".jpg", ".jpeg", ".png", ".webp")
        folder = Path(folder_path)
        
        try:
            image_paths = sorted([p for p in folder.iterdir() 
                                if p.suffix.lower() in supported_extensions and p.is_file()])
        except Exception as e:
            logger.error(f"Error reading folder {folder_path}: {e}")
            return [], [], folder_path

        images, filenames = [], []
        total_images = len(image_paths)
        
        # Initialize global progress for batch processing
        batch_progress.init_progress(total_images)
        
        # Use ComfyUI's progress system
        import comfy.utils
        pbar = comfy.utils.ProgressBar(total_images)
        
        for i, image_path in enumerate(image_paths):
            # Update ComfyUI progress bar
            pbar.update(1)
            logger.info(f"Loading images... {i+1}/{total_images} - {image_path.name}")
            
            try:
                with Image.open(image_path) as img:
                    arr = np.array(img.convert("RGB"))
                    if arr.size == 0 or arr.shape[0] == 0 or arr.shape[1] == 0:
                        logger.warning(f"Empty array for {image_path.name}, skipping")
                        continue
                    images.append(arr)
                    filenames.append(image_path.name)
            except Exception as e:
                logger.error(f"Error loading {image_path.name}: {e}")

        logger.info(f"Loaded {len(images)} images from {folder_path}")
        return images, filenames, folder_path


class BSS_WD14BatchTagger:
    """
    WD14 Batch Tagger for automatic image tagging using WD14 models.
    Supports multiple model architectures and GPU acceleration.
    Author: Blacksnowskill
    """
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "image": ("IMAGE",),
                "filename": ("STRING",),
                "folder_path": ("STRING", {"default": ""}),
                "model": (cls._get_model_choices(), {"default": "wd-vit-tagger-v3"}),
                "threshold": ("FLOAT", {"default": 0.35, "min": 0.0, "max": 1.0, "step": 0.01}),
                "character_threshold": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.01}),
                "replace_underscore": ("BOOLEAN", {"default": True}),
                "use_gpu": ("BOOLEAN", {"default": False}),
                "prepend_tags": ("STRING", {"multiline": True, "default": ""}),
                "exclude_tags": ("STRING", {"multiline": True, "default": ""})
            }
        }
    
    @classmethod
    def _get_model_choices(cls) -> List[str]:
        """Get model choices with current status indicators."""
        # Get all available models
        available_models = get_available_models()
        
        # Check which models are locally available
        model_dir = Path(__file__).parent / "models"
        local_models = set()
        if model_dir.exists():
            for model_name in MODEL_CONFIGS.keys():
                model_path = model_dir / f"{model_name}.onnx"
                csv_path = model_dir / f"{model_name}.csv"
                if model_path.exists() and csv_path.exists():
                    local_models.add(model_name)
        
        # Create display names for the dropdown with status indicators
        model_choices = []
        for model_name in available_models:
            if model_name in MODEL_CONFIGS:
                status = "✅" if model_name in local_models else "⬇️"
                display_name = f"{status} {MODEL_CONFIGS[model_name]['display_name']} ({model_name})"
                model_choices.append(f"{model_name}|{display_name}")
        
        return model_choices
    
    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        """Validate inputs, especially model selection."""
        model = kwargs.get("model", "")
        if not model:
            return True
            
        # Extract model name from dropdown selection
        model_name = model.split("|")[0] if "|" in model else model
        
        # Check if model is in our config
        if model_name not in MODEL_CONFIGS:
            return f"Unknown model: {model_name}"
        
        return True
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        """Force refresh when model status changes."""
        # This will force ComfyUI to refresh the node when models are downloaded
        model_dir = Path(__file__).parent / "models"
        if not model_dir.exists():
            return float("inf")
        
        # Check modification time of models directory
        try:
            return model_dir.stat().st_mtime
        except:
            return float("inf")

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("tags",)
    OUTPUT_IS_LIST = (False,)
    FUNCTION = "tag_batch"
    OUTPUT_NODE = True
    CATEGORY = "BSS/Image Processing"
    
    # ComfyUI progress bar support
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("inf")
    
    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        return True

    def tag_batch(self, image: np.ndarray, filename: str, folder_path: str, model: str, 
                   threshold: float, character_threshold: float, replace_underscore: bool, 
                   use_gpu: bool, prepend_tags: str, exclude_tags: str) -> Tuple[str]:
        """
        Tag a single image using WD14 model and save tags to txt file.
        
        Args:
            image: Input image as numpy array
            filename: Original filename
            folder_path: Output folder path
            model: Model name (format: "model_name|display_name")
            threshold: Confidence threshold for tags
            character_threshold: Character-specific threshold
            replace_underscore: Whether to replace underscores with spaces
            use_gpu: Whether to use GPU acceleration
            prepend_tags: Tags to prepend to result
            exclude_tags: Tags to exclude from result
            
        Returns:
            Tuple containing the generated tags string
        """
        try:
            # Extract model name from dropdown selection (handle both formats)
            if "|" in model:
                model_name = model.split("|")[0]
            else:
                model_name = model
            
            # Load model once (cached for subsequent calls)
            if not load_model_once(model_name, use_gpu):
                logger.error(f"Failed to load model: {model_name}")
                return ("",)
            
            # Get cached model data
            sess = model_cache['session']
            tags = model_cache['tags']
            input_name = model_cache['input_name']
            input_size = model_cache['input_size']
            
            # Process tags (replace underscores if needed)
            processed_tags = []
            for tag in tags:
                processed_tag = tag.replace("_", " ") if replace_underscore else tag
                processed_tags.append(processed_tag)
            
            # Parse exclude tags
            exclude_list = [t.strip().lower() for t in exclude_tags.split(",") if t.strip()]

            # Process image
            if image is None or image.size == 0 or image.shape[0] == 0 or image.shape[1] == 0:
                logger.warning(f"Empty image array for {filename}, skipping")
                return ("",)

            img = Image.fromarray(image)
            ratio = input_size / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            
            if new_size[0] <= 0 or new_size[1] <= 0:
                logger.error(f"Invalid resize dimensions {new_size} for {filename}")
                return ("",)

            # Resize and center image
            img = img.resize(new_size, Image.LANCZOS)
            square = Image.new("RGB", (input_size, input_size), (255, 255, 255))
            paste_pos = ((input_size - new_size[0]) // 2, (input_size - new_size[1]) // 2)
            square.paste(img, paste_pos)
            
            # Convert to model input format (BGR, normalized)
            inp = np.expand_dims(np.array(square).astype(np.float32)[:, :, ::-1], 0)

            # Run inference
            probs = sess.run(None, {input_name: inp})[0][0]
            
            # Filter tags by threshold and exclusions
            result_tags = []
            for tag, prob in zip(processed_tags, probs):
                if prob > threshold and tag.lower() not in exclude_list:
                    result_tags.append(tag)

            # Build output string
            output_tags = prepend_tags.strip()
            if output_tags and result_tags:
                output_tags += ", "
            output_tags += ", ".join(result_tags)

            # Save to file
            if folder_path:
                base_name = Path(filename).stem
                txt_path = Path(folder_path) / f"{base_name}.txt"
                try:
                    with open(txt_path, "w", encoding="utf-8") as f:
                        f.write(output_tags)
                    logger.info(f"Saved tags to {txt_path}")
                except Exception as e:
                    logger.error(f"Failed to write {txt_path}: {e}")

            # Update progress (1 step per image)
            batch_progress.update_image_progress(f"Generated {len(result_tags)} tags for '{filename}'")
            batch_progress.next_image()
            return (output_tags,)
            
        except Exception as e:
            logger.error(f"Error in tag_batch for {filename}: {e}")
            return ("",)


NODE_CLASS_MAPPINGS = {
    "BSS_LoadImagesFolder": BSS_LoadImagesFolder,
    "BSS_WD14BatchTagger": BSS_WD14BatchTagger,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BSS_LoadImagesFolder": "BSS Load Images from Folder 📂",
    "BSS_WD14BatchTagger": "BSS WD14 Batch Tagger 🌿",
}
