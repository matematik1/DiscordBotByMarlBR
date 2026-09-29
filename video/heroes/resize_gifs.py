import os
from PIL import Image, ImageSequence

# Розмір, до якого зменшуємо
TARGET_SIZE = (200, 200)

# Беремо папку, в якій лежить цей скрипт
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

gif_files = [
    f for f in os.listdir(CURRENT_DIR) 
    if f.lower().endswith(".gif") and not f.startswith("temp_")
]
total = len(gif_files)

print(f"Знайдено {total} GIF-файлів у папці: {CURRENT_DIR}")
print(f"Починаємо стиснення до {TARGET_SIZE[0]}x{TARGET_SIZE[1]} із перезаписом...\n")

for idx, filename in enumerate(gif_files, start=1):
    file_path = os.path.join(CURRENT_DIR, filename)
    temp_path = os.path.join(CURRENT_DIR, f"temp_{filename}")

    try:
        with Image.open(file_path) as im:
            frames = []
            durations = []
            disposals = []
            loop = im.info.get("loop", 0)

            for frame in ImageSequence.Iterator(im):
                durations.append(frame.info.get("duration", 100))
                disposals.append(frame.info.get("disposal", 2))

                # Конвертуємо в RGBA для збереження прозорості та якості
                frame_rgba = frame.convert("RGBA")
                resized_frame = frame_rgba.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
                frames.append(resized_frame)

            if frames:
                # Спочатку зберігаємо у тимчасовий файл
                frames[0].save(
                    temp_path,
                    save_all=True,
                    append_images=frames[1:],
                    optimize=True,
                    duration=durations,
                    loop=loop,
                    disposal=disposals
                )

        # Перезаписуємо оригінальний файл новим
        os.replace(temp_path, file_path)
        print(f"[{idx}/{total}] Перезаписано: {filename}")

    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        print(f"[{idx}/{total}] ❌ Помилка з {filename}: {e}")

print("\nГотово! Усі файли оновлено до 200x200 з оригінальними назвами.")