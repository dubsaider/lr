import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
import io

def pdf_to_image(pdf_path):
    """Конвертируем PDF в изображение и поворачиваем на 90° против часовой стрелки"""
    doc = fitz.open(pdf_path)
    page = doc[0]
    mat = fitz.Matrix(2, 2)  # Увеличиваем DPI для качества
    pix = page.get_pixmap(matrix=mat)
    img_data = pix.tobytes("ppm")
    img = Image.open(io.BytesIO(img_data))
    img_array = np.array(img)
    doc.close()
    
    # Поворачиваем на 90° против часовой стрелки
    rotated_array = np.rot90(img_array, 1)  # 1 = 90°, 2 = 180°, 3 = 270°
    
    # Конвертируем в формат, совместимый с OpenCV (BGR)
    rotated_array = cv2.cvtColor(rotated_array, cv2.COLOR_RGB2BGR)
    
    return rotated_array

def find_black_squares(image):
    """Находим черные квадраты на изображении"""
    # Конвертируем в grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Бинаризация для выделения черных объектов
    _, binary = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
    
    # Морфологические операции для улучшения качества
    kernel = np.ones((3,3), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    
    # Находим контуры
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    squares = []
    for contour in contours:
        # Аппроксимируем контур
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        # Проверяем что это квадрат (4 угла)
        if len(approx) == 4:
            area = cv2.contourArea(contour)
            # Фильтруем по размеру (настраивайте под ваш случай)
            if 50 < area < 5000:
                # Проверяем что форма близка к квадрату
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = float(w)/h
                if 0.7 <= aspect_ratio <= 1.3:  # Допуск для квадрата
                    squares.append(approx)
    
    return squares

def group_squares_by_position(squares, image_width):
    """Группируем квадраты на L и R по их позиции на изображении"""
    l_squares = []
    r_squares = []
    
    mid_x = image_width // 2
    
    for square in squares:
        # Находим центр квадрата
        M = cv2.moments(square)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            
            # Если центр квадрата слева от середины - L, иначе R
            if cx < mid_x:
                l_squares.append(square)
            else:
                r_squares.append(square)
    
    return l_squares, r_squares

def create_red_square_from_three_points(squares):
    """Создаем красный квадрат по трем точкам"""
    if len(squares) < 3:
        return None
    
    # Берем центры трех квадратов
    points = []
    for square in squares[:3]:
        M = cv2.moments(square)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            points.append((cx, cy))
    
    if len(points) < 3:
        return None
    
    # Находим ограничивающий прямоугольник
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    
    x_min, x_max = min(x_coords), max(x_coords)
    y_min, y_max = min(y_coords), max(y_coords)
    
    # Добавляем отступы
    padding = 10
    x_min = max(0, x_min - padding)
    y_min = max(0, y_min - padding)
    x_max = min(10000, x_max + padding)  # 10000 - максимальная ширина
    y_max = min(10000, y_max + padding)  # 10000 - максимальная высота
    
    return (x_min, y_min, x_max, y_max)

def process_medical_test(pdf_path):
    """Основная функция обработки"""
    # Конвертируем PDF в изображение (уже повернутое)
    image = pdf_to_image(pdf_path)
    original_image = image.copy()
    
    print(f"Размер изображения: {image.shape}")
    
    # Находим все черные квадраты
    squares = find_black_squares(image)
    print(f"Найдено квадратов: {len(squares)}")
    
    # Группируем на L и R
    l_squares, r_squares = group_squares_by_position(squares, image.shape[1])
    print(f"L квадратов: {len(l_squares)}, R квадратов: {len(r_squares)}")
    
    # Обрабатываем L область
    if len(l_squares) >= 3:
        l_bbox = create_red_square_from_three_points(l_squares)
        if l_bbox:
            print(f"L bbox: {l_bbox}")
            # Рисуем красный квадрат
            cv2.rectangle(image, (l_bbox[0], l_bbox[1]), (l_bbox[2], l_bbox[3]), (0, 0, 255), 3)
            # Сохраняем область L
            l_region = original_image[l_bbox[1]:l_bbox[3], l_bbox[0]:l_bbox[2]]
            cv2.imwrite('L_region.jpg', l_region)
            print(f"L область сохранена: {l_bbox}")
    
    # Обрабатываем R область
    if len(r_squares) >= 3:
        r_bbox = create_red_square_from_three_points(r_squares)
        if r_bbox:
            print(f"R bbox: {r_bbox}")
            # Рисуем красный квадрат
            cv2.rectangle(image, (r_bbox[0], r_bbox[1]), (r_bbox[2], r_bbox[3]), (0, 0, 255), 3)
            # Сохраняем область R
            r_region = original_image[r_bbox[1]:r_bbox[3], r_bbox[0]:r_bbox[2]]
            cv2.imwrite('R_region.jpg', r_region)
            print(f"R область сохранена: {r_bbox}")
    
    # Сохраняем результат с разметкой
    cv2.imwrite('result_with_red_squares.jpg', image)
    print("Обработка завершена!")

# Дополнительная функция для отладки - показывает все найденные квадраты
def debug_squares(pdf_path):
    """Функция для отладки - показывает все найденные квадраты"""
    image = pdf_to_image(pdf_path)
    squares = find_black_squares(image)
    
    debug_image = image.copy()
    for i, square in enumerate(squares):
        # Рисуем контур квадрата
        cv2.drawContours(debug_image, [square], -1, (0, 255, 0), 2)
        
        # Подписываем номер квадрата
        M = cv2.moments(square)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            cv2.putText(debug_image, str(i), (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    
    cv2.imwrite('debug_squares.jpg', debug_image)
    print(f"Отладочное изображение сохранено. Найдено {len(squares)} квадратов")

# Запуск обработки
if __name__ == "__main__":
    pdf_path = "1.pdf"
    
    # Сначала посмотрим что находит (для отладки)
    debug_squares(pdf_path)
    
    # Затем основная обработка
    process_medical_test(pdf_path)