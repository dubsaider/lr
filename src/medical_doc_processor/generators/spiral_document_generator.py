# generators/spiral_document_generator.py
import cv2
import numpy as np
from typing import Tuple, Dict, List

from ..core.spiral_generator import SpiralGenerator
from ..components.document_components import DocumentComponents


class SpiralDocumentGenerator:
    """Генератор медицинских документов со спиралями Архимеда"""

    def __init__(self, width: int = 2339, height: int = 1654, language: str = "ru"):
        self.width = width
        self.height = height
        self.margin = 50
        # Базовый размер; позже может быть уменьшен под доступную высоту
        self.square_size = int((width - 3 * self.margin) / 2 * 0.9)
        self.marker_size = max(20, int(0.025 * self.square_size))
        self.language = language

        self.spiral_generator = SpiralGenerator(self.square_size)
        self.components = DocumentComponents(width, height, self.margin, self.square_size, self.marker_size, language)
        self._top_y = int(self.height * 0.15)

    def set_language(self, language: str):
        """Установка языка"""
        self.language = language
        self.components.set_language(language)

    def _calculate_positions(self) -> List[Tuple[Tuple[int, int], str]]:
        """Вычисляет позиции для двух спиралей"""
        squares = []
        y = self._top_y

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
        """Генерирует документ со спиралями"""

        times = {}

        if exercise is None:
            if self.language == "en":
                exercise = "Archimedes Spirals"
            else:
                exercise = "Спирали Архимеда"

        img = np.ones((self.height, self.width, 3), dtype=np.uint8) * 255

        # Динамически рассчитываем верхнюю границу и допустимый размер квадратов,
        # чтобы исключить пересечения с блоками времени и инструкциями
        base_scale = self.height / 1654.0
        header_h = int(120 * base_scale)  # высота шапки с запасом
        time_h = 50                      # высота блока времени (только текстовая строка)
        instructions_h = int(220 * base_scale)  # высота инструкций
        bottom_reserved = time_h + 50 + instructions_h + self.margin  # резерв снизу
        self._top_y = self.margin + header_h
        max_square_by_height = self.height - self._top_y - bottom_reserved
        max_square_by_width = int((self.width - 3 * self.margin) / 2)
        new_square = min(self.square_size, max_square_by_height, max_square_by_width)

        # Обновляем размеры, если уменьшили
        if new_square <= 0:
            new_square = max_square_by_width
        if new_square != self.square_size:
            self.square_size = new_square
            self.marker_size = max(18, int(0.025 * self.square_size))
            self.spiral_generator.square_size = self.square_size
            self.components.square_size = self.square_size
            self.components.marker_size = self.marker_size

        # Шапка
        self.components.draw_header(img, probe_number, exercise)

        # Квадраты со спиралями
        squares_layout = self._calculate_positions()

        for position, side in squares_layout:
            self.components.draw_square_with_markers(img, position, side)

            if side == "L":
                spiral_points = self.spiral_generator.generate_left_spiral(position)
            else:
                spiral_points = self.spiral_generator.generate_right_spiral(position)

            img = self.spiral_generator.draw_spiral(img, spiral_points)

        # Квадратики Л и П под спиралями и блок времени
        last_y = self.components.draw_time_fields_side_by_side(img, squares_layout, times)

        # Инструкции под блоками времени без наложения
        self.components.draw_compact_instructions(img, last_y + 30)

        cv2.imwrite(output_path, img, [cv2.IMWRITE_JPEG_QUALITY, 95])
        print(f"[OK] Документ создан ({self.language}): {output_path}")
        return output_path
