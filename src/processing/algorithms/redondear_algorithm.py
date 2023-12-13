# -*- coding: utf-8 -*-
"""
************************************************************************
    Name                : redondear_algorithm.py
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

from qgis import processing

from qgis.core import (
    Qgis,
    QgsFeatureRequest,
    QgsFeatureSink,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterNumber,
    QgsWkbTypes
)
from qgis.PyQt.QtCore import (
    QCoreApplication)


class Redondear(QgsProcessingAlgorithm):
    """Redondear algorithm class."""


    def tr(self, string):
        """Return a localized string."""
        return QCoreApplication.translate('Otbn', string)

    def createInstance(self):
        """Return a new instance of the algorithm."""
        return Redondear()

    def name(self):
        """Return the algorithm name."""
        return 'redondear'

    def displayName(self):
        """Return the algorithm display name."""
        return self.tr('03 - Redondear vertices')

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
            Redondear los vertices de los poligonos.
            """
        )

    def shortDescription(self):
        """Return the display description of the algorithm."""
        return self.tr('Redondear los vertices de los poligonos.')

    #####
    # Inicialización de parametros
    #####
    def initAlgorithm(self, config=None):
        """Define inputs and outputs of the algorithm."""
        advanced_flag = QgsProcessingParameterDefinition.FlagAdvanced
        # INPUT
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                'INPUT',
                self.tr('Capa de entrada'),
                types=[QgsProcessing.TypeVectorPolygon],
                defaultValue=None))

        # REXT
        self.addParameter(
            QgsProcessingParameterNumber(
                'REXT',
                self.tr('Radio para vertices externos'),
            QgsProcessingParameterNumber.Double,
            minValue=0,
            defaultValue=5))

        # RINT
        self.addParameter(
            QgsProcessingParameterNumber(
                'RINT',
                self.tr('Radio para vertices internos'),
            QgsProcessingParameterNumber.Double,
            minValue=0,
            defaultValue=10))

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                name='OUTPUT',
                description=self.tr('Redondeada'),
                type=QgsProcessing.TypeVectorPolygon,
                defaultValue=QgsProcessing.TEMPORARY_OUTPUT))


    #####
    # PROCESAMIENTO
    #####
    def processAlgorithm(self, parameters, context, feedback):
        """Redondear los vertices de los poligonos.
        """

        outputs = {}


        #####
        # Input source
        #####
        input_source = self.parameterAsSource(
            parameters,
            'INPUT',
            context)

        # Verificar si el sistema de referencia es geográfico
        input_crs = input_source.sourceCrs()
        if input_crs.isGeographic():
            feedback.pushWarning("El sistema de coordenadas de la capa de entrada es geográfico.")
        input_fields = input_source.fields()


        #####
        # Rext parameter
        #####
        rext = self.parameterAsDouble(
            parameters,
            'REXT',
            context)


        #####
        # Rint parameter
        #####
        rint = self.parameterAsDouble(
            parameters,
            'RINT',
            context)


        #####
        # Dissolve
        #####
        params = {
            'INPUT': parameters['INPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        feedback.pushDebugInfo("Disolviendo todos los objetos antes de redondear ...")
        outputs['DISSOLVE'] = processing.run('native:dissolve',
            params,
            context=context,
            feedback=feedback,
            is_child_algorithm=True)
        if feedback.isCanceled():
            return {}


        #####
        # Buffer 1
        #####
        params = {
            'INPUT': outputs['DISSOLVE']['OUTPUT'],
            'DISTANCE': rint,
            'DISSOLVE': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        feedback.pushDebugInfo("Haciendo el buffer hacia afuera ...")
        outputs['BUFFER1'] = processing.run('native:buffer',
            params,
            context=context,
            feedback=feedback,
            is_child_algorithm=True)
        if feedback.isCanceled():
            return {}


        #####
        # Buffer 2
        #####
        params = {
            'INPUT': outputs['BUFFER1']['OUTPUT'],
            'DISTANCE': -rint - rext,
            'DISSOLVE': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        feedback.pushDebugInfo("Haciendo el buffer hacia adentro ...")
        outputs['BUFFER2'] = processing.run('native:buffer',
            params,
            context=context,
            feedback=feedback,
            is_child_algorithm=True)
        if feedback.isCanceled():
            return {}


        #####
        # Buffer 3
        #####
        params = {
            'INPUT': outputs['BUFFER2']['OUTPUT'],
            'DISTANCE': rext,
            'DISSOLVE': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        feedback.pushDebugInfo("Haciendo el último buffer hacia afuera ...")
        outputs['BUFFER3'] = processing.run('native:buffer',
            params,
            context=context,
            feedback=feedback,
            is_child_algorithm=True)
        if feedback.isCanceled():
            return {}


        #####
        # Singlepart
        #####
        params = {
            'INPUT': outputs['BUFFER3']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        feedback.pushDebugInfo("Promoviendo poligonos a monoparte ...")
        outputs['SINGLEPART'] = processing.run('native:multiparttosingleparts',
            params,
            context=context,
            feedback=feedback,
            is_child_algorithm=True)
        if feedback.isCanceled():
            return {}

        #####
        # Crear capa de salida
        #####

        # Definir el geometryType dependiendo la versión de QGIS:
        if Qgis.QGIS_VERSION_INT < 33000:
            geometryType = QgsWkbTypes.Polygon
        else:
            geometryType = Qgis.WkbType.Polygon

        # OUTPUT
        output_lyr = context.getMapLayer(outputs['SINGLEPART']['OUTPUT'])
        (output_sink, output_dest_id) = self.parameterAsSink(
            parameters=parameters,
            name='OUTPUT',
            context=context,
            fields=input_fields,
            geometryType=geometryType,
            crs=input_crs)

        feat_request = QgsFeatureRequest()

        if output_lyr.featureCount() > 500000:
            feat_request.setLimit(500000)
        feedback.pushDebugInfo("Creando capa de salida ...")
        for f in output_lyr.getFeatures(feat_request):
            if feedback.isCanceled():
                break
            output_sink.addFeature(f, QgsFeatureSink.FastInsert)


        # Devolver el identificador del sink como salida
        return {'OUTPUT': output_dest_id}
