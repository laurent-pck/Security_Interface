from rpi_camera import Camera

# Global variable to control detector thread ending
stop_detector = True

# Global camera object that will be available for the detector thread
pi_camera = Camera()
