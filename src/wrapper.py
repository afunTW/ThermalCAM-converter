"""
wrapper
    find_heatmap_by_XXX
        1. input a list of file path
        2. convert each frame into heatmap
        3. find one of the target heatmap by XXX
        4. convert the target heatmap and return
"""
import logging
from concurrent.futures import ProcessPoolExecutor
from os import listdir, makedirs, sep
from os.path import abspath, dirname, exists, join

import cv2
import matplotlib.pyplot as plt
import numpy as np

from src.convert import Converter, ConcurrentConverter

LOGGER = logging.getLogger(__name__)

def construct_png_path(path, i, directory):
    new_path = path.split(sep)
    new_path[-1] = new_path[-1].split('.')[0] + '.png'
    new_path[i] = str(directory)
    new_path = sep.join(new_path)
    return new_path

def cf_convert_to_grayscale(file_path, change_save_path=(-3, 'save')):
    """
    Input file path, there's multiple files under the folder
    convert all of matrix to grayscale image
    """
    frame_paths = [join(file_path, i) for i in listdir(file_path)]
    args = None

    # handle saving path
    if change_save_path is not None and isinstance(change_save_path, tuple):
        try:
            assert len(change_save_path) == 2
        except Exception as e:
            LOGGER.warning('parameter change_save_path length should be 2')
        cb = lambda x: construct_png_path(x, change_save_path[0], change_save_path[1])
        args = (frame_paths, cb)
    else:
        args = (frame_paths)

    cf_converter = ConcurrentConverter.cf_file_to_grayscale(*args)
    return cf_converter


def cf_convert_by_hough_circle(file_path, draw_circle=False, change_save_path=(-2, 'save')):
    """
    Input file path, there's multiple files under the folder
    convert all file into RGB images by hough circles
    """
    frame_paths = [join(file_path, i) for i in listdir(file_path)]
    args = None

    # handle saving path
    if change_save_path is not None and isinstance(change_save_path, tuple):
        try:
            assert len(change_save_path) == 2
        except Exception as e:
            LOGGER.warning('parameter change_save_path length should be 2')
        cb = lambda x: construct_png_path(x, change_save_path[0], change_save_path[1])
        args = (frame_paths, draw_circle, cb)
    else:
        args = (frame_paths, draw_circle)

    cf_converter = ConcurrentConverter.cf_file_to_rgb_by_hough_circle(*args)
    return cf_converter

def cf_convert_by_max_temperature_difference(file_path, change_save_path=(-3, 'save')):
    """
    Input file path, there's multiple files under the folder
    get one of the max temperature difference matrix and convert to RGB image
    """
    frame_paths = [join(file_path, i) for i in listdir(file_path)]
    args = None

    # handle saving path
    if change_save_path is not None and isinstance(change_save_path, tuple):
        try:
            assert len(change_save_path) == 2
        except Exception as e:
            LOGGER.warning('parameter change_save_path length should be 2')
        cb = lambda x: construct_png_path(x, change_save_path[0], change_save_path[1])
        args = (frame_paths, cb)
    else:
        args = (frame_paths)

    cf_converter = ConcurrentConverter.cf_file_to_rgb_by_temperature_difference(*args)
    return cf_converter
