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
import  os,random, json
from datetime import datetime
from functools import partial

 
from PyQt5.QtCore import ( Qt, QSize,  QTimer, QPoint )
 

from PyQt5.QtWidgets import ( 
        QVBoxLayout,  QGridLayout,  QHBoxLayout, 
        QPushButton, QWidget, QLabel, QComboBox,
        QToolButton, QDesktopWidget, QPlainTextEdit  
)


from .PG_ColorManager import * 
from .PG_SettingsDialog import *
from .PG_HSVOutput import *
from .PG_SavePalette import *

#from .GLColorBox  import GLColorBox

DOCKER_NAME = 'PaletteGenerator'
DOCKER_ID = 'pykrita_PaletteGenerator'


class PaletteGenerator(DockWidget): 
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Palette Generator")  
        
        self.scheme = [
            "Monochromatic", "Accented Achromatic", "Analogous", 
            "Complementary", "Split Complementary", "Double Split Complementary",
            "Triadic", "Tetradic Square", "Tetradic Rectangle"
        ]
        self.settings = {
            "color_scheme"       : 1,
            "color_variance"     : 5.0,
            "saturation_priority": "Normal",
            "value_priority"     : "Normal",
            "saturation_cutoff"   : {
                "low" : 0,
                "mid" : 150,
                "high": 220,
                "lim" : 255
            },
            "value_cutoff": {
                "low" : 0,
                "mid" : 180,
                "high": 230,
                "lim" : 255
            }
        }

        self.loadSettings() 
        
        self.stack_limit = 25

        self.color_count = 6
        self.grid_count  = 4

        self.color_manager = ColorGenerator(self, self.settings)   
        self.color_grid = [] 

        self.setting_dialog = None
        self.hsv_dialog = None
        self.svpalette_dialog = None 

        self.useFG = False

        self.undo_stack = []

        self.setUI()
        self.connectButtons()
        self.connectColorGrid()
    
    def loadSettings(self):
        self.json_setting = open(os.path.dirname(os.path.realpath(__file__)) + '/settings.json')
        self.settings = json.load(self.json_setting)
        self.json_setting.close() 

    def setUI(self):
        self.base_widget = QWidget()

        self.main_container = QVBoxLayout()
        self.main_container.setContentsMargins(1, 1, 1, 1)

        self.base_widget.setLayout(self.main_container)
        self.setWidget(self.base_widget)

        self.base_widget.setMinimumSize(QSize(160,160))
        #self.base_widget.setMaximumSize(QSize(400,450))

        self.combo_color_opt  = QComboBox()
        self.combo_color_opt.setObjectName(("Color Scheme")) 

        #COLOR BOX
        self.colorbox_widget    = QWidget()
        self.colorbox_container = QGridLayout()
        self.colorbox_widget.setLayout(self.colorbox_container)
        self.colorbox_container.setContentsMargins(4, 0, 4, 0)

        self.main_color_box = QWidget()
        self.main_color_container = QVBoxLayout()
        self.main_color_box.setLayout(self.main_color_container) 
        self.main_color_container.setContentsMargins(0, 0, 0, 0)

        self.gen_colorbox  = QWidget()
        self.gen_color_container = QGridLayout()
        self.gen_colorbox.setLayout(self.gen_color_container)
        self.gen_color_container.setContentsMargins(0, 0, 0, 0)
        
        self.colorbox_container.addWidget(self.combo_color_opt, 0, 0, 1, 7)  
        self.colorbox_container.addWidget(self.main_color_box, 2, 0)
        self.colorbox_container.addWidget(self.gen_colorbox, 2, 1, 1, 6) 

        self.main_color = ColorBox()
        self.main_color_container.addWidget(self.main_color)  

        #COLOR GRID
        for r in range(0, self.grid_count):
            self.color_grid.append([]) 
            for c in range(0, self.color_count):
                self.color_grid[r].append(ColorBox())
                self.gen_color_container.addWidget(self.color_grid[r][c], r, c, 1, 1)

        
        self.button_generate  =  QPushButton("Generate") 

        self.button_fg =  QToolButton() 
        self.button_fg.setIcon( Krita.instance().icon("showColoringOff") ) 
        
        self.button_undo =  QToolButton() 
        self.button_undo.setIcon( Krita.instance().icon("edit-undo") ) 
        
               
        self.button_configure =  QToolButton() 
        self.button_configure.setIcon( Krita.instance().icon("configure-shortcuts") )     

        self.button_hsvtext =  QToolButton() 
        self.button_hsvtext.setIcon( Krita.instance().icon("view-list-text") )   

        self.button_svpalette =  QToolButton() 
        self.button_svpalette.setIcon( Krita.instance().icon('palette-edit') )     

        self.colorbox_container.addWidget(self.button_generate, 5, 0 , 1, 7)  
        self.colorbox_container.addWidget(self.button_fg, 6, 0, 1, 1) 
        self.colorbox_container.addWidget(self.button_undo, 6, 3, 1, 1) 
        self.colorbox_container.addWidget(self.button_svpalette, 6, 4, 1, 1) 
        self.colorbox_container.addWidget(self.button_hsvtext, 6, 5, 1, 1) 
        self.colorbox_container.addWidget(self.button_configure, 6, 6, 1, 1) 
 
        self.main_container.addWidget(self.colorbox_widget)  

        self.main_container.addWidget(self.colorbox_widget)  
 
        #self.test =  QPlainTextEdit() 

        #self.main_container.addWidget(self.test)  

        #COLOR SCHEME 
        for scheme in self.scheme: self.combo_color_opt.addItem(scheme)  
        self.combo_color_opt.setCurrentIndex(self.settings["color_scheme"])
 


    def canvasChanged(self, canvas):
        if canvas:       
            if canvas.view():
                self.connectColorGrid()
            else: 
                self.disconnectColorGrid() 
        else: 
            self.disconnectColorGrid() 
        pass

    #CONNECT BUTTONS
    def connectButtons(self): 
        self.button_generate.clicked.connect(self.generatePalette)
        self.button_configure.clicked.connect(self.openSetting)
        self.button_hsvtext.clicked.connect(self.openHSVOutput)
        self.button_undo.clicked.connect(self.undo)

        self.combo_color_opt.currentIndexChanged.connect(self.saveScheme)

    #COLOR GRID CONNECT
    def connectColorGrid(self):  
        self.button_fg.clicked.connect(self.toggleUseFG)
        self.main_color.clicked.connect(lambda: self.setFGColor(self.main_color))  
        self.button_svpalette.clicked.connect(self.openSavePalette)
        for row in self.color_grid: 
            for color in row:
                color.clicked.connect(partial(self.setFGColor, color )) 

    def disconnectColorGrid(self):
        self.button_fg.setIcon(Krita.instance().icon("showColoringOff"))
        self.useFG = False

        self.button_fg.disconnect() 
        self.main_color.disconnect()
        self.button_svpalette.disconnect()
        for row in self.color_grid: 
            for color in row:
                color.disconnect()

    #Main Button Actions
    def saveScheme(self, index):
        self.settings["color_scheme"] = index

        json_setting = json.dumps(self.settings, indent=4)
    
        with open(os.path.dirname(os.path.realpath(__file__)) + '/settings.json', "w") as outfile:
            outfile.write(json_setting)
        
        self.loadSettings() 
        

    def setFGColor(self, color_box):   
        color_to_set = color_box.getColorForSet(Krita.instance().activeDocument(),  Krita.instance().activeWindow().activeView().canvas())
        Krita.instance().activeWindow().activeView().setForeGroundColor(color_to_set)
 

    def toggleUseFG(self):
        if self.useFG == True:
            self.button_fg.setIcon(Krita.instance().icon("showColoringOff"))
            self.useFG = False
        else:
            self.button_fg.setIcon(Krita.instance().icon("showColoring"))
            self.useFG = True 

        
    
    def openSetting(self):
        if self.setting_dialog == None:
            self.setting_dialog = SettingsDialog(self, "Settings")
            self.setting_dialog.show() 
        elif self.setting_dialog.isVisible() == False : 
            self.setting_dialog.show() 
            #self.setting_dialog.loadDefault()
        else:
            pass
        
        self.moveDialog(self.setting_dialog) 

    def openHSVOutput(self):
        if self.hsv_dialog == None:
            self.hsv_dialog = HSVOutPutDialog(self, "HSV Color Output") 
            self.hsv_dialog.show() 
        elif self.hsv_dialog.isVisible() == False : 
            self.hsv_dialog.show()  
        else:
            pass

        self.moveDialog(self.hsv_dialog)   

    def openSavePalette(self):
        if self.svpalette_dialog == None:
            self.svpalette_dialog = SavePaletteDialog(self, "Save Color Palette") 
            self.svpalette_dialog.show() 
        elif self.svpalette_dialog.isVisible() == False : 
            self.svpalette_dialog.loadDefault()
            self.svpalette_dialog.show()  
        else:
            pass
 
        self.moveDialog(self.svpalette_dialog)  

    def moveDialog(self, dialog):
        gp = self.mapToGlobal(QPoint(0, 0))     
         
        if self.x() < ( QDesktopWidget().screenGeometry().width() // 2) : 
            dialog.move(gp.x() + self.frameGeometry().width() + 10, gp.y() + 30) 
        else:  
            dialog.move(gp.x() - (dialog.frameGeometry().width() + 5 )  , gp.y() + 30) 

    #Palette Scheme Chooser
    def generatePalette(self):
        self.loadSettings() 
        
        cm =  self.color_manager 
        cm.reloadSettings(self.settings) 
        
        if(self.combo_color_opt.currentIndex() == 0):
            self.generateMonochromatic(cm)
        elif(self.combo_color_opt.currentIndex() == 1):
            self.generateAccentedAchromatic(cm)
        elif(self.combo_color_opt.currentIndex() == 2):
            self.generateAnalogous(cm)
        elif(self.combo_color_opt.currentIndex() == 3):
            self.generateComplementary(cm)
        elif(self.combo_color_opt.currentIndex() == 4):
            self.generateSplitComplementary(cm)
        elif(self.combo_color_opt.currentIndex() == 5):
            self.generateDblSplitComplementary(cm)
        elif(self.combo_color_opt.currentIndex() == 6):
            self.generateTriadic(cm)
        elif(self.combo_color_opt.currentIndex() == 7):
            self.generateTetradicSquare(cm)
        elif(self.combo_color_opt.currentIndex() == 8):
            self.generateTetradicRectangle(cm)
        else:
            pass

        self.addToUndoStack()

        
    def addToUndoStack(self):
        if len(self.undo_stack) >= self.stack_limit:
            self.undo_stack.pop(0)
        
        gen_colors = []
        for r in range(0,  self.grid_count):
            gen_colors.append([])
            for c in range(0,  self.color_count): 
                gen_colors[r].append(self.color_grid[r][c].toHSV())

        self.undo_stack.append( { "scheme": self.combo_color_opt.currentIndex(), "main" : self.main_color.toHSV()  , "colors" : gen_colors} )

 
    def undo(self): 
        if len(self.undo_stack) > 1:
            self.undo_stack.pop()
            to_undo = self.undo_stack[len(self.undo_stack)-1] 

            self.combo_color_opt.setCurrentIndex(to_undo["scheme"])

            self.main_color.setColorHSV(to_undo["main"]["H"], to_undo["main"]["S"], to_undo["main"]["V"]) 
             
            gen_colors = to_undo["colors"]
            
            for r in range(0,  self.grid_count):
                for c in range(0,  self.color_count): 
                    self.color_grid[r][c].setColorHSV(gen_colors[r][c]["H"], gen_colors[r][c]["S"], gen_colors[r][c]["V"]) 


    def calc_interval(self, start, end, count, floor = 5):
        interval = ( end - start ) // count
        if interval < floor: 
            return floor 
        else:
            return interval


    def getHSV(self, colmgr):
        if(self.useFG == True):
            FG = colmgr.getFGColor(Krita.instance().activeWindow().activeView(), Krita.instance().activeDocument())
            return { "hue" : FG.hsvHue(), "sat" : FG.hsvSaturation(), "val" : FG.value() }
        else:
            random.seed()
            return { "hue" : colmgr.setHue(), "sat" : colmgr.setSat(), "val" : colmgr.setVal() }

     
    #Palette Generator
    def generateMonochromatic(self, cm): 

        hsv = self.getHSV(cm)   
        
        self.main_color.setColorHSV( hsv["hue"], hsv["sat"], hsv["val"])  

        i_val  = self.calc_interval(self.settings["value_cutoff"]["low"], self.settings["value_cutoff"]["lim"], self.color_count, 2)    
        val    = [ self.settings["value_cutoff"]["low"] ,  i_val + self.settings["value_cutoff"]["low"] ]
        
        i_sat  = self.calc_interval(self.settings["saturation_cutoff"]["low"], self.settings["saturation_cutoff"]["lim"], 4, 2)    
        sat    = [ self.settings["saturation_cutoff"]["low"],  self.settings["saturation_cutoff"]["low"] + i_sat ]
      

        #remove cut_off for monochromatic. 
        for c in range(0,  self.color_count):
            self.color_grid[0][c].setColorHSV( cm.setHue(hsv["hue"],  random.randint(-5, -1)), cm.setSat(random.randint(sat[0], sat[1])), cm.setVal(random.randint(val[0], val[1])) ) 
            
            sat = [ sat[0] + i_sat, sat[1] + i_sat ] 

            self.color_grid[1][c].setColorHSV( cm.setHue(hsv["hue"]), cm.setSat(random.randint(sat[0], sat[1])), cm.setVal(random.randint(val[0], val[1])) ) 
            
            sat = [ sat[0] + i_sat, sat[1] + i_sat ] 
           
            self.color_grid[2][c].setColorHSV( cm.setHue(hsv["hue"],  random.randint(1, 5)), cm.setSat(random.randint(sat[0], sat[1])), cm.setVal(random.randint(val[0], val[1])) ) 
            
            sat = [ sat[0] + i_sat, sat[1] + i_sat ] 
           
            self.color_grid[3][c].setColorHSV( cm.setHue(hsv["hue"],  random.randint(1, 5)), cm.setSat(random.randint(sat[0], sat[1])), cm.setVal(random.randint(val[0], val[1])) ) 

            sat = [ self.settings["saturation_cutoff"]["low"],  self.settings["saturation_cutoff"]["low"] + i_sat ] 
            
            val = [ val[0] + i_val, val[1] + i_val ]  
             
        
        self.printHSV() 
        cm.reloadSettings(self.settings)
            

    def generateAccentedAchromatic(self, cm):
        
        hsv = self.getHSV(cm)  

        self.main_color.setColorHSV( hsv["hue"], hsv["sat"], hsv["val"]) 
         
        cv = [-1* self.settings["color_variance"],self.settings["color_variance"]] 
        for r in range(0,  self.grid_count):
            random.seed() 
            self.color_grid[r][0].setColorHSV( cm.setHue(hsv["hue"], random.randint(cv[0],cv[1])), cm.setSat(), cm.setVal())
 
        
        cm.settings["saturation_cutoff"]["low"]   = 0
        cm.settings["saturation_cutoff"]["lim"]   = 255
        cm.settings["value_cutoff"]["low"] = 0
        cm.settings["value_cutoff"]["lim"] = 255 

        for r in range(0,  self.grid_count // 2):
            random.seed() 
            self.color_grid[r][1].setColorHSV( cm.setHue(hsv["hue"], -1 * random.randint(0,120)), cm.setSat(random.randint(2, 45)), cm.setVal(random.randint(25, 65)))
            self.color_grid[r+2][1].setColorHSV( cm.setHue(hsv["hue"], random.randint(0,120)), cm.setSat(random.randint(2, 45)), cm.setVal(random.randint(25, 65)))
 
    
        for r in range(0,  self.grid_count // 2):
            for c in range(2,  4): 
                self.color_grid[r][c].setColorHSV( cm.setHue(hsv["hue"], -1 * random.randint(0,120)), cm.setSat(random.randint(2, 40)), cm.setVal(random.randint(45, 150)))  
                self.color_grid[r+2][c].setColorHSV( cm.setHue(hsv["hue"], random.randint(0,120)), cm.setSat(random.randint(2, 40)), cm.setVal(random.randint(45, 150)))  

            for c in range(4,  6): 
                self.color_grid[r][c].setColorHSV( cm.setHue(hsv["hue"], -1 * random.randint(0,120)), cm.setSat(random.randint(2, 40)), cm.setVal(random.randint(150, 250))) 
                self.color_grid[r+2][c].setColorHSV( cm.setHue(hsv["hue"], random.randint(0,120)), cm.setSat(random.randint(2, 40)), cm.setVal(random.randint(150, 250))) 
                
        
        self.printHSV()  
        cm.reloadSettings(self.settings)
        

    def generateAnalogous(self, cm): 
        
        hsv = self.getHSV(cm)  

        self.main_color.setColorHSV( hsv["hue"], hsv["sat"], hsv["val"]) 

        hues = []
        random.seed()
        hues.append(cm.setHue(hsv["hue"] -  random.randint(25,60)))
        hues.append(cm.setHue(hsv["hue"] +  random.randint(25,60))) 
        random.shuffle(hues)

        cv = [-1* self.settings["color_variance"],self.settings["color_variance"]]      
        for r in range(0,  self.grid_count):
            for c in range(0,  3): 
                random.seed() 
                self.color_grid[r][c].setColorHSV( cm.setHue(hsv["hue"], random.randint(cv[0],cv[1])), cm.setSat(), cm.setVal())  
            
            for c in range(3,  5): 
                random.seed() 
                self.color_grid[r][c].setColorHSV( cm.setHue(hues[0], random.randint(cv[0],cv[1]) ), cm.setSat(), cm.setVal())  

            for c in range(5,  6): 
                random.seed() 
                self.color_grid[r][c].setColorHSV( cm.setHue(hues[1], random.randint(cv[0],cv[1]) ), cm.setSat(), cm.setVal())  

        
        self.printHSV() 
        cm.reloadSettings(self.settings)
 
        #self.button_generate.setText("Analogous")
        pass

    def generateComplementary(self, cm):
      
        hsv = self.getHSV(cm)  
         
        self.main_color.setColorHSV( hsv["hue"], hsv["sat"], hsv["val"]) 
        comp_color = cm.setHue(hsv["hue"] + 180) 
     
        cv = [-1* self.settings["color_variance"],self.settings["color_variance"]]      
        for r in range(0,  self.grid_count):
            for c in range(0,  3): 
                random.seed() 
                self.color_grid[r][c].setColorHSV( cm.setHue(hsv["hue"], random.randint(cv[0],cv[1])), cm.setSat(), cm.setVal())  
            
            for c in range(3,  6): 
                random.seed() 
                self.color_grid[r][c].setColorHSV( cm.setHue(comp_color, random.randint(cv[0],cv[1]) ), cm.setSat(), cm.setVal())  

        
        self.printHSV() 
        cm.reloadSettings(self.settings)
 

    def generateSplitComplementary(self, cm): 

        hsv = self.getHSV(cm)  

        self.main_color.setColorHSV( hsv["hue"], hsv["sat"], hsv["val"]) 
        
        hues = []
        random.seed()
        hues.append(cm.setHue(hsv["hue"] + (180 + random.randint(15,50))))
        hues.append(cm.setHue(hsv["hue"] + (180 - random.randint(15,50)))) 
        random.shuffle(hues)
 
 
        cv = [-1* self.settings["color_variance"],self.settings["color_variance"]]      
        for r in range(0,  self.grid_count):
            for c in range(0,  3): 
                random.seed() 
                self.color_grid[r][c].setColorHSV( cm.setHue(hsv["hue"], random.randint(cv[0],cv[1])), cm.setSat(), cm.setVal())  
            
            for c in range(3,  5): 
                random.seed() 
                self.color_grid[r][c].setColorHSV( cm.setHue(hues[0], random.randint(cv[0],cv[1]) ), cm.setSat(), cm.setVal())  

            for c in range(5,  6): 
                random.seed() 
                self.color_grid[r][c].setColorHSV( cm.setHue(hues[1], random.randint(cv[0],cv[1]) ), cm.setSat(), cm.setVal())  
        #self.button_generate.setText("Split Complementary")
        
        self.printHSV() 
        cm.reloadSettings(self.settings)
         

    def generateDblSplitComplementary(self, cm):
     
        hsv = self.getHSV(cm)  
           
        self.main_color.setColorHSV( hsv["hue"], hsv["sat"], hsv["val"])  
         
        hues = [] 
        random.seed() 
        hues.append(cm.setHue(hsv["hue"] - random.randint(30,75)))
        hues.append(cm.setHue(hsv["hue"]  + (180 + random.randint(-5,5))))
        hues.append(cm.setHue(hues[0] + (180 - random.randint(-5,5))))  
        random.shuffle(hues)  


        cv = [-1* self.settings["color_variance"],self.settings["color_variance"]]      
        for r in range(0,  self.grid_count):
            for c in range(0,  2): 
                random.seed() 
                self.color_grid[r][c].setColorHSV( cm.setHue(hsv["hue"], random.randint(cv[0],cv[1])), cm.setSat(), cm.setVal())  
            
            for c in range(2,  4): 
                random.seed() 
                self.color_grid[r][c].setColorHSV( cm.setHue(hues[0], random.randint(cv[0],cv[1])), cm.setSat(), cm.setVal())  

            for c in range(4,  5): 
                random.seed() 
                self.color_grid[r][c].setColorHSV( cm.setHue(hues[1], random.randint(cv[0],cv[1])), cm.setSat(), cm.setVal())  
                
            for c in range(5,  6): 
                random.seed() 
                self.color_grid[r][c].setColorHSV( cm.setHue(hues[2], random.randint(cv[0],cv[1])), cm.setSat(), cm.setVal())  
        
        self.printHSV()
        cm.reloadSettings(self.settings) 

    def generateTriadic(self, cm):
         
        hsv = self.getHSV(cm)  
        
        self.main_color.setColorHSV( hsv["hue"], hsv["sat"], hsv["val"])  
        
        hues = []  
        random.seed()
        hues.append(cm.setHue(hsv["hue"] + 120))
        hues.append(cm.setHue(hues[0] + 120)) 
        random.shuffle(hues)  
        
        
        cv = [-1* self.settings["color_variance"],self.settings["color_variance"]]      
        for r in range(0,  self.grid_count):
            for c in range(0,  3): 
                random.seed() 
                self.color_grid[r][c].setColorHSV( cm.setHue(hsv["hue"], random.randint(cv[0],cv[1])), cm.setSat(), cm.setVal())  
            
            for c in range(3,  5): 
                random.seed() 
                self.color_grid[r][c].setColorHSV( cm.setHue(hues[0], random.randint(cv[0],cv[1]) ), cm.setSat(), cm.setVal())  

            for c in range(5,  6): 
                random.seed() 
                self.color_grid[r][c].setColorHSV( cm.setHue(hues[1], random.randint(cv[0],cv[1]) ), cm.setSat(), cm.setVal()) 
            
            
        self.printHSV() 
        cm.reloadSettings(self.settings)
      

    def generateTetradicSquare(self, cm):
        
        hsv = self.getHSV(cm)  
        
        
        self.main_color.setColorHSV( hsv["hue"], hsv["sat"], hsv["val"])  

        hues = []  
        random.seed()
        hues.append(cm.setHue(hsv["hue"] + 90))
        hues.append(cm.setHue(hues[0] + 90))
        hues.append(cm.setHue(hues[1] + 90)) 
        random.shuffle(hues)  
        
        
        cv = [-1* self.settings["color_variance"],self.settings["color_variance"]]      
        for r in range(0,  self.grid_count):
            for c in range(0,  2): 
                random.seed() 
                self.color_grid[r][c].setColorHSV( cm.setHue(hsv["hue"], random.randint(cv[0],cv[1])), cm.setSat(), cm.setVal())  
            
            for c in range(2,  4): 
                random.seed() 
                self.color_grid[r][c].setColorHSV( cm.setHue(hues[0], random.randint(cv[0],cv[1])), cm.setSat(), cm.setVal())  

            for c in range(4,  5): 
                random.seed() 
                self.color_grid[r][c].setColorHSV( cm.setHue(hues[1], random.randint(cv[0],cv[1])), cm.setSat(), cm.setVal())  
                
            for c in range(5,  6): 
                random.seed() 
                self.color_grid[r][c].setColorHSV( cm.setHue(hues[2], random.randint(cv[0],cv[1])), cm.setSat(), cm.setVal())  
        
        self.printHSV() 
        cm.reloadSettings(self.settings)
        pass

    def generateTetradicRectangle(self, cm):
         
        hsv = self.getHSV(cm)  
        
        self.main_color.setColorHSV( hsv["hue"], hsv["sat"], hsv["val"])  

        hues = []

        dis =  random.randint(60,85) if random.randint(0,1) == 0 else  -1 * random.randint(60,85)
        hues.append(cm.setHue(hsv["hue"] + dis))
        hues.append(cm.setHue(hsv["hue"] + 180))
        hues.append(cm.setHue(hues[0] + 180))

        random.shuffle(hues)  
        
        cv = [-1* self.settings["color_variance"],self.settings["color_variance"]]      
        for r in range(0,  self.grid_count):
            for c in range(0,  2): 
                random.seed() 
                self.color_grid[r][c].setColorHSV( cm.setHue(hsv["hue"], random.randint(cv[0],cv[1])), cm.setSat(), cm.setVal())  
            
            for c in range(2,  4): 
                random.seed() 
                self.color_grid[r][c].setColorHSV( cm.setHue(hues[0], random.randint(cv[0],cv[1])), cm.setSat(), cm.setVal())  

            for c in range(4,  5): 
                random.seed() 
                self.color_grid[r][c].setColorHSV( cm.setHue(hues[1], random.randint(cv[0],cv[1])), cm.setSat(), cm.setVal())  
                
            for c in range(5,  6): 
                random.seed() 
                self.color_grid[r][c].setColorHSV( cm.setHue(hues[2], random.randint(cv[0],cv[1])), cm.setSat(), cm.setVal())  
        
        self.printHSV() 
        cm.reloadSettings(self.settings)
    
    def printHSV(self): 
        if self.hsv_dialog :
           self.hsv_dialog.printHSV()

instance = Krita.instance()
dock_widget_factory = DockWidgetFactory(DOCKER_ID,
                                        DockWidgetFactoryBase.DockRight,
                                        PaletteGenerator)

instance.addDockWidgetFactory(dock_widget_factory) 