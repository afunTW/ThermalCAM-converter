import glob
import logging
import os
import time
import tkinter
from tkinter import filedialog, ttk

from .tkcomponent import TkFrame
from .ttkcomponent import TTKStyle, init_css
from .wrapper import cf_convert_to_rgb

LOGGER = logging.getLogger(__name__)


class ThermalViewer(object):
    def __init__(self, open_filenames=None, save_directory=None):
        super().__init__()
        self.open_directory = open_filenames
        self.save_directory = save_directory
        self.total_count = len(open_filenames) if self.open_directory else 0
        self.done_count = 0

        self._init_windows()
        self._open_filedialog()

    def _init_windows(self):
        self.root = tkinter.Tk()
        self.root.wm_title(time.ctime())
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self._init_frame()

    def _init_frame(self):
        self.frame_root = TkFrame(self.root)
        self.frame_root.grid(row=0, column=0)
        self.frame_root.grid_rowconfigure(0, weight=1)
        self.frame_root.grid_columnconfigure(0, weight=1)
        self._init_component()

    def _init_component(self):
        TTKStyle('H2.TLabel', font=('',24, 'bold'))

        self.label_state = ttk.Label(
            self.frame_root,
            text='Total file: {}/{}'.format(self.done_count, self.total_count),
            style='H2.TLabel'
        )
        self.label_state.grid(row=0, column=0, sticky='news')
        self._sync_component()

    def _sync_component(self):
        self.label_state.config(text='Total file: {}/{}'.format(self.done_count, self.total_count))
        self.label_state.after(10, self._sync_component)

    def _open_filedialog(self):
        self.open_directory = filedialog.askdirectory(
            parent=self.root,
            initialdir=os.path.abspath('.'),
            title='Choose Directory to load ThermalCAM .txt',
        )
        self.open_filenames = glob.glob(os.path.join(self.open_directory, '*.txt'))

        if self.open_directory:
            self.total_count = len(self.open_filenames)
            LOGGER.info('Load {} file from - {}'.format(self.total_count, self.open_directory))
            self._save_filedialog()

    def _save_filedialog(self):
        self.save_directory = filedialog.askdirectory(
            parent=self.root,
            initialdir=os.path.abspath('.'),
            title='Choose Directory to save'
        )

        if self.save_directory:
            LOGGER.info('Save image to - {}'.format(self.save_directory))

    def mainloop(self):
        self.root.mainloop()

class ThermalAction(ThermalViewer):
    def __init__(self, open_filenames=None, save_directory=None, multiprocess=True):
        super().__init__(open_filenames, save_directory)
        self._sync_component()

        self.flag_multiprocess = multiprocess
        self.run()

    def _sync_component(self):
        if self.save_directory:
            mod_savedir = self.save_directory.split(os.sep)
            mod_savedir[-1] += '_img'
            mod_savedir = os.sep.join(mod_savedir)
            self.done_count = len(os.listdir(mod_savedir)) if os.path.exists(mod_savedir) else self.done_count
        self.label_state.config(text='Total file: {}/{}'.format(self.done_count, self.total_count))
        self.label_state.after(10, self._sync_component)

    def mainloop(self):
        self.root.mainloop()

    def run(self):
        if self.open_filenames and self.save_directory:
            mod_savedir = self.save_directory.split(os.sep)[-1] + '_img'
            cf_convert_to_rgb(self.save_directory, (-2, mod_savedir))
            self.root.destroy()
