"""
/***************************************************************************
DeHazeImageDialog
A QGIS plugin
Removes Haze from Sat Image based on HOT
                             -------------------
begin                : 2009-09-10 
copyright            : (C) 2009 by Marx Tupas
email                : marx_tupas@gmail.com 
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4 import QtCore, QtGui 
from Ui_DeHazeImage import Ui_DeHazeImage
# create the dialog for zoom to point
class DeHazeImageDialog(QtGui.QDialog):
  def __init__(self): 
    QtGui.QDialog.__init__(self) 
    # Set up the user interface from Designer. 
    self.ui = Ui_DeHazeImage()
    self.ui.setupUi(self) 

