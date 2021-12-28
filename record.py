# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 23:16:08 2021

@author: marcu
"""

import sys
sys.path.append("D:\\Users\\Marcus\\Documents\\R Documents\\Coding\\Python\\Packages")
import tkinter as tk
from pygame import midi
midi.init()

from mh_logging import log_class
import tk_arrange as tka

import global_const as g
log_class = log_class(g.LOG_LEVEL)
from base import OctaveWindowBase, octave_db
from midi_connection import MidiConnection
from midi_plot import MidiPlot

class OctaveRecord(OctaveWindowBase):
    @log_class
    def __init__(self, master, title = "Octave"):
        self.master = master
        self.title = title
        super().__init__(self.master, self.title)

        self.midi_connection = MidiConnection()

        self.widget_frame = tk.Frame(self.window, bg = g.COLOUR_BACKGROUND)

        """ Book dropdown """
        bk_dd_label = tk.Label(
            self.widget_frame, text = "Select book", **g.LBL_STD_ARGS)

        bk_dd_options = ["None"]
        for book in octave_db.books.select("SELECT book_id, book_name FROM books"):
            bk_dd_options.append('%s - %s' % book)

        self.book_dd_var = tk.StringVar(self.master)
        self.book_dd_var.set(bk_dd_options[0])
        self.book_dropdown = tk.OptionMenu(
            self.widget_frame, self.book_dd_var, *bk_dd_options)
        self.book_dropdown.config(
            font = g.FONT_TEXT_DEFAULT, bg = g.COLOUR_INTERFACE_BUTTON)

        """ Buttons """
        self.btn_add_book = tk.Button(
            self.widget_frame,
            text = "Create new book",
            command = self.add_book,
            **g.BTN_LIGHT_ARGS
            )
        self.btn_save_record = tk.Button(
            self.widget_frame,
            text = "Save record",
            command = self.save_record,
            **g.BTN_LIGHT_ARGS
            )

        buttons = {1: {"name": "btn_start_recording",
                       "label": "Start recording",
                       "bindings": {"event": "<1>",
                                    "function": self.start_recording
                                    },
                       "widget_kwargs": g.BTN_LIGHT_ARGS,
                       "grid_kwargs": g.GRID_STICKY,
                       "stretch_width": True},
                   2: {"name": "btn_stop_recording",
                       "label": "Stop recording",
                       "bindings": {"event": "<1>",
                                    "function": self.stop_recording
                                    },
                       "widget_kwargs": g.BTN_LIGHT_ARGS,
                       "grid_kwargs": g.GRID_STICKY,
                       "stretch_width": True},
                   3: {"name": "btn_start_playback",
                       "label": "Start playback",
                       "bindings": {"event": "<1>",
                                    "function": self.start_playback
                                    },
                       "widget_kwargs": g.BTN_LIGHT_ARGS,
                       "grid_kwargs": g.GRID_STICKY,
                       "stretch_width": True},
                   4: {"name": "btn_stop_playback",
                       "label": "Stop playback",
                       "bindings": {"event": "<1>",
                                    "function": self.stop_playback
                                    },
                       "widget_kwargs": g.BTN_LIGHT_ARGS,
                       "grid_kwargs": g.GRID_STICKY,
                       "stretch_width": True},
                   }

        self.button_set = tka.ButtonSet(
            master = self.widget_frame,
            buttons = buttons,
            layout = [[1, 2, 3, 4]],
            frm_kwargs = {"bg": g.COLOUR_BACKGROUND}
            )

        self.button_set.btn_start_recording["state"] = tk.NORMAL
        self.button_set.btn_stop_recording["state"] = tk.DISABLED
        self.button_set.btn_start_playback["state"] = tk.NORMAL
        self.button_set.btn_stop_playback["state"] = tk.DISABLED

        self.midi_plot = MidiPlot(self.widget_frame, self.midi_connection)

        widgets = {1: {'widget': self.title_bar,
                       'grid_kwargs': g.GRID_STICKY,
                       'stretch_width': True},
                   2: {'widget': bk_dd_label,
                       'grid_kwargs': g.GRID_STICKY_PADDING_SMALL},
                   3: {'widget': self.book_dropdown,
                       'grid_kwargs': g.GRID_STICKY_PADDING_SMALL,
                       'stretch_width': True},
                   4: {'widget': self.btn_add_book,
                       'grid_kwargs': g.GRID_STICKY_PADDING_SMALL},
                   5: {'widget': self.btn_save_record,
                       'grid_kwargs': g.GRID_STICKY_PADDING_SMALL},
                   6: {'widget': self.button_set,
                       'grid_kwargs': g.GRID_STICKY_PADDING_SMALL,
                       'stretch_width': True},
                   7: {'widget': self.midi_plot,
                       'grid_kwargs': g.GRID_STICKY_PADDING_SMALL,
                       'stretch_width': True, 'stretch_height': True},
                   }
        self.widget_set = tka.WidgetSet(
            self.widget_frame, widgets,
            layout = [[1], [2, 3, 4, 5], [6], [7]]
            )
        self.widget_set.grid(row = 1, column = 0, **g.GRID_STICKY)
        self.window.columnconfigure(0, weight = 1)
        self.window.rowconfigure(1, weight = 1)

    @log_class
    def start_recording(self, event = None):
        self.button_set.btn_start_recording["state"] = tk.DISABLED
        self.button_set.btn_stop_recording["state"] = tk.NORMAL
        self.midi_connection.start_recording()

    @log_class
    def stop_recording(self, event = None):
        self.button_set.btn_start_recording["state"] = tk.NORMAL
        self.button_set.btn_stop_recording["state"] = tk.DISABLED
        self.midi_connection.stop_recording()

    @log_class
    def start_playback(self, event = None):
        self.button_set.btn_start_playback["state"] = tk.DISABLED
        self.button_set.btn_stop_playback["state"] = tk.NORMAL

    @log_class
    def stop_playback(self, event = None):
        self.button_set.btn_start_playback["state"] = tk.NORMAL
        self.button_set.btn_stop_playback["state"] = tk.DISABLED

    @log_class
    def add_book(self, event = None):
        print("add_book")

    @log_class
    def get_book(self):
        return self.book_dd_var.get()

    @log_class
    def save_record(self, event = None):
        print("save_record")