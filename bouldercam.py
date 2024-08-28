import cv2
import numpy as np
from picamera2 import Picamera2
from collections import deque
import time
import threading

BUFFER_SECONDS = 30
FPS = 30
BUFFER_SIZE = BUFFER_SECONDS * FPS

picam2 = Picamera2()
config = picam2.create_video_configuration(main={"size": (1920, 1080), "format": "RGB888"})
picam2.configure(config)
picam2.start()

stop_event = threading.Event()
buffer = deque(maxlen=BUFFER_SIZE)

def get_frames():
	while not stop_event.is_set():
		start_time = time.time()

		frame = picam2.capture_array()
		buffer.append(frame)

		elapsed_time = time.time() - start_time
		sleep_time = max(0, 1/FPS - elapsed_time)
		time.sleep(sleep_time)

thread = threading.Thread(target=get_frames)
thread.start()

cv2.namedWindow("BoulderCam", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("BoulderCam", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

try:
	while not stop_event.is_set():
		if len(buffer) == BUFFER_SIZE:
			start_time = time.time()
			frame = buffer.popleft()
			cv2.imshow('BoulderCam', frame)
			
			elapsed_time = time.time() - start_time
			sleep_time = max(0.001, 1/FPS - elapsed_time)

			if cv2.waitKey(int(1000 * sleep_time)) & 0xFF == ord('q'):
				break
	stop_event.set()
except KeyboardInterrupt:
	stop_event.set()

thread.join()
picam2.stop()
cv2.destroyAllWindows()
