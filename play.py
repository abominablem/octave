# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 22:27:18 2021

@author: marcu
"""

from mh_logging import log_class
import tk_arrange as tka

import global_const as g
import futil
log_class = log_class(g.LOG_LEVEL)
from base import OctaveFrameBase, OctaveWindowBase

class OctavePlay(OctaveWindowBase):
    @log_class
    def __init__(self, master, title = "Octave"):
        super().__init__(master, title)