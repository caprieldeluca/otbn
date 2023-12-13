# -*- coding: utf-8 -*-
"""
************************************************************************
    Name                : informar_algorithm.py
    Date                : November 2023
    Copyright           : (C) 2023 by Gabriel De Luca
    Email               : caprieldeluca@gmail.com
************************************************************************
  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.
************************************************************************
"""
import math

from qgis import processing

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource)
from qgis.PyQt.QtCore import (
    QCoreApplication)


class Informar(QgsProcessingAlgorithm):
    """Informar algorithm class."""


    def tr(self, string):
        """Return a localized string."""
        return QCoreApplication.translate('Otbn', string)

    def createInstance(self):
        """Return a new instance of the algorithm."""
        return Informar()

    def name(self):
        """Return the algorithm name."""
        return 'informar'

    def displayName(self):
        """Return the algorithm display name."""
        return self.tr('05 - Informar diferencias')

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
            Informar diferencias entre dos capas de poligonos.
            """
        )

    def shortDescription(self):
        """Return the display description of the algorithm."""
        return self.tr('Informar diferencias entre dos capas de poligonos.')

    #####
    # Inicialización de parametros
    #####
    def initAlgorithm(self, config=None):
        """Define inputs and outputs of the algorithm."""
        # OLD
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                'OLD',
                self.tr('Capa anterior'),
                types=[QgsProcessing.TypeVectorPolygon],
                defaultValue=None))

        # NEW
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                'NEW',
                self.tr('Capa nueva'),
                types=[QgsProcessing.TypeVectorPolygon],
                defaultValue=None))


    #####
    # PROCESAMIENTO
    #####
    def processAlgorithm(self, parameters, context, feedback):
        """Informar diferencias entre dos capas de poligonos.
        """

        outputs = {}


        #####
        # Old source
        #####
        old_source = self.parameterAsSource(
            parameters,
            'OLD',
            context)

        # SRC de la capa anterior
        old_crs = old_source.sourceCrs()

        # Reproyeccion si el sistema es geografico
        if old_crs.isGeographic():
            feedback.pushWarning("El sistema de coordenadas de la capa anterior es geográfico.")
            old_extent = old_source.sourceExtent()
            old_center = old_extent.center()
            old_lon = old_center.x()

            # Compute UTM zone and EPSG code
            reproj_zone = math.floor(old_lon / 6) + 31
            reproj_code = 32700 + reproj_zone # 32700 for WGS84 / UTM Zone ... S

            # Reproject the layer
            reproj_crs = QgsCoordinateReferenceSystem.fromEpsgId(reproj_code)
            params = {
                'INPUT': parameters['OLD'],
                'TARGET_CRS': reproj_crs,
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
            }
            msg = "Reproyectando la capa actual a EPSG:" + str(reproj_code) + " ..."
            feedback.pushDebugInfo(msg)
            outputs['REPROJ_OLD'] = processing.run('native:reprojectlayer',
                params,
                context=context,
                feedback=feedback,
                is_child_algorithm=True)
            if feedback.isCanceled():
                return {}

            old_id = outputs['REPROJ_OLD']['OUTPUT']

        else:
            old_id = parameters['OLD']


        #####
        # New source
        #####
        new_source = self.parameterAsSource(
            parameters,
            'NEW',
            context)

        # SRC de la capa actual
        new_crs = new_source.sourceCrs()

        # Reproyeccion si el sistema es geografico
        if new_crs.isGeographic():
            feedback.pushWarning("El sistema de coordenadas de la capa actual es geográfico.")
            new_extent = new_source.sourceExtent()
            new_center = new_extent.center()
            new_lon = new_center.x()

            # Compute UTM zone and EPSG code
            reproj_zone = math.floor(new_lon / 6) + 31
            reproj_code = 32700 + reproj_zone # 32700 for WGS84 / UTM Zone ... S

            # Reproject the layer
            reproj_crs = QgsCoordinateReferenceSystem.fromEpsgId(reproj_code)
            params = {
                'INPUT': parameters['NEW'],
                'TARGET_CRS': reproj_crs,
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
            }
            msg = "Reproyectando la capa actual a EPSG:" + str(reproj_code) + " ..."
            feedback.pushDebugInfo(msg)
            outputs['REPROJ_NEW'] = processing.run('native:reprojectlayer',
                params,
                context=context,
                feedback=feedback,
                is_child_algorithm=True)
            if feedback.isCanceled():
                return {}

            new_id = outputs['REPROJ_NEW']['OUTPUT']

        else:
            new_id = parameters['NEW']


        #####
        # Dissolve old
        #####
        params = {
            'INPUT': old_id,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        feedback.pushDebugInfo("Disolviendo la capa anterior ...")
        outputs['DISSOLVE_OLD'] = processing.run('native:dissolve',
            params,
            context=context,
            feedback=feedback,
            is_child_algorithm=True)
        if feedback.isCanceled():
            return {}


        #####
        # Dissolve new
        #####
        params = {
            'INPUT': new_id,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        feedback.pushDebugInfo("Disolviendo la capa actual ...")
        outputs['DISSOLVE_NEW'] = processing.run('native:dissolve',
            params,
            context=context,
            feedback=feedback,
            is_child_algorithm=True)
        if feedback.isCanceled():
            return {}


        #####
        # Diferencia entre anterior y actual
        #####
        params = {
            'INPUT': outputs['DISSOLVE_OLD']['OUTPUT'],
            'OVERLAY': outputs['DISSOLVE_NEW']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        feedback.pushDebugInfo("Calculando la diferencia entre anterior y actual ...")
        outputs['OLD-NEW'] = processing.run('qgis:difference',
            params,
            context=context,
            feedback=feedback,
            is_child_algorithm=True)
        if feedback.isCanceled():
            return {}


        #####
        # Diferencia entre actual y anterior
        #####
        params = {
            'INPUT': outputs['DISSOLVE_NEW']['OUTPUT'],
            'OVERLAY': outputs['DISSOLVE_OLD']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        feedback.pushDebugInfo("Calculando la diferencia entre actual y anterior ...")
        outputs['NEW-OLD'] = processing.run('qgis:difference',
            params,
            context=context,
            feedback=feedback,
            is_child_algorithm=True)
        if feedback.isCanceled():
            return {}


        #####
        # Crear capas y calcular areas
        #####

        # OLD
        old_lyr = context.getMapLayer(old_id)
        old_area = 0
        # Assume one feature, but iterate anyway
        for f in old_lyr.getFeatures():
            geom = f.geometry()
            old_area += geom.area()

        # NEW
        new_lyr = context.getMapLayer(new_id)
        new_area = 0
        # Assume one feature, but iterate anyway
        for f in new_lyr.getFeatures():
            geom = f.geometry()
            new_area += geom.area()

        # OLD-NEW
        old_new_lyr = context.getMapLayer(outputs['OLD-NEW']['OUTPUT'])
        old_new_area = 0
        # Assume one feature, but iterate anyway
        for f in old_new_lyr.getFeatures():
            geom = f.geometry()
            old_new_area += geom.area()

        # NEW-OLD
        new_old_lyr = context.getMapLayer(outputs['NEW-OLD']['OUTPUT'])
        new_old_area = 0
        # Assume one feature, but iterate anyway
        for f in new_old_lyr.getFeatures():
            geom = f.geometry()
            new_old_area += geom.area()


        #####
        # Imprimir resultados y terminar
        #####

        msg = "Area anterior = " + f'{old_area:.2f}'
        feedback.pushDebugInfo(msg)
        msg = "Area actual = " + f'{new_area:.2f}'
        feedback.pushDebugInfo(msg)
        msg = "Area de la diferencia: anterior menos actual = " + f'{old_new_area:.2f}'
        feedback.pushDebugInfo(msg)
        msg = "Area de la diferencia: actual menos anterior = " + f'{new_old_area:.2f}'
        feedback.pushDebugInfo(msg)

        results = {
            'OLD': round(old_area, 2),
            'NEW': round(new_area, 2),
            'OLD-NEW': round(old_new_area, 2),
            'NEW-OLD': round(new_old_area, 2)
        }


        return results
