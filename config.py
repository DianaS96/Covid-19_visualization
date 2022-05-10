import os

CURR_DIR = os. getcwd()

IMG_PATH = CURR_DIR + '/static/img/'

if not os.path.exists(IMG_PATH):
    os.makedirs(IMG_PATH)