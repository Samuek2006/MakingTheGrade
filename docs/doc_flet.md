# 📘 DOCUMENTACIÓN DEL DESARROLLO EN FLET

Esta guía reúne los aspectos clave que debes conocer cuando desarrollas y distribuyes tu aplicación con **Flet**. Además de repasar la estructura del proyecto, se explican las secciones importantes del archivo `pyproject.toml`, el archivo `requirements.txt` y la gestión de permisos y dependencias de Flutter.  
La intención es que cualquier desarrollador que lea este código comprenda qué hace cada sección y pueda **reproducir el entorno** o **adaptarlo** según sus necesidades.

---

## ⚙️ Configuración del entorno

Para ejecutar y empaquetar correctamente una aplicación Flet se recomienda disponer de un **entorno aislado** con **Python >= 3.9** (este proyecto utiliza **Python 3.11**) y los **paquetes mínimos necesarios**. Los pasos básicos son:

1) **Crear un virtualenv y activarlo**  
   ```bash
   python -m venv venv
   # Linux / macOS
   source venv/bin/activate
   # Windows
   venv\Scripts\activate
   ```

2) **Instalar Flet y las dependencias de la aplicación**  
   ```bash
   pip install -r requirements.txt
   ```

3) **Lanzar la aplicación en modo desarrollo**  
   ```bash
   python main.py
   # o bien (con recarga en caliente)
   flet run
   ```

4) **Configurar un archivo `.env` (opcional)** con las variables de entorno de la base de datos si se desea personalizar:  
   - `SQLITE_DB_PATH`: ruta de la base local  
   - `DB_NAME`: nombre de la base  
   - Otros parámetros descritos en este README

> 🔹 **Recomendación del equipo de Flet:** declara las dependencias en `pyproject.toml` en lugar de `requirements.txt`. Cuando ambos ficheros existen, **Flet prioriza `pyproject.toml`** y **no** se debe crear `requirements.txt` mediante `pip freeze`, ya que incluiría paquetes no compatibles con móviles (por ejemplo, `watchdog`). En su lugar, **selecciona a mano** sólo las **dependencias directas** y `flet`.

---

## 🧭 Archivos de configuración clave

### `pyproject.toml`

El archivo `pyproject.toml` combina la configuración estándar del proyecto con opciones específicas de Flet. Su **estructura básica** (según la documentación oficial) incluye una sección `[project]` con metadatos como **nombre**, **versión**, **descripción**, **autores** y las **dependencias mínimas** (al menos `flet`).  
En el caso de esta aplicación, además de Flet se requieren:

- `python-dotenv` para cargar variables de entorno.  
- **Uno** entre `httpx` **o** `requests` como cliente HTTP (elige uno y elimina el otro para evitar duplicados).  
- `certifi` para incluir certificados SSL al empaquetar la app.

A continuación se describen las secciones más relevantes del `pyproject.toml` de este proyecto:

#### Sección `[project]`
Define el nombre de la app (`name`), la versión (`version`), la ruta del archivo de lectura (`readme`) y la versión mínima de Python (`requires-python`).  
La lista `dependencies` declara los paquetes que se instalarán al construir la app. Según la guía de Flet, **basta con indicar `flet` y las dependencias directas**; evitar paquetes innecesarios ayuda a reducir el tamaño del paquete.

#### Sección `[tool.flet]`
Agrupa las opciones de empaquetado propias de Flet. Aquí se establece:
- `org`: identificador en notación de dominio inverso (por ejemplo `com.mycompany`) que se combina con `project.name` para formar el **Bundle ID** de las versiones móviles.
- `product`: **nombre visible** de la app en la pantalla de inicio y en las ventanas de escritorio.
- `company`: nombre de la compañía que se muestra en los diálogos “Acerca de”.
- `copyright`: texto de derechos de autor.
- `module_name`: módulo Python que contiene la función `main()` (en este proyecto es `main`).

#### Sección `[tool.flet.app]`
Especifica la ruta donde Flet encontrará la aplicación. Si los archivos fuente están en la **raíz**, se usa `path = "."` (como en este proyecto); si se alojan en un subdirectorio como `src`, se debe cambiar este valor.

#### Secciones de configuración de Flutter
Flet utiliza un **proyecto Flutter temporal** durante el empaquetado. Es posible **añadir o sobrescribir** configuraciones de su `pubspec.yaml` directamente desde `pyproject.toml` mediante las secciones `[tool.flet.flutter.*]`:

