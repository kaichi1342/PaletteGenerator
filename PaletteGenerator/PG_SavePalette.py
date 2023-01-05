
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
import os, json, zipfile 

#from PyQt5.QtCore import ( Qt, pyqtSignal, QEvent)

#from PyQt5.QtGui import (QStandardItemModel)


from PyQt5.QtWidgets import ( 
    QLabel, QHBoxLayout, QDialog, QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QFileDialog, QMessageBox
) 
 
 
class KPL_Creator(): 
    def __init__(self):   
        self.scheme_dict = {
            "Monochromatic"         : "mono", 
            "Accented Achromatic"   : "acct", 
            "Analogous"             : "ang", 
            "Complementary"         : "comp", 
            "Split Complementary"   : "scomp", 
            "Double Split Complementary"  : "dsc",
            "Triadic"               : "triad", 
            "Tetradic Square"       : "tetsq",  
            "Tetradic Rectangle"    : "tetrc" 
        }
        self.scheme_key = "mono"
        self.colorDepth = "U8"
        self.colorProfile = ""
        super().__init__() 

    def setColorScheme(self, scheme):
        self.scheme = scheme
        self.scheme_key = self.scheme_dict[scheme]

    def createProfile(self, file):  
        doc = Krita.instance().activeDocument()
        self.colorDepth   = doc.colorDepth()
        self.colorProfile = doc.colorProfile()
        comment = "Generated From Palette Generator Plugin - " + self.scheme + " Color Scheme."
        with open(os.path.dirname(os.path.realpath(__file__)) +  file, "w") as outfile: 
            outfile.write('<Profiles>\n')
            outfile.write('  <Profile filename="' + doc.colorProfile() + '" colorDepthId="' + doc.colorDepth() + '" colorModelId="' + doc.colorModel() + '" name="' + doc.colorProfile() + '" comment="' + comment + ' "/>\n')
            outfile.write('</Profiles>\n')


    def createColorSet(self, file, kpl_name, main_color, color_grid,  row = 4, col = 7):
        self.row = row
        self.col = col
        with open(os.path.dirname(os.path.realpath(__file__)) + file, "w") as outfile: 
            outfile.write('<ColorSet version="2.0" rows="' + str(self.row) + '" columns="' + str(self.col) + '" name="' + kpl_name + '" comment="">\n')
            self.kplColorGrid(outfile, main_color, color_grid)
            outfile.write('</ColorSet>\n')

     
    def kplColorGrid(self, outfile, main_color, color_grid):
        for r in range(0, self.row):
           self.kplSetColorEntry(outfile, main_color.color,  main_color.getHueName() + '_'  , r, 0) 

        for r in range(0, self.row):
            for c in range(1, self.col):
                self.kplSetColorEntry(outfile, color_grid[r][c-1].color,  color_grid[r][c-1].getHueName() + '_' , r, c) 
 

    def kplSetColorEntry(self, outfile, color, color_name, r, c): 
        color_name = color_name + "r" + str(r) + "c" + str(c)
        outfile.write('  <ColorSetEntry spot="true" id="' + color_name + '"  name="' + color_name + '" bitdepth="' + self.colorDepth + '">\n') 
        outfile.write('    <RGB space="' + str(self.colorProfile) + '" r="' + str(color.redF()) + '" g="' + str(color.greenF()) + '" b="' + str(color.blueF()) + '"/>\n') 
        outfile.write('    <Position row="'+str(r)+'" column="'+str(c)+'"/>\n')
        outfile.write('  </ColorSetEntry>\n')


class SavePaletteDialog(QDialog):
    def __init__(self, parent, title = "" ):
        super().__init__(parent)
        
        self.resize(200,80)  
        self.setWindowTitle(title)  

        self.KPL_Maker = KPL_Creator()
        self.setUI() 

    # UI LAYOUT
    def setUI(self):
        self.main_container = QVBoxLayout() 
        self.main_container.setContentsMargins(5, 5, 5, 5)
    
        self.setLayout(self.main_container)  

        self.button_container =  QHBoxLayout()
        self.button_widget = QWidget()
        self.button_widget.setLayout(self.button_container)
        self.button_container.setContentsMargins(0, 0, 0, 0)
        
        self.label_palette      = QLabel("Palette Name") 
        self.palette_name       = QLineEdit() 
        self.button_save        = QPushButton("Save") 
        self.button_export       = QPushButton("Export") 
        self.label_test         = QLabel()

        self.main_container.addWidget(self.label_palette) 
        self.main_container.addWidget(self.palette_name) 
 
        self.main_container.addWidget(self.button_widget) 

        self.button_container.addWidget(self.button_save)  
        self.button_container.addWidget(self.button_export) 

        #self.main_container.addWidget(self.label_test) 

        self.dlg = QFileDialog()
        self.dlg.setFileMode(QFileDialog.AnyFile)
 
        self.button_save.clicked.connect(lambda: self.savePalette(""))
        self.button_export.clicked.connect(self.browseDirectory)

    def loadDefault(self):
        self.palette_name.setText("")
 

    def browseDirectory(self):    
        filepath = str(QFileDialog.getExistingDirectory(self, "Select Directory")) 
        self.savePalette(filepath) 
         
 

    def savePalette(self, filepath = ""):   
        doc = Krita.instance().activeDocument()
       
        if doc == None: 
            QMessageBox.warning(self, "Error", "Error: No document selected.")  
            return False
        if doc.colorModel() != "RGBA" and doc.colorProfile() != "sRGB-elle-V2-srgbtrc.icc":
            QMessageBox.warning(self, "Error", "Error: Invalid Color Model: This function only works with RGBA model and sRGB-elle-V2-srgbtrc.icc profile.") 
            return False

        if  self.palette_name.text() == "": 
            QMessageBox.warning(self, "Error", "Error: Empty file name.") 
            return False

        kpl_name = self.palette_name.text()
        kpl_name = "".join(x for x in kpl_name if x.isalnum() or  x in "._- ")
     
        if kpl_name == "": 
            QMessageBox.warning(self, "Error", "Error: Invalid file name.") 
            return False

        self.KPL_Maker.setColorScheme(self.parent().combo_color_opt.currentText())
        self.KPL_Maker.createProfile('/paletteTemplate/profiles.xml')
        self.KPL_Maker.createColorSet('/paletteTemplate/colorset.xml', kpl_name, self.parent().main_color, self.parent().color_grid )
         
        self.saveKPL(kpl_name, filepath)
        self.done(0)
        return True


    def saveKPL(self, kpl_name, filepath = ""):   
        
        palette_file = os.path.dirname(os.path.realpath(__file__)) + '/../../palettes/' + kpl_name + '.kpl' if filepath == "" else filepath + '/' + kpl_name + '.kpl'

        isExist = os.path.exists(palette_file)

        if isExist : 
            QMessageBox.warning(self, "Error", "Error: Palette name already exist.") 
            return False

        content_loc  = os.path.dirname(os.path.realpath(__file__)) + '/paletteTemplate'
        with zipfile.ZipFile(palette_file, 'w') as palette_zip:
            for folderName, subfolders, filenames in os.walk(content_loc):
                for filename in filenames: 
                    filePath = os.path.join(folderName, filename) 
                    palette_zip.write(filePath, os.path.basename(filePath))
     
        QMessageBox.information(self, "Success", "Palette have been succesfully saved.")

        return True 
 