import os
import cv2
import numpy as np

def create_test_images():
    """Создает тестовые изображения в разных ориентациях из исходного document.jpg"""
    
    # Пути к файлам
    source_path = 'tests/data/document.jpg'
    generated_dir = 'tests/generated'
    
    # Проверяем что исходный файл существует
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Исходный файл не найден: {source_path}")
    
    # Создаем директории
    os.makedirs(generated_dir, exist_ok=True)
    os.makedirs('tests/output', exist_ok=True)
    
    # Загружаем исходное изображение
    original_image = cv2.imread(source_path)
    if original_image is None:
        raise ValueError(f"Не удалось загрузить изображение: {source_path}")
    
    print(f"✅ Исходное изображение загружено: {original_image.shape}")
    
    # Создаем изображения в разных ориентациях
    images = {
        'original.jpg': original_image,
        'rotated_90.jpg': cv2.rotate(original_image, cv2.ROTATE_90_CLOCKWISE),
        'rotated_180.jpg': cv2.rotate(original_image, cv2.ROTATE_180),
        'rotated_270.jpg': cv2.rotate(original_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    }
    
    # Сохраняем все изображения
    for filename, image in images.items():
        output_path = os.path.join(generated_dir, filename)
        cv2.imwrite(output_path, image)
        print(f"✅ Создано: {output_path} ({image.shape})")
    
    print(f"\n🎯 Создано {len(images)} тестовых изображения в tests/generated/")
    
    return images

def verify_test_images():
    """Проверяет что все тестовые изображения созданы корректно"""
    generated_dir = 'tests/generated'
    expected_files = ['original.jpg', 'rotated_90.jpg', 'rotated_180.jpg', 'rotated_270.jpg']
    
    missing_files = []
    for filename in expected_files:
        path = os.path.join(generated_dir, filename)
        if not os.path.exists(path):
            missing_files.append(filename)
    
    if missing_files:
        print(f"❌ Отсутствуют файлы: {missing_files}")
        return False
    else:
        print("✅ Все тестовые изображения созданы корректно")
        return True

if __name__ == '__main__':
    try:
        create_test_images()
        verify_test_images()
    except Exception as e:
        print(f"❌ Ошибка: {e}")