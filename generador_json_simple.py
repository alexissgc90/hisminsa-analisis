#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador JSON HISMINSA - Versión Simplificada
Sistema rápido y práctico para generar JSON de indicadores
"""

import streamlit as st
import json
from datetime import datetime, date
from typing import Dict, List, Optional

# Configuración de la página
st.set_page_config(
    page_title="Generador JSON Simple - HISMINSA",
    page_icon="🏥",
    layout="wide"
)

# Importar módulos de indicadores
from indicadores_joven import INDICADORES_JOVEN, PAQUETE_INTEGRAL_JOVEN
from indicadores_adulto import INDICADORES_ADULTO, PAQUETE_INTEGRAL_ADULTO
from indicadores_adulto_mayor import INDICADORES_ADULTO_MAYOR, PAQUETE_INTEGRAL_ADULTO_MAYOR

# ==============================================================================
# CONFIGURACIÓN SIMPLIFICADA
# ==============================================================================

CURSOS_VIDA = {
    "joven": {"min": 18, "max": 29, "nombre": "Joven (18-29 años)"},
    "adulto": {"min": 30, "max": 59, "nombre": "Adulto (30-59 años)"},
    "adulto_mayor": {"min": 60, "max": 150, "nombre": "Adulto Mayor (60+ años)"}
}

# Códigos de factores de riesgo más comunes
FACTORES_RIESGO_SIMPLE = {
    "obesidad": {"codigo": "E669", "descripcion": "Obesidad"},
    "sobrepeso": {"codigo": "E66", "descripcion": "Sobrepeso"},
    "alcohol": {"codigo": "Z721", "descripcion": "Problemas con el alcohol"},
    "tabaco": {"codigo": "Z720", "descripcion": "Problemas con el tabaco"},
    "drogas": {"codigo": "Z722", "descripcion": "Problemas con drogas"},
    "hipertension": {"codigo": "I10X", "descripcion": "Hipertensión"},
    "diabetes": {"codigo": "E11", "descripcion": "Diabetes tipo 2"}
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

def determinar_curso_vida(edad: int) -> Optional[str]:
    """Determina el curso de vida según la edad"""
    for key, rango in CURSOS_VIDA.items():
        if rango["min"] <= edad <= rango["max"]:
            return key
    return None

def obtener_indicadores_por_curso(curso: str):
    """Obtiene los indicadores según el curso de vida"""
    if curso == "joven":
        return INDICADORES_JOVEN, PAQUETE_INTEGRAL_JOVEN
    elif curso == "adulto":
        return INDICADORES_ADULTO, PAQUETE_INTEGRAL_ADULTO
    else:
        return INDICADORES_ADULTO_MAYOR, PAQUETE_INTEGRAL_ADULTO_MAYOR

def generar_codigos_indicador(indicador_key: str, indicador_info: Dict, edad: int, curso: str) -> List[Dict]:
    """Genera los códigos para un indicador específico"""
    codigos = []
    
    # Caso especial: agudeza visual - agregar los 3 códigos completos
    if indicador_key == 'agudeza_visual':
        codigos = [
            {
                "codigo": "Z010",
                "descripcion": "Z010 - EXAMEN DE OJOS Y VISION",
                "tipo": "D",
                "lab": "N"
            },
            {
                "codigo": "99173",
                "descripcion": "99173 - DETERMINACION AGUDEZA VISUAL",
                "tipo": "D",
                "lab": "20"
            },
            {
                "codigo": "99401.16",
                "descripcion": "99401.16 - OYC SALUD OCULAR",
                "tipo": "D",
                "lab": ""
            }
        ]
        return codigos
    
    if 'reglas' in indicador_info and isinstance(indicador_info['reglas'], list):
        for regla in indicador_info['reglas']:
            # Aplicar lógica especial para laboratorio
            if regla.get('codigo') == 'Z017' and curso == "adulto" and edad < 40:
                continue  # No incluir laboratorio para adultos < 40 sin factores
            
            codigo_obj = {
                "codigo": regla['codigo'],
                "descripcion": f"{regla['codigo']} - {regla.get('descripcion', '')}",
                "tipo": regla.get('tipo_dx', 'D'),
                "lab": obtener_valor_lab_default(regla, indicador_key)
            }
            codigos.append(codigo_obj)
    
    # Caso especial: laboratorio para adultos 40-59
    if indicador_key == 'valoracion_clinica_lab' and curso == "adulto" and edad >= 40:
        codigos.append({
            "codigo": "Z017",
            "descripcion": "Z017 - Tamizaje laboratorial",
            "tipo": "D",
            "lab": ""
        })
    
    return codigos

def obtener_valor_lab_default(regla: Dict, indicador_key: str) -> str:
    """Obtiene el valor LAB por defecto para un código"""
    codigo = regla.get('codigo', '')
    
    # Valores LAB especiales por código (valores normales/no patológicos)
    valores_default = {
        'Z019': 'DNT',
        '99199.22': 'N',  # Presión normal
        '99209.02': 'N',  # Nutricional normal
        '99209.04': 'RSM',  # Nutricional - RSM por defecto para jóvenes
        '99387': 'AS',    # VACAM autosuficiente
        '99215.03': 'AS', # VACAM autosuficiente
        '99801': '1'      # Plan elaborado
    }
    
    if codigo in valores_default:
        return valores_default[codigo]
    
    # Si tiene lab_valores en la regla
    if 'lab_valores' in regla:
        if isinstance(regla['lab_valores'], list) and regla['lab_valores']:
            return regla['lab_valores'][0] if regla['lab_valores'][0] else ""
    
    return ""

def optimizar_codigos(codigos: List[Dict]) -> List[Dict]:
    """Optimiza la lista eliminando duplicados y aplicando reglas"""
    # Eliminar duplicados
    vistos = set()
    unicos = []
    
    for codigo in codigos:
        key = f"{codigo['codigo']}_{codigo.get('lab', '')}"
        if key not in vistos:
            vistos.add(key)
            unicos.append(codigo)
    
    # Optimizar salud mental: una sola consejería
    codigos_sm = ['96150.01', '96150.02', '96150.03', '96150.04', '96150.07']
    tiene_sm = any(c['codigo'] in codigos_sm for c in unicos)
    
    if tiene_sm:
        # Eliminar consejerías múltiples
        unicos = [c for c in unicos if c['codigo'] not in ['99402.01', '99402.09']]
        # Agregar una sola
        unicos.append({
            "codigo": "99402.09",
            "descripcion": "99402.09 - Consejería en salud mental",
            "tipo": "D",
            "lab": ""
        })
    
    return unicos

# ==============================================================================
# INTERFAZ PRINCIPAL
# ==============================================================================

def main():
    st.title("🏥 Generador JSON HISMINSA - Versión Simple")
    st.markdown("Sistema rápido para generar JSON de indicadores")
    
    # Sidebar para configuración global
    with st.sidebar:
        st.markdown("### ⚙️ Configuración")
        dia_his = st.number_input("Día HIS:", min_value=1, max_value=31, value=datetime.now().day)
        fecha_atencion = st.date_input("Fecha de atención:", value=date.today())
        tipo_correccion = st.selectbox(
            "Tipo:",
            ["registro_nuevo", "correccion_paquete", "actualizacion_indicador"]
        )
    
    # Contenedor principal
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 👤 Datos del Paciente")
        
        # DNI
        dni = st.text_input("DNI:", max_chars=8, placeholder="12345678")
        
        # Fecha de nacimiento
        fecha_manual = st.text_input(
            "Fecha de Nacimiento (DD/MM/AAAA):",
            placeholder="15/06/1980",
            help="Ejemplo: 27/07/1990"
        )
        
        # Campos opcionales
        with st.expander("Datos opcionales", expanded=False):
            nombre_completo = st.text_input("Nombre completo:", placeholder="APELLIDOS NOMBRES")
            sexo = st.selectbox("Sexo:", ["", "M", "F"], help="Dejar vacío si no se requiere")
        
        # Validar fecha y calcular edad
        edad = None
        curso_vida = None
        
        if fecha_manual and dni:
            try:
                partes = fecha_manual.split('/')
                if len(partes) == 3:
                    dia, mes, anio = map(int, partes)
                    fecha_nacimiento = date(anio, mes, dia)
                    edad = calcular_edad(fecha_nacimiento)
                    curso_vida = determinar_curso_vida(edad)
                    
                    if curso_vida:
                        st.success(f"✅ {CURSOS_VIDA[curso_vida]['nombre']}")
                        st.info(f"Edad: {edad} años")
                    else:
                        st.error("❌ Edad fuera de rango")
            except:
                st.error("❌ Formato de fecha inválido")
    
    with col2:
        if curso_vida and dni:
            st.markdown("### 🎯 Selección de Indicadores")
            
            # Obtener indicadores del curso de vida
            indicadores, paquete = obtener_indicadores_por_curso(curso_vida)
            
            # Tabs para organizar
            tab1, tab2, tab3 = st.tabs(["📦 Paquete Completo", "📋 Indicadores Individuales", "⚠️ Factores de Riesgo"])
            
            with tab1:
                st.info(f"Generar todos los códigos del {paquete['nombre']}")
                
                # Mostrar componentes
                cols = st.columns(2)
                for idx, comp in enumerate(paquete['componentes_minimos']):
                    col = cols[idx % 2]
                    with col:
                        st.write(f"✓ {comp['componente']}")
                
                incluir_plan = st.checkbox("Incluir Plan de Atención Integral", value=True)
                
                if st.button("🚀 Generar Paquete Completo", type="primary", key="btn_paquete"):
                    # Generar todos los códigos del paquete
                    todos_codigos = []
                    
                    for comp in paquete['componentes_minimos']:
                        if 'indicador' in comp:
                            ind_info = indicadores.get(comp['indicador'], {})
                            codigos = generar_codigos_indicador(comp['indicador'], ind_info, edad, curso_vida)
                            todos_codigos.extend(codigos)
                    
                    # IMPORTANTE: Agregar agudeza visual para TODOS los cursos de vida
                    # (puede que no esté en algunos paquetes pero es necesario)
                    agudeza_codigos = generar_codigos_indicador('agudeza_visual', {}, edad, curso_vida)
                    # Verificar si ya existe para no duplicar
                    codigos_existentes = {c['codigo'] for c in todos_codigos}
                    for codigo in agudeza_codigos:
                        if codigo['codigo'] not in codigos_existentes:
                            todos_codigos.extend(agudeza_codigos)
                            break  # Solo agregar una vez
                    
                    # Plan de atención
                    if incluir_plan:
                        todos_codigos.extend([
                            {"codigo": "99801", "descripcion": "99801 - Plan Elaborado", "tipo": "D", "lab": "1"},
                            {"codigo": "99801", "descripcion": "99801 - Plan Ejecutado", "tipo": "D", "lab": "TA"}
                        ])
                    
                    # Optimizar y generar JSON
                    nombre = nombre_completo if 'nombre_completo' in locals() else ""
                    sexo_val = sexo if 'sexo' in locals() else ""
                    generar_y_mostrar_json(dni, str(edad), todos_codigos, dia_his, tipo_correccion, nombre, sexo_val, fecha_atencion)
            
            with tab2:
                st.markdown("Selecciona indicadores específicos:")
                
                # Lista de indicadores con checkboxes
                indicadores_seleccionados = []
                
                cols = st.columns(2)
                for idx, (key, info) in enumerate(indicadores.items()):
                    if key not in ['plan_atencion_elaborado', 'plan_atencion_ejecutado']:
                        col = cols[idx % 2]
                        with col:
                            if st.checkbox(info['nombre'], key=f"ind_{key}"):
                                indicadores_seleccionados.append(key)
                
                # Plan de atención
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    plan_elab = st.checkbox("Plan Elaborado", key="plan_e")
                with col2:
                    plan_ejec = st.checkbox("Plan Ejecutado", key="plan_x")
                
                if st.button("🚀 Generar Indicadores Seleccionados", type="primary", key="btn_individual"):
                    if indicadores_seleccionados or plan_elab or plan_ejec:
                        todos_codigos = []
                        
                        # Procesar indicadores seleccionados
                        for ind_key in indicadores_seleccionados:
                            ind_info = indicadores.get(ind_key, {})
                            codigos = generar_codigos_indicador(ind_key, ind_info, edad, curso_vida)
                            todos_codigos.extend(codigos)
                        
                        # Planes
                        if plan_elab:
                            todos_codigos.append({"codigo": "99801", "descripcion": "99801 - Plan Elaborado", "tipo": "D", "lab": "1"})
                        if plan_ejec:
                            todos_codigos.append({"codigo": "99801", "descripcion": "99801 - Plan Ejecutado", "tipo": "D", "lab": "TA"})
                        
                        nombre = nombre_completo if 'nombre_completo' in locals() else ""
                        sexo_val = sexo if 'sexo' in locals() else ""
                        generar_y_mostrar_json(dni, str(edad), todos_codigos, dia_his, tipo_correccion, nombre, sexo_val, fecha_atencion)
                    else:
                        st.warning("Selecciona al menos un indicador")
            
            with tab3:
                st.markdown("Agregar diagnósticos de factores de riesgo:")
                
                # Checkboxes para factores de riesgo
                factores_seleccionados = []
                
                cols = st.columns(2)
                factores_lista = list(FACTORES_RIESGO_SIMPLE.items())
                
                for idx, (key, info) in enumerate(factores_lista):
                    col = cols[idx % 2]
                    with col:
                        if st.checkbox(f"{info['descripcion']} ({info['codigo']})", key=f"factor_{key}"):
                            factores_seleccionados.append(key)
                
                # Modificar valores LAB para casos patológicos
                st.markdown("---")
                st.markdown("**Ajustar valores LAB para casos patológicos:**")
                
                col1, col2 = st.columns(2)
                with col1:
                    presion_alterada = st.checkbox("Presión arterial alterada (A)", key="pa_alt")
                    nutricion_riesgo = st.checkbox("Riesgo nutricional (RSM)", key="nut_risk")
                
                if st.button("🚀 Generar con Factores de Riesgo", type="primary", key="btn_factores"):
                    todos_codigos = []
                    
                    # Agregar factores de riesgo
                    for factor in factores_seleccionados:
                        info = FACTORES_RIESGO_SIMPLE[factor]
                        todos_codigos.append({
                            "codigo": info['codigo'],
                            "descripcion": f"{info['codigo']} - {info['descripcion']}",
                            "tipo": "D",
                            "lab": ""
                        })
                    
                    # Si hay factores, agregar valoración clínica con factores
                    if factores_seleccionados:
                        # Valoración clínica
                        todos_codigos.append({
                            "codigo": "Z019",
                            "descripcion": "Z019 - Valoración clínica",
                            "tipo": "D",
                            "lab": "DNT"
                        })
                        
                        # Consejería
                        todos_codigos.append({
                            "codigo": "99401.13",
                            "descripcion": "99401.13 - Consejería estilos de vida",
                            "tipo": "D",
                            "lab": ""
                        })
                        
                        # Para adultos 30-39 con factores, agregar laboratorio
                        if curso_vida == "adulto" and edad >= 30 and edad <= 39:
                            todos_codigos.append({
                                "codigo": "Z017",
                                "descripcion": "Z017 - Tamizaje laboratorial",
                                "tipo": "D",
                                "lab": ""
                            })
                    
                    # Ajustar valores LAB si hay patología
                    if presion_alterada:
                        todos_codigos.append({
                            "codigo": "99199.22",
                            "descripcion": "99199.22 - Control de presión arterial",
                            "tipo": "D",
                            "lab": "A"
                        })
                    
                    if nutricion_riesgo:
                        todos_codigos.append({
                            "codigo": "99209.04",
                            "descripcion": "99209.04 - Evaluación nutricional",
                            "tipo": "D",
                            "lab": "RSM"
                        })
                    
                    nombre = nombre_completo if 'nombre_completo' in locals() else ""
                    sexo_val = sexo if 'sexo' in locals() else ""
                    generar_y_mostrar_json(dni, str(edad), todos_codigos, dia_his, tipo_correccion, nombre, sexo_val, fecha_atencion)
        else:
            st.info("👆 Ingresa DNI y fecha de nacimiento para continuar")

def generar_y_mostrar_json(dni: str, edad: str, codigos: List[Dict], dia_his: int, tipo_correccion: str, nombre: str = "", sexo: str = "", fecha_atencion: date = None):
    """Genera y muestra el JSON final"""
    # Optimizar códigos
    codigos_optimizados = optimizar_codigos(codigos)
    
    # Formatear diagnósticos con estructura completa
    diagnosticos_formateados = []
    for codigo in codigos_optimizados:
        diag = {
            "codigo": codigo['codigo'],
            "descripcion": codigo['descripcion'],
            "tipo": codigo.get('tipo', 'D'),
            "tipo_original": codigo.get('tipo', 'D'),
            "modificado": False
        }
        # Solo agregar lab si tiene valor
        if codigo.get('lab'):
            diag['lab'] = codigo['lab']
        
        diagnosticos_formateados.append(diag)
    
    # Crear estructura JSON según el formato requerido
    fecha_at = fecha_atencion.strftime("%Y-%m-%d") if fecha_atencion else datetime.now().strftime("%Y-%m-%d")
    
    json_data = {
        "fecha_exportacion": datetime.now().isoformat() + 'Z',
        "dia_his": str(dia_his),
        "fecha_atencion": fecha_at,
        "total_pacientes": 1,
        "cambios_realizados": 0,
        "pacientes": [{
            "dni": dni,
            "nombre": nombre,
            "edad": edad,
            "sexo": sexo,
            "diagnosticos": diagnosticos_formateados
        }]
    }
    
    # Mostrar resultados
    st.markdown("---")
    st.markdown("### 📄 JSON Generado")
    
    # Estadísticas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total códigos", len(codigos_optimizados))
    with col2:
        st.metric("DNI", dni)
    with col3:
        st.metric("Edad", f"{edad} años")
    
    # Mostrar JSON
    with st.expander("Ver JSON completo", expanded=True):
        st.json(json_data)
    
    # Botón de descarga
    json_str = json.dumps(json_data, indent=2, ensure_ascii=False)
    st.download_button(
        label="⬇️ Descargar JSON",
        data=json_str,
        file_name=f"hisminsa_{dni}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        type="primary"
    )

if __name__ == "__main__":
    main()