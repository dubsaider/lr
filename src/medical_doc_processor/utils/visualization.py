import os
import cv2
import numpy as np
from collections import defaultdict
from typing import List
import numpy.typing as npt

from ..core.square_detector import SquareDetector


class Visualization:
    """Визуализация результатов обработки."""

    def __init__(self):
        self.square_detector = SquareDetector()

    def debug_lines(self, input_path: str, output_dir: str = "output") -> dict:
        """Создает отладочное изображение с линиями квадратов.

        Args:
            input_path: Путь к входному файлу
            output_dir: Директория для сохранения результатов

        Returns:
            dict: Информация о найденных линиях
        """
        from ..core.image_loader import ImageLoader

        os.makedirs(output_dir, exist_ok=True)
        file_name = os.path.splitext(os.path.basename(input_path))[0]

        # Загружаем изображение
        image_loader = ImageLoader()
        original_image = image_loader.load_image(input_path)

        # Находим квадраты
        squares = self.square_detector.find_black_squares(original_image)

        # Находим центры
        centers = []
        for square in squares:
            M = cv2.moments(square)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                centers.append((cx, cy, square))

        # Группируем по линиям
        y_tolerance = original_image.shape[0] * 0.05
        y_groups = self._group_centers_by_y(centers, y_tolerance)

        # Рисуем отладочное изображение
        debug_image = original_image.copy()
        self._draw_debug_info(debug_image, y_groups)

        # Сохраняем результат
        output_path = os.path.join(output_dir, f'{file_name}_debug_lines.jpg')
        cv2.imwrite(output_path, debug_image)

        # Выводим информацию
        line_info = self._get_line_info(y_groups)
        print(f"Найдено линий: {len(y_groups)}")
        for y, count in line_info.items():
            print(f"Линия на y={y}: {count} квадратов")

        return line_info

    def _group_centers_by_y(self, centers: List[tuple], y_tolerance: float) -> dict:
        """Группирует центры по Y координате."""
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
        return y_groups

    def _draw_debug_info(self, image: npt.NDArray, y_groups: dict):
        """Рисует отладочную информацию на изображении."""
        colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0),
                 (255, 0, 255), (0, 255, 255)]

        for i, (y, group) in enumerate(y_groups.items()):
            color = colors[i % len(colors)]
            for cx, cy, square in group:
                # Рисуем контур квадрата
                cv2.drawContours(image, [square], -1, color, 2)
                # Подписываем квадрат
                cv2.putText(image, f"L{i}", (cx, cy),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    def _get_line_info(self, y_groups: dict) -> dict:
        """Возвращает информацию о линиях."""
        return {y: len(group) for y, group in y_groups.items()}

    def create_processing_visualization(self, original_image: npt.NDArray,
                                      rotated_image: npt.NDArray,
                                      results: dict,
                                      file_name: str,
                                      output_dir: str = "output"):
        """Создает визуализацию процесса обработки."""
        os.makedirs(output_dir, exist_ok=True)

        # Создаем коллаж
        if original_image.shape != rotated_image.shape:
            # Приводим к одинаковому размеру для коллажа
            h, w = rotated_image.shape[:2]
            original_resized = cv2.resize(original_image, (w, h))
        else:
            original_resized = original_image

        # Создаем коллаж
        collage = np.vstack([original_resized, rotated_image])

        # Добавляем подписи
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(collage, "Original", (10, 30), font, 1, (255, 255, 255), 2)
        cv2.putText(collage, "Processed", (10, h + 30), font, 1, (255, 255, 255), 2)

        output_path = os.path.join(output_dir, f'{file_name}_processing_collage.jpg')
        cv2.imwrite(output_path, collage)


# Функция для обратной совместимости
def debug_lines(input_path: str, output_dir: str = "output") -> dict:
    """Создает отладочное изображение с линиями квадратов."""
    visualizer = Visualization()
    return visualizer.debug_lines(input_path, output_dir)
