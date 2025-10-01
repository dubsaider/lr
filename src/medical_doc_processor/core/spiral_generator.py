import cv2
import numpy as np
import math
from typing import Tuple, List


class SpiralGenerator:
    """Класс для генерации спиралей Архимеда"""
    
    def __init__(self, square_size: int = 1067, template_alpha: float = 0.4):
        self.square_size = square_size
        self.template_alpha = template_alpha  # Прозрачность эталонной спирали
    
    def generate_left_spiral(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Генерирует точки для левой спирали Архимеда"""
        x, y = position
        center_x = x + self.square_size // 2
        center_y = y + self.square_size // 2
        max_radius = self.square_size // 2 - 10
        
        points = []
        # 6 витков как и раньше, но с меньшим количеством точек для оптимизации
        for theta in np.linspace(0, 6 * math.pi, 800):  # Уменьшаем количество точек
            r = max_radius * (theta / (6 * math.pi))
            if r > max_radius:
                break
                
            px = int(center_x + r * math.cos(theta))
            py = int(center_y + r * math.sin(theta))
            
            if (x <= px <= x + self.square_size and 
                y <= py <= y + self.square_size):
                points.append((px, py))
        
        return points
    
    def generate_right_spiral(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Генерирует точки для правой спирали Архимеда"""
        x, y = position
        center_x = x + self.square_size // 2
        center_y = y + self.square_size // 2
        max_radius = self.square_size // 2 - 10
        
        points = []
        for theta in np.linspace(0, 6 * math.pi, 800):  # Уменьшаем количество точек
            r = max_radius * (theta / (6 * math.pi))
            if r > max_radius:
                break
                
            px = int(center_x + r * math.cos(-theta))
            py = int(center_y + r * math.sin(-theta))
            
            if (x <= px <= x + self.square_size and 
                y <= py <= y + self.square_size):
                points.append((px, py))
        
        return points
    
    def draw_spiral(self, img: np.ndarray, points: List[Tuple[int, int]], 
                   color: Tuple[int, int, int] = (128, 128, 128), thickness: int = 4,
                   alpha: float = None):
        """Рисует спираль на изображении с прозрачностью"""
        if alpha is None:
            alpha = self.template_alpha
            
        if len(points) > 1:
            # Создаем копию изображения для рисования спирали
            overlay = img.copy()
            for i in range(len(points) - 1):
                cv2.line(overlay, points[i], points[i+1], color, thickness)
            
            # Применяем прозрачность: смешиваем оригинал и overlay
            # alpha - непрозрачность спирали, (1-alpha) - непрозрачность фона
            img = cv2.addWeighted(img, 1.0 - alpha, overlay, alpha, 0)
        
        return img