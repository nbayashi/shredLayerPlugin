# -*- coding: utf-8 -*-
"""
/***************************************************************************
 shredlayer
                                 A QGIS plugin
 shreds layer plugin
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2020-05-06
        copyright            : (C) 2020 by nishibayashi
        email                : naoya_nstyle@hotmail.co.jp
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load shredlayer class from file shredlayer.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .shred_layer import shredlayer
    return shredlayer(iface)