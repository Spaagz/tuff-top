import time
import math
import evdev
import random
import sys
import os
import threading
import subprocess
from os import listdir
from os.path import isfile, join
from evdev import InputDevice, categorize, ecodes
from PIL import Image, ImageGrab, ImageOps
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# Delete previous screenshot if it exists. This only happens when the program is shutdown incorrectly
if os.path.isfile("temp/screenshot.png"):
    os.remove("temp/screenshot.png")

# Read config before startup with error handling because I'm so cool
if not os.path.isfile("config.txt"):
    sys.exit("No config found, aborting. Check it exists or redownload")

config = open("config.txt","r")
lines = config.readlines()
# Apply config to vars
chance = int(lines[12])
staytime = int(lines[14])
scale = int(lines[16])
global icons
global phonk
icons = []
phonk = []
icondir = os.listdir("icons")

for file in icondir:
    icons.append(file)

phonkdir = os.listdir("phonk")


for file in phonkdir:
    phonk.append(file)


def tuffchance():
    if random.randint(0,100) <= chance:
        twastuff()

# This should find the mouse. If you have multiple mice... Well...
devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
for device in devices:
    if 272 in device.capabilities().get(ecodes.EV_KEY, []):
        mousepath = device.path
        print(f"Found mouse: {device.name} at", mousepath)

mouse = InputDevice(mousepath)

TAU = math.tau

def out_elastic(time_step: float) -> float:
    ANGLE = TAU / 3
    return time_step if time_step == 0.0 or time_step == 1.0 \
        else math.pow(2, -10 * time_step) * math.sin((time_step * 10 - 0.75) * ANGLE) + 1

app = QApplication(sys.argv)

def twastuff():
    class GreyScreenGrab(QWidget):
        # This is mostly copied from Tuffimage
        def __init__(self):
            super().__init__()
            # Take a screenshot so we can turn the screen greyscale - this is done using PIL because pyqt doesn't support taking screenies on wayland
            self.gscale = ImageGrab.grab()
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint
                | Qt.WindowType.WindowStaysOnTopHint
                | Qt.WindowType.Tool
            )
            screen = QApplication.primaryScreen().geometry()
            self.setGeometry(screen)
            self.label = QLabel(self)
            self.setWindowTitle("Greyscale")
            # If we use the same filename it gets replaced upon screenshot
            self.gscale = ImageOps.grayscale(ImageGrab.grab())
            self.gscale.save("temp/screenshot.png")
            #self.setWindowIcon(QIcon(choice))
            self.pixmap = QPixmap("temp/screenshot.png")
            #self.setWindowIcon(QIcon("greyicon.svg"))
            self.label.setPixmap(self.pixmap)
            self.label.resize(self.width(), self.height())
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            #self.label.setPixmap(self.pixmap.scaled(scale, scale))
            #self.label.move(self.posx, self.posy)

    class Tuffimage(QWidget):
        # This animates the window
        def inanim(self):
            self.animstep += 1
            # We use modulus with random here to make it bounce randomly, it's not audio reactive but if you mute your speakers it kinda looks like it
            if self.animstep % random.randint(9,14) == 0:
                self.animscale = 0
            else:
                self.animscale += 1
            self.label.setPixmap(self.pixmap.scaled(50 + round(out_elastic(self.animscale /20) * 50), 50 + round(out_elastic(self.animscale /20) * 50)))
            # The position is hardcoded, this is not a to do but if you are bored then make it customizable
            self.posx = -200 + round(out_elastic(self.animstep / 10) * 200)
            self.posy = 100 + round(out_elastic(self.animstep / 10) * 200)
            self.label.move(self.posx, self.posy)
            self.activateWindow()
            self.raise_()
            self.setFocus()
            if self.animstep > staytime*20:
                # remove screenshot if it exists
                if os.path.isfile("temp/screenshot.png"):
                    os.remove("temp/screenshot.png")
                self.sound_process.terminate()
                self.timer.stop()
                self.hide()
                app.quit()
        # This is for creating the window
        def __init__(self):
            super().__init__()
            # YES TRANSPARENCY!!!
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint
                | Qt.WindowType.WindowStaysOnTopHint
                | Qt.WindowType.Tool
            )
            self.setWindowTitle("Tuff")
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
            # we play a random sound from the phonk directory
            global phonk
            name = random.choice(phonk)
            path = "phonk/"
            choices = (path, name)
            choice = "".join(choices)
            self.sound_process = subprocess.Popen(["mpg123", choice])
            screen = QApplication.primaryScreen().geometry()
            self.setGeometry(screen)
            self.label = QLabel(self)
            global icons
            name = random.choice(icons)
            path = "icons/"
            choices = (path, name)
            choice = "".join(choices)
            self.pixmap = QPixmap(choice)
            self.setWindowIcon(QIcon(choice))
            self.label.setPixmap(self.pixmap)
            self.label.resize(self.width(), self.height())
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.posx = 100
            self.posy = 100
            self.animscale = 0
            self.animstep = 0
            global scale
            self.label.setPixmap(self.pixmap.scaled(scale, scale))
            self.label.move(self.posx, self.posy)
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.inanim)
            self.timer.start(30)

    gscale = GreyScreenGrab()
    gscale.show()
    tuffimg = Tuffimage()
    tuffimg.show()
    app.exec()

for event in mouse.read_loop():
    if event.type == ecodes.EV_KEY:
        data = categorize(event)
        if data.keystate == 1:
            tuffchance()

