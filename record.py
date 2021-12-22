# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 23:16:08 2021

@author: marcu
"""

import sys
sys.path.append("D:\\Users\\Marcus\\Documents\\R Documents\\Coding\\Python\\Packages")
import tkinter as tk
from mh_logging import log_class
import tk_arrange as tka

from sqlite_tablecon import TableCon
import global_const as g
import futil
log_class = log_class(g.LOG_LEVEL)
from base import OctaveFrameBase, OctaveWindowBase, octave_db


class OctaveRecord(OctaveWindowBase):
    @log_class
    def __init__(self, master, title = "Octave"):
        self.master = master
        self.title = title
        super().__init__(self.master, self.title)

        self.widget_frame = tk.Frame(self.window, bg = g.COLOUR_BACKGROUND)

        """ Book dropdown """
        bk_dd_label = tk.Label(
            self.widget_frame, text = "Select book", **g.LBL_STD_ARGS)
        bk_dd_options = octave_db.books.select(
            "SELECT book_id, book_name FROM books")
        if bk_dd_options == []: #TODO test this
            bk_dd_options = ["No books created yet"]
        self.book_dd_var = tk.StringVar(self.master)
        self.book_dropdown = tk.OptionMenu(
            self.widget_frame, self.book_dd_var, *bk_dd_options)

        """ Buttons """
        self.btn_add_book = tk.Button(
            self.widget_frame,
            text = "Create new book",
            command = self.test_cmd,
            **g.BTN_STD_ARGS
            )

        widgets = {1: {'widget': self.title_bar,
                       'grid_kwargs': g.GRID_STICKY},
                   2: {'widget': bk_dd_label,
                       'grid_kwargs': g.GRID_STICKY},
                   3: {'widget': self.book_dropdown,
                       'grid_kwargs': g.GRID_STICKY,
                       'stretch_width': True},
                   4: {'widget': self.btn_add_book,
                       'grid_kwargs': g.GRID_STICKY},
                   }
        self.widget_set = tka.WidgetSet(self.widget_frame, widgets, layout = [1, [2, 3, 4]])
        self.widget_set.grid(row = 1, column = 0, **g.GRID_STICKY)
        self.window.columnconfigure(0, weight = 1)
        self.window.rowconfigure(1, weight = 1)

    @log_class
    def test_cmd(self, event = None):
        print("tsetsg")

    @log_class
    def get_book(self):
        return self.book_dd_var.get()