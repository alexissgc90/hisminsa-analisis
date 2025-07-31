#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicación Web FLEXIBLE - Sistema de Análisis de Atenciones Médicas HISMINSA
Permite cargar consolidados y opcionalmente actualizar archivos maestros
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import io
import warnings
import base64
import json
warnings.filterwarnings('ignore', category=UserWarning)

# Importar módulos de indicadores
from indicadores_adulto import (
    INDICADORES_ADULTO, 
    PAQUETE_INTEGRAL_ADULTO,
    verificar_cumplimiento_indicador as verificar_indicador_adulto,
    calcular_estadisticas_indicador as calcular_stats_adulto,
    verificar_paquete_integral as verificar_paquete_adulto
)

from indicadores_joven import (
    INDICADORES_JOVEN,
    PAQUETE_INTEGRAL_JOVEN,
    verificar_cumplimiento_indicador as verificar_indicador_joven,
    calcular_estadisticas_indicador as calcular_stats_joven,
    verificar_paquete_integral as verificar_paquete_joven
)

from indicadores_adulto_mayor import (
    INDICADORES_ADULTO_MAYOR,
    PAQUETE_INTEGRAL_ADULTO_MAYOR,
    verificar_cumplimiento_indicador as verificar_indicador_adulto_mayor,
    calcular_estadisticas_indicador as calcular_stats_adulto_mayor,
    verificar_paquete_integral as verificar_paquete_adulto_mayor
)

