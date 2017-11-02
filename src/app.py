import glob
import logging
import os
import time
import tkinter
from tkinter import filedialog, ttk

import cv2

from .convert import Converter
from .msg_box import MessageBox
from .tkcomponent import TkFrame
from .ttkcomponent import TTKStyle, init_css

LOGGER = logging.getLogger(__name__)
COLORMAP = [('RGB', 'rgb'), ('Gray', 'gray')]


class ThermalViewer(object):
    def __init__(self, open_filenames=None, save_directory=None):
        super().__init__()
        self.open_directory = open_filenames
        self.save_directory = save_directory
        self.root = None

        self._init_windows()
        self._init_style()

    # set grid all column configure
    def set_all_grid_columnconfigure(self, widget, *cols):
        for col in cols:
            widget.grid_columnconfigure(col, weight=1)

    # set grid all row comfigure
    def set_all_grid_rowconfigure(self, widget, *rows):
        for row in rows:
            widget.grid_rowconfigure(row, weight=1)

    def _init_windows(self):
        self.root = tkinter.Tk()
        self.root.wm_title(time.ctime())
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self._init_frame()
        self._init_frame_footer()

    def _init_style(self):
        init_css()
        TTKStyle('H5Bold.TLabel', font=('', 13, 'bold'))

    def _init_frame(self):
        # root
        self.frame_root = TkFrame(self.root)
        self.frame_root.grid(row=0, column=0, sticky='news')
        self.set_all_grid_rowconfigure(self.frame_root, 0, 1)
        self.set_all_grid_columnconfigure(self.frame_root, 0)

        # root > body
        self.frame_body = TkFrame(self.frame_root)
        self.frame_body.grid(row=0, column=0, sticky='news')
        self.set_all_grid_rowconfigure(self.frame_body, 0, 1)
        self.set_all_grid_columnconfigure(self.frame_body, 0)

        # root > body > option
        self.frame_option = TkFrame(self.frame_body)
        self.frame_option.grid(row=0, column=0, sticky='news')
        self.set_all_grid_rowconfigure(self.frame_option, 0, 1, 2)
        self.set_all_grid_columnconfigure(self.frame_option, *[i for i in range(len(COLORMAP)+1)])

        # root > body > load
        self.frame_load = TkFrame(self.frame_body)
        self.frame_load.grid(row=1, column=0, sticky='news')
        self.set_all_grid_rowconfigure(self.frame_load, 0)
        self.set_all_grid_columnconfigure(self.frame_load, 0)

        self._init_widget_body()

    def _init_frame_footer(self):
        # root > footer
        self.frame_footer = TkFrame(self.frame_root)
        self.frame_footer.grid(row=1, column=0, sticky='news')
        self.set_all_grid_rowconfigure(self.frame_footer, 0)
        self.set_all_grid_columnconfigure(self.frame_footer, 0)

        # root > footer > state
        self.frame_state = TkFrame(self.frame_footer)
        self.frame_state.grid(row=0, column=0, sticky='news')
        self.set_all_grid_rowconfigure(self.frame_state, 0)
        self.set_all_grid_columnconfigure(self.frame_state, 0)

        self._init_widget_state()

    def _init_widget_body(self):
        TTKStyle('H5.TLabel', font=('', 13))
        TTKStyle('Title.TLabel', font=('', 13, 'bold'))
        TTKStyle('H5.TButton', font=('', 13))
        TTKStyle('H5.TRadiobutton', font=('', 13))

        # frame_option
        self.label_option = ttk.Label(self.frame_option, text=u'請選擇 colour map: ', style='Title.TLabel')
        self.label_option.grid(row=0, column=0, sticky='w')
        self.val_colormap = tkinter.StringVar()
        self.val_colormap.set('gray')
        self.radiobtn = []
        for i, colourmap in enumerate(COLORMAP):
            text, mode = colourmap
            radiobtn = ttk.Radiobutton(self.frame_option, text=text, variable=self.val_colormap, value=mode, style='H5.TRadiobutton')
            radiobtn.grid(row=0, column=i+1, sticky='w')
            self.radiobtn.append(radiobtn)

        self.label_load = ttk.Label(self.frame_option, text=u'載入路徑: ', style='Title.TLabel')
        self.label_load.grid(row=1, column=0, sticky='w')
        self.label_load_path = ttk.Label(self.frame_option, text=u'N/A', style='H5.TLabel')
        self.label_load_path.grid(row=1, column=1, sticky='w', columnspan=len(COLORMAP)+1)
        self.label_save = ttk.Label(self.frame_option, text=u'儲存路徑: ', style='Title.TLabel')
        self.label_save.grid(row=2, column=0, sticky='w')
        self.label_save_path = ttk.Label(self.frame_option, text=u'N/A', style='H5.TLabel')
        self.label_save_path.grid(row=2, column=1, sticky='w', columnspan=len(COLORMAP)+1)

        # frame_load
        self.btn_load = ttk.Button(self.frame_load, text=u'載入資料夾', style='H5.TButton')
        self.btn_load.grid(row=0, column=0, sticky='e')
        self.btn_ok = ttk.Button(self.frame_load, text=u'開始轉換', style='H5.TButton')
        self.btn_ok.grid(row=0, column=1, sticky='e')

    def _init_widget_state(self):
        TTKStyle('H2.TLabel', font=('', 24, 'bold'))

        # frame_state
        self.label_state = ttk.Label(
            self.frame_state,
            text=u'共 N/A 份文件 - 準備中',
            style='H5Bold.TLabel'
        )
        self.label_state.grid(row=0, column=0, sticky='news')

    def _open_filedialog(self):
        self.open_directory = filedialog.askdirectory(
            parent=self.root,
            initialdir=os.path.abspath('.'),
            title='Choose Directory to load ThermalCAM .txt',
        )

        if self.open_directory:
            self.label_load_path.config(text=self.open_directory)
            self.open_filenames = glob.glob(os.path.join(self.open_directory, '*.txt'))
            self.label_state.config(text=u'共 {} 份文件 - 準備中'.format(len(self.open_filenames)))
            LOGGER.info('Load {} file from - {}'.format(len(self.open_filenames), self.open_directory))

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
        """"self.save_directory is useless"""
        super().__init__(open_filenames, save_directory)
        self.flag_multiprocess = multiprocess
        self.btn_load.config(command=self._choose_load_path)
        self.btn_ok.config(command=self.run)
        self._sync_generate_save_path()

    def _sync_generate_save_path(self):
        if self.open_directory and self.val_colormap.get():
            suffix = self.val_colormap.get()
            save_path = self.open_directory.split(os.sep)
            save_path[-1] = '{}_{}'.format(save_path[-1], suffix)
            self.save_directory = os.sep.join(save_path)
            self.label_save_path.config(text=self.save_directory)

        if self.root and 'normal' == self.root.state():
            self.root.after(10, self._sync_generate_save_path)

    def _choose_load_path(self):
        self._enable_all_checkbtn()
        self._open_filedialog()

    def _enable_all_checkbtn(self):
        for radiobtn in self.radiobtn:
            radiobtn.config(state=tkinter.ACTIVE)

    def _disable_all_checkbtn(self):
        for radiobtn in self.radiobtn:
            radiobtn.config(state=tkinter.DISABLED)

    def _gen_save_path(self, x, suffix):
        x = x.split(os.sep)
        directory, filename = os.sep.join(x[:-1]), x[-1]
        directory = '{}_{}'.format(directory, suffix)
        filename = '{}.jpg'.format(filename.split('.')[0])
        x = os.path.join(directory, filename)
        return x

    def _convert_to(self, func, cb_path):
        for i, txt in enumerate(self.open_filenames):
            save_path = cb_path(txt)
            save_dir_path = os.sep.join(save_path.split(os.sep)[:-1])
            img = func(txt)

            if not os.path.exists(save_dir_path):
                os.makedirs(save_dir_path)

            cv2.imwrite(save_path, img)
            LOGGER.info('Save - {}'.format(save_path))
            self.label_state.config(text=u'共 {}/{} 份文件 - 轉換中'.format(i+1, len(self.open_filenames)))
            self.root.update()

    def mainloop(self):
        self.root.mainloop()

    def run(self):
        if self.open_filenames:
            self._disable_all_checkbtn()

            if self.val_colormap.get() == 'rgb':
                mod_savedir = '{}_{}'.format(self.open_directory.split(os.sep)[-1], self.val_colormap.get())
                cb = lambda x: self._gen_save_path(x, 'rgb')
                self._convert_to(Converter.file_to_rgb, cb)
            elif self.val_colormap.get() == 'gray':
                mod_savedir = '{}_{}'.format(self.open_directory.split(os.sep)[-1], self.val_colormap.get())
                cb = lambda x: self._gen_save_path(x, 'gray')
                self._convert_to(Converter.file_to_grayscale, cb)

            Mbox = MessageBox()
            Mbox.info(string=u'已完成, 按確認關閉視窗', parent=self.root)
