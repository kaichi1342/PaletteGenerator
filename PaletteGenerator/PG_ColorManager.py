#-----------------------------------------------------------------------------#
# Palette Generator - Copyright (c) 2022 - kaichi1342                         #
# ----------------------------------------------------------------------------#
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
# ----------------------------------------------------------------------------#
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                        #
# See the GNU General Public License for more details.                        #
#-----------------------------------------------------------------------------#
# You should have received a copy of the GNU General Public License           #
# along with this program.                                                    #
# If not, see https://www.gnu.org/licenses/                                   # 
# -----------------------------------------------------------------------------
# PaletteGenerator is a docker that  generates color scheme palette randomly  #
# or based of the selected scheme. There are 9 color scheme available to      #
# generate from.                                                              #
# -----------------------------------------------------------------------------
  

from krita import *  
import random, time
from datetime import datetime

from PyQt5.QtCore import ( pyqtSignal)

from PyQt5.QtGui import (QPainter, QColor)

from PyQt5.QtWidgets import (QWidget, QMessageBox, QLabel)
 

class ColorBox(QWidget):
    clicked = pyqtSignal() 
    
    def __init__(self):  
        self.color = QColor(200, 200, 200)
        super().__init__() 
 
    def paintEvent(self, e):
        self.qp = QPainter()
        self.qp.begin(self)
        self.drawRectangles()
        self.qp.end()

    def drawRectangles(self):  
        self.qp.setBrush(self.color)
        self.qp.drawRect(-1, -1, self.geometry().width()+1, self.geometry().height()+1)
 
    def setColorHSV(self,h,s,v):
        self.color.setHsv(h,s,v,255)
        self.update()

    def setColorRGBF(self,r,g,b,a = 1.0):
        self.color.setRgbF(r, g, b, a)
        self.update()
  
    def getColorForSet(self, doc): 
        color_to_set = ManagedColor(doc.colorModel(), doc.colorDepth(), doc.colorProfile())
        colorComponents = color_to_set.components()
        colorComponents[0] = self.color.blueF()
        colorComponents[1] = self.color.greenF()
        colorComponents[2] = self.color.redF()
        colorComponents[3] = self.color.alphaF() 

        color_to_set.setComponents(colorComponents)

        return color_to_set

    def toString(self):
        return "Red "+str(self.color.red())+" Green "+str(self.color.green())+" Blue "+str(self.color.blue())+" Alpha "+str(self.color.alpha())

    def toStringHSV(self):
        return "H "+str(self.color.hsvHue())+" S "+str(self.color.hsvSaturation())+" V "+str(self.color.value())

    def getColorHex(self):
        return self.color.name()

    def toHSV(self):
        return { "H" : self.color.hsvHue(), "S" : self.color.hsvSaturation(), "V" : self.color.value()}

    def getHueName(self):
        hue = self.color.hsvHue()
        if hue >= 0     and hue <= 5        : return "red"
        elif hue >= 6   and hue <= 35       : return "orange"
        elif hue >= 36  and hue <= 65       : return "yellow" 
        elif hue >= 66  and hue <= 170      : return "green" 
        elif hue >= 171 and hue <= 185      : return "cyan" 
        elif hue >= 186 and hue <= 255      : return "blue" 
        elif hue >= 256 and hue <= 280      : return "purple" 
        elif hue >= 281 and hue <= 325      : return "magenta" 
        elif hue >= 326 and hue <= 345      : return "pink" 
        else                                : return "red" 

    def mousePressEvent(self, e):
        self.clicked.emit()

