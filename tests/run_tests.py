"""Главный скрипт для запуска всех тестов"""

import os
import subprocess
import sys

def main():
    print("🧪 ЗАПУСК ТЕСТОВ С REAL DOCUMENT")
    print("=" * 50)
    
    # 1. Проверяем исходный файл
    source_path = 'tests/data/document.jpg'
    if not os.path.exists(source_path):
        print(f"❌ Исходный файл не найден: {source_path}")
        print("   Поместите document.jpg в tests/data/")
        return False
    
    # 2. Создаем тестовые изображения
    print("1. Создание тестовых изображений...")
    try:
        from create_test_images import create_test_images, verify_test_images
        create_test_images()
        if not verify_test_images():
            print("❌ Ошибка создания тестовых изображений")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    
    # 3. Запускаем тесты
    print("\n2. Запуск тестов...")
    test_files = [
        'tests/test_orientation_detector.py',
        # Добавьте другие тестовые файлы по мере создания
    ]
    
    all_passed = True
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\n📋 Запуск {os.path.basename(test_file)}...")
            result = subprocess.run([
                sys.executable, '-m', 'pytest', test_file, '-v', '--tb=short'
            ], capture_output=True, text=True)
            
            print(result.stdout)
            if result.returncode != 0:
                all_passed = False
                if result.stderr:
                    print("STDERR:", result.stderr)
        else:
            print(f"⚠️ Файл {test_file} не найден")
    
    # 4. Создаем визуальный отчет
    print("\n3. Создание визуального отчета...")
    try:
        from test_visual_validation import create_visual_test_report
        create_visual_test_report()
    except Exception as e:
        print(f"⚠️ Ошибка создания визуального отчета: {e}")
    
    # 5. Итоги
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("📁 Результаты в tests/output/")
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ")
    
    return all_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)