import cv2
import numpy as np
import os

def put_text_ru(image, text, position, font_scale=0.7, color=(0, 0, 255), thickness=2):
    """Добавляет русский текст на изображение с обработкой кодировки"""
    try:
        # Пробуем разные шрифты
        fonts = [
            cv2.FONT_HERSHEY_SIMPLEX,
            cv2.FONT_HERSHEY_COMPLEX, 
            cv2.FONT_HERSHEY_TRIPLEX
        ]
        
        for font in fonts:
            try:
                cv2.putText(image, text, position, font, font_scale, color, thickness)
                return True
            except:
                continue
        
        # Если все шрифты не работают, используем английский аналог
        eng_text = text.replace('°', 'deg').replace('?', 'sq')
        cv2.putText(image, eng_text, position, fonts[0], font_scale, color, thickness)
        return True
        
    except Exception as e:
        print(f"Ошибка при добавлении текста: {e}")
        return False

def create_text_image(text, width=400, height=100, background_color=(255, 255, 255), text_color=(0, 0, 0)):
    """Создает изображение с текстом (альтернативный способ)"""
    # Создаем белое изображение
    img = np.ones((height, width, 3), dtype=np.uint8) * background_color
    
    # Пробуем добавить текст
    success = put_text_ru(img, text, (10, height//2), font_scale=1, color=text_color)
    
    if not success:
        # Если не удалось, создаем простой прямоугольник с английским текстом
        cv2.rectangle(img, (0, 0), (width, height), (0, 0, 255), 2)
        eng_text = "Text: " + text.encode('ascii', 'replace').decode('ascii')
        cv2.putText(img, eng_text, (10, height//2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1)
    
    return img