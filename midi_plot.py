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

from midi_connection import MidiConnection
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
        self.base_plot_rate = 0.2
        self._plotted_events = 0
        self._drawn_events = 0
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
        self.rowconfigure(0, weight = 1)
        self.columnconfigure(0, weight = 1)

    @log_class
    def start_plotting(self):
        self.plotting = True

    @log_class
    def stop_plotting(self):
        self.plotting = False

    @log_class
    def scale_axes(self, event):
        """ Update the axis limits based on the x/y coordinates of the
        specified event """
        ylim = {}
        if self.ymin is None or event.y - 1 < self.ymin:
            ylim["ymin"] = event.y - 1

        if self.ymax is None or event.y + 1 > self.ymax:
            ylim["ymax"] = event.y + 1

        self.__dict__.update(ylim)
        if ylim != {}:
            self.figure.set_ylim(**ylim)

        if self.xmax is None or event.x + event.duration > self.xmax:
            self.xmax = event.x + event.duration
            self.figure.set_xlim(xmax = self.xmax)

    @log_class
    def log_midi_event(self, event):
        """ Add MIDI events to the event queue as they are created """
        self.midi_events.append(event)
        if event.status in ["note-on", "note-off"]:
            self.live_events.append(event)
        elif (event.status == "control-change" and event.note == 64
              and self.plot_pedal):
            self.live_events.append(event)
        self.update_live_events(event)

    @log_class
    def plot(self, event, draw = True):
        """ Draw a representation of the MIDI event on the canvas """
        if event.drawn: return

        if event.status == "note-on":
            self.figure.add_patch(plt.patches.FancyBboxPatch(
                (event.x, event.y), event.duration, 1,
                boxstyle = "round, pad = 0.005, rounding_size = 0.05",
                facecolor = event.note_colour, fill = True,
                figure = self.visual_figure)
                )
            event.drawn = True
            self._plotted_events += 1
        elif event.status == "control-change" and event.note == 64:
            pass
            #TODO add option for pedal graph under main graph
        else:
            return

        if draw:
            self.draw()

    @log_class
    def draw(self):
        """ Redraw the matplotlib canvas """
        self._drawn_events = len(self.figure.patches)
        self.canvas.draw()
        # print("Drew %s MIDI events" % self._plotted_events - self._drawn_events)
        self._last_drawn = datetime.now()
        self._draw_now = False

    @log_class
    def clear(self):
        """ Clear the matploblib canvas of all objects """
        canvas = self.get_widget()
        for item in canvas.find_all():
            canvas.delete(item)

    @log_class
    def get_widget(self):
        """ Return the tk widget for the canvas """
        return self.canvas.get_tk_widget()

    @log_class
    def _draw_check(self):
        """ Check whether to draw or not based on the time since last drawn and
        number of events in the plot queue """
        plotted_but_undrawn = self._plotted_events - self._drawn_events

        # Don't plot if nothing new is drawn
        if plotted_but_undrawn == 0:
            return False
        # For very slow event input rates, plot live
        elif plotted_but_undrawn <= 7:
            return True
        # Draw at least every 25 midi events (very fast midi input)
        elif plotted_but_undrawn >= 25:
            return True

        since_last_draw = (datetime.now() - self._last_drawn).total_seconds()

        # Plot at least every second
        if since_last_draw > 1:
            return True
        # For slow event input rates, plot at the base rate
        elif since_last_draw > self.base_plot_rate and plotted_but_undrawn <= 10:
            return True
        # For medium event input rates, plot every ~1/2 a second
        elif plotted_but_undrawn <= 15 and since_last_draw > 0.5:
            return True
        else:
            return False

    @log_class
    def get_min_timestamp(self):
        """ Return the earliest timestamp of all MIDI events. Since MIDI events
        arrive in chronological order, this can be cached """
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
        """ Return the last timestamp of all MIDI events. """
        if self.midi_events == []:
            return 0
        self.max_timestamp = max(self.midi_events,
                                 key = lambda x: x.timestamp).timestamp
        return self.max_timestamp

    @log_class
    def get_oldest_live_event(self):
        """ Return the oldest event that is still live """
        return min(self.live_events, key = lambda x: x.logged_time)

    @log_class
    def update_live_events(self, event = None, cartesian_update = False):
        """ Update the list of list events based on either:
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
        """ Update the event queue based on the opening/closing event pair
        Calculate the opening event coordinates, duration, and other
        plotting arguments. """
        try: self.live_events.remove(opening_event)
        except ValueError: pass
        try: self.live_events.remove(closing_event)
        except ValueError: pass

        event = opening_event
        """ Set helper values for plotting """
        event.x = (event.timestamp - self.get_min_timestamp())/1000
        event.y = self._get_y_value(event.note)
        event.duration = (closing_event.timestamp - event.timestamp)/1000
        event.note_colour = self._get_note_colour(event.note)
        event.drawn = False

        self.scale_axes(event)
        self.plot(event, draw = self._draw_check())

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
        """ Get the y coordinates of a midi note """
        note = note - 21
        octaves = note // 12
        note_index = note % 12
        y_values = [1, 1.5, 2, 3, 3.5, 4, 4.5, 5, 6, 6.5, 7, 7.5]
        return octaves * 7 + y_values[note_index]

    @log_class
    def _get_note_colour(self, note):
        """ Get the colour of a note depending on if it is a white or black
        note """
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