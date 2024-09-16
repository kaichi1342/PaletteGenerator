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
import random, math 

from PyQt5.QtGui import (QColor)

from .PG_ColorManager import * 

class AnimeShadePicker():
    
    def __init__(self, parent):  
        self.parent  = parent
        
        self.color_manager = ColorGenerator(parent) 
        self.colorManagerSetting()

        self.palette = [] 
        self.hue_var = 5 
        
        self.sat_low    = self.color_manager.sat_limit["low"]
        self.val_low    = self.color_manager.val_limit["low"]
        self.val_chk_pt = self.color_manager.val_limit["low"] + int((self.color_manager.val_limit["lim"] - self.color_manager.val_limit["low"]) / 2)
        self.sat_chk_pt = self.color_manager.sat_limit["low"] + int((self.color_manager.sat_limit["lim"] - self.color_manager.sat_limit["low"]) / 2)

        super().__init__() 

    #MISC
    def colorManagerSetting(self):
        self.color_manager.setSatCutOff(15, 85, 170, 225)
        self.color_manager.setValCutOff(30, 85, 170, 225)
    
    def distanceFrom(self, end, start, div = 1, max = 20, min = 2, is_val = False):
        distance = abs(end - start)
        
        if(div <= 1): return distance 

        distance = math.floor(distance / div)
        distance = distance if is_val == True and start > 50 else min
        
        if( abs(distance) >= max): return max

        if( abs(distance) <= min): return min

        return distance

    def accessHueOffset(self, hue, is_cold, min = 20, max = 35):
       
        color_max = 210  #The Hue where the side for cold and warm will switch

        if(hue <= 5 or hue > color_max):
            return -1 * self.distanceFrom(color_max, hue, 2, max, min) if is_cold else self.distanceFrom(color_max, hue, 2, max, min) 
        else:
            return self.distanceFrom(color_max, hue, 2, max, min) if is_cold else -1 * self.distanceFrom(color_max, hue, 2, max, min)  
    
    def accessHueOffsetvalue(self, hue, min = 20, max = 35, is_cold = False):
       
        color_max = 210  #The Hue where the side for cold and warm will switch

        random.seed() 
        offset = random.randint(min, max)

        if(hue <= 5 or hue > color_max):
            return -1 * offset if is_cold else offset
        else:
            return offset if is_cold else -1 * offset


    def accessOffset(self, min, max, lim = 5):
        random.seed() 
        rnd = random.randint(min, max)
        return lim if rnd == 0 else rnd
 
    def accessInMidPoint(self, value, mid_point ,min_offset, max_offset, center_offset, offset_check = 0):
        if value >= mid_point + offset_check:
            return random.randint( mid_point - max_offset, mid_point + min_offset) 
            
        if value <= mid_point - offset_check:
            return random.randint( mid_point - min_offset, mid_point + max_offset) 
        
        if value >= mid_point :
            return random.randint( int(mid_point / 2) , mid_point - center_offset )
        else:
            return random.randint( mid_point + center_offset, mid_point + int(mid_point / 2) )

    #TONES
    def generateMidTone(self, color, hue_shift_up = True, base_on_value = False):
        cm    = self.color_manager
        colorbox = ColorBox()  
        
        shift =  random.randint(0, self.hue_var) if hue_shift_up else random.randint( -1 * self.hue_var, 0) 
        hue = cm.setHue(color.hsvHue(), shift ) 

        val_lim = self.color_manager.val_limit["lim"]
        sat_lim = self.color_manager.sat_limit["lim"]

        random.seed() 
        if base_on_value == False : 
            sat = random.randint( int(sat_lim * .45), int(sat_lim * .55) )
            val = random.randint( int(val_lim * .45), int(val_lim * .60) )
            colorbox.setColorHSV(hue, sat, val)
            
            return colorbox.color
            
        sat = color.hsvSaturation()
        val = color.value()
        
        random.seed()   
        if val >= 200 and sat <= 75 : #IT'S TOO LIGHT 
            sat_md =  random.randint( int( (255 - sat) * .12 ), int( (255 - sat) * .20 ) )     
            sat = cm.setCappedSat(sat, sat_md ) 
             
            val_md = random.randint(int( val * .15 ) , int( val * .25 ))
            val = cm.setCappedVal(val, -1 * val_md )  

            colorbox.setColorHSV(hue, sat, val)
            return colorbox.color

        if val >= 200 and sat >= 200 : #TOO BRIGHT
            sat_md =  random.randint(int( sat * .20 ) , int( sat * .25 ))   
            sat = cm.setCappedSat(sat, -1 * sat_md ) 
             
            val_md = random.randint(int( val * .15 ) , int( val * .25 ))
            val = cm.setCappedVal(val, -1 * val_md )  
 
            colorbox.setColorHSV(hue, sat, val)
            return colorbox.color

        if val <= 75: #IT'S TOO DARK  
            sat =  random.randint( int(sat_lim * .10), int(sat_lim * .30) )
            val = cm.setCappedVal(val, random.randint(25, 115) )  
            
            colorbox.setColorHSV(hue, sat, val)
            return colorbox.color

        #MID COLOR  
        val = self.accessInMidPoint(val, self.val_chk_pt, 5, 15, 2, 10) 
        sat = self.accessInMidPoint(sat, self.sat_chk_pt, 5, 15, 2, 10) 
 
        colorbox.setColorHSV(hue, sat, val) 
        return colorbox.color
        
 
    def generateLightTone(self, color, base_sat, base_val, hue_shift = -1 ):    
        cm    = self.color_manager
        colorbox = ColorBox()  

        #TO GO LIGHTER IT NEEDS TO BE WARMER + LOWER SAT + HIGHER VAL

        dis_sat  = int (abs(base_sat - 0) / 5) 
        dis_sat  = dis_sat if dis_sat > 1 else 2
        dis_val  = int (abs(base_val - 250) / 5)          
        dis_val  = dis_val if dis_val > 1 else 2
          
        random.seed() 
        if hue_shift < 0:
            hue = cm.setHue(color.hsvHue(), self.accessHueOffsetvalue(color.hsvHue(), 1, 4, False))
            sat = cm.setCappedSat(color.hsvSaturation(),  -1 * dis_sat )   
            val = cm.setCappedVal(color.value(), dis_val )   
            
            colorbox.setColorHSV(hue, sat, val)
            return colorbox.color

        
        hue = cm.setHue(color.hsvHue(), self.accessHueOffsetvalue(color.hsvHue(), 5, hue_shift, False)) 
        sat = cm.setCappedSat(color.hsvSaturation(), -1 * dis_sat )   
        val = cm.setCappedVal(color.value(),  dis_val ) 
        
        
        colorbox.setColorHSV(hue, sat, val)
        return colorbox.color
        
        
    def generateDarkTone(self, color, og_sat, og_val, hue_shift = -1 ):    
        cm    = self.color_manager
        colorbox = ColorBox()  

        #TO GO DARKER IT NEEDS TO BE COLDER + HIGHER SAT + LOWER VAL

        dis_sat  = int (abs(og_sat - 0) / 5) 
        dis_sat  = dis_sat if dis_sat > 1 else 2
        dis_val  = int (abs(og_val - 250) / 5)          
        dis_val  = dis_val if dis_val > 1 else 2
          
        random.seed()
        if hue_shift < 0:
            hue = cm.setHue(color.hsvHue(), self.accessHueOffsetvalue(color.hsvHue(), 1, 4, True))
            sat = cm.setCappedSat(color.hsvSaturation(), dis_sat )   
            val = cm.setCappedVal(color.value(),  -1 * dis_val )   
            
            colorbox.setColorHSV(hue, sat, val)
            return colorbox.color

        
        hue = cm.setHue(color.hsvHue(), self.accessHueOffsetvalue(color.hsvHue(), 5, hue_shift, True)) 
        sat = cm.setCappedSat(color.hsvSaturation(), dis_sat )   
        val = cm.setCappedVal(color.value(), -1 * dis_val ) 
        
        colorbox.setColorHSV(hue, sat, val)
        return colorbox.color
        