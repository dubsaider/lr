"""Извлекатель областей с улучшенной производительностью."""

import os
import cv2
import numpy as np
from typing import List, Optional, Tuple, Dict
import numpy.typing as npt
from concurrent.futures import ThreadPoolExecutor
import time

from .image_loader import ImageLoader
from .square_detector import SquareDetector
from .orientation_detector import OrientationDetector


class RegionExtractor:
    """Извлекатель областей L и R из медицинских документов."""
    
    def __init__(self, output_dir: str = "output", template_alpha: float = 0.4,
                 max_workers: int = 2):
        """
        Args:
            output_dir: Директория для сохранения результатов
            template_alpha: Прозрачность эталонной спирали
            max_workers: Максимальное количество потоков для параллельной обработки
        """
        self.output_dir = output_dir
        self.template_alpha = template_alpha
        self.max_workers = max_workers
        
        # Инициализируем компоненты
        self.image_loader = ImageLoader()
        self.square_detector = SquareDetector()
        self.orientation_detector = OrientationDetector()
        
        # Кэш для оптимизации
        self._processing_cache = {}
    
    def process_medical_test(self, input_path: str) -> Tuple[Optional[int], Dict]:
        """Обрабатывает медицинский документ с оптимизацией."""
        start_time = time.time()
        
        os.makedirs(self.output_dir, exist_ok=True)
        file_name = os.path.splitext(os.path.basename(input_path))[0]
        
        print(f"Обработка файла: {input_path}")
        
        # Загружаем изображение
        original_image = self.image_loader.load_image(input_path)
        print(f"Исходный размер изображения: {original_image.shape}")
        
        # Определяем ориентацию с оптимизацией
        squares = self.square_detector.find_black_squares(original_image)
        print(f"Найдено квадратов: {len(squares)}")
        
        rotation_angle = self.orientation_detector.detect_orientation_by_lines(
            squares, original_image.shape
        )
        print(f"Определен угол поворота: {rotation_angle}°")
        
        # Поворачиваем изображение
        rotated_image = self._rotate_image_optimized(original_image, rotation_angle)
        
        # Извлекаем области с оптимизацией
        results = self._extract_regions_optimized(rotated_image, file_name)
        
        # Сохраняем результаты параллельно
        self._save_results_parallel(rotated_image, results, file_name)
        
        processing_time = time.time() - start_time
        print(f"Обработка завершена за {processing_time:.2f} секунд!")
        
        return rotation_angle, results
    
    def _rotate_image_optimized(self, image: npt.NDArray, angle: int) -> npt.NDArray:
        """Оптимизированный поворот изображения."""
        if angle == 0:
            return image
        
        # Используем оптимизированные функции OpenCV
        if angle == 90:
            return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180:
            return cv2.rotate(image, cv2.ROTATE_180)
        elif angle == 270:
            return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        else:
            # Для произвольных углов используем матрицу поворота
            height, width = image.shape[:2]
            center = (width // 2, height // 2)
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            return cv2.warpAffine(image, rotation_matrix, (width, height))
    
    def _apply_template_transparency_optimized(self, region: np.ndarray, 
                                             alpha: float = 0.2) -> np.ndarray:
        """Оптимизированное применение прозрачности к эталонной спирали."""
        if len(region.shape) == 3:
            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        else:
            gray = region
        
        # Используем более эффективную бинаризацию
        _, light_mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        
        # Применяем прозрачность векторизованно
        result = region.copy()
        if len(result.shape) == 3:
            result[light_mask > 0] = result[light_mask > 0] * alpha + 255 * (1 - alpha)
        else:
            result[light_mask > 0] = result[light_mask > 0] * alpha + 255 * (1 - alpha)
        
        return result
    
    def _extract_regions_optimized(self, image: npt.NDArray, file_name: str) -> Dict:
        """Оптимизированное извлечение L и R областей."""
        squares = self.square_detector.find_black_squares(image)
        print(f"Найдено квадратов после поворота: {len(squares)}")
        
        l_squares, r_squares = self._group_squares_by_position_optimized(
            squares, image.shape[1]
        )
        print(f"L квадратов: {len(l_squares)}, R квадратов: {len(r_squares)}")
        
        results = {'L_region': None, 'R_region': None, 'L_bbox': None, 'R_bbox': None}
        
        # Параллельная обработка L и R областей
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            if len(l_squares) >= 3:
                futures.append(executor.submit(
                    self._process_region, l_squares, image, file_name, 'L'
                ))
            
            if len(r_squares) >= 3:
                futures.append(executor.submit(
                    self._process_region, r_squares, image, file_name, 'R'
                ))
            
            # Собираем результаты
            for future in futures:
                region_type, region_data, bbox = future.result()
                results[f'{region_type}_region'] = region_data
                results[f'{region_type}_bbox'] = bbox
        
        return results
    
    def _process_region(self, squares: List[npt.NDArray], image: npt.NDArray,
                       file_name: str, region_type: str) -> Tuple[str, np.ndarray, Tuple]:
        """Обрабатывает одну область (L или R)."""
        bbox = self._create_region_from_points_optimized(squares)
        if not bbox:
            return region_type, None, None
        
        x_min, y_min, x_max, y_max = bbox
        region = image[y_min:y_max, x_min:x_max]
        
        # Применяем прозрачность к эталонной спирали
        region = self._apply_template_transparency_optimized(
            region, alpha=self.template_alpha
        )
        
        # Сохраняем область
        output_path = os.path.join(
            self.output_dir, f'{file_name}_{region_type}_region.jpg'
        )
        cv2.imwrite(output_path, region)
        
        print(f"{region_type} область сохранена с прозрачностью: {bbox}")
        
        return region_type, region, bbox
    
    def _group_squares_by_position_optimized(self, squares: List[npt.NDArray],
                                            image_width: int) -> Tuple[List, List]:
        """Оптимизированная группировка квадратов по позиции."""
        l_squares, r_squares = [], []
        mid_x = image_width // 2
        
        # Векторизованная обработка центров
        centers = []
        for square in squares:
            M = cv2.moments(square)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                centers.append((cx, cy, square))
        
        # Группировка
        for cx, cy, square in centers:
            if cx < mid_x:
                l_squares.append(square)
            else:
                r_squares.append(square)
        
        return l_squares, r_squares
    
    def _create_region_from_points_optimized(self, squares: List[npt.NDArray],
                                           padding: int = 10) -> Optional[Tuple[int, int, int, int]]:
        """Оптимизированное создание ограничивающей рамки."""
        if len(squares) < 3:
            return None
        
        # Обрабатываем только первые 3 квадрата для оптимизации
        points = []
        for square in squares[:3]:
            M = cv2.moments(square)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                points.append((cx, cy))
        
        if len(points) < 3:
            return None
        
        # Векторизованное вычисление границ
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        
        # Добавляем отступы с проверкой границ
        x_min = max(0, x_min - padding)
        y_min = max(0, y_min - padding)
        x_max = min(10000, x_max + padding)
        y_max = min(10000, y_max + padding)
        
        return (x_min, y_min, x_max, y_max)
    
    def _save_results_parallel(self, image: npt.NDArray, results: Dict, file_name: str):
        """Параллельное сохранение результатов."""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            # Сохранение результата с красными рамками
            futures.append(executor.submit(
                self._save_result_with_boxes, image, results, file_name
            ))
            
            # Сохранение повернутого документа
            futures.append(executor.submit(
                self._save_rotated_document, image, file_name
            ))
            
            # Ждем завершения всех задач
            for future in futures:
                future.result()
    
    def _save_result_with_boxes(self, image: npt.NDArray, results: Dict, file_name: str):
        """Сохраняет результат с красными рамками."""
        result_image = image.copy()
        
        # Рисуем bounding boxes
        if results['L_bbox']:
            bbox = results['L_bbox']
            cv2.rectangle(result_image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 0, 255), 3)
        
        if results['R_bbox']:
            bbox = results['R_bbox']
            cv2.rectangle(result_image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 0, 255), 3)
        
        output_path = os.path.join(
            self.output_dir, f'{file_name}_result_with_red_squares.jpg'
        )
        cv2.imwrite(output_path, result_image)
    
    def _save_rotated_document(self, image: npt.NDArray, file_name: str):
        """Сохраняет повернутый документ."""
        output_path = os.path.join(
            self.output_dir, f'{file_name}_rotated_document.jpg'
        )
        cv2.imwrite(output_path, image)
    
    def clear_cache(self):
        """Очищает кэш."""
        self.square_detector.clear_cache()
        self._processing_cache.clear()


# Функция для обратной совместимости
def process_medical_test(input_path: str, output_dir: str = "output") -> int:
    """Обрабатывает медицинский документ."""
    extractor = RegionExtractor(output_dir)
    rotation_angle, _ = extractor.process_medical_test(input_path)
    return rotation_angle
