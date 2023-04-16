import logging
import os
import shutil
from pathlib import Path
from threading import Thread, RLock


FILES_DATA = {
    "audio": ['mp3', 'ogg', 'wav', 'amr'],
    "documents": ['doc', 'txt', 'pdf', 'xlsx', 'pptx', 'docx'],
    "images": ['jpeg', 'jpg', 'svg', 'png', 'bmp'],
    "archives": ['zip', 'gz', 'tar'],
    "video": ['avi', 'mp4', 'mov', 'mkv'],
}

CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")

TRANS = {}

for a, b in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(a)] = b
    TRANS[ord(a.upper())] = b.upper()

logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(asctime)s %(message)s')
lock = RLock()


def normalize(name):
    logging.debug(f"Normalizing {name}")
    if len(name.split('.')) == 1:
        prefix = list(name)
        format = ''
    else:
        dot_idx = name.rindex('.')
        prefix = list(name[:dot_idx])
        format = name[dot_idx: len(name)]

    for idx, letter in enumerate(prefix):
        char = ord(letter)

        if char in TRANS:
            prefix[idx] = TRANS[char]
        elif not letter.isnumeric() and char not in range(65, 91) and char not in range(97, 123):
            prefix[idx] = '_'

    return f'{"".join(prefix)}{format}'


def create_folder(path, name):
    os.makedirs(f"{path}\\{name}", exist_ok=True)


def handle_archives(file, path, type, locker):
    with locker:
        logging.debug(f"Handling archive {file.name}")
        normalized_name = normalize(file.name)
        archive_name = normalized_name.split('.')[0]
        shutil.unpack_archive(f"{path}\\{file.name}",
                                f"{path}\\{type}\\{archive_name}")
        shutil.move(f"{path}\\{file.name}", f"{path}\\{type}\\{archive_name}")


def handle_files(file, path, type, locker):
    with locker:
        logging.debug(f"Handling file {file.name}")
        normalized_name = normalize(file.name)
        shutil.move(f"{path}\\{file.name}",
                    f"{path}\\{type}\\{normalized_name}")


def handle_folder(file, path, locker):
    with locker:
        logging.debug(f"Handling folder {file.name}")
        if len(os.listdir(file)) == 0:
            os.rmdir(file)
        if file.name not in FILES_DATA and file.exists():
            normalized_name = normalize(file.name)
            os.rename(file, f"{path}\\{normalized_name}")
            new_folder_name =  f"{path}\\{normalized_name}"
            sort_folder(new_folder_name)


def launchThread(worker, file, path, type, locker):
    if worker.__name__ == "handle_folder":
        thread = Thread(target=worker, args=(file, path, locker))
    else:
        thread = Thread(target=worker, args=(file, path, type, locker))
    thread.start()


def sort_folder(folder_path):
    path = Path(folder_path)

    for file in path.iterdir():

        for type in FILES_DATA:
            if file.name.split('.')[-1].lower() in FILES_DATA[type]:
                create_folder(path, type)  # here should be a thread launched
                if type == "archives":
                    launchThread(handle_archives, file, path, type, lock)
                    # handle_archives(file, path, type)
                else:
                    launchThread(handle_files, file, path, type, lock)
                    # handle_files(file, path, type)
        if file.is_dir():
            launchThread(handle_folder, file, path, type, lock)
            # handle_folder(file, path)


try:
    directory = input("Enter your folder destination: ")
    sort_folder(directory)
except FileNotFoundError:
    print("This folder doesn't exist. Enter the correct path, please.")

logging.debug("=====>>>> Main thread finished")