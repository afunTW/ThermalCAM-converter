"""
convert.py
    [class] Converter
"""
import logging
from concurrent.futures import ProcessPoolExecutor
from os import listdir, makedirs, sep
from os.path import abspath, dirname, exists, join

import cv2
import numpy as np

from .heatmap import HeatMap

LOGGER = logging.getLogger(__name__)

class Converter(object):
    """
    Converter from typeto type by condition
    """
    def __init__(self):
        super().__init__()
    def _template_iter_tuple(self, func, l, index):
        return func(_[index] for _ in l)

    def _hough_circles_width(self, l):
        return self._template_iter_tuple(max, l, 0) - self._template_iter_tuple(min, l, 0)

    def _hough_circles_height(self, l):
        return self._template_iter_tuple(max, l, 1) - self._template_iter_tuple(min, l, 1)

    @staticmethod
    def file_to_heatmap(file_path):
        np_heat_map = np.loadtxt(open(file_path, 'rb'), delimiter=',', skiprows=1)
        heat_map = HeatMap(np_heat_map)
        return heat_map

    @staticmethod
    def file_to_rgb(file_path):
        heat_map = Converter.file_to_heatmap(file_path)
        np_heat_rgb = np.array(heat_map.transform_to_rgb(), np.uint8)
        return np_heat_rgb

    @staticmethod
    def file_to_grayscale(file_path):
        heat_map = Converter.file_to_heatmap(file_path)
        np_heat_gray = np.array(heat_map.transform_to_gray(), np.uint8)
        return np_heat_gray

    @staticmethod
    def file_to_rgb_by_hough_circle(file_path, draw_circle=False):
        """
        Find the anchor by Hough Circles
        ref: http://www.pyimagesearch.com/2014/07/21/detecting-circles-images-using-opencv-hough-circles/
        [Input] file path
        [Output] (ndarray) rgb image
        """
        np_heat_rgb = Converter.file_to_rgb(file_path)
        np_heat_gray = cv2.cvtColor(np_heat_rgb, cv2.COLOR_RGB2GRAY)
        heat_map_circle = cv2.HoughCircles(np_heat_gray, cv2.HOUGH_GRADIENT, 1, 10,
                                            param1=100,
                                            param2=22,
                                            minRadius=0,
                                            maxRadius=25)

        if heat_map_circle is None:
            return
        if heat_map_circle.shape[1] < 4:
            return

        heat_map_circle = heat_map_circle[0]
        LOGGER.info('{}: circle_count = {}'.format(file_path, len(heat_map_circle),))

        if draw_circle:
            for c in heat_map_circle:
                cv2.circle(np_heat_rgb, (c[0], c[1]), c[2], (0, 0, 0), 1)
                cv2.circle(np_heat_rgb, (c[0], c[1]), 2, (255, 255, 255), 1)

        return np_heat_rgb

    @staticmethod
    def find_heatmap_by_temperature_difference(paths):
        """
        Find the maximum temperature difference from matrices
        [Input] file paths
        [Output] (ndarray) maximumn temperature difference heat map
        """
        max_variation = None
        temperature_diff = lambda x,y: abs(y-x)

        for i, obj in enumerate(paths):
            heat_map = Converter.file_to_heatmap(obj)

            # boundary condition
            if max_variation is None:
                max_variation = heat_map
                LOGGER.info('{}: iter {} heat_min={} heat_max={}'.format(
                    obj, i, max_variation.heat_min, max_variation.heat_max
                ))
                continue

            # condition
            target = temperature_diff(max_variation.heat_min, max_variation.heat_max)
            current = temperature_diff(heat_map.heat_min, heat_map.heat_max)
            if current > target:
                max_variation = heat_map
                LOGGER.info('{}: iter {} heat_min={} heat_max={}'.format(
                    obj, i, max_variation.heat_min, max_variation.heat_max
                ))

        return max_variation

    @staticmethod
    def find_rgb_by_temperature_difference(paths):
        heatmap_max_difference = Converter.find_heatmap_by_temperature_difference(paths)
        rgb = heatmap_max_difference.transform_to_rgb()
        return rgb

