# 🏥 Aplicación Web Interactiva HISMINSA

## Descripción
Aplicación web moderna con interfaz visual para analizar las atenciones médicas. Incluye tablas interactivas, filtros dinámicos y gráficos estadísticos.

## 🚀 INSTALACIÓN PASO A PASO

### 1. Instalar las librerías necesarias
Abre el CMD en la carpeta del proyecto y ejecuta:

```cmd
pip install streamlit pandas plotly
```

Este comando instalará:
- **Streamlit**: Framework para crear la aplicación web
- **Pandas**: Para manejo de datos (ya lo tienes)
- **Plotly**: Para gráficos interactivos

### 2. Ejecutar la aplicación
En el mismo CMD, ejecuta:

```cmd
streamlit run app_web_atenciones.py
```

### 3. La aplicación se abrirá automáticamente
- Se abrirá tu navegador web con la aplicación
- Si no se abre, ve a: http://localhost:8501

## 📱 CARACTERÍSTICAS DE LA APLICACIÓN

### Panel de Filtros (Barra lateral izquierda)
- **Establecimiento**: Filtra por centro de salud
- **Rango de Edad**: Define edad mínima y máxima
- **DNI**: Busca un paciente específico
- **Código de Diagnóstico**: Busca por código (ej: I10, J03)
- **Turno**: Mañana, Tarde o Noche
- **Género**: Masculino o Femenino
- **Profesional de Salud**: Filtra por quien atendió

### Métricas Principales (Parte superior)
- Total de atenciones
- Pacientes únicos
- Personal activo
- Edad promedio

### Pestañas de Contenido

#### 📊 Tabla de Datos
- **Tabla interactiva**: Ordena por cualquier columna
- **Selección de columnas**: Elige qué columnas mostrar
- **Búsqueda rápida**: Usa Ctrl+F en la tabla
- **Descarga**: Botón para exportar a CSV

#### 📈 Gráficos
- **Distribución por Turno**: Gráfico circular
- **Distribución por Género**: Gráfico de barras
- **Top 10 Diagnósticos**: Los más frecuentes
- **Distribución por Edad**: Histograma

#### 📋 Resumen
- Estadísticas generales
- Top 5 diagnósticos
- Resumen de datos filtrados

## 💡 TIPS DE USO

### Filtros Múltiples
Puedes combinar varios filtros al mismo tiempo:
1. Selecciona establecimiento 4768
2. Rango de edad: 0-5 años
3. Turno: Mañana
→ Verás solo niños menores de 5 años atendidos en la mañana en ese establecimiento

### Ordenar Datos
- Click en cualquier encabezado de columna para ordenar
- Click de nuevo para orden inverso

### Descargar Resultados
- Aplica los filtros deseados
- Ve a la pestaña "Tabla de Datos"
- Click en "📥 Descargar datos filtrados"

### Zoom en Gráficos
- Todos los gráficos son interactivos
- Haz zoom arrastrando el mouse
- Doble click para resetear el zoom

## 🔧 SOLUCIÓN DE PROBLEMAS

### Error: "streamlit is not recognized"
Solución: Instala streamlit con `pip install streamlit`

### La página no carga
Solución: 
1. Cierra con Ctrl+C en el CMD
2. Ejecuta nuevamente `streamlit run app_web_atenciones.py`

### Navegador no se abre
Solución: Abre manualmente http://localhost:8501

## 🎯 CASOS DE USO COMUNES

### Ver todas las atenciones de un paciente
1. Ingresa el DNI en el filtro
2. Verás todas sus atenciones del día

### Análisis por grupos etarios
1. Usa el filtro de rango de edad
2. Revisa los gráficos para ver patrones

### Productividad del personal
1. Selecciona un profesional en el filtro
2. Ve cuántas atenciones realizó

### Análisis de diagnósticos
1. Ingresa parte del código (ej: "I" para cardíacos)
2. Analiza la distribución

## 📌 NOTAS IMPORTANTES

- La aplicación carga todos los datos en memoria
- Los cambios en filtros se aplican instantáneamente
- Puedes tener múltiples pestañas del navegador abiertas
- Para cerrar: Presiona Ctrl+C en el CMD

## 🚪 PARA SALIR
1. En el navegador: Cierra la pestaña
2. En el CMD: Presiona Ctrl+C
3. Confirma con 'Y' si te lo pide