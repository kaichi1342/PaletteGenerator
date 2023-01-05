
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
        QLabel, QHBoxLayout, QDialog, QWidget, QVBoxLayout
) 
 
class HSVOutPutDialog(QDialog):
    def __init__(self, parent, title = "" ):
        super().__init__(parent)
        
        self.resize(200,450)
        self.setWindowTitle(title)  
 
        self.setUI() 
        self.printHSV()

    # UI LAYOUT
    def setUI(self):
        self.output_container = QVBoxLayout() 
        self.output_container.setContentsMargins(5, 5, 5, 5)
    
        self.setLayout(self.output_container)  

        self.general_container =  QHBoxLayout()
        self.general_widget = QWidget()
        
        self.label      = QLabel() 
        self.output_container.addWidget(self.label) 

    def printHSV(self): 
        this_label = self.label
        this_label.setText(  "")
        for c in range(0,  self.parent().color_count): 
            for r in range(0,  self.parent().grid_count):
                this_label.setText(this_label.text() + self.parent().color_grid[r][c].toStringHSV() + "\n")
            this_label.setText(this_label.text() + "\n")
     
    def addToLabel(self, text):
        self.label.setText(self.label.text()+ text)