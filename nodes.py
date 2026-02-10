import os
import numpy as np
from PIL import Image
from pathlib import Path
import csv
from typing import Tuple, List, Dict, Any
import logging
from huggingface_hub import hf_hub_download
import sys
import json
import torch

# Configure logging FIRST, before any imports that might fail
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import onnxruntime with error handling
try:
    import onnxruntime as ort
    # Verify version compatibility
    try:
        version = ort.__version__
        major, minor = map(int, version.split('.')[:2])
        if major < 1 or (major == 1 and minor < 18):
            logger.warning(f"onnxruntime version {version} may be incompatible. Recommended: >=1.18.0,<2.0.0")
    except (ValueError, AttributeError):
        pass
except ImportError as e:
    error_msg = (
        f"[BSS WD14] ERROR: onnxruntime is not available in Python {sys.version.split()[0]}\n"
        f"Installation path: {sys.executable}\n"
        f"To fix, run:\n"
        f"  {sys.executable} -m pip uninstall onnxruntime onnxruntime-gpu -y\n"
        f"  {sys.executable} -m pip install 'onnxruntime>=1.18.0,<2.0.0'\n"
        f"Original error: {e}"
    )
    logger.error(error_msg)
    raise ImportError(error_msg) from e
except Exception as e:
    error_msg = (
        f"[BSS WD14] ERROR: Failed to import onnxruntime: {e}\n"
        f"Python: {sys.version.split()[0]}\n"
        f"Path: {sys.executable}\n"
        f"Try: {sys.executable} -m pip install --upgrade --force-reinstall 'onnxruntime>=1.18.0,<2.0.0'"
    )
    logger.error(error_msg)
    raise ImportError(error_msg) from e


def update_progress(progress: float, message: str = ""):
    print(f"[BSS WD14] Progress: {int(progress * 100)}% - {message}")


class BatchProgressManager:
    def __init__(self):
        self.pbar = None
        self.current_image = 0
        self.total_images = 0

    def init_progress(self, total_images: int):
        import comfy.utils
        self.total_images = total_images
        self.current_image = 0
        if total_images > 0:
            self.pbar = comfy.utils.ProgressBar(total_images)
        else:
            self.pbar = None

    def update_image_progress(self, message: str = ""):
        if self.pbar:
            self.pbar.update(1)
            if message:
                logger.info(f"Image {self.current_image + 1}/{self.total_images} - {message}")

    def next_image(self):
        self.current_image += 1


batch_progress = BatchProgressManager()

model_cache = {
    'session': None,
    'tags': None,
    'tag_categories': None,
    'model_name': None,
    'input_name': None,
    'input_size': None,
}

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

CATEGORY_DEFAULTS = {
    -1: "general",
    0: "general",
    1: "artist",
    2: "copyright",
    3: "character",
    4: "character",
    5: "meta",
    9: "rating",
}


def ensure_model_available(model_name: str) -> Tuple[bool, str, str]:
    if model_name not in MODEL_CONFIGS:
        logger.error(f"Unknown model: {model_name}")
        return False, "", ""

    model_dir = Path(__file__).parent / "models"
    model_dir.mkdir(exist_ok=True)

    config = MODEL_CONFIGS[model_name]
    model_path = model_dir / f"{model_name}.onnx"
    csv_path = model_dir / f"{model_name}.csv"

    if model_path.exists() and csv_path.exists():
        return True, str(model_path), str(csv_path)

    try:
        update_progress(0, f"Starting download of {model_name}...")

        if not model_path.exists():
            update_progress(0.1, f"Downloading {model_name} model file...")
            hf_hub_download(
                repo_id=config["repo_id"],
                filename=config["filename"],
                local_dir=str(model_dir),
                local_dir_use_symlinks=False,
            )
            downloaded_model = model_dir / config["filename"]
            if downloaded_model.exists() and downloaded_model != model_path:
                downloaded_model.rename(model_path)
            update_progress(0.5, "Model file downloaded successfully!")

        if not csv_path.exists():
            update_progress(0.5, f"Downloading {model_name} tags file...")
            hf_hub_download(
                repo_id=config["repo_id"],
                filename=config["csv_filename"],
                local_dir=str(model_dir),
                local_dir_use_symlinks=False,
            )
            downloaded_csv = model_dir / config["csv_filename"]
            if downloaded_csv.exists() and downloaded_csv != csv_path:
                downloaded_csv.rename(csv_path)
            update_progress(0.9, "Tags file downloaded successfully!")

        update_progress(1.0, f"Download complete! {model_name} ready to use.")
        return True, str(model_path), str(csv_path)
    except Exception as e:
        logger.error(f"Failed to download {model_name}: {e}")
        return False, "", ""


