# 📘 Alcanzando la Nota Pruebas🎓  
**Nombre original:** *Making The Grade*  

Un **MVP educativo desarrollado en Python + Flet** que busca convertirse en la base para un sistema de estandarización de pruebas escolares a nivel nacional.  

El objetivo es ofrecer al **Ministerio de Educación** una plataforma que garantice:  
✅ Estandarización de pruebas  
✅ Consolidación y trazabilidad de resultados  
✅ Facilidad de calificación y análisis  

Actualmente está en **fase de transición** desde una versión de consola hacia una **interfaz gráfica modular**, con miras a conectarse a una **base de datos** para gestión real de usuarios y reportes.  

---

## 🖼️ Capturas de Pantalla  

### 🔑 Login  
Pantalla inicial para autenticación de usuario.  
![Login](/img/login.png)  

### 🏠 Dashboard – Pruebas disponibles  
Vista general con tarjetas dinámicas de pruebas activas.  
![Dashboard](/img/home.png)  

### 📝 Presentación de Prueba  
Preguntas de selección múltiple con temporizador, validación y navegación controlada.  
![Prueba](/img/prueba.png)  

---

## 🚀 Funcionalidades actuales  

- **Login gráfico** con usuario y contraseña (mock).  
- **Dashboard de pruebas** con navegación modularizada.  
- **Presentación de pruebas** con:  
  - Temporizador automático ⏱️  
  - Opciones seleccionables con feedback inmediato  
  - Flujo Validar → Siguiente  
- **UI responsive** adaptable a escritorio y dispositivos móviles.  

---

## 🛠️ Roadmap / Próximos pasos  

- Conexión con **base de datos** (SQLite / PostgreSQL).  
- Gestión de **roles de usuario** (estudiante, calificador, administrador).  
- Registro y consolidación de resultados por estudiante.  
- Generación de reportes automáticos con estadísticas.  
- Exportación de resultados en PDF/Excel.  

---

## 🧩 Tecnologías utilizadas  

- **Python 3.11+**  
- **Flet** – framework para la UI (Flutter desde Python)  
- (Próximamente) **SQLite/PostgreSQL** para persistencia de datos  

---

## 📂 Estructura del Proyecto  

```
MakingTheGrade V2/
├── apps/ # Aplicaciones principales
│ ├── console/ # Versión en consola
│ │ ├── data/ # Archivos JSON de prueba (usuarios, notas, evidencias)
│ │ ├── modules/ # Módulos de la app consola
│ │ │ ├── admin/ # Vistas para administrador
│ │ │ ├── qualifiers/ # Vistas para calificadores
│ │ │ ├── students/ # Vistas para estudiantes
│ │ │ └── login.py # Lógica de login en consola
│ │ ├── util/ # Utilidades y sesión
│ │ └── main.py # Punto de entrada de la app consola
│ │
│ ├── db/ # Módulo de base de datos
│ │ ├── models/ # Modelos de datos
│ │ ├── seeds/ # Datos semilla en JSON
│ │ ├── supabase/ # Integración con Supabase y esquema SQL
│ │ ├── db.py # Conexión principal DB
│ │ └── db.sql # Script SQL inicial
│ │
│ └── ui/ # Interfaz gráfica con Flet
│ └── src/
│ ├── assets/ # Recursos gráficos (iconos, splash)
│ ├── components/ # Componentes reutilizables (CRUD)
│ ├── repositories/ # Repositorios de datos (auth, preguntas, resultados)
│ ├── services/ # Servicios externos (ej. cliente Supabase)
│ ├── state/ # Estado global (en construcción)
│ ├── storage/ # Almacenamiento temporal y persistente
│ │ ├── data/
│ │ └── temp/
│ ├── utils/ # Utilidades varias
│ ├── views/ # Vistas de la UI
│ │ ├── dashboard.py
│ │ ├── login.py
│ │ ├── nav_bar.py
│ │ ├── pruebas.py
│ │ └── prueba_panel.py
│ └── main.py # Punto de entrada de la app gráfica
│
├── img/ # Capturas de pantalla (README/docs)
│ ├── home.png
│ ├── login.png
│ └── prueba.png
│
├── packages/ # Dependencias externas / empaquetado futuro
├── .env # Variables de entorno
├── .gitignore # Exclusiones de git
├── pyproject.toml # Configuración del proyecto y dependencias
└── README.md # Documentación principal
```

---

## ▶️ Ejecución  

1. Clona este repositorio o descárgalo.  
2. Instala dependencias:  

```bash
pip install flet
```

3. Ejecuta el programa:
```
python main.py
```

## 🔑 Cuentas de prueba (mock)

Por ahora no hay base de datos real; el sistema permite el acceso con cuentas ficticias para pruebas de la UI:

Usuario: ```Andres1234```  
Contraseña: ```123456```