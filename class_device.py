from array import array as arr
import math             as math
import numpy            as np
import os               as o
import ROOT             as R
import sys              as sys

import macro

class device:

    id = None
    def setid(self,id):
        self.id = id

    title = None
    def gettitle(self):
        if self.id == None:
            return
        macro.boilerplate.run(self.id)
        self.title = macro.boilerplate.out

    stats = None
    def getstats(self):
        if self.id == None:
            return
        macro.rip_array.run(self.id)
        self.stats = macro.rip_array.out

    def __init__(self, id):
        self.setid(id)
        self.gettitle()
        self.getstats()