# Configuración de la página
st.set_page_config(
    page_title="HISMINSA - Análisis Flexible",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #0066cc;
        color: white;
    }
    div[data-testid="metric-container"] {
        background-color: #f0f2f6;
        border: 1px solid #e0e0e0;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .archivo-status {
        padding: 0.5rem;
        border-radius: 0.3rem;
        margin: 0.2rem 0;
    }
    .archivo-ok {
        background-color: #d4edda;
        color: #155724;
    }
    .archivo-nuevo {
        background-color: #cce5ff;
        color: #004085;
    }
    .archivo-falta {
        background-color: #f8d7da;
        color: #721c24;
    }
    section[data-testid="stFileUploadDropzone"] {
        background-color: #f0f8ff;
        border: 2px dashed #4CAF50;
        border-radius: 10px;
        padding: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar estado de sesión
if 'datos_cargados' not in st.session_state:
    st.session_state.datos_cargados = False
if 'df_completo' not in st.session_state:
    st.session_state.df_completo = None
if 'archivos_maestros_cargados' not in st.session_state:
    st.session_state.archivos_maestros_cargados = False
if 'maestros_origen' not in st.session_state:
    st.session_state.maestros_origen = 'directorio'  # 'directorio' o 'subidos'
if 'df_pacientes' not in st.session_state:
    st.session_state.df_pacientes = None
if 'df_personal' not in st.session_state:
    st.session_state.df_personal = None
if 'df_registradores' not in st.session_state:
    st.session_state.df_registradores = None
if 'descripciones_cargadas' not in st.session_state:
    st.session_state.descripciones_cargadas = False
if 'cie10_dict' not in st.session_state:
    st.session_state.cie10_dict = {}
if 'estab_dict' not in st.session_state:
    st.session_state.estab_dict = {}
if 'ups_dict' not in st.session_state:
    st.session_state.ups_dict = {}
if 'etnia_dict' not in st.session_state:
    st.session_state.etnia_dict = {}

def verificar_archivos_directorio():
    """Verifica qué archivos maestros están disponibles en el directorio"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    archivos_estado = {
        'MaestroPaciente.csv': os.path.exists(os.path.join(base_path, 'MaestroPaciente.csv')),
        'MaestroPersonal.csv': os.path.exists(os.path.join(base_path, 'MaestroPersonal.csv')),
        'MaestroRegistrador.csv': os.path.exists(os.path.join(base_path, 'MaestroRegistrador.csv'))
    }
    return archivos_estado

def cargar_descripciones(mostrar_mensajes=False):
    """Carga las descripciones de códigos desde el archivo Excel"""
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        archivo_desc = os.path.join(base_path, 'codigos_descripcion.xlsx')
        
        if not os.path.exists(archivo_desc):
            if mostrar_mensajes:
                st.warning(f"No se encontró el archivo: {archivo_desc}")
            return {}, {}, {}, {}
        
        # Primero verificar si tenemos openpyxl instalado
        try:
            import openpyxl
        except ImportError:
            if mostrar_mensajes:
                st.error("❌ Necesitas instalar openpyxl: pip install openpyxl")
            return {}, {}, {}, {}
        
        # Leer el archivo Excel y obtener las hojas disponibles
        try:
            xl_file = pd.ExcelFile(archivo_desc, engine='openpyxl')
            hojas_disponibles = xl_file.sheet_names
            if mostrar_mensajes:
                st.info(f"📋 Hojas encontradas en el archivo: {', '.join(hojas_disponibles)}")
        except Exception as e:
            if mostrar_mensajes:
                st.error(f"❌ Error al abrir el archivo Excel: {str(e)}")
            return {}, {}, {}, {}
        
        # Leer cada hoja del Excel
        cie10_dict = {}
        estab_dict = {}
        ups_dict = {}
        etnia_dict = {}
        
        # Función para corregir la codificación de caracteres
        def fix_encoding(text):
            """Corrige problemas de codificación UTF-8/Latin-1"""
            if pd.isna(text):
                return text
            
            text = str(text)
            
            # Intentar corregir la codificación
            try:
                # Si el texto contiene caracteres típicos de mala codificación
                if 'Ã' in text or 'Â' in text:
                    # Intentar recodificar de latin-1 a utf-8
                    try:
                        text_bytes = text.encode('latin-1', errors='ignore')
                        text_fixed = text_bytes.decode('utf-8', errors='ignore')
                        # Solo usar el texto corregido si no tiene caracteres de reemplazo
                        if '�' not in text_fixed:
                            return text_fixed
                    except:
                        pass
            except:
                pass
            
            return text
        
        # Intentar leer CIE10 - buscar también con nombre alternativo
        hojas_cie = [h for h in hojas_disponibles if 'CIE' in h.upper()]
        if hojas_cie:
            try:
                df_cie10 = pd.read_excel(archivo_desc, sheet_name=hojas_cie[0], engine='openpyxl')
                if len(df_cie10.columns) >= 2:
                    # Limpiar espacios y corregir codificación
                    codigos = df_cie10.iloc[:, 0].astype(str).str.strip()
                    descripciones = df_cie10.iloc[:, 1].apply(fix_encoding)
                    cie10_dict = dict(zip(codigos, descripciones))
                    if mostrar_mensajes:
                        st.success(f"✅ CIE10 cargado: {len(cie10_dict)} códigos")
            except Exception as e:
                if mostrar_mensajes:
                    st.warning(f"⚠️ Error al leer hoja CIE10: {str(e)}")
        
        # Intentar leer Establecimientos - buscar con nombre alternativo
        hojas_estab = [h for h in hojas_disponibles if 'ESTABLECIMIENTO' in h.upper()]
        if hojas_estab:
            try:
                df_estab = pd.read_excel(archivo_desc, sheet_name=hojas_estab[0], engine='openpyxl')
                if len(df_estab.columns) >= 2:
                    # Limpiar espacios y corregir codificación
                    ids = df_estab.iloc[:, 0].astype(str).str.strip()
                    nombres = df_estab.iloc[:, 1].apply(fix_encoding)
                    estab_dict = dict(zip(ids, nombres))
                    if mostrar_mensajes:
                        st.success(f"✅ Establecimientos cargado: {len(estab_dict)} registros")
            except Exception as e:
                if mostrar_mensajes:
                    st.warning(f"⚠️ Error al leer hoja Establecimientos: {str(e)}")
        
        # Intentar leer UPS - buscar con nombre alternativo
        hojas_ups = [h for h in hojas_disponibles if 'UPS' in h.upper()]
        if hojas_ups:
            try:
                df_ups = pd.read_excel(archivo_desc, sheet_name=hojas_ups[0], engine='openpyxl')
                if len(df_ups.columns) >= 2:
                    # Limpiar espacios y corregir codificación
                    ids = df_ups.iloc[:, 0].astype(str).str.strip()
                    descripciones = df_ups.iloc[:, 1].apply(fix_encoding)
                    ups_dict = dict(zip(ids, descripciones))
                    if mostrar_mensajes:
                        st.success(f"✅ UPS cargado: {len(ups_dict)} servicios")
            except Exception as e:
                if mostrar_mensajes:
                    st.warning(f"⚠️ Error al leer hoja UPS: {str(e)}")
        
        # Intentar leer Etnias - buscar con nombre alternativo
        hojas_etnia = [h for h in hojas_disponibles if 'ETNIA' in h.upper()]
        if hojas_etnia:
            try:
                df_etnia = pd.read_excel(archivo_desc, sheet_name=hojas_etnia[0], engine='openpyxl')
                if len(df_etnia.columns) >= 2:
                    # Convertir a int solo si es posible
                    try:
                        ids = df_etnia.iloc[:, 0].astype(int)
                        descripciones = df_etnia.iloc[:, 1].apply(fix_encoding)
                        etnia_dict = dict(zip(ids, descripciones))
                    except:
                        ids = df_etnia.iloc[:, 0].astype(str).str.strip()
                        descripciones = df_etnia.iloc[:, 1].apply(fix_encoding)
                        etnia_dict = dict(zip(ids, descripciones))
                    if mostrar_mensajes:
                        st.success(f"✅ Etnias cargado: {len(etnia_dict)} etnias")
            except Exception as e:
                if mostrar_mensajes:
                    st.warning(f"⚠️ Error al leer hoja Etnias: {str(e)}")
        
        return cie10_dict, estab_dict, ups_dict, etnia_dict
        
    except Exception as e:
        if mostrar_mensajes:
            st.warning(f"No se pudo cargar el archivo de descripciones: {str(e)}")
        return {}, {}, {}, {}

@st.cache_data
def cargar_archivos_maestros_directorio():
    """Carga los archivos maestros desde el directorio"""
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        # Cargar archivos maestros
        df_pacientes = pd.read_csv(os.path.join(base_path, 'MaestroPaciente.csv'), encoding='latin-1')
        df_personal = pd.read_csv(os.path.join(base_path, 'MaestroPersonal.csv'), encoding='latin-1')
        df_registradores = pd.read_csv(os.path.join(base_path, 'MaestroRegistrador.csv'), encoding='latin-1')
        
        # Renombrar columnas
        pacientes_cols = {col: f'pac_{col}' for col in df_pacientes.columns if col != 'Id_Paciente'}
        personal_cols = {col: f'per_{col}' for col in df_personal.columns if col != 'Id_Personal'}
        registrador_cols = {col: f'reg_{col}' for col in df_registradores.columns if col != 'Id_Registrador'}
        
        df_pacientes = df_pacientes.rename(columns=pacientes_cols)
        df_personal = df_personal.rename(columns=personal_cols)
        df_registradores = df_registradores.rename(columns=registrador_cols)
        
        return df_pacientes, df_personal, df_registradores, True
    except Exception as e:
        return None, None, None, str(e)

def procesar_archivos_maestros_subidos(archivo_pacientes, archivo_personal, archivo_registradores):
    """Procesa archivos maestros subidos por el usuario"""
    try:
        # Leer archivos
        df_pacientes = pd.read_csv(archivo_pacientes, encoding='latin-1') if archivo_pacientes else None
        df_personal = pd.read_csv(archivo_personal, encoding='latin-1') if archivo_personal else None
        df_registradores = pd.read_csv(archivo_registradores, encoding='latin-1') if archivo_registradores else None
        
        # Si falta algún archivo, cargar del directorio
        if df_pacientes is None or df_personal is None or df_registradores is None:
            df_pac_dir, df_per_dir, df_reg_dir, _ = cargar_archivos_maestros_directorio()
            if df_pacientes is None:
                df_pacientes = df_pac_dir
            if df_personal is None:
                df_personal = df_per_dir
            if df_registradores is None:
                df_registradores = df_reg_dir
        
        # Renombrar columnas
        if df_pacientes is not None:
            pacientes_cols = {col: f'pac_{col}' for col in df_pacientes.columns if col != 'Id_Paciente'}
            df_pacientes = df_pacientes.rename(columns=pacientes_cols)
        
        if df_personal is not None:
            personal_cols = {col: f'per_{col}' for col in df_personal.columns if col != 'Id_Personal'}
            df_personal = df_personal.rename(columns=personal_cols)
        
        if df_registradores is not None:
            registrador_cols = {col: f'reg_{col}' for col in df_registradores.columns if col != 'Id_Registrador'}
            df_registradores = df_registradores.rename(columns=registrador_cols)
        
        return df_pacientes, df_personal, df_registradores, True
    except Exception as e:
        return None, None, None, str(e)

def procesar_consolidados(archivos_subidos, df_pacientes, df_personal, df_registradores, mostrar_mensajes=True):
    """Procesa múltiples archivos consolidados"""
    dfs_consolidados = []
    archivos_procesados = []
    errores = []
    
    for archivo in archivos_subidos:
        try:
            # Leer el archivo consolidado
            df_temp = pd.read_csv(archivo, encoding='latin-1')
            
            # Extraer fecha del nombre del archivo si es posible
            nombre_archivo = archivo.name
            fecha_archivo = None
            
            # Intentar extraer fecha del nombre (formato: consolidado DD-MM-YYYY.csv)
            import re
            match = re.search(r'(\d{2}-\d{2}-\d{4})', nombre_archivo)
            if match:
                fecha_str = match.group(1)
                fecha_archivo = pd.to_datetime(fecha_str, format='%d-%m-%Y')
            
            # Si tiene columna Fecha_Atencion, usarla; si no, usar la fecha extraída
            if 'Fecha_Atencion' not in df_temp.columns and fecha_archivo:
                df_temp['Fecha_Atencion'] = fecha_archivo
            
            dfs_consolidados.append(df_temp)
            archivos_procesados.append(nombre_archivo)
            
        except Exception as e:
            errores.append(f"Error en {archivo.name}: {str(e)}")
    
    if not dfs_consolidados:
        return None, archivos_procesados, errores
    
    # Combinar todos los consolidados
    df_consolidado_total = pd.concat(dfs_consolidados, ignore_index=True)
    
    # CORRECCIÓN: Convertir IDs a string para evitar problemas de tipos de datos
    # Convertir columnas ID a string en el consolidado
    for col in ['Id_Paciente', 'Id_Personal', 'Id_Registrador']:
        if col in df_consolidado_total.columns:
            df_consolidado_total[col] = df_consolidado_total[col].astype(str).str.replace('.0', '', regex=False)
    
    # Convertir columnas ID a string en los archivos maestros
    df_pacientes = df_pacientes.copy()
    df_personal = df_personal.copy()
    df_registradores = df_registradores.copy()
    
    df_pacientes['Id_Paciente'] = df_pacientes['Id_Paciente'].astype(str).str.replace('.0', '', regex=False)
    df_personal['Id_Personal'] = df_personal['Id_Personal'].astype(str).str.replace('.0', '', regex=False)
    df_registradores['Id_Registrador'] = df_registradores['Id_Registrador'].astype(str).str.replace('.0', '', regex=False)
    
    # Unir con los archivos maestros
    df_completo = df_consolidado_total.copy()
    df_completo = pd.merge(df_completo, df_pacientes, on='Id_Paciente', how='left')
    df_completo = pd.merge(df_completo, df_personal, on='Id_Personal', how='left')
    df_completo = pd.merge(df_completo, df_registradores, on='Id_Registrador', how='left')
    
    # Calcular edad y crear columnas adicionales
    df_completo['pac_Fecha_Nacimiento'] = pd.to_datetime(df_completo['pac_Fecha_Nacimiento'], errors='coerce')
    df_completo['Fecha_Atencion'] = pd.to_datetime(df_completo['Fecha_Atencion'], errors='coerce')
    df_completo['edad_anos'] = ((df_completo['Fecha_Atencion'] - df_completo['pac_Fecha_Nacimiento']).dt.days / 365.25).round(1)
    
    # Calcular edad en años, meses y días
    def calcular_edad_detallada(fecha_nac, fecha_aten):
        if pd.isna(fecha_nac) or pd.isna(fecha_aten):
            return "N/A"
        años = fecha_aten.year - fecha_nac.year
        meses = fecha_aten.month - fecha_nac.month
        dias = fecha_aten.day - fecha_nac.day
        
        if dias < 0:
            meses -= 1
            dias += 30
        if meses < 0:
            años -= 1
            meses += 12
            
        return f"{años}a {meses}m {dias}d"
    
    df_completo['edad_detallada'] = df_completo.apply(
        lambda row: calcular_edad_detallada(row['pac_Fecha_Nacimiento'], row['Fecha_Atencion']), 
        axis=1
    )
    
    df_completo['Paciente_Completo'] = df_completo['pac_Apellido_Paterno_Paciente'].fillna('') + ' ' + \
                                      df_completo['pac_Apellido_Materno_Paciente'].fillna('') + ', ' + \
                                      df_completo['pac_Nombres_Paciente'].fillna('')
    
    df_completo['Personal_Completo'] = df_completo['per_Apellido_Paterno_Personal'].fillna('') + ' ' + \
                                      df_completo['per_Apellido_Materno_Personal'].fillna('') + ', ' + \
                                      df_completo['per_Nombres_Personal'].fillna('')
    
    df_completo['Turno_Desc'] = df_completo['Id_Turno'].map({1: 'Mañana', 2: 'Tarde', 3: 'Noche'})
    
    # Descripción de condición de establecimiento y servicio
    condicion_map = {'N': 'Nuevo', 'C': 'Continuador', 'R': 'Reingresante'}
    df_completo['Condicion_Establecimiento_Desc'] = df_completo['Id_Condicion_Establecimiento'].map(condicion_map)
    df_completo['Condicion_Servicio_Desc'] = df_completo['Id_Condicion_Servicio'].map(condicion_map)
    
    # Formatear fechas
    df_completo['Fecha_Formato'] = df_completo['Fecha_Atencion'].dt.strftime('%d/%m/%Y')
    df_completo['Fecha_Nacimiento_Formato'] = df_completo['pac_Fecha_Nacimiento'].dt.strftime('%d/%m/%Y')
    
    # Procesar FUR y calcular FPP
    df_completo['Fecha_Ultima_Regla'] = pd.to_datetime(df_completo['Fecha_Ultima_Regla'], errors='coerce')
    df_completo['FUR_Formato'] = df_completo['Fecha_Ultima_Regla'].dt.strftime('%d/%m/%Y')
    
    # Calcular FPP (Fecha Probable de Parto) = FUR + 280 días
    df_completo['FPP'] = df_completo['Fecha_Ultima_Regla'] + pd.Timedelta(days=280)
    df_completo['FPP_Formato'] = df_completo['FPP'].dt.strftime('%d/%m/%Y')
    
    # Formatear fechas de registro y modificación
    df_completo['Fecha_Registro'] = pd.to_datetime(df_completo['Fecha_Registro'], errors='coerce')
    df_completo['Fecha_Modificacion'] = pd.to_datetime(df_completo['Fecha_Modificacion'], errors='coerce')
    df_completo['Fecha_Registro_Formato'] = df_completo['Fecha_Registro'].dt.strftime('%d/%m/%Y %H:%M')
    df_completo['Fecha_Modificacion_Formato'] = df_completo['Fecha_Modificacion'].dt.strftime('%d/%m/%Y %H:%M')
    
    # Formato de Lote-Página-Registro
    df_completo['Lote_Pag_Reg'] = df_completo['Lote'].astype(str) + '-' + \
                                   df_completo['Num_Pag'].astype(str) + '-' + \
                                   df_completo['Num_Reg'].astype(str)
    
    # Cargar descripciones desde el archivo Excel (usar caché si ya están cargadas)
    if not st.session_state.descripciones_cargadas:
        cie10_dict, estab_dict, ups_dict, etnia_dict = cargar_descripciones(mostrar_mensajes=True)
        st.session_state.cie10_dict = cie10_dict
        st.session_state.estab_dict = estab_dict
        st.session_state.ups_dict = ups_dict
        st.session_state.etnia_dict = etnia_dict
        st.session_state.descripciones_cargadas = True
    else:
        cie10_dict = st.session_state.cie10_dict
        estab_dict = st.session_state.estab_dict
        ups_dict = st.session_state.ups_dict
        etnia_dict = st.session_state.etnia_dict
    
    # Aplicar descripciones de CIE10
    if cie10_dict and len(cie10_dict) > 0:
        # Limpiar espacios y convertir a string
        df_completo['Codigo_Item_Clean'] = df_completo['Codigo_Item'].astype(str).str.strip().str.upper()
        
        # Crear diccionario limpio - ya vienen limpios desde cargar_descripciones
        cie10_dict_clean = {}
        for k, v in cie10_dict.items():
            key_clean = str(k).strip().upper()
            cie10_dict_clean[key_clean] = str(v)
        
        # Aplicar mapeo
        df_completo['CIE10_Descripcion'] = df_completo['Codigo_Item_Clean'].map(cie10_dict_clean)
        
        # Contar cuántos se mapearon exitosamente
        mapped_count = df_completo['CIE10_Descripcion'].notna().sum()
        total_count = len(df_completo)
        unique_codes = df_completo['Codigo_Item_Clean'].dropna().nunique()
        
        # Mostrar estadísticas de mapeo
        if mostrar_mensajes:
            st.info(f"📊 CIE10: {mapped_count}/{total_count} registros mapeados ({mapped_count/total_count*100:.1f}%), "
                   f"{unique_codes} códigos únicos")
        
        # Si hay muy pocos mapeos, mostrar algunos ejemplos para debug
        if mapped_count < total_count * 0.5:  # Menos del 50% mapeado
            sample_codes = list(df_completo['Codigo_Item_Clean'].dropna().unique()[:5])
            sample_keys = list(cie10_dict_clean.keys())[:5]
            if mostrar_mensajes:
                with st.expander("🔍 Ver detalles de mapeo CIE10"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Ejemplos de códigos en datos:**")
                        for code in sample_codes:
                            st.text(f"'{code}'")
                    with col2:
                        st.write("**Ejemplos en diccionario:**")
                        for key in sample_keys:
                            st.text(f"'{key}'")
        
        # Rellenar valores faltantes
        df_completo['CIE10_Descripcion'] = df_completo['CIE10_Descripcion'].fillna('Sin descripción')
    else:
        df_completo['CIE10_Descripcion'] = 'Sin archivo de descripciones'
    
    # Aplicar descripciones de Establecimientos
    if estab_dict and len(estab_dict) > 0:
        # Convertir ambos a string para el mapeo
        df_completo['Id_Establecimiento_Str'] = df_completo['Id_Establecimiento'].astype(str).str.strip()
        
        # Crear diccionario limpio - ya vienen limpios desde cargar_descripciones
        estab_dict_clean = {}
        for k, v in estab_dict.items():
            key_clean = str(k).strip()
            estab_dict_clean[key_clean] = str(v)
        
        # Aplicar mapeo
        df_completo['Establecimiento_Nombre'] = df_completo['Id_Establecimiento_Str'].map(estab_dict_clean)
        
        # Contar mapeos exitosos
        mapped_count = df_completo['Establecimiento_Nombre'].notna().sum()
        total_count = len(df_completo)
        unique_estab = df_completo['Id_Establecimiento_Str'].dropna().nunique()
        
        if mostrar_mensajes:
            st.info(f"🏥 Establecimientos: {mapped_count}/{total_count} registros mapeados ({mapped_count/total_count*100:.1f}%), "
                   f"{unique_estab} establecimientos únicos")
        
        df_completo['Establecimiento_Nombre'] = df_completo['Establecimiento_Nombre'].fillna('Sin nombre')
    else:
        df_completo['Establecimiento_Nombre'] = 'Sin archivo de descripciones'
    
    # Aplicar descripciones de UPS
    if ups_dict and len(ups_dict) > 0:
        # Convertir ambos a string para el mapeo
        df_completo['Id_Ups_Str'] = df_completo['Id_Ups'].astype(str).str.strip()
        
        # Crear diccionario limpio - ya vienen limpios desde cargar_descripciones
        ups_dict_clean = {}
        for k, v in ups_dict.items():
            key_clean = str(k).strip()
            ups_dict_clean[key_clean] = str(v)
        
        # Aplicar mapeo
        df_completo['UPS_Descripcion'] = df_completo['Id_Ups_Str'].map(ups_dict_clean)
        
        # Contar mapeos exitosos
        mapped_count = df_completo['UPS_Descripcion'].notna().sum()
        total_count = len(df_completo)
        unique_ups = df_completo['Id_Ups_Str'].dropna().nunique()
        
        if mostrar_mensajes:
            st.info(f"🏪 UPS: {mapped_count}/{total_count} registros mapeados ({mapped_count/total_count*100:.1f}%), "
                   f"{unique_ups} servicios únicos")
        
        df_completo['UPS_Descripcion'] = df_completo['UPS_Descripcion'].fillna('Sin descripción')
    else:
        df_completo['UPS_Descripcion'] = 'Sin archivo de descripciones'
    
    # Aplicar descripciones de Etnias
    if etnia_dict:
        df_completo['Etnia_Desc'] = df_completo['pac_Id_Etnia'].map(etnia_dict).fillna('No especificado')
    else:
        # Usar diccionario básico si no hay archivo
        etnia_map = {
            40: 'Mestizo',
            58: 'Otros'
        }
        df_completo['Etnia_Desc'] = df_completo['pac_Id_Etnia'].map(etnia_map).fillna('No especificado')
    
    return df_completo, archivos_procesados, errores

def crear_filtros_sidebar(df):
    """Crea los filtros en la barra lateral"""
    st.sidebar.header("🔍 Filtros de Búsqueda")
    
    # Filtro por rango de fechas
    st.sidebar.subheader("📅 Rango de Fechas")
    fechas_unicas = sorted(df['Fecha_Atencion'].dt.date.unique())
    
    if len(fechas_unicas) > 1:
        fecha_min = st.sidebar.date_input(
            "Fecha inicial:",
            value=fechas_unicas[0],
            min_value=fechas_unicas[0],
            max_value=fechas_unicas[-1]
        )
        fecha_max = st.sidebar.date_input(
            "Fecha final:",
            value=fechas_unicas[-1],
            min_value=fechas_unicas[0],
            max_value=fechas_unicas[-1]
        )
    else:
        fecha_min = fecha_max = fechas_unicas[0]
        st.sidebar.info(f"Solo hay datos del {fecha_min}")
    
    # Filtro por establecimiento
    # Crear diccionario de código -> nombre
    estab_codigo_nombre = {}
    for codigo in df['Id_Establecimiento'].unique():
        # Convertir código a string y limpiar espacios
        codigo_str = str(codigo).strip()
        nombre = df[df['Id_Establecimiento'] == codigo]['Establecimiento_Nombre'].iloc[0] if 'Establecimiento_Nombre' in df.columns else 'Sin nombre'
        estab_codigo_nombre[codigo_str] = f"{codigo_str} - {nombre}"
    
    # Crear lista de opciones con formato "código - nombre"
    establecimientos_display = ['Todos'] + [estab_codigo_nombre[codigo] for codigo in sorted(estab_codigo_nombre.keys())]
    establecimiento_display = st.sidebar.selectbox(
        "Establecimiento:",
        establecimientos_display
    )
    
    # Extraer el código seleccionado
    if establecimiento_display == 'Todos':
        establecimiento_sel = 'Todos'
    else:
        # Extraer y limpiar el código
        establecimiento_sel = establecimiento_display.split(' - ')[0].strip()
    
    # Filtro por rango de edad
    st.sidebar.subheader("Rango de Edad")
    col1, col2 = st.sidebar.columns(2)
    edad_min = col1.number_input("Mínima:", min_value=0, max_value=120, value=0)
    edad_max = col2.number_input("Máxima:", min_value=0, max_value=120, value=120)
    
    # Filtro por DNI
    dni_buscar = st.sidebar.text_input(
        "DNI del Paciente:",
        placeholder="Ej: 46831573"
    )
    
    # Filtro por código de diagnóstico
    codigo_buscar = st.sidebar.text_input(
        "Código de Diagnóstico:",
        placeholder="Ej: I10, J03"
    )
    
    # Filtro por turno
    turnos_opciones = ['Todos', 'Mañana', 'Tarde', 'Noche']
    turno_sel = st.sidebar.selectbox("Turno:", turnos_opciones)
    
    # Filtro por género
    generos = ['Todos', 'M', 'F']
    genero_sel = st.sidebar.selectbox("Género:", generos)
    
    # Filtro por profesional de salud
    profesionales = ['Todos'] + sorted(df['Personal_Completo'].dropna().unique().tolist())
    profesional_sel = st.sidebar.selectbox(
        "Profesional de Salud:",
        profesionales,
        key="profesional_filter"
    )
    
    return {
        'fecha_min': pd.to_datetime(fecha_min),
        'fecha_max': pd.to_datetime(fecha_max),
        'establecimiento': establecimiento_sel,
        'edad_min': edad_min,
        'edad_max': edad_max,
        'dni': dni_buscar,
        'codigo': codigo_buscar,
        'turno': turno_sel,
        'genero': genero_sel,
        'profesional': profesional_sel
    }

def aplicar_filtros(df, filtros):
    """Aplica los filtros seleccionados al dataframe"""
    df_filtrado = df.copy()
    
    # Filtro por fechas
    df_filtrado = df_filtrado[
        (df_filtrado['Fecha_Atencion'].dt.date >= filtros['fecha_min'].date()) & 
        (df_filtrado['Fecha_Atencion'].dt.date <= filtros['fecha_max'].date())
    ]
    
    # Filtro por establecimiento
    if filtros['establecimiento'] != 'Todos':
        # Convertir ambos valores a string para comparación
        df_filtrado = df_filtrado[df_filtrado['Id_Establecimiento'].astype(str).str.strip() == str(filtros['establecimiento']).strip()]
    
    # Filtro por edad
    df_filtrado = df_filtrado[
        (df_filtrado['edad_anos'] >= filtros['edad_min']) & 
        (df_filtrado['edad_anos'] <= filtros['edad_max'])
    ]
    
    # Filtro por DNI
    if filtros['dni']:
        df_filtrado = df_filtrado[df_filtrado['pac_Numero_Documento'] == filtros['dni']]
    
    # Filtro por código
    if filtros['codigo']:
        df_filtrado = df_filtrado[
            df_filtrado['Codigo_Item'].str.contains(filtros['codigo'], case=False, na=False)
        ]
    
    # Filtro por turno
    if filtros['turno'] != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Turno_Desc'] == filtros['turno']]
    
    # Filtro por género
    if filtros['genero'] != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['pac_Genero'] == filtros['genero']]
    
    # Filtro por profesional
    if filtros['profesional'] != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Personal_Completo'] == filtros['profesional']]
    
    return df_filtrado

def mostrar_metricas(df):
    """Muestra métricas principales"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Atenciones",
            f"{len(df):,}",
            help="Número total de atenciones en el período"
        )
    
    with col2:
        st.metric(
            "Pacientes Únicos",
            f"{df['Id_Paciente'].nunique():,}",
            help="Número de pacientes diferentes atendidos"
        )
    
    with col3:
        dias_datos = df['Fecha_Atencion'].dt.date.nunique()
        st.metric(
            "Días con Datos",
            f"{dias_datos}",
            help="Cantidad de días diferentes con atenciones"
        )
    
    with col4:
        promedio_diario = len(df) / dias_datos if dias_datos > 0 else 0
        st.metric(
            "Promedio Diario",
            f"{promedio_diario:.0f}",
            help="Promedio de atenciones por día"
        )

