"""
/***************************************************************************
DeHazeImage
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
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import * 
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from DeHazeImageDialog import DeHazeImageDialog
# import libraries used
from osgeo import gdal
from osgeo.gdalconst import *
from numpy import *
import math
import sys
# import modified region tool
import regionTool

class DeHazeImage:

  CLrect = None
  band = None
  Top = None

  def __init__(self, iface):
    # Save reference to the QGIS interface
    self.iface = iface

  def initGui(self):
        
    # Create action that will start plugin configuration
    self.action = QAction(QIcon(":/plugins/dehazeimage/icon.png"), \
        "Load Hazy Image", self.iface.mainWindow())
    # connect the action to the run method
    QObject.connect(self.action, SIGNAL("triggered()"), self.run)

    self.actionRunHot = QAction(QIcon(":/plugins/dehazeimage/mAction.png"),"start HOT Haze removal", self.iface.mainWindow())
    QObject.connect( self.actionRunHot, SIGNAL("triggered()"), self.runHOT)
      
    self.actionMarkCL = QAction(QIcon(":/plugins/dehazeimage/mActionZoomFullExtent.png"),"Clear Sky Region Select", self.iface.mainWindow())
    QObject.connect( self.actionMarkCL, SIGNAL("activated()"), self.MarkCLactivate)
  
    # Create a toolbar
    self.toolbar = self.iface.addToolBar("HOT")
      
    # Add the actions to the toolbar
    self.toolbar.addAction(self.action)
    self.toolbar.addAction(self.actionMarkCL)
    self.toolbar.addAction(self.actionRunHot)

    # tool created to get marked CL
    self.toolMarkCL = regionTool.regionTool(self.iface.mapCanvas())
    QObject.connect( self.toolMarkCL.o,SIGNAL("finished(PyQt_PyObject)"), self.MarkCL)

    # Add toolbar button and menu item
    # self.iface.addToolBarIcon(self.action)
    #self.iface.addPluginToMenu("&De Haze (HOT)", self.action)

  def unload(self):
    # Remove the plugin menu item and icon
    #self.iface.removePluginMenu("&De Haze (HOT)",self.action)
    self.iface.removeToolBarIcon(self.action)
    self.iface.removeToolBarIcon(self.actionMarkCL)
    self.iface.removeToolBarIcon(self.actionRunHot)
    if self.CLrect != None:
      self.CLrect.reset(True)
      
    
  def lr(self,x,y,n):
    # linear regression 
    xbar = x.sum()/n;
    ybar = y.sum()/n;

    xxbar = 0.0
    yybar = 0.0
    xybar = 0.0
    
    for m in range(n):
        xxbar = xxbar + ((x[m] - xbar) * (x[m] - xbar))
        yybar = yybar + ((y[m] - ybar) * (y[m] - ybar))
        xybar = xybar + ((x[m] - xbar) * (y[m] - ybar))
    
    m = xybar / xxbar
    b = ybar - m * xbar
    return [m,b]
  
  def MarkCLactivate(self):
    # sets CL select tool as map tool
    self.iface.mapCanvas().setMapTool(self.toolMarkCL)
    if self.CLrect == None:
      QMessageBox.about(None,'dehaze','load and select image first'  )
      return
    self.CLrect.reset(True)
    

  def MarkCL(self,b):
    # after selecting CL pixels get extent of region
    # chack if image is selected
    if self.Gref == None:
      QMessageBox.about(None,'dehaze','load and select image first'  )
      return
    self.CLrect.reset(True)
     # check if georeferenced
    if (self.Gref == ''):
      # not georeferenced
      self.Left = max (b.xMinimum(), 0)
      self.Right = min (b.xMaximum(), self.cols_count )
      self.Bottom = min ((b.yMinimum()*-1),self.rows_count)
      self.Top = max ((b.yMaximum()*-1),0)
    else:
      # georeferenced
      tempXmin = (b.xMinimum()- self.GT[0]) / self.GT[1]
      tempXmax = (b.xMaximum()- self.GT[0]) / self.GT[1]
      tempYmax = (b.yMinimum()- self.GT[3]) / self.GT[5]
      tempYmin = (b.yMaximum()- self.GT[3]) / self.GT[5]
      self.Left = max (tempXmin, 0)
      self.Right = min (tempXmax, self.cols_count )
      self.Top = max (tempYmin,0)
      self.Bottom = min (tempYmax,self.rows_count)
      
    # QMessageBox.about(None,' ',str(b.xMinimum())+' '+str(b.yMinimum())+ ' '+ str(b.xMaximum())+ ' '+str(b.yMaximum())  )
    # QMessageBox.about(None,' ',str(tempXmin)+ ' '+str(tempYmin)+' '+str(tempXmax)+ ' '+ str(tempYmax)  )

    self.CLrect.addPoint(QgsPoint(b.xMinimum(), b.yMinimum()),True)
    self.CLrect.addPoint(QgsPoint(b.xMinimum(), b.yMaximum()),True)
    self.CLrect.addPoint(QgsPoint(b.xMaximum(), b.yMaximum()),True)
    self.CLrect.addPoint(QgsPoint(b.xMaximum(), b.yMinimum()),True)

    QMessageBox.about(None,'Dehaze',"Clear pixels selected within:\n" + str(self.Left)+ ' '+str(self.Top)+' '+str(self.Right)+ ' '+ str(self.Bottom) +"\nREady to run calculations..."  )

 
  def runHOT(self):
    # open envi driver
    # limit to envi in the meantime
    if (self.band == None):
      QMessageBox.about(None,'dehaze','load and select image first'  )
      return
    if (self.Top == None):
      QMessageBox.about(None,'dehaze','select Clear sky pixels on image first'  )
      return
    
    
    driver = gdal.GetDriverByName('ENVI')
    driver.Register()
    
    # clear cky line pixels definition based on rectangle extents
    cl = self.lr(self.band[0][self.Top:self.Bottom,self.Left:self.Right].ravel(),self.band[2][self.Top:self.Bottom,self.Left:self.Right].ravel(),self.band[2][self.Top:self.Bottom,self.Left:self.Right].ravel().size)

    # HOT coeff
    sin0 = math.sin(math.atan(cl[0]))
    cosO = math.cos(math.atan(cl[0]))

    # computing for HOT
    # HOT = zeros((rows_count,cols_count)).astype(dtype(float))
    HOT = ((self.band[0]*sin0) - (self.band[2]*cosO)).astype(dtype(integer))
    #HOT = floor(HOT)
    HOTmin = HOT.min()
    #HOT = HOT - HOTmin
    HOTmax = HOT.max()

    # save HOT file
    file2 = QFileDialog.getSaveFileName(None, "Save HOT image file", ".", "ENVI file (*.img)")
    if file2 == '':
      return
    fileInfo2 = QFileInfo(file2)
    fn2 = fileInfo2.filePath()
      
    outDatasetHOT = driver.Create(str(fn2), self.cols_count, self.rows_count, 1, GDT_Byte)
    outBandHOT = outDatasetHOT.GetRasterBand(1)
    outBandHOT.WriteArray(HOT, 0, 0)
    outBandHOT.FlushCache()

    outBandHOT = None
    outDatasetHOT = None

    # adding HOT image to Q
    hotlayer = self.iface.addRasterLayer(str(fn2), "HOT image")

    # getting CL statistic (mean)
    CLmean = zeros((self.band_count)).astype(dtype(float))

    # getting CL statistic (minimum)
    CLmin = zeros((self.band_count)).astype(dtype(integer))

    for k in range(self.band_count):
      cll = self.band[k][self.Top:self.Bottom,self.Left:self.Right].ravel().sort()
      CLmean[k] = average(cll)
      CLmin[k] = 0
      e = 0
      while CLmin[k] == 0:
        CLmin[k] = cll[e]
        e += 1

    # getting HOT statistic (mean)
    HOThist = zeros((self.band_count,HOTmax +1,256)).astype(dtype(integer))
    HOThistcnt = zeros((self.band_count,HOTmax +1)).astype(dtype(integer))
    HOThistsum = zeros((self.band_count,HOTmax +1)).astype(dtype(integer)
    HOThistmin = zeros((self.band_count,HOTmax +1)).astype(dtype(integer))

    pd = QProgressDialog("Operation in progress.", "Cancel", 0, self.band_count*self.rows_count*self.cols_count) #a1
    pd.setWindowModality(Qt.WindowModal)
    yy = 0 #a2
    
    for k in range(self.band_count):
        for i in range(self.rows_count):
            for j in range(self.cols_count):
       
                HOThist[k][HOT[i][j]][self.band[k][i][j]] += 1
                HOThistsum[k][HOT[i][j]] = HOThistsum[k][HOT[i][j]] + self.band[k][i][j]
                HOThistcnt[k][HOT[i][j]] = HOThistcnt[k][HOT[i][j]] + 1
                yy = yy + 1 #a3         
                pd.setValue(yy) #a4
                if (pd.wasCanceled()):
                  self.Top = None
                  self.Bottom = None
                  self.Left = None
                  self.Right = None
                  self.band = None
                  self.cols_count = None
                  self.rows_count = None
                  self.band_count = None
                  self.GT = None
                  self.Gref = None
                  self.CLrect.reset(True)
                  return 1
                  
                
      
    # HOThistmean = zeros((self.band_count,HOTmax +1)).astype(dtype(float))
    HOThistmean = HOThistsum / HOThistcnt

    for k in range(self.band_count):
        for h in range(HOTmax +1):
            w = 0
            e = 0
            while w == 0:
                try:
                    w = HOThist[k][h][e]
                    HOThistmin[k][h]= w
                    e += 1
                except:
                    print HOThist[k][h]
                    exit()
    
    # computing for f(HOT) use linear regression
    HOTREGbeta1 = zeros((self.band_count)).astype(dtype(float))
    HOTREGbeta0 = zeros((self.band_count)).astype(dtype(float))
    
    for k in range(self.band_count):
        tempx = zeros((HOTmax +1)).astype(dtype(float))
        tempy = zeros((HOTmax +1)).astype(dtype(float))
        tempcnt = 0
    
        for q in range(HOTmax +1):
            # HOThistmean[k][q]  =  HOThistsum[k][q]/HOThistcnt[k][q]
            if (HOThistcnt[k][q] > 0):
                #tempy[tempcnt] = HOThistmean[k][q] - CLmean[k]
                tempy[tempcnt] = HOThistmin[k][q] - CLmin[k]
                tempx[tempcnt] = q
                tempcnt = tempcnt + 1
                
        # Linear Regression of correction vs HOT values 
        temp = self.lr(tempx,tempy,tempcnt)
        HOTREGbeta1[k] = temp[0]
        HOTREGbeta0[k] = temp[1]
          
    file3 = QFileDialog.getSaveFileName(None, "Save dehazed image", ".", "Raster file (*.img)")
    fileInfo3 = QFileInfo(file3)
    fn3 = fileInfo3.filePath()

    outDataset = driver.Create(str(fn3), self.cols_count, self.rows_count, self.band_count, GDT_Float32)

    b_out = []
    
    for k in range(self.band_count):
        b_out.append( self.band[k] - ((HOTREGbeta1[k] * HOT) + HOTREGbeta0[k]) * greater(((HOTREGbeta1[k] * HOT) + HOTREGbeta0[k]),0))

    QMessageBox.about(None,str(outDataset),'computations done ' )
      
    for k in range(self.band_count):
        outDataset.GetRasterBand(k +1).WriteArray(b_out[k], 0, 0)
        outDataset.GetRasterBand(k +1).FlushCache()

    outDataset = None

    # add dehazed layer to Q
    dehazedlayer = self.iface.addRasterLayer(str(fn3), "dehazedimage")

    # cleanup
    self.Top = None
    self.Bottom = None
    self.Left = None
    self.Right = None
    self.band = None
    self.cols_count = None
    self.rows_count = None
    self.band_count = None
    self.GT = None
    self.Gref = None
    self.CLrect.reset(True)

  # run method that performs all the real work
  def run(self): 
    # create and show the dialog 
    dlg = DeHazeImageDialog() 
    # show the dialog
    #dlg.show()
    #result = dlg.exec_()
    # See if OK was pressed
    #if result == 1:
      # layout is set - open a layer

      # load active raster layer
    HazedLayer = self.iface.activeLayer()

     # need to add checks
    if (HazedLayer == None):
      QMessageBox.about(None,'DeHaze','Please Load and Select Image')
      return

      # get file name
    fn = HazedLayer.source()
    
    gdal.AllRegister()

    ds = gdal.Open(str(fn), GA_ReadOnly)

      # get image data set information
    self.cols_count = ds.RasterXSize
    self.rows_count = ds.RasterYSize
    self.band_count = ds.RasterCount
    self.GT = ds.GetGeoTransform()
    self.Gref = ds.GetProjectionRef()

    QMessageBox.about(None,'DeHaze', "layer loaded: " + HazedLayer.name() + "\n Please select clear pixels...")

    self.band = []
    for k in range(self.band_count):
      self.band.append(ds.GetRasterBand(k+1).ReadAsArray(0, 0, self.cols_count, self.rows_count) )

    ds = None

    self.CLrect = QgsRubberBand(self.iface.mapCanvas(), True)
    self.CLrect.setColor (QColor(255,0,0))
    self.CLrect.setWidth (3)



    

      
      
      
