#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador JSON HISMINSA - Sistema Inteligente para Generación de Indicadores
Desarrollado con tecnología avanzada para facilitar el registro de atenciones
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime, date
import math
from typing import Dict, List, Any, Optional, Tuple
import uuid
import locale

# Intentar configurar locale para español
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252')  # Windows
    except:
        pass  # Si falla, usar inglés por defecto

# Configuración de la página
st.set_page_config(
    page_title="Generador JSON HISMINSA",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Importar módulos de indicadores
from indicadores_joven import INDICADORES_JOVEN, PAQUETE_INTEGRAL_JOVEN
from indicadores_adulto import INDICADORES_ADULTO, PAQUETE_INTEGRAL_ADULTO
from indicadores_adulto_mayor import INDICADORES_ADULTO_MAYOR, PAQUETE_INTEGRAL_ADULTO_MAYOR

# ==============================================================================
# CONFIGURACIÓN Y CONSTANTES
# ==============================================================================

# Meses en español para mostrar fechas
MESES_ESPANOL = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
    5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
}

CURSOS_VIDA = {
    "Joven (18-29 años)": {"min": 18, "max": 29},
    "Adulto (30-59 años)": {"min": 30, "max": 59},
    "Adulto Mayor (60+ años)": {"min": 60, "max": 150}
}

FACTORES_RIESGO = {
    "obesidad": {
        "nombre": "Obesidad/Sobrepeso",
        "codigos": ["E65X", "E669", "E6691", "E6692", "E6693", "E6690"],
        "descripcion": "IMC ≥ 25"
    },
    "alcohol": {
        "nombre": "Consumo de Alcohol",
        "codigos": ["Z720", "Z721"],
        "descripcion": "Consumo problemático"
    },
    "drogas": {
        "nombre": "Consumo de Drogas",
        "codigos": ["Z723", "Z724"],
        "descripcion": "Consumo de sustancias"
    },
    "tabaco": {
        "nombre": "Consumo de Tabaco", 
        "codigos": ["Z783", "Z784"],
        "descripcion": "Fumador activo"
    }
}

# ==============================================================================
# FUNCIONES AUXILIARES
# ==============================================================================

