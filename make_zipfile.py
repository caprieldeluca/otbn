#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crear el archivo zip para instalar el plugin en QGIS.

Este script se puede correr cada vez que se realice un nuevo lanzamiento del plugin.
El archivo zip creado tendrá el nombre: otbn_v<x>_<y>_<z>.zip,
Donde <x>.<y>.<z> es el número de versión del plugin, el cual se extrae del
archivo metadata.txt ubicado en el directorio ./src
Dentro del archivo zip se escribe un directorio ./otbn con el código fuente del
plugin y el archvivo ./LICENSE.
"""

import configparser
import pathlib
import shutil

def make():
    """Crear el archivo zip para instalar en QGIS."""
    
    # Definir paths
    this_path = pathlib.Path().resolve()
    src_path = this_path / 'src'
    zipfiles_path = this_path / 'zipfiles'
    otbn_path = zipfiles_path / 'otbn'

    # Eliminar, si existe, el directorio ./releases/otbn    
    if otbn_path.exists():
        print(f"El directorio '{str(otbn_path)}' existe.")
        shutil.rmtree(otbn_path)
        print(f"Directorio '{str(otbn_path)}' eliminado")
    
    # Copiar el contenido del directorio ./src a ./zipfiles/otbn   
    shutil.copytree(src=src_path,
                    dst=otbn_path,
                    ignore=shutil.ignore_patterns('__pycache__'))
    print(f"Copiado el contenido de '{str(src_path)}' a '{str(zipfiles_path)}'")
    
    # Copiar ./LICENSE a ./releases/otbn/LICENSE
    shutil.copyfile(src=this_path / 'LICENSE',
                    dst=otbn_path / 'LICENSE')
    print("Copiado el archivo LICENSE")
    
    # Obtener el nombre del archivo zip a partir de la versión
    metadata = configparser.ConfigParser()
    metadata.read(src_path / 'metadata.txt')
    version = metadata['general']['version']
    x_y_z = '_'.join(version.split('.'))
    
    zip_name = f'otbn_v{x_y_z}'
    
    # Escribir archivo zip    
    shutil.make_archive(base_name=zipfiles_path / zip_name,
                        format='zip',
                        root_dir=zipfiles_path,
                        base_dir='otbn')
    print("Creado el archivo de instalación en:",
          f"'{str(zipfiles_path / zip_name)}.zip'")
    
    
    shutil.rmtree(otbn_path)
    print(f"Directorio '{str(otbn_path)}' eliminado")
    
if __name__ == "__main__":
    make()