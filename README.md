# Apache Derby DBMS

Un DBMS sencillo para Apache Derby hecho en Python con interfaz Tkinter. Permite administrar conexiones, esquemas, tablas, índices, vistas, triggers, procedimientos, funciones, checks y ejecutar queries.

El proyecto incluye el servidor Apache Derby (`db-derby-10.17.1.0-bin/`), así que solo hace falta tener Java y unas pocas dependencias de Python.

## Requisitos

- **Python 3** (probado con 3.11). Tkinter ya viene incluido en el Python oficial de macOS.
- **Java 21+** (Apache Derby 10.17 está compilado con class file version 63 → requiere JDK 19 mínimo, recomendado 21).
- **pip** para instalar paquetes de Python.

### Instalar Java en macOS (con Homebrew)

```bash
brew install openjdk@21
sudo ln -sfn /opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk \
  /Library/Java/JavaVirtualMachines/openjdk-21.jdk
```

Exportar `JAVA_HOME` y agregar al `PATH` (agregalo a `~/.zshrc` para que sea permanente):

```bash
export JAVA_HOME=/opt/homebrew/opt/openjdk@21
export PATH="$JAVA_HOME/bin:$PATH"
```

Verificá:

```bash
java -version   # debe imprimir openjdk version "21..."
```

### Instalar dependencias de Python

Usar wheels prebuilt evita compilar JPype1 desde source:

```bash
pip install --upgrade pip
pip install --only-binary=:all: JPype1 jaydebeapi
```

Si tu versión de Python no tiene wheel para la última JPype1, fijala:

```bash
pip install JPype1==1.5.2 jaydebeapi
```

## Cómo correr el proyecto

### 1. Levantar el Derby Network Server

En una terminal:

```bash
cd db-derby-10.17.1.0-bin/bin
./NetworkServerControl start -h localhost -p 1527
```

Dejala corriendo. Cuando veas `Apache Derby Network Server ... started and ready` el servidor está listo en `localhost:1527`.

### 2. Correr la aplicación

En otra terminal, desde la raíz del proyecto:

```bash
python3 clase.py
```

### 3. Crear una conexión desde la UI

En el panel izquierdo presioná **Crear** y completá:

| Campo    | Valor de ejemplo |
|----------|------------------|
| hostname | `localhost`      |
| port     | `1527`           |
| sid (DB) | `myNewDB`        |
| username | el que quieras   |
| password | el que quieras   |

Derby está configurado con `create=true`, así que la base se crea automáticamente la primera vez que conectás.

Una vez creada la conexión, seleccionala y presioná **Conectar**. Vas a poder navegar las pestañas: Tablas, Indices, Procedimientos Almacenados, Funciones, Triggers, Vistas, Checks, Esquemas y Query.

## Detener el servidor

```bash
cd db-derby-10.17.1.0-bin/bin
./NetworkServerControl shutdown -h localhost -p 1527
```

## Notas

- El driver JDBC se resuelve relativo al script (`db-derby-10.17.1.0-bin/lib/derbyclient.jar`), así que no hay que tocar rutas al cambiar de máquina.
- Las conexiones guardadas se persisten en `connections.pkl`.
