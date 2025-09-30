# Medical Document Processor

Автоматическое определение ориентации и извлечение областей из медицинских документов.

## Что делает проект

1. **Автоматическое определение ориентации** - анализирует расположение черных квадратов-маркеров (2 сверху, 4 снизу) и автоматически поворачивает документ в правильную ориентацию
2. **Извлечение областей** - находит L и R области на основе расположения квадратов-маркеров
3. **Поддержка разных форматов** - работает с PDF и изображениями (JPG, PNG, TIFF, BMP)
4. **Визуализация** - создает отладочные изображения для анализа процесса

## Установка

### Из репозитория GitHub
```bash
pip install git+https://github.com/constantintesla/lr.git
```

### Для разработки
```bash
git clone https://github.com/constantintesla/lr.git
cd lr
pip install -e ".[dev]"
```

## Быстрый старт

### Через CLI
```bash
# Обработать один файл
lr-processor process document.pdf

# С отладочной информацией
lr-processor process scan.jpg --debug --output-dir results

# Обработать все файлы в папке
lr-processor batch ./scans --recursive
```

### Через Python
```python
from medical_doc_processor import process_medical_test, debug_lines

# Обработка документа
rotation_angle = process_medical_test("document.pdf", output_dir="results")

# Отладочная визуализация
debug_lines("document.pdf", output_dir="debug")
```

## Использование CLI

### Обработка одного файла
```bash
lr-processor process input.pdf --output-dir results --debug
```

### Пакетная обработка
```bash
lr-processor batch ./input_scans --recursive --output-dir ./output
```

### Отладочная информация
```bash
lr-processor debug document.pdf
```

### Проверка файла
```bash
lr-processor validate image.png
```

### Информация о форматах
```bash
lr-processor info
```

## Результаты

Для каждого обработанного файла создаются:

- `*_L_region.jpg` - извлеченная L область
- `*_R_region.jpg` - извлеченная R область  
- `*_result_with_red_squares.jpg` - результат с красными рамками
- `*_rotated_document.jpg` - повернутый документ
- `*_debug_lines.jpg` - отладочная информация (с опцией `--debug`)

## Поддерживаемые форматы

- **Изображения**: JPG, JPEG, PNG, BMP, TIFF, TIF
- **Документы**: PDF (требуется PyMuPDF)

## Алгоритм работы

1. **Загрузка документа** - конвертация PDF или загрузка изображения
2. **Обнаружение маркеров** - поиск черных квадратов методами компьютерного зрения
3. **Анализ ориентации** - определение правильного положения по расположению квадратов (2 сверху, 4 снизу)
4. **Автоповорот** - автоматический поворот документа в правильную ориентацию
5. **Извлечение областей** - выделение L и R областей на основе квадратов-маркеров

## Настройка параметров

Основные параметры можно настроить через код:

- **Порог чувствительности**: `sensitivity` в `SquareDetector`
- **Размер квадратов**: `min_area` и `max_area` 
- **Допуск формы**: `aspect_ratio` диапазон
- **Отступы областей**: `padding` параметр

## Структура проекта

```
medical_doc_processor/
├── core/                 # Основные модули
│   ├── image_loader.py      # Загрузка файлов
│   ├── orientation_detector.py # Определение ориентации
│   ├── square_detector.py     # Детекция квадратов
│   └── region_extractor.py    # Извлечение областей
├── utils/                # Вспомогательные модули
│   ├── visualization.py      # Визуализация
│   └── file_utils.py        # Работа с файлами
└── cli.py               # CLI интерфейс
```

## Зависимости

- `opencv-python` - компьютерное зрение
- `numpy` - численные операции
- `Pillow` - работа с изображениями
- `PyMuPDF` - работа с PDF (опционально)
- `click` - CLI интерфейс

## Лицензия

MIT - свободное использование и модификация.