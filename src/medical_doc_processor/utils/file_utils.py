import os
import glob
from typing import List, Optional


class FileUtils:
    """Утилиты для работы с файлами."""

    SUPPORTED_FORMATS = {'.pdf', '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}

    @classmethod
    def find_supported_files(cls, directory: str, recursive: bool = False) -> List[str]:
        """Находит поддерживаемые файлы в директории.

        Args:
            directory: Путь к директории
            recursive: Искать в поддиректориях

        Returns:
            List[str]: Список путей к файлам
        """
        if not os.path.exists(directory):
            return []

        pattern = "**/*" if recursive else "*"
        files = []

        for ext in cls.SUPPORTED_FORMATS:
            search_pattern = os.path.join(directory, pattern + ext)
            files.extend(glob.glob(search_pattern, recursive=recursive))

        return sorted(files)

    @classmethod
    def validate_file_path(cls, file_path: str) -> Optional[str]:
        """Проверяет валидность пути к файлу.

        Args:
            file_path: Путь к файлу

        Returns:
            Optional[str]: Сообщение об ошибке или None если все ок
        """
        if not os.path.exists(file_path):
            return f"Файл не существует: {file_path}"

        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in cls.SUPPORTED_FORMATS:
            return f"Неподдерживаемый формат файла: {file_ext}"

        return None

    @classmethod
    def get_file_info(cls, file_path: str) -> dict:
        """Возвращает информацию о файле.

        Args:
            file_path: Путь к файлу

        Returns:
            dict: Информация о файле
        """
        stat = os.stat(file_path)
        file_ext = os.path.splitext(file_path)[1].lower()

        return {
            'name': os.path.basename(file_path),
            'extension': file_ext,
            'size_bytes': stat.st_size,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'modified_time': stat.st_mtime
        }

    @classmethod
    def create_output_structure(cls, base_dir: str = "output") -> dict:
        """Создает структуру директорий для выходных файлов.

        Args:
            base_dir: Базовая директория

        Returns:
            dict: Пути к созданным директориям
        """
        dirs = {
            'base': base_dir,
            'regions': os.path.join(base_dir, 'regions'),
            'debug': os.path.join(base_dir, 'debug'),
            'results': os.path.join(base_dir, 'results')
        }

        for dir_path in dirs.values():
            os.makedirs(dir_path, exist_ok=True)

        return dirs
