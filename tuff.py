import math
import random
import sys
import os
import time
import platform
import base64
from PIL import ImageGrab, ImageOps
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QTimer, QUrl, QSocketNotifier, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QFont, QFontDatabase, QColor, QGuiApplication
from PyQt6.QtMultimedia import QMediaPlayer, QSoundEffect

operatingsystem = platform.system()
if operatingsystem == "Windows":
    from pynput import mouse
    print("Using pynput on Windows")
    linux = False
elif operatingsystem == "Linux":
    import evdev
    from evdev import InputDevice, categorize, ecodes
    linux = True
    print("Using evdev on Linux")
else:
    linux = True
    print("System ",operatingsystem," is unsupported, defaulting to evdev")

# get path relative to script
def get_app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

APP_DIR = get_app_dir()

def app_path(*parts):
    return os.path.join(APP_DIR, *parts)

os.makedirs(app_path("tempscreenshots"), exist_ok=True)

# Delete previous screenshot if it exists
if os.path.isfile(app_path("tempscreenshots", "screenshot.png")):
    os.remove(app_path("tempscreenshots", "screenshot.png"))

# Read config before startup with error handling because im so cool
if not os.path.isfile(app_path("config.txt")):
    sys.exit("No config found, aborting. Check it exists")
# Utf 8 has to be specified on windows or else some weird encoding errors start bombarding you
config = open(app_path("config.txt"), encoding = "UTF-8")
lines = config.readlines()

phrasestext = open(app_path("phrases.txt"), encoding = "UTF-8")
phrases = phrasestext.readlines()

channelnamestext = open(app_path("channels.txt"), encoding = "UTF-8")
channels = channelnamestext.readlines()

# Apply config to vars
# I absolutely love that this line here just works
chance = int(float(lines[12])*10)
staytime = int(lines[14])
scale = int(lines[16])
bars = int(lines[18])
showtext = float(lines[20])
volume = float(float(lines[22])/100)
showoverlay = float(lines[24])
bounceintensity = int(lines[26])
bgbounce = int(lines[28])
icons = []
phonk = []
fonts = []
overlays = []

icondir = os.listdir(app_path("icons"))
for file in icondir:
    icons.append(file)

phonkdir = os.listdir(app_path("phonk"))
for file in phonkdir:
    phonk.append(file)

fontdir = os.listdir(app_path("fonts"))
for file in fontdir:
    fonts.append(file)

overlaydir = os.listdir(app_path("overlays"))
for file in overlaydir:
    overlays.append(file)

TAU = math.tau

def out_elastic(time_step: float) -> float:
    ANGLE = TAU / 3
    return time_step if time_step == 0.0 or time_step == 1.0 \
        else math.pow(2, -10 * time_step) * math.sin((time_step * 10 - 0.75) * ANGLE) + 1


# This scales a pixmap without stretching it
def aspectscale(newsize,me):
    me.scalefactor = me.pixmap.width()/me.pixmap.height()
    me.icon.setPixmap(me.pixmap.scaled(int(round(newsize*me.scalefactor)), newsize))

# This randomly appends K or M to a string
def numberifystring(string):
    if random.randint(1,3) == 1:
        p = "K"
    elif random.randint(1,3) == 1:
        p = "M"
    else:
        p = ""
    l = [str(string),p]
    out = "".join(l)
    return(out)

