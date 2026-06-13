import time
import math
import evdev
import random
import sys
import os
import subprocess
import asyncio
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
    sys.exit("No config found, aborting. Check it exists")

config = open("config.txt","r")
global lines
lines = config.readlines()

# Apply config to vars
global chance
chance = int(lines[12])*10
staytime = int(lines[14])
global scale
scale = int(lines[16])
bars = int(lines[18])
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

# MATH

TAU = math.tau

def out_elastic(time_step: float) -> float:
    ANGLE = TAU / 3
    return time_step if time_step == 0.0 or time_step == 1.0 \
        else math.pow(2, -10 * time_step) * math.sin((time_step * 10 - 0.75) * ANGLE) + 1

# WINDOW DEFINITIONS
app = QApplication(sys.argv)

def onend(self):
    # remove screenshot if it exists
    if os.path.isfile("temp/screenshot.png"):
        os.remove("temp/screenshot.png")
    self.sound_process.terminate()
    self.timer.stop()
    self.hide()
    app.quit()

class Blackbar(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)

        screen = QApplication.primaryScreen().size()
        # get a third of the screen so we can get the phone(tm) aspect ratio
        dividedwidth = int(round(screen.width()/3))
        self.setGeometry(0, 0, screen.width(), screen.height())
        self.leftbar = QLabel(self)
        self.rightbar = QLabel(self)
        self.leftbar.resize(dividedwidth,screen.height())
        self.rightbar.resize(dividedwidth,screen.height())
        self.rightbar.move(dividedwidth*2,0)
        self.leftbar.setStyleSheet("background-color: black")
        self.rightbar.setStyleSheet("background-color: black")
        self.setWindowTitle("Black bar")

class GreyScreenGrab(QWidget):
    # This is mostly copied from Tuffimage
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        self.label = QLabel(self)
        self.setWindowTitle("Greyscale")
        # Take a screenshot so we can turn the screen greyscale - this is done using PIL because pyqt doesn't support taking screenies on wayland
        # If we use the same filename it gets replaced upon screenshot
        self.gscale = ImageOps.grayscale(ImageGrab.grab())
        self.gscale.save("temp/screenshot.png")
        self.pixmap = QPixmap("temp/screenshot.png")
        self.setWindowIcon(QIcon("greyicon.svg"))
        self.label.setPixmap(self.pixmap)
        self.label.resize(self.width(), self.height())
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

class Tuffimage(QWidget):
    # This animates the window
    def inanim(self):
        self.animstep += 1
        # We use modulus it to make it bounce to the beat, it's not audio reactive but if you mute your speakers it kinda looks like it
        if self.animstep % 12 == 0:
            self.animscale = 0
        else:
            self.animscale += 1
        global scale
        self.label.setPixmap(self.pixmap.scaled(scale + round(out_elastic(self.animscale /40) * 20), scale + round(out_elastic(self.animscale /40) * 20)))
        # The position is hardcoded, this is not a to do but if you are bored then make it customizable
        self.posx = -200 + round(out_elastic(self.animstep / 10) * 200)
        self.posy = 100 + round(out_elastic(self.animstep / 10) * 200)
        self.label.move(self.posx, self.posy)
        self.activateWindow()
        self.raise_()
        self.setFocus()
        if self.animstep > staytime*20:
            onend(self)
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

# EVENT HANDLING

# This should find the mouse. If you have multiple mice... Well...
devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
for device in devices:
    if 272 in device.capabilities().get(ecodes.EV_KEY, []):
        mousepath = device.path
        print(f"Found mouse: {device.name} at", mousepath)

mouse = InputDevice(mousepath)

async def input(dev):
    async for event in dev.async_read_loop():
        if event.type == ecodes.EV_KEY:
            data = categorize(event)
            if data.keystate == 0:
                if random.randint(0,1000) <= chance:
                    gscale = GreyScreenGrab()
                    gscale.show()
                    tuffimg = Tuffimage()
                    tuffimg.show()
                    if bars == 1:
                        blackbar = Blackbar()
                        blackbar.show()
                    app.exec()


asyncio.run(input(mouse))