def mostrar_estado_maestros():
    """Muestra el estado de los archivos maestros"""
    archivos_estado = verificar_archivos_directorio()
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("**Estado de Archivos Maestros:**")
        
        if st.session_state.maestros_origen == 'directorio':
            st.markdown("📁 **Usando archivos del directorio**")
            for archivo, existe in archivos_estado.items():
                if existe:
                    st.markdown(f"<div class='archivo-status archivo-ok'>✅ {archivo}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='archivo-status archivo-falta'>❌ {archivo} (No encontrado)</div>", unsafe_allow_html=True)
        else:
            st.markdown("📤 **Usando archivos subidos**")
            st.markdown("<div class='archivo-status archivo-nuevo'>✅ Archivos maestros actualizados</div>", unsafe_allow_html=True)
    
    with col2:
        if all(archivos_estado.values()):
            st.success("✅ Sistema listo")
        else:
            st.warning("⚠️ Faltan archivos")
    
    with col3:
        # Mostrar estado de descripciones
        if st.session_state.descripciones_cargadas:
            total_desc = (len(st.session_state.cie10_dict) + 
                         len(st.session_state.estab_dict) + 
                         len(st.session_state.ups_dict) + 
                         len(st.session_state.etnia_dict))
            if total_desc > 0:
                st.info(f"📚 {total_desc} descripciones")
            else:
                st.warning("📚 Sin descripciones")

def seccion_carga_archivos():
    """Sección principal de carga de archivos"""
    tab1, tab2, tab3 = st.tabs(["📄 Consolidados", "🗂️ Archivos Maestros (Opcional)", "🔍 Diagnóstico Descripciones"])
    
    archivos_consolidados = None
    archivo_pacientes = None
    archivo_personal = None
    archivo_registradores = None
    
    with tab1:
        st.markdown("### 📄 Cargar Archivos Consolidados")
        st.info("Arrastra aquí los archivos consolidados de las atenciones diarias")
        
        archivos_consolidados = st.file_uploader(
            "Archivos consolidados CSV",
            type=['csv'],
            accept_multiple_files=True,
            key="consolidados"
        )
        
        if archivos_consolidados:
            st.success(f"✅ {len(archivos_consolidados)} archivo(s) consolidado(s) cargado(s)")
            with st.expander("Ver archivos"):
                for archivo in archivos_consolidados:
                    st.write(f"• {archivo.name}")
    
    with tab2:
        st.markdown("### 🗂️ Actualizar Archivos Maestros (Opcional)")
        st.warning("⚠️ Solo actualiza estos archivos si tienes versiones más recientes")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Pacientes**")
            archivo_pacientes = st.file_uploader(
                "MaestroPaciente",
                type=['csv'],
                key="pacientes"
            )
            if archivo_pacientes:
                st.success("✅ Actualizado")
        
        with col2:
            st.markdown("**Personal**")
            archivo_personal = st.file_uploader(
                "MaestroPersonal",
                type=['csv'],
                key="personal"
            )
            if archivo_personal:
                st.success("✅ Actualizado")
        
        with col3:
            st.markdown("**Registradores**")
            archivo_registradores = st.file_uploader(
                "MaestroRegistrador",
                type=['csv'],
                key="registradores"
            )
            if archivo_registradores:
                st.success("✅ Actualizado")
        
        if any([archivo_pacientes, archivo_personal, archivo_registradores]):
            st.info("📌 Los archivos maestros no cargados se tomarán del directorio")
    
    with tab3:
        st.markdown("### 🔍 Diagnóstico de Descripciones")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            if st.button("🔄 Recargar descripciones", key="reload_desc", type="secondary"):
                st.session_state.descripciones_cargadas = False
                st.rerun()
        
        # Mostrar información de las descripciones cargadas
        if st.session_state.descripciones_cargadas:
            # Métricas principales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("CIE10", f"{len(st.session_state.cie10_dict):,}", "códigos")
            with col2:
                st.metric("Establecimientos", f"{len(st.session_state.estab_dict)}", "registros")
            with col3:
                st.metric("UPS", f"{len(st.session_state.ups_dict)}", "servicios")
            with col4:
                st.metric("Etnias", f"{len(st.session_state.etnia_dict)}", "registros")
            
            st.markdown("---")
            
            # Muestras de datos
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📝 Ejemplos de CIE10:**")
                if st.session_state.cie10_dict:
                    sample_cie10 = list(st.session_state.cie10_dict.items())[:5]
                    for k, v in sample_cie10:
                        # Truncar descripción si es muy larga
                        desc = v[:60] + "..." if len(v) > 60 else v
                        st.text(f"{k} → {desc}")
                else:
                    st.warning("No hay códigos CIE10 cargados")
                
                st.markdown("**🏥 Ejemplos de Establecimientos:**")
                if st.session_state.estab_dict:
                    sample_estab = list(st.session_state.estab_dict.items())[:3]
                    for k, v in sample_estab:
                        desc = v[:40] + "..." if len(v) > 40 else v
                        st.text(f"{k} → {desc}")
                else:
                    st.warning("No hay establecimientos cargados")
            
            with col2:
                st.markdown("**🏪 Ejemplos de UPS:**")
                if st.session_state.ups_dict:
                    sample_ups = list(st.session_state.ups_dict.items())[:5]
                    for k, v in sample_ups:
                        desc = v[:60] + "..." if len(v) > 60 else v
                        st.text(f"{k} → {desc}")
                else:
                    st.warning("No hay UPS cargados")
                
                st.markdown("**👥 Ejemplos de Etnias:**")
                if st.session_state.etnia_dict:
                    sample_etnia = list(st.session_state.etnia_dict.items())[:3]
                    for k, v in sample_etnia:
                        st.text(f"{k} → {v}")
                else:
                    st.warning("No hay etnias cargadas")
            
            # Información adicional
            with st.expander("ℹ️ Información del archivo"):
                st.info("""
                **Archivo**: codigos_descripcion.xlsx
                
                **Hojas esperadas**:
                - CIE_DESCRIPCION o similar
                - ESTABLECIMIENTO_DESCRIPCION o similar
                - UPS_DESCRIPCION o similar
                - ETNIA_DESCRIPCION o similar
                
                **Nota**: El sistema busca hojas que contengan las palabras clave CIE, ESTABLECIMIENTO, UPS y ETNIA.
                """)
        else:
            st.info("""
            📚 **No hay descripciones cargadas**
            
            Las descripciones se cargarán automáticamente cuando proceses los archivos consolidados.
            
            **Requisitos**:
            - El archivo `codigos_descripcion.xlsx` debe estar en el mismo directorio
            - Debe contener las hojas con los códigos y descripciones
            """)
    
    return archivos_consolidados, archivo_pacientes, archivo_personal, archivo_registradores