def mainloop():
    #Start the application only once for better performance and because all of the pyqt examples had it setup this way
    app = QApplication(sys.argv)
    class Tuff(QWidget):
        # This is a way to get back to the pyqt thread
        mouseClicked = pyqtSignal()
        # This animates the window
        def inanim(self):
            if self.animstep == 0:
                #Set as fullscreen application so it can display over a fullscreen app
                screen = QApplication.primaryScreen().geometry()
                dividedwidth = int(round(screen.width()/3))
                #rerandomize on first tick of the animation

                name = random.choice(icons)
                choice = app_path("icons", name)
                self.pixmap = QPixmap(choice)
                self.setWindowIcon(QIcon(choice))
                self.icon.setPixmap(self.pixmap)
                self.icon.resize(self.width(), self.height())
                self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.posx = 100
                self.posy = 100
                self.animscale = 0
                aspectscale(scale,self)
                self.icon.move(self.posx, self.posy)
                screenshot_path = app_path("tempscreenshots", "screenshot.png")
                self.gscale = ImageOps.grayscale(ImageGrab.grab())
                self.gscale.save(screenshot_path)
                self.gscreen = QPixmap(screenshot_path)
                self.greyscreenshot.setPixmap(self.gscreen)
                if showtext > 0:
                    if float(random.randint(1,100))/100 <= showtext:
                        self.text.show()
                        name = random.choice(fonts)
                        choice = app_path("fonts", name)

                        id = QFontDatabase.addApplicationFont(choice)
                        families = QFontDatabase.applicationFontFamilies(id)
                        self.text.setText(random.choice(phrases))
                        self.text.setFont(QFont(families[0], 44))
                        self.text.resize(int(round(screen.width()/3)), screen.height())
                        self.text.setWordWrap(True)
                        self.text.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.text.move(int(round(screen.width()/3)), int(round(screen.height()/-3)))
                        # apply shadow to text
                        shadow = QGraphicsDropShadowEffect()
                        shadow.setBlurRadius(50)
                        shadow.setColor(QColor('#222222'))
                        self.text.setGraphicsEffect(shadow)
                    else:
                        self.text.hide()
                if showoverlay > 0:
                    if float(random.randint(1,100))/100 <= showoverlay:
                        self.overlay.show()
                        # Read template svg, create a new one with template values replaced and then delete it
                        template = open(app_path("overlays", random.choice(overlays)), "r")
                        data = template.read()

                        for i in range(len(data)):
                            if data.startswith("CNT", i):
                                data = data[:i] + numberifystring(random.randint(1,100)) + data[i+3:]

                        # progress bar is static because I really dont want to create and delete a new svg every animation tick, nor do I know how to
                        tojoin = ['transform="matrix(',str(random.randint(0,100)/100),',0,0,1,0.01126176,0)"']
                        replacement = "".join(tojoin)
                        data = data.replace('transform="matrix(1.0053463,0,0,1,0.01126176,0)"', replacement)
                        data = data.replace('channelname', random.choice(channels))
                        # Modify both sides of the gradient to have a random colour. Thank you geeks4geeks
                        color = random.randrange(0, 2**24)
                        hexrand = hex(color)
                        randcol = hexrand[2:]
                        data = data.replace('994d00', randcol)
                        color = random.randrange(0, 2**24)
                        hexrand = hex(color)
                        randcol = hexrand[2:]
                        data = data.replace('0000bb', randcol)
                        data = data.replace('0.1232', str(random.uniform(0,1)))
                        data = data.replace('0.1212', str(random.uniform(1,2)))
                        randico = random.choice(icons)
                        ico = app_path("icons", randico)
                        # Convert random icon into base64 so we can use it in the svg
                        with open(ico, "rb") as image_file:
                            b64 = base64.b64encode(image_file.read())
                            data = data.replace('b64here', b64.decode('utf8'))

                        template.close()
                        overlay = open(app_path("overlay.svg"), "w")
                        overlay.write(data)
                        overlay.close()
                        self.overlaypix = QPixmap(app_path("overlay.svg"))
                        os.remove(app_path("overlay.svg"))
                        self.overlay.setPixmap(self.overlaypix.scaled(dividedwidth,screen.height()))
                    else:
                        self.overlay.hide()
                self.showFullScreen()
                name = random.choice(phonk)
                phonksound = app_path("phonk", name)
                self.effect.setSource(QUrl.fromLocalFile(phonksound))
                self.effect.play()

            self.animstep += 1
            # We use modulus to make it bounce to the beat, it's not audio reactive but if you mute your speakers it kinda looks like it
            if self.animstep % 12 == 0:
                self.animscale = 0
            else:
                self.animscale += 1
            aspectscale(scale + round(out_elastic(self.animscale /40) * bounceintensity), self)
            if bgbounce == 1:
                newsize = self.gscreen.height() + round(out_elastic(self.animscale /40) * bounceintensity)
                self.greyscreenshot.scalefactor = self.gscreen.width()/self.gscreen.height()
                self.greyscreenshot.setPixmap(self.gscreen.scaled(int(round(newsize*self.greyscreenshot.scalefactor)), newsize))
            # The position is hardcoded, this is not a to do but if you are bored then make it customizable
            self.posx = -200 + round(out_elastic(self.animstep / 10)*200)
            self.posy = 100 + round(out_elastic(self.animstep / 10)*200)
            self.icon.move(self.posx, self.posy)
            if self.animstep > staytime*20:
                self.effect.stop()
                self.hide()
                self.animation.stop()
                if os.path.isfile(app_path("tempscreenshots", "screenshot.png")):
                    os.remove(app_path("tempscreenshots", "screenshot.png"))

        # This is for creating the main window
        def __init__(self):
            super().__init__()
            # YES TRANSPARENCY!!!

            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint
                | Qt.WindowType.WindowStaysOnTopHint
            )
            self.setWindowTitle("Tuff")
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)

            # SETUP GREYSCALE BACKGROUND
            screen = QApplication.primaryScreen().geometry()
            self.setGeometry(screen)
            self.greyscreenshot = QLabel(self)
            # Take a screenshot so we can turn the screen greyscale - this is done using PIL because pyqt doesn't support taking screenies on wayland
            # If we use the same filename it gets replaced upon screenshot
            screenshot_path = app_path("tempscreenshots", "screenshot.png")
            self.pixmap = QPixmap(screenshot_path)
            self.greyscreenshot.setPixmap(self.pixmap)
            self.greyscreenshot.resize(self.width(), self.height())
            self.greyscreenshot.setAlignment(Qt.AlignmentFlag.AlignCenter)
            # SETUP ICON
            self.icon = QLabel(self)
            name = random.choice(icons)
            choice = app_path("icons", name)
            self.pixmap = QPixmap(choice)
            self.icon.setPixmap(self.pixmap)
            self.icon.resize(self.width(), self.height())
            self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.posx = 100
            self.posy = 100
            self.animscale = 0
            self.animstep = 0
            aspectscale(scale,self)
            self.icon.move(self.posx, self.posy)
            # SETUP BLACK BARS AND TEXT
            dividedwidth = int(round(screen.width()/3))
            self.setGeometry(0, 0, screen.width(), screen.height())
            if bars == 1:
                self.leftbar = QLabel(self)
                self.rightbar = QLabel(self)
                self.leftbar.resize(dividedwidth,screen.height())
                self.rightbar.resize(dividedwidth,screen.height())
                self.rightbar.move(dividedwidth*2,0)
                self.leftbar.setStyleSheet("background-color: black")
                self.rightbar.setStyleSheet("background-color: black")
            if showoverlay > 0:
                self.overlay = QLabel(self)
                self.overlay.resize(dividedwidth,screen.height())
                self.overlay.move(dividedwidth,0)
            if showtext > 0:
                name = random.choice(fonts)
                choice = app_path("fonts", name)
                id = QFontDatabase.addApplicationFont(choice)
                if id < 0:
                    print("No font file found. Check capitalisation and that it exists as a child of the script")
                else:
                    families = QFontDatabase.applicationFontFamilies(id)

                    self.text = QLabel(random.choice(phrases), self)
                    self.text.setFont(QFont(families[0], 44))
                    self.text.resize(int(round(screen.width()/3)), screen.height())
                    self.text.setWordWrap(True)
                    self.text.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.text.move(int(round(screen.width()/3)), int(round(screen.height()/-3)))
                    self.text.setStyleSheet("color : white;")
                    # apply shadow to text
                    shadow = QGraphicsDropShadowEffect()
                    shadow.setBlurRadius(50)
                    shadow.setColor(QColor('#222222'))
                    self.text.setGraphicsEffect(shadow)
            self.animation = QTimer(self)
            self.animation.timeout.connect(self.inanim)

            # Trigger_anim always runs on pyqt thread
            self.mouseClicked.connect(self.trigger_anim)
            self.effect = QSoundEffect()
            # Create qsoundeffect and play a test startup sound
            self.effect.setVolume(volume)
            self.effect.setSource(QUrl.fromLocalFile(app_path("startup.wav")))
            self.effect.play()
            if linux:
                self.mouse = InputDevice(mousepath)
                # We setup a notifier for mouse clicks
                self.notifier = QSocketNotifier(self.mouse.fd, QSocketNotifier.Type.Read, self)
                self.notifier.activated.connect(self.on_mouse_event)
            else:
                self.windows_listener()

        def on_mouse_event(self):
            for event in self.mouse.read():
                if event.type == ecodes.EV_KEY and event.code == ecodes.BTN_LEFT:
                    key_event = categorize(event)
                    if key_event.keystate == key_event.key_up:
                        self.trigger_anim()

        def windows_listener(self):
            def on_click(x, y, button, pressed):
                if button == mouse.Button.left and not pressed:
                    self.mouseClicked.emit()

            self.listener = mouse.Listener(on_click=on_click)
            self.listener.start()  # non-blocking, runs in background thread

        def trigger_anim(self):
            if not self.animation.isActive() and random.randint(0,1000) <= chance:
                self.animstep = 0
                self.animation.start(30)

    tuff = Tuff()
    sys.exit(app.exec())

if linux:
    # This should find the mouse. If you have multiple mice... Well...
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        if 272 in device.capabilities().get(ecodes.EV_KEY, []):
            mousepath = device.path
            print(f"Found mouse: {device.name} at", mousepath)

    mouse = InputDevice(mousepath)

if __name__ == "__main__":
    # Start the main loop, now evdev and windows are handled in this
    mainloop()