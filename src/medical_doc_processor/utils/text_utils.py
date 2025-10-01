import cv2
import numpy as np
from typing import Tuple, Dict
import os
from PIL import Image, ImageDraw, ImageFont


class TextRenderer:
    """Класс для работы с текстом и шрифтами с поддержкой мультиязычности"""
    
    def __init__(self, language: str = "ru"):
        self.language = language
        self._setup_fonts()
    
    def _setup_fonts(self):
        """Настройка шрифтов: ищем системный TTF с поддержкой кириллицы."""
        self.available_fonts = [cv2.FONT_HERSHEY_SIMPLEX]
        self.ttf_font_path = self._find_font_path()
        self._font_cache: Dict[float, ImageFont.FreeTypeFont] = {}

    def _find_font_path(self) -> str:
        """Находит путь к TTF-шрифту с поддержкой кириллицы.
        Возвращает пустую строку если не найдено (будет fallback).
        """
        candidates = []
        # Windows стандартные шрифты
        win_fonts = [
            r"C:\\Windows\\Fonts\\arial.ttf",
            r"C:\\Windows\\Fonts\\ARIAL.TTF",
            r"C:\\Windows\\Fonts\\segoeui.ttf",
            r"C:\\Windows\\Fonts\\Calibri.ttf",
            r"C:\\Windows\\Fonts\\tahoma.ttf",
        ]
        candidates.extend(win_fonts)
        # Популярные кроссплатформенные
        candidates.extend([
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            "/Library/Fonts/Arial.ttf",
        ])
        for path in candidates:
            if os.path.exists(path):
                return path
        return ""
    
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
                "ru": "1. Возьмите синюю ручку.",
                "en": "1. Use a blue pen."
            },
            "instruction_2": {
                "ru": "2. Для каждого шаблона измерьте время в секундах.",
                "en": "2. For each template, measure drawing time in seconds."
            },
            "instruction_3": {
                "ru": "3. Начните из центра и ведите по контуру, не отрываясь.",
                "en": "3. Start from the center and follow the contour without lifting."
            },
            "instruction_4": {
                "ru": "4. Сначала выполните шаблон Л, затем шаблон П.",
                "en": "4. Complete the L template first, then the R template."
            },
            "instruction_5": {
                "ru": "5. Запишите значения в поля \"Время Л\" и \"Время П\".",
                "en": "5. Enter the values in the \"Time L\" and \"Time R\" fields."
            },
            "left": {
                "ru": "Л",
                "en": "L"
            },
            "right": {
                "ru": "П",
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
        """Отрисовывает текст с поддержкой кириллицы через PIL, с fallback на OpenCV.
        position — левый нижний угол (как у cv2.putText).
        """
        if not isinstance(img, np.ndarray) or img.ndim != 3:
            return

        # Если найден TTF-шрифт, используем PIL
        if self.ttf_font_path:
            try:
                # Приблизим cv2 font_scale к пикселям (эмпирически ~32 px на 1.0)
                px = max(10, int(32 * font_scale))
                font = self._font_cache.get(px)
                if font is None:
                    font = ImageFont.truetype(self.ttf_font_path, px)
                    self._font_cache[px] = font

                # cv2 в BGR; PIL ожидает RGB
                image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(image_rgb)
                draw = ImageDraw.Draw(pil_img)

                # У PIL координата — по верхней левой точке. Преобразуем из baseline.
                # Оценим высоту текста для смещения вверх.
                ascent, descent = font.getmetrics()
                text_y_top = position[1] - ascent

                draw.text((position[0], text_y_top), text, font=font,
                          fill=(int(color[2]), int(color[1]), int(color[0])),
                          stroke_width=max(0, thickness - 1), stroke_fill=(int(color[2]), int(color[1]), int(color[0])))

                # Обратно в OpenCV
                img[:, :, :] = cv2.cvtColor(np.asarray(pil_img), cv2.COLOR_RGB2BGR)
                return
            except Exception:
                pass

        # Fallback: OpenCV (ASCII)
        try:
            cv2.putText(img, text, position, cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
        except Exception:
            safe_text = text.encode('ascii', 'ignore').decode('ascii') or "TEXT"
            cv2.putText(img, safe_text, position, cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