def main():
    """Función principal de la aplicación"""
    # Título y descripción
    st.title("🏥 Sistema de Análisis Flexible HISMINSA")
    st.markdown("### Análisis de atenciones con carga flexible de archivos")
    
    # Mostrar estado de archivos maestros
    mostrar_estado_maestros()
    
    st.markdown("---")
    
    # Sección de carga de archivos
    archivos_consolidados, archivo_pacientes, archivo_personal, archivo_registradores = seccion_carga_archivos()
    
    # Botón de procesamiento
    if archivos_consolidados:
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col2:
            procesar = st.button("🔄 Procesar Archivos", type="primary", use_container_width=True)
        
        if procesar:
            with st.spinner('Procesando archivos...'):
                # Determinar origen de archivos maestros
                if any([archivo_pacientes, archivo_personal, archivo_registradores]):
                    # Usar archivos subidos (y complementar con directorio si falta alguno)
                    df_pacientes, df_personal, df_registradores, resultado = procesar_archivos_maestros_subidos(
                        archivo_pacientes, archivo_personal, archivo_registradores
                    )
                    st.session_state.maestros_origen = 'subidos'
                else:
                    # Usar archivos del directorio
                    df_pacientes, df_personal, df_registradores, resultado = cargar_archivos_maestros_directorio()
                    st.session_state.maestros_origen = 'directorio'
                
                if df_pacientes is not None:
                    st.session_state.df_pacientes = df_pacientes
                    st.session_state.df_personal = df_personal
                    st.session_state.df_registradores = df_registradores
                    st.session_state.archivos_maestros_cargados = True
                    
                    # Procesar consolidados
                    df_completo, archivos_procesados, errores = procesar_consolidados(
                        archivos_consolidados,
                        df_pacientes,
                        df_personal,
                        df_registradores,
                        mostrar_mensajes=True
                    )
                    
                    if df_completo is not None:
                        st.session_state.df_completo = df_completo
                        st.session_state.datos_cargados = True
                        st.success(f"✅ Procesamiento completado: {len(archivos_procesados)} archivos")
                        
                        if errores:
                            with st.expander("Ver advertencias"):
                                for error in errores:
                                    st.warning(error)
                        
                        # Recargar para mostrar resultados
                        st.rerun()
                    else:
                        st.error("Error al procesar consolidados")
                        for error in errores:
                            st.error(error)
                else:
                    st.error(f"Error al cargar archivos maestros: {resultado}")
    
    # Mostrar análisis si hay datos cargados
    if st.session_state.datos_cargados and st.session_state.df_completo is not None:
        df = st.session_state.df_completo
        
        # Crear filtros
        filtros = crear_filtros_sidebar(df)
        
        # Aplicar filtros
        df_filtrado = aplicar_filtros(df, filtros)
        
        # Mostrar métricas
        st.markdown("---")
        mostrar_metricas(df_filtrado)
        
        # Crear tabs de análisis
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Tabla", "📈 Gráficos", "📅 Temporal", "📋 Resumen", "🎯 Indicadores"])
        
        with tab1:
            st.subheader("📊 Tabla de Atenciones")
            
            # Botón para mostrar todas las columnas
            if st.button("📋 Mostrar todas las columnas", type="secondary"):
                st.session_state['mostrar_todas'] = True
            elif st.button("🔧 Personalizar columnas", type="secondary"):
                st.session_state['mostrar_todas'] = False
            
            # Lista de todas las columnas disponibles
            todas_las_columnas = ['Fecha_Formato', 'Lote_Pag_Reg', 'Id_Establecimiento', 'Establecimiento_Nombre',
                                'pac_Numero_Documento', 'Paciente_Completo', 'Fecha_Nacimiento_Formato',
                                'edad_anos', 'edad_detallada', 'pac_Genero', 'Etnia_Desc',
                                'Codigo_Item', 'CIE10_Descripcion', 'Tipo_Diagnostico', 'Valor_Lab', 
                                'Id_Ups', 'UPS_Descripcion',
                                'Condicion_Establecimiento_Desc', 'Condicion_Servicio_Desc',
                                'Peso', 'Talla', 'Perimetro_Abdominal', 'Hemoglobina',
                                'FUR_Formato', 'FPP_Formato', 'Personal_Completo', 
                                'per_Numero_Colegiatura', 'Turno_Desc',
                                'Fecha_Registro_Formato', 'Fecha_Modificacion_Formato']
            
            # Si está activado mostrar todas o es la primera vez
            if st.session_state.get('mostrar_todas', False):
                columnas_mostrar = todas_las_columnas
                st.info("✅ Mostrando todas las columnas disponibles")
            else:
                # Organizar columnas por categorías
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Datos básicos:**")
                    basicas_sel = st.multiselect(
                        "Columnas básicas",
                        ['Fecha_Formato', 'Lote_Pag_Reg', 'Id_Establecimiento', 'Establecimiento_Nombre',
                         'pac_Numero_Documento', 'Paciente_Completo', 'Fecha_Nacimiento_Formato',
                         'edad_anos', 'edad_detallada', 'pac_Genero', 'Etnia_Desc'],
                        default=['Fecha_Formato', 'pac_Numero_Documento', 'Paciente_Completo', 'edad_detallada']
                    )
                
                with col2:
                    st.markdown("**Datos clínicos:**")
                    clinicas_sel = st.multiselect(
                        "Columnas clínicas",
                        ['Codigo_Item', 'CIE10_Descripcion', 'Tipo_Diagnostico', 'Valor_Lab', 
                         'Id_Ups', 'UPS_Descripcion',
                         'Condicion_Establecimiento_Desc', 'Condicion_Servicio_Desc',
                         'Peso', 'Talla', 'Perimetro_Abdominal', 'Hemoglobina',
                         'FUR_Formato', 'FPP_Formato'],
                        default=['Codigo_Item', 'CIE10_Descripcion', 'Tipo_Diagnostico']
                    )
                
                col3, col4 = st.columns(2)
                
                with col3:
                    st.markdown("**Personal y turno:**")
                    personal_sel = st.multiselect(
                        "Columnas de personal",
                        ['Personal_Completo', 'per_Numero_Colegiatura', 'Turno_Desc'],
                        default=['Personal_Completo']
                    )
                
                with col4:
                    st.markdown("**Registro:**")
                    registro_sel = st.multiselect(
                        "Columnas de registro",
                        ['Fecha_Registro_Formato', 'Fecha_Modificacion_Formato'],
                        default=[]
                    )
                
                # Combinar todas las columnas seleccionadas
                columnas_mostrar = basicas_sel + clinicas_sel + personal_sel + registro_sel
            
            if columnas_mostrar:
                columnas_existentes = [col for col in columnas_mostrar if col in df_filtrado.columns]
                
                # Configuración mejorada de columnas
                column_config = {
                    "Fecha_Formato": st.column_config.TextColumn("Fecha Atención", width="small"),
                    "Lote_Pag_Reg": st.column_config.TextColumn("Lote-Pág-Reg", width="small"),
                    "Id_Establecimiento": st.column_config.TextColumn("ID Estab.", width="small"),
                    "Establecimiento_Nombre": st.column_config.TextColumn("Nombre Establecimiento", width="medium"),
                    "pac_Numero_Documento": st.column_config.TextColumn("DNI", width="small"),
                    "Paciente_Completo": st.column_config.TextColumn("Paciente", width="medium"),
                    "Fecha_Nacimiento_Formato": st.column_config.TextColumn("F. Nacimiento", width="small"),
                    "edad_anos": st.column_config.NumberColumn("Edad", format="%.1f", width="small"),
                    "edad_detallada": st.column_config.TextColumn("Edad Detallada", width="small"),
                    "pac_Genero": st.column_config.TextColumn("Sexo", width="small"),
                    "Etnia_Desc": st.column_config.TextColumn("Etnia", width="small"),
                    "Codigo_Item": st.column_config.TextColumn("CIE-10", width="small"),
                    "CIE10_Descripcion": st.column_config.TextColumn("Diagnóstico", width="large"),
                    "Tipo_Diagnostico": st.column_config.TextColumn("Tipo Dx", width="small"),
                    "Valor_Lab": st.column_config.TextColumn("Lab", width="small"),
                    "Id_Ups": st.column_config.TextColumn("UPS", width="small"),
                    "UPS_Descripcion": st.column_config.TextColumn("Servicio", width="medium"),
                    "Condicion_Establecimiento_Desc": st.column_config.TextColumn("Cond. Estab.", width="small"),
                    "Condicion_Servicio_Desc": st.column_config.TextColumn("Cond. Serv.", width="small"),
                    "Peso": st.column_config.NumberColumn("Peso (kg)", format="%.1f", width="small"),
                    "Talla": st.column_config.NumberColumn("Talla (cm)", format="%.0f", width="small"),
                    "Perimetro_Abdominal": st.column_config.NumberColumn("P. Abdom.", format="%.0f", width="small"),
                    "Hemoglobina": st.column_config.NumberColumn("Hb", format="%.1f", width="small"),
                    "FUR_Formato": st.column_config.TextColumn("FUR", width="small"),
                    "FPP_Formato": st.column_config.TextColumn("FPP", width="small"),
                    "Personal_Completo": st.column_config.TextColumn("Personal", width="medium"),
                    "per_Numero_Colegiatura": st.column_config.TextColumn("Colegiatura", width="small"),
                    "Turno_Desc": st.column_config.TextColumn("Turno", width="small"),
                    "Fecha_Registro_Formato": st.column_config.TextColumn("F. Registro", width="small"),
                    "Fecha_Modificacion_Formato": st.column_config.TextColumn("F. Modif.", width="small")
                }
                
                # Ordenar por fecha descendente
                # Primero, verificar si necesitamos incluir Fecha_Atencion para ordenar
                if 'Fecha_Atencion' in df_filtrado.columns and 'Fecha_Atencion' not in columnas_existentes:
                    # Incluir temporalmente Fecha_Atencion para ordenar
                    columnas_con_fecha = columnas_existentes + ['Fecha_Atencion']
                    df_temp = df_filtrado[columnas_con_fecha].sort_values('Fecha_Atencion', ascending=False)
                    # Quitar Fecha_Atencion después de ordenar
                    df_mostrar = df_temp[columnas_existentes]
                elif 'Fecha_Formato' in columnas_existentes:
                    # Si tenemos Fecha_Formato, ordenar por el índice ya que está basado en Fecha_Atencion
                    df_mostrar = df_filtrado[columnas_existentes].sort_index(ascending=False)
                else:
                    # Si no hay columnas de fecha, mostrar tal cual
                    df_mostrar = df_filtrado[columnas_existentes]
                
                st.dataframe(
                    df_mostrar,
                    use_container_width=True,
                    height=500,
                    hide_index=True,
                    column_config=column_config
                )
                
                # Botón de descarga
                csv = df_filtrado[columnas_existentes].to_csv(index=False, encoding='latin-1')
                st.download_button(
                    label="📥 Descargar CSV",
                    data=csv.encode('latin-1'),
                    file_name=f'datos_hisminsa_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                    mime='text/csv'
                )
        
        with tab2:
            if len(df_filtrado) > 0:
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_turno = px.pie(
                        df_filtrado['Turno_Desc'].value_counts().reset_index(),
                        values='count',
                        names='Turno_Desc',
                        title="Distribución por Turno"
                    )
                    st.plotly_chart(fig_turno, use_container_width=True)
                
                with col2:
                    fig_genero = px.bar(
                        df_filtrado['pac_Genero'].value_counts().reset_index(),
                        x='pac_Genero',
                        y='count',
                        title="Distribución por Género"
                    )
                    st.plotly_chart(fig_genero, use_container_width=True)
                
                # Top diagnósticos
                top_diagnosticos = df_filtrado['Codigo_Item'].value_counts().head(10).reset_index()
                fig_diagnosticos = px.bar(
                    top_diagnosticos,
                    x='count',
                    y='Codigo_Item',
                    orientation='h',
                    title="Top 10 Diagnósticos"
                )
                st.plotly_chart(fig_diagnosticos, use_container_width=True)
        
        with tab3:
            if len(df_filtrado) > 0 and df_filtrado['Fecha_Atencion'].dt.date.nunique() > 1:
                # Tendencia temporal
                df_por_dia = df_filtrado.groupby(df_filtrado['Fecha_Atencion'].dt.date).size().reset_index(name='Atenciones')
                
                fig_temporal = px.line(
                    df_por_dia,
                    x='Fecha_Atencion',
                    y='Atenciones',
                    title="Tendencia de Atenciones",
                    markers=True
                )
                st.plotly_chart(fig_temporal, use_container_width=True)
                
                # Patrón semanal
                df_filtrado['Dia_Semana'] = df_filtrado['Fecha_Atencion'].dt.day_name()
                df_filtrado['Dia_Num'] = df_filtrado['Fecha_Atencion'].dt.dayofweek
                
                df_semanal = df_filtrado.groupby(['Dia_Num', 'Dia_Semana']).size().reset_index(name='Atenciones')
                df_semanal = df_semanal.sort_values('Dia_Num')
                
                fig_semanal = px.bar(
                    df_semanal,
                    x='Dia_Semana',
                    y='Atenciones',
                    title="Patrón Semanal de Atenciones"
                )
                st.plotly_chart(fig_semanal, use_container_width=True)
            else:
                st.info("📊 Se requieren datos de múltiples días para el análisis temporal")
        
        with tab4:
            st.subheader("📋 Resumen de Datos")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Período:**")
                if len(df_filtrado) > 0:
                    fecha_min = df_filtrado['Fecha_Atencion'].min()
                    fecha_max = df_filtrado['Fecha_Atencion'].max()
                    st.write(f"Desde: {fecha_min.strftime('%d/%m/%Y')}")
                    st.write(f"Hasta: {fecha_max.strftime('%d/%m/%Y')}")
            
            with col2:
                st.markdown("**Estadísticas:**")
                st.write(f"Registros: {len(df_filtrado):,}")
                st.write(f"Pacientes: {df_filtrado['Id_Paciente'].nunique():,}")
                st.write(f"Personal: {df_filtrado['Id_Personal'].nunique():,}")
            
            with col3:
                st.markdown("**Top Diagnósticos:**")
                if len(df_filtrado) > 0:
                    top_5 = df_filtrado['Codigo_Item'].value_counts().head(5)
                    for codigo, count in top_5.items():
                        st.write(f"{codigo}: {count}")
        
        with tab5:
            st.subheader("🎯 Supervisión de Indicadores por Curso de Vida")
            
            # Selector de curso de vida
            curso_vida = st.selectbox(
                "Seleccionar Curso de Vida:",
                ["Adulto (30-59 años)", "Joven (18-29 años)", "Adulto Mayor (60+ años)"],
                key="curso_vida_sel"
            )
            
            # Filtros de indicadores
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                # Selector de tipo de supervisión
                tipo_supervision = st.selectbox(
                    "Tipo de Supervisión:",
                    ["Indicadores Individuales", "Paquete de Atención Integral"],
                    key="tipo_supervision"
                )
            
            with col2:
                if tipo_supervision == "Indicadores Individuales":
                    # Selector de indicador según curso de vida
                    if curso_vida == "Adulto (30-59 años)":
                        indicador_opciones = {
                            "Evaluación Oral Completa": "evaluacion_oral",
                            "Tamizaje Violencia - WAST": "tamizaje_violencia",
                            "Tamizaje Agudeza Visual": "agudeza_visual",
                            "Valoración Nutricional": "valoracion_nutricional",
                            "Vacuna Influenza": "vacuna_influenza",
                            "Sintomáticos Respiratorios": "sintomaticos_respiratorios",
                            "Tamizaje VIH": "tamizaje_vih",
                            "Tamizaje Hepatitis B": "tamizaje_hepatitis_b",
                            "Tamizaje Alcohol y Drogas": "tamizaje_alcohol_drogas",
                            "Cáncer Cuello Uterino (Mujeres)": "cancer_cuello_uterino",
                            "Cáncer Próstata (Varones 50-59)": "cancer_prostata",
                            "Cáncer Colon y Recto (50-59)": "cancer_colon_recto",
                            "Trastornos Depresivos (PHQ-9)": "trastornos_depresivos",
                            "Plan Atención Integral Elaborado": "plan_atencion_elaborado",
                            "Plan Atención Integral Ejecutado": "plan_atencion_ejecutado",
                            "Consejería SSR": "consejeria_ssr"
                        }
                    elif curso_vida == "Joven (18-29 años)":
                        indicador_opciones = {
                            "Valoración Clínica Factores Riesgo": "valoracion_clinica_riesgo",
                            "Evaluación Nutricional": "evaluacion_nutricional",
                            "Tamizaje Violencia Intrafamiliar": "tamizaje_violencia",
                            "Tamizaje VIH": "tamizaje_vih",
                            "Consejería Integral": "consejeria_integral",
                            "Sintomático Respiratorio": "sintomatico_respiratorio",
                            "Evaluación Oral Completa": "evaluacion_oral",
                            "Consejería Prevención Cáncer": "consejeria_prevencion_cancer",
                            "Consejería SSR": "consejeria_ssr",
                            "Plan Atención Iniciado": "plan_atencion_iniciado",
                            "Plan Atención Ejecutado": "plan_atencion_ejecutado",
                            "Tamizaje Alcohol y Drogas": "tamizaje_alcohol_drogas",
                            "Tamizaje Depresión": "tamizaje_depresion",
                            "Acceso Anticonceptivos": "acceso_anticonceptivos"
                        }
                    else:  # Adulto Mayor
                        indicador_opciones = {
                            "Paquete Integral (Resumen)": "paquete_atencion_integral",
                            "VACAM - Valoración Clínica AM": "vacam",
                            "Tamizaje Agudeza Visual": "agudeza_visual",
                            "Tamizaje Integral Salud Mental": "tamizaje_salud_mental",
                            "Evaluación Oral Completa": "evaluacion_oral",
                            "Vacuna Neumococo": "vacuna_neumococo",
                            "Vacuna Influenza": "vacuna_influenza",
                            "Consejería Integral AM": "consejeria_integral",
                            "Valoración Clínica y Lab": "valoracion_clinica_lab",
                            "Vacuna COVID-19": "vacuna_covid19",
                            "Visita Familiar Integral": "visita_familiar",
                            "Cáncer Cuello Uterino (60-64)": "cancer_cuello_uterino",
                            "Cáncer Próstata (60-75)": "cancer_prostata",
                            "Cáncer Colon-Recto (60-70)": "cancer_colon_recto",
                            "Cáncer Piel (60-70)": "cancer_piel",
                            "Examen Clínico Mama (60-69)": "examen_clinico_mama",
                            "Sintomáticos Respiratorios": "sintomaticos_respiratorios"
                        }
                    
                    indicador_seleccionado = st.selectbox(
                        "Seleccionar Indicador:",
                        list(indicador_opciones.keys()),
                        key="indicador_sel"
                    )
                    indicador_key = indicador_opciones[indicador_seleccionado]
            
            with col3:
                # Botón de análisis
                if st.button("🔍 Analizar", type="primary", key="btn_analizar_indicador"):
                    st.session_state['analizar_indicador'] = True
            
            # División de la interfaz
            st.markdown("---")
            
            # Análisis según tipo seleccionado
            if tipo_supervision == "Indicadores Individuales" and st.session_state.get('analizar_indicador', False):
                # Seleccionar funciones e indicadores según curso de vida
                if curso_vida == "Adulto (30-59 años)":
                    verificar_indicador = verificar_indicador_adulto
                    INDICADORES = INDICADORES_ADULTO
                elif curso_vida == "Joven (18-29 años)":
                    verificar_indicador = verificar_indicador_joven
                    INDICADORES = INDICADORES_JOVEN
                else:  # Adulto Mayor
                    verificar_indicador = verificar_indicador_adulto_mayor
                    INDICADORES = INDICADORES_ADULTO_MAYOR
                
                # Verificar cumplimiento del indicador
                df_indicador = verificar_indicador(df_filtrado, indicador_key)
                
                if df_indicador is not None and not df_indicador.empty:
                    # Mostrar estadísticas
                    col1, col2, col3, col4 = st.columns(4)
                    
                    # Calcular estadísticas
                    dni_cumplen = df_indicador['pac_Numero_Documento'].nunique()
                    dni_total = df_filtrado[
                        (df_filtrado['edad_anos'] >= INDICADORES[indicador_key]['edad_min']) & 
                        (df_filtrado['edad_anos'] <= INDICADORES[indicador_key]['edad_max'])
                    ]['pac_Numero_Documento'].nunique()
                    
                    # Aplicar filtro de género si corresponde
                    if 'genero' in INDICADORES[indicador_key]:
                        dni_total = df_filtrado[
                            (df_filtrado['edad_anos'] >= INDICADORES[indicador_key]['edad_min']) & 
                            (df_filtrado['edad_anos'] <= INDICADORES[indicador_key]['edad_max']) &
                            (df_filtrado['pac_Genero'] == INDICADORES[indicador_key]['genero'])
                        ]['pac_Numero_Documento'].nunique()
                    
                    porcentaje_cumplimiento = (dni_cumplen / dni_total * 100) if dni_total > 0 else 0
                    
                    with col1:
                        st.metric("DNIs que cumplen", f"{dni_cumplen:,}")
                    with col2:
                        st.metric("DNIs elegibles", f"{dni_total:,}")
                    with col3:
                        st.metric("% Cumplimiento", f"{porcentaje_cumplimiento:.1f}%")
                    with col4:
                        clasificacion = "🟢 Satisfactorio" if porcentaje_cumplimiento >= 80 else \
                                       "🟡 Aceptable" if porcentaje_cumplimiento >= 70 else \
                                       "🟠 En proceso" if porcentaje_cumplimiento >= 60 else "🔴 Crítico"
                        st.metric("Estado", clasificacion)
                    
                    # Mostrar lista de DNIs con capacidad de selección
                    st.markdown("### 📋 DNIs que cumplen el indicador")
                    
                    # Selector de columnas adicionales
                    columnas_disponibles = {
                        'Fecha_Atencion': 'Última Fecha',
                        'Id_Establecimiento': 'Código Estab.',
                        'Establecimiento_Nombre': 'Nombre Estab.',
                        'Personal_Completo': 'Personal',
                        'UPS_Descripcion': 'Servicio',
                        'mes_Descripcion': 'Mes',
                        'Id_Turno': 'Turno'
                    }
                    
                    # Botones para seleccionar/quitar todas
                    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
                    with col_btn1:
                        if st.button("✅ Seleccionar todas", key="sel_todas_ind"):
                            st.session_state.columnas_indicador = list(columnas_disponibles.keys())
                            st.rerun()
                    with col_btn2:
                        if st.button("❌ Quitar todas", key="quit_todas_ind"):
                            st.session_state.columnas_indicador = []
                            st.rerun()
                    
                    # Usar el valor del session_state si existe
                    default_cols = st.session_state.get('columnas_indicador', [])
                    
                    columnas_seleccionadas = st.multiselect(
                        "Agregar columnas a la tabla:",
                        options=list(columnas_disponibles.keys()),
                        default=default_cols,
                        format_func=lambda x: columnas_disponibles[x],
                        key="columnas_indicador"
                    )
                    
                    # Crear DataFrame con información resumida
                    agg_dict = {
                        'Paciente_Completo': 'first',
                        'edad_anos': 'first',
                        'pac_Genero': 'first',
                        'Fecha_Atencion': 'count'
                    }
                    
                    # Agregar columnas seleccionadas al agregado
                    for col in columnas_seleccionadas:
                        if col == 'Fecha_Atencion':
                            agg_dict[col] = 'max'  # Última fecha
                        else:
                            agg_dict[col] = 'first'
                    
                    df_resumen_dni = df_indicador.groupby('pac_Numero_Documento').agg(agg_dict).reset_index()
                    
                    # Renombrar columnas base
                    columnas_rename = {
                        'pac_Numero_Documento': 'DNI',
                        'Paciente_Completo': 'Nombre Completo',
                        'edad_anos': 'Edad',
                        'pac_Genero': 'Género'
                    }
                    
                    # Manejar la columna de conteo de fecha
                    if 'Fecha_Atencion' in columnas_seleccionadas:
                        # Crear columna temporal para el conteo
                        df_resumen_dni['N° Registros'] = df_indicador.groupby('pac_Numero_Documento').size().values
                        # La fecha ya está como max
                        columnas_rename['Fecha_Atencion'] = 'Última Fecha'
                    else:
                        columnas_rename['Fecha_Atencion'] = 'N° Registros'
                    
                    # Agregar columnas seleccionadas al rename
                    for col in columnas_seleccionadas:
                        if col in columnas_disponibles and col != 'Fecha_Atencion':
                            columnas_rename[col] = columnas_disponibles[col]
                    
                    df_resumen_dni = df_resumen_dni.rename(columns=columnas_rename)
                    
                    # Selector de DNI para supervisión detallada
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        dni_supervisar = st.selectbox(
                            "Seleccionar DNI para supervisar códigos:",
                            ["Seleccione un DNI..."] + df_resumen_dni['DNI'].tolist(),
                            key="dni_supervisar"
                        )
                    
                    with col2:
                        if dni_supervisar != "Seleccione un DNI...":
                            if st.button("📊 Ver Detalle", key="btn_ver_detalle"):
                                st.session_state['mostrar_detalle_dni'] = dni_supervisar
                    
                    # Mostrar tabla resumen
                    st.dataframe(
                        df_resumen_dni,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "DNI": st.column_config.TextColumn("DNI", width="small"),
                            "Nombre Completo": st.column_config.TextColumn("Nombre", width="medium"),
                            "Edad": st.column_config.NumberColumn("Edad", width="small"),
                            "Género": st.column_config.TextColumn("Género", width="small"),
                            "N° Registros": st.column_config.NumberColumn("Registros", width="small")
                        }
                    )
                    
                    # Mostrar detalle del DNI seleccionado
                    if st.session_state.get('mostrar_detalle_dni') and st.session_state['mostrar_detalle_dni'] == dni_supervisar:
                        st.markdown(f"### 🔍 Detalle de códigos para DNI: {dni_supervisar}")
                        
                        # Filtrar registros del DNI
                        df_dni_detalle = df_indicador[df_indicador['pac_Numero_Documento'] == dni_supervisar]
                        
                        # Información del indicador
                        info_indicador = INDICADORES[indicador_key]
                        st.info(f"**{info_indicador['nombre']}** - {info_indicador['descripcion']}")
                        
                        # Mostrar códigos relevantes para el indicador
                        columnas_detalle = ['Fecha_Formato', 'Codigo_Item', 'CIE10_Descripcion', 
                                          'Tipo_Diagnostico', 'Valor_Lab', 'Personal_Completo']
                        
                        df_mostrar = df_dni_detalle[columnas_detalle].copy()
                        
                        st.dataframe(
                            df_mostrar,
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "Fecha_Formato": st.column_config.TextColumn("Fecha", width="small"),
                                "Codigo_Item": st.column_config.TextColumn("Código", width="small"),
                                "CIE10_Descripcion": st.column_config.TextColumn("Descripción", width="medium"),
                                "Tipo_Diagnostico": st.column_config.TextColumn("Tipo Dx", width="small"),
                                "Valor_Lab": st.column_config.TextColumn("Lab", width="small"),
                                "Personal_Completo": st.column_config.TextColumn("Personal", width="medium")
                            }
                        )
                        
                        # Mostrar reglas del indicador
                        with st.expander("📋 Ver reglas del indicador"):
                            for regla in info_indicador.get('reglas', []):
                                if isinstance(regla, dict):
                                    st.markdown(f"**Código:** {regla.get('codigo', 'N/A')}")
                                    st.markdown(f"**Descripción:** {regla.get('descripcion', 'N/A')}")
                                    if 'lab_descripcion' in regla:
                                        st.markdown(f"**Valores Lab:** {regla['lab_descripcion']}")
                                    st.markdown("---")
                
                else:
                    st.warning("No se encontraron registros que cumplan con este indicador en el período seleccionado.")
            
            elif tipo_supervision == "Paquete de Atención Integral":
                # Análisis del paquete integral
                st.markdown("### 📦 Análisis del Paquete de Atención Integral")
                
                # Seleccionar rango de edad y función según curso de vida
                if curso_vida == "Adulto (30-59 años)":
                    edad_min, edad_max = 30, 59
                    verificar_paquete = verificar_paquete_adulto
                    grupo_etario = "Adultos"
                elif curso_vida == "Joven (18-29 años)":
                    edad_min, edad_max = 18, 29
                    verificar_paquete = verificar_paquete_joven
                    grupo_etario = "Jóvenes"
                else:  # Adulto Mayor
                    edad_min, edad_max = 60, 150
                    verificar_paquete = verificar_paquete_adulto_mayor
                    grupo_etario = "Adultos Mayores"
                
                # Filtrar por curso de vida
                df_curso = df_filtrado[
                    (df_filtrado['edad_anos'] >= edad_min) & 
                    (df_filtrado['edad_anos'] <= edad_max)
                ]
                
                if not df_curso.empty:
                    # Selector de columnas adicionales para paquete integral
                    st.markdown("#### 🔧 Personalizar tabla de resultados")
                    columnas_disponibles_paquete = {
                        'Id_Establecimiento': 'Código Estab.',
                        'Establecimiento_Nombre': 'Nombre Estab.',
                        'Personal_Completo': 'Último Personal',
                        'Fecha_Atencion': 'Última Atención',
                        'UPS_Descripcion': 'Último Servicio',
                        'mes_Descripcion': 'Mes Atención',
                        'Id_Turno': 'Turno'
                    }
                    
                    # Botones para seleccionar/quitar todas
                    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
                    with col_btn1:
                        if st.button("✅ Seleccionar todas", key="sel_todas_paq"):
                            st.session_state.columnas_paquete = list(columnas_disponibles_paquete.keys())
                            st.rerun()
                    with col_btn2:
                        if st.button("❌ Quitar todas", key="quit_todas_paq"):
                            st.session_state.columnas_paquete = []
                            st.rerun()
                    
                    # Usar el valor del session_state si existe
                    default_cols_paq = st.session_state.get('columnas_paquete', [])
                    
                    columnas_seleccionadas_paquete = st.multiselect(
                        "Agregar columnas a la tabla de paquetes:",
                        options=list(columnas_disponibles_paquete.keys()),
                        default=default_cols_paq,
                        format_func=lambda x: columnas_disponibles_paquete[x],
                        key="columnas_paquete"
                    )
                    
                    # Obtener DNIs únicos
                    dni_curso = df_curso['pac_Numero_Documento'].unique()
                    
                    # Calcular cumplimiento del paquete para cada DNI
                    resultados_paquete = []
                    
                    with st.spinner(f'Analizando paquetes de atención integral para {grupo_etario.lower()}...'):
                        for dni in dni_curso[:100]:  # Limitar a 100 para evitar demoras
                            resultado = verificar_paquete(df_curso, dni)
                            
                            # Obtener información del paciente
                            info_paciente = df_curso[df_curso['pac_Numero_Documento'] == dni].iloc[0]
                            
                            # Construir registro con información básica primero
                            registro = {
                                'DNI': dni,
                                'Nombre': info_paciente['Paciente_Completo'],
                                'Edad': info_paciente['edad_anos'],
                                'Género': info_paciente['pac_Genero']
                            }
                            
                            # Agregar columnas seleccionadas
                            for col in columnas_seleccionadas_paquete:
                                if col == 'Fecha_Atencion':
                                    # Obtener la última fecha de atención
                                    registro[columnas_disponibles_paquete[col]] = df_curso[df_curso['pac_Numero_Documento'] == dni]['Fecha_Formato'].max()
                                elif col in info_paciente.index:
                                    registro[columnas_disponibles_paquete[col]] = info_paciente[col]
                                else:
                                    # Para otras columnas, obtener el último valor
                                    ultimo_registro = df_curso[df_curso['pac_Numero_Documento'] == dni].iloc[-1]
                                    registro[columnas_disponibles_paquete[col]] = ultimo_registro.get(col, 'N/A')
                            
                            # Agregar componentes según curso de vida
                            if curso_vida == "Adulto (30-59 años)":
                                registro.update({
                                    'Val. Clínica': '✅' if resultado['componentes'].get('Valoración Clínica y Tamizaje Laboratorial', False) else '❌',
                                    'Depresión': '✅' if resultado['componentes'].get('Tamizaje Trastornos Depresivos', False) else '❌',
                                    'Violencia': '✅' if resultado['componentes'].get('Tamizaje Violencia', False) else '❌',
                                    'VIH': '✅' if resultado['componentes'].get('Tamizaje VIH', False) else '❌',
                                    'Agudeza Visual': '✅' if resultado['componentes'].get('Tamizaje Agudeza Visual', False) else '❌',
                                    'Eval. Oral': '✅' if resultado['componentes'].get('Evaluación Oral Completa', False) else '❌',
                                    'Alcohol/Drogas': '✅' if resultado['componentes'].get('Tamizaje Alcohol y Drogas', False) else '❌'
                                })
                            elif curso_vida == "Joven (18-29 años)":
                                registro.update({
                                    'Val. Clínica': '✅' if resultado['componentes'].get('Valoración Clínica y Factores de Riesgo', False) else '❌',
                                    'Violencia': '✅' if resultado['componentes'].get('Tamizaje Violencia Intrafamiliar', False) else '❌',
                                    'Alcohol/Drogas': '✅' if resultado['componentes'].get('Tamizaje Alcohol y Drogas', False) else '❌',
                                    'Depresión': '✅' if resultado['componentes'].get('Tamizaje Depresión', False) else '❌',
                                    'Eval. Nutricional': '✅' if resultado['componentes'].get('Evaluación Nutricional y Antropométrica', False) else '❌',
                                    'Consejería SSR': '✅' if resultado['componentes'].get('Consejería Salud Sexual y Reproductiva', False) else '❌'
                                })
                            else:  # Adulto Mayor
                                registro.update({
                                    'VACAM': '✅' if resultado['componentes'].get('VACAM - Valoración Clínica', False) else '❌',
                                    'Agudeza Visual': '✅' if resultado['componentes'].get('Tamizaje Agudeza Visual', False) else '❌',
                                    'Salud Mental': '✅' if resultado['componentes'].get('Tamizaje Integral Salud Mental', False) else '❌',
                                    'Eval. Oral': '✅' if resultado['componentes'].get('Evaluación Oral Completa', False) else '❌',
                                    'Vac. Influenza': '✅' if resultado['componentes'].get('Vacuna Influenza', False) else '❌',
                                    'Consejería': '✅' if resultado['componentes'].get('Consejería Integral', False) else '❌',
                                    'Val. Clínica/Lab': '✅' if resultado['componentes'].get('Valoración Clínica y Laboratorio', False) else '❌'
                                })
                            
                            # Agregar columnas de estado del paquete al final
                            registro.update({
                                'N° Componentes': sum(resultado['componentes'].values()),
                                'Plan Elaborado': '✅' if resultado['plan_elaborado'] else '❌',
                                'Plan Ejecutado': '✅' if resultado['plan_ejecutado'] else '❌',
                                'Completo': '✅' if resultado['completo'] else '❌'
                            })
                            
                            resultados_paquete.append(registro)
                    
                    df_paquetes = pd.DataFrame(resultados_paquete)
                    
                    # Calcular número de componentes esperados según curso de vida
                    if curso_vida == "Adulto (30-59 años)":
                        num_componentes_total = 7
                    elif curso_vida == "Joven (18-29 años)":
                        num_componentes_total = 6
                    else:  # Adulto Mayor
                        num_componentes_total = 7
                    
                    # Agregar columna de componentes faltantes
                    df_paquetes['Componentes_Faltantes'] = num_componentes_total - df_paquetes['N° Componentes']
                    
                    # Reorganizar columnas para que las de estado estén al final
                    columnas_base = ['DNI', 'Nombre', 'Edad', 'Género']
                    columnas_adicionales = [col for col in columnas_disponibles_paquete.values() if col in df_paquetes.columns]
                    
                    # Columnas de componentes según curso de vida
                    if curso_vida == "Adulto (30-59 años)":
                        columnas_componentes = ['Val. Clínica', 'Depresión', 'Violencia', 'VIH', 
                                              'Agudeza Visual', 'Eval. Oral', 'Alcohol/Drogas']
                    elif curso_vida == "Joven (18-29 años)":
                        columnas_componentes = ['Val. Clínica', 'Violencia', 'Alcohol/Drogas', 
                                              'Depresión', 'Eval. Nutricional', 'Consejería SSR']
                    else:  # Adulto Mayor
                        columnas_componentes = ['VACAM', 'Agudeza Visual', 'Salud Mental', 
                                              'Eval. Oral', 'Vac. Influenza', 'Consejería', 'Val. Clínica/Lab']
                    
                    # Columnas de estado al final
                    columnas_estado = ['N° Componentes', 'Componentes_Faltantes', 'Plan Elaborado', 
                                     'Plan Ejecutado', 'Completo']
                    
                    # Reordenar DataFrame
                    columnas_ordenadas = columnas_base + columnas_adicionales + columnas_componentes + columnas_estado
                    df_paquetes = df_paquetes[columnas_ordenadas]
                    
                    # Ordenar por prioridad: primero los que tienen más componentes (les falta menos)
                    df_paquetes = df_paquetes.sort_values('N° Componentes', ascending=False)
                    
                    # Visualización mejorada del estado
                    st.markdown("### 🎯 Resumen Visual del Estado de Paquetes")
                    
                    # Gráfico de dona para completos vs incompletos
                    col_graf1, col_graf2 = st.columns(2)
                    
                    with col_graf1:
                        # Datos para el gráfico de dona
                        completos = len(df_paquetes[df_paquetes['Completo'] == '✅'])
                        incompletos = len(df_paquetes[df_paquetes['Completo'] == '❌'])
                        
                        fig_dona = px.pie(
                            values=[completos, incompletos],
                            names=['Completos', 'Incompletos'],
                            title='Estado de Paquetes',
                            hole=0.4,
                            color_discrete_map={'Completos': '#00CC88', 'Incompletos': '#FF6B6B'}
                        )
                        fig_dona.update_traces(textposition='inside', textinfo='value+percent')
                        fig_dona.update_layout(height=300)
                        st.plotly_chart(fig_dona, use_container_width=True)
                    
                    with col_graf2:
                        # Distribución por número de componentes
                        dist_componentes = df_paquetes['N° Componentes'].value_counts().sort_index()
                        
                        fig_dist = px.bar(
                            x=dist_componentes.index,
                            y=dist_componentes.values,
                            title='Distribución por N° Componentes Completados',
                            labels={'x': 'N° Componentes', 'y': 'Cantidad de Personas'},
                            color=dist_componentes.index,
                            color_continuous_scale='Viridis'
                        )
                        fig_dist.update_layout(height=300, showlegend=False)
                        st.plotly_chart(fig_dist, use_container_width=True)
                    
                    # Mostrar métricas
                    col1, col2, col3, col4 = st.columns(4)
                    
                    total_personas = len(dni_curso)
                    con_plan = len(df_paquetes[df_paquetes['Plan Elaborado'] == '✅'])
                    completos = len(df_paquetes[df_paquetes['Completo'] == '✅'])
                    porcentaje_completo = (completos / total_personas * 100) if total_personas > 0 else 0
                    
                    with col1:
                        st.metric(f"Total {grupo_etario}", f"{total_personas:,}")
                    with col2:
                        st.metric("Con Plan Elaborado", f"{con_plan:,}")
                    with col3:
                        st.metric("Paquetes Completos", f"{completos:,}")
                    with col4:
                        st.metric("% Cumplimiento", f"{porcentaje_completo:.1f}%")
                    
                    # Filtros mejorados para la tabla
                    st.markdown("### 🔍 Filtros de Supervisión")
                    col1, col2, col3 = st.columns([2, 2, 2])
                    
                    with col1:
                        filtro_paquete = st.selectbox(
                            "Filtrar por estado:",
                            ["Todos", "Completos", "Incompletos", "Con Plan", "Sin Plan", "Casi Completos (1-2 faltantes)"],
                            key="filtro_paquete"
                        )
                    
                    with col2:
                        # Filtro por número de componentes
                        num_componentes_filtro = st.select_slider(
                            "N° Componentes completados:",
                            options=list(range(0, num_componentes_total + 1)),
                            value=(0, num_componentes_total),
                            key="filtro_num_componentes"
                        )
                    
                    with col3:
                        # Mostrar estadísticas de priorización
                        casi_completos = len(df_paquetes[df_paquetes['Componentes_Faltantes'].isin([1, 2])])
                        st.info(f"🎯 **Prioridad Alta**: {casi_completos} personas\nLes faltan 1-2 componentes")
                    
                    # Aplicar filtros
                    df_mostrar = df_paquetes.copy()
                    
                    if filtro_paquete == "Completos":
                        df_mostrar = df_mostrar[df_mostrar['Completo'] == '✅']
                    elif filtro_paquete == "Incompletos":
                        df_mostrar = df_mostrar[df_mostrar['Completo'] == '❌']
                    elif filtro_paquete == "Con Plan":
                        df_mostrar = df_mostrar[df_mostrar['Plan Elaborado'] == '✅']
                    elif filtro_paquete == "Sin Plan":
                        df_mostrar = df_mostrar[df_mostrar['Plan Elaborado'] == '❌']
                    elif filtro_paquete == "Casi Completos (1-2 faltantes)":
                        df_mostrar = df_mostrar[df_mostrar['Componentes_Faltantes'].isin([1, 2])]
                    
                    # Filtro por número de componentes
                    df_mostrar = df_mostrar[
                        (df_mostrar['N° Componentes'] >= num_componentes_filtro[0]) &
                        (df_mostrar['N° Componentes'] <= num_componentes_filtro[1])
                    ]
                    
                    # Si hay registros filtrados y son incompletos, mostrar análisis de componentes faltantes
                    if len(df_mostrar) > 0 and (filtro_paquete in ["Incompletos", "Casi Completos (1-2 faltantes)"]):
                        st.markdown("### 📊 Análisis de Componentes Faltantes")
                        
                        # Contar qué componentes faltan más
                        componentes_faltantes = {}
                        
                        # Definir las columnas de componentes según curso de vida
                        if curso_vida == "Adulto (30-59 años)":
                            columnas_componentes = ['Val. Clínica', 'Depresión', 'Violencia', 'VIH', 
                                                  'Agudeza Visual', 'Eval. Oral', 'Alcohol/Drogas']
                        elif curso_vida == "Joven (18-29 años)":
                            columnas_componentes = ['Val. Clínica', 'Violencia', 'Alcohol/Drogas', 
                                                  'Depresión', 'Eval. Nutricional', 'Consejería SSR']
                        else:  # Adulto Mayor
                            columnas_componentes = ['VACAM', 'Agudeza Visual', 'Salud Mental', 
                                                  'Eval. Oral', 'Vac. Influenza', 'Consejería', 'Val. Clínica/Lab']
                        
                        # Contar componentes faltantes
                        for col in columnas_componentes:
                            if col in df_mostrar.columns:
                                faltantes = len(df_mostrar[df_mostrar[col] == '❌'])
                                if faltantes > 0:
                                    componentes_faltantes[col] = faltantes
                        
                        if componentes_faltantes:
                            # Crear gráfico de componentes faltantes
                            fig_faltantes = px.bar(
                                x=list(componentes_faltantes.keys()),
                                y=list(componentes_faltantes.values()),
                                title='Componentes Faltantes por Frecuencia',
                                labels={'x': 'Componente', 'y': 'N° Personas que les falta'},
                                color=list(componentes_faltantes.values()),
                                color_continuous_scale='Reds'
                            )
                            fig_faltantes.update_layout(height=300, showlegend=False)
                            st.plotly_chart(fig_faltantes, use_container_width=True)
                            
                            # Mostrar recomendaciones
                            componente_mas_faltante = max(componentes_faltantes, key=componentes_faltantes.get)
                            st.warning(f"⚠️ **Componente crítico**: '{componente_mas_faltante}' falta en {componentes_faltantes[componente_mas_faltante]} personas")
                    
                    # Mostrar tabla de paquetes
                    st.markdown("### 📊 Estado de Paquetes de Atención Integral")
                    
                    # Configuración de columnas
                    config_columnas = {
                        "DNI": st.column_config.TextColumn("DNI", width="small"),
                        "Nombre": st.column_config.TextColumn("Nombre", width="medium"),
                        "Edad": st.column_config.NumberColumn("Edad", width="small"),
                        "Género": st.column_config.TextColumn("Género", width="small"),
                        "N° Componentes": st.column_config.NumberColumn("Componentes", width="small", help="Número de componentes completados"),
                        "Componentes_Faltantes": st.column_config.NumberColumn("Faltantes", width="small", help="Número de componentes que faltan"),
                        "Plan Elaborado": st.column_config.TextColumn("Plan Elaborado", width="small"),
                        "Plan Ejecutado": st.column_config.TextColumn("Plan Ejecutado", width="small"),
                        "Completo": st.column_config.TextColumn("Completo", width="small")
                    }
                    
                    # Agregar configuración para columnas adicionales
                    for col_nombre in columnas_disponibles_paquete.values():
                        if col_nombre in df_mostrar.columns:
                            if "Fecha" in col_nombre:
                                config_columnas[col_nombre] = st.column_config.TextColumn(col_nombre, width="small")
                            elif "Código" in col_nombre:
                                config_columnas[col_nombre] = st.column_config.TextColumn(col_nombre, width="small")
                            else:
                                config_columnas[col_nombre] = st.column_config.TextColumn(col_nombre, width="medium")
                    
                    st.dataframe(
                        df_mostrar,
                        use_container_width=True,
                        hide_index=True,
                        column_config=config_columnas
                    )
                    
                    # Sistema avanzado de exportación JSON
                    if filtro_paquete in ["Incompletos", "Casi Completos (1-2 faltantes)", "Todos"]:
                        st.markdown("### 🤖 Automatización HIS-MINSA - Exportación Flexible")
                        
                        # Selector de modo de exportación
                        modo_exportacion = st.radio(
                            "Modo de exportación:",
                            ["🚀 Rápido (Todos los faltantes)", "⚙️ Avanzado (Selección personalizada)"],
                            horizontal=True,
                            key="modo_export"
                        )
                        
                        if modo_exportacion == "🚀 Rápido (Todos los faltantes)":
                            # Modo simple - comportamiento original
                            col_exp1, col_exp2 = st.columns([2, 2])
                            
                            with col_exp1:
                                if st.button("📥 Exportar JSON para Corrección", type="primary", key="btn_export_simple"):
                                    json_data = generar_json_exportacion(df_filtrado, filtro_paquete, curso_vida)
                                    
                                    if json_data:
                                        json_str = json.dumps(json_data, indent=2, ensure_ascii=False)
                                        nombre_archivo = f"correccion_paquetes_{curso_vida.lower().replace(' ', '_').replace('(', '').replace(')', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                                        
                                        st.download_button(
                                            label="💾 Descargar JSON",
                                            data=json_str,
                                            file_name=nombre_archivo,
                                            mime="application/json",
                                            key="download_json_simple"
                                        )
                                        
                                        st.success(f"✅ JSON generado con {json_data['total_pacientes']} pacientes")
                                        
                                        with st.expander("👁️ Vista previa del JSON"):
                                            st.json(json_data)
                                    else:
                                        st.warning("No se encontraron pacientes para exportar")
                            
                            with col_exp2:
                                st.info("📌 Exporta todos los códigos faltantes de todos los pacientes filtrados")
                        
                        else:  # Modo Avanzado
                            # Contenedor para selección personalizada
                            st.markdown("#### 📋 Selección Personalizada de Pacientes y Códigos")
                            
                            # Inicializar estados en session_state
                            if 'pacientes_seleccionados' not in st.session_state:
                                st.session_state.pacientes_seleccionados = []
                            if 'componentes_seleccionados' not in st.session_state:
                                st.session_state.componentes_seleccionados = {}
                            if 'codigos_seleccionados' not in st.session_state:
                                st.session_state.codigos_seleccionados = {}
                            
                            # Tab para organizar la selección
                            tab_pac, tab_comp, tab_preview = st.tabs(["1️⃣ Seleccionar Pacientes", "2️⃣ Seleccionar Componentes", "3️⃣ Vista Previa y Exportar"])
                            
                            with tab_pac:
                                st.markdown("##### Selecciona los pacientes a incluir:")
                                
                                # Botones de selección rápida
                                col_sel1, col_sel2, col_sel3, col_sel4 = st.columns(4)
                                with col_sel1:
                                    if st.button("✅ Seleccionar Todos", key="sel_todos_pac"):
                                        st.session_state.pacientes_seleccionados = df_mostrar['DNI'].tolist()
                                        st.rerun()
                                with col_sel2:
                                    if st.button("❌ Quitar Todos", key="quit_todos_pac"):
                                        st.session_state.pacientes_seleccionados = []
                                        st.rerun()
                                with col_sel3:
                                    if st.button("🎯 Solo Casi Completos", key="sel_casi_comp"):
                                        # Seleccionar solo los que les falta 1-2 componentes
                                        df_casi = df_mostrar[df_mostrar['Componentes_Faltantes'].isin([1, 2])]
                                        st.session_state.pacientes_seleccionados = df_casi['DNI'].tolist()
                                        st.rerun()
                                
                                # Crear DataFrame con checkboxes
                                df_seleccion = df_mostrar[['DNI', 'Nombre', 'Edad', 'N° Componentes', 'Componentes_Faltantes']].copy()
                                df_seleccion['Seleccionar'] = df_seleccion['DNI'].apply(
                                    lambda x: x in st.session_state.pacientes_seleccionados
                                )
                                
                                # Editor de datos con checkboxes
                                df_editado = st.data_editor(
                                    df_seleccion,
                                    column_config={
                                        "Seleccionar": st.column_config.CheckboxColumn(
                                            "Seleccionar",
                                            help="Marca para incluir en la exportación",
                                            default=False,
                                        ),
                                        "DNI": st.column_config.TextColumn("DNI", disabled=True),
                                        "Nombre": st.column_config.TextColumn("Nombre", disabled=True),
                                        "Edad": st.column_config.NumberColumn("Edad", disabled=True),
                                        "N° Componentes": st.column_config.NumberColumn("Completados", disabled=True),
                                        "Componentes_Faltantes": st.column_config.NumberColumn("Faltantes", disabled=True),
                                    },
                                    disabled=["DNI", "Nombre", "Edad", "N° Componentes", "Componentes_Faltantes"],
                                    hide_index=True,
                                    use_container_width=True,
                                    key="df_pacientes_editor"
                                )
                                
                                # Actualizar selección
                                st.session_state.pacientes_seleccionados = df_editado[df_editado['Seleccionar']]['DNI'].tolist()
                                
                                if st.session_state.pacientes_seleccionados:
                                    st.success(f"✅ {len(st.session_state.pacientes_seleccionados)} pacientes seleccionados")
                                else:
                                    st.warning("⚠️ No hay pacientes seleccionados")
                            
                            with tab_comp:
                                if st.session_state.pacientes_seleccionados:
                                    st.markdown("##### Configuración de exportación:")
                                    
                                    # Opción para elegir qué exportar
                                    col_config1, col_config2 = st.columns(2)
                                    with col_config1:
                                        tipo_exportacion = st.radio(
                                            "¿Qué códigos deseas exportar?",
                                            ["Solo códigos faltantes", "Todos los códigos (existentes + faltantes)"],
                                            key="tipo_export_radio",
                                            help="Faltantes: Solo códigos que el paciente NO tiene. Todos: Incluye códigos existentes para modificar LAB"
                                        )
                                    
                                    # Guardar en session state
                                    st.session_state.exportar_solo_faltantes = (tipo_exportacion == "Solo códigos faltantes")
                                    
                                    st.markdown("##### Selecciona qué componentes/códigos exportar:")
                                    
                                    # Obtener componentes disponibles según curso de vida
                                    if curso_vida == "Adulto (30-59 años)":
                                        componentes_disponibles = list(PAQUETE_INTEGRAL_ADULTO['componentes_minimos'])
                                        indicadores_ref = INDICADORES_ADULTO
                                    elif curso_vida == "Joven (18-29 años)":
                                        componentes_disponibles = list(PAQUETE_INTEGRAL_JOVEN['componentes_minimos'])
                                        indicadores_ref = INDICADORES_JOVEN
                                    else:
                                        componentes_disponibles = list(PAQUETE_INTEGRAL_ADULTO_MAYOR['componentes_minimos'])
                                        indicadores_ref = INDICADORES_ADULTO_MAYOR
                                    
                                    # Selector de componentes
                                    componentes_nombres = [comp['componente'] for comp in componentes_disponibles]
                                    # Agregar Plan de Atención como opción adicional
                                    componentes_nombres_con_plan = componentes_nombres + ["Plan de Atención Integral"]
                                    
                                    componentes_seleccionados = st.multiselect(
                                        "Componentes a incluir:",
                                        componentes_nombres_con_plan,
                                        default=componentes_nombres_con_plan,
                                        key="multi_componentes"
                                    )
                                    
                                    # Para cada componente seleccionado, mostrar códigos específicos
                                    if componentes_seleccionados:
                                        st.markdown("##### Personalización por componente:")
                                        
                                        for comp_nombre in componentes_seleccionados:
                                            # Encontrar el componente
                                            componente = next((c for c in componentes_disponibles if c['componente'] == comp_nombre), None)
                                            if componente and 'indicador' in componente:
                                                indicador_info = indicadores_ref.get(componente['indicador'], {})
                                                
                                                with st.expander(f"📌 {comp_nombre}"):
                                                    # Mostrar códigos disponibles
                                                    codigos_componente = []
                                                    
                                                    if 'reglas' in indicador_info:
                                                        if isinstance(indicador_info['reglas'], list):
                                                            for regla in indicador_info['reglas']:
                                                                codigo_desc = f"{regla['codigo']} - {regla.get('descripcion', 'Sin descripción')}"
                                                                if 'lab_valores' in regla and regla['lab_valores']:
                                                                    lab_info = regla['lab_valores'][0] if isinstance(regla['lab_valores'], list) else regla['lab_valores']
                                                                    if lab_info:
                                                                        codigo_desc += f" [LAB: {lab_info}]"
                                                                codigos_componente.append({
                                                                    'codigo': regla['codigo'],
                                                                    'descripcion': codigo_desc,
                                                                    'regla': regla
                                                                })
                                                    
                                                    if codigos_componente:
                                                        # Crear key única para este componente
                                                        key_comp = f"codigos_{componente['indicador']}"
                                                        
                                                        # Selector de códigos
                                                        codigos_seleccionados = st.multiselect(
                                                            "Selecciona códigos específicos:",
                                                            [c['descripcion'] for c in codigos_componente],
                                                            default=[c['descripcion'] for c in codigos_componente],
                                                            key=key_comp
                                                        )
                                                        
                                                        # Guardar selección
                                                        st.session_state.codigos_seleccionados[componente['indicador']] = [
                                                            c for c in codigos_componente 
                                                            if c['descripcion'] in codigos_seleccionados
                                                        ]
                                                    else:
                                                        st.info("No hay códigos específicos configurados")
                                            
                                        # Manejo especial para Plan de Atención Integral
                                        if "Plan de Atención Integral" in componentes_seleccionados:
                                            with st.expander("📌 Plan de Atención Integral"):
                                                st.markdown("**Selecciona qué elementos del plan incluir:**")
                                                col_plan1, col_plan2 = st.columns(2)
                                                with col_plan1:
                                                    plan_elaborado = st.checkbox("✓ 99801 - Plan Elaborado [LAB: 1]", value=True, key="plan_elab_check")
                                                with col_plan2:
                                                    plan_ejecutado = st.checkbox("✓ 99801 - Plan Ejecutado [LAB: TA]", value=True, key="plan_ejec_check")
                                                
                                                st.session_state.codigos_seleccionados['plan_atencion'] = {
                                                    'elaborado': plan_elaborado,
                                                    'ejecutado': plan_ejecutado
                                                }
                                                
                                                # Mostrar información adicional
                                                st.info("💡 El Plan de Atención Integral es necesario para completar el paquete de atención")
                                    else:
                                        st.warning("⚠️ Selecciona al menos un componente")
                                else:
                                    st.warning("⚠️ Primero selecciona pacientes en la pestaña anterior")
                            
                            with tab_preview:
                                if st.session_state.pacientes_seleccionados and componentes_seleccionados:
                                    st.markdown("##### 📋 Vista Previa de la Exportación")
                                    
                                    # Generar JSON personalizado
                                    json_personalizado = generar_json_exportacion_personalizada(
                                        df_filtrado,
                                        st.session_state.pacientes_seleccionados,
                                        componentes_seleccionados,
                                        st.session_state.codigos_seleccionados,
                                        curso_vida
                                    )
                                    
                                    if json_personalizado:
                                        # Mostrar resumen
                                        col_res1, col_res2, col_res3 = st.columns(3)
                                        with col_res1:
                                            st.metric("Pacientes", json_personalizado['total_pacientes'])
                                        with col_res2:
                                            total_diagnosticos = sum(len(p['diagnosticos']) for p in json_personalizado['pacientes'])
                                            st.metric("Total Diagnósticos", total_diagnosticos)
                                        with col_res3:
                                            st.metric("Curso de Vida", curso_vida.split(' ')[0])
                                        
                                        # Vista previa del JSON
                                        st.json(json_personalizado)
                                        
                                        # Botón de descarga
                                        json_str = json.dumps(json_personalizado, indent=2, ensure_ascii=False)
                                        nombre_archivo = f"correccion_personalizada_{curso_vida.lower().replace(' ', '_').replace('(', '').replace(')', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                                        
                                        st.download_button(
                                            label="💾 Descargar JSON Personalizado",
                                            data=json_str,
                                            file_name=nombre_archivo,
                                            mime="application/json",
                                            type="primary",
                                            key="download_json_custom"
                                        )
                                    else:
                                        st.error("Error al generar el JSON personalizado")
                                else:
                                    st.info("📌 Completa la selección de pacientes y componentes en las pestañas anteriores")
                    
                    # Gráfico de componentes
                    st.markdown("### 📈 Cumplimiento por Componente")
                    
                    # Estadísticas según curso de vida
                    if curso_vida == "Adulto (30-59 años)":
                        componentes_stats = {
                            'Valoración Clínica': len(df_paquetes[df_paquetes['Val. Clínica'] == '✅']),
                            'Tamizaje Depresión': len(df_paquetes[df_paquetes['Depresión'] == '✅']),
                            'Tamizaje Violencia': len(df_paquetes[df_paquetes['Violencia'] == '✅']),
                            'Tamizaje VIH': len(df_paquetes[df_paquetes['VIH'] == '✅']),
                            'Agudeza Visual': len(df_paquetes[df_paquetes['Agudeza Visual'] == '✅']),
                            'Evaluación Oral': len(df_paquetes[df_paquetes['Eval. Oral'] == '✅']),
                            'Alcohol/Drogas': len(df_paquetes[df_paquetes['Alcohol/Drogas'] == '✅'])
                        }
                    elif curso_vida == "Joven (18-29 años)":
                        componentes_stats = {
                            'Valoración Clínica': len(df_paquetes[df_paquetes['Val. Clínica'] == '✅']),
                            'Tamizaje Violencia': len(df_paquetes[df_paquetes['Violencia'] == '✅']),
                            'Alcohol/Drogas': len(df_paquetes[df_paquetes['Alcohol/Drogas'] == '✅']),
                            'Tamizaje Depresión': len(df_paquetes[df_paquetes['Depresión'] == '✅']),
                            'Eval. Nutricional': len(df_paquetes[df_paquetes['Eval. Nutricional'] == '✅']),
                            'Consejería SSR': len(df_paquetes[df_paquetes['Consejería SSR'] == '✅'])
                        }
                    else:  # Adulto Mayor
                        componentes_stats = {
                            'VACAM': len(df_paquetes[df_paquetes['VACAM'] == '✅']),
                            'Agudeza Visual': len(df_paquetes[df_paquetes['Agudeza Visual'] == '✅']),
                            'Salud Mental': len(df_paquetes[df_paquetes['Salud Mental'] == '✅']),
                            'Evaluación Oral': len(df_paquetes[df_paquetes['Eval. Oral'] == '✅']),
                            'Vacuna Influenza': len(df_paquetes[df_paquetes['Vac. Influenza'] == '✅']),
                            'Consejería': len(df_paquetes[df_paquetes['Consejería'] == '✅']),
                            'Val. Clínica/Lab': len(df_paquetes[df_paquetes['Val. Clínica/Lab'] == '✅'])
                        }
                    
                    fig_componentes = px.bar(
                        x=list(componentes_stats.keys()),
                        y=list(componentes_stats.values()),
                        title="Cumplimiento por Componente del Paquete",
                        labels={'x': 'Componente', 'y': f'N° de {grupo_etario}'}
                    )
                    fig_componentes.add_hline(
                        y=total_personas, 
                        line_dash="dash", 
                        annotation_text=f"Total: {total_personas}"
                    )
                    st.plotly_chart(fig_componentes, use_container_width=True)
                    
                    # Descargar reporte
                    if st.button("📥 Descargar Reporte de Paquetes", key="btn_descargar_paquetes"):
                        csv = df_paquetes.to_csv(index=False, encoding='latin-1')
                        b64 = base64.b64encode(csv.encode('latin-1')).decode()
                        href = f'<a href="data:file/csv;base64,{b64}" download="reporte_paquetes_integral.csv">Descargar CSV</a>'
                        st.markdown(href, unsafe_allow_html=True)
                
                else:
                    st.warning(f"No se encontraron registros de {grupo_etario.lower()} ({edad_min}-{edad_max} años) en el período seleccionado.")
    
    else:
        # Instrucciones cuando no hay datos
        st.info("""
        ### 📌 Cómo usar esta aplicación:
        
        **Opción 1: Solo Consolidados (Recomendado)**
        1. Arrastra los archivos consolidados en la pestaña "📄 Consolidados"
        2. Haz clic en "Procesar Archivos"
        3. Los archivos maestros se cargarán automáticamente del directorio
        
        **Opción 2: Actualizar Todo**
        1. Carga los consolidados en la primera pestaña
        2. Ve a la pestaña "🗂️ Archivos Maestros" y carga las versiones nuevas
        3. Haz clic en "Procesar Archivos"
        
        **Nota:** Solo actualiza los archivos maestros si tienes versiones más recientes
        """)
    
    # Pie de página
    st.markdown("---")
    st.markdown(
        f"""<div style='text-align: center; color: #666;'>
        Sistema Flexible HISMINSA | Modo: {st.session_state.maestros_origen.title() if st.session_state.archivos_maestros_cargados else 'Sin cargar'} | 
        {datetime.now().strftime("%d/%m/%Y %H:%M")}
        </div>""",
        unsafe_allow_html=True
    )

