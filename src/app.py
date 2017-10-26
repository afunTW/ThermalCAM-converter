import glob
import logging
import os
import time
import tkinter
from tkinter import filedialog, ttk

from .msg_box import MessageBox
from .tkcomponent import TkFrame
from .ttkcomponent import TTKStyle, init_css
from .wrapper import cf_convert_to_grayscale, cf_convert_to_rgb

LOGGER = logging.getLogger(__name__)
COLORMAP = [('RGB', 'rgb'), ('Gray', 'gray')]


class ThermalViewer(object):
    def __init__(self, open_filenames=None, save_directory=None):
        super().__init__()
        self.open_directory = open_filenames
        self.save_directory = save_directory
        self.total_count = len(open_filenames) if self.open_directory else 0
        self.done_count = 0
        self.root = None

        self._init_windows()
        # self._open_filedialog()

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
        self.val_colormap.set('rgb')
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
            text='Total file: {}/{}'.format(self.done_count, self.total_count),
            style='H2.TLabel'
        )
        self.label_state.grid(row=0, column=0, sticky='news')
        self._sync_state()

    def _sync_state(self):
        self.label_state.config(text='Total file: {}/{}'.format(self.done_count, self.total_count))
        if self.root is not None and 'normal' == self.root.state():
            self.label_state.after(10, self._sync_state)

    def _open_filedialog(self):
        self.open_directory = filedialog.askdirectory(
            parent=self.root,
            initialdir=os.path.abspath('.'),
            title='Choose Directory to load ThermalCAM .txt',
        )

        if self.open_directory:
            self.label_load_path.config(text=self.open_directory)
            self.open_filenames = glob.glob(os.path.join(self.open_directory, '*.txt'))
            self.total_count = len(self.open_filenames)
            LOGGER.info('Load {} file from - {}'.format(self.total_count, self.open_directory))

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
        self.convert_mode = None
        self.flag_multiprocess = multiprocess
        self.btn_load.config(command=self._choose_load_path)
        self.btn_ok.config(command=self.run)
        self._sync_generate_save_path()

    def _sync_state(self):
        if self.save_directory and os.path.exists(self.save_directory):
            self.done_count = len(os.listdir(self.save_directory))

        msg = ''
        if self.convert_mode is None:
            msg = u'N/A'
        elif self.convert_mode == 'convert':
            msg = u'轉換中'
        elif self.convert_mode == 'done':
            msg = u'已轉換完成'
        self.label_state.config(text=u'共 {} 份文件 - {}'.format(self.total_count, msg))

        if self.root is not None and 'normal' == self.root.state():
            self.root.update()
            self.label_state.after(10, self._sync_state)

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

    def mainloop(self):
        self.root.mainloop()

    def run(self):
        if self.open_filenames:
            self._init_frame_footer()
            self._disable_all_checkbtn()

            if self.val_colormap.get() == 'rgb':
                self.convert_mode = 'convert'
                self._sync_state()
                self.root.update()
                mod_savedir = '{}_{}'.format(self.open_directory.split(os.sep)[-1], self.val_colormap.get())
                cf_convert_to_rgb(self.open_directory, (-2, mod_savedir))
                self.convert_mode = 'done'
                # self.root.destroy()
            elif self.val_colormap.get() == 'gray':
                self.convert_mode = 'convert'
                self._sync_state()
                self.root.update()
                mod_savedir = '{}_{}'.format(self.open_directory.split(os.sep)[-1], self.val_colormap.get())
                cf_convert_to_grayscale(self.open_directory, (-2, mod_savedir))
                self.convert_mode = 'done'
                Mbox = MessageBox()
                Mbox.info(string=u'已完成, 按確認關閉視窗', parent=self.root)
                # self.root.destroy()
