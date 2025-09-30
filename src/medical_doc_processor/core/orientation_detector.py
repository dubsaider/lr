import numpy as np
from collections import defaultdict
from typing import List, Tuple, Dict
import numpy.typing as npt
import cv2


class OrientationDetector:
    """Детектор ориентации документа по черным квадратам."""
    
    def __init__(self, y_tolerance_percent: float = 0.05):
        """
        Args:
            y_tolerance_percent: Допуск для группировки по Y координате (% от высоты)
        """
        self.y_tolerance_percent = y_tolerance_percent
    
    def detect_orientation_by_lines(self, squares: List[npt.NDArray], 
                                  image_shape: Tuple[int, int]) -> int:
        """Определяет ориентацию по двум линиям квадратов.
        
        Args:
            squares: Список контуров квадратов
            image_shape: Размеры изображения (height, width, channels)
            
        Returns:
            int: Угол поворота (0, 90, 180, 270)
        """
        if len(squares) < 6:  # Минимум 6 квадратов (2 + 4)
            print(f"Недостаточно квадратов для определения ориентации: {len(squares)}")
            return 0
        
        centers = self._get_square_centers(squares)
        y_groups = self._group_squares_by_lines(centers, image_shape[0])
        
        if len(y_groups) < 2:
            print(f"Не найдено достаточно линий: {len(y_groups)}")
            return self._fallback_orientation_detection(centers, image_shape)
        
        top_line, bottom_line = self._get_main_lines(y_groups)
        print(f"Верхняя линия: {len(top_line)} квадратов")
        print(f"Нижняя линия: {len(bottom_line)} квадратов")
        
        return self._determine_rotation_angle(top_line, bottom_line, image_shape)
    
    def _get_square_centers(self, squares: List[npt.NDArray]) -> List[Tuple[float, float, npt.NDArray]]:
        """Возвращает центры квадратов."""
        centers = []
        for square in squares:
            M = cv2.moments(square)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                centers.append((cx, cy, square))
        return centers
    
    def _group_squares_by_lines(self, centers: List[Tuple], image_height: int) -> Dict[float, List]:
        """Группирует квадраты по горизонтальным линиям."""
        y_tolerance = image_height * self.y_tolerance_percent
        y_groups = defaultdict(list)
        
        for cx, cy, square in centers:
            found_group = False
            for existing_y in y_groups.keys():
                if abs(cy - existing_y) < y_tolerance:
                    y_groups[existing_y].append((cx, cy, square))
                    found_group = True
                    break
            if not found_group:
                y_groups[cy].append((cx, cy, square))
        
        # Фильтруем группы с достаточным количеством квадратов
        return {y: group for y, group in y_groups.items() if len(group) >= 2}
    
    def _get_main_lines(self, y_groups: Dict[float, List]) -> Tuple[List, List]:
        """Возвращает верхнюю и нижнюю линии квадратов."""
        sorted_groups = sorted(y_groups.items(), key=lambda x: x[0])
        top_line = sorted_groups[0][1]
        bottom_line = sorted_groups[-1][1]
        return top_line, bottom_line
    
    def _determine_rotation_angle(self, top_line: List, bottom_line: List, 
                                image_shape: Tuple[int, int]) -> int:
        """Определяет угол поворота на основе расположения квадратов."""
        top_count, bottom_count = len(top_line), len(bottom_line)
        
        # Правильная ориентация: верхняя линия - 2 квадрата, нижняя - 4 квадрата
        if top_count == 2 and bottom_count == 4:
            print("Ориентация правильная")
            return 0
        elif top_count == 4 and bottom_count == 2:
            print("Изображение перевернуто на 180°")
            return 180
        elif top_count == 2 and bottom_count == 2:
            return self._handle_vertical_orientation(top_line, bottom_line, image_shape)
        else:
            print("Нестандартное расположение квадратов, используем fallback метод")
            return self._fallback_orientation_detection(
                top_line + bottom_line, image_shape
            )
    
    def _handle_vertical_orientation(self, top_line: List, bottom_line: List,
                                   image_shape: Tuple[int, int]) -> int:
        """Обрабатывает вертикальную ориентацию."""
        avg_x_top = np.mean([x for x, y, sq in top_line])
        avg_x_bottom = np.mean([x for x, y, sq in bottom_line])
        
        if avg_x_top < image_shape[1] * 0.5 and avg_x_bottom < image_shape[1] * 0.5:
            print("Поворот на 90° по часовой стрелке")
            return 90
        else:
            print("Поворот на 270° по часовой стрелке")
            return 270
    
    def _fallback_orientation_detection(self, centers: List[Tuple], 
                                      image_shape: Tuple[int, int]) -> int:
        """Альтернативный метод определения ориентации."""
        if not centers:
            return 0
            
        x_coords = [c[0] for c in centers]
        y_coords = [c[1] for c in centers]
        
        width = max(x_coords) - min(x_coords)
        height = max(y_coords) - min(y_coords)
        
        if width > height * 1.5:
            # Горизонтальная ориентация
            avg_y = np.mean(y_coords)
            return 90 if avg_y < image_shape[0] * 0.4 else 270
        else:
            # Вертикальная ориентация
            avg_x = np.mean(x_coords)
            return 0 if avg_x < image_shape[1] * 0.4 else 180


# Функция для обратной совместимости
def detect_orientation_by_lines(squares: List[npt.NDArray], 
                              image_shape: Tuple[int, int]) -> int:
    """Определяет ориентацию по двум линиям квадратов."""
    detector = OrientationDetector()
    return detector.detect_orientation_by_lines(squares, image_shape)