- `[tool.flet.flutter.pubspec.environment]`: define la versión mínima y máxima del SDK de **Dart** que se usará en el wrapper de Flutter (por ejemplo, `sdk = ">=3.7.0-0 <4.0.0"`).
- `[tool.flet.flutter.pubspec.dependencies]`: permite incluir **paquetes de Flutter** adicionales. En este proyecto se añade `webview_flutter` para incrustar páginas web y `webview_flutter_android` para la implementación específica de Android.
- `[tool.flet.flutter.pubspec.dependency_overrides]`: sirve para **forzar una versión concreta** de una dependencia cuando la predeterminada no es compatible.  
  Por ejemplo, si al construir el APK aparece un error indicando que la versión de `webview_flutter_android` es demasiado alta, puedes fijar una versión compatible añadiendo:
  ```toml
  [tool.flet.flutter.pubspec.dependency_overrides]
  webview_flutter_android = "3.7.1"
  ```
  (Este ajuste se documenta en varios tutoriales de Flet como solución a conflictos de versiones.)

#### Sección `[tool.uv]`
Incluye dependencias de desarrollo para el gestor **uv** (opcional). Aquí se puede indicar `flet[all]` con la misma versión que el paquete principal para instalar **todos los controles adicionales** durante el desarrollo.

#### Sección `[tool.poetry]` y grupos de dependencias
Si utilizas **Poetry** para manejar dependencias, Flet también lee estas secciones. En este proyecto se especifica `package-mode = false` y se declara un grupo `dev` donde se instalan las dependencias de desarrollo (por ejemplo, `flet` con todos sus extras).

---

## 🤖 Permisos y características de Android

Flet permite **configurar directamente** los permisos y características que se escribirán en `AndroidManifest.xml` desde `pyproject.toml`.

- `[tool.flet.android.permission]`: cada clave es un **permiso de Android** y su valor es `true/false` indicando si se solicita.  
  En este proyecto se habilitan permisos como `CAMERA`, `INTERNET`, `ACCESS_NETWORK_STATE`, `READ_EXTERNAL_STORAGE` y `WRITE_EXTERNAL_STORAGE`. También se añade `RECORD_AUDIO`, inicialmente **desactivado**; cambia el valor a `true` si tu aplicación necesita grabar audio.

- `[tool.flet.android.feature]`: define **características de hardware** que se escribirán en el manifiesto para que **Play Store filtre dispositivos**. Por ejemplo, se indica que la aplicación **requiere cámara** (`android.hardware.camera`), **autofoco** (`android.hardware.camera.autofocus`) y **no** requiere micrófono (`android.hardware.microphone = false`).

---

## 📝 `requirements.txt`

Aunque Flet **prioriza `pyproject.toml`**, este proyecto mantiene un `requirements.txt` con las librerías **mínimas** para el desarrollo y la ejecución en escritorio.  
Al generarlo se han **seleccionado a mano** sólo los paquetes necesarios para evitar incluir dependencias incompatibles con Android.  
La documentación oficial subraya que **no** se debe crear este archivo con `pip freeze` porque añadiría paquetes como `watchdog` que no funcionan en móviles.

Ejemplo de `requirements.txt` usado aquí:
```text
flet==0.28.3
python-dotenv==1.0.1
httpx==0.28.1
# Si prefieres requests en vez de httpx, deja solo una de estas líneas:
requests==2.32.5
certifi==2024.8.30
```

---

## 📦 Dependencias utilizadas (resumen)

| Dependencia             | Versión   | Propósito principal                                                                 |
|-------------------------|-----------|--------------------------------------------------------------------------------------|
| flet                    | 0.28.3    | Framework de UI que permite construir la app en Python con widgets de Flutter.      |
| python-dotenv           | 1.0.1     | Carga variables de entorno desde un archivo `.env`.                                 |
| httpx / requests        | 0.28.1 / 2.32.5 | Clientes HTTP para consumir APIs externas; **elige uno** y elimina el otro.  |
| certifi                 | 2024.8.30 | Certificados CA para conexiones HTTPS seguras.                                      |
| webview_flutter         | 4.10.0    | Paquete de Flutter para mostrar contenido web dentro de la app.                     |
| webview_flutter_android | 4.10.1    | Implementación específica de Android para `webview_flutter`; fíjalo si hay conflictos. |

> En el entorno de desarrollo se pueden incluir paquetes como `cookiecutter`, `markdown-it-py` o `watchdog` **solo** para la experiencia de desarrollo (no para la app móvil).

---

## 🔐 Permisos en tiempo de ejecución (Permission Handler)

Una vez configurados los permisos en `pyproject.toml`, la app puede **comprobar y solicitar permisos en tiempo de ejecución** usando controles/paquetes tipo *PermissionHandler*.  
Para que funcione en el empaquetado, añade el paquete correspondiente (p.ej. `flet-permission-handler`) a la lista de dependencias en `pyproject.toml`. Su uso típico consiste en instanciar el manejador y llamar a métodos como `check_permission` o `request_permission` desde la UI.

