#!/usr/bin/env python3
"""CLI интерфейс для Medical Document Processor."""

import os
import click
from typing import List

from .core.region_extractor import RegionExtractor
from .utils.visualization import Visualization
from .utils.file_utils import FileUtils
from .core.image_loader import ImageLoader


@click.group()
@click.version_option()
def main():
    """Medical Document Processor - автоматическое определение ориентации и извлечение областей из медицинских документов."""
    pass


@main.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='output', 
              help='Директория для сохранения результатов')
@click.option('--debug', '-d', is_flag=True, help='Создать отладочные изображения')
def process(input_path: str, output_dir: str, debug: bool):
    """Обработать один файл."""
    try:
        # Создаем отладочное изображение если нужно
        if debug:
            visualizer = Visualization()
            visualizer.debug_lines(input_path, output_dir)
        
        # Обрабатываем файл
        extractor = RegionExtractor(output_dir)
        rotation_angle, results = extractor.process_medical_test(input_path)
        
        click.echo(click.style(f"✅ Обработка завершена!", fg='green'))
        click.echo(f"Угол поворота: {rotation_angle}°")
        click.echo(f"L область: {'✅' if results['L_region'] is not None else '❌'}")
        click.echo(f"R область: {'✅' if results['R_region'] is not None else '❌'}")
        
    except Exception as e:
        click.echo(click.style(f"❌ Ошибка: {e}", fg='red'))


@main.command()
@click.argument('input_dir', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='output', 
              help='Директория для сохранения результатов')
@click.option('--recursive', '-r', is_flag=True, help='Рекурсивный поиск файлов')
@click.option('--debug', '-d', is_flag=True, help='Создать отладочные изображения')
def batch(input_dir: str, output_dir: str, recursive: bool, debug: bool):
    """Обработать все файлы в директории."""
    # Находим файлы
    files = FileUtils.find_supported_files(input_dir, recursive)
    
    if not files:
        click.echo(click.style("❌ Не найдено поддерживаемых файлов", fg='yellow'))
        return
    
    click.echo(f"Найдено файлов: {len(files)}")
    
    # Обрабатываем каждый файл
    success_count = 0
    extractor = RegionExtractor(output_dir)
    visualizer = Visualization()
    
    for file_path in files:
        try:
            click.echo(f"\n📄 Обработка: {os.path.basename(file_path)}")
            
            # Создаем отладочное изображение если нужно
            if debug:
                visualizer.debug_lines(file_path, output_dir)
            
            # Обрабатываем файл
            rotation_angle, results = extractor.process_medical_test(file_path)
            
            click.echo(click.style(f"✅ Успешно - угол: {rotation_angle}°", fg='green'))
            success_count += 1
            
        except Exception as e:
            click.echo(click.style(f"❌ Ошибка: {e}", fg='red'))
    
    click.echo(f"\n📊 Итоги: {success_count}/{len(files)} файлов обработано успешно")


@main.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='output', 
              help='Директория для сохранения результатов')
def debug(input_path: str, output_dir: str):
    """Создать отладочное изображение с линиями квадратов."""
    try:
        visualizer = Visualization()
        line_info = visualizer.debug_lines(input_path, output_dir)
        
        click.echo(click.style("✅ Отладочное изображение создано", fg='green'))
        for y, count in line_info.items():
            click.echo(f"Линия y={y}: {count} квадратов")
            
    except Exception as e:
        click.echo(click.style(f"❌ Ошибка: {e}", fg='red'))


@main.command()
def info():
    """Показать информацию о поддерживаемых форматах."""
    image_loader = ImageLoader()
    formats = image_loader.get_supported_formats()
    
    click.echo("📁 Поддерживаемые форматы:")
    click.echo(f"📷 Изображения: {', '.join(formats['images'])}")
    if formats['pdf']:
        click.echo(f"📄 PDF: {', '.join(formats['pdf'])}")
    else:
        click.echo("📄 PDF: ❌ (требуется установка PyMuPDF)")


@main.command()
@click.argument('input_path', type=click.Path(exists=True))
def validate(input_path: str):
    """Проверить файл на возможность обработки."""
    error = FileUtils.validate_file_path(input_path)
    
    if error:
        click.echo(click.style(f"❌ {error}", fg='red'))
    else:
        file_info = FileUtils.get_file_info(input_path)
        click.echo(click.style("✅ Файл валиден", fg='green'))
        click.echo(f"Имя: {file_info['name']}")
        click.echo(f"Размер: {file_info['size_mb']} MB")
        click.echo(f"Формат: {file_info['extension']}")


if __name__ == '__main__':
    main()