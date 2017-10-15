import logging
import os
import tkinter
from tkinter import filedialog

LOGGER = logging.getLogger(__name__)


class ThermalFileDialog(object):
    def __init__(self):
        super().__init__()

        self.root = tkinter.Tk()
        self._init_filedialog()

    def _init_filedialog(self):
        self.root.filename = filedialog.askopenfilenames(
            initialdir=os.path.abspath('.'),
            title='Select .txt ThermalCAM file',
            filetypes=(("text files", "*.txt"),)
        )

        if self.root.filename:
            LOGGER.info('Get image - {}'.format(self.root.filename))

    def mainloop(self):
        self.root.mainloop()
