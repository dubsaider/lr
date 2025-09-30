import cv2
import numpy as np
from typing import Tuple, Dict
import os


class TextRenderer:
    """Класс для работы с текстом и шрифтами с поддержкой мультиязычности"""
    
    def __init__(self, language: str = "ru"):
        self.language = language
        self._setup_fonts()
    
    def _setup_fonts(self):
        """Настройка шрифтов"""
        self.available_fonts = [cv2.FONT_HERSHEY_SIMPLEX]
    
    def set_language(self, language: str):
        """Установка языка"""
        self.language = language
    
    def get_text(self, key: str) -> str:
        """Получение текста на выбранном языке"""
        translations = {
            "medical_test": {
                "ru": "МЕДИЦИНСКИЙ ТЕСТ",
                "en": "MEDICAL TEST"
            },
            "probe": {
                "ru": "Проба",
                "en": "Probe"
            },
            "date": {
                "ru": "Дата",
                "en": "Date"
            },
            "exercise": {
                "ru": "Упражнение",
                "en": "Exercise"
            },
            "archimedes_spirals": {
                "ru": "Спирали Архимеда",
                "en": "Archimedes Spirals"
            },
            "archimedes_spirals_test": {
                "ru": "Тест спиралей Архимеда",
                "en": "Archimedes Spirals Test"
            },
            "time": {
                "ru": "Время",
                "en": "Time"
            },
            "sec": {
                "ru": "сек",
                "en": "sec"
            },
            "instructions": {
                "ru": "ИНСТРУКЦИЯ:",
                "en": "INSTRUCTIONS:"
            },
            "instruction_1": {
                "ru": "1. Нарисуйте спираль, используя ручку синего цвета.",
                "en": "1. Draw the spiral using a blue pen."
            },
            "instruction_2": {
                "ru": "2. Начните рисование из центра шаблона, двигая ручку по его контуру.",
                "en": "2. Start drawing from the center of the template, moving the pen along its contour."
            },
            "instruction_3": {
                "ru": "3. Выполните упражнение левой и правой рукой, соответственно шаблонам L и R.",
                "en": "3. Perform the exercise with left and right hands, according to L and R templates."
            },
            "instruction_4": {
                "ru": "4. Измерьте время рисования фигуры в секундах, используя секундомер.",
                "en": "4. Measure the drawing time in seconds using a stopwatch."
            },
            "instruction_5": {
                "ru": "5. Результат измерения запишите в соответствующее поле на шаблоне.",
                "en": "5. Record the measurement result in the corresponding field on the template."
            },
            "left": {
                "ru": "L",
                "en": "L"
            },
            "right": {
                "ru": "R",
                "en": "R"
            },
            "time_left": {
                "ru": "Время L",
                "en": "Time L"
            },
            "time_right": {
                "ru": "Время R",
                "en": "Time R"
            }
        }
        
        return translations.get(key, {}).get(self.language, key)
    
    def put_text(self, img: np.ndarray, text: str, position: Tuple[int, int], 
                 font_scale: float = 1.0, color: Tuple[int, int, int] = (0, 0, 0), 
                 thickness: int = 2):
        """Функция для отображения текста"""
        try:
            cv2.putText(img, text, position, cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
        except Exception as e:
            # Если есть проблемы с отображением, пробуем английскую версию
            try:
                safe_text = text.encode('ascii', 'ignore').decode('ascii')
                if not safe_text:
                    safe_text = "TEXT"
                cv2.putText(img, safe_text, position, cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
            except Exception as e2:
                cv2.putText(img, "TEXT", position, cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)