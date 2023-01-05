
#-----------------------------------------------------------------------------#
# Palette Generator - Copyright (c) 2023 - kaichi1342                         #
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
import os, json  

from PyQt5.QtCore import ( Qt, pyqtSignal, QEvent)

from PyQt5.QtGui import (QStandardItemModel)


from PyQt5.QtWidgets import ( 
        QWidget, QFrame, QDialog, QDoubleSpinBox,
        QVBoxLayout, QHBoxLayout, QGridLayout, QSpacerItem, QSizePolicy,
        QLabel, QPushButton, QToolButton, QComboBox , QCheckBox,
        QListWidget, QLineEdit, QListWidgetItem, QMenu,
        QMessageBox
)


class DoubleSpinBox(QDoubleSpinBox):
    stepChanged = pyqtSignal() 
    
    def __init__(self):
         super(QDoubleSpinBox, self).__init__() 
    
    def __init__(self, low = 0, high = 0, step = 0):
        super(QDoubleSpinBox, self).__init__() 
        self.setRange(low, high)
        self.setSingleStep(step)

    def stepBy(self, step):
        value = self.value()
        super(DoubleSpinBox, self).stepBy(step)
        if self.value() != value:
            self.stepChanged.emit()

    def focusOutEvent(self, e):
        value = self.value() 
        super(DoubleSpinBox, self).focusOutEvent(e)
        self.stepChanged.emit()

