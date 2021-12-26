# -*- coding: utf-8 -*-
"""
Created on Sun Dec 26 02:51:24 2021

@author: marcu
"""

import itertools
import tkinter as tk
from datetime import datetime

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib as plt

from midi_connection import MidiConnection, MIDI_STATUS_MAP
from mh_logging import log_class
log_class = log_class("min")

class MidiPlot(tk.Frame):
    @log_class
    def __init__(self, master, midi_connection, plot_pedal = False, **kwargs):
        super().__init__(master, **kwargs)

        self.midi_connection = midi_connection
        self.midi_connection.bind("<<MidiEvent>>", self.log_midi_event)
        self.midi_connection.bind("<<RecordingStart>>", self.start_plotting)
        self.midi_connection.bind("<<RecordingStop>>", self.stop_plotting)

        self.plot_pedal = plot_pedal
        self.midi_events = []
        self.live_events = []
        self.plotting = False
        self._plot_buffer = []
        self._plot_buffer_index = 0
        self._last_drawn = datetime.min

        self.visual_figure = plt.figure.Figure(figsize=(10, 5), dpi=100)
        self.visual_figure.subplots_adjust(
            left = 0.03, right = 0.97, top = 0.95, bottom = 0.05)
        self.figure = self.visual_figure.add_subplot(111)
        self.ymin, self.ymax, self.xmin, self.xmax = None, None, 0, None
        self.figure.axes.get_yaxis().set_visible(False)
        self.figure.axis("off")
        self.figure.margins(x = 0, y = 0)

        self.canvas = FigureCanvasTkAgg(figure = self.visual_figure,
                                        master = self)
        self.canvas.get_tk_widget().grid(row = 0, column = 0, sticky = "nesw")
        self.rowconfigure(0, weight = 1); self.columnconfigure(0, weight = 1)
        self.draw()

    @log_class
    def start_plotting(self):
        self.plotting = True

    @log_class
    def stop_plotting(self):
        self.plotting = False

    @log_class
    def scale_axes(self, event):
        self.ymin = (event.y - 1 if self.ymin is None
                     else min(self.ymin, event.y - 1))
        self.ymax = (event.y + 1 if self.ymax is None
                     else max(self.ymax, event.y + 1))
        self.xmin = 0
        self.xmax = (event.x + event.duration if self.xmax is None
                     else max(self.xmax, event.x + event.duration))
        self.figure.set(ylim = (self.ymin, self.ymax),
                        xlim = (self.xmin, self.xmax))

    @log_class
    def log_midi_event(self, event):
        self.midi_events.append(event)
        if event.status in ["note-on", "note-off"]:
            self.live_events.append(event)
        elif (event.status == "control-change" and event.note == 64
              and self.plot_pedal):
            self.live_events.append(event)
        self.update_live_events(event)

    @log_class
    def plot(self, event, draw = True):
        if not self.plotting: return

        if event.status == "note-on":
            self.figure.add_patch(plt.patches.FancyBboxPatch(
                (event.x, event.y), event.duration, 1,
                boxstyle = "round, pad = 0.005, rounding_size = 0.05",
                facecolor = event.note_colour, fill = True,
                figure = self.visual_figure)
                )
        elif event.status == "control-change" and event.note == 64:
            pass
            #TODO add option for pedal graph under main graph
        else:
            return

        if draw:
            self.scale_axes(event)
            self.draw()

    @log_class
    def draw(self, scale_axes = False):
        self.canvas.draw()
        self._last_drawn = datetime.now()

        if scale_axes:
            drawn_events = [event for event in self.midi_events
                            if event.status == "note-on"]
            self.ymin = min(drawn_events, key = lambda event: event.y)
            self.ymax = max(drawn_events, key = lambda event: event.y)
            self.xmin = 0
            self.xmax = max(drawn_events, key = lambda event: event.x)
            self.figure.set(ylim = (self.ymin, self.ymax),
                            xlim = (self.xmin, self.xmax))

    @log_class
    def _draw_check(self):
        if (datetime.now() - self._last_drawn).total_seconds() > 1:
            self.draw()

    @log_class
    def get_min_timestamp(self):
        if self.midi_events == []:
            return 0
        try:
            return self.min_timestamp
        except AttributeError:
            self.min_timestamp = min(self.midi_events,
                                     key = lambda x: x.timestamp).timestamp
            return self.min_timestamp

    @log_class
    def get_max_timestamp(self):
        if self.midi_events == []:
            return 0
        self.max_timestamp = max(self.midi_events,
                                 key = lambda x: x.timestamp).timestamp
        return self.max_timestamp

    @log_class
    def _get_event_buffer_size(self):
        return len(self.live_events)

    @log_class
    def update_live_events(self, event = None, cartesian_update = False):
        """
        Update the list of list events based on either:
        1. The provided event (if cartesian_update = False)
        2. All currently live events (if cartesian_update = True)
        """
        if not cartesian_update and event is None:
            raise ValueError("MiidEvent must be provided if cartesian_update "
                             "is False")

        if cartesian_update:
            for event_before, event_after in itertools.product(self.live_events):
                if event_after.closes(event_before):
                    self._update_live_events(event_before, event_after)
        else:
            for event_before in self.live_events:
                if event.closes(event_before):
                    self._update_live_events(event_before, event)

    @log_class
    def _update_live_events(self, opening_event, closing_event):
        try: self.live_events.remove(opening_event)
        except ValueError: pass
        try: self.live_events.remove(closing_event)
        except ValueError: pass

        """ Set helper values for plotting """
        opening_event.x = (opening_event.timestamp - self.get_min_timestamp())/1000
        opening_event.y = self._get_y_value(opening_event.note)
        opening_event.duration = (closing_event.timestamp
                                  - opening_event.timestamp)/1000
        opening_event.note_colour = self._get_note_colour(opening_event.note)

        self.plot(opening_event)
        return

        """ If a large amount of notes are played in quick succession, the
        calls to self.plot get very expensive if the whole canvas is redrawn
        each time. """
        if self._plot_buffer_index == 0:
            self._plot_buffer_index = self._get_event_buffer_size()
        self._add_to_plot_buffer(event = opening_event)
        self._handle_plot_buffer()
        self._draw_check()

    @log_class
    def _add_to_plot_buffer(self, event):
        self._plot_buffer.append(event)

    @log_class
    def _handle_plot_buffer(self):
        if len(self._plot_buffer) < self._plot_buffer_index + 1:
            return
        else:
            print("buffering %s plot events" % self._plot_buffer_index)
            for event in self._plot_buffer[:self._plot_buffer_index - 1]:
                self.plot(event, draw = False)
            event = self._plot_buffer[self._plot_buffer_index - 1]
            self.plot(event, draw = True)
            self._plot_buffer_index = 0
        self._plot_buffer = self._plot_buffer[self._plot_buffer_index:]

    @log_class
    def _note_num_to_name(self, note):
        """ Currently unused - turns note into its string name """
        index = note - 21
        notes = ['A0', 'Bb0', 'B0', 'C1', 'Db1', 'D1', 'Eb1', 'E1', 'F1',
                 'Gb1', 'G1', 'Ab1', 'A1', 'Bb1', 'B1', 'C2', 'Db2', 'D2',
                 'Eb2', 'E2', 'F2', 'Gb2', 'G2', 'Ab2', 'A2', 'Bb2', 'B2',
                 'C3', 'Db3', 'D3', 'Eb3', 'E3', 'F3', 'Gb3', 'G3', 'Ab3',
                 'A3', 'Bb3', 'B3', 'C4', 'Db4', 'D4', 'Eb4', 'E4', 'F4',
                 'Gb4', 'G4', 'Ab4', 'A4', 'Bb4', 'B4', 'C5', 'Db5', 'D5',
                 'Eb5', 'E5', 'F5', 'Gb5', 'G5', 'Ab5', 'A5', 'Bb5', 'B5',
                 'C6', 'Db6', 'D6', 'Eb6', 'E6', 'F6', 'Gb6', 'G6', 'Ab6',
                 'A6', 'Bb6', 'B6', 'C7', 'Db7', 'D7', 'Eb7', 'E7', 'F7',
                 'Gb7', 'G7', 'Ab7', 'A7', 'Bb7', 'B7', 'C8']
        return notes[index]

    @log_class
    def _get_y_value(self, note):
        note = note - 21
        octaves = note // 12
        note_index = note % 12
        y_values = [1, 1.5, 2, 3, 3.5, 4, 4.5, 5, 6, 6.5, 7, 7.5]
        return octaves * 7 + y_values[note_index]

    @log_class
    def _get_note_colour(self, note):
        wht = "blue"; blk = "black"
        index = note % 12
        colours = [wht, blk, wht, blk, wht, wht, blk, wht, blk, wht, blk, wht]
        return colours[index]

if __name__ == "__main__":
    class TestApp:
        @log_class
        def __init__(self):
            self.root = tk.Tk()
            self.midi_con = MidiConnection()
            self.midi_plot = MidiPlot(self.root, self.midi_con)
            btn_start_rec = tk.Button(
                self.root, text = "start recording",
                command = self.midi_con.start_recording,
                font = ("Constantia", 32, "bold"))
            btn_stop_rec = tk.Button(
                self.root, text = "stop recording",
                command = self.midi_con.stop_recording,
                font = ("Constantia", 32, "bold"))
            btn_start_rec.grid(row = 0, column = 0, sticky = "nesw")
            btn_stop_rec.grid(row = 0, column = 1, sticky = "nesw")
            self.midi_plot.grid(row = 1, column = 0, columnspan = 2, sticky = "nesw")

            self.root.rowconfigure(1, weight = 1)
            self.root.columnconfigure(0, weight = 1)
            self.root.columnconfigure(1, weight = 1)
            self.midi_plot.rowconfigure(0, weight = 1)
            self.midi_plot.columnconfigure(0, weight = 1)

            self.root.mainloop()

    app = TestApp()
    app.midi_con.close()