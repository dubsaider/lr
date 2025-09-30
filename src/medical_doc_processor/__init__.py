"""Medical Document Processor - автоматическое определение ориентации и извлечение областей из медицинских документов."""

__version__ = "0.1.0"

from .core.image_loader import load_image
from .core.square_detector import find_black_squares
from .core.orientation_detector import detect_orientation_by_lines
from .core.region_extractor import process_medical_test
from .utils.visualization import debug_lines

__all__ = [
    'load_image',
    'find_black_squares', 
    'detect_orientation_by_lines',
    'process_medical_test',
    'debug_lines',
]