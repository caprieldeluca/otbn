# -*- coding: utf-8 -*-
"""
************************************************************************
    Name                : poligonizar_algorithm.py
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

from qgis.core import (
    Qgis,
    QgsFeatureRequest,
    QgsFeatureSink,
    QgsField,
    QgsFields,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterField,
    QgsProcessingParameterNumber,
    QgsProcessingParameterRasterLayer,
    QgsWkbTypes
)
from qgis.PyQt.QtCore import (
    QCoreApplication,
    QVariant
)
import processing


class Poligonizar(QgsProcessingAlgorithm):
    """Poligonizar algorithm class."""


    def tr(self, string):
        """Return a localized string."""
        return QCoreApplication.translate('Otbn', string)

    def createInstance(self):
        """Return a new instance of the algorithm."""
        return Poligonizar()

    def name(self):
        """Return the algorithm name."""
        return 'poligonizar'

    def displayName(self):
        """Return the algorithm display name."""
        return self.tr('02 - Poligonizar')

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
            Poligonizar raster y aplicar filtros vectoriales.
            """
        )

    def shortDescription(self):
        """Return the display description of the algorithm."""
        return self.tr('Poligonizar raster y aplicar filtros vectoriales.')

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
                self.tr('Raster a poligonizar'),
                defaultValue=None))

        # HOLESHA
        self.addParameter(
            QgsProcessingParameterNumber(
                'HOLESHA',
                self.tr('Superficie máxima de holes a preservar (en hectáreas)'),
            QgsProcessingParameterNumber.Double,
            minValue=0,
            defaultValue=14))

        # POLIGHA
        self.addParameter(
            QgsProcessingParameterNumber(
                'POLIGHA',
                self.tr('Superficie mínima de polígonos a preservar (en hectáreas)'),
            QgsProcessingParameterNumber.Double,
            minValue=0,
            defaultValue=4))

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                name='OUTPUT',
                description=self.tr('Poligonizados'),
                type=QgsProcessing.TypeVectorPolygon,
                createByDefault=True,
                supportsAppend=True,
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


        #####
        # HolesHa source
        #####
        holesha = self.parameterAsDouble(
            parameters,
            'HOLESHA',
            context)


        #####
        # PoligHa source
        #####
        poligha = self.parameterAsDouble(
            parameters,
            'POLIGHA',
            context)


        #####
        # Poligonizar raster
        #####
        alg_params = {
            'BAND': 1,
            'EIGHT_CONNECTEDNESS': False,
            'EXTRA': '',
            'FIELD': 'class',
            'INPUT': parameters['INPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        feedback.pushDebugInfo("Vectorizando capa raster ...")
        outputs['POLYGONIZE'] = processing.run('gdal:polygonize',
            alg_params,
            context=context,
            feedback=feedback,
            is_child_algorithm=True)

        if feedback.isCanceled():
            return {}


        #####
        # Pormover poligonos a singlepart
        #####
        alg_params = {
            'INPUT': outputs['POLYGONIZE']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        feedback.pushDebugInfo("Convirtiendo multipartes a singlepart ...")
        outputs['MULTI2SINGLE1'] = processing.run('native:multiparttosingleparts',
            alg_params,
            context=context,
            feedback=feedback,
            is_child_algorithm=True)

        if feedback.isCanceled():
            return {}


        #####
        # Unir holes de menos de HolesHa hectareas
        #####
        # Definir la consulta
        query = """WITH nombres AS
        (
            SELECT
                class AS class,
                ST_Area(geometry)/(100*100) AS ha,
                geometry
            FROM
                input1
        ),
        holes AS (
            SELECT
                geometry
            FROM
                nombres
            WHERE """
        query += f'((class = 0) AND (ha <= {holesha})) OR (class = 1)'
        query += """)
        SELECT
            1 AS class,
            GUnion(geometry) AS geometry
        FROM
            holes;
            """
        # Execute SQL
        alg_params = {
            'INPUT_DATASOURCES': outputs['MULTI2SINGLE1']['OUTPUT'],
            'INPUT_GEOMETRY_CRS': input_raster.crs(),
            'INPUT_GEOMETRY_FIELD': 'geometry',
            'INPUT_GEOMETRY_TYPE': 4, # Poligono
            'INPUT_QUERY': query,
            'INPUT_UID_FIELD': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        feedback.pushDebugInfo(f"Uniendo holes de hasta {holesha} hectareas ...")
        outputs['SQL1'] = processing.run('qgis:executesql',
            alg_params,
            context=context,
            feedback=feedback,
            is_child_algorithm=True)
        if feedback.isCanceled():
            return {}


        #####
        # Promover la union a singlepart
        #####
        alg_params = {
            'INPUT': outputs['SQL1']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        feedback.pushDebugInfo("Convirtiendo la unión a singlepart ...")
        outputs['MULTI2SINGLE2'] = processing.run('native:multiparttosingleparts',
            alg_params,
            context=context,
            feedback=feedback,
            is_child_algorithm=True)
        if feedback.isCanceled():
            return {}


        #####
        # Simplificar geometrias y extraer mayores que PoligHa
        #####
        query = """WITH nombres AS
        (
            SELECT
                class AS class,
                geometry
            FROM
                input1
        ),
        simplificados AS (
            SELECT
                class,
                ST_Simplify(geometry, 10) AS geometry
            FROM
                nombres
        ),
        areas AS (
            SELECT
                class,
                ST_Area(geometry)/(100*100) AS ha,
                geometry
            FROM
                simplificados
        ),
        filtrados AS (
            SELECT *
            FROM areas """
        query += f'WHERE ha >= {poligha}'
        query += """)
        SELECT
            ROW_NUMBER() OVER() AS pol_id,
            class,
            ha,
            geometry
        FROM
            filtrados;
            """
        # Execute SQL
        alg_params = {
            'INPUT_DATASOURCES': outputs['MULTI2SINGLE2']['OUTPUT'],
            'INPUT_GEOMETRY_CRS': input_raster.crs(),
            'INPUT_GEOMETRY_FIELD': 'geometry',
            'INPUT_GEOMETRY_TYPE': 4, # Poligono
            'INPUT_QUERY': query,
            'INPUT_UID_FIELD': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        feedback.pushDebugInfo(f"Simplificando geometrías y extrayendo polígonos de al menos {poligha} hectáreas ...")
        outputs['SQL2'] = processing.run('qgis:executesql',
            alg_params,
            context=context,
            feedback=feedback,
            is_child_algorithm=True)
        if feedback.isCanceled():
            return {}


        # Obtener la capa de salida de SQL2 a partir de su id
        #  dentro del context
        vlyr = context.getMapLayer(outputs['SQL2']['OUTPUT'])

        # Campos para la salida
        fields = QgsFields()
        fields.append(QgsField('pol_id', QVariant.Int))
        fields.append(QgsField('class', QVariant.Int))
        fields.append(QgsField('ha', QVariant.Double))

        # Definir el geometryType dependiendo la versión de QGIS:
        if Qgis.QGIS_VERSION_INT < 33000:
            geometryType = QgsWkbTypes.Polygon
        else:
            geometryType = Qgis.WkbType.Polygon

        # Crear el sink a partir del parametro de salida
        (sink, dest_id) = self.parameterAsSink(
            parameters=parameters,
            name='OUTPUT',
            context=context,
            fields=fields,
            geometryType=geometryType,
            crs=input_raster.crs())

        # Transferir los objetos de la vector layer al sink
        feat_request = QgsFeatureRequest()

        if vlyr.featureCount() > 100000:
            feat_request.setLimit(100000)

        feedback.pushDebugInfo("Creando capa de salida ...")
        for f in vlyr.getFeatures(feat_request):
            if feedback.isCanceled():
                break
            sink.addFeature(f, QgsFeatureSink.FastInsert)

        # Devolver el identificador del sink como salida
        return {'OUTPUT': dest_id}
