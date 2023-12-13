# -*- coding: utf-8 -*-
"""
************************************************************************
    Name                : otbn_provider.py
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

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import QgsProcessingProvider

from otbn.processing.algorithms import (
    filtroraster_algorithm,
    poligonizar_algorithm,
    redondear_algorithm,
    desagrupar_algorithm,
    informar_algorithm,
    criterios_algorithm
)


class OtbnProvider(QgsProcessingProvider):
    """Otbn provider class."""

    def tr(self, string):
        """Return a localized string."""
        return QCoreApplication.translate('Otbn', string)

    def loadAlgorithms(self, *args, **kwargs):
        """Load the algorithms of the provider."""
        self.addAlgorithm(filtroraster_algorithm.FiltroRaster())
        self.addAlgorithm(poligonizar_algorithm.Poligonizar())
        self.addAlgorithm(redondear_algorithm.Redondear())
        self.addAlgorithm(desagrupar_algorithm.Desagrupar())
        self.addAlgorithm(informar_algorithm.Informar())
        self.addAlgorithm(criterios_algorithm.Criterios())

    def id(self, *args, **kwargs):
        """Return the id of the provider."""
        return 'otbn'

    def name(self, *args, **kwargs):
        """Return the display name of the provider."""
        return self.tr('OTBN')

    def icon(self):
        """Return the icon of the provider."""
        # TODO: Agregar un icono
        return QgsProcessingProvider.icon(self)