def calcular_edad(fecha_nacimiento: date) -> int:
    """Calcula la edad en años"""
    hoy = date.today()
    edad = hoy.year - fecha_nacimiento.year
    if (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        edad -= 1
    return edad

def calcular_imc(peso: float, talla: float) -> Tuple[float, str]:
    """Calcula el IMC y retorna valor y clasificación"""
    if talla > 0 and peso > 0:
        talla_metros = talla / 100  # Convertir cm a metros
        imc = peso / (talla_metros ** 2)
        
        if imc < 18.5:
            clasificacion = "Bajo peso"
        elif imc < 25:
            clasificacion = "Normal"
        elif imc < 30:
            clasificacion = "Sobrepeso"
        else:
            clasificacion = "Obesidad"
            
        return round(imc, 2), clasificacion
    return 0, "No calculado"

def determinar_curso_vida(edad: int) -> Optional[str]:
    """Determina el curso de vida según la edad"""
    for curso, rango in CURSOS_VIDA.items():
        if rango["min"] <= edad <= rango["max"]:
            return curso
    return None

def generar_codigo_factor_riesgo(factor: str, tipo: str = "factor") -> Dict[str, Any]:
    """Genera código JSON para factor de riesgo"""
    if factor in FACTORES_RIESGO:
        info = FACTORES_RIESGO[factor]
        codigo = info["codigos"][0]  # Usar el primer código de la lista
        
        return {
            "codigo": codigo,
            "descripcion": f"{codigo} - {info['nombre']}",
            "tipo": "D" if tipo == "factor" else "R",
            "lab": ""
        }
    return None

# ==============================================================================
# INTERFAZ PRINCIPAL
# ==============================================================================

def main():
    st.title("🏥 Generador JSON HISMINSA")
    st.markdown("### Sistema Inteligente para Generación de Indicadores")
    
    # Inicializar session state
    if 'pacientes' not in st.session_state:
        st.session_state.pacientes = []
    if 'paciente_actual' not in st.session_state:
        st.session_state.paciente_actual = {}
    if 'indicadores_seleccionados' not in st.session_state:
        st.session_state.indicadores_seleccionados = {}
    
    # Sidebar para navegación
    with st.sidebar:
        st.markdown("## 📋 Navegación")
        modo = st.radio(
            "Selecciona el modo:",
            ["➕ Nuevo Paciente", "📊 Pacientes Registrados", "💾 Generar JSON"],
            key="modo_nav"
        )
        
        st.markdown("---")
        st.markdown("### 🔧 Configuración")
        
        # Configuración global
        incluir_factores_riesgo = st.checkbox("Incluir factores de riesgo", value=True)
        modo_paquete = st.checkbox("Generar paquete integral", value=True)
        
    # Contenido principal según modo
    if modo == "➕ Nuevo Paciente":
        registrar_nuevo_paciente(incluir_factores_riesgo, modo_paquete)
    elif modo == "📊 Pacientes Registrados":
        mostrar_pacientes_registrados()
    else:  # Generar JSON
        generar_json_final()

def registrar_nuevo_paciente(incluir_factores_riesgo: bool, modo_paquete: bool):
    """Interfaz para registrar un nuevo paciente"""
    st.markdown("## 👤 Registro de Nuevo Paciente")
    
    # Crear tabs para organizar la información
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Datos Básicos", "📏 Antropometría", "⚠️ Factores de Riesgo", "🎯 Indicadores"])
    
    with tab1:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            dni = st.text_input("DNI:", max_chars=8, key="dni_input")
            apellido_paterno = st.text_input("Apellido Paterno:", key="ap_paterno")
            
        with col2:
            nombres = st.text_input("Nombres:", key="nombres_input")
            apellido_materno = st.text_input("Apellido Materno:", key="ap_materno")
            
        with col3:
            # Opción para elegir método de ingreso
            metodo_fecha = st.radio(
                "Método de ingreso:",
                ["📅 Calendario", "⌨️ Escribir fecha"],
                horizontal=True,
                key="metodo_fecha"
            )
            
            if metodo_fecha == "📅 Calendario":
                fecha_nacimiento = st.date_input(
                    "Fecha de Nacimiento:",
                    max_value=date.today(),
                    min_value=date(1900, 1, 1),  # Permitir desde 1900
                    value=date(1980, 1, 1),  # Valor por defecto más razonable
                    key="fecha_nac_cal"
                )
            else:
                # Ingreso manual de fecha
                fecha_manual = st.text_input(
                    "Fecha (DD/MM/AAAA):",
                    placeholder="27/07/1930",
                    help="Formato: día/mes/año",
                    key="fecha_manual"
                )
                
                # Validar y convertir fecha manual
                if fecha_manual:
                    try:
                        partes = fecha_manual.split('/')
                        if len(partes) == 3:
                            dia, mes, anio = map(int, partes)
                            fecha_nacimiento = date(anio, mes, dia)
                            
                            # Validar que no sea fecha futura
                            if fecha_nacimiento > date.today():
                                st.error("❌ La fecha no puede ser futura")
                                fecha_nacimiento = None
                            elif fecha_nacimiento.year < 1900:
                                st.error("❌ El año debe ser mayor a 1900")
                                fecha_nacimiento = None
                            else:
                                # Mostrar fecha en español
                                mes_esp = MESES_ESPANOL.get(fecha_nacimiento.month, fecha_nacimiento.strftime('%B'))
                                st.success(f"✅ Fecha válida: {fecha_nacimiento.day} de {mes_esp} de {fecha_nacimiento.year}")
                        else:
                            st.error("❌ Formato incorrecto. Use DD/MM/AAAA")
                            fecha_nacimiento = None
                    except ValueError as e:
                        st.error("❌ Fecha inválida. Verifique el formato DD/MM/AAAA")
                        fecha_nacimiento = None
                else:
                    fecha_nacimiento = None
                    
            sexo = st.selectbox("Sexo:", ["M", "F"], key="sexo_input")
        
        # Calcular edad y curso de vida
        if fecha_nacimiento:
            edad = calcular_edad(fecha_nacimiento)
            curso_vida = determinar_curso_vida(edad)
            
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**Edad:** {edad} años")
            with col2:
                if curso_vida:
                    st.success(f"**Curso de vida:** {curso_vida}")
                else:
                    st.error("Edad fuera de rango (18-150 años)")
        
        # Fecha de atención
        st.markdown("### 📅 Datos de la Atención")
        fecha_atencion = st.date_input(
            "Fecha de Atención:",
            value=date.today(),
            key="fecha_atencion"
        )
        
    with tab2:
        st.markdown("### 📏 Medidas Antropométricas")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            peso = st.number_input("Peso (kg):", min_value=0.0, max_value=300.0, step=0.1, key="peso_input")
            talla = st.number_input("Talla (cm):", min_value=0.0, max_value=250.0, step=0.1, key="talla_input")
            
        with col2:
            pab = st.number_input("Perímetro Abdominal (cm):", min_value=0.0, max_value=200.0, step=0.1, key="pab_input")
            
            # Calcular IMC
            if peso > 0 and talla > 0:
                imc, clasificacion = calcular_imc(peso, talla)
                
                # Mostrar resultado con color según clasificación
                if clasificacion == "Normal":
                    st.success(f"**IMC:** {imc} - {clasificacion}")
                elif clasificacion == "Sobrepeso":
                    st.warning(f"**IMC:** {imc} - {clasificacion}")
                else:
                    st.error(f"**IMC:** {imc} - {clasificacion}")
                
                # Determinar código de valoración nutricional
                if clasificacion in ["Sobrepeso", "Obesidad"]:
                    lab_nutricional = "RSM"  # Riesgo de Salud Metabólica
                else:
                    lab_nutricional = "N"  # Normal
                    
                st.info(f"**Código LAB Nutricional:** {lab_nutricional}")
        
        with col3:
            presion_sistolica = st.number_input("Presión Sistólica:", min_value=0, max_value=300, key="pa_sis")
            presion_diastolica = st.number_input("Presión Diastólica:", min_value=0, max_value=200, key="pa_dia")
            
            # Determinar código de presión arterial
            if presion_sistolica > 0 and presion_diastolica > 0:
                if presion_sistolica >= 140 or presion_diastolica >= 90:
                    lab_presion = "A"  # Alterado
                    st.warning(f"**Presión Arterial:** Alterada")
                else:
                    lab_presion = "N"  # Normal
                    st.success(f"**Presión Arterial:** Normal")
    
    with tab3:
        st.markdown("### ⚠️ Factores de Riesgo")
        
        # Detección automática
        factores_automaticos = []
        if 'imc' in locals() and clasificacion in ["Sobrepeso", "Obesidad"]:
            factores_automaticos.append("obesidad")
            st.info("✓ Sobrepeso/Obesidad detectado automáticamente")
        
        # Selección manual
        st.markdown("**Selecciona factores de riesgo adicionales:**")
        
        col1, col2 = st.columns(2)
        factores_seleccionados = []
        
        with col1:
            if st.checkbox("🍺 Consumo de Alcohol", key="factor_alcohol"):
                factores_seleccionados.append("alcohol")
            if st.checkbox("🚬 Consumo de Tabaco", key="factor_tabaco"):
                factores_seleccionados.append("tabaco")
                
        with col2:
            if st.checkbox("💊 Consumo de Drogas", key="factor_drogas"):
                factores_seleccionados.append("drogas")
            if st.checkbox("🩺 Otros factores (HTA, DM)", key="factor_otros"):
                st.text_input("Especificar:", key="otros_factores")
        
        # Combinar factores
        todos_factores = list(set(factores_automaticos + factores_seleccionados))
        
        if todos_factores:
            st.markdown("### 📋 Resumen de Factores de Riesgo:")
            for factor in todos_factores:
                if factor in FACTORES_RIESGO:
                    st.write(f"• {FACTORES_RIESGO[factor]['nombre']}")
    
    with tab4:
        if curso_vida:
            seleccionar_indicadores(curso_vida, edad, todos_factores if 'todos_factores' in locals() else [], modo_paquete)
        else:
            st.warning("⚠️ Primero completa los datos básicos del paciente")
    
    # Botón para agregar paciente
    if st.button("➕ Agregar Paciente", type="primary", key="btn_agregar"):
        # Validar que haya fecha de nacimiento
        if 'fecha_nacimiento' not in locals() or fecha_nacimiento is None:
            st.error("❌ Debe ingresar una fecha de nacimiento válida")
        elif not curso_vida:
            st.error("❌ La edad del paciente está fuera del rango permitido (18+ años)")
        elif validar_datos_paciente(dni, nombres, apellido_paterno):
            # Construir objeto paciente
            paciente = {
                "id": str(uuid.uuid4()),
                "dni": dni,
                "nombre_completo": f"{apellido_paterno} {apellido_materno or ''} {nombres}".strip(),
                "nombres": nombres,
                "apellido_paterno": apellido_paterno,
                "apellido_materno": apellido_materno or "",
                "fecha_nacimiento": fecha_nacimiento.isoformat(),
                "edad": edad,
                "sexo": sexo,
                "curso_vida": curso_vida,
                "fecha_atencion": fecha_atencion.isoformat(),
                "antropometria": {
                    "peso": peso,
                    "talla": talla,
                    "imc": imc if 'imc' in locals() else 0,
                    "clasificacion_imc": clasificacion if 'clasificacion' in locals() else "",
                    "pab": pab,
                    "presion_sistolica": presion_sistolica if 'presion_sistolica' in locals() else 0,
                    "presion_diastolica": presion_diastolica if 'presion_diastolica' in locals() else 0,
                    "lab_nutricional": lab_nutricional if 'lab_nutricional' in locals() else "",
                    "lab_presion": lab_presion if 'lab_presion' in locals() else ""
                },
                "factores_riesgo": todos_factores if 'todos_factores' in locals() else [],
                "indicadores_seleccionados": st.session_state.get('indicadores_temp', {}),
                "modo_paquete": modo_paquete
            }
            
            st.session_state.pacientes.append(paciente)
            st.success(f"✅ Paciente {nombres} {apellido_paterno} agregado correctamente")
            st.balloons()
            
            # Limpiar campos
            if st.button("🔄 Limpiar formulario"):
                st.rerun()

def seleccionar_indicadores(curso_vida: str, edad: int, factores_riesgo: List[str], modo_paquete: bool):
    """Interfaz para seleccionar indicadores según curso de vida"""
    st.markdown("### 🎯 Selección de Indicadores")
    
    # Obtener indicadores según curso de vida
    if curso_vida == "Joven (18-29 años)":
        indicadores = INDICADORES_JOVEN
        paquete = PAQUETE_INTEGRAL_JOVEN
    elif curso_vida == "Adulto (30-59 años)":
        indicadores = INDICADORES_ADULTO
        paquete = PAQUETE_INTEGRAL_ADULTO
    else:
        indicadores = INDICADORES_ADULTO_MAYOR
        paquete = PAQUETE_INTEGRAL_ADULTO_MAYOR
    
    # Modo de selección
    modo_seleccion = st.radio(
        "Modo de selección:",
        ["Paquete Integral Completo", "Indicadores Individuales", "Personalizado"],
        key="modo_seleccion"
    )
    
    indicadores_seleccionados = {}
    
    if modo_seleccion == "Paquete Integral Completo":
        st.info(f"📦 Se generarán todos los códigos del {paquete['nombre']}")
        
        # Mostrar componentes del paquete
        st.markdown("**Componentes incluidos:**")
        for comp in paquete['componentes_minimos']:
            st.write(f"✓ {comp['componente']}")
        
        # Agregar plan de atención
        st.write("✓ Plan de Atención Integral (Elaborado y Ejecutado)")
        
        # Guardar selección
        indicadores_seleccionados['modo'] = 'paquete_completo'
        indicadores_seleccionados['componentes'] = [c['componente'] for c in paquete['componentes_minimos']]
        
    elif modo_seleccion == "Indicadores Individuales":
        st.markdown("**Selecciona los indicadores a generar:**")
        
        # Crear columnas para mejor visualización
        col1, col2 = st.columns(2)
        
        indicadores_elegidos = []
        
        for idx, (key, info) in enumerate(indicadores.items()):
            # Saltar indicadores especiales
            if key in ['plan_atencion_elaborado', 'plan_atencion_ejecutado']:
                continue
                
            col = col1 if idx % 2 == 0 else col2
            
            with col:
                if st.checkbox(info['nombre'], key=f"ind_{key}"):
                    indicadores_elegidos.append(key)
        
        # Plan de atención
        st.markdown("**Plan de Atención:**")
        col1, col2 = st.columns(2)
        with col1:
            plan_elaborado = st.checkbox("Plan Elaborado", key="plan_elab")
        with col2:
            plan_ejecutado = st.checkbox("Plan Ejecutado", key="plan_ejec")
        
        indicadores_seleccionados['modo'] = 'individual'
        indicadores_seleccionados['indicadores'] = indicadores_elegidos
        indicadores_seleccionados['plan_elaborado'] = plan_elaborado
        indicadores_seleccionados['plan_ejecutado'] = plan_ejecutado
        
    else:  # Personalizado
        st.markdown("**Personalización avanzada:**")
        
        # Permitir selección detallada por componente
        componentes_personalizados = {}
        
        for comp in paquete['componentes_minimos']:
            with st.expander(f"📌 {comp['componente']}"):
                incluir = st.checkbox(f"Incluir {comp['componente']}", value=True, key=f"comp_{comp['componente']}")
                
                if incluir and 'indicador' in comp:
                    # Mostrar códigos del indicador
                    indicador_info = indicadores.get(comp['indicador'], {})
                    if 'reglas' in indicador_info:
                        st.markdown("**Códigos incluidos:**")
                        
                        if isinstance(indicador_info['reglas'], list):
                            for regla in indicador_info['reglas']:
                                codigo_desc = f"{regla['codigo']} - {regla.get('descripcion', '')}"
                                if 'lab_valores' in regla:
                                    codigo_desc += f" [LAB: {regla['lab_valores'][0] if regla['lab_valores'] else ''}]"
                                st.write(f"• {codigo_desc}")
                
                if incluir:
                    componentes_personalizados[comp['componente']] = comp.get('indicador', '')
        
        indicadores_seleccionados['modo'] = 'personalizado'
        indicadores_seleccionados['componentes_personalizados'] = componentes_personalizados
    
    # Configuraciones especiales según curso de vida
    if curso_vida == "Adulto (30-59 años)" and edad >= 40:
        st.warning("⚠️ Para adultos 40-59 años, se incluirá automáticamente el tamizaje laboratorial (Z017)")
    
    # Guardar en session state temporal
    st.session_state.indicadores_temp = indicadores_seleccionados

def validar_datos_paciente(dni: str, nombres: str, apellido_paterno: str) -> bool:
    """Valida que los datos mínimos del paciente estén completos"""
    if not dni or len(dni) < 8:
        st.error("❌ El DNI debe tener 8 dígitos")
        return False
    if not nombres:
        st.error("❌ Los nombres son obligatorios")
        return False
    if not apellido_paterno:
        st.error("❌ El apellido paterno es obligatorio")
        return False
    return True

def mostrar_pacientes_registrados():
    """Muestra la lista de pacientes registrados"""
    st.markdown("## 📊 Pacientes Registrados")
    
    if not st.session_state.pacientes:
        st.info("No hay pacientes registrados aún")
        return
    
    # Crear DataFrame para visualización
    df_pacientes = pd.DataFrame([
        {
            "DNI": p['dni'],
            "Nombre": p['nombre_completo'],
            "Edad": p['edad'],
            "Sexo": p['sexo'],
            "Curso de Vida": p['curso_vida'],
            "Fecha Atención": p['fecha_atencion'],
            "IMC": f"{p['antropometria']['imc']} ({p['antropometria']['clasificacion_imc']})",
            "Factores Riesgo": len(p['factores_riesgo']),
            "ID": p['id']
        }
        for p in st.session_state.pacientes
    ])
    
    # Mostrar tabla interactiva
    st.dataframe(
        df_pacientes.drop(columns=['ID']),
        use_container_width=True,
        hide_index=True
    )
    
    # Acciones
    st.markdown("### 🔧 Acciones")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ Limpiar todos", type="secondary"):
            st.session_state.pacientes = []
            st.rerun()
    
    with col2:
        # Selector para eliminar paciente individual
        if st.session_state.pacientes:
            paciente_eliminar = st.selectbox(
                "Eliminar paciente:",
                options=[f"{p['dni']} - {p['nombre_completo']}" for p in st.session_state.pacientes],
                key="sel_eliminar"
            )
            
            if st.button("🗑️ Eliminar seleccionado"):
                dni_eliminar = paciente_eliminar.split(" - ")[0]
                st.session_state.pacientes = [
                    p for p in st.session_state.pacientes if p['dni'] != dni_eliminar
                ]
                st.success("Paciente eliminado")
                st.rerun()

def generar_json_final():
    """Genera el JSON final con todos los pacientes"""
    st.markdown("## 💾 Generar JSON Final")
    
    if not st.session_state.pacientes:
        st.warning("No hay pacientes registrados para generar JSON")
        return
    
    # Configuración de exportación
    st.markdown("### ⚙️ Configuración de Exportación")
    
    col1, col2 = st.columns(2)
    with col1:
        dia_his = st.number_input("Día HIS:", min_value=1, max_value=31, value=datetime.now().day)
        incluir_diagnosticos_riesgo = st.checkbox("Incluir diagnósticos de factores de riesgo", value=True)
        
    with col2:
        tipo_correccion = st.selectbox(
            "Tipo de corrección:",
            ["registro_nuevo", "correccion_paquete", "actualizacion_indicador"]
        )
    
    # Vista previa
    st.markdown("### 👁️ Vista Previa del JSON")
    
    # Generar JSON
    json_data = generar_json_exportacion(
        st.session_state.pacientes,
        dia_his,
        tipo_correccion,
        incluir_diagnosticos_riesgo
    )
    
    # Mostrar estadísticas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Pacientes", json_data['total_pacientes'])
    with col2:
        total_diagnosticos = sum(len(p['diagnosticos']) for p in json_data['pacientes'])
        st.metric("Total Diagnósticos", total_diagnosticos)
    with col3:
        st.metric("Día HIS", json_data['dia_his'])
    with col4:
        st.metric("Tipo", json_data['tipo_correccion'])
    
    # Mostrar JSON con formato
    with st.expander("📄 Ver JSON completo", expanded=True):
        st.json(json_data)
    
    # Botón de descarga
    json_str = json.dumps(json_data, indent=2, ensure_ascii=False)
    
    st.download_button(
        label="⬇️ Descargar JSON",
        data=json_str,
        file_name=f"hisminsa_generado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        type="primary"
    )
    
    # Análisis del JSON
    with st.expander("📊 Análisis del JSON generado"):
        analizar_json_generado(json_data)

def generar_json_exportacion(pacientes: List[Dict], dia_his: int, tipo_correccion: str, incluir_factores: bool) -> Dict:
    """Genera el JSON final con todos los pacientes y sus códigos"""
    pacientes_json = []
    
    for paciente in pacientes:
        diagnosticos = []
        
        # Generar códigos según la selección
        if paciente.get('indicadores_seleccionados', {}).get('modo') == 'paquete_completo':
            diagnosticos = generar_codigos_paquete_completo(paciente, incluir_factores)
        elif paciente.get('indicadores_seleccionados', {}).get('modo') == 'individual':
            diagnosticos = generar_codigos_individuales(paciente, incluir_factores)
        else:  # Personalizado
            diagnosticos = generar_codigos_personalizados(paciente, incluir_factores)
        
        # Agregar factores de riesgo si corresponde
        if incluir_factores and paciente.get('factores_riesgo'):
            for factor in paciente['factores_riesgo']:
                codigo_factor = generar_codigo_factor_riesgo(factor, "factor")
                if codigo_factor and codigo_factor not in diagnosticos:
                    diagnosticos.append(codigo_factor)
        
        # Construir objeto paciente para JSON
        paciente_json = {
            "dni": paciente['dni'],
            "nombre": paciente['nombre_completo'],
            "edad": str(paciente['edad']),
            "sexo": paciente['sexo'],
            "diagnosticos": diagnosticos
        }
        
        pacientes_json.append(paciente_json)
    
    # Estructura final
    fecha_actual = datetime.now()
    
    return {
        "fecha_exportacion": fecha_actual.isoformat(),
        "dia_his": str(dia_his),
        "fecha_atencion": fecha_actual.strftime("%Y-%m-%d"),
        "tipo_correccion": tipo_correccion,
        "total_pacientes": len(pacientes_json),
        "cambios_realizados": 0,
        "pacientes": pacientes_json
    }

def generar_codigos_paquete_completo(paciente: Dict, incluir_factores: bool) -> List[Dict]:
    """Genera todos los códigos del paquete integral"""
    diagnosticos = []
    curso_vida = paciente['curso_vida']
    edad = paciente['edad']
    
    # Obtener configuración según curso de vida
    if curso_vida == "Joven (18-29 años)":
        indicadores = INDICADORES_JOVEN
        paquete = PAQUETE_INTEGRAL_JOVEN
    elif curso_vida == "Adulto (30-59 años)":
        indicadores = INDICADORES_ADULTO
        paquete = PAQUETE_INTEGRAL_ADULTO
    else:
        indicadores = INDICADORES_ADULTO_MAYOR
        paquete = PAQUETE_INTEGRAL_ADULTO_MAYOR
    
    # Procesar cada componente del paquete
    for componente in paquete['componentes_minimos']:
        if 'indicador' in componente:
            indicador_key = componente['indicador']
            indicador_info = indicadores.get(indicador_key, {})
            
            if 'reglas' in indicador_info:
                # Procesar reglas
                diagnosticos.extend(procesar_reglas_indicador(
                    indicador_info['reglas'], 
                    paciente,
                    indicador_key
                ))
    
    # Agregar plan de atención
    diagnosticos.extend([
        {
            "codigo": "99801",
            "descripcion": "99801 - Plan de Atención Integral Elaborado",
            "tipo": "D",
            "lab": "1"
        },
        {
            "codigo": "99801",
            "descripcion": "99801 - Plan de Atención Integral Ejecutado",
            "tipo": "D",
            "lab": "TA"
        }
    ])
    
    # Aplicar optimizaciones
    diagnosticos = optimizar_lista_diagnosticos(diagnosticos)
    
    return diagnosticos

def generar_codigos_individuales(paciente: Dict, incluir_factores: bool) -> List[Dict]:
    """Genera códigos para indicadores seleccionados individualmente"""
    diagnosticos = []
    curso_vida = paciente['curso_vida']
    
    # Obtener indicadores según curso de vida
    if curso_vida == "Joven (18-29 años)":
        indicadores = INDICADORES_JOVEN
    elif curso_vida == "Adulto (30-59 años)":
        indicadores = INDICADORES_ADULTO
    else:
        indicadores = INDICADORES_ADULTO_MAYOR
    
    # Procesar indicadores seleccionados
    for indicador_key in paciente['indicadores_seleccionados'].get('indicadores', []):
        indicador_info = indicadores.get(indicador_key, {})
        
        if 'reglas' in indicador_info:
            diagnosticos.extend(procesar_reglas_indicador(
                indicador_info['reglas'],
                paciente,
                indicador_key
            ))
    
    # Agregar plan si está seleccionado
    if paciente['indicadores_seleccionados'].get('plan_elaborado'):
        diagnosticos.append({
            "codigo": "99801",
            "descripcion": "99801 - Plan de Atención Integral Elaborado",
            "tipo": "D",
            "lab": "1"
        })
    
    if paciente['indicadores_seleccionados'].get('plan_ejecutado'):
        diagnosticos.append({
            "codigo": "99801",
            "descripcion": "99801 - Plan de Atención Integral Ejecutado",
            "tipo": "D",
            "lab": "TA"
        })
    
    return optimizar_lista_diagnosticos(diagnosticos)

def generar_codigos_personalizados(paciente: Dict, incluir_factores: bool) -> List[Dict]:
    """Genera códigos para selección personalizada"""
    # Similar a individuales pero con lógica personalizada
    return generar_codigos_individuales(paciente, incluir_factores)

def procesar_reglas_indicador(reglas: Any, paciente: Dict, indicador_key: str) -> List[Dict]:
    """Procesa las reglas de un indicador y genera los diagnósticos"""
    diagnosticos = []
    edad = paciente['edad']
    curso_vida = paciente['curso_vida']
    
    if isinstance(reglas, list):
        for regla in reglas:
            # Aplicar lógica especial según indicador
            incluir = True
            
            # Caso especial: laboratorio para adultos
            if (regla.get('codigo') == 'Z017' and 
                curso_vida == "Adulto (30-59 años)" and 
                edad >= 30 and edad <= 39):
                # Para 30-39 años, no incluir laboratorio (simplificado)
                incluir = False
            
            if incluir:
                diagnostico = {
                    "codigo": regla['codigo'],
                    "descripcion": f"{regla['codigo']} - {regla.get('descripcion', '')}",
                    "tipo": regla.get('tipo_dx', 'D')
                }
                
                # Agregar valor LAB
                diagnostico["lab"] = obtener_valor_lab(regla, paciente, indicador_key)
                
                diagnosticos.append(diagnostico)
    
    # Manejar casos especiales por indicador
    if indicador_key == 'valoracion_clinica_lab' and curso_vida == "Adulto (30-59 años)" and edad >= 40:
        # Agregar laboratorio para adultos 40-59
        diagnosticos.append({
            "codigo": "Z017",
            "descripcion": "Z017 - Tamizaje laboratorial",
            "tipo": "D",
            "lab": ""
        })
    
    return diagnosticos

def obtener_valor_lab(regla: Dict, paciente: Dict, indicador_key: str) -> str:
    """Determina el valor LAB apropiado según el contexto"""
    codigo = regla.get('codigo', '')
    
    # Valores LAB especiales por código
    if codigo == 'Z019':
        return "DNT"
    elif codigo == '99199.22':
        # Presión arterial
        return paciente['antropometria'].get('lab_presion', 'N')
    elif codigo in ['99209.02', '99209.04']:
        # Valoración nutricional
        return paciente['antropometria'].get('lab_nutricional', 'RSM')
    elif codigo == '99387' or codigo == '99215.03':
        # VACAM
        return "AS"
    
    # Si tiene lab_valores en la regla
    if 'lab_valores' in regla:
        if isinstance(regla['lab_valores'], list) and regla['lab_valores']:
            return regla['lab_valores'][0] if regla['lab_valores'][0] else ""
        elif isinstance(regla['lab_valores'], str):
            return regla['lab_valores']
    
    # Si tiene lab directo
    if 'lab' in regla:
        if isinstance(regla['lab'], list):
            return regla['lab'][0]
        return regla['lab']
    
    return ""

def optimizar_lista_diagnosticos(diagnosticos: List[Dict]) -> List[Dict]:
    """Optimiza la lista de diagnósticos eliminando duplicados y aplicando reglas"""
    # Eliminar duplicados
    vistos = set()
    diagnosticos_unicos = []
    
    for diag in diagnosticos:
        key = f"{diag['codigo']}_{diag.get('lab', '')}"
        if key not in vistos:
            vistos.add(key)
            diagnosticos_unicos.append(diag)
    
    # Aplicar optimización de salud mental
    codigos_salud_mental = ['96150.01', '96150.02', '96150.03', '96150.04', '96150.07']
    tiene_tamizajes_sm = any(d['codigo'] in codigos_salud_mental for d in diagnosticos_unicos)
    
    if tiene_tamizajes_sm:
        # Eliminar consejerías múltiples de salud mental
        diagnosticos_unicos = [
            d for d in diagnosticos_unicos 
            if d['codigo'] not in ['99402.01', '99402.09']
        ]
        
        # Agregar una sola consejería
        diagnosticos_unicos.append({
            "codigo": "99402.09",
            "descripcion": "99402.09 - Consejería en salud mental",
            "tipo": "D",
            "lab": ""
        })
    
    return diagnosticos_unicos

def analizar_json_generado(json_data: Dict):
    """Muestra análisis del JSON generado"""
    st.markdown("### 📊 Análisis del JSON")
    
    # Contar códigos por tipo
    conteo_codigos = {}
    for paciente in json_data['pacientes']:
        for diag in paciente['diagnosticos']:
            codigo = diag['codigo']
            conteo_codigos[codigo] = conteo_codigos.get(codigo, 0) + 1
    
    # Mostrar tabla de frecuencias
    df_frecuencias = pd.DataFrame(
        [(k, v) for k, v in conteo_codigos.items()],
        columns=['Código', 'Frecuencia']
    ).sort_values('Frecuencia', ascending=False)
    
    st.dataframe(df_frecuencias, use_container_width=True, hide_index=True)
    
    # Verificaciones
    st.markdown("### ✅ Verificaciones")
    
    # Verificar planes
    planes_elaborados = sum(1 for p in json_data['pacientes'] 
                           for d in p['diagnosticos'] 
                           if d['codigo'] == '99801' and d.get('lab') == '1')
    planes_ejecutados = sum(1 for p in json_data['pacientes'] 
                           for d in p['diagnosticos'] 
                           if d['codigo'] == '99801' and d.get('lab') == 'TA')
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Planes Elaborados", planes_elaborados)
    with col2:
        st.metric("Planes Ejecutados", planes_ejecutados)

if __name__ == "__main__":
    main()