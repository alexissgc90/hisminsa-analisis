# Sistema de Análisis de Atenciones HISMINSA

## 📋 Descripción
Sistema web interactivo para analizar atenciones médicas del sistema HISMINSA. Permite cargar múltiples archivos consolidados, unirlos con archivos maestros y realizar análisis con filtros avanzados.

## 🚀 Inicio Rápido

### Requisitos
```bash
pip install streamlit pandas plotly openpyxl
```

### Ejecutar la aplicación
```bash
python -m streamlit run app_web_flexible.py
```

## 📁 Estructura de Archivos

### Archivos Maestros (Obligatorios)
- `MaestroPaciente.csv` - Información de pacientes
- `MaestroPersonal.csv` - Información del personal médico
- `MaestroRegistrador.csv` - Información de registradores

### Archivos de Datos
- `01-07-2025/consolidado 01-07-2025.csv` - Atenciones diarias
- Puedes cargar múltiples consolidados de diferentes días

### Archivo de Descripciones (Opcional)
- `codigos_descripcion.xlsx` - Contiene descripciones de:
  - Códigos CIE-10
  - Nombres de establecimientos
  - Descripciones de UPS
  - Nombres de etnias

## 🎯 Características Principales

### 1. Carga Flexible de Archivos
- Arrastra y suelta múltiples consolidados
- Actualiza archivos maestros opcionalmente
- Procesamiento automático de datos

### 2. Filtros Avanzados
- Por rango de fechas
- Por edad (rango)
- Por DNI del paciente
- Por código de diagnóstico
- Por establecimiento
- Por turno y género
- Por profesional de salud ✅

### 3. Visualizaciones
- Tabla interactiva con columnas personalizables
- Gráficos de distribución (turno, género, diagnósticos)
- Análisis temporal de tendencias
- Estadísticas automáticas

### 4. Columnas Disponibles
- **Datos básicos**: Fecha, DNI, nombre completo, edad detallada
- **Datos clínicos**: CIE-10 con descripción, tipo diagnóstico, valores lab
- **Medidas**: Peso, talla, hemoglobina, perímetro abdominal
- **Datos obstétricos**: FUR, FPP calculada
- **Personal**: Nombre completo, colegiatura
- **Registro**: Fechas de registro y modificación

### 5. Supervisión de Indicadores (ACTUALIZADO 🆕)
- **Múltiples Cursos de Vida**: Adulto (30-59 años), Joven (18-29 años) y Adulto Mayor (60+ años)
- **Indicadores Individuales**: 15-17 indicadores por curso de vida
- **Paquete de Atención Integral**: Verifica cumplimiento completo según edad
- **Visualización de DNIs**: Muestra pacientes que cumplen cada indicador
- **Supervisión detallada**: Revisa códigos específicos por DNI seleccionado
- **Estadísticas en tiempo real**: Porcentaje de cumplimiento y clasificación

### 6. Exportación
- Descarga de datos filtrados en formato CSV
- Descarga de reportes de indicadores
- Mantiene codificación latin-1 para caracteres especiales

## 🔧 Solución de Problemas

### Error: "No module named 'openpyxl'"
```bash
pip install openpyxl
```

### No se muestran las descripciones
1. Verifica que existe `codigos_descripcion.xlsx`
2. Ve a la pestaña "🔍 Diagnóstico Descripciones"
3. Revisa que las hojas tengan los nombres correctos: CIE10, Establecimientos, UPS, Etnias

### Error de codificación
Los archivos usan codificación latin-1 para manejar caracteres como Ñ

## 📊 Uso Típico

1. **Análisis mensual**: Carga todos los consolidados del mes
2. **Búsqueda de paciente**: Filtra por DNI para ver historial
3. **Análisis de productividad**: Filtra por profesional
4. **Identificar tendencias**: Usa análisis temporal para ver patrones
5. **Supervisión de indicadores**: Ve a la pestaña "🎯 Indicadores" para verificar cumplimiento
6. **Auditoría de paquetes**: Analiza qué adultos, jóvenes o adultos mayores tienen su paquete de atención completo

## 🛠️ Estructura del Código

- **app_web_flexible.py**: Aplicación principal con Streamlit
- **indicadores_adulto.py**: Definiciones y lógica de indicadores del curso de vida adulto
- **indicadores_joven.py**: Definiciones y lógica de indicadores del curso de vida joven
- **indicadores_adulto_mayor.py**: Definiciones y lógica de indicadores del curso de vida adulto mayor
- Usa `session_state` para mantener datos entre interacciones
- Caché inteligente para evitar recargas innecesarias
- Manejo robusto de errores y tipos de datos

## 📝 Notas Importantes

- Los archivos maestros se cargan del directorio por defecto
- Las descripciones se cargan una sola vez y se cachean
- La aplicación maneja automáticamente las conversiones de tipos de datos
- Los filtros se aplican en tiempo real sin recargar datos

## 👤 Autor
Sistema desarrollado para el análisis de datos HISMINSA

---
Para más detalles, revisa los archivos de documentación adicionales en la carpeta.