# Modules
from time import sleep
import os
import pygetwindow as gw
from PIL import ImageGrab
import cv2
import numpy as np
import sys
from pystray import MenuItem as item
from pystray import Icon, Menu
from PIL import Image

# Functions
from vision import *

def main(debug=False):

    def get_active_window():
        
        active_window = gw.getActiveWindow()

        if active_window:
            return active_window
        else:
            return None

    def capture_window(window_title):

        # Get the window by title
        window = gw.getWindowsWithTitle(window_title)

        if not window:
            print(f"[LOG] Window with title '{window_title}' not found.")
            return

        window = window[0]

        # Get the window's position and size
        left, top, width, height = window.left, window.top, window.width, window.height

        # Capture the screen content of the window
        screenshot = ImageGrab.grab(bbox=(left, top, left + width, top + height))

        return screenshot

    def show(capture_input):

        screenshot_np = np.array(capture_input)

        # Convierte de BGR a RGB si es necesario
        if len(screenshot_np.shape) == 3 and screenshot_np.shape[2] == 3:
            screenshot_np = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2RGB)

        # Muestra la imagen en una ventana de OpenCV
        cv2.imshow('Debug overlay', screenshot_np)
        cv2.resizeWindow('Debug overlay', 800, 500)
        cv2.waitKey(1)  # Espera 1 milisegundo para actualizar la interfaz gráfica

    def resize_img(img, new_width=816, new_height=638):

        img = np.array(img)

        # Resize the image to the new resolution
        img = cv2.resize(img, (new_width, new_height))

        return img

    def bandeja_entrada():

        def no_action():
            pass

        def exit_action(icon, item):
            global running
            icon.stop()
            running = False
            os._exit

        # Definir el menú de la bandeja de entrada
        menu = (
            item('Deepwoken auto fishing', no_action),
            item('"ñ" to toggle. by @abykko', no_action),
            item('Exit', exit_action),
        )

        # Crear un ícono para la bandeja de entrada
        image = Image.open("Fishing_Rod.ico")  # Reemplaza "icon.png" con la ruta de tu propia imagen
        icon = Icon("name", image, menu=Menu(*menu))

        icon.run()

    # Variables
    global running
    running = True

    if debug:
        cv2.namedWindow('Debug overlay', cv2.WINDOW_NORMAL)

    # Bandeja entrada
    bandeja = threading.Thread(target=bandeja_entrada)
    bandeja.start()

    while True:

        if running:
            pass
        else:
            break

        # Script will only work / continue if roblox is open and active or focus
        active_window = get_active_window()

        if active_window is None:
            print(f'[LOG] No window found.')
            sleep(1)
            continue
        else:

            try:
                active_window_title = active_window.title
            except Exception as err:
                print(err)
                sleep(1)
                continue

            if active_window_title != 'Roblox':
                print('[LOG] Roblox is not active. Current window:', active_window_title)
                sleep(1)
                continue

        # Roblox is open then:

        os.system('cls' if os.name == 'nt' else 'clear')

        roblox_capture = capture_window(active_window_title)

        roblox_capture = resize_img(roblox_capture)
        
        window_width = active_window.width
        window_height = active_window.height

        if window_height <= 1000 and window_width <= 1000:
            roblox_capture = hit_box(roblox_capture,lmargin=70, rmargin=38)
        else:
            roblox_capture = hit_box(roblox_capture,lmargin=53, rmargin=20)

        if debug:
            try:
                show(roblox_capture)
            except:
                pass
        
if __name__ == '__main__':
    from sys import argv
    if argv[0] == 'debug':
        debug = True
    else:
        debug = False
    try:
        main(debug)
    except KeyboardInterrupt:
        running = False
        os._exit
        exit()
    except Exception as err:
        print(err)
    finally:
        ahk.clear_hotkeys()
        os._exit