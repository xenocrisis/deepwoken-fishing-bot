import cv2
import numpy as np
import time
import threading

from ahk import AHK
ahk = AHK()

character = {
    'toggle_fishing': False,
    'sensors_active': False,
    'is_fishing': False,
    'middle': False,
    'right': False,
    'left': False
}

white_threshold = 0.5
gray_scale_threshold = 80

is_moving_camera = False
is_throwing_rod = False
time_is_running = False
fishing_was_false_for = False
not_fishing_time = 0

def keep_camera_down():
    global is_moving_camera
    character['sensors_active'] = False
    
    is_moving_camera = True
    time.sleep(2)
    ahk.mouse_drag(0, 100, relative=True, button='R', speed=6, blocking=False)
    is_moving_camera = False

    time.sleep(0.1)
    character['sensors_active'] = True


def fish():
    global is_moving_camera

    if character['sensors_active']:

        if not is_moving_camera:

            thread = threading.Thread(target=keep_camera_down)
            thread.start()

        if character['is_fishing']:
            ahk.click()

        if character['middle']:
            ahk.key_down('s')
        else:
            ahk.key_up('s')

        if character['left']:
            ahk.key_down('a')
        else:
            ahk.key_up('a')

        if character['right']:
            ahk.key_down('d')
        else:
            ahk.key_up('d')

def throw_rod():
    global is_throwing_rod

    is_throwing_rod = True

    ahk.click(direction='D')
    time.sleep(1.5)
    ahk.click(direction='U')

    time.sleep(6)

    is_throwing_rod = False

