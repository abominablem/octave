# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 22:35:23 2021

@author: marcu
"""
import sys
sys.path.append("D:\\Users\\Marcus\\Documents\\R Documents\\Coding\\Python\\Packages")
import tkinter as tk
import re
from PIL import Image, ImageTk

from mh_logging import log_class
import tk_arrange as tka
from sqlite_tablecon import TableCon, MultiConnection

import global_const as g
import futil
log_class = log_class(g.LOG_LEVEL)

class OctaveFrameBase:
    """ Base tk.Frame with menu, Octave logo, and title bar """
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
    def get_widget(self):
        return self.widget_set

    @log_class
    def grid(self, **kwargs):
        self.widget_set.grid(**kwargs)

    def rowconfigure(self, *args, **kwargs):
        self.widget_set.rowconfigure(*args, **kwargs)

    def columnconfigure(self, *args, **kwargs):
        self.widget_set.columnconfigure(*args, **kwargs)

class OctaveMenuBar(tk.Menu):
    @log_class
    def __init__(self, master, include_midi = False):
        self._menu_bar_kwargs = {
            "fg": g.COLOUR_MENU_BAR_FOREGROUND,
            "activebackground": g.COLOUR_MENU_BAR_ACTIVE_BACKGROUND,
            "activeforeground": g.COLOUR_MENU_BAR_ACTIVE_FOREGROUND,
            "tearoff": False,
            }
        super().__init__(master, bg = g.COLOUR_MENU_BAR_MAIN_BACKGROUND,
                       **self._menu_bar_kwargs)
        self.menus_dict = {}
        self.add_menu("File", ["New", "Open", "Save", "Save As",
                               "__seperator__", "Exit", "File"])

        tools_commands = []
        if include_midi:
            tools_commands += ["MIDI Input device", "MIDI Output device",
                               "Refresh MIDI devices"]
        self.add_menu("Tools", tools_commands)

    @log_class
    def add_menu(self, label, commands):
        """ Iteratively add a list of labels and commands to a menu"""
        if commands == []: return
        menu = tk.Menu(
            self, bg = g.COLOUR_MENU_BAR_BACKGROUND, **self._menu_bar_kwargs)
        self.menus_dict[label] = menu
        for command in commands:
            if command == "__seperator__":
                menu.add_separator()
            else:
                self._add_menu_item(menu, label, command)
        self.add_cascade(label = label, menu = menu)

    @log_class
    def _add_menu_item(self, menu, label, command):
        event_string = self._get_custom_event_string(label, command)
        callback = lambda: self.event_generate(event_string)
        menu.add_command(label = command, command = callback)
        self.bind(event_string, lambda: print(event_string))

    @log_class
    def _get_custom_event_string(self, label, command):
        command = command.title().replace(" ", "")
        command = re.sub("[^\w]", "", command)
        return "<<%s-%s>>" % (label, command)

    # @log_class
    # def event_generate(self, sequence, **kw):
    #     """Generate an event SEQUENCE. Additional
    #     keyword arguments specify parameter of the event
    #     (e.g. x, y, rootx, rooty)."""
    #     print(sequence)
    #     args = ('event', 'generate', self._w, sequence)
    #     for k, v in kw.items():
    #         args = args + ('-%s' % k, str(v))
    #     self.tk.call(args)


class OctaveWindowBase:
    """ Toplevel window with OctaveFrameBase """
    @log_class
    def __init__(self, master, title = "Octave"):
        self.master = master
        self.window = tk.Toplevel(self.master, bg = g.COLOUR_BACKGROUND)
        self.master.eval(f'tk::PlaceWindow {self.window} center')
        self.menu_bar = OctaveMenuBar(self.window, include_midi = True)
        self.window.config(menu = self.menu_bar)
        self.title_bar = OctaveFrameBase(self.window, title = title)

    @log_class
    def start(self):
        # self.window.transient(self.master)
        self.window.grab_set()
        self.window.mainloop()

octave_db = MultiConnection(r".\data\octave_sqlite.db",
                            ["books", "records", "tags"])


if __name__ == "__main__":
    class TestApp:
        @log_class
        def __init__(self):
            self.root = tk.Tk()
            btn_start_rec = tk.Button(
                self.root, text = "start recording",
                command = self.start_window,
                font = ("Constantia", 32, "bold"))
            btn_start_rec.grid(row = 1, column = 0)
            self.menu_bar = OctaveMenuBar(self.root)
            self.root.config(menu = self.menu_bar)

            def test_func(self, *args, **kwargs):
                print("test func activated")

            self.menu_bar.bind("<<File-Exit>>", test_func)

            self.root.mainloop()

        @log_class
        def start_window(self):
            title_bar = OctaveWindowBase(self.root, title = "TEST WINDOW")
            btn_stop_rec = tk.Button(
                title_bar.window, text = "stop recording",
                font = ("Constantia", 32, "bold"))
            btn_stop_rec.grid(row = 1, column = 0)
            title_bar.start()

    app = TestApp()