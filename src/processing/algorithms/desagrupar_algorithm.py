# -*- coding: utf-8 -*-
"""
************************************************************************
    Name                : desagrupar_algorithm.py
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

from qgis import processing
from qgis.core import (
    QgsFeatureRequest,
    QgsFeatureSink,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterNumber)
from qgis.PyQt.QtCore import (
    QCoreApplication)

from otbn.processing.algorithms.otbn_utils import remove_spikes


class Desagrupar(QgsProcessingAlgorithm):
    """Desagrupar algorithm class."""


    def tr(self, string):
        """Return a localized string."""
        return QCoreApplication.translate('Otbn', string)

    def createInstance(self):
        """Return a new instance of the algorithm."""
        return Desagrupar()

    def name(self):
        """Return the algorithm name."""
        return 'desagrupar'

    def displayName(self):
        """Return the algorithm display name."""
        return self.tr('04 - Desagrupar clases')

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
            Desagrupar polígonos de clases agrupadas.
            """
        )

    def shortDescription(self):
        """Return the display description of the algorithm."""
        return self.tr('Desagrupar polígonos de clases agrupadas.')

    #####
    # Inicialización de parametros
    #####
    def initAlgorithm(self, config=None):
        """Define inputs and outputs of the algorithm."""
        # AGRUP
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                'AGRUP',
                self.tr('Polígonos de clases agrupadas'),
                types=[QgsProcessing.TypeVectorPolygon],
                defaultValue=None))

        # SUELTAIN
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                'SUELTAIN',
                self.tr('Polígonos de clase suelta'),
                types=[QgsProcessing.TypeVectorPolygon],
                defaultValue=None))

        # HA
        self.addParameter(
            QgsProcessingParameterNumber(
                'HA',
                self.tr('Superficie mínima de polígonos (en hectáreas)'),
            QgsProcessingParameterNumber.Double,
            minValue=0,
            defaultValue=4))

        # SPIKESANGLE
        self.addParameter(
            QgsProcessingParameterNumber(
                'SPIKESANGLE',
                self.tr('Ángulo de vértice mínimo (en grados)'),
            QgsProcessingParameterNumber.Double,
            minValue=0,
            defaultValue=20,
            maxValue=180))

        # DESAGRUP
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                name='DESAGRUP',
                description=self.tr('Clase desagrupada'),
                type=QgsProcessing.TypeVectorPolygon,
                defaultValue=QgsProcessing.TEMPORARY_OUTPUT))

        # SUELTAOUT
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                name='SUELTAOUT',
                description=self.tr('Clase suelta'),
                type=QgsProcessing.TypeVectorPolygon,
                defaultValue=QgsProcessing.TEMPORARY_OUTPUT))


    #####
    # PROCESAMIENTO
    #####
    def processAlgorithm(self, parameters, context, feedback):
        """Desagrupar polígonos de clases agrupadas.
        """

        outputs = {}


        #####
        # Ha from parameter
        #####
        ha = self.parameterAsDouble(
            parameters,
            'HA',
            context)

        #####
        # Spikesangle from parameter
        #####
        spikesangle = self.parameterAsDouble(
            parameters,
            'SPIKESANGLE',
            context)

        #####
        # Diferencia entre agrup y suelta
        #####
        params = {
            'INPUT': parameters['AGRUP'],
            'OVERLAY': parameters['SUELTAIN'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        feedback.pushDebugInfo("Calculando la diferencia entre agrupadas y suelta ...")
        outputs['DESAGRUP'] = processing.run('qgis:difference',
            params,
            context=context,
            feedback=feedback,
            is_child_algorithm=True)
        if feedback.isCanceled():
            return {}


        #####
        # Diferencia entre suelta y agrup
        #####
        params = {
            'INPUT': parameters['SUELTAIN'],
            'OVERLAY': parameters['AGRUP'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        feedback.pushDebugInfo("Calculando la diferencia entre suelta y agrupadas ...")
        outputs['SUELTAPURA'] = processing.run('qgis:difference',
            params,
            context=context,
            feedback=feedback,
            is_child_algorithm=True)
        if feedback.isCanceled():
            return {}


        #####
        # Interseccion
        #####
        params = {
            'INPUT': parameters['SUELTAIN'],
            'OVERLAY': parameters['AGRUP'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        feedback.pushDebugInfo("Calculando interseccion entre capas ...")
        outputs['INTERSEC'] = processing.run('qgis:intersection',
            params,
            context=context,
            feedback=feedback,
            is_child_algorithm=True)
        if feedback.isCanceled():
            return {}


        #####
        # Union entre suelta pura e interseccion
        #####
        params = {
            'INPUT': outputs['SUELTAPURA']['OUTPUT'],
            'OVERLAY': outputs['INTERSEC']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        feedback.pushDebugInfo("Calculando union entre suelta pura e interseccion ...")
        outputs['UNION'] = processing.run('qgis:union',
            params,
            context=context,
            feedback=feedback,
            is_child_algorithm=True)
        if feedback.isCanceled():
            return {}


        #####
        # Desagrup to singlepart
        #####
        params = {
            'INPUT': outputs['DESAGRUP']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        feedback.pushDebugInfo("Promoviendo desagrupada a singlepart ...")
        outputs['DESAGRUPSINGLEPART'] = processing.run('native:multiparttosingleparts',
            params,
            context=context,
            feedback=feedback,
            is_child_algorithm=True)
        if feedback.isCanceled():
            return {}


        #####
        # Suelta to singlepart
        #####
        params = {
            'INPUT': outputs['UNION']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        feedback.pushDebugInfo("Promoviendo suelta a singlepart ...")
        outputs['SUELTASINGLEPART'] = processing.run('native:multiparttosingleparts',
            params,
            context=context,
            feedback=feedback,
            is_child_algorithm=True)
        if feedback.isCanceled():
            return {}


        #####
        # Extraer desagrupadas de mas de 4 hectareas
        #####
        extractdesagrup_params = {
            'INPUT': outputs['DESAGRUPSINGLEPART']['OUTPUT'],
            'EXPRESSION': f'area($geometry) > {ha}*100*100',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        feedback.pushDebugInfo(f"Extrayendo poligonos de clase desagrupada de mas de {ha} hectareas ...")
        outputs['EXTRACTDESAGRUP'] = processing.run('qgis:extractbyexpression',
            extractdesagrup_params,
            context=context,
            feedback=feedback,
            is_child_algorithm=True)
        if feedback.isCanceled():
            return {}


        #####
        # Extraer suelta de mas de 4 hectareas
        #####
        extractsuelta_params = {
            'INPUT': outputs['SUELTASINGLEPART']['OUTPUT'],
            'EXPRESSION': f'area($geometry) > {ha}*100*100',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        feedback.pushDebugInfo(f"Extrayendo poligonos de clase suelta de mas de {ha} hectareas ...")
        outputs['EXTRACTSUELTA'] = processing.run('qgis:extractbyexpression',
            extractsuelta_params,
            context=context,
            feedback=feedback,
            is_child_algorithm=True)
        if feedback.isCanceled():
            return {}


        #####
        # Crear capas de salida
        #####

        # DESAGRUP
        desagrup_lyr = context.getMapLayer(outputs['EXTRACTDESAGRUP']['OUTPUT'])

        desagrup_fields = desagrup_lyr.fields()
        desagrup_wkbtype = desagrup_lyr.wkbType()
        desagrup_crs = desagrup_lyr.crs()

        (desagrup_sink, desagrup_dest_id) = self.parameterAsSink(
            parameters=parameters,
            name='DESAGRUP',
            context=context,
            fields=desagrup_fields,
            geometryType=desagrup_wkbtype,
            crs=desagrup_crs)

        feat_request = QgsFeatureRequest()
        f_count = desagrup_lyr.featureCount()
        limite = 100000
        if f_count > limite:
            feedback.pushWarning("Se alcanzó el límite de objetos de salida.")
            feedback.pushDebugInfo(f"Se iban a escribir {f_count} objetos, limitando a {limite}...")
            feat_request.setLimit(limite)
        feedback.pushDebugInfo("Creando capa de salida: Clase desagrupada ...")
        m = 0
        for f in desagrup_lyr.getFeatures(feat_request):
            if feedback.isCanceled():
                break
            geom = f.geometry()
            geom_without_spikes, n = remove_spikes.run(geom, spikesangle)
            m += n
            f.setGeometry(geom_without_spikes)
            desagrup_sink.addFeature(f, QgsFeatureSink.FastInsert)

        feedback.pushDebugInfo(f"Se eliminaron {m} vértices con ángulo menor a {spikesangle} grados.")

        if feedback.isCanceled():
            return {}


        # SUELTAOUT
        sueltaout_lyr = context.getMapLayer(outputs['EXTRACTSUELTA']['OUTPUT'])

        sueltaout_fields = sueltaout_lyr.fields()
        sueltaout_wkbtype = sueltaout_lyr.wkbType()
        sueltaout_crs = sueltaout_lyr.crs()

        (sueltaout_sink, sueltaout_dest_id) = self.parameterAsSink(
            parameters=parameters,
            name='SUELTAOUT',
            context=context,
            fields=sueltaout_fields,
            geometryType=sueltaout_wkbtype,
            crs=sueltaout_crs)

        feat_request = QgsFeatureRequest()
        f_count = sueltaout_lyr.featureCount()
        limite = 100000
        if f_count > limite:
            feedback.pushWarning("Se alcanzó el límite de objetos de salida.")
            feedback.pushDebugInfo(f"Se iban a escribir {f_count} objetos, limitando a {limite}...")
            feat_request.setLimit(limite)
        feedback.pushDebugInfo("Creando capa de salida: Clase suelta ...")
        m = 0
        for f in sueltaout_lyr.getFeatures(feat_request):
            if feedback.isCanceled():
                break
            geom = f.geometry()
            geom_without_spikes, n = remove_spikes.run(geom, spikesangle)
            m += n
            f.setGeometry(geom_without_spikes)
            sueltaout_sink.addFeature(f, QgsFeatureSink.FastInsert)

        feedback.pushDebugInfo(f"Se eliminaron {m} vértices con ángulo menor a {spikesangle} grados.")


        # Devolver el identificador del sink como salida
        return {'DESAGRUP': desagrup_dest_id, 'SUELTAOUT': sueltaout_dest_id}
