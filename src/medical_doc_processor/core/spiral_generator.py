import cv2
import numpy as np
import math
from typing import Tuple, List


class SpiralGenerator:
    """Класс для генерации спиралей Архимеда"""
    
    def __init__(self, square_size: int = 1067):  # Обновляем размер по умолчанию
        self.square_size = square_size
    
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
                   color: Tuple[int, int, int] = (128, 128, 128), thickness: int = 4):  # Уменьшаем толщину
        """Рисует спираль на изображении серым цветом"""
        if len(points) > 1:
            for i in range(len(points) - 1):
                cv2.line(img, points[i], points[i+1], color, thickness)