from pathlib import Path
import uuid


ALLOWED_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.gif']
MAX_FILE_SIZE = 5 * 1024 * 1024


def is_allowed_file(filename: Path) -> bool:
    """ Проверка правильности расширения из списка ALLOWED_EXTENSIONS"""
    ext = filename.suffix.lower()
    return ext in ALLOWED_EXTENSIONS

def is_file_size(file_size: int) -> bool:
    """ Проверка размера файла с константой MAX_FILE_SIZE"""
    return file_size <= MAX_FILE_SIZE


def get_unique_filename(filename: Path) -> str:
    """ Создание уникального имени файла """
    ext = filename.suffix.lower()
    name = str(filename)[:str(filename).find('.')]
    unique_filename = name + "_" + uuid.uuid4().hex + ext
    return unique_filename


if __name__ == "__main__":
    name_file = "test.jpg"
    print(is_allowed_file(Path(name_file)))
    print(get_unique_filename(Path(name_file)))