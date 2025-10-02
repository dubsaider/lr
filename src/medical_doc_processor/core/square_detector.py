import cv2
import numpy as np
from typing import List, Tuple
import math
import numpy.typing as npt


class SquareDetector:
    """Детектор черных квадратов на изображениях."""
    
    def __init__(self, sensitivity: int = 70, min_area: int = 200, max_area: int = 5000, 
                 min_size: int = 15, max_size: int = 100, min_distance: int = 50):
        """
        Args:
            sensitivity: Порог бинаризации (0-255). По умолчанию 70 для надежной детекции всех маркеров
            min_area: Минимальная площадь квадрата
            max_area: Максимальная площадь квадрата
            min_size: Минимальный размер стороны квадрата в пикселях
            max_size: Максимальный размер стороны квадрата в пикселях
            min_distance: Минимальное расстояние между квадратами для фильтрации дубликатов
        """
        self.sensitivity = sensitivity
        self.min_area = min_area
        self.max_area = max_area
        self.min_size = min_size
        self.max_size = max_size
        self.min_distance = min_distance
    
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
        
        # Предварительная фильтрация по площади для быстрого отсеивания
        contours = [c for c in contours if self._quick_area_check(c)]
        
        # Объединенная проверка квадратов и фильтрация
        squares = self._find_and_filter_squares(contours, image)
        
        return squares
    
    def _quick_area_check(self, contour: npt.NDArray) -> bool:
        """Быстрая проверка площади контура для предварительной фильтрации."""
        area = cv2.contourArea(contour)
        return self.min_area < area < self.max_area
    
    def _find_and_filter_squares(self, contours: List[npt.NDArray], image: npt.NDArray) -> List[npt.NDArray]:
        """Объединенная проверка квадратов и фильтрация для оптимизации."""
        squares = []
        square_data = []  # Кэшированные данные для каждого квадрата
        
        for contour in contours:
            # Проверяем, является ли контур квадратом
            square_info = self._is_square_optimized(contour)
            if square_info:
                squares.append(contour)
                square_data.append(square_info)
        
        # Применяем дополнительные фильтры
        filtered_squares = self._apply_additional_filters(squares, square_data, image)
        
        return filtered_squares
    
    def _is_square_optimized(self, contour: npt.NDArray) -> dict:
        """Оптимизированная проверка квадрата с кэшированием вычислений."""
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            return None

        # Аппроксимируем контур
        epsilon = 0.02 * perimeter
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # Должно быть 4 вершины и контур выпуклый
        if len(approx) != 4 or not cv2.isContourConvex(approx):
            return None

        area = cv2.contourArea(contour)
        if not (self.min_area < area < self.max_area):
            return None

        # Соотношение сторон bounding box — близко к квадрату
        x, y, w, h = cv2.boundingRect(approx)
        if h == 0:
            return None
        aspect_ratio = float(w) / h
        if not (0.85 <= aspect_ratio <= 1.15):
            return None

        # Плотность заливки: площадь контура к площади прямоугольника
        rect_area = float(w * h)
        if rect_area == 0:
            return None
        fill_ratio = area / rect_area
        if fill_ratio < 0.6:
            return None

        # Солидность к выпуклой оболочке — убираем сильно зубчатые формы
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        if hull_area == 0:
            return None
        solidity = area / hull_area
        if solidity < 0.9:
            return None

        # Отношение площади к квадрату периметра — фильтр «тонких» фигур
        compactness = 4 * math.pi * area / (perimeter * perimeter)
        if compactness < 0.5:
            return None

        # Возвращаем кэшированные данные
        return {
            'area': area,
            'bbox': (x, y, w, h),
            'center': (x + w//2, y + h//2)
        }
    
    def _apply_additional_filters(self, squares: List[npt.NDArray], square_data: List[dict], 
                                image: npt.NDArray) -> List[npt.NDArray]:
        """Применяет дополнительные фильтры к квадратам."""
        if not squares:
            return squares
        
        filtered_squares = []
        filtered_data = []
        
        for square, data in zip(squares, square_data):
            x, y, w, h = data['bbox']
            
            # Фильтр по размеру стороны
            if w < self.min_size or h < self.min_size or w > self.max_size or h > self.max_size:
                continue
            
            # Проверяем плотность черных пикселей внутри квадрата
            if not self._check_black_density_fast(square, image, data['bbox']):
                continue
            
            # Проверяем, что квадрат не слишком близко к краям изображения
            margin = 20
            if (x < margin or y < margin or 
                x + w > image.shape[1] - margin or y + h > image.shape[0] - margin):
                continue
            
            filtered_squares.append(square)
            filtered_data.append(data)
        
        # Оптимизированная фильтрация дубликатов
        filtered_squares = self._remove_duplicates_optimized(filtered_squares, filtered_data)
        
        return filtered_squares
    
    def _check_black_density_fast(self, square: npt.NDArray, image: npt.NDArray, bbox: Tuple[int, int, int, int]) -> bool:
        """Оптимизированная проверка плотности черных пикселей."""
        x, y, w, h = bbox
        
        # Вырезаем область квадрата
        roi = image[y:y+h, x:x+w]
        if roi.size == 0:
            return False
        
        # Конвертируем в grayscale
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # Считаем черные пиксели (темнее порога)
        black_pixels = np.sum(gray_roi < self.sensitivity)
        total_pixels = gray_roi.size
        
        # Плотность черных пикселей должна быть не менее 30%
        black_density = black_pixels / total_pixels
        return black_density >= 0.3
    
    def _remove_duplicates_optimized(self, squares: List[npt.NDArray], square_data: List[dict]) -> List[npt.NDArray]:
        """Оптимизированное удаление дубликатов O(n log n)."""
        if len(squares) <= 1:
            return squares
        
        # Создаем список с индексами и центрами для сортировки
        indexed_centers = [(i, data['center'], data['area']) for i, data in enumerate(square_data)]
        
        # Сортируем по x-координате для оптимизации
        indexed_centers.sort(key=lambda x: x[1][0])
        
        filtered_squares = []
        used_indices = set()
        
        for i, (cx1, cy1), area1 in indexed_centers:
            if i in used_indices:
                continue
                
            is_duplicate = False
            
            # Проверяем только близкие по x координате квадраты
            for j, (cx2, cy2), area2 in indexed_centers:
                if i == j or j in used_indices:
                    continue
                
                # Если x координаты слишком далеко, пропускаем остальные
                if abs(cx1 - cx2) > self.min_distance:
                    break
                
                distance = math.sqrt((cx1 - cx2)**2 + (cy1 - cy2)**2)
                if distance < self.min_distance:
                    # Выбираем квадрат с большей площадью
                    if area1 >= area2:
                        used_indices.add(j)
                    else:
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                filtered_squares.append(squares[i])
        
        return filtered_squares
    


# Функция для обратной совместимости
def find_black_squares(image: npt.NDArray, sensitivity: int = 50) -> List[npt.NDArray]:
    """Находит черные квадраты на изображении."""
    detector = SquareDetector(sensitivity=sensitivity)
    return detector.find_black_squares(image)