import os
import cv2
import numpy as np
import math
from typing import Tuple, Dict, List
from datetime import datetime

from ..core.spiral_generator import SpiralGenerator
from ..components.document_components import DocumentComponents


class SpiralDocumentGenerator:
    """Генератор медицинских документов со спиралями Архимеда в альбомной ориентации"""
    
    def __init__(self, width: int = 2339, height: int = 1654, language: str = "ru"):
        self.width = width
        self.height = height
        self.margin = 35
        # Адаптивный размер квадрата - 70% от ширины документа для двух квадратов
        self.square_size = int((width - 3 * self.margin) / 2 * 0.9)
        self.marker_size = 27
        self.language = language
        
        # Инициализация компонентов
        self.spiral_generator = SpiralGenerator(self.square_size)
        self.components = DocumentComponents(width, height, self.margin, self.square_size, self.marker_size, language)
    
    def set_language(self, language: str):
        """Установка языка"""
        self.language = language
        self.components.set_language(language)
    
    def _calculate_positions(self) -> List[Tuple[Tuple[int, int], str]]:
        """Вычисляет позиции для двух спиралей с адаптивным расположением"""
        squares = []
        
        # Адаптивная позиция по вертикали - 20% от высоты документа
        y = int(self.height * 0.15)
        
        # Центрируем квадраты с равными отступами
        total_width_needed = 2 * self.square_size + self.margin
        start_x = (self.width - total_width_needed) // 2
        
        x_left = start_x
        squares.append(((x_left, y), "L"))
        
        x_right = start_x + self.square_size + self.margin
        squares.append(((x_right, y), "R"))
        
        return squares

    def generate_document(self, output_path: str, 
                         probe_number: str = "1",
                         exercise: str = None,
                         times: Dict[str, str] = None) -> str:
        """Генерирует документ со спиралями в альбомной ориентации"""
        if times is None:
            times = {}
        
        # Устанавливаем упражнение по умолчанию в зависимости от языка
        if exercise is None:
            if self.language == "en":
                exercise = "Archimedes Spirals"
            else:
                exercise = "Спирали Архимеда"
        
        img = np.ones((self.height, self.width, 3), dtype=np.uint8) * 255
        
        # Рисуем компактную шапку
        self.components.draw_header(img, probe_number, exercise)
        
        squares_layout = self._calculate_positions()
        
        for position, side in squares_layout:
            self.components.draw_square_with_markers(img, position, side)
            
            if side == "L":
                spiral_points = self.spiral_generator.generate_left_spiral(position)
            else:
                spiral_points = self.spiral_generator.generate_right_spiral(position)
            
            self.spiral_generator.draw_spiral(img, spiral_points)
            
            time_key = f"{side.lower()}_time"
            time_value = times.get(time_key, "")
            self.components.draw_time_field(img, position, side, time_value)
        
        # Проверяем, что инструкции не пересекаются с квадратами
        max_square_bottom = max([pos[1] + self.square_size + 200 for pos, _ in squares_layout])
        if max_square_bottom > self.height * 0.7:
            print(f"⚠️ Внимание: Высота документа может быть недостаточной для инструкций")
        
        self.components.draw_instructions(img)
        
        cv2.imwrite(output_path, img, [cv2.IMWRITE_JPEG_QUALITY, 95])
        print(f"✅ Документ создан ({self.language}, {self.width}x{self.height}px): {output_path}")
        return output_path


def generate_sample_documents(output_dir: str = "generated_documents_landscape", language: str = "ru") -> List[str]:
    """Генерирует набор тестовых документов в альбомной ориентации"""
    os.makedirs(output_dir, exist_ok=True)
    generator = SpiralDocumentGenerator(language=language)
    
    documents = []
    
    # Основной документ
    if language == "en":
        exercise = "Archimedes Spirals Test"
    else:
        exercise = "Тест спиралей Архимеда"
    
    main_doc = generator.generate_document(
        os.path.join(output_dir, f"spiral_document_{language}.jpg"),
        probe_number="1",
        exercise=exercise
    )
    documents.append(main_doc)
    
    # Документ с временем
    doc_with_time = generator.generate_document(
        os.path.join(output_dir, f"spiral_document_with_time_{language}.jpg"),
        probe_number="2", 
        exercise=exercise,
        times={"l_time": "45", "r_time": "52"}
    )
    documents.append(doc_with_time)
    
    print(f"✅ Создано {len(documents)} тестовых документов ({language}) в {output_dir}/")
    return documents