# -*- coding: utf-8 -*-
"""
Created on Mon Dec 20 17:01:10 2021

@author: marcu
"""
import sys
sys.path.append("D:\\Users\\Marcus\\Documents\\R Documents\\Coding\\Python\\Packages")
import tkinter as tk

from mh_logging import log_class
import tk_arrange as tka

import global_const as g
from base import OctaveFrameBase, OctaveMenuBar
log_class = log_class(g.LOG_LEVEL)

from play import OctavePlay
from record import OctaveRecord

class Octave:
    @log_class
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Octave - MIDI Recording and Playback")
        self.root.protocol("WM_DELETE_WINDOW", self.destroy)

        self.menu_bar = OctaveMenuBar(self.root)
        self.root.config(menu = self.menu_bar)

        self.widget_frame = tk.Frame(self.root, bg = g.COLOUR_BACKGROUND)
        self.title_bar = OctaveFrameBase(self.widget_frame, title = "Octave")

        buttons = {
            1: {"label": "Play",
                "bindings": {
                    "event": "<1>",
                    "function": lambda event: self.open_window(event, "play")
                    },
                "widget_kwargs": g.BTN_MAIN_ARGS,
                "grid_kwargs": g.GRID_STICKY_PADDING_LARGE,
                "stretch_width": True, "stretch_height": False},
            2: {"label": "Record",
                "bindings": {
                    "event": "<1>",
                    "function": lambda event: self.open_window(event, "record")
                    },
                "widget_kwargs": g.BTN_MAIN_ARGS,
                "grid_kwargs": g.GRID_STICKY_PADDING_LARGE,
                "stretch_width": True, "stretch_height": False},
            }

        frame_kwargs = {"bg": g.COLOUR_BACKGROUND}
        self.button_set = tka.ButtonSet(
            master = self.widget_frame, buttons = buttons, layout = [[1], [2]],
            frm_kwargs = frame_kwargs, set_width = 30
            )

        widgets = {1: {'widget': self.title_bar,
                       'grid_kwargs': g.GRID_STICKY,
                       'stretch_width': True},
                   2: {'widget': self.button_set,
                       'grid_kwargs': g.GRID_STICKY,
                       'stretch_width': True},
                   }
        self.widget_set = tka.WidgetSet(
            self.widget_frame, widgets, layout = [[1], [2]])

        self.widget_set.grid(row = 0, column = 0, **g.GRID_STICKY)
        self.root.rowconfigure(0, weight = 1)
        self.root.columnconfigure(0, weight = 1)

        self.style()

    @log_class
    def open_window(self, event, window):
        if window == "play":
            self.octave_play = OctavePlay(self.root, "Octave - Play")
            self.octave_play.start()
        elif window == "record":
            self.octave_play = OctaveRecord(self.root, "Octave - Record")
            self.octave_play.start()

    @log_class
    def start(self):
        self.root.eval('tk::PlaceWindow . center')
        self.root.mainloop()

    @log_class
    def destroy(self, event = None):
        self.running = False
        self.root.quit()
        self.root.destroy()

    @log_class
    def style(self):
        return


octave = Octave()
octave.start()