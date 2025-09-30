import pytest
import sys
import os

# Добавляем src в путь для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

@pytest.fixture(scope='session', autouse=True)
def ensure_test_images_exist():
    """Фикстура гарантирует что тестовые изображения созданы перед запуском тестов"""
    try:
        # Добавляем tests в путь для импорта
        tests_dir = os.path.dirname(__file__)
        if tests_dir not in sys.path:
            sys.path.insert(0, tests_dir)
        
        from create_test_images import create_test_images, verify_test_images
        
        # Проверяем существование исходного файла
        source_path = 'tests/data/document.jpg'
        if not os.path.exists(source_path):
            pytest.skip(f"Исходный файл не найден: {source_path}")
        
        # Создаем тестовые изображения если их нет
        if not verify_test_images():
            create_test_images()
            
    except ImportError as e:
        pytest.skip(f"Не удалось импортировать create_test_images: {e}")
    except Exception as e:
        pytest.skip(f"Ошибка при создании тестовых изображений: {e}")