class SettingsDialog(QDialog):
    def __init__(self, parent, title = "" ):
        super().__init__(parent)
        
        self.resize(350,210)
        self.setWindowTitle(title)  

        self.loadSettings()
        self.setUI()
        self.loadDefault()
        self.connectSignals()

    
    # UI LAYOUT
    def setUI(self):
        self.setting_container = QVBoxLayout() 
        self.setting_container.setContentsMargins(5, 5, 5, 5)
    
        self.setLayout(self.setting_container)  

        self.general_container =  QHBoxLayout()
        self.general_widget = QWidget()
        self.general_widget.setLayout(self.general_container)
        self.general_container.setContentsMargins(0, 0, 0, 0)

        self.setting_container.addWidget(self.general_widget)
        
        self.roll_container =  QGridLayout()  
        self.roll_container.setContentsMargins(0, 0, 0, 0)
        self.frame_color_setting = QWidget()
        self.frame_color_setting.setLayout(self.roll_container) 

        self.label_sat = QLabel("Saturation Range")
        self.label_val = QLabel("Value Range")
        self.combo_sat = QComboBox()
        self.combo_val = QComboBox() 
        self.combo_sat.setToolTip("Set Color Saturation RNG Priority")
        self.combo_val.setToolTip("Set Color Value RNG Priority")     
        
        self.dsb_sat_low  = DoubleSpinBox(1,255,1)
        self.dsb_sat_mid  = DoubleSpinBox(1,255,1)
        self.dsb_sat_high = DoubleSpinBox(1,255,1)
        self.dsb_sat_lim  = DoubleSpinBox(1,255,1)
        self.dsb_val_low  = DoubleSpinBox(1,255,1)
        self.dsb_val_mid  = DoubleSpinBox(1,255,1)
        self.dsb_val_high = DoubleSpinBox(1,255,1)
        self.dsb_val_lim  = DoubleSpinBox(1,255,1)

        self.dsb_sat_low.setToolTip("Saturation Lower Bound Start")
        self.dsb_sat_mid.setToolTip("Saturation Mid Bound Start")
        self.dsb_sat_high.setToolTip("Saturation Upper Bound Start") 
        self.dsb_sat_lim.setToolTip("Saturation Upper Bound Limit") 
        self.dsb_val_low.setToolTip("Value Lower Bound Start")
        self.dsb_val_mid.setToolTip("Value Mid Bound Start")
        self.dsb_val_high.setToolTip("Value Upper Bound Start")
        self.dsb_val_lim.setToolTip("Value Upper Bound Limit") 
 

        self.roll_container.addWidget(self.label_sat, 2, 0, 1, 8)
        self.roll_container.addWidget(self.combo_sat, 3, 0, 1, 8)

        self.roll_container.addWidget(self.dsb_sat_low,     4, 0, 1, 2) 
        self.roll_container.addWidget(self.dsb_sat_mid,     4, 2, 1, 2) 
        self.roll_container.addWidget(self.dsb_sat_high,    4, 4, 1, 2)
        self.roll_container.addWidget(self.dsb_sat_lim,     4, 6, 1, 2)
        
        self.roll_container.addWidget(self.label_val, 5, 0, 1, 8)
        self.roll_container.addWidget(self.combo_val, 6, 0, 1, 8)
 
        self.roll_container.addWidget(self.dsb_val_low,     7, 0, 1, 2)
        self.roll_container.addWidget(self.dsb_val_mid,     7, 2, 1, 2)
        self.roll_container.addWidget(self.dsb_val_high,    7, 4, 1, 2)
        self.roll_container.addWidget(self.dsb_val_lim,     7, 6, 1, 2) 
        
        self.general_container.addWidget(self.frame_color_setting )     

        self.action_container =  QGridLayout()
        self.action_widget = QWidget()
        self.action_widget.setLayout(self.action_container)
        self.action_widget.setContentsMargins(0, 0, 0, 0)
 
        self.button_ok      = QPushButton("&Save")
        self.button_cancel  = QPushButton("&Cancel") 
        
        self.action_container.addWidget(self.button_ok, 0, 2, 1, 1 )  
        self.action_container.addWidget(self.button_cancel, 0, 3, 1, 1 )  

        self.setting_container.addWidget(self.action_widget ) 


    def loadDefault(self): 
        
        self.dsb_sat_low.setValue(self.evalSettingValue(self.settings["saturation_cutoff"]["low"], 1, 255))
        self.dsb_sat_mid.setValue(self.evalSettingValue(self.settings["saturation_cutoff"]["mid"], 1, 255))
        self.dsb_sat_high.setValue(self.evalSettingValue(self.settings["saturation_cutoff"]["high"], 1, 255))
        self.dsb_sat_lim.setValue(self.evalSettingValue(self.settings["saturation_cutoff"]["lim"], 1, 255))

        self.dsb_val_low.setValue(self.evalSettingValue(self.settings["value_cutoff"]["low"], 1, 255))
        self.dsb_val_mid.setValue(self.evalSettingValue(self.settings["value_cutoff"]["mid"], 1, 255))
        self.dsb_val_high.setValue(self.evalSettingValue(self.settings["value_cutoff"]["high"], 1, 255))
        self.dsb_val_lim.setValue(self.evalSettingValue(self.settings["value_cutoff"]["lim"], 1, 255))
  
        self.color_priority_option = ["Low", "Mid", "High", "Low Only", "Mid Only", "High Only", "Normal", "Equal"]
        
        self.combo_sat.clear()
        for prio in self.color_priority_option:
            if prio == "Equal" : self.combo_sat.addItem(prio + " Distribution")
            elif prio == "Normal" : self.combo_sat.addItem(prio + " Distribution")
            elif "Only" in prio:  
                word = prio.split()
                self.combo_sat.addItem("Only " + word[0]+ " Saturated Color")
            else: self.combo_sat.addItem("More "+ prio + " Saturated Color" )

        self.combo_val.clear()
        for prio in self.color_priority_option: 
            if(prio == "Equal") : self.combo_val.addItem(prio + " Distribution")
            elif(prio == "Normal") : self.combo_val.addItem(prio + " Distribution")
            elif "Only" in prio:  
                word = prio.split()
                self.combo_val.addItem(word[0]+ " Value Color Only ")
            else: self.combo_val.addItem("More "+ prio + " Value Color" )

        def_sat_idx = self.color_priority_option.index(self.settings["saturation_priority"])
        def_val_idx = self.color_priority_option.index(self.settings["value_priority"])
        if def_sat_idx != -1 : self.combo_sat.setCurrentIndex(def_sat_idx)
        if def_val_idx != -1 : self.combo_val.setCurrentIndex(def_val_idx)

    
    def loadSettings(self):
        json_setting = open(os.path.dirname(os.path.realpath(__file__)) + '/settings.json')
        self.settings = json.load(json_setting)
        json_setting.close() 
    
    def evalSettingValue(self, value, low, high, off_low = 0, off_high = 0 ):
        if value < low: 
            value = low + off_low
        elif value > high:
            value = high + off_high
        else:
            pass
        return value 
    
    
    #SIGNALS

    def connectSignals(self): 
        self.button_ok.clicked.connect(self.saveSettings)
        self.button_cancel.clicked.connect(self.cancelSave)

    
    def cancelSave(self): 
        self.loadSettings()
        self.done(0)

    def saveSettings(self):   
        self.settings["saturation_priority"] = self.color_priority_option[self.combo_sat.currentIndex()]
        self.settings["value_priority"]      = self.color_priority_option[self.combo_val.currentIndex()]

        self.settings["saturation_cutoff"]["low"]  = int(self.dsb_sat_low.value())
        self.settings["saturation_cutoff"]["mid"]  = int(self.dsb_sat_mid.value())
        self.settings["saturation_cutoff"]["high"]  = int(self.dsb_sat_high.value())
        self.settings["saturation_cutoff"]["lim"]  = int(self.dsb_sat_lim.value())
 
        self.settings["value_cutoff"]["low"] = int(self.dsb_val_low.value())
        self.settings["value_cutoff"]["mid"] = int(self.dsb_val_mid.value())
        self.settings["value_cutoff"]["high"] = int(self.dsb_val_high.value())
        self.settings["value_cutoff"]["lim"]  = int(self.dsb_val_lim.value())

        json_setting = json.dumps(self.settings, indent = 4)
    
        with open(os.path.dirname(os.path.realpath(__file__)) + '/settings.json', "w") as outfile:
            outfile.write(json_setting)
        
        self.loadSettings()
        self.done(0)
        