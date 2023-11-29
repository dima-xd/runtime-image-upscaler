# runtime-image-upscaler

Watches a chosen directory for new image files and automatically sends them for upscaling.
Uses <a href="https://github.com/xinntao/Real-ESRGAN#portable-executable-files-ncnn">Real-ESRGAN</a> to upscale images.

Install dependencies:
```bash
    pip install realesrgan
    pip install watchdog
    pip install cv2
    
    # Install pytorch with CUDA support from - https://pytorch.org/
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```
