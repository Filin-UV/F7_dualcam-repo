from picamera2 import Picamera2
from libcamera import controls
import numpy as np
import cv2
import threading
import time

# Инициализация камер
picam1 = Picamera2(0)  # Первая камера (CSI0)
picam2 = Picamera2(1)  # Вторая камера (CSI1)

# Настройка конфигурации для максимальной скорости (меньшее разрешение = выше FPS)
config1 = picam1.create_preview_configuration(
    main={"size": (640, 480), "format": "RGB888"},
    controls={"FrameRate": 60}
)
config2 = picam2.create_preview_configuration(
    main={"size": (640, 480), "format": "RGB888"},
    controls={"FrameRate": 60}
)

picam1.configure(config1)
picam2.configure(config2)

# Глобальные переменные для хранения последних кадров
frame1 = None
frame2 = None
lock = threading.Lock()

# Функция захвата кадров с первой камеры
def capture_cam1():
    global frame1
    picam1.start()
    while True:
        with lock:
            frame1 = picam1.capture_array("main")  # RGB формат

# Функция захвата кадров со второй камеры
def capture_cam2():
    global frame2
    picam2.start()
    while True:
        with lock:
            frame2 = picam2.capture_array("main")  # RGB формат

# Запуск потоков для камер
thread1 = threading.Thread(target=capture_cam1, daemon=True)
thread2 = threading.Thread(target=capture_cam2, daemon=True)
thread1.start()
thread2.start()

# Ждем, пока камеры начнут выдавать кадры
time.sleep(2)

# Основной цикл: наложение и вывод изображения
while True:
    if frame1 is not None and frame2 is not None:
        with lock:
            # Наложение двух изображений (50% прозрачности)
            blended = cv2.addWeighted(frame1, 0.5, frame2, 0.5, 0)
            cv2.imshow("Blended Cameras", blended)
    
    # Выход по нажатию 'q'
    if cv2.waitKey(1) == ord('q'):
        break

# Очистка
picam1.stop()
picam2.stop()
cv2.destroyAllWindows()