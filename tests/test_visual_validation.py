import os
import cv2
import numpy as np

def create_visual_test_report():
    """Создает визуальный отчет для проверки работы детектора"""
    from medical_doc_processor.core.orientation_detector import OrientationDetector
    from medical_doc_processor.core.square_detector import SquareDetector
    from medical_doc_processor.core.image_loader import load_image
    
    # Пробуем импортировать нашу утилиту для текста
    try:
        from medical_doc_processor.utils.text_utils import put_text_ru
        use_russian_text = True
    except ImportError:
        use_russian_text = False
    
    detector = OrientationDetector()
    square_detector = SquareDetector()
    
    test_cases = [
        ('original.jpg', 'Original'),
        ('rotated_90.jpg', 'Rotated 90deg'), 
        ('rotated_180.jpg', 'Rotated 180deg'),
        ('rotated_270.jpg', 'Rotated 270deg')
    ]
    
    os.makedirs('tests/output/visual_report', exist_ok=True)
    
    print("[INFO] Creating visual report...")
    
    for filename, description in test_cases:
        try:
            image_path = os.path.join('tests/generated', filename)
            image = load_image(image_path)
            squares = square_detector.find_black_squares(image)
            orientation = detector.detect_orientation_by_lines(squares, image.shape)
            
            # Создаем визуализацию
            vis_image = image.copy()
            
            # Рисуем квадраты
            for i, square in enumerate(squares):
                cv2.drawContours(vis_image, [square], -1, (0, 255, 0), 2)
            
            # Добавляем информацию на английском (избегаем проблем с кодировкой)
            info_text = f"{description}: {orientation}deg ({len(squares)} squares)"
            
            # Пробуем разные способы добавления текста
            try:
                # Способ 1: Стандартный шрифт
                cv2.putText(vis_image, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            except:
                try:
                    # Способ 2: Другой шрифт
                    cv2.putText(vis_image, info_text, (10, 30), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)
                except:
                    # Способ 3: Простой текст без специальных символов
                    simple_text = f"Orientation: {orientation} deg"
                    cv2.putText(vis_image, simple_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Сохраняем
            output_path = os.path.join('tests/output/visual_report', filename)
            cv2.imwrite(output_path, vis_image)
            print(f"[OK] Created: {output_path}")
            
        except Exception as e:
            print(f"[ERR] Error processing {filename}: {e}")
    
    print("[INFO] Visual report created in tests/output/visual_report/")

def create_simple_text_image():
    """Создает тестовое изображение с текстом для проверки кодировки"""
    # Создаем изображение
    img = np.ones((200, 600, 3), dtype=np.uint8) * 255
    
    # Добавляем разный текст
    texts = [
        "English: Orientation 90deg",
        "Russian test: Градусы",
        "Symbols: 90° 180° 270°",
        "Squares: 6 квадратов"
    ]
    
    for i, text in enumerate(texts):
        y_position = 30 + i * 40
        try:
            cv2.putText(img, text, (10, y_position), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
            print(f"[OK] Text added: {text}")
        except Exception as e:
            safe_text = text.encode('ascii', 'replace').decode('ascii')
            cv2.putText(img, safe_text, (10, y_position), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            print(f"[WARN] Used safe text: {safe_text} (original: {text})")
    
    # Сохраняем
    os.makedirs('tests/output', exist_ok=True)
    cv2.imwrite('tests/output/text_encoding_test.jpg', img)
    print("[OK] Text encoding test saved: tests/output/text_encoding_test.jpg")

if __name__ == '__main__':
    create_simple_text_image()
    create_visual_test_report()