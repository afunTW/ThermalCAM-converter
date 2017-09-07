"""
Browse all temperature matrix per moth and get the maximum difference frame
Then, transform the maximum varience frame to temperature image and save it
"""
import logging
import sys
from glob import glob
from os import sep
from os.path import abspath, dirname, join

import cv2

from src.heatmap import HeatMap
from src.convert import Converter
from src.image import BaseImageCV
from src.wrapper import (cf_convert_by_hough_circle,
                         cf_convert_by_max_temperature_difference,
                         cf_convert_to_grayscale)


def test_hough_circle(moth_path):
    im = cv2.imread(moth_path)
    im_resize = cv2.resize(im, (320, 239), interpolation=cv2.INTER_AREA)
    im_gray = cv2.cvtColor(im_resize, cv2.COLOR_BGR2GRAY)
    im_circle = cv2.HoughCircles(im_gray, cv2.HOUGH_GRADIENT, 1, 10,
                                param1=100, param2=22, minRadius=0, maxRadius=25)
    for c in im_circle[0]:
        cv2.circle(im_resize,  (c[0], c[1]), c[2], (0, 0, 255), 1)
        cv2.circle(im_resize, (c[0], c[1]), 2, (255, 0, 0), 1)

    BaseImageCV.show_image_by_cv2(im_resize)

def test_connected_component(moth_path):
    im = cv2.imread(moth_path)
    im_resize = cv2.resize(im, (320, 239), interpolation=cv2.INTER_AREA)
    im_gray = cv2.cvtColor(im_resize, cv2.COLOR_BGR2GRAY)

def temperature_img_preprocess(paths):
    """
    preprocess thermal data
    - convert temperature file in difference condition
        - cf_convert_by_hough_circle(moth_path, False, (-4, 'temperature_anchor_all'))
        - cf_convert_by_max_temperature_difference(moth_path, (-4, 'temperature_temp_diff'))
    """
    # 20170307_30C, 20170313_5C, 20170314_5C
    for folder_path in glob(join(paths, '*')):
        # per moth folder
        for i, moth_paths in enumerate(glob(join(folder_path, '*'))):
            # cf_convert_by_hough_circle(moth_paths, False, (-4, 'temperature_anchor_all'))
            # cf_convert_by_max_temperature_difference(moth_paths, (-4, 'temperature_temp_diff'))
            cf_convert_to_grayscale(moth_paths, (-4, 'temperature_gray'))
            # pass

def original_img_preprocess(paths):
    """
    preprocess original RGB images
    - resize
    - detect hough circles
    """
    # 20170307, 20170313, 20170314
    for folder_path in glob(join(paths, '*')):
        # mod, raw
        for sub_folder in glob(join(folder_path, '*')):
            if sub_folder.split(sep)[-1] == 'mod':
                # per moth image
                for i, moth_path in enumerate(glob(join(sub_folder, '*'))):
                    LOGGER.info('path: {}'.format(moth_path))
                    test_hough_circle(moth_path)
                    # break
            break
        break

def main():
    """
    image preprocessing
    - temperature_img_preprocess(THERMAL_PATH): handle temperature image
    - original_img_preprocess(RGB_PATH): handle original RGB image
    """
    temperature_img_preprocess(THERMAL_PATH)
    # original_img_preprocess(RGB_PATH)
    pass

if __name__ == '__main__':
    # logging config
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(filename)12s:L%(lineno)-3s [%(levelname)8s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        stream=sys.stdout
    )

    LOGGER = logging.getLogger(__name__)
    THERMAL_PATH = abspath(join(dirname(__file__), '../data/temperature_matrix'))
    RGB_PATH = abspath(join(dirname(__file__), '../data/RGB_images'))
    main()
