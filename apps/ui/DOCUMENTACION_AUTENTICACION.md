# 📚 Documentación del Sistema de Autenticación

## 📋 Tabla de Contenidos

1. [Arquitectura General](#arquitectura-general)
2. [Flujo de Autenticación](#flujo-de-autenticación)
3. [Componentes Principales](#componentes-principales)
4. [Estructura del Proyecto](#estructura-del-proyecto)
5. [Proceso de Login Detallado](#proceso-de-login-detallado)
6. [Proceso de Registro](#proceso-de-registro)
7. [Cliente REST (API)](#cliente-rest-api)
8. [Puntos Importantes](#puntos-importantes)
9. [Mejoras Recomendadas](#mejoras-recomendadas)

---

## 🏗️ Arquitectura General

El proyecto utiliza una **arquitectura modular** con separación clara entre la **UI (Interfaz de Usuario)** y la **Lógica de Negocio**. El flujo de autenticación sigue este patrón:

```
main.py → AuthController → LoginLogic/RegisterLogic → RestClient (API) → MockAPI
```

### Patrón de Diseño

- **Separación de Responsabilidades**: Cada componente tiene una función específica
- **Router Central**: `AuthController` gestiona la navegación entre vistas
- **Lógica Separada**: `LoginLogic` y `RegisterLogic` manejan la lógica de negocio
- **UI Independiente**: `LoginUI` y `RegisterUI` solo se encargan de la presentación

---

## 🔄 Flujo de Autenticación

### Diagrama de Flujo

```
┌─────────────┐
│   main.py   │
│  (Splash)   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ AuthController  │  ← Router Central
└──────┬──────────┘
       │
       ├──────────────┬──────────────┐
       ▼              ▼              ▼
┌──────────┐   ┌──────────┐   ┌──────────┐
│  Login   │   │ Register │   │ Dashboard│
│  Logic   │   │  Logic   │   │  Logic   │
└────┬─────┘   └────┬─────┘   └────┬─────┘
     │              │              │
     ▼              ▼              ▼
┌──────────┐   ┌──────────┐   ┌──────────┐
│ LoginUI  │   │RegisterUI│   │DashboardUI│
└────┬─────┘   └────┬─────┘   └────┬─────┘
     │              │              │
     └──────────────┴──────────────┘
                    │
                    ▼
            ┌──────────────┐
            │ RestClient   │
            │   (API)      │
            └──────┬───────┘
                   │
                   ▼
            ┌──────────────┐
            │   MockAPI     │
            │  (Backend)    │
            └──────────────┘
```

---

## 🧩 Componentes Principales

### 1. **main.py** - Punto de Entrada

**Ubicación**: `main.py`

**Responsabilidades**:
- Inicializa la aplicación Flet
- Muestra la pantalla de splash
- Inicializa el `AuthController` después del splash

**Código Clave**:
```python
def main(page: ft.Page):
    # Configuración de la ventana
    page.window.full_screen = True
    
    # Mostrar splash
    splash = SplashUI(page)
    page.views.append(ft.View(route="/splash", controls=[splash]))
    
    # Después de 1 segundo, mostrar login
    async def go_login():
        await asyncio.sleep(1.0)
        AuthController(page)
```

---

### 2. **AuthController** - Router Central

**Ubicación**: `src/modules/login/auth_controller.py`

**Responsabilidades**:
- Gestiona la navegación entre vistas (login, registro, dashboard)
- Crea instancias de las clases de lógica
- Monta las vistas en `page.views`

**Métodos Principales**:

| Método | Descripción |
|--------|-------------|
| `show_login()` | Muestra la pantalla de login |
| `show_register()` | Muestra la pantalla de registro |
| `show_dashboard(user_obj)` | Muestra el dashboard con datos del usuario |
| `ir_login()` | Navega al login |
| `ir_register()` | Navega al registro |

**Flujo de Navegación**:
```python
# Login → Registro
LoginLogic.ir_register() → AuthController.show_register()

# Registro → Login
RegisterLogic.ir_login() → AuthController.show_login()

# Login → Dashboard (éxito)
LoginLogic.continuar(user) → AuthController.show_dashboard(user)
```

---

### 3. **LoginLogic** - Lógica de Login

**Ubicación**: `src/modules/login/login.py`

**Responsabilidades**:
- Crea y gestiona la UI de login (`LoginUI`)
- Valida credenciales del usuario
- Se comunica con la API para verificar usuarios
- Gestiona el overlay de carga
- Maneja el "Recordarme"

**Componentes**:
- `self.ui`: Instancia de `LoginUI`
- `self.api`: Cliente REST (`RestClient`)
- `self.loading_overlay`: Overlay de carga animado
- `self.router`: Referencia al `AuthController`

**Métodos Principales**:

| Método | Descripción |
|--------|-------------|
| `vefCredencialesUser()` | Verifica username y contraseña |
| `show_loading()` | Muestra overlay de carga |
| `hide_loading()` | Oculta overlay de carga |
| `show_info()` | Muestra mensajes (snackbar) |
| `continuar()` | Navega al dashboard tras login exitoso |
| `ir_register()` | Navega a registro |

---

### 4. **RegisterLogic** - Lógica de Registro

**Ubicación**: `src/modules/login/register.py`

**Responsabilidades**:
- Crea y gestiona la UI de registro (`RegisterUI`)
- Valida los datos del formulario
- Verifica que el username no exista
- Crea nuevos usuarios en la API

**Métodos Principales**:

| Método | Descripción |
|--------|-------------|
| `registrar()` | Procesa el registro de nuevo usuario |
| `validar()` | Valida todos los campos del formulario |
| `ir_login()` | Navega de vuelta al login |

**Validaciones**:
- Nombre: No vacío
- Apellido: No vacío
- Teléfono: Mínimo 7 caracteres
- Username: Mínimo 3 caracteres, único
- Contraseña: Mínimo 6 caracteres

---

### 5. **RestClient** - Cliente REST

**Ubicación**: `src/API/crud.py`

**Responsabilidades**:
- Realiza peticiones HTTP a la API MockAPI
- Maneja errores de red
- Proporciona métodos CRUD (Create, Read, Update, Delete)

**URL Base**: `https://69069a11b1879c890ed7a77d.mockapi.io/`

**Métodos Disponibles**:

| Método | Descripción | Ejemplo |
|--------|-------------|---------|
| `get(path, params)` | Obtener datos | `api.get("users", params={"search": "user"})` |
| `post(path, json)` | Crear recurso | `api.post("users", json={...})` |
| `put(path, json)` | Reemplazar recurso | `api.put("users/1", json={...})` |
| `patch(path, json)` | Actualizar parcialmente | `api.patch("users/1", json={...})` |
| `delete(path)` | Eliminar recurso | `api.delete("users/1")` |

**Retorno**:
Todas las peticiones retornan una tupla:
```python
(ok: bool, data: JSON, status: int, error: str)
```

---

## 📁 Estructura del Proyecto

```
UI MarkingTheGrade/
├── main.py                          # Punto de entrada principal
│
├── src/
│   ├── API/
│   │   └── crud.py                 # Cliente REST para MockAPI
│   │
│   ├── modules/
│   │   ├── login/
│   │   │   ├── auth_controller.py  # Router central de autenticación
│   │   │   ├── login.py            # Lógica de login
│   │   │   └── register.py         # Lógica de registro
│   │   │
│   │   ├── dashboard/
│   │   │   └── dashboardLogic.py   # Lógica del dashboard
│   │   │
│   │   ├── navBar/
│   │   │   └── navBarLogic.py      # Lógica de navegación
│   │   │
│   │   └── pruebas/
│   │       └── pruebasLogic.py     # Lógica de pruebas
│   │
│   ├── views/
│   │   ├── session.py              # UI de Login y Register
│   │   ├── dashboard.py            # UI del dashboard
│   │   ├── splash.py               # Pantalla de inicio
│   │   ├── loading_overlay.py      # Overlay de carga animado
│   │   ├── nav_bar.py              # Barra de navegación
│   │   └── pruebaPanel.py          # Panel de pruebas
│   │
│   └── utils/
│       ├── buttonLogin.py          # Componente de botón personalizado
│       └── constants.py            # Constantes del proyecto
│
├── storage/
│   ├── data/                       # Datos persistentes
│   └── temp/                       # Archivos temporales
│
├── requirements.txt                # Dependencias Python
├── pyproject.toml                  # Configuración del proyecto
└── README.md                       # Documentación general
```

---

## 🔐 Proceso de Login Detallado

### Paso a Paso

#### **Paso 1: Usuario ingresa credenciales**

El usuario completa los campos en `LoginUI`:
- Username
- Contraseña
- (Opcional) Checkbox "Recordarme"

#### **Paso 2: Validación inicial**

```python
def vefCredencialesUser(self, e, user_val, pwd_val):
    # 1. Validar que los campos no estén vacíos
    if not user or not pwd:
        return  # Muestra error en UI
```

#### **Paso 3: Mostrar overlay de carga**

```python
self.show_loading("Verificando credenciales...")
# Muestra animación de carga con mensaje
```

#### **Paso 4: Buscar usuario en la API**

```python
# Realiza GET request a MockAPI
ok_u, users, status_u, err_u = self.api.get(
    "users", 
    params={"search": user}
)
```

**Request**:
```
GET https://69069a11b1879c890ed7a77d.mockapi.io/users?search=Andres1234
```

**Response esperado**:
```json
[
  {
    "id": "1",
    "username": "Andres1234",
    "password_hash": "123456",
    "nombre": "Andrés",
    "apellido": "García",
    "rol": "user",
    "estado": "activo"
  }
]
```

#### **Paso 5: Verificar existencia del usuario**

```python
# Buscar usuario exacto por username
usr = next((u for u in data if u.get("username") == user), None)

if not usr:
    # Mostrar error: usuario no encontrado
    self.loading_overlay.show_error()
    return
```

#### **Paso 6: Comparar contraseña**

```python
# ⚠️ IMPORTANTE: Actualmente compara texto plano
if str(usr.get("password_hash", "")) != str(pwd):
    # Mostrar error: contraseña incorrecta
    self.loading_overlay.show_error()
    return
```

**⚠️ Nota de Seguridad**: Las contraseñas se almacenan y comparan en texto plano. Esto es solo para demostración.

#### **Paso 7: Guardar "Recordarme" (opcional)**

```python
if self.ui.remember.value:
    # Guardar username en almacenamiento local
    self.page.client_storage.set("remember_username", user)
else:
    # Eliminar si no está marcado
    self.page.client_storage.remove("remember_username")
```

#### **Paso 8: Navegar al Dashboard**

```python
# Mostrar mensaje de éxito
self.loading_overlay.loading_text.value = "¡Inicio de sesión exitoso!"

# Navegar al dashboard con datos del usuario
self.continuar(usr)  # → AuthController.show_dashboard(usr)
```

---

## 📝 Proceso de Registro

### Paso a Paso

#### **Paso 1: Usuario completa formulario**

Campos requeridos:
- Nombre
- Apellido
- Teléfono
- Username
- Contraseña

#### **Paso 2: Validación de campos**

```python
def validar(self) -> bool:
    # Valida cada campo:
    # - Nombre: no vacío
    # - Apellido: no vacío
    # - Teléfono: mínimo 7 caracteres
    # - Username: mínimo 3 caracteres
    # - Contraseña: mínimo 6 caracteres
```

#### **Paso 3: Verificar username único**

```python
# Buscar si el username ya existe
ok_u, users, _, _ = self.api.get("users", params={"search": username})

if any(u.get("username") == username for u in users):
    self._toast("El usuario ya existe")
    return
```

#### **Paso 4: Construir payload**

```python
payload = {
    "nombre": nombre,
    "apellido": apellido,
    "telefono": telefono,
    "username": username,
    "password_hash": password,  # ⚠️ Texto plano
    "rol": "user",
    "estado": "activo"
}
```

#### **Paso 5: Crear usuario en API**

```python
ok, data, status, err = self.api.post("users", json=payload)

if ok:
    self._toast("Usuario registrado correctamente")
    self.ir_login()  # Redirigir al login
else:
    self._toast(f"Error: {err}")
```

**Request**:
```
POST https://69069a11b1879c890ed7a77d.mockapi.io/users
Content-Type: application/json

{
  "nombre": "Juan",
  "apellido": "Pérez",
  "telefono": "+1234567890",
  "username": "juan123",
  "password_hash": "mipassword",
  "rol": "user",
  "estado": "activo"
}
```

---

## 🌐 Cliente REST (API)

### Configuración

**URL Base**: `https://69069a11b1879c890ed7a77d.mockapi.io/`

**Timeout**: 12 segundos

**Headers por defecto**:
```python
{
    "Content-Type": "application/json"
}
```

### Ejemplos de Uso

#### **Buscar usuarios**
```python
api = RestClient(base_url="https://69069a11b1879c890ed7a77d.mockapi.io/")

# Buscar por username
ok, users, status, err = api.get("users", params={"search": "Andres1234"})

if ok:
    print(f"Encontrados {len(users)} usuarios")
else:
    print(f"Error {status}: {err}")
```

#### **Crear usuario**
```python
payload = {
    "username": "nuevo_user",
    "password_hash": "password123",
    "rol": "user"
}

ok, data, status, err = api.post("users", json=payload)

if ok:
    print(f"Usuario creado: {data}")
else:
    print(f"Error: {err}")
```

#### **Obtener usuario por ID**
```python
ok, user, status, err = api.get("users/1")

if ok:
    print(f"Usuario: {user}")
```

### Manejo de Errores

El cliente REST maneja errores de forma elegante:

```python
try:
    resp = self._session.request(...)
    # Procesar respuesta
except requests.exceptions.RequestException as e:
    return False, None, 0, str(e)
```

**Códigos de estado**:
- `200-299`: Éxito (`ok = True`)
- `400-599`: Error (`ok = False`)

---

## ⚠️ Puntos Importantes

### 1. **Seguridad Actual**

#### **Contraseñas en Texto Plano**
- ⚠️ Las contraseñas se almacenan y comparan en texto plano
- ⚠️ No hay hashing (bcrypt, argon2, etc.)
- ⚠️ Esto es solo para demostración/MVP

**Código actual**:
```python
# En register.py
"password_hash": ui.password_tf.value  # ⚠️ No es hash real

# En login.py
if str(usr.get("password_hash", "")) != str(pwd):  # ⚠️ Comparación directa
```

#### **Sin Tokens de Sesión**
- No hay JWT (JSON Web Tokens)
- No hay sesiones persistentes
- El usuario se autentica en cada inicio de sesión

#### **Sin HTTPS en Desarrollo**
- La API MockAPI usa HTTPS, pero en producción debería validarse

### 2. **Almacenamiento Local**

#### **Client Storage**
```python
# Guardar
page.client_storage.set("remember_username", username)

# Leer
remembered_username = page.client_storage.get("remember_username") or ""

# Eliminar
page.client_storage.remove("remember_username")
```

**⚠️ Limitaciones**:
- Solo guarda el username (no la contraseña)
- No hay encriptación del almacenamiento local
- Se puede limpiar fácilmente

### 3. **Flujo de Navegación**

```
┌─────────┐
│ Splash  │
└────┬────┘
     │
     ▼
┌─────────────────┐
│ AuthController  │
└────┬────────────┘
     │
     ├──────────────┬──────────────┐
     ▼              ▼              ▼
┌──────────┐   ┌──────────┐   ┌──────────┐
│  Login   │   │ Register │   │ Dashboard│
└────┬─────┘   └────┬─────┘   └──────────┘
     │              │
     └──────┬───────┘
            │
            ▼
     (Usuario autenticado)
```

### 4. **API Utilizada**

#### **MockAPI**
- **URL**: `https://69069a11b1879c890ed7a77d.mockapi.io/`
- **Tipo**: Servicio de mock/testing
- **Endpoint**: `/users`
- **Operaciones**: GET, POST, PUT, PATCH, DELETE

**⚠️ Limitaciones**:
- Es un servicio de prueba, no producción
- Los datos pueden ser temporales
- No hay garantía de persistencia

---

## 🚀 Mejoras Recomendadas

### 1. **Seguridad de Contraseñas**

#### **Implementar Hashing**
```python
import bcrypt

# Al registrar
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Al verificar
is_valid = bcrypt.checkpw(password.encode(), stored_hash.encode())
```

#### **Requisitos de Contraseña**
- Mínimo 8 caracteres
- Al menos una mayúscula
- Al menos un número
- Al menos un carácter especial

### 2. **Sistema de Tokens**

#### **Implementar JWT**
```python
import jwt
import datetime

# Generar token al login
token = jwt.encode({
    'user_id': user['id'],
    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
}, SECRET_KEY, algorithm='HS256')

# Validar token en cada request
decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
```

### 3. **Base de Datos Real**

#### **Migrar de MockAPI a Base de Datos**
- **SQLite** para desarrollo
- **PostgreSQL** para producción
- **ORM** como SQLAlchemy

### 4. **Validación Mejorada**

#### **Validación en Backend**
- Validar datos en el servidor, no solo en el cliente
- Sanitizar inputs
- Prevenir SQL Injection

### 5. **Manejo de Errores**

#### **Errores Específicos**
```python
class AuthError(Exception):
    pass

class UserNotFoundError(AuthError):
    pass

class InvalidPasswordError(AuthError):
    pass
```

### 6. **Logging y Auditoría**

#### **Registrar Eventos**
```python
import logging

logging.info(f"Usuario {username} inició sesión")
logging.warning(f"Intento de login fallido para {username}")
```

### 7. **Rate Limiting**

#### **Prevenir Ataques de Fuerza Bruta**
```python
# Limitar intentos de login por IP
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = 15 * 60  # 15 minutos
```

### 8. **Recuperación de Contraseña**

#### **Implementar Reset de Contraseña**
- Envío de email con token
- Página de reset
- Validación de token

---

## 📊 Resumen del Flujo Completo

### Login

```
1. Usuario ingresa credenciales
   ↓
2. LoginLogic.vefCredencialesUser() se ejecuta
   ↓
3. Validación de campos (UI)
   ↓
4. Mostrar overlay de carga
   ↓
5. Buscar usuario en API (GET /users?search=username)
   ↓
6. Verificar que el usuario existe
   ↓
7. Comparar contraseña (texto plano)
   ↓
8. Si es correcto:
   - Guardar username (si "Recordarme" está activo)
   - Mostrar mensaje de éxito
   - Navegar al dashboard
   ↓
9. Si hay error:
   - Mostrar error en overlay
   - Permitir reintento
```

### Registro

```
1. Usuario completa formulario
   ↓
2. RegisterLogic.validar() valida campos
   ↓
3. Verificar que username no existe (GET /users?search=username)
   ↓
4. Construir payload con datos
   ↓
5. Crear usuario (POST /users)
   ↓
6. Si es exitoso:
   - Mostrar mensaje de éxito
   - Redirigir al login
   ↓
7. Si hay error:
   - Mostrar mensaje de error
   - Permitir corrección
```

---

## 🔍 Cuentas de Prueba

Según el README del proyecto:

- **Usuario**: `Andres1234`
- **Contraseña**: `123456`

Estas credenciales están almacenadas en MockAPI y pueden usarse para probar el sistema.

---

## 📞 Soporte

Para más información sobre el proyecto, consulta:
- `README.md` - Documentación general del proyecto
- Código fuente en `src/modules/login/`
- Comentarios en el código

---

**Última actualización**: 2024
**Versión del documento**: 1.0

