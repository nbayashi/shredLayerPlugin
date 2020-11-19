# -*- coding: utf-8 -*-
"""
/***************************************************************************
 shredlayerDialog
                                 A QGIS plugin
 shreds layer plugin
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2020-05-06
        git sha              : $Format:%H$
        copyright            : (C) 2020 by nishibayashi
        email                : naoya_nstyle@hotmail.co.jp
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

import os
import glob
import qgis

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.core import *
from qgis.gui import *
from qgis.utils import iface

from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QSlider


import processing

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'shred_layer_dialog_base.ui'))


class shredlayerDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(shredlayerDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        #setting slider
        self.horizontalSlider.setMinimum(1)
        self.horizontalSlider.setMaximum(10)
        self.horizontalSlider.setSingleStep(1)
        self.horizontalSlider.setPageStep(1)

        self.radioButton.setChecked(True)

        # 実行ボタン
        self.button_box.accepted.connect(self.run_shred)
        self.button_box.rejected.connect(self.dlg_close)


    def dlg_close(self):
        self.close()



    def run_shred(self):

        layer = self.layer_ComboBox.currentLayer()
        shrednum = self.horizontalSlider.value()*10





        (Dir,filename) = os.path.split(layer.dataProvider().dataSourceUri())
        os.chdir(Dir)



        #getExtent
        box = layer.extent()
        xmin = box.xMinimum()
        xmax = box.xMaximum()
        ymin = box.yMinimum()
        ymax = box.yMaximum()

        exta = str(xmin) + ',' + str(xmax) + ',' + str(ymin) + ',' +str(ymax)


        #VectorGrid
        if self.radioButton.isChecked() == True:
            shredGrid = processing.runAndLoadResults("qgis:creategrid",{'TYPE':2,'EXTENT':exta,'HSPACING':box.width()/shrednum,'VSPACING':box.height(),'HOVERLAY':0,'VOVERLAY':0,'CRS':layer.crs().authid(),'OUTPUT':'memory:'})
        elif self.radioButton_2.isChecked() == True:
            shredGrid = processing.runAndLoadResults("qgis:creategrid",{'TYPE':2,'EXTENT':exta,'HSPACING':box.width(),'VSPACING':box.height()/shrednum,'HOVERLAY':0,'VOVERLAY':0,'CRS':layer.crs().authid(),'OUTPUT':'memory:'})


        shredlayer =  QgsProject.instance().mapLayersByName("グリッドベクタの出力")[0]




        if layer.type() == 0:
            #Vector
            for i in range(1,shrednum+1,1):
                shredlayer.selectByExpression('"id" =' + str(i),QgsVectorLayer.SetSelection)
                
                
                processing.runAndLoadResults("native:clip", {"INPUT": layer, "OVERLAY":QgsProcessingFeatureSourceDefinition(shredGrid['OUTPUT'],True) , "OUTPUT": Dir + '/shred_'+layer.name() + "_" +  str(i) + '.shp'})
        else:
            #Raster
            for i in range(1,shrednum+1,1):
                shredlayer.selectByExpression('"id" =' + str(i),QgsVectorLayer.SetSelection)
                
                
                rasClip =processing.runAndLoadResults("gdal:cliprasterbymasklayer", {"INPUT": layer, "MASK":QgsProcessingFeatureSourceDefinition(shredGrid['OUTPUT'],True) ,"NODATA":None,"ALPHA_BAND":False, "CROP_TO_CUTLINE":True,"KEEP_RESOLUTION":True, "OPTIONS":'',"DATA_TYPE":0,"OUTPUT":Dir + '/shred_'+ layer.name() + "_" + str(i) + '.tif'})
       
        #remove layer
        QgsProject.instance().removeMapLayer(layer)
        QgsProject.instance().removeMapLayer(shredlayer)

        layer = None
        iface.mapCanvas().refresh()


        #shp一式選択
        files = glob.glob(filename.split('shp')[0]+'*')


        #Delete
        for i in files:
            os.remove(i)

        self.close()


        

