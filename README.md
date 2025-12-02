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

### Instalacion y ejecución
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

### Uso de la aplicación

#### Interfaz gráfica
![Vista Grafica](/images/guiExec.png)

Una vez se inicia la aplicacion aparece la anterior ventana. Con dos paneles principales el izquierdo es interactivo y el derecho muestra la informacion del procesamiento:

Panel izquierdo:

1. **Cuadro de texto:** Aqui se escribe el texto que se desea corregir.
2. **Boton**: Envia el texto a corregir al modelo de lenguaje. Tambien se puede presionar enter para enviar el texto.
3. **Vista de historial:** Muestra los resultados anteriores. Se pueden seleccionar para volver a ver las estadisticas.

Panel derecho:

4. **Texto original:** Muestra el texto ingresado por el usuario.
5. **Texto corregido:** Muestra el texto corregido por el modelo de lenguaje.
6. **Ranking:** Muestra las 5 predicciones mas probables segun el modelo y sus estadisticas:
    - Palabra
    - Ctx: 
    - Kbd:
    - Total:
7. **Score:** Muestra el score obtenido por la palara _ganadora_

#### Cli / Consola

![alt text](/images/cliExec.png)

Se puede escribir directamente la palabra en la consola.
Al dar `enter` se envia al modelo de lenguaje y se muestran los mismos resultados anteriores.

Para salir se puede presionar `Ctrl+C` o `Ctrl+D` en la consola o escribir `salir` en la consola.

## Manual técnico




## Escenarios de prueba

