"""
image
    [class] BaseImage: collect basic image operation function
"""
import time
import logging

import cv2
import numpy as np
import matplotlib.pyplot as plt


LOGGER = logging.getLogger(__name__)

class BaseImage(object):
    """
    Base image operation with cv2
    """
    def __init__(self, img):
        super().__init__()
        self._original = img
        self.image = img

    @property
    def original_image(self):
        return self._original

    @staticmethod
    def show_image_by_plt(img, maximize_window=True):
        """
        show image by matplotlib.pyplot
        """
        plt.imshow(img)
        if maximize_window:
            mng = plt.get_current_fig_manager()
            mng.resize(*mng.window.maxsize())
        plt.show()

    @staticmethod
    def get_gamma_image(img, gamma):
        """
        modified image by gamma
        """
        try:
            assert isinstance(img, np.ndarray) and len(img.shape) == 3
            img[:] /= 255
            img[:] = img[:]**(gamma)
            img[:] *= 255
            return img
        except Exception as e:
            LOGGER.exception(e)

class BaseImageCV(BaseImage):
    def __init__(self, img):
        super().__init__(img)

    @staticmethod
    def show_image_by_cv2(img, exit_code=27):
        """
        show image by cv2
        """
        winname = str(hash(time.time()))
        cv2.namedWindow(winname)
        while True:
            cv2.imshow(winname, img)
            k = cv2.waitKey(0)
            if k == exit_code:
                break
        cv2.destroyAllWindows()

    @staticmethod
    def get_component_by(threshold, nth, by):
        '''
        return nth connected component by the value in stat matrix
        in descending sequences
            cv2.CC_STAT_LEFT The leftmost (x) coordinate
            cv2.CC_STAT_TOP The topmost (y) coordinate
            cv2.CC_STAT_WIDTH The horizontal size of the bounding box
            cv2.CC_STAT_HEIGHT The vertical size of the bounding box
            cv2.CC_STAT_AREA The total area (in pixels) of the connected component
        '''
        output = cv2.connectedComponentsWithStats(threshold, 4, cv2.CV_32S)
        assert by in [
            cv2.CC_STAT_LEFT, cv2.CC_STAT_TOP,
            cv2.CC_STAT_WIDTH, cv2.CC_STAT_HEIGHT, cv2.CC_STAT_AREA]
        if 0 >= nth or nth >= output[0]: return

        cond_sequence = [(i ,output[2][i][by]) for i in range(output[0]) if i != 0]
        cond_sequence = sorted(cond_sequence, key=lambda x: x[1], reverse=True)
        return np.where(output[1] == cond_sequence[nth-1][0])