# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 22:35:23 2021

@author: marcu
"""
import sys
sys.path.append("D:\\Users\\Marcus\\Documents\\R Documents\\Coding\\Python\\Packages")
import tkinter as tk
from PIL import Image, ImageTk
from mh_logging import log_class
import tk_arrange as tka
from sqlite_tablecon import TableCon

import global_const as g
import futil
log_class = log_class(g.LOG_LEVEL)

class OctaveFrameBase:
    """ Base tk.Frame with Octave logo and title bar """
    @log_class
    def __init__(self, master, title = "Octave"):
        self.master = master
        self.widget_frame = tk.Frame(self.master, bg = g.COLOUR_BACKGROUND)
        """ Draw logo"""
        with Image.open(".\common\Octave Logo.png") as image:
            self.img_logo = ImageTk.PhotoImage(image.resize((100, 100)))
            self.img_logo_padded = ImageTk.PhotoImage(
                futil.pad_image_with_transparency(
                    image.resize((85, 85)), 15, keep_size = False
                    )
                )
        self.title = tk.Label(
            self.widget_frame,
            text = title,
            background = g.COLOUR_TITLEBAR,
            foreground = g.COLOUR_OFFWHITE_TEXT,
            padx = 20,
            font = g.FONT_OCTAVE_TITLE,
            anchor = "w",
            )
        self.logo = tk.Label(
            self.widget_frame,
            image = self.img_logo_padded,
            background = g.COLOUR_TITLEBAR,
            anchor = "w", padx = 20,
            )

        widgets = {1: {'widget': self.logo,
                       'grid_kwargs': g.GRID_STICKY},
                   2: {'widget': self.title,
                       'grid_kwargs': g.GRID_STICKY,
                       'stretch_width': True},
                   }
        self.widget_set = tka.WidgetSet(
            self.widget_frame, widgets, layout = [1, 2])

        self.widget_set.grid(row = 0, column = 0, **g.GRID_STICKY)
        self.master.rowconfigure(0, weight = 1)
        self.master.columnconfigure(0, weight = 1)

    @log_class
    def grid(self, **kwargs):
        self.widget_set.grid(**kwargs)

class OctaveWindowBase:
    """ Toplevel window with OctaveFrameBase """
    @log_class
    def __init__(self, master, title = "Octave"):
        self.master = master
        self.window = tk.Toplevel(self.master, bg = g.COLOUR_BACKGROUND)
        self.master.eval(f'tk::PlaceWindow {self.window} center')
        self.title_bar = OctaveFrameBase(self.window, title = title)
        self.title_bar.grid(row = 0, column = 0, **g.GRID_STICKY)

    @log_class
    def start(self):
        # self.window.transient(self.master)
        self.window.grab_set()
        self.window.mainloop()

class OctaveConnections:
    def __init__(self, db, tables = None):
        self.db = db
        if tables is None:
            raise AttributeError("At least one table must be specified")
        elif not isinstance(tables, list):
            tables = [tables]

        for table in tables:
            self.__dict__[table] = TableCon(db = db, table = table,
                                            debug = g.DEBUG)

octave_db = OctaveConnections(r".\data\octave_sqlite.db",
                              ["books", "records", "tags"])