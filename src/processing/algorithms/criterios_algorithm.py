# -*- coding: utf-8 -*-
"""
************************************************************************
    Name                : criterios_algorithm.py
    Date                : December 2023
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
    QgsProcessingParameterNumber,
    QgsProcessingParameterString)
from qgis.PyQt.QtCore import (
    QCoreApplication)


class Criterios(QgsProcessingAlgorithm):
    """Criterios algorithm class."""


    def tr(self, string):
        """Return a localized string."""
        return QCoreApplication.translate('Otbn', string)

    def createInstance(self):
        """Return a new instance of the algorithm."""
        return Criterios()

    def name(self):
        """Return the algorithm name."""
        return 'criterios'

    def displayName(self):
        """Return the algorithm display name."""
        return self.tr('06 - Ponderar CSA')

    def group(self):
        """Return the name of the group this algorithm belongs to."""
        return ''

    def groupId(self):
        """Return the unique ID of the group this algorithm belongs to."""
        return ''

    def shortHelpString(self):
        """Return the display help of the algortihm."""
        return self.tr('Calcular categorias de conservación ponderando CSA.')

    def shortDescription(self):
        """Return the display description of the algorithm."""
        return self.tr('Calcular categorias de conservación en base a la ponderación de los criterios de sustentabilidad.')

    #####
    # Inicialización de parametros
    #####
    def initAlgorithm(self, config=None):
        """Define inputs and outputs of the algorithm."""

        # INPUT
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                'INPUT',
                'Capa de entrada',
                types=[QgsProcessing.TypeVectorPolygon],
                defaultValue=None))

        # UMBRAL1
        self.addParameter(
            QgsProcessingParameterNumber(
                'UMBRAL1',
                'Categoría I para valores mayores que:',
                QgsProcessingParameterNumber.Double,
                minValue=0,
                maxValue=100,
                defaultValue=16))

        # UMBRAL2
        self.addParameter(
            QgsProcessingParameterNumber(
                'UMBRAL2',
                'Categoría III para valores menores o iguales que:',
                QgsProcessingParameterNumber.Double,
                minValue=0,
                maxValue=100,
                defaultValue=8))

        # CATEGORIA
        self.addParameter(
            QgsProcessingParameterString(
                'CATEGORIA',
                'Nombre de la columna a llenar con la categoría',
                defaultValue='Categoría'))

        # COEF01
        self.addParameter(
            QgsProcessingParameterNumber(
                'COEF01',
                'Peso del valor CSA01',
                QgsProcessingParameterNumber.Double,
                defaultValue=1))

        # COEF02
        self.addParameter(
            QgsProcessingParameterNumber(
                'COEF02',
                'Peso del valor CSA02',
                QgsProcessingParameterNumber.Double,
                defaultValue=1))

        # COEF03
        self.addParameter(
            QgsProcessingParameterNumber(
                'COEF03',
                'Peso del valor CSA03',
                QgsProcessingParameterNumber.Double,
                defaultValue=1))

        # COEF04
        self.addParameter(
            QgsProcessingParameterNumber(
                'COEF04',
                'Peso del valor CSA04',
                QgsProcessingParameterNumber.Double,
                defaultValue=1))

        # COEF05
        self.addParameter(
            QgsProcessingParameterNumber(
                'COEF05',
                'Peso del valor CSA05',
                QgsProcessingParameterNumber.Double,
                defaultValue=1))

        # COEF06
        self.addParameter(
            QgsProcessingParameterNumber(
                'COEF06',
                'Peso del valor CSA06',
                QgsProcessingParameterNumber.Double,
                defaultValue=1))

        # COEF07
        self.addParameter(
            QgsProcessingParameterNumber(
                'COEF07',
                'Peso del valor CSA07',
                QgsProcessingParameterNumber.Double,
                defaultValue=1))

        # COEF08
        self.addParameter(
            QgsProcessingParameterNumber(
                'COEF08',
                'Peso del valor CSA08',
                QgsProcessingParameterNumber.Double,
                defaultValue=-1))

        # COEF09
        self.addParameter(
            QgsProcessingParameterNumber(
                'COEF09',
                'Peso del valor CSA09',
                QgsProcessingParameterNumber.Double,
                defaultValue=1))

        # COEF10
        self.addParameter(
            QgsProcessingParameterNumber(
                'COEF10',
                'Peso del valor CSA10',
                QgsProcessingParameterNumber.Double,
                defaultValue=1))

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                name='OUTPUT',
                description='Categorias',
                type=QgsProcessing.TypeVectorPolygon,
                defaultValue=QgsProcessing.TEMPORARY_OUTPUT))


    #####
    # PROCESAMIENTO
    #####
    def processAlgorithm(self, parameters, context, feedback):
        """Calcular categorias de conservación en base a la aplicación de los criterios de sustentabilidad.
        """

        outputs = {}


        #####
        # Umbrales para las categorias I, II y III
        #####

        umbral1 = self.parameterAsDouble(
            parameters,
            'UMBRAL1',
            context)

        umbral2 = self.parameterAsDouble(
            parameters,
            'UMBRAL2',
            context)


        #####
        # Nombre de la columna "categoria"
        #####

        categoria = self.parameterAsString(
            parameters,
            'CATEGORIA',
            context)


        #####
        # Campos de CSA
        #####
        CSA01_name = 'CSA01'

        CSA02_name = 'CSA02'

        CSA03_name = 'CSA03'

        CSA04_name = 'CSA04'

        CSA05_name = 'CSA05'

        CSA06_name = 'CSA06'

        CSA07_name = 'CSA07'

        CSA08_name = 'CSA08'

        CSA09_name = 'CSA09'

        CSA10_name = 'CSA10'


        #####
        # Pesos de cada CSA
        #####

        coef01 = self.parameterAsDouble(
            parameters,
            'COEF01',
            context)

        coef02 = self.parameterAsDouble(
            parameters,
            'COEF02',
            context)

        coef03 = self.parameterAsDouble(
            parameters,
            'COEF03',
            context)

        coef04 = self.parameterAsDouble(
            parameters,
            'COEF04',
            context)

        coef05 = self.parameterAsDouble(
            parameters,
            'COEF05',
            context)

        coef06 = self.parameterAsDouble(
            parameters,
            'COEF06',
            context)

        coef07 = self.parameterAsDouble(
            parameters,
            'COEF07',
            context)

        coef08 = self.parameterAsDouble(
            parameters,
            'COEF08',
            context)

        coef09 = self.parameterAsDouble(
            parameters,
            'COEF09',
            context)

        coef10 = self.parameterAsDouble(
            parameters,
            'COEF10',
            context)


        #####
        # Verificaciones iniciales
        #####
        input_source = self.parameterAsSource(
            parameters,
            'INPUT',
            context)
        input_fields = input_source.fields()

        # Verifica que existen los campos CSAxx
        lista_de_verif = ['CSA01', 'CSA02', 'CSA03', 'CSA04',
                        'CSA05', 'CSA06', 'CSA07', 'CSA08', 'CSA09', 'CSA10']
        for verif in lista_de_verif:
            if input_fields.indexOf(verif) == -1:
                msg = f'No se encontró el campo "{verif}".'
                feedback.pushWarning(msg)
                return {}


        #####
        # Calcular el campo "categoria"
        #####
        form = f'if("{CSA01_name}" = 4 OR "{CSA02_name}" = 4 OR '
        form += f'"{CSA03_name}" = 4 OR "{CSA04_name}" = 4 OR '
        form += f'"{CSA05_name}" = 4 OR "{CSA06_name}" = 4 OR '
        form += f'"{CSA07_name}" = 4 OR "{CSA08_name}" = 4 OR '
        form += f'"{CSA09_name}" = 4 OR "{CSA10_name}" = 4, \'I\', '
        form += "with_variable('sumapond', "
        form += f'"{CSA01_name}" * {coef01} + "{CSA02_name}" * {coef02} + '
        form += f'"{CSA03_name}" * {coef03} + "{CSA04_name}" * {coef04} + '
        form += f'"{CSA05_name}" * {coef05} + "{CSA06_name}" * {coef06} + '
        form += f'"{CSA07_name}" * {coef07} + "{CSA08_name}" * {coef08} + '
        form += f'"{CSA09_name}" * {coef09} + "{CSA10_name}" * {coef10}, '
        form += f"if(@sumapond > {umbral1}, 'I', "
        form += f"if(@sumapond > {umbral2} , 'II', "
        form += f"if(@sumapond <= {umbral2}, 'III', NULL)))))"

        params = {
            'INPUT':parameters['INPUT'],
            'FIELD_NAME':categoria,
            'FIELD_TYPE':2, # String
            'FIELD_LENGTH':10,
            'FIELD_PRECISION':0,
            'FORMULA':form,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}


        feedback.pushDebugInfo(f'Calculando el campo "{categoria}"...')
        outputs['CATEGORIA'] = processing.run('native:fieldcalculator',
            params,
            context=context,
            feedback=feedback,
            is_child_algorithm=True)
        if feedback.isCanceled():
            return {}


        #####
        # CAPA DE SALIDA
        #####

        # Obtener la capa de salida de INTERSECA a partir de su id
        #  dentro del context
        vlyr = context.getMapLayer(outputs['CATEGORIA']['OUTPUT'])
        fields = vlyr.fields()
        wkbtype = vlyr.wkbType()
        crs = vlyr.crs()

        # Crear el sink a partir del parametro de salida
        (sink, dest_id) = self.parameterAsSink(
            parameters=parameters,
            name='OUTPUT',
            context=context,
            fields=fields,
            geometryType=wkbtype,
            crs=crs)

        # Transferir los objetos de la vector layer al sink
        feat_request = QgsFeatureRequest()

        f_count = vlyr.featureCount()
        limite = 100000
        if f_count > limite:
            feedback.pushWarning("Se alcanzó el límite de objetos de salida.")
            feedback.pushDebugInfo(f"Se iban a escribir {f_count} objetos, limitando a {limite}...")
            feat_request.setLimit(limite)

        feedback.pushDebugInfo("Creando capa de salida ...")
        for f in vlyr.getFeatures(feat_request):
            if feedback.isCanceled():
                break
            sink.addFeature(f, QgsFeatureSink.FastInsert)

        # Devolver el identificador del sink como salida
        return {'OUTPUT': dest_id}

