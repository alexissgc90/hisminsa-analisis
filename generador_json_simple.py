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
    "sobrepeso": {"codigo": "E6690", "descripcion": "Sobrepeso"},
    "obesidad_i": {"codigo": "E6691", "descripcion": "Obesidad grado I"},
    "obesidad_ii": {"codigo": "E6692", "descripcion": "Obesidad grado II"},
    "obesidad_iii": {"codigo": "E6693", "descripcion": "Obesidad grado III"},
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

def calcular_riesgo_pab(pab: float, sexo: str) -> str:
    """
    Calcula el riesgo según el perímetro abdominal y sexo
    
    Criterios:
    - RSM (Riesgo Mínimo): M <94cm, F <80cm
    - RSA (Riesgo Alto): M ≥94cm, F ≥80cm  
    - RMA (Riesgo Muy Alto): M ≥102cm, F ≥88cm
    """
    if not pab or pab <= 0 or not sexo:
        return "RSM"  # Por defecto si no hay datos
    
    if sexo == "M":
        if pab < 94:
            return "RSM"
        elif pab < 102:
            return "RSA"
        else:
            return "RMA"
    elif sexo == "F":
        if pab < 80:
            return "RSM"
        elif pab < 88:
            return "RSA"
        else:
            return "RMA"
    else:
        return "RSM"  # Por defecto si sexo no especificado

def clasificar_imc(imc: float) -> Dict[str, str]:
    """
    Clasifica el IMC y retorna el código y descripción correspondiente
    
    Clasificación:
    - Normal: IMC < 25
    - Sobrepeso: IMC 25-29.9 (E6690)
    - Obesidad I: IMC 30-34.9 (E6691)
    - Obesidad II: IMC 35-39.9 (E6692)
    - Obesidad III: IMC ≥40 (E6693)
    """
    if imc < 25:
        return None
    elif imc < 30:
        return {"codigo": "E6690", "descripcion": "Sobrepeso"}
    elif imc < 35:
        return {"codigo": "E6691", "descripcion": "Obesidad grado I"}
    elif imc < 40:
        return {"codigo": "E6692", "descripcion": "Obesidad grado II"}
    else:
        return {"codigo": "E6693", "descripcion": "Obesidad grado III"}

