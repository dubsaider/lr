import cv2
import numpy as np
from typing import Tuple, List
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
        
        # Компактная шапка в одну строку
        header_text = (
            f"{self.text_renderer.get_text('medical_test')} | "
            f"{self.text_renderer.get_text('probe')} {probe_number} | "
            f"{self.text_renderer.get_text('date')}: {current_date} | "
            f"{self.text_renderer.get_text('exercise')}: {exercise}"
        )
        
        # Адаптивный размер шрифта в зависимости от высоты документа
        base_font_scale = self.height / 1400  # Нормализуем относительно 2480px
        
        # Заголовок - одна строка, крупный шрифт
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
        
        # Буквы L/R под квадратом (крупные)
        text_y = y + self.square_size + 80
        side_text = self.text_renderer.get_text("left") if side == "L" else self.text_renderer.get_text("right")
        
        # Адаптивный размер шрифта
        base_font_scale = self.height / 1400
        
        self._put_text(img, side_text, 
                      (x + self.square_size // 2 - 20, text_y),
                      font_scale=2.5 * base_font_scale, color=(0, 0, 0), thickness=5)
        
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
    
    def draw_time_field(self, img: np.ndarray, position: Tuple[int, int], side: str, time: str = ""):
        """Рисует поле для ввода времени"""
        x, y = position
        time_y = y + self.square_size + 150
        
        # Получаем тексты для времени
        time_text = self.text_renderer.get_text("time_left") if side == "L" else self.text_renderer.get_text("time_right")
        sec_text = self.text_renderer.get_text("sec")
        
        if time:
            time_display = f"{time_text}: {time} {sec_text}"
        else:
            time_display = f"{time_text}: ________ {sec_text}"
        
        # Адаптивный размер шрифта
        base_font_scale = self.height / 1400
        
        # Рисуем время
        self._put_text(img, time_display, (x, time_y),
                      font_scale=1.4 * base_font_scale, color=(0, 0, 0), thickness=3)
    
    def draw_instructions(self, img: np.ndarray):
        """Добавляет инструкции к документу - АДАПТИВНОЕ РАСПОЛОЖЕНИЕ"""
        # Вычисляем позицию инструкций адаптивно относительно высоты документа
        # Оставляем 20% от высоты документа для инструкций
        instructions_start_ratio = 0.75  # 75% высоты - начало инструкций
        instructions_y = int(self.height * instructions_start_ratio)
        
        # Проверяем, не пересекается ли с квадратами
        min_safe_y = self.square_size + 400  # Минимальная безопасная позиция
        if instructions_y < min_safe_y:
            instructions_y = min_safe_y
        
        instructions = [
            self.text_renderer.get_text("instruction_1"),
            self.text_renderer.get_text("instruction_2"),
            self.text_renderer.get_text("instruction_3"),
            self.text_renderer.get_text("instruction_4"),
            self.text_renderer.get_text("instruction_5")
        ]
        
        # Адаптивный размер шрифта
        base_font_scale = self.height / 1400
        
        # Рисуем разделительную линию
        cv2.line(img, (self.margin, instructions_y - 30), 
                (self.width - self.margin, instructions_y - 30), (0, 0, 0), 3)
        
        # Заголовок инструкций
        instructions_title = self.text_renderer.get_text("instructions")
        self._put_text(img, instructions_title, 
                      (self.margin, instructions_y),
                      font_scale=1.5 * base_font_scale, color=(0, 0, 0), thickness=3)
        
        # Пункты инструкций
        for i, instruction in enumerate(instructions):
            y_pos = instructions_y + int(80 * base_font_scale) + i * int(70 * base_font_scale)
            self._put_text(img, instruction, 
                          (self.margin, y_pos),
                          font_scale=1.0 * base_font_scale, color=(0, 0, 0), thickness=2)