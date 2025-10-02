"""CLI интерфейс для Medical Document Processor."""

import os
import click
import time
from typing import Optional

from .core.region_extractor import RegionExtractor
from .utils.visualization import Visualization
from .utils.file_utils import FileUtils
from .core.image_loader import ImageLoader


@click.group()
@click.version_option()
def main():
    """Medical Document Processor - автоматическое определение ориентации и извлечение областей."""
    pass


@main.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='output',
              help='Директория для сохранения результатов')
@click.option('--debug', '-d', is_flag=True, help='Создать отладочные изображения')
@click.option('--workers', default=2, help='Количество потоков для параллельной обработки')
def process(input_path: str, output_dir: str, debug: bool, workers: int):
    """Обработать один файл."""
    try:
        start_time = time.time()
        
        # Создаем отладочное изображение если нужно
        if debug:
            visualizer = Visualization()
            visualizer.debug_lines(input_path, output_dir)
        
        # Создаем обработчик
        extractor = RegionExtractor(output_dir, max_workers=workers)
        click.echo(f"Используется {workers} потоков для обработки")
        
        # Обрабатываем файл
        rotation_angle, results = extractor.process_medical_test(input_path)
        
        processing_time = time.time() - start_time
        
        click.echo(click.style("[OK] Обработка завершена!", fg='green'))
        click.echo(f"Время обработки: {processing_time:.2f} секунд")
        click.echo(f"Угол поворота: {rotation_angle}°")
        click.echo(f"L область: {'[OK]' if results['L_region'] is not None else '[FAIL]'}")
        click.echo(f"R область: {'[OK]' if results['R_region'] is not None else '[FAIL]'}")
        
    except Exception as e:
        click.echo(click.style(f"[ERROR] Ошибка: {e}", fg='red'))


@main.command()
@click.argument('input_dir', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='output',
              help='Директория для сохранения результатов')
@click.option('--recursive', '-r', is_flag=True, help='Рекурсивный поиск файлов')
@click.option('--debug', '-d', is_flag=True, help='Создать отладочные изображения')
@click.option('--workers', default=2, help='Количество потоков для параллельной обработки')
def batch(input_dir: str, output_dir: str, recursive: bool, debug: bool, workers: int):
    """Обработать все файлы в директории."""
    # Находим файлы
    files = FileUtils.find_supported_files(input_dir, recursive)
    
    if not files:
        click.echo(click.style("[WARN] Не найдено поддерживаемых файлов", fg='yellow'))
        return
    
    click.echo(f"Найдено файлов: {len(files)}")
    
    # Создаем обработчик
    extractor = RegionExtractor(output_dir, max_workers=workers)
    click.echo(f"Используется {workers} потоков для обработки")
    
    visualizer = Visualization()
    
    # Обрабатываем каждый файл
    success_count = 0
    total_time = 0
    
    for i, file_path in enumerate(files, 1):
        try:
            file_start_time = time.time()
            click.echo(f"\n[{i}/{len(files)}] Обработка: {os.path.basename(file_path)}")
            
            # Создаем отладочное изображение если нужно
            if debug:
                visualizer.debug_lines(file_path, output_dir)
            
            # Обрабатываем файл
            rotation_angle, results = extractor.process_medical_test(file_path)
            
            file_time = time.time() - file_start_time
            total_time += file_time
            
            click.echo(click.style(f"[OK] Успешно - угол: {rotation_angle}° ({file_time:.2f}с)", fg='green'))
            success_count += 1
            
        except Exception as e:
            click.echo(click.style(f"[ERROR] Ошибка: {e}", fg='red'))
    
    avg_time = total_time / len(files) if files else 0
    click.echo(f"\n[SUMMARY] Итоги:")
    click.echo(f"Обработано успешно: {success_count}/{len(files)} файлов")
    click.echo(f"Общее время: {total_time:.2f} секунд")
    click.echo(f"Среднее время на файл: {avg_time:.2f} секунд")


@main.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='output',
              help='Директория для сохранения результатов')
def debug(input_path: str, output_dir: str):
    """Создать отладочное изображение с линиями квадратов."""
    try:
        visualizer = Visualization()
        line_info = visualizer.debug_lines(input_path, output_dir)
        
        click.echo(click.style("[OK] Отладочное изображение создано", fg='green'))
        for y, count in line_info.items():
            click.echo(f"Линия y={y}: {count} квадратов")
            
    except Exception as e:
        click.echo(click.style(f"[ERROR] Ошибка: {e}", fg='red'))


@main.command()
def info():
    """Показать информацию о поддерживаемых форматах."""
    image_loader = ImageLoader()
    formats = image_loader.get_supported_formats()
    
    click.echo("[INFO] Поддерживаемые форматы:")
    click.echo(f"Изображения: {', '.join(formats['images'])}")
    if formats['pdf']:
        click.echo(f"PDF: {', '.join(formats['pdf'])}")
    else:
        click.echo("PDF: [NOT AVAILABLE] (требуется установка PyMuPDF)")


