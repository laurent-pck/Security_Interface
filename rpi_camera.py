import config
import time
import io
import threading
import picamera
from singleton import Singleton


class Camera(metaclass=Singleton):
    thread = None # camera bg thread
    frame = None # current frame
    last_access = 0 # timestamp of last client access

    def initialize(self):
        """Start a new thread and wait for first frames"""
        if Camera.thread is None:
            # Start a bg camera thread
            Camera.thread = threading.Thread(target=Camera._thread)
            Camera.thread.start()

            # Wait until frames start to be available
            while self.frame is None:
                time.sleep(0)

    def get_frame(self):
        """Return a camera frame"""
        Camera.last_access = time.time()
        self.initialize()
        return Camera.frame

    @classmethod
    def _thread(cls):
        """Separate thread with continuous camera capture"""
        with picamera.PiCamera() as camera:
            # camera settings
            camera.resolution = (384, 216)
            camera.framerate = 24
            camera.hflip = False
            camera .vflip = False

            # start camera
            camera.start_preview()
            time.sleep(2)

            stream = io.BytesIO()
            for foo in camera.capture_continuous(
                stream,
                'jpeg',
                use_video_port=True
            ):
                # store frame
                stream.seek(0)
                cls.frame = stream.read()

                # reset stream for next capture
                stream.seek(0)
                stream.truncate()

                # if no clients asking for frames in last 10 secs, stop the thread
                if time.time() - cls.last_access > 10 and config.stop_detector:
                    break
        cls.thread = None
