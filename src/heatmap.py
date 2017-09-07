"""
heatmap.py
    [class] HeatMap: define a heat map for transformation and operation
"""
import logging

from .color import ColorTransformation as c_trans
from .color import Palette


LOGGER = logging.getLogger(__name__)

class HeatMap(object):
    """
    Input and matrix in float and out put as image

    [Input] ndarray
    [Output] ndarray
    """
    def __init__(self, mat):
        self.mat = mat
        self.mat_row, self.mat_col = len(mat), len(mat[0])
        self.palette = Palette()
        self._heat_min = min(min(t for t in row) for row in mat)
        self._heat_max = max(max(t for t in row) for row in mat)

    @property
    def heat_min(self):
        return self._heat_min

    @property
    def heat_max(self):
        return self._heat_max

    def transform_to_rgb(self):
        rgb_mat = []
        for row in self.mat:
            rgb_row = [
                list(c_trans.color_transformation(
                    col, self._heat_min, self._heat_max, self.palette.temperature_rgb))
                for col in row
            ]
            rgb_mat.append(rgb_row)
        return rgb_mat

    def transform_to_gray(self):
        gray_mat = []
        # print(list(c_trans.color_transformation(31, 25, 32, self.palette.temperature_rgb)))
        # print([c_trans.gray_transformation(31, 25, 32, self.palette.grayscale)])
        for row in self.mat:
            gray_row = [
                c_trans.gray_transformation(
                    col, self._heat_min, self._heat_max, self.palette.grayscale)
                for col in row
            ]
            gray_mat.append(gray_row)
        return gray_mat

