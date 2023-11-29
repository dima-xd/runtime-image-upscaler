import os
import threading
from queue import Queue

import cv2
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

models = {
    "realesrgan-x4plus": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth",
    "realesrgan-x4plus-anime": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4"
                               "/RealESRGAN_x4plus_anime_6B.pth"
}


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


def run_realesrgan(file_queue, output_folder, realesrganer):
    while True:
        file_path = file_queue.get()
        if file_path is None:
            break

        print(f"Trying to upscale: {file_path}")

        output, _ = realesrganer.enhance(cv2.imread(file_path, cv2.IMREAD_UNCHANGED))
        cv2.imwrite(output_folder + os.path.basename(file_path), output)

        print("Successfully upscaled")


def main():
    folder_to_listen = input("Choose folder to listen: ")
    output_folder = input("Choose output folder: ")

    models_to_choose = ["realesrgan-x4plus", "realesrgan-x4plus-anime"]

    print("Available models:")
    for i, model in enumerate(models_to_choose, start=1):
        print(f"{i}. {model}")

    while True:
        try:
            model_index = int(input("Choose a model by index: "))
            if 1 <= model_index <= len(models):
                model_choice = models[models_to_choose[model_index - 1]]
                break
            else:
                print("Invalid index. Please choose from the available options.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    RealESRGAN_models = {
        "realesrgan-x4plus": RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4),
        "realesrgan-x4plus_anime": RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=6, num_grow_ch=32,
                                           scale=4)
    }

    realesrganer = RealESRGANer(scale=4,
                                model_path=model_choice,
                                model=RealESRGAN_models[models_to_choose[model_index - 1]],
                                device="cuda")

    print("Ready to accept files")

    file_queue = Queue()

    event_handler = FolderListener(folder_to_listen, output_folder, file_queue)
    observer = Observer()
    observer.schedule(event_handler, path=folder_to_listen, recursive=True)
    observer.start()

    processing_thread = threading.Thread(target=run_realesrgan,
                                         args=(file_queue, output_folder, realesrganer))
    processing_thread.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()

    file_queue.put(None)

    observer.join()
    processing_thread.join()


if __name__ == '__main__':
    main()
