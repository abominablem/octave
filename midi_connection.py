# -*- coding: utf-8 -*-
"""
Created on Thu Dec 23 23:10:11 2021

@author: marcu
"""

import sys
sys.path.append("D:\\Users\\Marcus\\Documents\\R Documents\\Coding\\Python\\Packages")
from mh_logging import log_class
log_class = log_class("min")
from pygame import midi
# from pygame import fastevents
import midiutil
import threading

status_map = {
    144: "note-on",
    128: "note-off",
    176: "control-change",
    160: "poly-pressure",
    192: "program-change",
    208: "channel-pressure",
    224: "pitch-wheel",
    240: "system-exclusive",
    }

class NoMidiDevice(midi.MidiException):
    """ Raised when no MIDI devices are connected """
    pass

class MidiEvent:
    @log_class
    def __init__(self, event = None):
        if event is None:
            self.status = None; self.note = None; self.velocity = None
            self.channel = None; self.timestamp = None
        else:
            self.status_id = event[0][0]
            self.status = status_map[self.status_id]
            self.note = event[0][1]
            self.velocity = event[0][2]
            self.channel = event[0][3]
            self.timestamp = event[1]
        # optional integer corresponding to order of event in sequence
        self.order = -1

    def closes(self, event):
        """ Return whether this event is a valid closing event for the
        provided event """
        if self.status == "note-off":
            if (event.timestamp < self.timestamp and
                event.note == self.note and
                event.channel == self.channel):
                return True
        elif self.status == "control-change":
          if (event.timestamp < self.timestamp and
              self.note == event.note):
              return True
        return False

    def opens(self, event):
        """ Return whether this event is a valid opening event for the
        provided event """
        if self.status == "note-on":
            if (event.timestamp < self.timestamp and
                event.note == self.note and
                event.channel == self.channel):
                return True
        elif self.status == "control-change":
          if (event.timestamp < self.timestamp and
              self.note == event.note):
              return True
        return False

    def __str__(self):
        return "MidiEvent " + " ".join(
            ["%s: %s" % (key, value) for key, value in self.__dict__.items()]
            )

class MidiRecording:
    @log_class
    def __init__(self):
        self.pygame_events = []
        self.midi_events = []
        self._ecount = 0
        self.midi_file = midiutil.MIDIFile(
            numTracks = 1,
            eventtime_is_ticks = True,
            file_format = 1,
            ticks_per_quarternote = 600 #100 bpm
            )

    @log_class
    def log(self, events):
        self._ecount += 1
        self.pygame_events += events
        for event in events:
            midi_event = MidiEvent(event)
            midi_event.order = self._ecount
            self.midi_events.append(midi_event)

    def get_event_duration(self, event):
        if not isinstance(event, MidiEvent):
            event = MidiEvent(event)
            event.order = self.pygame_events.index(event)

        if not event.status == "note-on":
            return 0

        for event_after in self.midi_events:
            if event_after.closes(event):
                # duration in milliseconds
                duration = event_after.timestamp - event.timestamp
                return duration
        # assume event continues until last recorded event if no explicit end
        # is found
        return self.get_max_timestamp() - event["timestamp"]

    def get_event_time(self, event):
        if not isinstance(event, MidiEvent):
            event = MidiEvent(event)
        return event.timestamp - self.get_min_timestamp() + 1

    def get_sorted_events(self):
        unsorted_list = self.pygame_events[:]
        return unsorted_list.sort(key = lambda x: x[1])

    def event_status(self, event):
        return status_map[event[0][0]]

    def get_max_timestamp(self):
        return max(self.midi_events, key = lambda x: x.timestamp).timestamp

    def get_min_timestamp(self):
        try:
            return self.min_timestamp
        except AttributeError:
            self.min_timestamp = min(self.midi_events,
                                     key = lambda x: x.timestamp).timestamp
            return self.min_timestamp

    @log_class
    def add_event_to_midi_file(self, event):
        if not isinstance(event, MidiEvent):
            raise ValueError("Input must be instance of MidiEvent")

        event.duration = self.get_event_duration(event)
        event.time = self.get_event_time(event)
        if event.status == "note-on":
            self.midi_file.addNote(
                track = 0,
                channel = event.channel,
                pitch = event.note,
                time = event.time,
                duration = event.duration,
                volume = event.velocity
                )
        elif event.status == "control-change":
            """ add pedal events e.g. sostenuto """
            self.midi_file.addControllerEvent(
                track = 0,
                channel = event.channel,
                time = event.time,
                controller_number = event.note,
                parameter = event.velocity
                )

    @log_class
    def write(self, filename):
        self.filename = filename
        for event in self.midi_events:
            self.add_event_to_midi_file(event)
        self.write_file(filename)

    @log_class
    def write_file(self, filename):
        with open(filename, 'wb') as file_con:
            self.midi_file.writeFile(file_con)

class MidiConnection:
    @log_class
    def __init__(self):
        self.recording = False
        self.input_device_id = None
        self.output_device_id = None
        self.midi = MidiRecording()

    @log_class
    def start_recording(self):
        self.recording = True
        midi.init()
        self.set_input()
        self.midi = MidiRecording()
        self.recording_thread = threading.Thread(target = self._start_recording)
        self.recording_thread.start()

    @log_class
    def _start_recording(self):
        while self.recording:
            midi_events = self.input.read(10)
            if midi_events != []:
                self.midi.log(midi_events)

    @log_class
    def stop_recording(self):
        self.recording = False
         # don't quit until all inputs have been read from the buffer
        self.recording_thread.join()

        midi.quit()

        self.midi.write("D:\\Users\\Marcus\\Documents\\R Documents\\Coding\\Python\\Octave\\test.midi")
        self.midi.midi_file = None

    @log_class
    def start_playback(self):
        print("start p")

    @log_class
    def stop_playback(self):
        print("stop p")

    @log_class
    def get_devices(self):
        device_dict = {}
        for device_id in range(midi.get_count()):
            device_info = midi.get_device_info(device_id)
            device_dict[device_id] = {
                "interf": device_info[0],
                "name": device_info[1],
                "input": device_info[2] == 1,
                "output": device_info[3] == 1,
                "opened": device_info[4] == 1,
                }

    @log_class
    def get_default_input_device(self):
        device_id = midi.get_default_input_id()
        if device_id == -1:
            raise NoMidiDevice
        else:
            return device_id

    @log_class
    def get_default_output_device(self):
        device_id = midi.get_default_output_id()
        if device_id == -1:
            raise NoMidiDevice
        else:
            return device_id

    @log_class
    def set_input(self, device_id = None):
        if device_id is None and self.input_device_id is None:
            self.input_device_id = midi.get_default_input_id()

        self.input = midi.Input(self.input_device_id)

    @log_class
    def set_output(self, device_id = None):
        if device_id is None and self.output_device_id is None:
            self.output_device_id = midi.get_default_output_id()

        self.output = midi.Output(self.output_device_id)

    def close():
        midi.quit()


if __name__ == "__main__":
    import tkinter as tk

    class TestApp:
        @log_class
        def __init__(self):
            self.root = tk.Tk()
            self.midi_con = MidiConnection()
            btn_start_rec = tk.Button(self.root, text = "start rec", command = self.midi_con.start_recording, font = ("Constantia", 32, "bold"))
            btn_stop_rec = tk.Button(self.root, text = "stop rec",  command = self.midi_con.stop_recording, font = ("Constantia", 32, "bold"))
            btn_start_rec.pack()
            btn_stop_rec.pack()
            self.root.mainloop()

    TestApp()
    midi.quit()