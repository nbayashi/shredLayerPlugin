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
        copyright            : (C) 2020 by nbayashi
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
import random
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

        # setting slider
        self.horizontalSlider.setMinimum(2)
        self.horizontalSlider.setMaximum(10)
        self.horizontalSlider.setSingleStep(1)
        self.horizontalSlider.setPageStep(1)

        self.radioButton_vertical.setChecked(True)
        self.layer_ComboBox.layerChanged.connect(
            self.checkable)

        # button setting
        self.button_box.accepted.connect(self.run_shred)
        self.button_box.rejected.connect(self.dlg_close)

    def dlg_close(self):
        self.close()

    def checkable(self):
        if self.layer_ComboBox.currentLayer().type() == 0:
            self.groupBox_option.setEnabled(True)
            self.groupBox_option.setCheckable(True)
            self.groupBox_option.setChecked(False)
        else:
            self.groupBox_option.setEnabled(False)

    def run_shred(self):

        input_layer = self.layer_ComboBox.currentLayer()
        shrednum = self.horizontalSlider.value()

        (Dir, filename) = os.path.split(
            input_layer.dataProvider().dataSourceUri())
        os.chdir(Dir)

        # getExtent
        box = input_layer.extent()
        xmin = box.xMinimum()
        xmax = box.xMaximum()
        ymin = box.yMinimum()
        ymax = box.yMaximum()

        exta = str(xmin) + ',' + str(xmax) + ',' + str(ymin) + ',' + str(ymax)

        # VectorGrid
        if self.radioButton_vertical.isChecked() == True:
            shredgrid = processing.run("qgis:creategrid", {'TYPE': 2, 'EXTENT': exta, 'HSPACING': box.width(
            )/(shrednum*10), 'VSPACING': box.height(), 'HOVERLAY': 0, 'VOVERLAY': 0, 'CRS': input_layer.crs().authid(), 'OUTPUT': 'memory:'})['OUTPUT']
        elif self.radioButton_horizonal.isChecked() == True:
            shredgrid = processing.run("qgis:creategrid", {'TYPE': 2, 'EXTENT': exta, 'HSPACING': box.width(
            ), 'VSPACING': box.height()/(shrednum*10), 'HOVERLAY': 0, 'VOVERLAY': 0, 'CRS': input_layer.crs().authid(), 'OUTPUT': 'memory:'})['OUTPUT']
        else:
            shredgrid = processing.run("qgis:creategrid", {'TYPE': 2, 'EXTENT': exta, 'HSPACING': box.width(
            )/shrednum, 'VSPACING': box.height()/shrednum, 'HOVERLAY': 0, 'VOVERLAY': 0, 'CRS': input_layer.crs().authid(), 'OUTPUT': 'memory:'})['OUTPUT']

        # run clip
        extent_list = []
        clipped_list = []
        if input_layer.type() == 0:
            # shredgrid を順に指定
            for feat in shredgrid.getFeatures():
                featId = feat.id()
                selection = shredgrid.selectByExpression(
                    '$id=' + str(featId))
                selectedlyr = shredgrid.materialize(
                    QgsFeatureRequest().setFilterFids(shredgrid.selectedFeatureIds()))
                # get bbox
                extent_list.append(selectedlyr.extent())
                clipped_output = processing.run("native:clip", {
                                                "INPUT": input_layer, "OVERLAY": selectedlyr, "OUTPUT": Dir + "/shred_"+input_layer.name() + "_" + str(featId) + '.shp'})['OUTPUT']
                clipped = QgsVectorLayer(
                    clipped_output, input_layer.name() + "_" + str(featId), 'ogr')
                QgsProject.instance().addMapLayer(clipped)
                clipped_list.append(clipped)
        else:
            for feat in shredgrid.getFeatures():
                featId = feat.id()
                selection = shredgrid.selectByExpression(
                    '$id=' + str(featId))
                selectedlyr = shredgrid.materialize(
                    QgsFeatureRequest().setFilterFids(shredgrid.selectedFeatureIds()))
                # get bbox
                extent_list.append(selectedlyr.extent())

                rasClip = processing.run("gdal:cliprasterbymasklayer", {'INPUT': input_layer, 'MASK': selectedlyr, 'SOURCE_CRS': None, 'TARGET_CRS': None, 'NODATA': None, 'ALPHA_BAND': False, 'CROP_TO_CUTLINE': True,
                                                                        'KEEP_RESOLUTION': False, 'SET_RESOLUTION': False, 'X_RESOLUTION': None, 'Y_RESOLUTION': None, 'MULTITHREADING': False, 'OPTIONS': '', 'DATA_TYPE': 0, 'EXTRA': '', 'OUTPUT':  Dir + "/shred_" + input_layer.name() + "_" + str(featId) + '.tif'})['OUTPUT']
                clipped = QgsRasterLayer(
                    rasClip, input_layer.name() + "_" + str(featId), input_layer.dataProvider().name())
                QgsProject.instance().addMapLayer(clipped)

        # shuffle
        if self.groupBox_option.isEnabled() == True and self.groupBox_option.isChecked() == True and (self.radioButton_shuffle.isChecked() == True or self.radioButton__collage.isChecked() == True):
            random_list = random.sample(extent_list, len(extent_list))
            diff_xlist = [rl.xMaximum() - l.xMaximum()
                          for (rl, l) in zip(random_list, extent_list)]
            diff_ylist = [rl.yMaximum() - l.yMaximum()
                          for (rl, l) in zip(random_list, extent_list)]
            # collage
            if self.radioButton__collage.isChecked() == True:
                dx = extent_list[0].xMaximum() - extent_list[0].xMinimum()
                dy = extent_list[0].yMaximum() - extent_list[0].yMinimum()
                for i in range(len(extent_list)):
                    diff_xlist[i] = diff_xlist[i] + \
                        dx * random.uniform(-1.0, 1.0)
                    diff_ylist[i] = diff_ylist[i] + \
                        dy * random.uniform(-1.0, 1.0)

            # change geometry
            for i in range(len(clipped_list)):
                for clipped_feature in clipped_list[i].getFeatures():
                    geom = clipped_feature.geometry()
                    geom.translate(diff_xlist[i], diff_ylist[i])
                    clipped_list[i].dataProvider().changeGeometryValues(
                        {clipped_feature.id(): geom})
                    iface.mapCanvas().refreshAllLayers()
                    iface.mapCanvas().refresh()
                    clipped_list[i].triggerRepaint()

        # remove layer
        QgsProject.instance().removeMapLayer(input_layer)

        # refresh
        input_layer = None
        iface.mapCanvas().refresh()
        iface.mapCanvas().refreshAllLayers()
        
        # shp一式選択
        files = glob.glob(filename.split('shp')[0]+'*')

        # Delete
        for i in files:
            try:
                os.remove(i)
            except PermissionError:
                    pass
        self.close()