# ==============================================================================
# FUNCIONES DE EXPORTACIÓN JSON PARA AUTOMATIZACIÓN HIS-MINSA
# ==============================================================================

def obtener_codigos_faltantes_paquete(df_paciente, curso_vida):
    """
    Identifica qué códigos le faltan a un paciente para completar su paquete integral
    Retorna lista de diagnósticos faltantes con formato para JSON
    """
    codigos_faltantes = []
    
    # Obtener información según curso de vida
    if curso_vida == "Adulto (30-59 años)":
        paquete_info = PAQUETE_INTEGRAL_ADULTO
        verificar_func = verificar_paquete_adulto
        edad_paciente = df_paciente['edad_anos'].iloc[0]
    elif curso_vida == "Joven (18-29 años)":
        paquete_info = PAQUETE_INTEGRAL_JOVEN
        verificar_func = verificar_paquete_joven
        edad_paciente = df_paciente['edad_anos'].iloc[0]
    else:  # Adulto Mayor
        paquete_info = PAQUETE_INTEGRAL_ADULTO_MAYOR
        verificar_func = verificar_paquete_adulto_mayor
        edad_paciente = df_paciente['edad_anos'].iloc[0]
    
    # Verificar qué tiene y qué le falta
    dni = df_paciente['pac_Numero_Documento'].iloc[0]
    resultado_paquete = verificar_func(df_paciente, dni)
    
    # Revisar cada componente del paquete
    for componente in paquete_info['componentes_minimos']:
        if not resultado_paquete['componentes'].get(componente['componente'], False):
            # Este componente le falta, obtener los códigos necesarios
            if 'indicador' in componente:
                # Buscar el indicador correspondiente
                if curso_vida == "Adulto (30-59 años)":
                    indicador_info = INDICADORES_ADULTO.get(componente['indicador'], {})
                elif curso_vida == "Joven (18-29 años)":
                    indicador_info = INDICADORES_JOVEN.get(componente['indicador'], {})
                else:
                    indicador_info = INDICADORES_ADULTO_MAYOR.get(componente['indicador'], {})
                
                # Procesar reglas del indicador
                if 'reglas' in indicador_info:
                    reglas = indicador_info['reglas']
                    
                    # Manejar diferentes estructuras de reglas
                    if isinstance(reglas, dict):
                        # Caso especial: reglas con opciones (ej: agudeza visual)
                        if 'opcion_a' in reglas:
                            # Por defecto usar opción A
                            for codigo_info in reglas['opcion_a'].get('codigos', []):
                                codigos_faltantes.append(crear_diagnostico_json(codigo_info))
                    elif isinstance(reglas, list):
                        # Reglas normales
                        for regla in reglas:
                            # Verificar si esta regla específica ya fue cumplida
                            if not verificar_codigo_existe(df_paciente, regla['codigo']):
                                # Para valoración clínica de adultos, no incluir Z017 aquí
                                if curso_vida == "Adulto (30-59 años)" and componente['indicador'] == 'valoracion_clinica_lab':
                                    # Solo agregar los códigos básicos (Z019, 99199.22, 99401.13)
                                    # El Z017 se maneja aparte según la edad
                                    codigos_faltantes.append(crear_diagnostico_json(regla))
                                elif curso_vida == "Adulto Mayor (60+ años)" and componente['indicador'] == 'valoracion_clinica_lab':
                                    # Para adulto mayor, laboratorio SIEMPRE obligatorio
                                    codigos_faltantes.append(crear_diagnostico_json(regla))
                                else:
                                    codigos_faltantes.append(crear_diagnostico_json(regla))
                
                # Agregar Z017 para adultos 40-59 si es valoración clínica
                if (componente['indicador'] == 'valoracion_clinica_lab' and 
                    curso_vida == "Adulto (30-59 años)" and 
                    edad_paciente >= 40 and edad_paciente <= 59):
                    if not verificar_codigo_existe(df_paciente, 'Z017'):
                        codigos_faltantes.append({
                            "codigo": "Z017",
                            "descripcion": "Z017 - Tamizaje laboratorial",
                            "tipo": "D",
                            "lab": ""
                        })
            
            # Manejo especial para componentes con reglas por edad (paquete adulto)
            elif 'reglas_30_39' in componente or 'reglas_40_59' in componente:
                if edad_paciente >= 30 and edad_paciente <= 39 and 'reglas_30_39' in componente:
                    for regla in componente['reglas_30_39']:
                        if not verificar_codigo_existe(df_paciente, regla['codigo']):
                            if 'condicion' in regla and regla['codigo'] == 'Z017':
                                # Laboratorio condicional
                                factores_riesgo = regla.get('factores_riesgo', [])
                                tiene_factores = any(df_paciente['Codigo_Item'].isin(factores_riesgo))
                                if tiene_factores:
                                    codigos_faltantes.append(crear_diagnostico_json(regla))
                            else:
                                codigos_faltantes.append(crear_diagnostico_json(regla))
                elif edad_paciente >= 40 and edad_paciente <= 59 and 'reglas_40_59' in componente:
                    for regla in componente['reglas_40_59']:
                        if not verificar_codigo_existe(df_paciente, regla['codigo']):
                            codigos_faltantes.append(crear_diagnostico_json(regla))
    
    # Agregar código de plan si no lo tiene
    if not resultado_paquete['plan_elaborado']:
        codigos_faltantes.append({
            "codigo": "99801",
            "descripcion": "99801 - Plan de Atención Integral Elaborado",
            "tipo": "D",
            "lab": "1"
        })
    
    if not resultado_paquete['plan_ejecutado']:
        codigos_faltantes.append({
            "codigo": "99801",
            "descripcion": "99801 - Plan de Atención Integral Ejecutado",
            "tipo": "D",
            "lab": "TA"
        })
    
    return codigos_faltantes