def get_available_models() -> List[str]:
    return list(MODEL_CONFIGS.keys())


def load_model_once(model_name: str, use_gpu: bool) -> bool:
    global model_cache

    if model_cache['model_name'] == model_name and model_cache['session'] is not None:
        return True

    try:
        success, model_path, csv_path = ensure_model_available(model_name)
        if not success:
            return False

        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"] if use_gpu else ["CPUExecutionProvider"]
        try:
            sess = ort.InferenceSession(model_path, providers=providers)
        except Exception as e:
            logger.warning(f"GPU not available, falling back to CPU: {e}")
            sess = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])

        input_name = sess.get_inputs()[0].name
        input_size = int(sess.get_inputs()[0].shape[1])

        tags: List[str] = []
        tag_categories: List[int] = []
        if not Path(csv_path).exists():
            logger.error(f"CSV file not found: {csv_path}")
            return False

            
        tags = []
        tag_categories = []
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if len(row) > 1:
                    tags.append(row[1])
                    try:
                        tag_categories.append(int(row[2]))
                    except (ValueError, IndexError):
                        tag_categories.append(-1)

        
        # Cache the model and tags
        model_cache['session'] = sess
        model_cache['tags'] = tags
        model_cache['tag_categories'] = tag_categories
        model_cache['model_name'] = model_name
        model_cache['input_name'] = input_name
        model_cache['input_size'] = input_size
        return True
    except Exception as e:
        logger.error(f"Error loading model {model_name}: {e}")
        return False


def normalize_image_to_uint8(image: Any) -> np.ndarray:
    if isinstance(image, torch.Tensor):
        image_np = image.detach().cpu().numpy()
    else:
        image_np = np.asarray(image)

    if image_np is None or image_np.size == 0:
        raise ValueError("Empty image")

    if image_np.ndim == 4:
        image_np = image_np[0]

    if image_np.ndim != 3:
        raise ValueError(f"Unsupported image shape: {image_np.shape}")

    if image_np.shape[-1] == 4:
        image_np = image_np[:, :, :3]

    if image_np.dtype != np.uint8:
        image_np = np.clip(image_np, 0.0, 1.0)
        image_np = (image_np * 255.0).astype(np.uint8)

    return image_np


