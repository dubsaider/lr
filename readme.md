# Medical Document Processor

Автоматическое определение ориентации и извлечение областей из медицинских документов.

## Что делает проект

1. **Автоматическое определение ориентации** - анализирует расположение черных квадратов-маркеров (2 сверху, 4 снизу) и автоматически поворачивает документ в правильную ориентацию
2. **Извлечение областей** - находит L и R области на основе расположения квадратов-маркеров
3. **Генерация тестовых документов** - создает медицинские тесты со спиралями Архимеда с поддержкой русского и английского языков
4. **Поддержкa разных форматов** - работает с PDF и изображениями (JPG, PNG, TIFF, BMP)
5. **Визуализация** - создает отладочные изображения для анализа процесса

## Установка

### Из репозитория GitHub
```bash
pip install git+https://github.com/dubsaider/lr.git
```

### Для разработки
```bash
git clone https://github.com/dubsaider/lr.git
cd lr
pip install -e ".[dev]"
```

## Быстрый старт

### Через CLI
```bash
# Обработать один файл
medical-doc-processor process document.pdf

# С отладочной информацией
medical-doc-processor process scan.jpg --debug --output-dir results

# Обработать все файлы в папке
medical-doc-processor batch ./scans --recursive
```

### Через Python
```python
from medical_doc_processor import process_medical_test, debug_lines, SpiralDocumentGenerator

# Обработка документа
rotation_angle = process_medical_test("document.pdf", output_dir="results")

# Отладочная визуализация
debug_lines("document.pdf", output_dir="debug")

# Генерация тестового документа со спиралями Архимеда
generator = SpiralDocumentGenerator(width=2339, height=1654, language="ru")
generator.generate_document(
    output_path="test_spiral_ru.jpg",
    probe_number="1",
    exercise="Спирали Архимеда"
)
```

## Использование CLI

### Обработка одного файла
```bash
medical-doc-processor process input.pdf --output-dir results --debug
```

### Пакетная обработка
```bash
medical-doc-processor batch ./input_scans --recursive --output-dir ./output
```

### Отладочная информация
```bash
medical-doc-processor debug document.pdf
```

### Проверка файла
```bash
medical-doc-processor validate image.png
```

### Информация о форматах
```bash
medical-doc-processor info
```

### Генерация тестовых документов
```bash
# Сгенерировать документ со спиралями Архимеда (русский, 200 DPI)
medical-doc-processor generate --output-dir generated_documents --language ru --count 1

# Сгенерировать английскую версию в 300 DPI
medical-doc-processor generate --output-dir docs --language en --dpi 300 --count 1

# Сгенерировать с номером пробы
medical-doc-processor generate --output-dir output --probe-number 5 --language ru
```

## Тестирование

### Структура тестов
```
tests/
├── data/                 # Исходные тестовые данные
│   └── document.jpg      # Тестовый документ
├── generated/            # Автогенерируемые изображения
│   ├── original.jpg      # Исходная ориентация
│   ├── rotated_90.jpg    # Поворот 90°
│   ├── rotated_180.jpg   # Поворот 180°
│   └── rotated_270.jpg   # Поворот 270°
└── output/               # Результаты тестов
    ├── visual_report/    # Визуальные отчеты
    ├── simple_report/    # Упрощенные отчеты
    └── minimal/          # Минимальная визуализация
```

### Подготовка тестовой среды

1. **Поместите тестовый документ:**
   ```bash
   # Скопируйте document.jpg в tests/data/
   cp document.jpg tests/data/
   ```

2. **Создайте тестовые изображения:**
   ```bash
   # Создаст 4 варианта ориентации
   python tests/create_test_images.py
   ```

3. Пропустите шаги подготовки, визуальные артефакты генерируются на лету тестами.

### Запуск тестов

#### Полный тестовый прогон
```bash
# Автоматически создаст изображения и запустит все тесты
python tests/run_tests.py
```

#### Отдельные тесты
```bash
# Основные тесты ориентации
python -m pytest tests/test_orientation_detector.py -v
```

#### Создание визуальных отчетов
```bash
# Подробный визуальный отчет
python tests/test_visual_validation.py
```

### Тестирование всех ориентаций

Проект автоматически тестирует 4 варианта ориентации:
- **original.jpg** - исходная ориентация
- **rotated_90.jpg** - поворот 90° по часовой
- **rotated_180.jpg** - поворот 180°
- **rotated_270.jpg** - поворот 270°

### Проверка результатов

После запуска тестов проверьте:
1. **Количество квадратов** - должно быть одинаковым во всех ориентациях
2. **Определенная ориентация** - должна соответствовать ожидаемой
3. **Визуальные отчеты** - в папке `tests/output/`