class ConcurrentConverter(Converter):
    """
    Converter from typeto type by condition with concurrent.feature
    """
    def __init__(self):
        super().__init__()

    def calc_temperature_difference_by_file(self, path):
        heatmap = self.file_to_heatmap(path)
        return heatmap.heat_max - heatmap.heat_min

    @staticmethod
    def cf_file_to_grayscale(paths, cb_save=None):
        with ProcessPoolExecutor(max_workers=7) as executor:
            cf_converter = ConcurrentConverter()
            cf_func = cf_converter.file_to_grayscale

            if cb_save is not None:
                for path, temp in zip(paths, executor.map(cf_func, paths)):
                    saved_path = cb_save(path)
                    if not exists(dirname(saved_path)):
                        makedirs(dirname(saved_path))

                    LOGGER.info('Saved final result in {}'.format(saved_path))
                    cv2.imwrite(saved_path, temp)
            else:
                return zip(paths, executor.map(cf_func, paths))

    @staticmethod
    def cf_file_to_rgb(paths, cb_save=None):
        with ProcessPoolExecutor(max_workers=7) as executor:
            cf_converter = ConcurrentConverter()
            cf_func = cf_converter.file_to_rgb

            if cb_save is not None:
                for path, temp in zip(paths, executor.map(cf_func, paths)):
                    saved_path = cb_save(path)
                    if not exists(dirname(saved_path)):
                        makedirs(dirname(saved_path))

                    LOGGER.info('Saved final result in {}'.format(saved_path))
                    cv2.imwrite(saved_path, temp)
            else:
                return zip(paths, executor.map(cf_func, paths))

    @staticmethod
    def cf_file_to_rgb_by_hough_circle(paths, draw_circle=False, cb_save=None):
        """
        1. set the path
        2. multiprocess converting by hough circle
        """
        with ProcessPoolExecutor(max_workers=7) as executor:
            convert_by = ConcurrentConverter.file_to_rgb_by_hough_circle
            args = (paths, [draw_circle]*len(paths))

            if cb_save is None:
                return zip(paths, executor.map(convert_by,*args))

            try:
                # convert if hough circle meet the condition
                for frame_path, heat_img in zip(paths, executor.map(convert_by,*args)):
                    saved_path = cb_save(frame_path)
                    if not exists(dirname(saved_path)):
                        makedirs(dirname(saved_path))

                    if heat_img is not None:
                        LOGGER.info('Saved {}'.format(saved_path))
                        rgb_to_bgr = cv2.cvtColor(heat_img, cv2.COLOR_RGB2BGR)
                        cv2.imwrite(saved_path, rgb_to_bgr)
                    else:
                        LOGGER.info('{} is None'.format(frame_path))

                return True
            except Exception as e:
                LOGGER.exception('{}'.format(e))
                return False

    @staticmethod
    def cf_file_to_rgb_by_temperature_difference(paths, cb_save=None):
        """
        1. calc all temperature difference
        2. convert the maximum variance matrix to rgb
        TODO: read the target matrix once and multiprocessing at the same time
        """
        file_max_difference = None

        with ProcessPoolExecutor(max_workers=7) as executor:
            cf_converter = ConcurrentConverter()
            cf_func = cf_converter.calc_temperature_difference_by_file

            for path, temp_diff in zip(paths, executor.map(cf_func, paths)):
                if file_max_difference is None:
                    LOGGER.info('{} with temperature difference {}'.format(path, temp_diff))
                    file_max_difference = (path, temp_diff)
                elif temp_diff > file_max_difference[1]:
                    LOGGER.info('{} with temperature difference {}'.format(path, temp_diff))
                    file_max_difference = (path, temp_diff)
                else:
                    pass

            LOGGER.info('Final path={} temperature_diff={}'.format(
                file_max_difference[0],
                file_max_difference[1]
            ))
            rgb_max_difference = ConcurrentConverter.file_to_rgb(file_max_difference[0])

            if cb_save is not None:
                saved_path = cb_save(file_max_difference[0])
                if not exists(dirname(saved_path)):
                    makedirs(dirname(saved_path))

                LOGGER.info('Saved final result in {}'.format(saved_path))
                rgb_to_bgr = cv2.cvtColor(rgb_max_difference, cv2.COLOR_RGB2BGR)
                cv2.imwrite(saved_path, rgb_to_bgr)

            return rgb_max_difference

    @staticmethod
    def cf_file_to_grayscale_by_temperature_difference(paths, cb_save=None):
        """
        1. calc all temperature difference
        2. convert the maximum variance matrix to rgb
        TODO: read the target matrix once and multiprocessing at the same time
        """
        file_max_difference = None

        with ProcessPoolExecutor(max_workers=7) as executor:
            cf_converter = ConcurrentConverter()
            cf_func = cf_converter.calc_temperature_difference_by_file

            for path, temp_diff in zip(paths, executor.map(cf_func, paths)):
                if file_max_difference is None:
                    LOGGER.info('{} with temperature difference {}'.format(path, temp_diff))
                    file_max_difference = (path, temp_diff)
                elif temp_diff > file_max_difference[1]:
                    LOGGER.info('{} with temperature difference {}'.format(path, temp_diff))
                    file_max_difference = (path, temp_diff)
                else:
                    pass

            LOGGER.info('Final path={} temperature_diff={}'.format(
                file_max_difference[0],
                file_max_difference[1]
            ))
            gray_max_difference = ConcurrentConverter.file_to_grayscale(file_max_difference[0])

            if cb_save is not None:
                saved_path = cb_save(file_max_difference[0])
                if not exists(dirname(saved_path)):
                    makedirs(dirname(saved_path))

                LOGGER.info('Saved final result in {}'.format(saved_path))
                cv2.imwrite(saved_path, gray_max_difference)

            return gray_max_difference
