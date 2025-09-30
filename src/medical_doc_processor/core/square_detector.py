import cv2
import numpy as np
from typing import List, Tuple
import math
import numpy.typing as npt


class SquareDetector:
    """Детектор черных квадратов на изображениях."""
    
    def __init__(self, sensitivity: int = 30, min_area: int = 50, max_area: int = 5000):
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
        
        # Находим все контуры, включая вложенные (маркеры могут быть внутри рамки)
        contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        squares = []
        for contour in contours:
            if self._is_square(contour):
                squares.append(contour)
        
        return squares
    
    def _is_square(self, contour: npt.NDArray) -> bool:
        """Проверяет, является ли контур квадратом (насыщенный, выпуклый, почти 1:1)."""
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            return False

        # Аппроксимируем контур
        epsilon = 0.02 * perimeter
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # Должно быть 4 вершины и контур выпуклый
        if len(approx) != 4 or not cv2.isContourConvex(approx):
            return False

        area = cv2.contourArea(contour)
        if not (self.min_area < area < self.max_area):
            return False

        # Соотношение сторон bounding box — близко к квадрату
        x, y, w, h = cv2.boundingRect(approx)
        if h == 0:
            return False
        aspect_ratio = float(w) / h
        if not (0.85 <= aspect_ratio <= 1.15):
            return False

        # Плотность заливки: площадь контура к площади прямоугольника
        rect_area = float(w * h)
        if rect_area == 0:
            return False
        fill_ratio = area / rect_area
        if fill_ratio < 0.6:
            # Отсекаем тонкие/рамочные компоненты и пересечения линий спирали
            return False

        # Солидность к выпуклой оболочке — убираем сильно зубчатые формы
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        if hull_area == 0:
            return False
        solidity = area / hull_area
        if solidity < 0.9:
            return False

        # Отношение площади к квадрату периметра — фильтр «тонких» фигур
        compactness = 4 * math.pi * area / (perimeter * perimeter)
        if compactness < 0.5:
            return False

        return True


# Функция для обратной совместимости
def find_black_squares(image: npt.NDArray, sensitivity: int = 50) -> List[npt.NDArray]:
    """Находит черные квадраты на изображении."""
    detector = SquareDetector(sensitivity=sensitivity)
    return detector.find_black_squares(image)