class ColorGenerator():  

    def __init__(self, parent, settings):  
        self.hue = 0
        self.sat = 0
        self.val = 0

        self.parent     = parent
        self.settings   = settings
        self.sat_limit  = self.settings["saturation_cutoff"]
        self.val_limit  = self.settings["value_cutoff"] 
        
        super().__init__() 
 
    def reloadSettings(self, settings):
        self.settings = settings
        self.sat_limit = self.settings["saturation_cutoff"]
        self.val_limit = self.settings["value_cutoff"]
        self.sat_cutoff = self.setCutOffPoint(self.settings["saturation_priority"])
        self.sat_cutoff = self.setCutOffPoint(self.settings["value_priority"])


    def setSatCutOff(self, low, mid, high, lim):
        self.sat_limit["low"]  = low 
        self.sat_limit["mid"]  = mid
        self.sat_limit["high"] = high
        self.sat_limit["lim"]  = lim

    def setValCutOff(self,low, mid, high, lim):
        self.val_limit["low"]  = low
        self.val_limit["mid"]  = mid
        self.val_limit["high"] = high
        self.val_limit["lim"]  = lim


    def reloadSatCutOff(self):
        self.sat_limit = self.settings["saturation_cutoff"] 
    def reloadSatCutOff(self):
        self.val_limit = self.settings["value_cutoff"]

    def getFGColor(self, view, doc):
        color   = view.foregroundColor() 

        config = {
            "depth"     : doc.colorDepth(),
            "model"     : doc.colorModel(),
            "profile"   : doc.colorProfile()
        }

        color.setColorSpace(config["model"], config["depth"], config["profile"])
        colorData = color.components() 
        
        FGColor = QColor()
        FGColor.setRgbF(colorData[2], colorData[1], colorData[0], colorData[3]) 

        return FGColor


    def setHue(self, hue = -1, offset = 0):
        if(hue < 0 ): 
            random.seed()
            return random.randint(0, 360) 
        else:
            if(hue + offset > 360):
                return (hue + offset) % 360
            elif(hue + offset < 0):
                return 360 + (hue + offset)  
            else:
                return hue + offset
        
    #SATURATION
    def setSat(self, sat = -1, offset = 0, rand_offset = False):
        self.sat_cutoff = self.setCutOffPoint(self.settings["saturation_priority"])
        if(sat < 0 ): 
            return self.setRandomSat()
        else:
            return self.setRotatingSat(sat, offset, rand_offset) 

    def setRandomSat(self): 
        #random.seed()
        cutoff = random.randint(0, 100)
        if cutoff <= self.sat_cutoff[0]:
            return random.randint(self.sat_limit["low"],self.sat_limit["mid"])
        elif cutoff > self.sat_cutoff[1]:
            return random.randint(self.sat_limit["mid"],self.sat_limit["lim"])
        else: 
            return random.randint(self.sat_limit["mid"],self.sat_limit["high"])

    def setRotatingSat(self, sat = -1,  offset = 0, rand_offset = False ):
        if(rand_offset): offset = self.randomizedOffset()  

        if(sat + offset > self.sat_limit["lim"]): 
            offset = (sat + offset) % self.sat_limit["lim"]
            return self.sat_limit["low"] + abs(offset) 
        elif(sat + offset < self.sat_limit["low"]):
            offset  = (sat + offset) % self.sat_limit["low"]  
            return self.sat_limit["lim"] - abs(offset)
        else: 
            return sat + offset 


    #VALUE
    def setVal(self, val = -1, offset = 0, rand_offset = False):
        self.val_cutoff = self.setCutOffPoint(self.settings["value_priority"])
        if(val < 0 ):   
            return self.setRandomVal()
        else:  
            return self.setRotatingVal(val, offset, rand_offset)


    def setRandomVal(self): 
        #random.seed()   
        cutoff = random.randint(0, 100)
        
        if cutoff <= self.val_cutoff[0]:    
            return random.randint(self.val_limit["low"],self.val_limit["mid"])  
        elif cutoff > self.val_cutoff[1]:  
            return random.randint(self.val_limit["high"],self.val_limit["lim"])
        else:  
            return random.randint(self.val_limit["mid"],self.val_limit["high"])

    def setRotatingVal(self, val = -1,  offset = 0, rand_offset = False ): 
        if(rand_offset): offset = self.randomizedOffset()  
        
        if(val + offset > self.val_limit["lim"]):
            offset = (val + offset) % self.val_limit["lim"]   
            return self.val_limit["low"] + abs(offset) 
        elif(val + offset < self.val_limit["low"]):  
            offset  = (val + offset) % self.val_limit["low"] 
            return self.val_limit["lim"] - abs(offset) 
        else:  
            return val + offset

    def randomizedOffset(self):
        random.seed()
        if ( random.randint(1, 500) % 2 == 0 ):
            return random.randint(5,20)
        else: 
             return -1 * random.randint(5,20)

    def setCutOffPoint(self, t):
        if t == "Low":
            return [90,95]
        elif t == "High":
            return [5,10]
        elif t == "Mid":
            return [5,95]
        elif t == "Normal":
            return [14,86]
        elif t == "Low Only":
            return [100,100]
        elif t == "Mid Only":
            return [-1,100]
        elif t == "High Only":
            return [-1,-1]
        else:
            return [33,66]
  
    