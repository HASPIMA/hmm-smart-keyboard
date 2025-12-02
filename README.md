# HMM Smart Keyboard

>[!NOTE] 
>¿Que es HMM Smart Keyboard?
>
>HMM Smart Keyboard es una herramienta que permite corregir errores en textos mediante la utilización de un modelo de Markov Hidden Markov.

## Contenido
- [Marco Teórico](#Marco-Teorico)
- [Descripción y justificación del problema](#Descripción-y-justificación-del-problema)
- [Diseño de la aplicación](#Diseño-de-la-aplicación)
- [Código fuente](#Código-fuente)
- [Manual de usuario](#Manual-de-usuario)
- [Manual técnico](#Manual-técnico)
- [Escenarios de prueba](#Escenarios-de-prueba)

## Marco Teórico

  

## Descripción y justificación del problema

  

## Diseño de la aplicación

  

## Código fuente

  

## Manual de usuario

Para desarrollo se requiere la instalacion de los siguientes paquetes:

- [UV](https://docs.astral.sh/uv/getting-started/installation/) Gestor de proyecto y package manager

En algunos entornos linux con instalaciones minimas es necesario instalar los siguientes paquetes para la ejecución de la interfaz gráfica:

```bash
libxcb-xinerama0
libxcb-icccm4 
libxcb-image0 
libxcb-keysyms1 
libxcb-render-util0 
libxcb-randr0 
libxcb-shape0 
libxcb-sync1 
libxcb-xfixes0 
libxcb-shm0 
libxcb-xkb1 
libxkbcommon-x11-0 
libxcb-xinerama0-dev
```

De momento, es requerido el siguiente [archivo](https://we.tl/t-oawXJBRm08) en la carpeta `/src/hmm_smart_keyboard/data/` para la ejecución de la aplicación.

Una vez configurado el entorno se puede ejecutar la aplicación con el comando:
```bash
uv run gui-sk
```
o si se desea usar sin interfaz grafica:
```bash
uv run python -m hmm_smart_keyboard.app
```

## Manual técnico




## Escenarios de prueba