def run_wd14_single(
    image: Any,
    model_name: str,
    threshold_general: float,
    threshold_character: float,
    threshold_meta: float,
    threshold_rating: float,
    replace_underscore: bool,
    exclude_tags: str,
    use_gpu: bool,
) -> Tuple[str, List[str], List[Tuple[str, float, str]]]:
    if not load_model_once(model_name, use_gpu):
        return "", [], []

    sess = model_cache['session']
    tags = model_cache['tags']
    categories = model_cache['tag_categories'] or []
    input_name = model_cache['input_name']
    input_size = model_cache['input_size']

    processed_tags = [t.replace("_", " ") if replace_underscore else t for t in tags]
    exclude_list = [t.strip().lower() for t in exclude_tags.split(",") if t.strip()]

    image_np = normalize_image_to_uint8(image)
    img = Image.fromarray(image_np)
    ratio = input_size / max(img.size)
    new_size = (max(1, int(img.size[0] * ratio)), max(1, int(img.size[1] * ratio)))
    try:
        img = img.resize(new_size, Image.Resampling.LANCZOS)
    except AttributeError:
        img = img.resize(new_size, Image.LANCZOS)

    square = Image.new("RGB", (input_size, input_size), (255, 255, 255))
    square.paste(img, ((input_size - new_size[0]) // 2, (input_size - new_size[1]) // 2))

    inp = np.expand_dims(np.array(square).astype(np.float32)[:, :, ::-1], 0)
    probs = sess.run(None, {input_name: inp})[0][0]

    result_tags: List[str] = []
    debug_scores: List[Tuple[str, float, str]] = []
    for idx, (tag, prob) in enumerate(zip(processed_tags, probs)):
        raw_category = categories[idx] if idx < len(categories) else -1
        category_name = CATEGORY_DEFAULTS.get(raw_category, "general")
        if category_name == "character":
            current_threshold = threshold_character
        elif category_name == "meta":
            current_threshold = threshold_meta
        elif category_name == "rating":
            current_threshold = threshold_rating
        else:
            current_threshold = threshold_general

        if prob > current_threshold and tag.lower() not in exclude_list:
            result_tags.append(tag)
            debug_scores.append((tag, float(prob), category_name))

    return ", ".join(result_tags), result_tags, debug_scores


class BSS_LoadImagesFolder:
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {"required": {"folder_path": ("STRING", {"multiline": False, "default": ""})}}

    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("images", "filenames", "folder_path")
    OUTPUT_IS_LIST = (True, True, False)
    FUNCTION = "load_images"
    CATEGORY = "BSS/Image Processing"

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("inf")

    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        return True

    def load_images(self, folder_path: str) -> Tuple[List[torch.Tensor], List[str], str]:
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

        supported_extensions = (".jpg", ".jpeg", ".png", ".webp")
        folder = Path(folder_path)
        try:
            image_paths = sorted([p for p in folder.iterdir() if p.suffix.lower() in supported_extensions and p.is_file()])
        except Exception as e:
            logger.error(f"Error reading folder {folder_path}: {e}")
            return [], [], folder_path

        images: List[torch.Tensor] = []
        filenames: List[str] = []
        total_images = len(image_paths)
        batch_progress.init_progress(total_images)

        import comfy.utils
        pbar = comfy.utils.ProgressBar(total_images) if total_images > 0 else None

        for i, image_path in enumerate(image_paths):
            if pbar:
                pbar.update(1)
            logger.info(f"Loading images... {i + 1}/{total_images} - {image_path.name}")

            try:
                with Image.open(image_path) as img:
                    arr = np.array(img.convert("RGB"), dtype=np.float32) / 255.0
                    if arr.size == 0 or arr.shape[0] == 0 or arr.shape[1] == 0:
                        continue
                    images.append(torch.from_numpy(arr))
                    filenames.append(image_path.name)
            except Exception as e:
                logger.error(f"Error loading {image_path.name}: {e}")

        return images, filenames, folder_path


class BSS_WD14BatchTagger:
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "image": ("IMAGE",),
                "filename": ("STRING",),
                "folder_path": ("STRING", {"default": ""}),
                "model": (cls._get_model_choices(), {"default": "wd-vit-tagger-v3"}),
                "general_threshold": ("FLOAT", {"default": 0.35, "min": 0.0, "max": 1.0, "step": 0.01}),
                "character_threshold": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.01}),
                "meta_threshold": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "rating_threshold": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "replace_underscore": ("BOOLEAN", {"default": True}),
                "use_gpu": ("BOOLEAN", {"default": False}),
                "prepend_tags": ("STRING", {"multiline": True, "default": ""}),
                "exclude_tags": ("STRING", {"multiline": True, "default": ""}),
            }
        }

    @classmethod
    def _get_model_choices(cls) -> List[str]:
        model_dir = Path(__file__).parent / "models"
        local_models = set()
        if model_dir.exists():
            for model_name in MODEL_CONFIGS.keys():
                if (model_dir / f"{model_name}.onnx").exists() and (model_dir / f"{model_name}.csv").exists():
                    local_models.add(model_name)

        choices = []
        for model_name in get_available_models():
            status = "✅" if model_name in local_models else "⬇️"
            display_name = f"{status} {MODEL_CONFIGS[model_name]['display_name']} ({model_name})"
            choices.append(f"{model_name}|{display_name}")
        return choices

    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        model = kwargs.get("model", "")
        if not model:
            return True
        model_name = model.split("|")[0] if "|" in model else model
        if model_name not in MODEL_CONFIGS:
            return f"Unknown model: {model_name}"
        return True

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        model_dir = Path(__file__).parent / "models"
        if not model_dir.exists():
            return float("inf")
        try:
            return model_dir.stat().st_mtime
        except Exception:
            return float("inf")

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("tags",)
    OUTPUT_IS_LIST = (False,)
    FUNCTION = "tag_batch"
    OUTPUT_NODE = True
    CATEGORY = "BSS/Image Processing"

    def tag_batch(
        self,
        image: Any,
        filename: str,
        folder_path: str,
        model: str,
        general_threshold: float,
        character_threshold: float,
        meta_threshold: float,
        rating_threshold: float,
        replace_underscore: bool,
        use_gpu: bool,
        prepend_tags: str,
        exclude_tags: str,
    ) -> Tuple[str]:
        try:
            model_name = model.split("|")[0] if "|" in model else model
            _, result_tags, _ = run_wd14_single(
                image,
                model_name,
                general_threshold,
                character_threshold,
                meta_threshold,
                rating_threshold,
                replace_underscore,
                exclude_tags,
                use_gpu,
            )

    def tag_batch(self, image: Any, filename: str, folder_path: str, model: str, 
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
            tag_categories = model_cache.get('tag_categories', [])
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
            if isinstance(image, torch.Tensor):
                image_np = image.detach().cpu().numpy()
            else:
                image_np = np.asarray(image)

            if image_np is None or image_np.size == 0:
                logger.warning(f"Empty image array for {filename}, skipping")
                return ("",)

            if image_np.ndim == 4:
                image_np = image_np[0]

            if image_np.shape[-1] == 4:
                image_np = image_np[:, :, :3]

            if image_np.dtype != np.uint8:
                image_np = np.clip(image_np, 0.0, 1.0)
                image_np = (image_np * 255.0).astype(np.uint8)

            img = Image.fromarray(image_np)
            ratio = input_size / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            
            if new_size[0] <= 0 or new_size[1] <= 0:
                logger.error(f"Invalid resize dimensions {new_size} for {filename}")
                return ("",)

            # Resize and center image
            try:
                # Use new Pillow API if available
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            except AttributeError:
                # Fallback for older Pillow versions
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
            for idx, (tag, prob) in enumerate(zip(processed_tags, probs)):
                current_threshold = character_threshold if idx < len(tag_categories) and tag_categories[idx] == 4 else threshold
                if prob > current_threshold and tag.lower() not in exclude_list:
                    result_tags.append(tag)

            # Build output string
            output_tags = prepend_tags.strip()
            if output_tags and result_tags:
                output_tags += ", "
            output_tags += ", ".join(result_tags)

            if folder_path:
                txt_path = Path(folder_path) / f"{Path(filename).stem}.txt"
                try:
                    with open(txt_path, "w", encoding="utf-8") as f:
                        f.write(output_tags)
                except Exception as e:
                    logger.error(f"Failed to write {txt_path}: {e}")

            batch_progress.update_image_progress(f"Generated {len(result_tags)} tags for '{filename}'")
            batch_progress.next_image()
            return (output_tags,)
        except Exception as e:
            logger.error(f"Error in tag_batch for {filename}: {e}")
            return ("",)


class BSS_WD14TaggerBatch:
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "images": ("IMAGE",),
                "filenames": ("STRING",),
                "folder_path": ("STRING", {"default": ""}),
                "model": (BSS_WD14BatchTagger._get_model_choices(), {"default": "wd-vit-tagger-v3"}),
                "general_threshold": ("FLOAT", {"default": 0.35, "min": 0.0, "max": 1.0, "step": 0.01}),
                "character_threshold": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.01}),
                "meta_threshold": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "rating_threshold": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "replace_underscore": ("BOOLEAN", {"default": True}),
                "use_gpu": ("BOOLEAN", {"default": False}),
                "prepend_tags": ("STRING", {"multiline": True, "default": ""}),
                "exclude_tags": ("STRING", {"multiline": True, "default": ""}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("tags", "tags_json")
    OUTPUT_IS_LIST = (True, False)
    FUNCTION = "tag_images"
    CATEGORY = "BSS/Image Processing"

    def tag_images(self, images, filenames, folder_path, model, general_threshold, character_threshold, meta_threshold,
                   rating_threshold, replace_underscore, use_gpu, prepend_tags, exclude_tags):
        model_name = model.split("|")[0] if "|" in model else model
        image_list = list(images) if isinstance(images, (list, tuple)) else [images]
        filename_list = list(filenames) if isinstance(filenames, (list, tuple)) else [filenames]

        if len(filename_list) < len(image_list):
            filename_list += [f"image_{i:05d}.png" for i in range(len(filename_list), len(image_list))]

        tags_list: List[str] = []
        payload: Dict[str, Any] = {}

        for image, name in zip(image_list, filename_list):
            _, result_tags, scored_tags = run_wd14_single(
                image,
                model_name,
                general_threshold,
                character_threshold,
                meta_threshold,
                rating_threshold,
                replace_underscore,
                exclude_tags,
                use_gpu,
            )
            output_tags = prepend_tags.strip()
            if output_tags and result_tags:
                output_tags += ", "
            output_tags += ", ".join(result_tags)
            tags_list.append(output_tags)
            payload[name] = [{"tag": t, "score": s, "category": c} for t, s, c in scored_tags]

            if folder_path:
                txt_path = Path(folder_path) / f"{Path(name).stem}.txt"
                try:
                    with open(txt_path, "w", encoding="utf-8") as f:
                        f.write(output_tags)
                except Exception as e:
                    logger.error(f"Failed to write {txt_path}: {e}")

        return tags_list, json.dumps(payload, ensure_ascii=False)


class BSS_TagsPostprocess:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "tags": ("STRING", {"multiline": True, "default": ""}),
                "sort_alphabetically": ("BOOLEAN", {"default": False}),
                "unique_only": ("BOOLEAN", {"default": True}),
                "replace_underscore": ("BOOLEAN", {"default": True}),
                "append_tags": ("STRING", {"multiline": True, "default": ""}),
                "prepend_tags": ("STRING", {"multiline": True, "default": ""}),
                "exclude_tags": ("STRING", {"multiline": True, "default": ""}),
            }
        }

    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("tags", "tag_count")
    FUNCTION = "process"
    CATEGORY = "BSS/Image Processing"

    def process(self, tags, sort_alphabetically, unique_only, replace_underscore, append_tags, prepend_tags, exclude_tags):
        source = [t.strip() for t in tags.split(",") if t.strip()]
        if prepend_tags.strip():
            source = [t.strip() for t in prepend_tags.split(",") if t.strip()] + source
        if append_tags.strip():
            source += [t.strip() for t in append_tags.split(",") if t.strip()]

        if replace_underscore:
            source = [t.replace("_", " ") for t in source]

        excluded = {t.strip().lower() for t in exclude_tags.split(",") if t.strip()}
        source = [t for t in source if t.lower() not in excluded]

        if unique_only:
            seen = set()
            out = []
            for t in source:
                key = t.lower()
                if key not in seen:
                    seen.add(key)
                    out.append(t)
            source = out

        if sort_alphabetically:
            source = sorted(source, key=lambda x: x.lower())

        return ", ".join(source), len(source)


