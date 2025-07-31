# 🚀 Guía de Instalación - Sistema HISMINSA

## 📋 Requisitos Previos

- Python 3.8 o superior
- Git instalado
- Conexión a internet

## 🔧 Instalación en Nueva PC

### 1. Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/hisminsa-analisis.git
cd hisminsa-analisis
```

### 2. Crear entorno virtual (recomendado)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Preparar archivos de datos

Necesitarás obtener los siguientes archivos maestros (no incluidos en el repositorio por seguridad):

- `MaestroPaciente.csv`
- `MaestroPersonal.csv`
- `MaestroRegistrador.csv`
- `codigos_descripcion.xlsx`

Colócalos en la carpeta raíz del proyecto.

### 5. Ejecutar la aplicación

```bash
streamlit run app_web_flexible.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

## 📁 Estructura de Archivos Necesaria

```
hisminsa-analisis/
│
├── app_web_flexible.py          # Aplicación principal
├── indicadores_adulto.py        # Módulo de indicadores curso de vida adulto
├── requirements.txt             # Dependencias
├── README.md                    # Documentación
├── codigos_descripcion.xlsx     # Descripciones (obtener por separado)
│
├── MaestroPaciente.csv    # Archivos maestros (obtener por separado)
├── MaestroPersonal.csv
├── MaestroRegistrador.csv
│
└── consolidados/                # Carpeta para tus archivos de datos
    └── consolidado-fecha.csv
```

## 🔑 Notas Importantes

1. **Archivos Maestros**: Por seguridad, los archivos maestros con datos sensibles NO se incluyen en el repositorio. Deberás obtenerlos por separado.

2. **Codificación**: Los archivos CSV deben estar en codificación Latin-1.

3. **Formato de Fechas**: Los consolidados deben seguir el formato `consolidado DD-MM-YYYY.csv`

## 🆘 Solución de Problemas

### Error: "No module named 'streamlit'"
```bash
pip install -r requirements.txt
```

### Error: "No se encontró el archivo MaestroPaciente..."
Asegúrate de copiar los archivos maestros en la carpeta del proyecto.

### La aplicación no carga descripciones
Verifica que `codigos_descripcion.xlsx` esté en la carpeta raíz y contenga las hojas correctas.

## 📞 Soporte

Si tienes problemas con la instalación, revisa que:
1. Python esté correctamente instalado: `python --version`
2. Pip esté actualizado: `pip install --upgrade pip`
3. Todos los archivos necesarios estén en su lugar