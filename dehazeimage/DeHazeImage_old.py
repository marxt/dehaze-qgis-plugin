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
import time

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


    # Create a toolbar
    self.toolbar = self.iface.addToolBar("HOT")
      
    # Add the actions to the toolbar
    self.toolbar.addAction(self.action)

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
  
  def ExtChanged(self):
      a = self.lineEditMaxX.text()
      b = self.lineEditMaxY.text()
      c = self.lineEditMinX.text()
      d = self.lineEditMinY.text()

      if a != "" and b != "" and c != "" and d != "":

          try:
              xMax = float(a)
              yMax = float(b)
              xMin = float(c)
              yMin = float(d)

              self.CLrect.reset(True)
              self.CLrect.addPoint(QgsPoint(xMin, yMin),True)
              self.CLrect.addPoint(QgsPoint(xMin, yMax),True)
              self.CLrect.addPoint(QgsPoint(xMax, yMax),True)
              self.CLrect.addPoint(QgsPoint(xMax, yMin),True)
              self.CLrect.addPoint(QgsPoint(xMin, yMin),True)

          except:
              QMessageBox.about(None,'dehaze','Please enter numerical values')
              return

  def setExt(self):
      try:
          xMax = float(self.lineEditMaxX.text())
          yMax = float(self.lineEditMaxY.text())
          xMin = float(self.lineEditMinX.text())
          yMin = float(self.lineEditMinY.text())
      except:
          return 1


      if (self.Gref == ''):
          # not georeferenced
          self.Left = max (xMin, 0)
          self.Right = min (xMax, self.cols_count )
          self.Bottom = min ((yMin*-1),self.rows_count)
          self.Top = max ((yMax*-1),0)
      else:
          # georeferenced
          tempXmin = (xMin - self.GT[0]) / self.GT[1]
          tempXmax = (xMax - self.GT[0]) / self.GT[1]
          tempYmax = (yMin - self.GT[3]) / self.GT[5]
          tempYmin = (yMax - self.GT[3]) / self.GT[5]
          self.Left = max (tempXmin, 0)
          self.Right = min (tempXmax, self.cols_count )
          self.Top = max (tempYmin,0)
          self.Bottom = min (tempYmax,self.rows_count)
      return 0

  def MarkCL(self,b):
    # after selecting CL pixels get extent of region
    # check if image is selected

     # check if georeferenced
    self.lineEditMaxX.setText(str(b.xMaximum()))
    self.lineEditMaxY.setText(str(b.yMaximum()))
    self.lineEditMinX.setText(str(b.xMinimum()))
    self.lineEditMinY.setText(str(b.yMinimum()))

    self.CLrect.reset(True)
    self.CLrect.addPoint(QgsPoint(b.xMinimum(), b.yMinimum()),True)
    self.CLrect.addPoint(QgsPoint(b.xMinimum(), b.yMaximum()),True)
    self.CLrect.addPoint(QgsPoint(b.xMaximum(), b.yMaximum()),True)
    self.CLrect.addPoint(QgsPoint(b.xMaximum(), b.yMinimum()),True)
    self.CLrect.addPoint(QgsPoint(b.xMinimum(), b.yMinimum()),True)

  def runHOT(self):
      tt = time.time()
      tFile = open(str(int(tt)),"w")
      print tt
      timeStamp = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime())
      print timeStamp
      tFile.write(timeStamp + "\n")
      tFile.write("maxX\t" + self.lineEditMaxX.text() + "\n")
      tFile.write("maxY\t" + self.lineEditMaxY.text() + "\n")
      tFile.write("minX\t" + self.lineEditMinX.text() + "\n")
      tFile.write("minY\t" + self.lineEditMinY.text() + "\n")
      # open envi driver
      # limit to envi in the meantime

      driver = gdal.GetDriverByName('ENVI')
      driver.Register()
    
      # clear cky line pixels definition based on rectangle extents
      blueCL = self.band[self.blueBand][self.Top:self.Bottom,self.Left:self.Right].ravel()
      redCL = self.band[self.redBand][self.Top:self.Bottom,self.Left:self.Right].ravel()
      print blueCL
      print redCL
      sizeCL = redCL.size
      cl = self.lr(blueCL,redCL,sizeCL)

      # HOT coeff
      sin0 = math.sin(math.atan(cl[0]))
      cosO = math.cos(math.atan(cl[0]))
      tFile.write("sinO:\t"+str(sin0)+ "\n")
      tFile.write("cosO:\t"+str(cosO)+ "\n")

      # computing for HOT
      #HOT = zeros((rows_count,cols_count)).astype(dtype(integer)
      print "mask after greater", self.mask
      HOT = ((self.band[self.blueBand]*sin0) - (self.band[self.redBand]*cosO)).astype(dtype(integer))

      """
      if self.checkBoxMask.isChecked():
          HOT = ((self.band[self.blueBand]*sin0*self.scaleFactor*self.mask) - (self.band[self.redBand]*cosO*self.scaleFactor*self.mask)).astype(dtype(integer))
      else:
          HOT = ((self.band[self.blueBand]*sin0*self.scaleFactor) - (self.band[self.redBand]*cosO*self.scaleFactor)).astype(dtype(integer))

      if mean(HOT) < 1:
          HOT = ((10000*self.band[self.blueBand]*sin0) - (10000*self.band[self.redBand]*cosO)).astype(dtype(integer))
          HOT = HOT * greater(HOT,0)
      """


      clMeanHOT = int(mean(HOT[self.Top:self.Bottom,self.Left:self.Right]))
      clMaxHOT = amax(HOT[self.Top:self.Bottom,self.Left:self.Right])
      print "max CL Hot", clMaxHOT
      print "mean CL Hot", clMeanHOT
      tFile.write("CL Mean HOT:\t"+str(clMeanHOT)+ "\n")
      tFile.write("CL Max HOT:\t"+str(clMaxHOT)+ "\n")

      #
      #normalization/translation
      if self.checkBoxMask.isChecked():
          HOTmin = amin(extract(self.mask,HOT[:]))
          HOT = HOT * self.mask
      else:
          HOTmin = amin(HOT)
      print HOTmin
      if HOTmin < 0:
          HOT = greater(HOT, 0) * HOT
      else:
          HOT = HOT - HOTmin
      HOTmax = int(amax(HOT))
      print HOTmin
      #
      tFile.write("HOT min:\t"+str(HOTmin)+ "\n")
      #print HOT
      #HOT = self.histeq(HOT,HOTmax)[0]

      #QMessageBox.about(None,"test",str(HOTmax) + "\n" + str(sin0))

      # save HOT file
      file2 = QFileDialog.getSaveFileName(None, "Save HOT image file", ".", "ENVI file (*.img)")
      if file2 == '':
          return
      fileInfo2 = QFileInfo(file2)
      fn2 = fileInfo2.filePath()
      
      outDatasetHOT = driver.Create(str(fn2), self.cols_count, self.rows_count, 1, GDT_Int16)
      outDatasetHOT.SetGeoTransform(self.GT)
      outDatasetHOT.SetProjection(self.Gref)
      outBandHOT = outDatasetHOT.GetRasterBand(1)
      outBandHOT.WriteArray(HOT*self.mask, 0, 0)
      outBandHOT.FlushCache()


      outBandHOT = None
      outDatasetHOT = None

      # adding HOT image to Q
      hotlayer = self.iface.addRasterLayer(str(fn2), "HOT image")



      #getting CL statistic (mean)
      CLstat = zeros((self.band_count)).astype(dtype(integer))

      for k in range(self.band_count):
          cll = self.band[k][self.Top:self.Bottom,self.Left:self.Right]
          #print cll
          if self.statMatch == "percentile":
              CLstat[k] = percentile(cll,self.Percentile)
              tFile.write("%s %f Band %d: %d\n" % (self.statMatch, self.Percentile, k+1, CLstat[k]))
          elif self.statMatch == "mean":
              CLstat[k] = mean(cll)
              tFile.write("%s Band %d: %d" % (self.statMatch, k+1, CLstat[k]))
          else:
              CLstat[k] = percentile(cll,self.Percentile)
              tFile.write("%s %f Band %d: %d\n" % (self.statMatch, self.Percentile, k+1, CLstat[k]))

      """
      # getting HOT statistic (mean)
      HOThist = zeros((self.band_count,HOTmax +1,self.maxVal)).astype(integer)
      HOThistcnt = zeros((self.band_count,HOTmax +1)).astype(dtype(integer))
      HOThistsum = zeros((self.band_count,HOTmax +1)).astype(dtype(integer))

      pd = QProgressDialog("Operation in progress.", "Cancel", 0, self.band_count*self.rows_count*self.cols_count) #a1
      pd.setWindowModality(Qt.WindowModal)
      yy = 0 #a2
    
      for k in range(self.band_count):
        for i in range(self.rows_count):
            for j in range(self.cols_count):

                HOThist[k][HOT[i][j]][self.band[k][i][j]] += 1
                HOThistsum[k][HOT[i][j]] += self.band[k][i][j]
                HOThistcnt[k][HOT[i][j]] += 1
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

      HOThistmean = HOThistsum / HOThistcnt
      """
      HOTstat = zeros((self.band_count,HOTmax +1)).astype(dtype(integer))
      HOTvalues = unique(HOT[:]*self.mask)
      startHOTval = int(percentile(HOTvalues,2))
      stopHOTval= int(percentile(HOTvalues,98))

      #HOTvalues = HOTvalues[int(HOTvalues.size*self.exclude) : int(HOTvalues.size*(100 - self.exclude)) + 1]

      print "HOT values:"
      #for i in HOTvalues:
      #  print i

      # computing for f(HOT) use linear regression
      HOTREGbeta1 = zeros((self.band_count)).astype(dtype(float))
      HOTREGbeta0 = zeros((self.band_count)).astype(dtype(float))
      p = []

      pd = QProgressDialog("Operation in progress.", "Cancel", 0, self.band_count*HOTvalues.size) #a1
      pd.setWindowModality(Qt.WindowModal)
      yy = 0 #a2


      for k in range(self.band_count):
          #lr
          tempx = zeros((HOTmax +1)).astype(dtype(float))
          tempy = zeros((HOTmax +1)).astype(dtype(float))
          tempcnt = 0

          print "band" + str(k)
          for q in HOTvalues:
              if q == 0:
                  continue
              if self.checkBoxMask.isChecked():
                  m = equal(HOT * self.mask,q)
              else:
                  m = equal(HOT,q)
              e = extract(m,self.band[k][:])
              print e

              if self.statMatch == "percentile":
                  HOTstat[k,q] = percentile(e,self.Percentile)
              elif self.statMatch == "mean":
                  HOTstat[k,q] = mean(e)
              else:
                  HOTstat[k,q] = percentile(e,self.Percentile)


              lineP = "Band" + str(k) +"\t"+str(q) + "\t" + str(HOTstat[k,q]) + "\t" + str(CLstat[k]) + "\n"
              print lineP
              tFile.write(lineP)
                  #lr
              tempy[tempcnt] = HOTstat[k,q] - CLstat[k]
              tempx[tempcnt] = q
              tempcnt += 1

              m = None
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
                  tFile.close()
                  return 1

          # Linear Regression of correction vs HOT values
          z = polyfit(tempx[:tempcnt+1], tempy[:tempcnt+1], self.PolyDeg)
          p.append(z)
          #temp = self.lr(tempx[:tempcnt+1],tempy[:tempcnt+1],tempcnt)
          HOTREGbeta1[k] = 0 #temp[0]
          HOTREGbeta0[k] = 0# temp[1]

          
      file3 = QFileDialog.getSaveFileName(None, "Save dehazed image", ".", "Raster file (*.img)")
      fileInfo3 = QFileInfo(file3)
      fn3 = fileInfo3.filePath()

      outDataset = driver.Create(str(fn3), self.cols_count, self.rows_count, self.band_count, GDT_Float32)
      outDataset.SetGeoTransform(self.GT)
      outDataset.SetProjection(self.Gref)

      tFile.write(str(p))
      tFile.close()
      QMessageBox.about(None,"f(HOT)","m:" + str( HOTREGbeta1) + "\nb:" + str(HOTREGbeta0) + "\n" + str(p))

      #HOT = HOT - clMeanHOT
      #HOT = greater(HOT,0) * HOT
      for k in range(self.band_count):

          pp = poly1d(p[k])
          val = pp(HOT)
          #val = ((HOTREGbeta1[k] * HOT ) + HOTREGbeta0[k])
          val = greater(val,0.0) * val
          val = (self.band[k] - val) / self.scaleFactor #* mask
          if self.checkBoxMask.isChecked():
              val = self.mask * val
          outDataset.GetRasterBand(k +1).WriteArray(val, 0, 0)
          outDataset.GetRasterBand(k +1).FlushCache()

      QMessageBox.about(None,"dehaze",'computations done ' )

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

  def prepDlg(self):
      self.dlg = DeHazeImageDialog()
      self.dlg.setWindowFlags(Qt.WindowStaysOnTopHint)
      self.layerComboBox = self.dlg.findChild(QComboBox, "layerComboBox")
      self.comboBoxMask = self.dlg.findChild(QComboBox, "comboBoxMask")
      self.blueComboBox = self.dlg.findChild(QComboBox, "blueComboBox")
      self.redComboBox = self.dlg.findChild(QComboBox, "redComboBox")
      self.lineEditMaxX = self.dlg.findChild(QLineEdit, "lineEditMaxX")
      self.lineEditMaxY = self.dlg.findChild(QLineEdit, "lineEditMaxY")
      self.lineEditMinX = self.dlg.findChild(QLineEdit, "lineEditMinX")
      self.lineEditMinY = self.dlg.findChild(QLineEdit, "lineEditMinY")
      self.spinBoxPolyDeg = self.dlg.findChild(QSpinBox, "spinBoxPolyDeg")
      self.spinBoxScaling = self.dlg.findChild(QSpinBox, "spinBoxScaling")
      self.doubleSpinPerc = self.dlg.findChild(QDoubleSpinBox, "doubleSpinPerc")
      self.radioButtonMean = self.dlg.findChild(QRadioButton,"radioButtonMean")
      self.radioButtonPercentile = self.dlg.findChild(QRadioButton,"radioButtonPercentile")
      self.checkBoxMask = self.dlg.findChild(QCheckBox,"checkBoxMask")

      QObject.connect(self.layerComboBox, SIGNAL("currentIndexChanged(const QString&)"), self.rasterLayerChanged)
      QObject.connect(self.comboBoxMask, SIGNAL("currentIndexChanged(const QString&)"), self.maskLayerChanged)
      QObject.connect(self.lineEditMaxX, SIGNAL("textChanged(const QString&)"), self.ExtChanged)
      QObject.connect(self.lineEditMaxY, SIGNAL("textChanged(const QString&)"), self.ExtChanged)
      QObject.connect(self.lineEditMinX, SIGNAL("textChanged(const QString&)"), self.ExtChanged)
      QObject.connect(self.lineEditMinY, SIGNAL("textChanged(const QString&)"), self.ExtChanged)

      mc = self.iface.mapCanvas()

      layers = []
      for layer in mc.layers():
          if layer.type() == QgsMapLayer.RasterLayer:
              layers += [ layer.name() ]
      self.layerComboBox.clear()
      self.layerComboBox.insertItems(len(layers), layers)
      self.comboBoxMask.insertItems(len(layers), layers)

  def maskLayerChanged(self, layername):
      self.mask = QgsMapLayerRegistry.instance().mapLayersByName(layername)[0]

  def rasterLayerChanged(self, layername):
    self.hl = QgsMapLayerRegistry.instance().mapLayersByName(layername)[0]
    bc = self.hl.bandCount()
    if bc < 2:
        QMessageBox.about(None,'DeHaze','Select Image an image with a blue and red band')

    l = []
    for n in range(bc):
        l += ["band %d" % (n + 1)]
    self.blueComboBox.clear()
    self.redComboBox.clear()
    self.blueComboBox.insertItems(len(l),l)
    self.redComboBox.insertItems(len(l),l)

    if bc >= 3:
        self.blueComboBox.setCurrentIndex(0)
        self.redComboBox.setCurrentIndex(2)

      #QMessageBox.about(None,str(x),'Testing signals')

  def run(self):
      #run prep for dialog entries
      self.prepDlg()

      #enable the selection tool
      self.iface.mapCanvas().setMapTool(self.toolMarkCL)

      # initializing rubberband
      self.CLrect = QgsRubberBand(self.iface.mapCanvas(), True)
      self.CLrect.setColor (QColor(255,0,0))
      self.CLrect.setWidth (3)

      # show the dialog
      self.dlg.show()
      result = self.dlg.exec_()
      self.iface.mapCanvas().setMapTool(None)

      # See if OK was pressed
      if result == 0:
          self.iface.actionPan().trigger()
          self.CLrect.reset(True)
          return

      try:
          self.hl
      except:
          QMessageBox.about(None,'DeHaze','Please Load and Select Image')
          return

      # get file name
      fn = self.hl.source()

      # opening raster files
      gdal.AllRegister()
      ds = gdal.Open(str(fn), GA_ReadOnly)

      # get mask file name
      fnMask = self.mask.source()

      # opening raster files
      gdal.AllRegister()
      self.mask = gdal.Open(str(fnMask), GA_ReadOnly)


      # get image data set information
      self.cols_count = ds.RasterXSize
      self.rows_count = ds.RasterYSize
      self.band_count = ds.RasterCount
      self.GT = ds.GetGeoTransform()
      self.Gref = ds.GetProjectionRef()
      self.blueBand = self.blueComboBox.currentIndex()
      self.redBand = self.redComboBox.currentIndex()
      self.scaleFactor = self.spinBoxScaling.value()

      self.PolyDeg = self.spinBoxPolyDeg.value()
      self.Percentile = self.doubleSpinPerc.value()
      self.exclude = 0.0

      if self.radioButtonPercentile.isChecked():
          self.statMatch = "percentile"
      elif self.radioButtonMean.isChecked():
          self.statMatch = "mean"
      else:
          self.statMatch = "percentile"

      self.mask = self.mask.GetRasterBand(1).ReadAsArray()
      self.mask = greater(self.mask,0)

      print self.mask

      self.maxVal = 0.00
      self.band = []
      for k in range(self.band_count):
          if self.checkBoxMask.isChecked():
              curBand = (ds.GetRasterBand(k+1).ReadAsArray(0, 0, self.cols_count, self.rows_count)*self.mask*self.scaleFactor).astype(dtype(float))
          else:
              curBand = (ds.GetRasterBand(k+1).ReadAsArray(0, 0, self.cols_count, self.rows_count)*self.scaleFactor).astype(dtype(float))
          print curBand
          self.maxVal = max(amax(curBand),self.maxVal)
          self.band.append( curBand )

      self.maxVal = int(math.ceil(self.maxVal))
      ds = None


      if self.setExt():
          QMessageBox.about(None,'dehaze','Please Delineate Clear Sky pixels\nTerminating...')
          self.iface.actionPan().trigger()
          return

      QMessageBox.about(None,'DeHaze', "Layer loaded: " + self.hl.name() + "\nClear Sky pixels selected.\nRed Band: "+str(self.redBand + 1) + "\nBlue Band: " + str(self.blueBand + 1)+" \n")
      self.iface.actionPan().trigger()
      self.runHOT()



