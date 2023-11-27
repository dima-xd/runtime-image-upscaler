import os
import subprocess
import threading
import zipfile
from queue import Queue
from sys import platform
from urllib.request import urlretrieve

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Upscale options #
models = ["realesrgan-x4plus", "realesrnet-x4plus", "realesrgan-x4plus-anime"]
scales = ["2", "3", "4"]

filename = "realesrgan"
url = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-"


class FolderListener(FileSystemEventHandler):
    def __init__(self, folder_to_listen, output_folder, file_queue):
        super().__init__()
        self.folder_to_listen = folder_to_listen
        self.output_folder = output_folder
        self.file_queue = file_queue

    def on_created(self, event):
        if not event.is_directory:
            print(f"Found new file: {event.src_path}")

            self.file_queue.put(event.src_path)


def run_realesrgan(file_queue, output_folder, model, scale):
    while True:
        file_path = file_queue.get()
        if file_path is None:
            break

        command = [
            "./" + filename + "/realesrgan-ncnn-vulkan",
            "-i", file_path,
            "-o", output_folder + os.path.basename(file_path),
            "-n", model,
            "-s", scale
        ]

        print(f"Trying to upscale: {file_path}")

        try:
            subprocess.run(command, check=True)
            print(f"Successfully upscaled: {file_path}")
        except subprocess.CalledProcessError as proc_err:
            print(f"Error executing command: {proc_err}")


def run():
    folder_to_listen = input("Choose folder to listen: ")
    output_folder = input("Choose output folder: ")

    print("Available models:")
    for i, model in enumerate(models, start=1):
        print(f"{i}. {model}")

    while True:
        try:
            model_index = int(input("Choose a model by index: "))
            if 1 <= model_index <= len(models):
                model_choice = models[model_index - 1]
                break
            else:
                print("Invalid index. Please choose from the available options.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    print("Available scales:")
    for i, scale in enumerate(scales, start=1):
        print(f"{i}. {scale}")

    while True:
        try:
            scale_index = int(input("Choose a scale by index: "))
            if 1 <= scale_index <= len(scales):
                scale_choice = scales[scale_index - 1]
                break
            else:
                print("Invalid index. Please choose from the available options.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    file_queue = Queue()

    event_handler = FolderListener(folder_to_listen, output_folder, file_queue)
    observer = Observer()
    observer.schedule(event_handler, path=folder_to_listen, recursive=True)
    observer.start()

    processing_thread = threading.Thread(target=run_realesrgan,
                                         args=(file_queue, output_folder, model_choice, scale_choice))
    processing_thread.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()

    file_queue.put(None)

    observer.join()
    processing_thread.join()


def download_and_extract():
    zip_filename = os.path.join(filename, filename + '.zip')

    urlretrieve(url, zip_filename)

    with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
        zip_ref.extractall(filename)

    os.remove(zip_filename)


if __name__ == '__main__':
    print("Using OS " + platform)

    if not os.path.exists(filename):
        os.makedirs(filename)

        if platform.startswith("win"):
            url += "windows.zip"
        if platform.startswith("linux"):
            url = "ubuntu.zip"
        elif platform.startswith("mac"):
            url = "macos.zip"

        try:
            download_and_extract()
            print("Downloaded and extracted successfully")

            run()

        except Exception as e:
            print(f"Error: {e}")

    else:
        run()