def generar_codigos_indicador(indicador_key: str, indicador_info: Dict, edad: int, curso: str, tiene_factores: bool = False, sexo: str = "", pab: float = 0, imc: float = 0) -> List[Dict]:
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
    
    # Casos especiales: tamizajes de cáncer (próstata, colon) - formato específico
    if indicador_key == 'cancer_prostata':
        codigos = [
            {"codigo": "84152", "descripcion": "84152 - Dosaje PSA", "tipo": "D", "lab": ""},
            {"codigo": "84152", "descripcion": "84152 - Dosaje PSA", "tipo": "D", "lab": "N"},
            {"codigo": "99402.08", "descripcion": "99402.08 - Consejería factores riesgo cáncer", "tipo": "D", "lab": "1"}
        ]
        return codigos
    
    if indicador_key == 'cancer_colon_recto':
        codigos = [
            {"codigo": "82270", "descripcion": "82270 - Test sangre oculta en heces", "tipo": "D", "lab": ""},
            {"codigo": "82270", "descripcion": "82270 - Test sangre oculta en heces", "tipo": "D", "lab": "N"},
            {"codigo": "99402.08", "descripcion": "99402.08 - Consejería factores riesgo cáncer", "tipo": "D", "lab": "1"}
        ]
        return codigos
    
    # Casos especiales: tamizajes de cáncer de cuello uterino
    if indicador_key == 'cancer_cuello_uterino':
        # Usar método principal según edad
        if 25 <= edad <= 29:
            # Prueba molecular VPH
            codigos = [
                {"codigo": "87621", "descripcion": "87621 - Prueba molecular VPH", "tipo": "D", "lab": ""},
                {"codigo": "87621", "descripcion": "87621 - Prueba molecular VPH", "tipo": "D", "lab": "N"},
                {"codigo": "99402.08", "descripcion": "99402.08 - Consejería factores riesgo cáncer", "tipo": "D", "lab": "1"}
            ]
        elif 30 <= edad <= 49:
            # IVAA
            codigos = [
                {"codigo": "88141.01", "descripcion": "88141.01 - Inspección Visual con Ácido Acético", "tipo": "D", "lab": ""},
                {"codigo": "88141.01", "descripcion": "88141.01 - Inspección Visual con Ácido Acético", "tipo": "D", "lab": "N"},
                {"codigo": "99402.08", "descripcion": "99402.08 - Consejería factores riesgo cáncer", "tipo": "D", "lab": "1"}
            ]
        else:
            # PAP
            codigos = [
                {"codigo": "88141", "descripcion": "88141 - Papanicolaou", "tipo": "D", "lab": ""},
                {"codigo": "88141", "descripcion": "88141 - Papanicolaou", "tipo": "D", "lab": "N"},
                {"codigo": "99402.08", "descripcion": "99402.08 - Consejería factores riesgo cáncer", "tipo": "D", "lab": "1"}
            ]
        return codigos
    
    if 'reglas' in indicador_info and isinstance(indicador_info['reglas'], list):
        for regla in indicador_info['reglas']:
            # Aplicar lógica especial para laboratorio
            if regla.get('codigo') == 'Z017' and curso == "adulto" and edad < 40:
                continue  # No incluir laboratorio para adultos < 40 sin factores
            
            # Manejo especial para perímetro abdominal
            if regla.get('codigo') == '99209.03' and sexo and pab > 0:
                valor_riesgo = calcular_riesgo_pab(pab, sexo)
                codigo_obj = {
                    "codigo": regla['codigo'],
                    "descripcion": f"{regla['codigo']} - {regla.get('descripcion', '')}",
                    "tipo": regla.get('tipo_dx', 'D'),
                    "lab": valor_riesgo
                }
            else:
                codigo_obj = {
                    "codigo": regla['codigo'],
                    "descripcion": f"{regla['codigo']} - {regla.get('descripcion', '')}",
                    "tipo": regla.get('tipo_dx', 'D'),
                    "lab": obtener_valor_lab_default(regla, indicador_key)
                }
            codigos.append(codigo_obj)
            
            # Agregar código de sobrepeso/obesidad después de Z019 en valoración clínica
            if regla.get('codigo') == 'Z019' and indicador_key in ['valoracion_clinica_con_factores', 'valoracion_clinica_sin_factores'] and imc > 0:
                clasificacion = clasificar_imc(imc)
                if clasificacion:
                    codigos.append({
                        "codigo": clasificacion['codigo'],
                        "descripcion": f"{clasificacion['codigo']} - {clasificacion['descripcion']}",
                        "tipo": "D",
                        "lab": ""
                    })
    
    # Caso especial: laboratorio para adultos
    if curso == "adulto" and (indicador_key == 'valoracion_clinica_con_factores' or indicador_key == 'valoracion_clinica_sin_factores'):
        # Agregar laboratorio si: 40-59 años O 30-39 con factores
        if edad >= 40 or (30 <= edad <= 39 and tiene_factores):
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
        '99209.02': '',   # Cálculo IMC sin LAB
        '99209.03': 'RSM',  # Perímetro abdominal - RSM (Riesgo Bajo) por defecto
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

