from enum import Enum
import os
import subprocess
import time
import threading

from flask import Flask, render_template, request, jsonify, redirect, url_for
import RPi.GPIO as GPIO
import vlc

app = Flask(__name__)

movie_path = "/home/pi/Videos/Barbie.mp4"
movie_status = "stopped"
movie_position = 0
# number of seconds to jump forward/backward
jump_time = 300

# Set GPIO mode and pin number
GPIO.setmode(GPIO.BCM)

backlight_pin = 18  # Replace with the actual backlight pin number

# Define the GPIO pins for Red, Green, and Blue led
red_pin = 21
green_pin = 16
blue_pin = 20

# Set up PWM for backlight
GPIO.setup(backlight_pin, GPIO.OUT)
GPIO.output(backlight_pin, GPIO.LOW)

player = None
rgb_led = None

# wrapper for vlc players
class Player:
    # based on https://stackoverflow.com/a/75996857
    def __init__(self):
        self.player = vlc.Instance()

    def addPlayList(self, localPath):
        self.mediaList = self.player.media_list_new()
        path = os.path.join(os.getcwd(), localPath)
        self.mediaList.add_media(path)
        self.listPlayer = self.player.media_list_player_new()
        self.listPlayer.set_media_list(self.mediaList)
        # make this loop
        self.listPlayer.set_playback_mode(vlc.PlaybackMode(1))
        self.media_player = self.listPlayer.get_media_player()
        self.media_player.set_fullscreen(True)

    def play(self):
        self.listPlayer.play()

    def stop(self):
        self.listPlayer.stop()

    def pause(self):
        self.listPlayer.pause()

    def jump_movie_time(self, delta):
        # move forward by delta seconds
        self.media_player.set_time(self.media_player.get_time() + delta * 1000)

    def seek_movie_time(self, time):
        # time in seconds
        self.media_player.set_time(time * 1000)