def verificar_codigo_existe(df_paciente, codigo):
    """Verifica si un código ya existe en los registros del paciente"""
    return not df_paciente[df_paciente['Codigo_Item'] == codigo].empty

def crear_diagnostico_json(regla):
    """Crea un diagnóstico en formato JSON a partir de una regla"""
    # Obtener descripción del diccionario CIE10 si está disponible
    codigo = regla['codigo']
    descripcion_cie = ""
    if hasattr(st.session_state, 'cie10_dict') and codigo in st.session_state.cie10_dict:
        descripcion_cie = st.session_state.cie10_dict[codigo]
    else:
        descripcion_cie = regla.get('descripcion', 'Descripción no disponible')
    
    diagnostico = {
        "codigo": codigo,
        "descripcion": f"{codigo} - {descripcion_cie}",
        "tipo": regla.get('tipo_dx', 'D')
    }
    
    # Primero verificar si hay un valor 'lab' directo en la regla (como en reglas_30_39, reglas_40_59)
    if 'lab' in regla:
        if isinstance(regla['lab'], list):
            # Si es lista, usar el primer valor
            diagnostico["lab"] = regla['lab'][0]
        elif isinstance(regla['lab'], str):
            diagnostico["lab"] = regla['lab']
    # Luego verificar lab_valores (estructura de indicadores)
    elif 'lab_valores' in regla and regla['lab_valores']:
        if isinstance(regla['lab_valores'], list) and len(regla['lab_valores']) > 0:
            # Usar el primer valor no vacío
            lab_val = next((v for v in regla['lab_valores'] if v != ""), None)
            if lab_val:
                diagnostico["lab"] = lab_val
        elif isinstance(regla['lab_valores'], str) and regla['lab_valores']:
            diagnostico["lab"] = regla['lab_valores']
    
    # Casos especiales de LAB según el código
    if codigo == 'Z019' and 'lab' not in diagnostico:
        diagnostico["lab"] = "DNT"
    elif codigo == '99199.22' and 'lab' not in diagnostico:
        diagnostico["lab"] = "N"  # Normal por defecto
    elif codigo == '99387' and 'lab' not in diagnostico:
        diagnostico["lab"] = "AS"  # Autosuficiente por defecto para VACAM
    elif codigo == '99215.03' and 'lab' not in diagnostico:
        diagnostico["lab"] = "AS"  # Autosuficiente por defecto para VACAM alternativo
    elif codigo in ['99209.02', '99209.04'] and 'lab' not in diagnostico:
        diagnostico["lab"] = "RSM"  # Riesgo de Salud Metabólica por defecto para valoración nutricional
    elif codigo == '99801':
        # Plan de atención integral - se maneja en la función principal
        pass
    
    return diagnostico