def hit_box(image, trigger_size=20, trigger_alture=45, lmargin=70, rmargin=38, middle_size=10, middle_offset=10,  fishing_trigger_alture=28):

    global gray_scale_threshold
    global time_is_running
    global fishing_was_false_for
    global not_fishing_time

    # Gray scale
    image = turn_to_black(image, threshold=gray_scale_threshold)

    img_pixels = np.sum(image)
    img_white_pixels = np.sum(image == 255)

    white_per = (img_white_pixels / img_pixels) * 1000
    ideal_per = (90000 / img_pixels) * 1000

    if white_per == ideal_per:
        pass
    else:
        gray_scale_threshold = gray_scale_threshold + 1 if white_per >= ideal_per else gray_scale_threshold - 1

    # Center coords
    (h, w) = image.shape[:2]
            
    center_y = h // 2
    center_x = w // 2
   
    coordinates = center_x, center_y

    # Logic hitboxes:

    y_top, y_bottom = coordinates[1] + trigger_alture - trigger_size // 2, coordinates[1] + trigger_alture + trigger_size // 2

    x_left, x_right = coordinates[0] - lmargin, coordinates[0] + rmargin

    # Coordenadas de la línea izquierda
    line_left_coordinates = np.column_stack((np.full_like(range(y_top, y_bottom + 1), x_left), range(y_top, y_bottom + 1)))

    # Coordenadas de la línea derecha
    line_right_coordinates = np.column_stack((np.full_like(range(y_top, y_bottom + 1), x_right), range(y_top, y_bottom + 1)))
    
    # Coordenadas middle con offset
    line_middle_coordinates = np.column_stack((np.arange(coordinates[0] - middle_size - middle_offset, coordinates[0] + middle_size - middle_offset + 1),
                                               np.full_like(np.arange(coordinates[0] - middle_size - middle_offset, coordinates[0] + middle_size - middle_offset + 1),
                                                            y_top + fishing_trigger_alture)))

    white_pixels_left = image[line_left_coordinates[:, 1], line_left_coordinates[:, 0]] == 255
    white_pixels_right = image[line_right_coordinates[:, 1], line_right_coordinates[:, 0]] == 255
    white_pixels_middle = image[line_middle_coordinates[:, 1], line_middle_coordinates[:, 0]] == 255

    # Contar píxeles blancos en cada línea
    count_white_left = np.sum(white_pixels_left)
    count_white_right = np.sum(white_pixels_right)
    count_white_middle = np.sum(white_pixels_middle)

    # Calcular la proporción de píxeles blancos en cada línea
    ratio_white_left = count_white_left / len(white_pixels_left)
    ratio_white_right = count_white_right / len(white_pixels_right)
    ratio_white_middle = count_white_middle / len(white_pixels_middle)

    # Verificar si la mayoría de la superficie es blanca para cada línea
    left_is_mostly_white = ratio_white_left > white_threshold
    right_is_mostly_white = ratio_white_right > white_threshold
    middle_is_mostly_white = ratio_white_middle > white_threshold

    if character['sensors_active'] is False:
        character['left'] = False
        character['right'] = False
        character['middle'] = False
    else:
        if left_is_mostly_white:
            character['left'] = True
        else:
            character['left'] = False

        if right_is_mostly_white:
            character['right'] = True
        else:
            character['right'] = False

        if middle_is_mostly_white:
            character['middle'] = True
        else:
            character['middle'] = False
    
    if character['left'] is True or character['right'] is True or character['middle'] is True:
        character['is_fishing'] = True
        time_is_running = False
    else:
        character['is_fishing'] = False
        if not time_is_running:
            fishing_was_false_for = int(time.time())
            time_is_running = True

    try:
        if ahk.key_state('ñ'):
            character['toggle_fishing'] = not character['toggle_fishing']
            time.sleep(0.15)
            ahk.key_press('a')
            ahk.key_press('s')
            ahk.key_press('d')

        not_fishing_time = int(time.time()) - fishing_was_false_for

        if character['toggle_fishing']:
            character['sensors_active'] = True
        else:
            character['sensors_active'] = False

        if character['toggle_fishing'] is True:

            if not character['is_fishing'] and int(time.time()) >= fishing_was_false_for + 6:
                not_fishing_time = 0
                if not is_throwing_rod:
                    thread = threading.Thread(target=throw_rod)
                    thread.start()
            else:
                fish_thread = threading.Thread(target=fish)
                fish_thread.start()

        else:
            pass
    except KeyboardInterrupt:
        exit()
    except:
        pass

    print(character)

    # Visual hitbox NOT LOGICAL:
    image_visual = cv2.cvtColor(image.copy(), cv2.COLOR_BAYER_BG2BGR)

    current_position = None

    # Sensors view
    if character['middle'] == True:
        cv2.polylines(image_visual, [line_middle_coordinates.astype(np.int32)], isClosed=False, color=(0, 255, 0), thickness=2)
        current_position = 'Middle'
    else:
        cv2.polylines(image_visual, [line_middle_coordinates.astype(np.int32)], isClosed=False, color=(255, 0, 0), thickness=2)

    if character['left'] == True:
        cv2.polylines(image_visual, [line_left_coordinates.astype(np.int32)], isClosed=False, color=(0, 255, 0), thickness=2)
        current_position = 'Left'
    else:
        cv2.polylines(image_visual, [line_left_coordinates.astype(np.int32)], isClosed=False, color=(255, 0, 0), thickness=2)

    if character['right'] == True:
        cv2.polylines(image_visual, [line_right_coordinates.astype(np.int32)], isClosed=False, color=(0, 255, 0), thickness=2)
        current_position = 'Right'
    else:
        cv2.polylines(image_visual, [line_right_coordinates.astype(np.int32)], isClosed=False, color=(255, 0, 0), thickness=2)

    # Ui info
    h, w = image_visual.shape[:2]

    # Definir la región superior que se va a pintar de blanco
    per_up = 0.2  # Porcentaje de la parte superior que se pintará
    h_up = int(h * per_up)

    # Pintar la parte superior de blanco
    image_visual[:h_up, :] = [0, 0, 0]  # [255, 255, 255] representa el color blanco en formato BGR

    if character['toggle_fishing']:
        fishing = "ON"
    else:
        fishing = "OFF"

    # Agregar texto encima
    text = f'{fishing} | Not fishing for: {not_fishing_time} | Sensors Active: {character["sensors_active"]}'
    position = (30, 50)  # Coordenadas (x, y) del texto en píxeles
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_size = 1
    color_texto = (255, 255, 255)  # Color del texto en formato BGR

    cv2.putText(image_visual, text, position, font, font_size, color_texto, 2, cv2.LINE_AA)

    return image_visual


def turn_to_black(image, contrast_factor=1.5, threshold=200):
    # Leer la imagen
    image = np.array(image)

    # Aplicar mejora de contraste
    image_contrast = cv2.convertScaleAbs(image, alpha=contrast_factor, beta=0)

    # Convertir a escala de grises
    gray_scale_img = cv2.cvtColor(image_contrast, cv2.COLOR_BGR2GRAY)

    _, img_binary = cv2.threshold(gray_scale_img, threshold, 255, cv2.THRESH_BINARY)

    # Filtro
    img_binary = cv2.medianBlur(img_binary, 15)

    return img_binary