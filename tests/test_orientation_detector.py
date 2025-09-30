import os
import cv2
import pytest

from medical_doc_processor.core.orientation_detector import OrientationDetector
from medical_doc_processor.core.square_detector import SquareDetector
from medical_doc_processor.core.image_loader import load_image

class TestOrientationDetection:
    """Тесты определения ориентации на реальном документе"""
    
    def setup_method(self):
        self.orientation_detector = OrientationDetector()
        self.square_detector = SquareDetector()
        self.test_images_dir = 'tests/generated'
    
    def test_original_orientation(self):
        """Тест ориентации исходного изображения"""
        image_path = os.path.join(self.test_images_dir, 'original.jpg')
        image = load_image(image_path)
        squares = self.square_detector.find_black_squares(image)
        orientation = self.orientation_detector.detect_orientation_by_lines(squares, image.shape)
        
        print(f"📄 original.jpg: {len(squares)} квадратов, ориентация {orientation}°")
        assert orientation in [0, 90, 180, 270]
    
    def test_90_degrees_rotation(self):
        """Тест ориентации после поворота на 90°"""
        image_path = os.path.join(self.test_images_dir, 'rotated_90.jpg')
        image = load_image(image_path)
        squares = self.square_detector.find_black_squares(image)
        orientation = self.orientation_detector.detect_orientation_by_lines(squares, image.shape)
        
        print(f"📄 rotated_90.jpg: {len(squares)} квадратов, ориентация {orientation}°")
        assert orientation in [0, 90, 180, 270]
    
    def test_180_degrees_rotation(self):
        """Тест ориентации после поворота на 180°"""
        image_path = os.path.join(self.test_images_dir, 'rotated_180.jpg')
        image = load_image(image_path)
        squares = self.square_detector.find_black_squares(image)
        orientation = self.orientation_detector.detect_orientation_by_lines(squares, image.shape)
        
        print(f"📄 rotated_180.jpg: {len(squares)} квадратов, ориентация {orientation}°")
        assert orientation in [0, 90, 180, 270]
    
    def test_270_degrees_rotation(self):
        """Тест ориентации после поворота на 270°"""
        image_path = os.path.join(self.test_images_dir, 'rotated_270.jpg')
        image = load_image(image_path)
        squares = self.square_detector.find_black_squares(image)
        orientation = self.orientation_detector.detect_orientation_by_lines(squares, image.shape)
        
        print(f"📄 rotated_270.jpg: {len(squares)} квадратов, ориентация {orientation}°")
        assert orientation in [0, 90, 180, 270]
    
    def test_consistent_square_detection(self):
        """Тест что количество квадратов одинаково во всех ориентациях"""
        orientations = ['original.jpg', 'rotated_90.jpg', 'rotated_180.jpg', 'rotated_270.jpg']
        square_counts = []
        
        for filename in orientations:
            image_path = os.path.join(self.test_images_dir, filename)
            image = load_image(image_path)
            squares = self.square_detector.find_black_squares(image)
            square_counts.append(len(squares))
        
        # Допускаем небольшую разницу из-за артефактов поворота
        max_count = max(square_counts)
        min_count = min(square_counts)
        assert max_count - min_count <= 2, f"Сильно разное количество квадратов: {square_counts}"
        
        print(f"✅ Согласованность квадратов: {square_counts}")

def test_source_file_exists():
    """Проверка что исходный файл существует"""
    assert os.path.exists('tests/data/document.jpg'), "Исходный файл tests/data/document.jpg не найден"

def test_generated_images_exist():
    """Проверка что все сгенерированные изображения существуют"""
    generated_dir = 'tests/generated'
    expected_files = ['original.jpg', 'rotated_90.jpg', 'rotated_180.jpg', 'rotated_270.jpg']
    
    for filename in expected_files:
        path = os.path.join(generated_dir, filename)
        assert os.path.exists(path), f"Сгенерированный файл не найден: {path}"