def generar_json_exportacion(df_filtrado, filtro_estado, curso_vida):
    """
    Genera el JSON de exportación para pacientes con paquetes incompletos
    Compatible con el script de automatización HIS-MINSA
    """
    pacientes_json = []
    
    # Filtrar según el estado seleccionado
    if filtro_estado == "Incompletos":
        # Obtener solo pacientes con paquete incompleto
        pacientes_procesar = []
        for dni in df_filtrado['pac_Numero_Documento'].unique():
            df_dni = df_filtrado[df_filtrado['pac_Numero_Documento'] == dni]
            if curso_vida == "Adulto (30-59 años)":
                resultado = verificar_paquete_adulto(df_dni, dni)
            elif curso_vida == "Joven (18-29 años)":
                resultado = verificar_paquete_joven(df_dni, dni)
            else:
                resultado = verificar_paquete_adulto_mayor(df_dni, dni)
            
            if not resultado['completo']:
                pacientes_procesar.append(dni)
    elif filtro_estado == "Casi Completos (1-2 faltantes)":
        # Filtrar por componentes faltantes
        pacientes_procesar = []
        # Determinar número total de componentes según curso de vida
        if curso_vida == "Adulto (30-59 años)":
            num_componentes_total = 7
        elif curso_vida == "Joven (18-29 años)":
            num_componentes_total = 6
        else:  # Adulto Mayor
            num_componentes_total = 7
            
        for dni in df_filtrado['pac_Numero_Documento'].unique():
            df_dni = df_filtrado[df_filtrado['pac_Numero_Documento'] == dni]
            if curso_vida == "Adulto (30-59 años)":
                resultado = verificar_paquete_adulto(df_dni, dni)
            elif curso_vida == "Joven (18-29 años)":
                resultado = verificar_paquete_joven(df_dni, dni)
            else:
                resultado = verificar_paquete_adulto_mayor(df_dni, dni)
            
            # Calcular componentes completados
            componentes_completados = sum(resultado['componentes'].values())
            componentes_faltantes = num_componentes_total - componentes_completados
            
            # Si le faltan 1 o 2 componentes
            if componentes_faltantes in [1, 2] and not resultado['completo']:
                pacientes_procesar.append(dni)
    else:
        return None
    
    # Procesar cada paciente
    for dni in pacientes_procesar[:100]:  # Limitar a 100 por rendimiento
        df_paciente = df_filtrado[df_filtrado['pac_Numero_Documento'] == dni]
        info_paciente = df_paciente.iloc[0]
        
        # Obtener códigos faltantes
        codigos_faltantes = obtener_codigos_faltantes_paquete(df_paciente, curso_vida)
        
        if codigos_faltantes:
            # Optimizar códigos antes de agregar
            codigos_optimizados = optimizar_codigos_exportacion(codigos_faltantes)
            
            paciente_json = {
                "dni": dni,
                "nombre": info_paciente['Paciente_Completo'],
                "edad": str(int(info_paciente['edad_anos'])),
                "sexo": info_paciente['pac_Genero'],
                "diagnosticos": codigos_optimizados
            }
            pacientes_json.append(paciente_json)
    
    # Estructura final del JSON
    fecha_actual = datetime.now()
    json_exportacion = {
        "fecha_exportacion": fecha_actual.isoformat(),
        "dia_his": str(fecha_actual.day),
        "fecha_atencion": fecha_actual.strftime("%Y-%m-%d"),
        "curso_vida": curso_vida,
        "tipo_correccion": "paquete_integral_incompleto",
        "total_pacientes": len(pacientes_json),
        "cambios_realizados": 0,
        "pacientes": pacientes_json
    }
    
    return json_exportacion

