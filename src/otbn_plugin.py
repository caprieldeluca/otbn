# -*- coding: utf-8 -*-
"""
************************************************************************
    Name                : otbn_plugin.py
    Date                : September 2023
    Copyright           : (C) 2023 by Gabriel De Luca
    Email               : caprieldeluca@gmail.com
************************************************************************
  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.
************************************************************************
"""

import os

from qgis import processing
from qgis.core import QgsApplication, QgsSettings
from qgis.PyQt.QtCore import QCoreApplication, QLocale, QTranslator
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMenu

from otbn.processing.otbn_provider import (
    OtbnProvider
)


class OtbnPlugin:
    """Main plugin class."""

    def __init__(self, iface):
        """Init the plugin."""
        self.plugin_abspath = os.path.dirname(os.path.abspath(__file__))
        locale = QgsSettings().value(
            "locale/userLocale",
            QLocale().name()
        )
        qm_file = os.path.join(
            self.plugin_abspath,
            'i18n',
            f'otbn_{locale}.qm'
        )
        self.translator = QTranslator()
        self.translator.load(qm_file)
        QCoreApplication.installTranslator(self.translator)
        self.iface = iface
        self.provider = None
        self.snaps_action = None
        self.menu = None

    def tr(self, string):
        """Return a localized string."""
        return QCoreApplication.translate('Otbn', string)

    def initProcessing(self):
        """Init processing provider."""
        self.provider = OtbnProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        """Init actions, run methods, menu entries and provider."""
        #####
        # Init actions
        #####

        # Filtro raster
        self.filtroraster_action = QAction(
            self.tr('01 - &Filtro Raster'),
            self.iface.mainWindow()
        )
        self.filtroraster_action.triggered.connect(
            self.run_filtroraster
        )

        # Poligonizar
        self.poligonizar_action = QAction(
            self.tr('02 - &Poligonizar'),
            self.iface.mainWindow()
        )
        self.poligonizar_action.triggered.connect(
            self.run_poligonizar
        )

        # Redondear vertices
        self.redondear_action = QAction(
            self.tr('03 - &Redondear vertices'),
            self.iface.mainWindow()
        )
        self.redondear_action.triggered.connect(
            self.run_redondear
        )

        # Desagrupar clases
        self.desagrupar_action = QAction(
            self.tr('04 - &Desagrupar clases'),
            self.iface.mainWindow()
        )
        self.desagrupar_action.triggered.connect(
            self.run_desagrupar
        )

        # Informar diferencias
        self.informar_action = QAction(
            self.tr('05 - &Informar diferencias'),
            self.iface.mainWindow()
        )
        self.informar_action.triggered.connect(
            self.run_informar
        )

        # Calcular categorias ponderando criterios de sustentabilidad
        self.criterios_action = QAction(
            self.tr('06 - Ponderar &CSA'),
            self.iface.mainWindow()
        )
        self.criterios_action.triggered.connect(
            self.run_criterios
        )

        #####
        # Init menu
        #####
        self.menu = QMenu(self.tr('&OTBN'))
        self.menu.addActions([
            self.filtroraster_action
        ])
        self.menu.addActions([
            self.poligonizar_action
        ])
        self.menu.addActions([
            self.redondear_action
        ])
        self.menu.addActions([
            self.desagrupar_action
        ])
        self.menu.addActions([
            self.informar_action
        ])
        self.menu.addActions([
            self.criterios_action
        ])

        self.iface.pluginMenu().addMenu(self.menu)

        #####
        # Init processing
        #####
        self.initProcessing()

    def unload(self):
        """Remove menu entries and provider."""
        self.iface.removePluginMenu(
            self.tr('&OTBN'),
            self.filtroraster_action
        )
        self.iface.removePluginMenu(
            self.tr('&OTBN'),
            self.poligonizar_action
        )
        self.iface.removePluginMenu(
            self.tr('&OTBN'),
            self.redondear_action
        )
        self.iface.removePluginMenu(
            self.tr('&OTBN'),
            self.desagrupar_action
        )
        self.iface.removePluginMenu(
            self.tr('&OTBN'),
            self.informar_action
        )
        self.iface.removePluginMenu(
            self.tr('&OTBN'),
            self.criterios_action
        )
        QgsApplication.processingRegistry().removeProvider(self.provider)

    def run_filtroraster(self):
        """Open the Filtro Raster algorithm dialog."""
        processing.execAlgorithmDialog('otbn:filtroraster')

    def run_poligonizar(self):
        """Open the Poligonizar algorithm dialog."""
        processing.execAlgorithmDialog('otbn:poligonizar')

    def run_redondear(self):
        """Open the Redondear algorithm dialog."""
        processing.execAlgorithmDialog('otbn:redondear')

    def run_desagrupar(self):
        """Open the Desagrupar algorithm dialog."""
        processing.execAlgorithmDialog('otbn:desagrupar')

    def run_informar(self):
        """Open the Informar algorithm dialog."""
        processing.execAlgorithmDialog('otbn:informar')

    def run_criterios(self):
        """Open the Criterios algorithm dialog."""
        processing.execAlgorithmDialog('otbn:criterios')
