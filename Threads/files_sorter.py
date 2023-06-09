import logging
import os
import shutil
from pathlib import Path
from threading import Thread


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


def normalize(name):
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


def handle_archives(file, path, type):
    logging.debug(f"Handling archive {file.name}")
    normalized_name = normalize(file.name)
    archive_name = normalized_name.split('.')[0]
    shutil.unpack_archive(f"{path}\\{file.name}",
                          f"{path}\\{type}\\{archive_name}")
    shutil.move(f"{path}\\{file.name}", f"{path}\\{type}\\{archive_name}")


def handle_files(file, path, type):
    logging.debug(f"Handling file {file.name}")
    normalized_name = normalize(file.name)
    shutil.move(f"{path}\\{file.name}",
                f"{path}\\{type}\\{normalized_name}")


def handle_folder(file, path):
    logging.debug(f"Handling folder {file.name}")
    if len(os.listdir(file)) == 0:
        os.rmdir(file)
    if file.name not in FILES_DATA and file.exists():
        normalized_name = normalize(file.name)
        os.rename(file, f"{path}\\{normalized_name}")
        new_folder_name = f"{path}\\{normalized_name}"
        sort_folder(new_folder_name)


def sort_folder(folder_path):
    path = Path(folder_path)
    threads = []

    for file in path.iterdir():

        for type in FILES_DATA:
            if file.name.split('.')[-1].lower() in FILES_DATA[type]:
                create_folder(path, type)
                if type == "archives":
                    thread = Thread(target=handle_archives,
                                    args=(file, path, type))
                else:
                    thread = Thread(target=handle_files,
                                    args=(file, path, type))
                thread.start()
                threads.append(thread)
        if file.is_dir():
            thread = Thread(target=handle_folder, args=(file, path))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG,
                        format='%(threadName)s %(asctime)s %(message)s')

    try:
        directory = input("Enter your folder destination: ")
        sort_folder(directory)
    except FileNotFoundError:
        print("This folder doesn't exist. Enter the correct path, please.")

    logging.debug("=====>>>> Folder has been sorted")