def generar_json_exportacion_personalizada(df_filtrado, pacientes_seleccionados, componentes_seleccionados, codigos_seleccionados_dict, curso_vida):
    """
    Genera JSON personalizado con selección específica de pacientes y códigos
    """
    pacientes_json = []
    
    # Obtener configuración de exportación
    exportar_solo_faltantes = st.session_state.get('exportar_solo_faltantes', True)
    
    # Obtener información de referencia según curso de vida
    if curso_vida == "Adulto (30-59 años)":
        paquete_info = PAQUETE_INTEGRAL_ADULTO
        componentes_disponibles = paquete_info['componentes_minimos']
        indicadores_ref = INDICADORES_ADULTO
    elif curso_vida == "Joven (18-29 años)":
        paquete_info = PAQUETE_INTEGRAL_JOVEN
        componentes_disponibles = paquete_info['componentes_minimos']
        indicadores_ref = INDICADORES_JOVEN
    else:
        paquete_info = PAQUETE_INTEGRAL_ADULTO_MAYOR
        componentes_disponibles = paquete_info['componentes_minimos']
        indicadores_ref = INDICADORES_ADULTO_MAYOR
    
    # Procesar cada paciente seleccionado
    for dni in pacientes_seleccionados:
        df_paciente = df_filtrado[df_filtrado['pac_Numero_Documento'] == dni]
        if df_paciente.empty:
            continue
            
        info_paciente = df_paciente.iloc[0]
        edad_paciente = info_paciente['edad_anos']
        
        # Recolectar códigos para este paciente
        codigos_paciente = []
        
        # Procesar cada componente seleccionado
        for comp_nombre in componentes_seleccionados:
            # Saltar el Plan de Atención Integral ya que se maneja por separado
            if comp_nombre == "Plan de Atención Integral":
                continue
                
            # Encontrar el componente
            componente = next((c for c in componentes_disponibles if c['componente'] == comp_nombre), None)
            
            if componente and 'indicador' in componente:
                indicador_key = componente['indicador']
                
                # Si hay códigos seleccionados específicos para este indicador
                if indicador_key in codigos_seleccionados_dict and codigos_seleccionados_dict[indicador_key]:
                    codigos_seleccionados_indicador = codigos_seleccionados_dict[indicador_key]
                    
                    # Agregar cada código seleccionado
                    for codigo_info in codigos_seleccionados_indicador:
                        # Verificar si debemos incluirlo según la configuración
                        if exportar_solo_faltantes and verificar_codigo_existe(df_paciente, codigo_info['codigo']):
                            continue  # Saltar si ya existe y solo queremos faltantes
                            
                        # Crear diagnóstico JSON
                        diagnostico = crear_diagnostico_json(codigo_info['regla'])
                        
                        # Aplicar lógica especial para casos específicos
                        if aplicar_logica_especial_codigo(codigo_info['codigo'], edad_paciente, df_paciente, curso_vida):
                            codigos_paciente.append(diagnostico)
                else:
                    # Si no está en el diccionario o está vacío, incluir todos los códigos del indicador
                    indicador_info = indicadores_ref.get(indicador_key, {})
                    if 'reglas' in indicador_info:
                        reglas = indicador_info['reglas']
                        
                        if isinstance(reglas, list):
                            for regla in reglas:
                                # Verificar si debemos incluirlo según la configuración
                                codigo_existe = verificar_codigo_existe(df_paciente, regla['codigo'])
                                if exportar_solo_faltantes and codigo_existe:
                                    continue  # Saltar si ya existe y solo queremos faltantes
                                
                                # Aplicar lógica especial solo para casos específicos
                                incluir_codigo = True
                                
                                # Caso especial: laboratorio para adultos 30-39
                                if (regla['codigo'] == 'Z017' and curso_vida == "Adulto (30-59 años)" and 
                                    edad_paciente >= 30 and edad_paciente <= 39):
                                    factores_riesgo = ["E65X", "E669", "E6691", "E6692", "E6693", "E6690", 
                                                     "Z720", "Z721", "Z723", "Z724", "Z783", "Z784"]
                                    incluir_codigo = any(df_paciente['Codigo_Item'].isin(factores_riesgo))
                                
                                if incluir_codigo:
                                    codigos_paciente.append(crear_diagnostico_json(regla))
                        
                        # Agregar laboratorio Z017 para adultos 40-59 si es valoración clínica
                        if (indicador_key == 'valoracion_clinica_lab' and 
                            curso_vida == "Adulto (30-59 años)" and 
                            edad_paciente >= 40 and edad_paciente <= 59):
                            
                            # Verificar si necesita Z017
                            if exportar_solo_faltantes:
                                if not verificar_codigo_existe(df_paciente, 'Z017'):
                                    codigos_paciente.append({
                                        "codigo": "Z017",
                                        "descripcion": "Z017 - Tamizaje laboratorial",
                                        "tipo": "D",
                                        "lab": ""
                                    })
                            else:
                                codigos_paciente.append({
                                    "codigo": "Z017",
                                    "descripcion": "Z017 - Tamizaje laboratorial", 
                                    "tipo": "D",
                                    "lab": ""
                                })
                        
                        elif isinstance(reglas, dict) and 'opcion_a' in reglas:
                            # Caso especial de opciones (ej: agudeza visual)
                            for codigo_info in reglas['opcion_a'].get('codigos', []):
                                codigo_existe = verificar_codigo_existe(df_paciente, codigo_info['codigo'])
                                if exportar_solo_faltantes and codigo_existe:
                                    continue  # Saltar si ya existe y solo queremos faltantes
                                    
                                codigos_paciente.append(crear_diagnostico_json(codigo_info))
            
            # Manejo especial para componentes con reglas por edad (sin indicador)
            elif 'reglas_30_39' in componente or 'reglas_40_59' in componente:
                if edad_paciente >= 30 and edad_paciente <= 39 and 'reglas_30_39' in componente:
                    for regla in componente['reglas_30_39']:
                        if not verificar_codigo_existe(df_paciente, regla['codigo']):
                            if 'condicion' in regla and regla['codigo'] == 'Z017':
                                # Verificar factores de riesgo
                                factores_riesgo = regla.get('factores_riesgo', [])
                                tiene_factores = any(df_paciente['Codigo_Item'].isin(factores_riesgo))
                                if tiene_factores:
                                    codigos_paciente.append(crear_diagnostico_json(regla))
                            else:
                                codigos_paciente.append(crear_diagnostico_json(regla))
                elif edad_paciente >= 40 and edad_paciente <= 59 and 'reglas_40_59' in componente:
                    for regla in componente['reglas_40_59']:
                        if not verificar_codigo_existe(df_paciente, regla['codigo']):
                            codigos_paciente.append(crear_diagnostico_json(regla))
        
        # Agregar plan de atención si está seleccionado
        if 'plan_atencion' in codigos_seleccionados_dict:
            plan_config = codigos_seleccionados_dict['plan_atencion']
            
            # Verificar si ya tiene plan elaborado
            tiene_plan_elaborado = not df_paciente[
                (df_paciente['Codigo_Item'] == '99801') & 
                (df_paciente['Valor_Lab'] == '1')
            ].empty
            
            # Verificar si ya tiene plan ejecutado
            tiene_plan_ejecutado = not df_paciente[
                (df_paciente['Codigo_Item'] == '99801') & 
                (df_paciente['Valor_Lab'] == 'TA')
            ].empty
            
            if plan_config.get('elaborado', False):
                if not exportar_solo_faltantes or not tiene_plan_elaborado:
                    codigos_paciente.append({
                        "codigo": "99801",
                        "descripcion": "99801 - Plan de Atención Integral Elaborado",
                        "tipo": "D",
                        "lab": "1"
                    })
            
            if plan_config.get('ejecutado', False):
                if not exportar_solo_faltantes or not tiene_plan_ejecutado:
                    codigos_paciente.append({
                        "codigo": "99801",
                        "descripcion": "99801 - Plan de Atención Integral Ejecutado",
                        "tipo": "D",
                        "lab": "TA"
                    })
        
        # Si hay códigos para este paciente, agregarlo al JSON
        if codigos_paciente:
            # Optimizar códigos antes de agregar
            codigos_optimizados = optimizar_codigos_exportacion(codigos_paciente)
            
            paciente_json = {
                "dni": dni,
                "nombre": info_paciente['Paciente_Completo'],
                "edad": str(int(edad_paciente)),
                "sexo": info_paciente['pac_Genero'],
                "diagnosticos": codigos_optimizados
            }
            pacientes_json.append(paciente_json)
    
    # Estructura final del JSON
    fecha_actual = datetime.now()
    json_exportacion = {
        "fecha_exportacion": fecha_actual.isoformat(),
        "dia_his": str(fecha_actual.day),
        "fecha_atencion": fecha_actual.strftime("%Y-%m-%d"),
        "curso_vida": curso_vida,
        "tipo_correccion": "paquete_integral_personalizado",
        "modo_exportacion": "seleccion_personalizada",
        "componentes_incluidos": componentes_seleccionados,
        "total_pacientes": len(pacientes_json),
        "total_diagnosticos": sum(len(p['diagnosticos']) for p in pacientes_json),
        "cambios_realizados": 0,
        "pacientes": pacientes_json
    }
    
    return json_exportacion

def aplicar_logica_especial_codigo(codigo, edad_paciente, df_paciente, curso_vida):
    """
    Aplica lógica especial para determinar si un código debe incluirse
    basado en edad, factores de riesgo u otras condiciones
    """
    # Laboratorio para adultos 30-39 años
    if codigo == 'Z017' and curso_vida == "Adulto (30-59 años)" and edad_paciente >= 30 and edad_paciente <= 39:
        # Verificar factores de riesgo
        factores_riesgo = ["E65X", "E669", "E6691", "E6692", "E6693", "E6690", 
                         "Z720", "Z721", "Z723", "Z724", "Z783", "Z784"]
        tiene_factores = any(df_paciente['Codigo_Item'].isin(factores_riesgo))
        return tiene_factores
    
    # Para adultos 40-59 y adultos mayores, laboratorio siempre
    if codigo == 'Z017' and (
        (curso_vida == "Adulto (30-59 años)" and edad_paciente >= 40) or
        curso_vida == "Adulto Mayor (60+ años)"
    ):
        return True
    
    # Por defecto, incluir el código
    return True

def optimizar_codigos_exportacion(codigos_list):
    """
    Optimiza la lista de códigos eliminando duplicados y agrupando consejerías
    """
    # Eliminar duplicados exactos
    codigos_unicos = {}
    for codigo in codigos_list:
        key = f"{codigo['codigo']}_{codigo.get('lab', '')}"
        if key not in codigos_unicos:
            codigos_unicos[key] = codigo
    
    # Convertir de vuelta a lista
    codigos_optimizados = list(codigos_unicos.values())
    
    # Identificar códigos de tamizaje de salud mental
    codigos_salud_mental = ['96150.01', '96150.02', '96150.03', '96150.04', '96150.07']
    consejerias_salud_mental = ['99402.01', '99402.09']
    
    # Verificar si hay tamizajes de salud mental
    tiene_tamizajes_sm = any(c['codigo'] in codigos_salud_mental for c in codigos_optimizados)
    
    if tiene_tamizajes_sm:
        # Eliminar todas las consejerías de salud mental existentes
        codigos_optimizados = [c for c in codigos_optimizados if c['codigo'] not in consejerias_salud_mental]
        
        # Agregar una sola consejería de salud mental (99402.09)
        codigos_optimizados.append({
            "codigo": "99402.09",
            "descripcion": "99402.09 - Consejería en salud mental",
            "tipo": "D",
            "lab": ""
        })
    
    return codigos_optimizados

if __name__ == "__main__":
    main()