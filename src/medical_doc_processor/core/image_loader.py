import os
import cv2
import numpy as np
from PIL import Image, UnidentifiedImageError
import io
from typing import Union, Tuple

try:
    import fitz  # PyMuPDF
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False


class ImageLoader:
    """Загрузчик изображений из различных форматов."""
    
    SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
    SUPPORTED_PDF_FORMATS = {'.pdf'}
    
    @classmethod
    def load_image(cls, input_path: str) -> np.ndarray:
        """Загружает изображение из различных форматов.
        
        Args:
            input_path: Путь к файлу (PDF или изображение)
            
        Returns:
            numpy.ndarray: Загруженное изображение в формате BGR
            
        Raises:
            FileNotFoundError: Если файл не существует
            ValueError: Если формат не поддерживается или файл поврежден
            ImportError: Если требуется PDF но PyMuPDF не установлен
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Файл не найден: {input_path}")
        
        file_ext = os.path.splitext(input_path)[1].lower()
        
        if file_ext in cls.SUPPORTED_PDF_FORMATS:
            return cls._load_pdf(input_path)
        elif file_ext in cls.SUPPORTED_IMAGE_FORMATS:
            return cls._load_image_file(input_path)
        else:
            raise ValueError(f"Неподдерживаемый формат файла: {file_ext}")
    
    @classmethod
    def _load_pdf(cls, pdf_path: str) -> np.ndarray:
        """Загружает первую страницу PDF как изображение."""
        if not PDF_SUPPORT:
            raise ImportError(
                "Для работы с PDF установите PyMuPDF: pip install PyMuPDF"
            )
        
        try:
            doc = fitz.open(pdf_path)
            page = doc[0]
            mat = fitz.Matrix(2, 2)  # Увеличиваем DPI для качества
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("ppm")
            img = Image.open(io.BytesIO(img_data))
            img_array = np.array(img)
            doc.close()
            
            # Конвертируем в формат, совместимый с OpenCV (BGR)
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            return img_array
        except Exception as e:
            raise ValueError(f"Ошибка загрузки PDF: {e}")
    
    @classmethod
    def _load_image_file(cls, image_path: str) -> np.ndarray:
        """Загружает изображение из файла."""
        # Пробуем загрузить через OpenCV
        image = cv2.imread(image_path)
        if image is not None:
            return image
        
        # Если OpenCV не смог, пробуем через PIL
        try:
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img_array = np.array(img)
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            return img_array
        except UnidentifiedImageError:
            raise ValueError(f"Не удалось идентифицировать изображение: {image_path}")
        except Exception as e:
            raise ValueError(f"Ошибка загрузки изображения: {e}")
    
    @classmethod
    def get_supported_formats(cls) -> dict:
        """Возвращает поддерживаемые форматы файлов."""
        return {
            'images': list(cls.SUPPORTED_IMAGE_FORMATS),
            'pdf': list(cls.SUPPORTED_PDF_FORMATS) if PDF_SUPPORT else []
        }


# Алиас для обратной совместимости
load_image = ImageLoader.load_image