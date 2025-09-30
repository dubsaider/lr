import cv2
import numpy as np
from typing import List, Tuple
import numpy.typing as npt


class SquareDetector:
    """Детектор черных квадратов на изображениях."""
    
    def __init__(self, sensitivity: int = 50, min_area: int = 50, max_area: int = 5000):
        """
        Args:
            sensitivity: Порог бинаризации (0-255)
            min_area: Минимальная площадь квадрата
            max_area: Максимальная площадь квадрата
        """
        self.sensitivity = sensitivity
        self.min_area = min_area
        self.max_area = max_area
    
    def find_black_squares(self, image: npt.NDArray) -> List[npt.NDArray]:
        """Находит черные квадраты на изображении.
        
        Args:
            image: Входное изображение в формате BGR
            
        Returns:
            List[npt.NDArray]: Список контуров квадратов
        """
        # Конвертируем в grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Бинаризация для выделения черных объектов
        _, binary = cv2.threshold(gray, self.sensitivity, 255, cv2.THRESH_BINARY_INV)
        
        # Морфологические операции для улучшения качества
        kernel = np.ones((3, 3), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        # Находим контуры
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        squares = []
        for contour in contours:
            if self._is_square(contour):
                squares.append(contour)
        
        return squares
    
    def _is_square(self, contour: npt.NDArray) -> bool:
        """Проверяет, является ли контур квадратом."""
        # Аппроксимируем контур
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        # Проверяем что это квадрат (4 угла)
        if len(approx) != 4:
            return False
        
        area = cv2.contourArea(contour)
        if not (self.min_area < area < self.max_area):
            return False
        
        # Проверяем что форма близка к квадрату
        x, y, w, h = cv2.boundingRect(approx)
        aspect_ratio = float(w) / h
        
        return 0.7 <= aspect_ratio <= 1.3


# Функция для обратной совместимости
def find_black_squares(image: npt.NDArray, sensitivity: int = 50) -> List[npt.NDArray]:
    """Находит черные квадраты на изображении."""
    detector = SquareDetector(sensitivity=sensitivity)
    return detector.find_black_squares(image)