class BSS_SaveCaptions:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "tags": ("STRING",),
                "filename": ("STRING",),
                "output_folder": ("STRING", {"default": ""}),
                "format": (["txt", "json", "csv"], {"default": "txt"}),
                "overwrite": ("BOOLEAN", {"default": True}),
                "suffix": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING", "BOOLEAN")
    RETURN_NAMES = ("saved_path", "saved")
    FUNCTION = "save"
    CATEGORY = "BSS/Image Processing"

    def save(self, tags, filename, output_folder, format, overwrite, suffix):
        if not output_folder:
            return "", False
        out_dir = Path(output_folder)
        out_dir.mkdir(parents=True, exist_ok=True)
        stem = Path(filename).stem
        base = f"{stem}{suffix}" if suffix else stem
        out_path = out_dir / f"{base}.{format}"

        if out_path.exists() and not overwrite:
            return str(out_path), False

        try:
            if format == "txt":
                out_path.write_text(tags, encoding="utf-8")
            elif format == "json":
                out_path.write_text(json.dumps({"filename": filename, "tags": tags}, ensure_ascii=False, indent=2), encoding="utf-8")
            else:
                with open(out_path, "w", encoding="utf-8", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["filename", "tags"])
                    writer.writerow([filename, tags])
            return str(out_path), True
        except Exception as e:
            logger.error(f"Failed to save captions: {e}")
            return "", False


