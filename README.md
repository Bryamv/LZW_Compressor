# Compresor y Descompresor de archivos

Este proyecto consiste en un compresor y descompresor secuencial de archivos de texto, así como un verificador para garantizar la integridad del archivo descomprimido. 

## Funcionamiento

El compresor, llamado "compresor.py", recibe como parámetro un archivo de texto y lo comprime en un archivo llamado "comprimido.elmejorprofesor". El tiempo en segundos que toma este proceso es mostrado por pantalla.

El descompresor, llamado "descompresor.py", busca en la carpeta el archivo "comprimido.elmejorprofesor" y lo descomprime en un archivo llamado "descomprimido-elmejorprofesor.txt". El tiempo en segundos que toma este proceso también es mostrado por pantalla.

El verificador, llamado "verificador.py", recibe como parámetro un archivo de texto y lo compara con el archivo descomprimido. Si son idénticos, retorna "ok". De lo contrario, retorna "nok".

## Instrucciones de uso

1. Descarga o clona este repositorio en tu computadora.

2. Abre la terminal y dirígete al directorio donde se encuentra el proyecto.

3. Para comprimir un archivo, ejecuta el siguiente comando en la terminal:

```
python compresor.py nombre_del_archivo.txt
```

4. Para descomprimir el archivo comprimido, ejecuta el siguiente comando:

```
python descompresor.py
```

5. Para verificar la integridad del archivo descomprimido, ejecuta el siguiente comando:

```
python verificador.py nombre_del_archivo.txt
```

## Requisitos

- Python 3.x
- Sistema operativo compatible con Python 3.x