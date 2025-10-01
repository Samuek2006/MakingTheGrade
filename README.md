# 📘 Alcanzando la Nota 🎓  
**Nombre original:** *Making The Grade*  

Este proyecto es un **MVP desarrollado en Python con Flet**. Su objetivo es diseñar un sistema que permita al **Ministerio de Educación** estandarizar las pruebas de todos los colegios del país, asegurando consolidación, trazabilidad y facilidad de calificación.  

Actualmente está en transición desde una versión en consola hacia una **interfaz gráfica**, y en el futuro se conectará con una **base de datos** para manejo real de usuarios, resultados y reportes.  

---

## 🖼️ Capturas de Pantalla  

### 🔑 Login  
Permite a los usuarios iniciar sesión con credenciales.  
![Login](/img/login.png)  

### 🏠 Dashboard – Pruebas disponibles  
Lista las pruebas activas con navegación adaptada.  
![Dashboard](/img/home.png)  

### 📝 Presentación de Prueba  
Renderiza preguntas de selección múltiple con temporizador y navegación.  
![Prueba](/img/prueba.png)  

---

## 📌 Características actuales  
- **Login gráfico** con campos de usuario y contraseña.  
- **Dashboard de pruebas** con tarjetas dinámicas (ejemplo: Lógica, Numérica, Verbal).  
- **Presentación de pruebas** con temporizador y opciones de respuesta seleccionables.  
- **Navegación modularizada**: login → dashboard → prueba.  
- **UI responsive**: diseño centrado, compatible con escritorio y dispositivos móviles.  

---

## 📌 Próximos pasos  
- Conexión con **base de datos** (SQLite o PostgreSQL).  
- Gestión de **roles de usuario** (estudiante, calificador, administrador).  
- Registro y consolidación de resultados.  
- Generación de reportes de notas y estadísticas.  

---

## 📂 Tecnologías utilizadas  
- **Python 3.11+**  
- **Flet** (para la interfaz gráfica)  
- (Próximamente) **SQLite/PostgreSQL** para persistencia  

---

## 📂 Estructura del Proyecto  

```
MAKINGTHEGRADE
├── views/
│ ├── login.py # Pantalla de login
│ ├── dashBoard.py # Dashboard principal
│ ├── prueba_panel.py # Presentación de prueba
│ └── navBar.py # Barra de navegación
├── main.py # Entry point
├── README.md # Documentación
└── docs/
└── screens/ # Capturas de pantalla
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

Usuario: ```demo```  
Contraseña: ```demo123```