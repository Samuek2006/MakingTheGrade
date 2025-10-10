# MakingTheGrade

MVP para *Alcanzando la Nota*. Permite a **estudiantes** presentar pruebas con preguntas mixtas, a **profesores** calificar manualmente respuestas abiertas y a **administradores** generar reportes básicos consolidados.

> UI actual en **Python** (`apps/ui`) y preparación de **backend en C#** (planificado en `apps/api`). Infraestructura y scripts auxiliares en `infra`.

---

## 🗂️ Estructura del repositorio

```
.
├─ apps/
│  ├─ ui/          # Frontend/cliente escrito en Python (UI actual)
│  └─ api/         # (Plan) Backend en C#/.NET para endpoints REST
├─ infra/          # Infraestructura, scripts de despliegue, IaC, pipelines
├─ docs/           # (Sugerido) Diagramas, decisiones, guías operativas
├─ .env.example    # (Sugerido) Variables de entorno ejemplo
└─ README.md
```

---

## 🎯 Objetivos del proyecto

- **Estudiantes:** presentar pruebas (ítems selección múltiple y abiertas).
- **Profesores:** calificar respuestas abiertas y revisar resultados por estudiante/prueba.
- **Administradores:** ver reportes/indicadores agregados por sede/ciudad/país.
- **Arquitectura evolutiva:** separar UI (Python) y API (C#) con contratos claros.

---

## 🏗️ Arquitectura (propuesta)

- **UI (Python)**: cliente de escritorio/web que consume la API.  
- **API (C#/.NET)**: expone endpoints REST para autenticación, pruebas, calificaciones y reportes.  
- **Capa de datos**: base relacional (p. ej., MySQL/SQL Server/PostgreSQL — definir).  
- **Infra**: contenedores, CI/CD, IaC (según necesidades).

**Diagrama lógico (alto nivel):**

```
[UI Python]  <---- HTTP/JSON ---->  [API C# .NET]  <---- SQL/ORM ---->  [Base de Datos]
```

---

## ⚙️ Configuración inicial

### 1. Clonar el repositorio
```bash
git clone https://github.com/Samuek2006/MakingTheGrade.git
cd MakingTheGrade
```

### 2. Entorno Python (UI)
```bash
cd apps/ui
python -m venv venv
venv\Scripts\activate     # (Windows)
pip install -r requirements.txt
python main.py
```

### 3. Backend C# (API)
> 🔧 **Pendiente:** crear solución `.NET` (por ejemplo `MakingTheGrade.Api`) con endpoints REST.  
Ejemplo:
```bash
cd apps
dotnet new webapi -n MakingTheGrade.Api
```

### 4. Base de datos
> Definir conexión en archivo `.env` o configuración de entorno.  
Ejemplo:
```env
DB_HOST=localhost
DB_USER=root
DB_PASS=
DB_NAME=makingthegrade
```

---

## 🧩 Funcionalidades previstas

| Módulo | Lenguaje | Estado | Descripción |
|--------|-----------|--------|--------------|
| UI | Python | ✅ En desarrollo | Interfaz gráfica funcional |
| API | C# | 🚧 Pendiente | Backend con endpoints REST |
| DB | MySQL | 🚧 Pendiente | Gestión de usuarios, pruebas y resultados |
| Infra | — | 🧱 Base | Scripts de despliegue y estructura de proyecto |

---

## 📘 Licencia

Este proyecto se distribuye bajo la licencia MIT.  
© 2025 MakingTheGrade — Todos los derechos reservados.
