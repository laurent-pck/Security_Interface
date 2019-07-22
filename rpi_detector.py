import config
import os
import threading
from datetime import datetime
from gpiozero import MotionSensor


class MovementDetector(threading.Thread):
    INPUT_PIN = 'GPIO4'
    LOG_DIR = 'var/log/'
    PICTURES_DIR = 'var/pictures/'
    TIMEOUT = 2

    camera = None

    def __init__(self, pi_camera):
        threading.Thread.__init__(self)
        self.camera = pi_camera

    def run(self):
        """Continuous movement detection"""
        sensor = MotionSensor(self.INPUT_PIN)

        while True:
            # wait for motion for maximum TIMEOUT seconds
            sensor.wait_for_motion(self.TIMEOUT)

            # check if the thread should stop
            if (config.stop_detector):
                return

            date = datetime.now().strftime('%Y-%m-%d')
            moment = datetime.now().strftime('%H:%M:%S:%f')
            logfile_path = self.LOG_DIR + date + '.log'
            logfile = open(logfile_path, 'a')
            logfile.write(date + ' ' + moment + " Movement detected!\n")
            pictures_dir_path = self.PICTURES_DIR + date
            if not os.path.isdir(pictures_dir_path):
                os.mkdir(pictures_dir_path)

            # Take five pictures if movement is detected
            for i in range(5):
                frame = self.camera.get_frame()
                moment = datetime.now().strftime('%H:%M:%S:%f')
                picture_file_path = pictures_dir_path + '/' + moment
                # Open file in binary mode to write frame
                picture_file = open(picture_file_path, 'wb')
                picture_file.write(frame)