class BSS_TagAnalytics:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "tags_list": ("STRING",),
                "top_k": ("INT", {"default": 20, "min": 1, "max": 200, "step": 1}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("top_tags", "full_stats_json")
    FUNCTION = "analyze"
    OUTPUT_NODE = True
    CATEGORY = "BSS/Image Processing"

    def analyze(self, tags_list, top_k):
        values = list(tags_list) if isinstance(tags_list, (list, tuple)) else [tags_list]
        counts: Dict[str, int] = {}
        total_items = 0
        for text in values:
            for tag in [t.strip() for t in str(text).split(",") if t.strip()]:
                counts[tag] = counts.get(tag, 0) + 1
                total_items += 1

        sorted_tags = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
        top = sorted_tags[:top_k]
        top_line = ", ".join([f"{tag}:{count}" for tag, count in top])

        payload = {
            "total_tags": total_items,
            "unique_tags": len(counts),
            "top": [{"tag": tag, "count": count} for tag, count in top],
        }
        return top_line, json.dumps(payload, ensure_ascii=False, indent=2)


NODE_CLASS_MAPPINGS = {
    "BSS_LoadImagesFolder": BSS_LoadImagesFolder,
    "BSS_WD14BatchTagger": BSS_WD14BatchTagger,
    "BSS_WD14TaggerBatch": BSS_WD14TaggerBatch,
    "BSS_TagsPostprocess": BSS_TagsPostprocess,
    "BSS_SaveCaptions": BSS_SaveCaptions,
    "BSS_TagAnalytics": BSS_TagAnalytics,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BSS_LoadImagesFolder": "BSS Load Images from Folder 📂",
    "BSS_WD14BatchTagger": "BSS WD14 Batch Tagger 🌿",
    "BSS_WD14TaggerBatch": "BSS WD14 Tagger Batch ⚡",
    "BSS_TagsPostprocess": "BSS Tags Postprocess 🧹",
    "BSS_SaveCaptions": "BSS Save Captions 💾",
    "BSS_TagAnalytics": "BSS Tag Analytics 📊",
}
