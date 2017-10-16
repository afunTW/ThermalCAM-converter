import logging
from tkinter import ttk

LOGGER = logging.getLogger(__name__)

class TTKStyle(ttk.Style):
    def __init__(self, style_name, theme='alt', **kwargs):
        super().__init__()
        self.theme_use(theme)
        self.configure(style_name, **kwargs)

def init_css():
    TTKStyle('H1.TLabel', font=('',32, 'bold'), background='white')
    TTKStyle('H2.TLabel', font=('',24, 'bold'), background='white')
    TTKStyle('H3.TLabel', font=('',18), background='gray86')
    TTKStyle('H4.TLabel', font=('',16), background='gray86')
    TTKStyle('H5.TLabel', font=('',13), background='gray86')
    TTKStyle('H6.TLabel', font=('',10), background='gray86')
    TTKStyle('H1.TCheckbutton', font=('',32,'bold'), background='gray86')
    TTKStyle('H2.TCheckbutton', font=('',24,'bold'), background='gray86')
    TTKStyle('H3.TCheckbutton', font=('',18), background='gray86')
    TTKStyle('H4.TCheckbutton', font=('',16), background='gray86')
    TTKStyle('H5.TCheckbutton', font=('',13), background='gray86')
    TTKStyle('H6.TCheckbutton', font=('',10), background='gray86')
    TTKStyle('White.Horizontal.TScale', padding=20, background='gray86')