## Результаты обработки

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

## Отладка проблем

### Проблемы с зависимостями
```bash
# Переустановка dev зависимостей
pip install -e ".[dev]"

# Ручная установка тестовых зависимостей
pip install pytest pytest-cov
```

### Проблемы с тестовыми изображениями
```bash
# Принудительное пересоздание
python tests/create_test_images.py

# Проверка существования файлов
python tests/prepare_tests.py
```

## Настройка параметров

Основные параметры можно настроить через код:

- **Порог чувствительности**: `sensitivity` в `SquareDetector`
- **Размер квадратов**: `min_area` и `max_area` 
- **Допуск формы**: `aspect_ratio` диапазон
- **Отступы областей**: `padding` параметр

## Генерация тестовых документов

### Возможности генератора

Проект включает мощный генератор медицинских тестовых документов со спиралями Архимеда:

- **Двуязычность**: поддержка русского и английского языков
- **Разные разрешения**: 150, 200, 300 DPI
- **Адаптивная верстка**: автоматическое масштабирование под разные размеры
- **Маркеры ориентации**: черные квадраты для определения ориентации
- **Настраиваемые параметры**: номер пробы, название упражнения

### Структура документа

Каждый сгенерированный документ содержит:

1. **Шапка**: название теста, номер пробы, дата
2. **Две спирали Архимеда**: левая (L) и правая (R) с маркерами ориентации
3. **Блоки для записи времени**: "Время Л _______ сек" и "Время П _______ сек"
4. **Инструкции**: 5 пунктов с руководством по выполнению теста

### Примеры использования

#### Через CLI
```bash
# Базовая генерация (русский, 200 DPI)
medical-doc-processor generate --output-dir docs --language ru --count 1

# Высокое разрешение для печати
medical-doc-processor generate --output-dir print --dpi 300 --language en

# С кастомными параметрами
medical-doc-processor generate \
  --output-dir output \
  --language ru \
  --probe-number 3 \
  --exercise "Тест координации" \
  --dpi 200
```

#### Через Python API
```python
from medical_doc_processor import SpiralDocumentGenerator

# Создание генератора
generator = SpiralDocumentGenerator(
    width=2339,    # Ширина в пикселях (A4 landscape @ 200 DPI)
    height=1654,   # Высота в пикселях
    language="ru"  # Язык: "ru" или "en"
)

# Генерация документа
generator.generate_document(
    output_path="spiral_test.jpg",
    probe_number="1",
    exercise="Спирали Архимеда"
)

# Изменение языка
generator.set_language("en")
generator.generate_document("spiral_test_en.jpg", probe_number="1")
```

### Параметры команды generate

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `--output-dir` | Директория для сохранения | `generated_documents` |
| `--count` | Количество документов | `1` |
| `--language` | Язык (ru/en) | `ru` |
| `--dpi` | Разрешение (150/200/300) | `200` |
| `--probe-number` | Номер пробы | `1` |
| `--exercise` | Название упражнения | "Спирали Архимеда" |

### Размеры документов по DPI

- **150 DPI**: 1754×1240 px (для экранного просмотра)
- **200 DPI**: 2339×1654 px (стандартное качество)
- **300 DPI**: 3508×2480 px (высокое качество для печати)

Все размеры соответствуют формату A4 в альбомной ориентации.

## Структура проекта

```
medical_doc_processor/
├── core/                    # Основные модули
│   ├── image_loader.py         # Загрузка файлов
│   ├── orientation_detector.py # Определение ориентации
│   ├── square_detector.py      # Детекция квадратов
│   ├── region_extractor.py     # Извлечение областей
│   └── spiral_generator.py     # Генератор спиралей Архимеда
├── generators/              # Генераторы документов
│   └── spiral_document_generator.py # Генератор тестовых документов
├── components/              # Компоненты документов
│   └── document_components.py   # Компоненты (шапка, инструкции, и т.д.)
├── utils/                   # Вспомогательные модули
│   ├── visualization.py         # Визуализация
│   ├── file_utils.py           # Работа с файлами
│   └── text_utils.py           # Работа с текстом и мультиязычность
└── cli.py                   # CLI интерфейс
```

## Зависимости

- `opencv-python` - компьютерное зрение
- `numpy` - численные операции
- `Pillow` - работа с изображениями
- `PyMuPDF` - работа с PDF (опционально)
- `click` - CLI интерфейс

### Тестовые зависимости
- `pytest` - фреймворк тестирования
- `pytest-cov` - покрытие кода
- `black` - форматирование кода
- `flake8` - линтинг

## Лицензия

MIT - свободное использование и модификация.
