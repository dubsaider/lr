"""Детектор черных квадратов."""

import cv2
import numpy as np
from typing import List, Tuple, Optional
import math
import numpy.typing as npt
from dataclasses import dataclass


@dataclass
class SquareInfo:
    """Информация о найденном квадрате."""
    contour: npt.NDArray
    area: float
    bbox: Tuple[int, int, int, int]
    center: Tuple[int, int]
    confidence: float


class SquareDetector:
    """Детектор черных квадратов с кэшированием и улучшенными алгоритмами."""
    
    def __init__(self, sensitivity: int = 70, min_area: int = 200, max_area: int = 5000,
                 min_size: int = 15, max_size: int = 100, min_distance: int = 50):
        """
        Args:
            sensitivity: Порог бинаризации (0-255)
            min_area: Минимальная площадь квадрата
            max_area: Максимальная площадь квадрата
            min_size: Минимальный размер стороны квадрата в пикселях
            max_size: Максимальный размер стороны квадрата в пикселях
            min_distance: Минимальное расстояние между квадратами
        """
        self.sensitivity = sensitivity
        self.min_area = min_area
        self.max_area = max_area
        self.min_size = min_size
        self.max_size = max_size
        self.min_distance = min_distance
        
        # Кэш для оптимизации
        self._cache = {}
        self._morph_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    
    def find_black_squares(self, image: npt.NDArray) -> List[npt.NDArray]:
        """Находит черные квадраты на изображении с оптимизацией."""
        # Проверяем кэш
        image_hash = hash(image.tobytes())
        if image_hash in self._cache:
            return self._cache[image_hash]
        
        # Конвертируем в grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Бинаризация с оптимизацией
        _, binary = cv2.threshold(gray, self.sensitivity, 255, cv2.THRESH_BINARY_INV)
        
        # Морфологические операции с предварительно созданным ядром
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, self._morph_kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, self._morph_kernel)
        
        # Находим контуры
        contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        # Быстрая фильтрация по площади
        valid_contours = [c for c in contours if self._quick_area_check(c)]
        
        # Детекция квадратов с оптимизацией
        squares = self._detect_squares_optimized(valid_contours, image)
        
        # Кэшируем результат
        self._cache[image_hash] = squares
        
        return squares
    
    def _quick_area_check(self, contour: npt.NDArray) -> bool:
        """Быстрая проверка площади контура."""
        area = cv2.contourArea(contour)
        return self.min_area < area < self.max_area
    
    def _detect_squares_optimized(self, contours: List[npt.NDArray], 
                                 image: npt.NDArray) -> List[npt.NDArray]:
        """Оптимизированная детекция квадратов."""
        squares = []
        square_infos = []
        
        # Параллельная обработка контуров
        for contour in contours:
            square_info = self._analyze_contour_fast(contour)
            if square_info:
                squares.append(contour)
                square_infos.append(square_info)
        
        # Фильтрация дубликатов с оптимизацией
        filtered_squares = self._remove_duplicates_fast(squares, square_infos)
        
        return filtered_squares
    
    def _analyze_contour_fast(self, contour: npt.NDArray) -> Optional[SquareInfo]:
        """Быстрый анализ контура на предмет квадрата."""
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            return None
        
        # Аппроксимация контура
        epsilon = 0.02 * perimeter
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        # Проверка на квадрат
        if len(approx) != 4 or not cv2.isContourConvex(approx):
            return None
        
        area = cv2.contourArea(contour)
        if not (self.min_area < area < self.max_area):
            return None
        
        # Bounding box
        x, y, w, h = cv2.boundingRect(approx)
        if h == 0:
            return None
        
        # Проверка соотношения сторон
        aspect_ratio = float(w) / h
        if not (0.85 <= aspect_ratio <= 1.15):
            return None
        
        # Проверка плотности заливки
        rect_area = float(w * h)
        if rect_area == 0:
            return None
        fill_ratio = area / rect_area
        if fill_ratio < 0.6:
            return None
        
        # Проверка солидности
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        if hull_area == 0:
            return None
        solidity = area / hull_area
        if solidity < 0.9:
            return None
        
        # Проверка компактности
        compactness = 4 * math.pi * area / (perimeter * perimeter)
        if compactness < 0.5:
            return None
        
        # Проверка размера
        if w < self.min_size or h < self.min_size or w > self.max_size or h > self.max_size:
            return None
        
        center = (x + w // 2, y + h // 2)
        confidence = min(fill_ratio, solidity, compactness)
        
        return SquareInfo(
            contour=contour,
            area=area,
            bbox=(x, y, w, h),
            center=center,
            confidence=confidence
        )
    
    def _remove_duplicates_fast(self, squares: List[npt.NDArray], 
                               square_infos: List[SquareInfo]) -> List[npt.NDArray]:
        """Быстрое удаление дубликатов с использованием пространственного индекса."""
        if len(squares) <= 1:
            return squares
        
        # Создаем пространственный индекс
        spatial_index = {}
        for i, info in enumerate(square_infos):
            x, y = info.center
            key = (x // self.min_distance, y // self.min_distance)
            if key not in spatial_index:
                spatial_index[key] = []
            spatial_index[key].append((i, info))
        
        # Фильтрация дубликатов
        filtered_squares = []
        used_indices = set()
        
        for bucket in spatial_index.values():
            for i, info in bucket:
                if i in used_indices:
                    continue
                
                is_duplicate = False
                for j, other_info in bucket:
                    if i == j or j in used_indices:
                        continue
                    
                    distance = math.sqrt(
                        (info.center[0] - other_info.center[0])**2 +
                        (info.center[1] - other_info.center[1])**2
                    )
                    
                    if distance < self.min_distance:
                        # Выбираем квадрат с большей уверенностью
                        if info.confidence >= other_info.confidence:
                            used_indices.add(j)
                        else:
                            is_duplicate = True
                            break
                
                if not is_duplicate:
                    filtered_squares.append(squares[i])
        
        return filtered_squares
    
    def clear_cache(self):
        """Очищает кэш."""
        self._cache.clear()


# Функция для обратной совместимости
def find_black_squares(image: npt.NDArray, sensitivity: int = 50) -> List[npt.NDArray]:
    """Находит черные квадраты на изображении."""
    detector = SquareDetector(sensitivity=sensitivity)
    return detector.find_black_squares(image)
