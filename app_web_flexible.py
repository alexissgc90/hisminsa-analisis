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
warnings.filterwarnings('ignore', category=UserWarning)

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
        'MaestroPaciente952732.csv': os.path.exists(os.path.join(base_path, 'MaestroPaciente952732.csv')),
        'MaestroPersonal951318.csv': os.path.exists(os.path.join(base_path, 'MaestroPersonal951318.csv')),
        'MaestroRegistrador952399.csv': os.path.exists(os.path.join(base_path, 'MaestroRegistrador952399.csv'))
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
        df_pacientes = pd.read_csv(os.path.join(base_path, 'MaestroPaciente952732.csv'), encoding='latin-1')
        df_personal = pd.read_csv(os.path.join(base_path, 'MaestroPersonal951318.csv'), encoding='latin-1')
        df_registradores = pd.read_csv(os.path.join(base_path, 'MaestroRegistrador952399.csv'), encoding='latin-1')
        
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
    establecimientos = ['Todos'] + sorted(df['Id_Establecimiento'].unique().tolist())
    establecimiento_sel = st.sidebar.selectbox(
        "Establecimiento:",
        establecimientos
    )
    
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
    
    return {
        'fecha_min': pd.to_datetime(fecha_min),
        'fecha_max': pd.to_datetime(fecha_max),
        'establecimiento': establecimiento_sel,
        'edad_min': edad_min,
        'edad_max': edad_max,
        'dni': dni_buscar,
        'codigo': codigo_buscar,
        'turno': turno_sel,
        'genero': genero_sel
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
        df_filtrado = df_filtrado[df_filtrado['Id_Establecimiento'] == filtros['establecimiento']]
    
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
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Tabla", "📈 Gráficos", "📅 Temporal", "📋 Resumen"])
        
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

if __name__ == "__main__":
    main()