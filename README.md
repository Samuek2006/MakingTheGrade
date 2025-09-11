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