> Asegúrate de **declarar también el permiso** en `[tool.flet.android.permission]` para que esté presente en el `AndroidManifest.xml` del build.

---

## 🎛️ Controles opcionales y extensiones (Audio/Video/WebView)

Flet soporta **controles adicionales** (Audio, Video, WebView, etc.) como **paquetes de Python**. La guía de publicación indica que si tu aplicación utiliza estos controles, debes **incluir sus paquetes** en la sección `dependencies` del `pyproject.toml` **o** pasar `--include-packages` al comando `flet build`.

Ejemplo de declaración en `pyproject.toml` (como paquetes Python):
```toml
[project]
dependencies = [
  "flet==0.28.3",
  "flet-audio==2.0.0",
  "flet-video==1.0.0",
  # ...
]
```

Si prefieres **inyectar dependencias Flutter** directamente, puedes añadirlas en:
```toml
[tool.flet.flutter.pubspec.dependencies]
webview_flutter = "4.10.0"
webview_flutter_android = "4.10.1"   # cambia a "3.7.1" si tu build lo requiere
```

---

## ✅ Buenas prácticas

- **Mantén las dependencias al mínimo**: evita paquetes innecesarios.  
- **Separa la lógica de UI y negocio**: por ejemplo, `src/views/` (pantallas) y `src/components/` (componentes reutilizables).  
- **Permisos incrementales**: comienza con los **mínimos** y habilita gradualmente los que necesites.  
- **Fija versiones** cuando haya conflictos (usa `dependency_overrides` para Flutter).  
- **CLI de Flet** para desarrollar y empaquetar:
  ```bash
  flet run
  flet build android     # o: ios / windows / macos / linux / web
  ```

---

## 🔧 Ejemplo completo de `pyproject.toml` (proyecto *Making the Grade*)

```toml
[project]
name = "Making the Grade"
version = "0.1.6"
description = ""
readme = "README.md"
requires-python = ">=3.9"
authors = [
    { name = "SamDev Developer", email = "samuelcalderonsoto@gmail.com" }
]
dependencies = [
  "flet==0.28.3",
  "python-dotenv==1.0.1",
  # Elige UNO de los dos clientes HTTP:
  "httpx==0.28.1",
  "requests==2.32.5",
  "certifi==2024.8.30",
]

[tool.flet]
org = "com.mycompany"
product = "makingthegrade"
company = "SamDev"
copyright = "Copyright (C) 2025 by SamDev"
module_name = "main"

[tool.flet.app]
path = "."

# Configuración de Flutter (wrapper)
[tool.flet.flutter.pubspec.environment]
sdk = ">=3.7.0-0 <4.0.0"

[tool.flet.flutter.pubspec.dependencies]
webview_flutter = "4.10.0"
webview_flutter_android = "4.10.1"

# Si hay conflictos de versión en Android:
[tool.flet.flutter.pubspec.dependency_overrides]
# Alternativa recomendable cuando 4.10.1 falla en tu build:
# webview_flutter_android = "3.7.1"

# Permisos y características Android
[tool.flet.android.permission]
"android.permission.CAMERA" = true
"android.permission.INTERNET" = true
"android.permission.ACCESS_NETWORK_STATE" = true
"android.permission.READ_EXTERNAL_STORAGE" = true
"android.permission.WRITE_EXTERNAL_STORAGE" = true
"android.permission.RECORD_AUDIO" = false

[tool.flet.android.feature]
"android.hardware.camera" = true
"android.hardware.camera.autofocus" = true
"android.hardware.microphone" = false

# Dependencias de desarrollo (opcional, gestores alternativos)
[tool.uv]
dev-dependencies = [
  "flet[all]==0.28.3",
]

[tool.poetry]
package-mode = false

[tool.poetry.group.dev.dependencies]
flet = { extras = ["all"], version = "0.28.3" }
```

---

## 📄 `requirements.txt` sugerido

```text
flet==0.28.3
python-dotenv==1.0.1
# Elegir UNO: httpx o requests
httpx==0.28.1
requests==2.32.5
certifi==2024.8.30
```

> Si empaquetas para móviles, evita `pip freeze`. Mantén este archivo curado manualmente.

---

## 🔗 Recursos útiles

- Sitio y docs de Flet: https://flet.dev / https://docs.flet.dev  
- Ejemplos oficiales: https://github.com/flet-dev/examples

---

**© 2025 · Making the Grade · SamDev Developer**