def generar_script_js(codigos: List[Dict], dni: str) -> str:
    """Genera un script JS para automatizar el ingreso en HISMINSA usando el formato exacto de prostata.txt y colon.txt"""
    
    # Convertir códigos al formato del script
    diagnosticos_js = []
    for codigo in codigos:
        # Manejo especial para códigos de tamizaje de cáncer
        codigo_str = codigo["codigo"]
        
        # Si es un código de tamizaje de cáncer, generar el patrón especial
        if codigo_str in ["82270", "84152", "87621"]:  # Colon, Próstata, Cuello uterino
            # Primero sin LAB
            diagnosticos_js.append(f"""        {{
            codigo: "{codigo_str}",
            tipo: "D",
            lab: null  // Sin LAB
        }}""")
            # Luego con LAB = N
            diagnosticos_js.append(f"""        {{
            codigo: "{codigo_str}",
            tipo: "D",
            lab: "N"  // LAB = N
        }}""")
            # Luego la consejería con LAB = 1
            diagnosticos_js.append(f"""        {{
            codigo: "99402.08",
            tipo: "D",
            lab: "1"  // LAB = 1
        }}""")
        else:
            # Para otros códigos, formato normal
            lab_value = f'"{codigo.get("lab", "")}"' if codigo.get("lab") else "null"
            diagnosticos_js.append(f"""        {{
            codigo: "{codigo_str}",
            tipo: "{codigo.get("tipo", "D")}",
            lab: {lab_value}{"  // Sin LAB" if not codigo.get("lab") else f'  // LAB = {codigo.get("lab")}'}
        }}""")
    
    # Template del script exacto como en prostata.txt y colon.txt
    script_template = f"""// Script para ingresar los diagnósticos específicos
  async function ingresarDiagnosticosEspecificos() {{
      const diagnosticos = [
{','.join(diagnosticos_js)}
      ];

      console.log('🚀 Iniciando ingreso de ' + diagnosticos.length + ' diagnósticos...');

      for (let i = 0; i < diagnosticos.length; i++) {{
          const dx = diagnosticos[i];
          console.log(`\\n📍 Diagnóstico ${{i + 1}}/${{diagnosticos.length}}: ${{dx.codigo}}`);

          try {{
              // 1. Agregar nueva fila (Shift+1)
              const gridview = document.querySelector('[id*="gridview-"]');
              gridview.focus();
              gridview.dispatchEvent(new KeyboardEvent('keydown', {{
                  key: '1', keyCode: 49, shiftKey: true, bubbles: true
              }}));
              await new Promise(r => setTimeout(r, 1000));

              // 2. Ingresar código
              document.activeElement.value = dx.codigo;
              ['input', 'keyup', 'change'].forEach(evt =>
                  document.activeElement.dispatchEvent(new Event(evt, {{ bubbles: true }}))
              );
              await new Promise(r => setTimeout(r, 2000));

              // 3. Seleccionar de lista (Enter)
              document.activeElement.dispatchEvent(new KeyboardEvent('keydown', {{
                  key: 'Enter', keyCode: 13, bubbles: true
              }}));
              await new Promise(r => setTimeout(r, 1000));

              // 4. Ingresar tipo D
              const tabla = document.querySelector('[id*="gridpanel"]');
              const filas = tabla.querySelectorAll('tr.x-grid-row, tr.x-grid3-row');
              const ultimaFila = filas[filas.length - 1];
              ultimaFila.cells[4].dispatchEvent(new MouseEvent('dblclick', {{ bubbles: true }}));       
              await new Promise(r => setTimeout(r, 500));

              document.activeElement.value = dx.tipo;
              document.activeElement.dispatchEvent(new Event('change', {{ bubbles: true }}));
              document.activeElement.dispatchEvent(new KeyboardEvent('keydown', {{
                  key: 'Enter', keyCode: 13, bubbles: true
              }}));
              await new Promise(r => setTimeout(r, 1000));

              // 5. Si hay LAB, ingresarlo
              if (dx.lab) {{
                  console.log(`   → Ingresando LAB: ${{dx.lab}}`);
                  document.body.dispatchEvent(new KeyboardEvent('keydown', {{
                      key: 'Z', keyCode: 90, shiftKey: true, bubbles: true
                  }}));
                  await new Promise(r => setTimeout(r, 2500)); // Aumentado de 1500 a 2500

                  document.activeElement.value = dx.lab;
                  ['input', 'keyup', 'change'].forEach(evt =>
                      document.activeElement.dispatchEvent(new Event(evt, {{ bubbles: true }}))
                  );
                  await new Promise(r => setTimeout(r, 1000)); // Aumentado de 500 a 1000
                  document.activeElement.dispatchEvent(new KeyboardEvent('keydown', {{
                      key: 'Enter', keyCode: 13, bubbles: true
                  }}));
                  await new Promise(r => setTimeout(r, 1500)); // Aumentado de 1000 a 1500
              }}

              console.log(`✅ ${{dx.codigo}} ingresado` + (dx.lab ? ` con LAB=${{dx.lab}}` : ''));        

          }} catch (error) {{
              console.error(`❌ Error con ${{dx.codigo}}:`, error);
          }}
      }}

      console.log('\\n✨ Proceso completado');
      console.log('💾 Para guardar: guardarRegistro() o presiona Shift+A');
  }}

  // Función para guardar
  function guardarRegistro() {{
      document.body.dispatchEvent(new KeyboardEvent('keydown', {{
          key: 'A', keyCode: 65, shiftKey: true, bubbles: true
      }}));
      console.log('💾 Guardando registro...');
  }}

  // Ejecutar automáticamente
  ingresarDiagnosticosEspecificos();"""
    
    return script_template

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
        
        # Validar fecha y calcular edad primero
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
        
        # Campos opcionales
        nombre_completo = ""
        sexo = ""
        with st.expander("Datos opcionales", expanded=False):
            nombre_completo = st.text_input("Nombre completo:", placeholder="APELLIDOS NOMBRES")
            sexo = st.selectbox("Sexo:", ["", "M", "F"], help="Dejar vacío si no se requiere")
        
        # Datos antropométricos para calcular factores de riesgo
        st.markdown("### 📏 Datos Antropométricos")
        col_peso, col_talla = st.columns(2)
        with col_peso:
            peso = st.number_input("Peso (kg):", min_value=0.0, max_value=300.0, step=0.1, value=0.0)
        with col_talla:
            talla = st.number_input("Talla (cm):", min_value=0.0, max_value=250.0, step=0.1, value=0.0)
        
        # Calcular IMC si hay datos
        imc = 0
        tiene_sobrepeso = False
        if peso > 0 and talla > 0:
            talla_metros = talla / 100
            imc = peso / (talla_metros ** 2)
            
            # Clasificar IMC
            clasificacion = clasificar_imc(imc)
            if clasificacion:
                tiene_sobrepeso = True
                # Mostrar con colores según gravedad
                if clasificacion['codigo'] == 'E6690':
                    st.warning(f"⚠️ IMC: {imc:.1f} - {clasificacion['descripcion']} ({clasificacion['codigo']})")
                elif clasificacion['codigo'] in ['E6691', 'E6692']:
                    st.error(f"🔴 IMC: {imc:.1f} - {clasificacion['descripcion']} ({clasificacion['codigo']})")
                else:  # E6693
                    st.error(f"⛔ IMC: {imc:.1f} - {clasificacion['descripcion']} ({clasificacion['codigo']})")
            else:
                st.success(f"✅ IMC: {imc:.1f} - Peso normal")
        
        # Perímetro abdominal (solo para adultos)
        pab = 0.0  # Inicializar siempre
        if curso_vida == "adulto":
            pab = st.number_input(
                "Perímetro Abdominal (cm):", 
                min_value=0.0, 
                max_value=200.0, 
                step=0.1, 
                value=0.0,
                help="Necesario para calcular el riesgo sanitario (RSM/RSA/RMA)"
            )
            
            # Mostrar el riesgo calculado si hay datos
            if pab > 0 and sexo:
                riesgo_calculado = calcular_riesgo_pab(pab, sexo)
                riesgo_texto = {
                    "RSM": "Riesgo Sanitario Mínimo (Bajo)",
                    "RSA": "Riesgo Sanitario Alto", 
                    "RMA": "Riesgo Muy Alto"
                }
                color = {"RSM": "🟢", "RSA": "🟡", "RMA": "🔴"}
                st.info(f"{color[riesgo_calculado]} Riesgo calculado: **{riesgo_texto[riesgo_calculado]}** (LAB = {riesgo_calculado})")
    
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
                            # Manejar valoración clínica según factores
                            indicador_usar = comp['indicador']
                            if comp['componente'] == "Valoración Clínica" and tiene_sobrepeso:
                                # Cambiar a versión con factores si hay sobrepeso
                                indicador_usar = indicador_usar.replace("sin_factores", "con_factores")
                            
                            ind_info = indicadores.get(indicador_usar, {})
                            codigos = generar_codigos_indicador(indicador_usar, ind_info, edad, curso_vida, tiene_sobrepeso, sexo, pab, imc)
                            todos_codigos.extend(codigos)
                    
                    # IMPORTANTE: Agregar agudeza visual para TODOS los cursos de vida
                    # (puede que no esté en algunos paquetes pero es necesario)
                    agudeza_codigos = generar_codigos_indicador('agudeza_visual', {}, edad, curso_vida, False, sexo, pab, imc)
                    # Verificar si ya existe para no duplicar
                    codigos_existentes = {c['codigo'] for c in todos_codigos}
                    for codigo in agudeza_codigos:
                        if codigo['codigo'] not in codigos_existentes:
                            todos_codigos.extend(agudeza_codigos)
                            break  # Solo agregar una vez
                    
                    # Agregar diagnóstico de sobrepeso/obesidad si aplica
                    if tiene_sobrepeso and imc > 0:
                        clasificacion = clasificar_imc(imc)
                        if clasificacion:
                            todos_codigos.append({
                                "codigo": clasificacion['codigo'],
                                "descripcion": f"{clasificacion['codigo']} - {clasificacion['descripcion']}",
                                "tipo": "D",
                                "lab": ""
                            })
                    
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
                idx_col = 0
                for key, info in indicadores.items():
                    if key not in ['plan_atencion_elaborado', 'plan_atencion_ejecutado', 'plan_atencion_iniciado']:
                        # Para valoración clínica, mostrar ambas opciones si aplica
                        if key in ['valoracion_clinica_sin_factores', 'valoracion_clinica_con_factores']:
                            nombre_mostrar = info['nombre']
                            # Agregar nota sobre el uso automatico según IMC
                            if key == 'valoracion_clinica_sin_factores':
                                nombre_mostrar += " (auto si IMC < 25)"
                            else:
                                nombre_mostrar += " (auto si IMC ≥ 25)"
                            
                            # Si hay sobrepeso/obesidad, indicar que se incluirá el código
                            if imc >= 25:
                                clasificacion = clasificar_imc(imc)
                                if clasificacion:
                                    nombre_mostrar += f", incluirá {clasificacion['codigo']}"
                        else:
                            nombre_mostrar = info['nombre']
                        
                        col = cols[idx_col % 2]
                        with col:
                            if st.checkbox(nombre_mostrar, key=f"ind_{key}"):
                                indicadores_seleccionados.append(key)
                        idx_col += 1
                
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
                            codigos = generar_codigos_indicador(ind_key, ind_info, edad, curso_vida, tiene_sobrepeso, sexo, pab, imc)
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
    with st.expander("📄 Ver JSON completo", expanded=True):
        st.json(json_data)
    
    # Mostrar instrucciones para el script JS
    with st.expander("📜 Instrucciones para usar el Script JS", expanded=False):
        st.markdown("""
        ### 🚀 Cómo usar el script de automatización:
        
        1. **Abrir HISMINSA** en el navegador web
        2. **Navegar** a la página de registro de diagnósticos del paciente
        3. **Abrir la consola** del navegador (presionar `F12`)
        4. **Ir a la pestaña "Console"**
        5. **Copiar y pegar** todo el contenido del script JS descargado
        6. **Presionar Enter** para ejecutar
        7. **Confirmar** cuando el script pregunte si desea proceder
        
        ### ⚠️ Importante:
        - El script simulará el ingreso manual de cada diagnóstico
        - Espere a que termine antes de hacer otra acción
        - Al final, confirmará si desea guardar con `Shift+A`
        
        ### 🔧 Atajos de teclado HISMINSA:
        - `Shift+1`: Agregar nueva fila
        - `Shift+Z`: Ir al campo LAB
        - `Shift+A`: Guardar registro
        """)
    
    # Opciones de descarga
    col1, col2 = st.columns(2)
    
    with col1:
        # Botón de descarga JSON
        json_str = json.dumps(json_data, indent=2, ensure_ascii=False)
        st.download_button(
            label="⬇️ Descargar JSON",
            data=json_str,
            file_name=f"hisminsa_{dni}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            type="primary"
        )
    
    with col2:
        # Botón de descarga JS
        js_str = generar_script_js(codigos_optimizados, dni)
        st.download_button(
            label="📜 Descargar Script JS",
            data=js_str,
            file_name=f"hisminsa_script_{dni}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.js",
            mime="text/javascript",
            type="secondary"
        )

if __name__ == "__main__":
    main()