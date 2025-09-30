import os
import cv2
import pytest

class TestDocumentGenerator:
    """Тесты генератора документов"""
    
    def test_generator_creation(self):
        """Тест создания генератора"""
        from medical_doc_processor.generators import SpiralDocumentGenerator
        
        generator = SpiralDocumentGenerator()
        assert generator.width == 1200
        assert generator.height == 1600
        print("✅ Генератор создан успешно")
    
    def test_document_generation(self):
        """Тест генерации документа"""
        from medical_doc_processor.generators import SpiralDocumentGenerator
        
        generator = SpiralDocumentGenerator()
        output_path = 'tests/output/test_generated.jpg'
        
        os.makedirs('tests/output', exist_ok=True)
        result_path = generator.generate_document(output_path)
        
        # Проверяем что файл создан
        assert os.path.exists(result_path)
        
        # Проверяем что это валидное изображение
        img = cv2.imread(result_path)
        assert img is not None
        assert img.shape == (1600, 1200, 3)
        
        print(f"✅ Документ сгенерирован: {result_path}")

if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])