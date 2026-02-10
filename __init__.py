# BSS WD14 Batch Tagger for ComfyUI
# Author: Blacksnowskill
# Description: Automatic image tagging using WD14 models with batch processing support

from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

# ComfyUI node mappings
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

# Version info
__version__ = "2.0.0"
__author__ = "Blacksnowskill"
__description__ = "WD14 Batch Tagger v2.0 with batch tools, postprocessing, and analytics"