@main.command()
@click.argument('input_path', type=click.Path(exists=True))
def validate(input_path: str):
    """Проверить файл на возможность обработки."""
    error = FileUtils.validate_file_path(input_path)
    
    if error:
        click.echo(click.style(f"[ERROR] {error}", fg='red'))
    else:
        file_info = FileUtils.get_file_info(input_path)
        click.echo(click.style("[OK] Файл валиден", fg='green'))
        click.echo(f"Имя: {file_info['name']}")
        click.echo(f"Размер: {file_info['size_mb']} MB")
        click.echo(f"Формат: {file_info['extension']}")


@main.command()
@click.option('--output-dir', '-o', default='generated_documents',
              help='Директория для сохранения сгенерированных документов')
@click.option('--count', '-c', default=1, help='Количество документов для генерации')
@click.option('--width', default=2339, help='Ширина документа (альбомная A4, 200 DPI)')
@click.option('--height', default=1654, help='Высота документа (альбомная A4, 200 DPI)')
@click.option('--probe-number', default='1', help='Номер пробы')
@click.option('--exercise', default=None, help='Название упражнения')
@click.option('--l-time', default='', help='Время для левой спирали')
@click.option('--r-time', default='', help='Время для правой спирали')
@click.option('--language', '-l', default='ru', type=click.Choice(['ru', 'en']),
              help='Язык документа (ru/en)')
@click.option('--dpi', default=200, type=click.Choice([150, 200, 300]),
              help='Разрешение документа (150/200/300 DPI)')
def generate(output_dir: str, count: int, width: int, height: int,
             probe_number: str, exercise: str, l_time: str, r_time: str,
             language: str, dpi: int):
    """Сгенерировать тестовые документы со спиралями в альбомной ориентации"""
    try:
        from .generators.spiral_document_generator import SpiralDocumentGenerator
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Автоматически устанавливаем размеры по DPI
        if dpi == 150:
            width, height = 1754, 1240  # A4 альбомная 150 DPI
        elif dpi == 200:
            width, height = 2339, 1654  # A4 альбомная 200 DPI (по умолчанию)
        else:  # 300 DPI
            width, height = 3508, 2480  # A4 альбомная 300 DPI
        
        if count == 1:
            generator = SpiralDocumentGenerator(width, height, language)
            output_path = os.path.join(output_dir, f"spiral_document_{language}_{dpi}dpi.jpg")
            
            generator.generate_document(
                output_path,
                probe_number=probe_number,
                exercise=exercise
            )
            click.echo(f"[OK] Документ создан ({language}, {dpi} DPI): {output_path}")
        else:
            click.echo("[INFO] Пакетная генерация пока не реализована")
            
    except Exception as e:
        click.echo(f"[ERROR] Ошибка генерации: {e}")


@main.command()
@click.option('--input-path', required=True, help='Путь к файлу для тестирования')
@click.option('--iterations', default=5, help='Количество итераций для тестирования')
def benchmark(input_path: str, iterations: int):
    """Тестирование производительности с кэшированием и без."""
    if not os.path.exists(input_path):
        click.echo(click.style(f"[ERROR] Файл не найден: {input_path}", fg='red'))
        return
    
    click.echo(f"Тестирование производительности на {iterations} итерациях...")
    
    # Тестируем без кэширования
    no_cache_times = []
    
    click.echo("Тестирование без кэширования...")
    for i in range(iterations):
        start_time = time.time()
        extractor = RegionExtractor("benchmark_output", max_workers=1)
        extractor.square_detector.clear_cache()  # Очищаем кэш
        extractor.process_medical_test(input_path)
        no_cache_times.append(time.time() - start_time)
        click.echo(f"Итерация {i + 1}: {no_cache_times[-1]:.2f}с")
    
    # Тестируем с кэшированием
    cached_times = []
    
    click.echo("Тестирование с кэшированием...")
    extractor = RegionExtractor("benchmark_output", max_workers=2)
    for i in range(iterations):
        start_time = time.time()
        extractor.process_medical_test(input_path)
        cached_times.append(time.time() - start_time)
        click.echo(f"Итерация {i + 1}: {cached_times[-1]:.2f}с")
    
    # Результаты
    avg_no_cache = sum(no_cache_times) / len(no_cache_times)
    avg_cached = sum(cached_times) / len(cached_times)
    improvement = ((avg_no_cache - avg_cached) / avg_no_cache) * 100
    
    click.echo(f"\n[RESULTS] Результаты тестирования:")
    click.echo(f"Без кэширования: {avg_no_cache:.2f}с (среднее)")
    click.echo(f"С кэшированием: {avg_cached:.2f}с (среднее)")
    click.echo(f"Улучшение: {improvement:.1f}%")


if __name__ == '__main__':
    main()
