# Sistema de Análisis de Atenciones Médicas HISMINSA

## Descripción
Este programa permite unir y analizar los archivos de atenciones médicas del sistema HISMINSA. Une los datos del consolidado diario con los archivos maestros de pacientes, personal y registradores, permitiendo realizar diversos filtros y análisis.

## Características principales
- ✅ Une automáticamente los 4 archivos CSV
- ✅ Calcula la edad actual de los pacientes
- ✅ Filtros interactivos por:
  - Rango de edad
  - DNI del paciente
  - Código de diagnóstico
  - Establecimiento de salud
- ✅ Exportación de resultados filtrados
- ✅ Estadísticas generales automáticas

## Requisitos
- Python 3.6 o superior
- Librería pandas

## Instalación de requisitos
```bash
pip install pandas
```

## Uso del programa

### 1. Ejecutar el programa
```bash
python analizar_atenciones.py
```

### 2. El programa automáticamente:
- Cargará todos los archivos CSV
- Unirá los datos en una tabla completa
- Mostrará estadísticas generales
- Presentará un menú interactivo

### 3. Opciones del menú:
1. **Filtrar por rango de edad**: Busca pacientes entre edades específicas
2. **Filtrar por DNI**: Busca todas las atenciones de un paciente específico
3. **Filtrar por código**: Busca atenciones con códigos de diagnóstico específicos
4. **Filtrar por establecimiento**: Busca atenciones de un establecimiento específico
5. **Ver establecimientos**: Lista todos los establecimientos con sus IDs
6. **Exportar datos completos**: Guarda todos los datos unidos en un nuevo archivo
7. **Salir**: Termina el programa

## Estructura de archivos requerida
El programa espera encontrar los siguientes archivos en el mismo directorio:
```
📁 consolidado 01-07-2025 al 03-07-2025/
├── MaestroPaciente.csv
├── MaestroPersonal.csv
├── MaestroRegistrador.csv
├── 📁 01-07-2025/
│   └── consolidado 01-07-2025.csv
└── analizar_atenciones.py
```

## Ejemplos de uso

### Buscar atenciones de niños menores de 5 años:
- Seleccionar opción 1
- Edad mínima: 0
- Edad máxima: 5

### Buscar atenciones por DNI:
- Seleccionar opción 2
- Ingresar DNI: 46831573

### Buscar diagnósticos específicos:
- Seleccionar opción 3
- Ingresar código: I10 (para buscar hipertensión)

## Archivos de salida
Los resultados filtrados se guardan con el formato:
`filtrado_[tipo]_[criterio]_[fecha]_[hora].csv`

Ejemplo: `filtrado_edad_0_5_20250722_143025.csv`

## Notas importantes
- El programa maneja automáticamente la codificación UTF-8 con BOM
- Los resultados muestran un máximo de 10 registros en pantalla
- Todos los filtros son opcionales y se pueden exportar
- Los archivos exportados mantienen todas las columnas de datos