import os
import cv2
import numpy as np
from typing import List, Optional, Tuple
import numpy.typing as npt

from .image_loader import ImageLoader
from .square_detector import SquareDetector
from .orientation_detector import OrientationDetector


class RegionExtractor:
    """Извлекает области L и R из медицинских документов."""
    
    def __init__(self, output_dir: str = "output", template_alpha: float = 0.4):
        self.output_dir = output_dir
        self.template_alpha = template_alpha
        self.image_loader = ImageLoader()
        self.square_detector = SquareDetector()
        self.orientation_detector = OrientationDetector()
    
    def process_medical_test(self, input_path: str) -> Tuple[Optional[int], dict]:
        """Обрабатывает медицинский документ.
        
        Args:
            input_path: Путь к входному файлу
            
        Returns:
            Tuple: (угол_поворота, результаты_обработки)
        """
        os.makedirs(self.output_dir, exist_ok=True)
        file_name = os.path.splitext(os.path.basename(input_path))[0]
        
        print(f"Обработка файла: {input_path}")
        
        # Загружаем изображение
        original_image = self.image_loader.load_image(input_path)
        print(f"Исходный размер изображения: {original_image.shape}")
        
        # Определяем ориентацию
        squares = self.square_detector.find_black_squares(original_image)
        print(f"Найдено квадратов: {len(squares)}")
        
        rotation_angle = self.orientation_detector.detect_orientation_by_lines(
            squares, original_image.shape
        )
        print(f"Определен угол поворота: {rotation_angle}°")
        
        # Поворачиваем изображение
        rotated_image = self._rotate_image(original_image, rotation_angle)
        
        # Извлекаем области
        results = self._extract_regions(rotated_image, file_name)
        
        # Сохраняем результаты
        self._save_results(rotated_image, results, file_name)
        
        print("Обработка завершена!")
        return rotation_angle, results
    
    def _rotate_image(self, image: npt.NDArray, angle: int) -> npt.NDArray:
        """Поворачивает изображение на заданный угол."""
        if angle == 0:
            return image
        elif angle == 90:
            return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180:
            return cv2.rotate(image, cv2.ROTATE_180)
        elif angle == 270:
            return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        else:
            height, width = image.shape[:2]
            center = (width // 2, height // 2)
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            return cv2.warpAffine(image, rotation_matrix, (width, height))
    
    def _apply_template_transparency(self, region: np.ndarray, alpha: float = 0.2) -> np.ndarray:
        """Применяет прозрачность к эталонной спирали в области"""
        # Находим светлые области (эталонная спираль)
        gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        _, light_mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        
        # Применяем прозрачность к светлым областям
        result = region.copy()
        result[light_mask > 0] = result[light_mask > 0] * alpha + 255 * (1 - alpha)
        
        return result
    
    def _extract_regions(self, image: npt.NDArray, file_name: str) -> dict:
        """Извлекает L и R области из изображения."""
        squares = self.square_detector.find_black_squares(image)
        print(f"Найдено квадратов после поворота: {len(squares)}")
        
        l_squares, r_squares = self._group_squares_by_position(squares, image.shape[1])
        print(f"L квадратов: {len(l_squares)}, R квадратов: {len(r_squares)}")
        
        results = {'L_region': None, 'R_region': None, 'L_bbox': None, 'R_bbox': None}
        
        # Обрабатываем L область
        if len(l_squares) >= 3:
            l_bbox = self._create_region_from_points(l_squares)
            if l_bbox:
                results['L_bbox'] = l_bbox
                l_region = image[l_bbox[1]:l_bbox[3], l_bbox[0]:l_bbox[2]]
                # Применяем прозрачность к эталонной спирали
                l_region = self._apply_template_transparency(l_region, alpha=self.template_alpha)
                results['L_region'] = l_region
                cv2.imwrite(
                    os.path.join(self.output_dir, f'{file_name}_L_region.jpg'),
                    l_region
                )
                print(f"L область сохранена с прозрачностью: {l_bbox}")
        
        # Обрабатываем R область
        if len(r_squares) >= 3:
            r_bbox = self._create_region_from_points(r_squares)
            if r_bbox:
                results['R_bbox'] = r_bbox
                r_region = image[r_bbox[1]:r_bbox[3], r_bbox[0]:r_bbox[2]]
                # Применяем прозрачность к эталонной спирали
                r_region = self._apply_template_transparency(r_region, alpha=self.template_alpha)
                results['R_region'] = r_region
                cv2.imwrite(
                    os.path.join(self.output_dir, f'{file_name}_R_region.jpg'),
                    r_region
                )
                print(f"R область сохранена с прозрачностью: {r_bbox}")
        
        return results
    
    def _group_squares_by_position(self, squares: List[npt.NDArray], 
                                 image_width: int) -> Tuple[List, List]:
        """Группирует квадраты на L и R по их позиции."""
        l_squares, r_squares = [], []
        mid_x = image_width // 2
        
        for square in squares:
            M = cv2.moments(square)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                if cx < mid_x:
                    l_squares.append(square)
                else:
                    r_squares.append(square)
        
        return l_squares, r_squares
    
    def _create_region_from_points(self, squares: List[npt.NDArray], 
                                 padding: int = 10) -> Optional[Tuple[int, int, int, int]]:
        """Создает ограничивающую рамку по точкам квадратов."""
        if len(squares) < 3:
            return None
        
        points = []
        for square in squares[:3]:
            M = cv2.moments(square)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                points.append((cx, cy))
        
        if len(points) < 3:
            return None
        
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        
        # Добавляем отступы
        x_min = max(0, x_min - padding)
        y_min = max(0, y_min - padding)
        x_max = min(10000, x_max + padding)
        y_max = min(10000, y_max + padding)
        
        return (x_min, y_min, x_max, y_max)
    
    def _save_results(self, image: npt.NDArray, results: dict, file_name: str):
        """Сохраняет результаты обработки."""
        result_image = image.copy()
        
        # Рисуем bounding boxes
        if results['L_bbox']:
            bbox = results['L_bbox']
            cv2.rectangle(result_image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 0, 255), 3)
        
        if results['R_bbox']:
            bbox = results['R_bbox']
            cv2.rectangle(result_image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 0, 255), 3)
        
        cv2.imwrite(
            os.path.join(self.output_dir, f'{file_name}_result_with_red_squares.jpg'),
            result_image
        )
        
        cv2.imwrite(
            os.path.join(self.output_dir, f'{file_name}_rotated_document.jpg'),
            image
        )


# Функция для обратной совместимости
def process_medical_test(input_path: str, output_dir: str = "output") -> int:
    """Обрабатывает медицинский документ."""
    extractor = RegionExtractor(output_dir)
    rotation_angle, _ = extractor.process_medical_test(input_path)
    return rotation_angle