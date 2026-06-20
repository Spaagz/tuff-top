
                      _______     __  __   _______
                     |__   __|   / _|/ _| |__   __|
                        | |_   _| |_| |_     | | ___  _ __
                        | | | | |  _|  _|    | |/ _ \| '_ \
                        | | |_| | | | |      | | (_) | |_) |
                        |_|\__,_|_| |_|      |_|\___/| .__/
                                                     | |
                                                     |_|

# Make your desktop TUFF 🔥
-> [Promotional Preview Video](https://www.youtube.com/watch?v=HbPldsK_V3k) <-

<p align="center">
  <img src="https://github.com/Spaagz/tuff-top/blob/master/example-gifs/gameinterruptionpreview.gif?raw=true" alt="Fall guys getting interrupted by a phonk edit"/>
</p>

If the app crashes on launch, try adding your user to the input group and logging out and back in:
```
sudo usermod -aG input $USER
```

This is a project with the intention to mimic those low quality phonk gameplay edits where the screen is frozen, grayscaled, accompanied with some stupid catchphrase and a bouncing "tuff" icon.
In other words, it gives you the classic youtube shorts experience (from 3 years ago)

Built for Linux wayland.
The goal is to be able to use it in any game or app without having to make explicit support for it.

The project uses PyQt6 for displaying transparent overlay windows as tkinter doesn't support transparency, mpg123 for playing audio and evdev for input capturing on wayland. We also use Pillow for taking screenshots and grayscaling them.

AI was used in generating examples on what various PyQt flags do, it was not used to generate code (This is my first python project afterall, I want to learn something _even if_ it is a slow and tedious journey)

## 🛠️ Usage
Head on over to the latest release, extract and run it!
Start spam clicking to ensure it works, if not, you may need to add your user to the input group
If all works well, then you can have some fun changing the configs, icons, fonts and phrases
You will have to close the python process from a task manager when done

## 🔨 Based of off generational game modifications such as:
> https://modrinth.com/mod/so-tuff
> 
> https://geode-sdk.org/mods/saritahhh.youtubeshortsedit

🧰 **Features:**
- Customisable icons and music
- Robust config with chance of tuffness and stay time
- Click detection as a trigger
- Greyscaling of the screen for maximum tuffness
- And more being added (suggestions allowed)

🎶 **Music Credits:**
- DVRST - Close Eyes
- g3ox_em - GigaChad Theme (Phonk House Version) sped up
- Kordhell - Live Another Day
- INTERWORLD - METAMORPHOSIS
- MoonDeity - NEON BLADE
- Hensonn - Sahara
