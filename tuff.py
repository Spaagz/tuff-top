import math
import evdev
import random
import sys
import os
import subprocess
import asyncio
from evdev import InputDevice, categorize, ecodes
from PIL import ImageGrab, ImageOps
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QFont, QFontDatabase, QColor

# get path relative to script
def get_app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

APP_DIR = get_app_dir()

def app_path(*parts):
    return os.path.join(APP_DIR, *parts)

os.makedirs(app_path("tempscreenshots"), exist_ok=True)

# Delete previous screenshot if it exists, this only happens when the program shuts down incorrectly
if os.path.isfile(app_path("tempscreenshots", "screenshot.png")):
    os.remove(app_path("tempscreenshots", "screenshot.png"))

# Read config before startup with error handling because im so cool
if not os.path.isfile(app_path("config.txt")):
    sys.exit("No config found, aborting. Check it exists")

config = open(app_path("config.txt"), "r")
global lines
lines = config.readlines()

phrasestext = open(app_path("phrases.txt"),"r")
global phrases
phrases = phrasestext.readlines()

# Apply config to vars
global chance
# I absolutely love that this line here just works
chance = int(float(lines[12])*10)
staytime = int(lines[14])
global scale
scale = int(lines[16])
bars = int(lines[18])
showtext = int(lines[20])
global icons
global phonk
icons = []
phonk = []
fonts = []

icondir = os.listdir(app_path("icons"))
for file in icondir:
    icons.append(file)

phonkdir = os.listdir(app_path("phonk"))
for file in phonkdir:
    phonk.append(file)

fontdir = os.listdir(app_path("fonts"))
for file in fontdir:
    fonts.append(file)

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
    if os.path.isfile(app_path("tempscreenshots", "screenshot.png")):
        os.remove(app_path("tempscreenshots", "screenshot.png"))
    self.sound_process.terminate()
    self.timer.stop()
    self.hide()
    app.quit()

# This scales a pixmap without stretching it
def aspectscale(newsize,self):
    self.scalefactor = self.pixmap.width()/self.pixmap.height()
    self.label.setPixmap(self.pixmap.scaled(int(round(newsize*self.scalefactor)), newsize))


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
        self.setWindowTitle("Black bars")
        self.setWindowIcon(QIcon("blackbars.svg"))
        if showtext == 1:
            name = random.choice(fonts)
            choice = app_path("fonts", name)

            id = QFontDatabase.addApplicationFont(choice)
            if id < 0:
                print("No font file found. Check capitalisation and that it exists as a child of the script")
            else:
                families = QFontDatabase.applicationFontFamilies(id)

                self.text = QLabel(random.choice(phrases), self)
                self.text.setFont(QFont(families[0], 44))
                #self.text.setFont(QFont('Times', 44))
                #self.text.setAlignment(QtCore.Qt.AlignCenter)
                self.text.resize(int(round(screen.width()/3)), screen.height())
                self.text.setWordWrap(True)
                self.text.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.text.move(int(round(screen.width()/3)), int(round(screen.height()/-3)))
                # apply shadow to text
                shadow = QGraphicsDropShadowEffect()
                shadow.setBlurRadius(50)
                shadow.setColor(QColor('#222222'))
                self.text.setGraphicsEffect(shadow)

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
        screenshot_path = app_path("tempscreenshots", "screenshot.png")
        self.gscale = ImageOps.grayscale(ImageGrab.grab())
        self.gscale.save(screenshot_path)
        self.pixmap = QPixmap(screenshot_path)
        self.setWindowIcon(QIcon(app_path("greyicon.svg")))
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
        aspectscale(scale + round(out_elastic(self.animscale /40) * 20), self)
        # The position is hardcoded, this is not a to do but if you are bored then make it customizable
        self.posx = -200 + round(out_elastic(self.animstep / 10)*200)
        self.posy = 100 + round(out_elastic(self.animstep / 10)*200)
        self.label.move(self.posx, self.posy)
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
        choice = app_path("phonk", name)
        self.sound_process = subprocess.Popen(["mpg123", choice])
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        self.label = QLabel(self)
        global icons
        name = random.choice(icons)
        choice = app_path("icons", name)
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
        aspectscale(scale,self)
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
# Play startup sound when after we have assigned everything
startupsound = subprocess.Popen(["mpg123", app_path("startup.mp3")])

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