class RGBLed:
    def __init__(self, red_pin, green_pin, blue_pin, filename):
        # Set the GPIO mode and warnings
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        self.red_pin = red_pin
        self.green_pin = green_pin
        self.blue_pin = blue_pin

        # Set up the GPIO pins as outputs
        GPIO.setup(red_pin, GPIO.OUT)
        GPIO.setup(green_pin, GPIO.OUT)
        GPIO.setup(blue_pin, GPIO.OUT)

        # set up PWM
        self.red_pwm = GPIO.PWM(red_pin, 100)  
        self.green_pwm = GPIO.PWM(green_pin, 100)
        self.blue_pwm = GPIO.PWM(blue_pin, 100)

        # rgb values
        self.red = 0
        self.green = 0
        self.blue = 0

        # file in which rgb values are stored
        self.filename = filename

        # check if file exists, if not, write out a default file
        if not os.path.exists(self.filename):
            self.set_color(100, 100, 100)
            self.save_state()
        else:
            self.load_state()

        self.red_pwm.start(0)  # Start PWM with 0% duty cycle
        self.green_pwm.start(0)
        self.blue_pwm.start(0)
        self.turn_on()

    def set_color(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue

        self.red_pwm.ChangeDutyCycle(red)
        self.green_pwm.ChangeDutyCycle(green)
        self.blue_pwm.ChangeDutyCycle(blue)

    def turn_on(self):
        print(f"Setting rgb {self.red},{self.green},{self.blue}")
        self.set_color(self.red, self.green, self.blue)

    def turn_off(self):
        self.red_pwm.ChangeDutyCycle(0)
        self.green_pwm.ChangeDutyCycle(0)
        self.blue_pwm.ChangeDutyCycle(0)

    def save_state(self):
        # Open the file in write mode and save RGB values
        print("Saving rgb led state")
        with open(self.filename, 'w') as file:
            file.write(f"{self.red},{self.green},{self.blue}")

    def load_state(self):
        # Open the file in read mode and retrieve RGB values
        with open(self.filename, 'r') as file:
            rgb_values = file.read().split(',')
            self.red = int(rgb_values[0])
            self.green = int(rgb_values[1])
            self.blue = int(rgb_values[2])

    def __del__(self):
        self.red_pwm.stop()
        self.green_pwm.stop()
        self.blue_pwm.stop()

def control_backlight(state):
    if state == "on":
        GPIO.output(backlight_pin, GPIO.HIGH)
    elif state == "off":
        GPIO.output(backlight_pin, GPIO.LOW)

def turn_on_display():
    control_backlight("on")
    activated = False

# play the movie from the start
def play_movie():
    global movie_status
    #player.set_media(media)
    
    player.seek_movie_time(0)
    player.play()
    turn_on_screen_after_delay(0.75)
    rgb_led.turn_on()

    movie_status = "playing"

def load_movie():
    global movie_status
    # loop forever
    player.set_media(media)
    movie_status = "playing"

# pause/resume the movie
def pause_resume_movie():
    global movie_status
    player.pause()
    if movie_status == "playing":
        movie_status = "paused"
    elif movie_status == "paused":
        movie_status = "playing"
    elif movie_status == "stopped":
        control_backlight("on")
        rgb_led.turn_on()
        movie_status = "playing"

def stop_movie():
    global movie_status
    #player.stop()
    if movie_status == "playing":
        player.pause()

    control_backlight("off")
    rgb_led.turn_off()
    movie_status = "stopped"

def get_movie_status():
    return movie_status

activated = False  # Flag to track activation

def turn_on_screen_after_delay(delay):
    global activated
    # Create a Timer to execute the callback function after the specified delay
    timer = threading.Timer(delay, turn_on_display)
    timer.start()
    activated = True  # Set flag to indicate activation

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/play')
def play():
    play_movie()
    return jsonify({"status": get_movie_status()})

@app.route('/pause')
def pause():
    pause_resume_movie()
    return jsonify({"status": get_movie_status()})

@app.route('/stop')
def stop():
    stop_movie()
    return jsonify({"status": get_movie_status()})


@app.route('/status')
def status():
    return jsonify({"status": get_movie_status()})

@app.route('/jump-forward')
def jump_forward():
    player.jump_movie_time(jump_time)
    return jsonify({"status": get_movie_status()})

@app.route('/jump-backward')
def jump_backward():
    player.jump_movie_time(-jump_time)
    return jsonify({"status": get_movie_status()})

@app.route('/settings', methods=['GET', 'POST'])
def light():
    print(f"red={rgb_led.red}, green={rgb_led.green}, blue={rgb_led.blue}")
    if request.method == 'POST':
        red = int(request.form['red'])
        green = int(request.form['green'])
        blue = int(request.form['blue'])
        rgb_led.set_color(red, green, blue)

        if request.form['action'] == 'light-default':  # Check if "Set Default" button is clicked
            print("set default registered")
            rgb_led.save_state()

        return render_template('settings.html', red=rgb_led.red, green=rgb_led.green, blue=rgb_led.blue)
    return render_template('settings.html', red=rgb_led.red, green=rgb_led.green, blue=rgb_led.blue)

@app.route('/restart', methods=['POST'])
def restart():
    if request.method == 'POST':
        os.system("sudo shutdown -r now")  # Restart command
        return "Restarting device..."
    return "Invalid request method"

@app.route('/shutdown', methods=['POST'])
def shutdown():
    if request.method == 'POST':
        os.system("sudo shutdown now")  # Shutdown command
        return "Shutting down device..."
    return "Invalid request method"

if __name__ == '__main__':
    os.environ["DISPLAY"] = ":0"
    player = Player()
    player.addPlayList("/home/pi/Videos/Barbie.mp4")
    rgb_led = RGBLed(red_pin, green_pin, blue_pin, 'rgb_values.txt')
    play_movie()

    app.run(host='0.0.0.0', port=80, debug=False)
