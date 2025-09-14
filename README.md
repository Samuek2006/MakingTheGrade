# Alcanzando la Nota 🎓  
**Nombre original:** *Making The Grade*  

Este proyecto es un **MVP desarrollado en Python** como parte de una kata de arquitectura y un taller de Scrum. El objetivo es diseñar un sistema que permita al **Ministerio de Educación** estandarizar las pruebas de todos los colegios del país, asegurando consolidación, trazabilidad y facilidad de calificación.  

## 📌 Contexto  
El sistema debe dar soporte a:  
- **40,000+ estudiantes** que presentan pruebas en centros autorizados.  
- **2,000 calificadores** responsables de evaluar respuestas abiertas y ensayos.  
- **50 administradores** encargados de la supervisión y generación de reportes.  

## 🛠️ Requerimientos principales  
- Los estudiantes presentan las pruebas únicamente en **centros de prueba autorizados**.  
- Consolidación nacional de resultados (por colegio, profesor y estudiante).  
- Soporte a **preguntas de selección múltiple, respuesta corta y ensayos**.  
- **Calificación automática** para selección múltiple y **manual** para respuestas abiertas.  
- **Módulo de reportes** para consultar estudiantes presentados y puntajes obtenidos.  

## 🌐 Contexto adicional  
- Cambios en el almacenamiento de notas requieren aprobación de **3 entidades gubernamentales** (seguridad y auditoría).  
- El **hosting es delegado a un tercero**, ya que el país no cuenta con infraestructura propia.  
- El proyecto debe **defender su presupuesto** anualmente.  

## 🚀 Alcance del MVP  
El MVP incluye:  
1. **Presentación de exámenes** con preguntas de distintos tipos.  
2. **Autocalificación** de preguntas de selección múltiple.  
3. **Ingreso manual de notas** para respuestas cortas y ensayos.  
4. **Reportes básicos** para administradores (por estudiante y colegio).  
5. Consolidación de resultados en una **base de datos única** que simula el registro nacional.  

## 📂 Tecnologías  
- **Python 3.11+**  
- **SQLite** (almacenamiento ligero)  
- Scripts y funciones para gestión de exámenes, calificación y reportes  

## 🎯 Metodología  
El desarrollo se realizó con un enfoque **Scrum**, trabajando en sprints cortos y entregando un MVP funcional en 6 días, priorizando simplicidad y funcionalidad mínima viable.

---
### 📖 Historias y Avance por Sprint  

| Sprint | Historia / User Story | Estado | Responsable(s) | Notas |
|--------|------------------------|---------|----------------|-------|
| 1 | A1 – Iniciar sesión desde centro de pruebas | ✅ Terminado / En pruebas | Equipo | Validación simple lista |
| 1 | A2 – Presentar prueba selección múltiple | ⏳ En desarrollo | Equipo | Base central en construcción |
| 2 | A3 – Preguntas cortas y ensayo | 🔜 Pendiente | Equipo | Depende de A2 |
| 2 | B1 – Calificación de ensayos pendientes | 🔜 Pendiente | Equipo | Planificado para sprint 2 |
| 3 | B2 – Consolidar resultados finales | 🔜 Pendiente | Equipo | Sprint futuro |
| 3 | C1 – Reporte básico para administradores | 🔜 Pendiente | Equipo | Sprint futuro |

---

### 🏃 Sprint 1 – Resumen
- **Historias incluidas**: A1, A2  
- **Avances**:  
  - ✅ A1: Login funcional con validación de centro.  
  - ⏳ A2: Preguntas de selección múltiple en desarrollo, aún faltan pruebas automáticas y registro en DB.  
- **Retos encontrados**: Ajustes en estructura de datos para que todas las preguntas carguen desde la base central.  
- **Entregable parcial**: Prototipo de login + primera versión de examen selección múltiple.  

---

### 🏃 Sprint 2 – Resumen
- **Historias incluidas**: A3, B1  
- **Avances esperados**:  
  - Implementar campos de texto para preguntas cortas y ensayos.  
  - Crear vista de calificador con lista de ensayos pendientes.  
- **Notas**: La finalización de A2 es condición para este sprint.  

---

### 🏃 Sprint 3 – Resumen
- **Historias incluidas**: B2, C1  
- **Avances esperados**:  
  - Consolidar resultados automáticamente.  
  - Generar reportes básicos (por estudiante y puntajes).  
- **Notas**: Se espera dedicar esfuerzo adicional en validación, seguridad y pruebas de integración.  

## 📂 Estructura del Proyecto

```
MAKINGTHEGRADE
├── data/
│ ├── evidence.json
│ ├── grades.json
│ └── user.json
├── modules/
│ ├── admin/
│ │ └── adminView.py
│ ├── qualifiers/
│ │ └── qualifierView.py
│ └── students/
│ │ └── studentView.py
│ ├── login.json
│ └── mainMenu.py
├── util/
│ ├── corefiles.py
│ ├── session.py
│ └── utilidades.py
├── .gitignore
├── main.py
└── README.md

```

## ▶️ Ejecución

1. Clona este repositorio o descarga el proyecto.  
2. Asegúrate de tener **Python 3.10 o superior** instalado.  
3. Ejecuta el programa con:

```bash
python main.py
```

---

## EJEMPLO EJECUCION  

# 🔑 Inicio de Sesión y Roles

El sistema inicia siempre en un **login**, donde el usuario debe ingresar sus credenciales.  
Dependiendo del **rol** al que pertenezca la cuenta, accederá a un menú distinto (**Student, Qualifier o Admin**).

---

## 👥 Cuentas de Prueba

Estas cuentas están precargadas para que puedas probar el sistema sin necesidad de abrir los archivos JSON:

### 🧑‍🎓 Student
- **Usuario:** `student`  
- **Contraseña:** `Student1234`

### 👨‍🏫 Qualifier
- **Usuario:** `qualifier`  
- **Contraseña:** `Qualifier1234`

### 🛠 Admin
- **Usuario:** `admin`  
- **Contraseña:** `Admin1234`

---