# -*- coding: utf-8 -*-
"""
************************************************************************
    Name                : filtroraster_algorithm.py
    Date                : October 2023
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

from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterNumber,
    QgsProcessingParameterRasterDestination,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterString,
    QgsRasterFileWriter
)
from qgis.PyQt.QtCore import (
    QCoreApplication
)
import processing

from osgeo import gdal
import numpy as np
from scipy import signal


class FiltroRaster(QgsProcessingAlgorithm):
    """FiltroRaster algorithm class."""


    def tr(self, string):
        """Return a localized string."""
        return QCoreApplication.translate('Otbn', string)

    def createInstance(self):
        """Return a new instance of the algorithm."""
        return FiltroRaster()

    def name(self):
        """Return the algorithm name."""
        return 'filtroraster'

    def displayName(self):
        """Return the algorithm display name."""
        return self.tr('01 - Filtro Raster')

    def group(self):
        """Return the name of the group this algorithm belongs to."""
        return ''

    def groupId(self):
        """Return the unique ID of the group this algorithm belongs to."""
        return ''

    def shortHelpString(self):
        """Return the display help of the algortihm."""
        return self.tr(
            """
            Filtrar raster de clasificación para extraer clase(s) a poligonizar.
            """
        )

    def shortDescription(self):
        """Return the display description of the algorithm."""
        return self.tr('Filtrar raster de clasificación para extraer clase(s) a poligonizar.')

    #####
    # Inicialización de parametros
    #####
    def initAlgorithm(self, config=None):
        """Define inputs and outputs of the algorithm."""
        advanced_flag = QgsProcessingParameterDefinition.FlagAdvanced

        # INPUT
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                'INPUT',
                self.tr('Raster de clasificación'),
                defaultValue=None))

        # CLASES
        self.addParameter(
            QgsProcessingParameterString(
                'CLASES',
                self.tr('Clase(s) a extraer (separadas por coma)'),
                defaultValue=None))

        # M2P
        self.addParameter(
            QgsProcessingParameterNumber(
                'M2P',
                self.tr('Porcentaje de cobertura para Radio 2'),
            QgsProcessingParameterNumber.Integer,
            minValue=0,
            maxValue=100,
            defaultValue=50))

        # M3P
        self.addParameter(
            QgsProcessingParameterNumber(
                'M3P',
                self.tr('Porcentaje de cobertura para Radio 3'),
            QgsProcessingParameterNumber.Integer,
            minValue=0,
            maxValue=100,
            defaultValue=50))

        # M4P
        self.addParameter(
            QgsProcessingParameterNumber(
                'M4P',
                self.tr('Porcentaje de cobertura para Radio 4'),
            QgsProcessingParameterNumber.Integer,
            minValue=0,
            maxValue=100,
            defaultValue=50))

        # M5P
        self.addParameter(
            QgsProcessingParameterNumber(
                'M5P',
                self.tr('Porcentaje de cobertura para Radio 5'),
            QgsProcessingParameterNumber.Integer,
            minValue=0,
            maxValue=100,
            defaultValue=50))

        # M11BOOL
        self.addParameter(
            QgsProcessingParameterBoolean(
                'M11BOOL',
                self.tr('Suavizado final'),
            defaultValue=True))

        # MADYBOOL
        self.addParameter(
            QgsProcessingParameterBoolean(
                'MADYBOOL',
                self.tr('Absorber pixeles adyacentes'),
            defaultValue=True))

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                name='OUTPUT',
                description=self.tr('Filtrado'),
                defaultValue=QgsProcessing.TEMPORARY_OUTPUT))


    #####
    # PROCESAMIENTO
    #####
    def processAlgorithm(self, parameters, context, feedback):
        """Poligonizar raster y aplicar filtros vectoriales.
        """

        outputs = {}


        #####
        # InputRaster source
        #####
        input_raster = self.parameterAsRasterLayer(
            parameters,
            'INPUT',
            context)

        dataset = gdal.Open(input_raster.source())
        geotransform = dataset.GetGeoTransform()
        projection = dataset.GetProjection()
        band_n = 1
        band = dataset.GetRasterBand(band_n)
        R = np.array(band.ReadAsArray())


        #####
        # Clases source
        #####
        clases_str = self.parameterAsString(
            parameters,
            'CLASES',
            context)
        clases = [int(clase) for clase in clases_str.split(',')]


        #####
        # M2P
        #####
        m2p = self.parameterAsInt(
            parameters,
            'M2P',
            context)


        #####
        # M3P
        #####
        m3p = self.parameterAsInt(
            parameters,
            'M3P',
            context)


        #####
        # M4P
        #####
        m4p = self.parameterAsInt(
            parameters,
            'M4P',
            context)


        #####
        # M5P
        #####
        m5p = self.parameterAsInt(
            parameters,
            'M5P',
            context)


        #####
        # M11BOOL
        #####
        m11bool = self.parameterAsBool(
            parameters,
            'M11BOOL',
            context)


        #####
        # MADYBOOL
        #####
        madybool = self.parameterAsBool(
            parameters,
            'MADYBOOL',
            context)


        #####
        # Make Circle
        #####
        def make_circle(r):
            C = np.zeros([2*r+1,2*r+1],dtype=np.byte)
            for i in range(r):
                for j in range(r):
                    if np.sqrt((i+1)*(i+1)+(j+1)*(j+1))<=r+0.4:
                        C[r-i-1,r-j-1]=1
                        C[r-i-1,r+j+1]=1
                        C[r+i+1,r-j-1]=1
                        C[r+i+1,r+j+1]=1
            for i in range(r):
                C[r,r-i-1]=1
                C[r,r+i+1]=1
                C[r+i+1,r]=1
                C[r-i-1,r]=1
            C[r,r]=1
            return C

        C1 = make_circle(1)
        C2 = make_circle(2)
        C3 = make_circle(3)
        C4 = make_circle(4)
        C5 = make_circle(5)


        #####
        # Enmascarar clases
        #####
        feedback.pushDebugInfo(f"Extrayendo clase(s)...")
        M1 = np.logical_or.reduce([R == x for x in clases])
        if feedback.isCanceled():
            return {}


        #####
        # Filtrados
        #####
        feedback.pushDebugInfo(f"Filtrado de radio 2...")
        M2x=signal.convolve(M1, C2, mode='same')
        M2=M2x>(C2.sum()*m2p/100)
        if feedback.isCanceled():
            return {}

        feedback.pushDebugInfo(f"Filtrado de radio 3...")
        M3x=signal.convolve(M1, C3, mode='same')
        M3=M3x>(C3.sum()*m3p/100)
        if feedback.isCanceled():
            return {}

        feedback.pushDebugInfo(f"Filtrado de radio 4...")
        M4x=signal.convolve(M1, C4, mode='same')
        M4=M4x>(C4.sum()*m4p/100)
        if feedback.isCanceled():
            return {}

        feedback.pushDebugInfo(f"Filtrado de radio 5...")
        M5x=signal.convolve(M1, C5, mode='same')
        M5=M5x>(C5.sum()*m5p/100)
        M6 = M2 + 2*M3 + 4*M4 + 8*M5
        M7=M6>0
        if feedback.isCanceled():
            return {}

        M8=(signal.convolve(M7, C1, mode='same')>0)&M1
        M9=M7|M8
        M10=signal.convolve(M9, C3, mode='same')
        if feedback.isCanceled():
            return {}

        if m11bool:
            feedback.pushDebugInfo(f"Filtrado final...")
            M11=signal.convolve(M10>0, C3, mode='same')==C3.sum()
        else:
            M11=M9
        if feedback.isCanceled():
            return {}

        if madybool:
            feedback.pushDebugInfo(f"Absorbiendo pixeles adyacentes...")
            MAdy=(signal.convolve(M11, C1, mode='same')>0)&M1
            M11=M11|MAdy
        if feedback.isCanceled():
            return {}

        #####
        # OUTPUT
        #####
        output_file = self.parameterAsOutputLayer(parameters, 'OUTPUT', context)

        # Driver name for the output_file extension
        output_format = QgsRasterFileWriter.driverForExtension(
            os.path.splitext(output_file)[-1])

        driver = gdal.GetDriverByName(output_format)

        feedback.pushDebugInfo(f"Escribiendo raster de salida...")
        dst_ds = driver.Create(output_file,
                       band.XSize,
                       band.YSize,
                       band_n,
                       band.DataType)
        dst_ds.GetRasterBand(band_n).WriteArray(M11)
        dst_ds.SetGeoTransform(geotransform)
        dst_ds.SetProjection(projection)

        # Flush and cleanup
        dst_ds = None
        dataset = None
        if feedback.isCanceled():
            return {}

        return {'OUTPUT': output_file}
