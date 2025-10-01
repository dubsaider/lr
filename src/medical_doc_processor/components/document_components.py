import cv2
import numpy as np
from typing import Tuple, List, Dict
from datetime import datetime

from ..utils.text_utils import TextRenderer


class DocumentComponents:
    """Класс для отрисовки компонентов документа"""
    
    def __init__(self, width: int, height: int, margin: int, square_size: int, marker_size: int, language: str = "ru"):
        self.width = width
        self.height = height
        self.margin = margin
        self.square_size = square_size
        self.marker_size = marker_size
        self.text_renderer = TextRenderer(language)
        self.language = language
    
    def set_language(self, language: str):
        """Установка языка"""
        self.language = language
        self.text_renderer.set_language(language)
    
    def _put_text(self, img: np.ndarray, text: str, position: Tuple[int, int], 
                 font_scale: float = 1.0, color: Tuple[int, int, int] = (0, 0, 0), 
                 thickness: int = 2):
        """Обертка для функции put_text"""
        self.text_renderer.put_text(img, text, position, font_scale, color, thickness)
    
    def draw_header(self, img: np.ndarray, probe_number: str, exercise: str):
        """Рисует компактную шапку документа в одну строку"""
        current_date = datetime.now().strftime("%d.%m.%Y")
        
        header_text = (
            f"{exercise} | "
            f"{self.text_renderer.get_text('probe')} {probe_number} | "
            f"{current_date}"
        )
        
        base_font_scale = self.height / 1400
        
        self._put_text(img, header_text, 
                      (self.margin, int(80 * base_font_scale)),
                      font_scale=1.8 * base_font_scale, color=(0, 0, 0), thickness=3)
    
    def draw_square_with_markers(self, img: np.ndarray, position: Tuple[int, int], side: str):
        """Рисует квадрат с маркерами ориентации"""
        x, y = position
        
        # Рисуем внешний квадрат
        cv2.rectangle(img, (x, y), 
                     (x + self.square_size, y + self.square_size), 
                     (0, 0, 0), 4)
        
        # Маркеры ориентации в углах
        if side == "L":
            markers = [
                (x + 40, y + 40),
                (x + 40, y + self.square_size - 40),
                (x + self.square_size - 40, y + self.square_size - 40)
            ]
        else:
            markers = [
                (x + self.square_size - 40, y + 40),
                (x + 40, y + self.square_size - 40),
                (x + self.square_size - 40, y + self.square_size - 40)
            ]
        
        # Рисуем увеличенные маркеры
        for marker_pos in markers:
            cv2.rectangle(img, 
                         (marker_pos[0] - self.marker_size, marker_pos[1] - self.marker_size),
                         (marker_pos[0] + self.marker_size, marker_pos[1] + self.marker_size),
                         (0, 0, 0), -1)
    
    def draw_time_fields_side_by_side(self, img: np.ndarray, squares_layout: List[Tuple[Tuple[int, int], str]], times: Dict[str, str]):
        """Рисует строки для записи времени под спиралями (Время Л ___ сек)"""
        if len(squares_layout) < 2:
            return
            
        # Получаем позиции квадратов
        (left_pos, _), (right_pos, _) = squares_layout
        
        base_font_scale = self.height / 1400
        
        # Позиция под квадратами со спиралями
        below_y = left_pos[1] + self.square_size + 40
        
        # ЛЕВЫЙ БЛОК (Время Л ___________ сек)
        # Центр левой спирали
        left_center_x = left_pos[0] + self.square_size // 2
        
        # Формируем текст
        time_left_text = f"{self.text_renderer.get_text('time')} {self.text_renderer.get_text('left')} ___________ {self.text_renderer.get_text('sec')}"
        
        # Вычисляем ширину текста для центрирования
        (text_w, text_h), _ = cv2.getTextSize(time_left_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8 * base_font_scale, 2)
        left_text_x = left_center_x - text_w // 2
        
        self._put_text(img, time_left_text, (left_text_x, below_y + 30), 
                      font_scale=0.8 * base_font_scale, color=(0, 0, 0), thickness=2)
        
        # ПРАВЫЙ БЛОК (Время П ___________ сек)
        # Центр правой спирали
        right_center_x = right_pos[0] + self.square_size // 2
        
        # Формируем текст
        time_right_text = f"{self.text_renderer.get_text('time')} {self.text_renderer.get_text('right')} ___________ {self.text_renderer.get_text('sec')}"
        
        # Вычисляем ширину текста для центрирования
        (text_w, text_h), _ = cv2.getTextSize(time_right_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8 * base_font_scale, 2)
        right_text_x = right_center_x - text_w // 2
        
        self._put_text(img, time_right_text, (right_text_x, below_y + 30), 
                      font_scale=0.8 * base_font_scale, color=(0, 0, 0), thickness=2)
        
        # Возвращаем нижнюю границу
        return below_y + 50
    
    
    def draw_compact_instructions(self, img: np.ndarray, start_y: int):
        """Рисует компактные инструкции. Заголовок начинается ПОД линией."""
        instructions = [
            self.text_renderer.get_text("instruction_1"),
            self.text_renderer.get_text("instruction_2"), 
            self.text_renderer.get_text("instruction_3"),
            self.text_renderer.get_text("instruction_4"),
            self.text_renderer.get_text("instruction_5")
        ]
        
        base_font_scale = self.height / 1400
        
        # Разделительная линия на уровне start_y
        line_y = start_y
        cv2.line(img, (self.margin, line_y), 
                (self.width - self.margin, line_y), (0, 0, 0), 2)
        
        # Заголовок инструкций — чуть ниже линии
        title_offset = int(50 * base_font_scale)
        title_y = line_y + title_offset
        
        instructions_title = self.text_renderer.get_text("instructions")
        self._put_text(img, instructions_title, 
                      (self.margin, title_y),
                      font_scale=1.3 * base_font_scale, color=(0, 0, 0), thickness=3)
        
        # Инструкции — две колонки (1-3 слева, 4-5 справа)
        start_list_y = title_y + int(55 * base_font_scale)
        line_step = int(42 * base_font_scale)  # уменьшенный интервал между строками
        col_width = (self.width - 3 * self.margin) // 2
        col1_x = self.margin
        col2_x = self.margin + col_width + self.margin

        col1 = instructions[:3]
        col2 = instructions[3:]

        # Рисуем все инструкции без проверки (они должны поместиться)
        for i, instruction in enumerate(col1):
            y_pos = start_list_y + i * line_step
            self._put_text(img, instruction, (col1_x, y_pos),
                          font_scale=0.85 * base_font_scale, color=(0, 0, 0), thickness=2)
        
        for i, instruction in enumerate(col2):
            y_pos = start_list_y + i * line_step
            self._put_text(img, instruction, (col2_x, y_pos),
                          font_scale=0.85 * base_font_scale, color=(0, 0, 0), thickness=2)