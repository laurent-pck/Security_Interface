from flask import Flask, render_template, Response, request
from rpi_detector import MovementDetector
import config
import datetime


app = Flask(__name__)

if __name__ == '__main__':
    app.run(host='0.0.0.0')

@app.route('/')
def hello_world():
    """Home page"""
    date = datetime.datetime.now()
    return 'Hello, World! The actual time is: '+str(date)

@app.route('/camera')
def camera_show():
    """Video streaming page"""
    return render_template('camera.html')

def stream_gen(camera):
    """Video streaming generator function"""
    while True:
        frame = camera.get_frame()
        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
        )

@app.route('/camera_stream')
def camera_stream():
    """Video streaming route"""
    resp = Response(
        stream_gen(config.pi_camera),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )
    # Tell nginx not to buffer the response, otherwise it will close
    # connection to backend prematurely and stop the stream.
    resp.headers['X-Accel-Buffering'] = 'no'

    return resp

@app.route('/cockpit', methods=['GET', 'POST'])
def cockpit():
    """Cockpit page to control system state and watch (ON/OFF)"""
    if request.method == "POST":
        if request.form['state'] == '1':
            config.stop_detector = False
            # activate movement detector thread
            movement_thread = MovementDetector(config.pi_camera)
            movement_thread.start()
            return 'Started'
        else:
            # stop movement detector thread if needed
            config.stop_detector = True
            return 'Stopped'
    else:
        return render_template('cockpit.html')
