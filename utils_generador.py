#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilidades para el Generador JSON HISMINSA
Funciones auxiliares y mapeos especializados
"""

from typing import Dict, List, Optional, Tuple
from datetime import date

# ==============================================================================
# MAPEOS Y CÓDIGOS ESPECIALIZADOS
# ==============================================================================

# Mapeo de códigos CIE10 para factores de riesgo comunes
CODIGOS_FACTORES_RIESGO_DETALLADOS = {
    "obesidad": {
        "E66": "Obesidad",
        "E669": "Obesidad, no especificada",
        "E6690": "Obesidad, no especificada sin complicaciones",
        "E6691": "Obesidad grado I",
        "E6692": "Obesidad grado II", 
        "E6693": "Obesidad grado III (mórbida)",
        "E65X": "Adiposidad localizada"
    },
    "alcohol": {
        "Z720": "Problemas relacionados con el uso del tabaco",
        "Z721": "Problemas relacionados con el uso del alcohol",
        "F10": "Trastornos mentales y del comportamiento debidos al uso de alcohol"
    },
    "drogas": {
        "Z722": "Problemas relacionados con el uso de drogas",
        "Z723": "Problemas relacionados con falta de ejercicio físico",
        "Z724": "Problemas relacionados con dieta y hábitos alimentarios inapropiados"
    },
    "tabaco": {
        "Z783": "Consumidor de tabaco",
        "Z784": "Ex consumidor de tabaco",
        "F17": "Trastornos mentales y del comportamiento debidos al uso de tabaco"
    },
    "hipertension": {
        "I10X": "Hipertensión esencial (primaria)",
        "I11": "Enfermedad cardíaca hipertensiva",
        "I12": "Enfermedad renal hipertensiva",
        "I13": "Enfermedad cardiorrenal hipertensiva"
    },
    "diabetes": {
        "E10": "Diabetes mellitus tipo 1",
        "E11": "Diabetes mellitus tipo 2",
        "E13": "Otras diabetes mellitus especificadas",
        "E14": "Diabetes mellitus, no especificada"
    }
}

# Valores LAB especiales por código
VALORES_LAB_ESPECIALES = {
    # Valoración clínica
    "Z019": "DNT",  # Diagnóstico No Transmisible
    
    # Presión arterial
    "99199.22": {
        "normal": "N",
        "alterado": "A"
    },
    
    # Valoración nutricional
    "99209.02": {
        "normal": "N",
        "riesgo_bajo": "RSM",  # Riesgo de Salud Metabólica
        "riesgo_alto": "RSA",
        "riesgo_muy_alto": "RMA"
    },
    "99209.04": {
        "normal": "N",
        "riesgo_bajo": "RSM",
        "riesgo_alto": "RSA", 
        "riesgo_muy_alto": "RMA"
    },
    
    # VACAM
    "99387": {
        "autosuficiente": "AS",
        "esposa": "E",
        "algun_familiar": "AF",
        "grupo_comunitario": "GC"
    },
    "99215.03": {
        "autosuficiente": "AS",
        "esposa": "E",
        "algun_familiar": "AF",
        "grupo_comunitario": "GC"
    },
    
    # Salud mental
    "96150.01": "",  # Violencia intrafamiliar
    "96150.02": "",  # Alcohol y drogas
    "96150.03": "",  # Trastornos depresivos
    "96150.04": "",  # Psicosis
    "96150.07": "",  # Deterioro cognitivo
    
    # VIH
    "86780": {
        "negativo": "1",
        "positivo": "2",
        "indeterminado": "3"
    },
    
    # Plan de atención
    "99801": {
        "elaborado": "1",
        "ejecutado": "TA"
    }
}

# Códigos que requieren secuencia específica
CODIGOS_CON_SECUENCIA = {
    "tamizaje_vih": {
        "orden": ["99401.33", "86780", "99401.30"],
        "descripcion": "Pre-test → Tamizaje → Post-test"
    },
    "vacam": {
        "orden": ["99387", "99401"],
        "alternativo": ["99215.03", "99401"],
        "descripcion": "VACAM → Consejería"
    },
    "salud_mental": {
        "tamizajes": ["96150.01", "96150.02", "96150.03", "96150.04", "96150.07"],
        "consejeria": "99402.09",
        "descripcion": "5 tamizajes → 1 consejería"
    }
}

# ==============================================================================
# FUNCIONES DE CÁLCULO Y VALIDACIÓN
# ==============================================================================

def calcular_riesgo_cardiovascular(edad: int, sexo: str, presion_sistolica: int, 
                                 presion_diastolica: int, colesterol: float = None,
                                 fumador: bool = False, diabetico: bool = False) -> Dict[str, Any]:
    """
    Calcula el riesgo cardiovascular según criterios simplificados
    """
    riesgo_score = 0
    factores = []
    
    # Edad
    if sexo == "M":
        if edad >= 45:
            riesgo_score += 2
            factores.append("Edad ≥ 45 años (hombre)")
    else:  # F
        if edad >= 55:
            riesgo_score += 2
            factores.append("Edad ≥ 55 años (mujer)")
    
    # Presión arterial
    if presion_sistolica >= 140 or presion_diastolica >= 90:
        riesgo_score += 3
        factores.append("Hipertensión")
    elif presion_sistolica >= 130 or presion_diastolica >= 85:
        riesgo_score += 1
        factores.append("Pre-hipertensión")
    
    # Colesterol (si está disponible)
    if colesterol:
        if colesterol >= 240:
            riesgo_score += 3
            factores.append("Colesterol alto")
        elif colesterol >= 200:
            riesgo_score += 1
            factores.append("Colesterol límite alto")
    
    # Factores adicionales
    if fumador:
        riesgo_score += 2
        factores.append("Fumador")
    
    if diabetico:
        riesgo_score += 3
        factores.append("Diabetes")
    
    # Clasificación
    if riesgo_score >= 5:
        clasificacion = "Alto"
        color = "🔴"
    elif riesgo_score >= 3:
        clasificacion = "Moderado"
        color = "🟡"
    else:
        clasificacion = "Bajo"
        color = "🟢"
    
    return {
        "score": riesgo_score,
        "clasificacion": clasificacion,
        "color": color,
        "factores": factores
    }

def determinar_periodicidad_control(edad: int, factores_riesgo: List[str], 
                                   tiene_cronicas: bool = False) -> Dict[str, Any]:
    """
    Determina la periodicidad de controles según edad y factores de riesgo
    """
    if tiene_cronicas:
        return {
            "frecuencia": "Trimestral",
            "meses": 3,
            "razon": "Paciente con enfermedad crónica"
        }
    
    num_factores = len(factores_riesgo)
    
    if edad >= 60:
        if num_factores >= 2:
            return {
                "frecuencia": "Trimestral",
                "meses": 3,
                "razon": "Adulto mayor con múltiples factores de riesgo"
            }
        else:
            return {
                "frecuencia": "Semestral",
                "meses": 6,
                "razon": "Adulto mayor"
            }
    elif edad >= 40:
        if num_factores >= 2:
            return {
                "frecuencia": "Semestral",
                "meses": 6,
                "razon": "Adulto con factores de riesgo"
            }
        else:
            return {
                "frecuencia": "Anual",
                "meses": 12,
                "razon": "Adulto sin factores de riesgo significativos"
            }
    else:  # < 40
        return {
            "frecuencia": "Anual",
            "meses": 12,
            "razon": "Adulto joven"
        }

def calcular_percentil_pab(pab: float, edad: int, sexo: str) -> Dict[str, Any]:
    """
    Calcula el percentil del perímetro abdominal según edad y sexo
    """
    # Valores de referencia simplificados
    if sexo == "M":
        limite_normal = 94
        limite_alto = 102
    else:  # F
        limite_normal = 80
        limite_alto = 88
    
    if pab < limite_normal:
        return {
            "clasificacion": "Normal",
            "percentil": "< P75",
            "color": "🟢",
            "riesgo": "Sin riesgo metabólico"
        }
    elif pab < limite_alto:
        return {
            "clasificacion": "Riesgo aumentado",
            "percentil": "P75-P90",
            "color": "🟡",
            "riesgo": "Riesgo metabólico aumentado"
        }
    else:
        return {
            "clasificacion": "Riesgo muy alto",
            "percentil": "> P90",
            "color": "🔴",
            "riesgo": "Riesgo metabólico muy alto"
        }

def generar_recomendaciones_personalizadas(paciente: Dict) -> List[str]:
    """
    Genera recomendaciones personalizadas según el perfil del paciente
    """
    recomendaciones = []
    
    # Por IMC
    imc = paciente.get('antropometria', {}).get('imc', 0)
    if imc >= 25:
        recomendaciones.append("📊 Control nutricional y plan de actividad física")
        recomendaciones.append("🥗 Consejería en alimentación saludable")
    
    # Por presión arterial
    pa_sistolica = paciente.get('antropometria', {}).get('presion_sistolica', 0)
    if pa_sistolica >= 130:
        recomendaciones.append("💊 Evaluación para inicio de tratamiento antihipertensivo")
        recomendaciones.append("🧂 Restricción de sodio en la dieta")
    
    # Por edad
    edad = paciente.get('edad', 0)
    if edad >= 40:
        recomendaciones.append("🔬 Perfil lipídico completo anual")
        recomendaciones.append("🩺 Evaluación cardiovascular integral")
    
    if edad >= 50:
        if paciente.get('sexo') == 'M':
            recomendaciones.append("🔍 Tamizaje de cáncer de próstata")
        recomendaciones.append("🔍 Tamizaje de cáncer colorrectal")
    
    # Por factores de riesgo
    if 'alcohol' in paciente.get('factores_riesgo', []):
        recomendaciones.append("🚫 Consejería para reducción de consumo de alcohol")
    
    if 'tabaco' in paciente.get('factores_riesgo', []):
        recomendaciones.append("🚭 Programa de cesación tabáquica")
    
    return recomendaciones

def validar_coherencia_diagnosticos(diagnosticos: List[Dict]) -> Dict[str, Any]:
    """
    Valida la coherencia de los diagnósticos generados
    """
    errores = []
    advertencias = []
    
    # Verificar duplicados
    codigos_vistos = {}
    for diag in diagnosticos:
        codigo = diag['codigo']
        if codigo in codigos_vistos:
            errores.append(f"Código duplicado: {codigo}")
        codigos_vistos[codigo] = True
    
    # Verificar secuencias requeridas
    codigos_list = [d['codigo'] for d in diagnosticos]
    
    # VIH: debe tener pre-test antes que el tamizaje
    if '86780' in codigos_list and '99401.33' not in codigos_list:
        advertencias.append("Tamizaje VIH sin pre-test")
    
    # VACAM: debe tener consejería después
    if ('99387' in codigos_list or '99215.03' in codigos_list) and '99401' not in codigos_list:
        advertencias.append("VACAM sin consejería posterior")
    
    # Salud mental: verificar consejería única
    tamizajes_sm = [c for c in codigos_list if c in CODIGOS_CON_SECUENCIA['salud_mental']['tamizajes']]
    consejerias_sm = [d for d in diagnosticos if d['codigo'] in ['99402.01', '99402.09']]
    
    if len(tamizajes_sm) > 0 and len(consejerias_sm) > 1:
        advertencias.append("Múltiples consejerías de salud mental (debe ser una sola)")
    
    # Verificar valores LAB
    for diag in diagnosticos:
        codigo = diag['codigo']
        lab = diag.get('lab', '')
        
        if codigo in VALORES_LAB_ESPECIALES:
            esperado = VALORES_LAB_ESPECIALES[codigo]
            if isinstance(esperado, str) and lab != esperado:
                advertencias.append(f"Código {codigo} con LAB '{lab}', esperado '{esperado}'")
    
    return {
        "valido": len(errores) == 0,
        "errores": errores,
        "advertencias": advertencias,
        "total_diagnosticos": len(diagnosticos)
    }

def generar_codigo_especial_nutricion(imc: float, pab: float, sexo: str) -> Dict[str, str]:
    """
    Genera el código y LAB apropiado para valoración nutricional
    """
    # Determinar riesgo por IMC
    if imc >= 30:
        riesgo_imc = "alto"
    elif imc >= 25:
        riesgo_imc = "moderado"
    else:
        riesgo_imc = "bajo"
    
    # Determinar riesgo por PAB
    limite_pab = 94 if sexo == "M" else 80
    if pab > limite_pab:
        riesgo_pab = "alto"
    else:
        riesgo_pab = "bajo"
    
    # Combinar riesgos
    if riesgo_imc == "alto" or riesgo_pab == "alto":
        lab = "RSA"  # Riesgo de Salud Alto
    elif riesgo_imc == "moderado" or riesgo_pab == "alto":
        lab = "RSM"  # Riesgo de Salud Metabólica
    else:
        lab = "N"  # Normal
    
    return {
        "codigo": "99209.04",
        "descripcion": "99209.04 - Evaluación nutricional antropométrica",
        "tipo": "D",
        "lab": lab,
        "detalle": f"IMC: {imc}, PAB: {pab}cm"
    }

def mapear_medicamentos_cronicos(condicion: str) -> List[Dict[str, str]]:
    """
    Mapea condiciones crónicas a códigos de medicamentos comunes
    """
    medicamentos = {
        "hipertension": [
            {"codigo": "N02BA01", "descripcion": "Ácido acetilsalicílico 100mg"},
            {"codigo": "C07AB03", "descripcion": "Atenolol 50mg"},
            {"codigo": "C09AA01", "descripcion": "Captopril 25mg"}
        ],
        "diabetes": [
            {"codigo": "A10BA02", "descripcion": "Metformina 850mg"},
            {"codigo": "A10AB01", "descripcion": "Insulina humana"}
        ],
        "dislipidemia": [
            {"codigo": "C10AA01", "descripcion": "Simvastatina 20mg"},
            {"codigo": "C10AA05", "descripcion": "Atorvastatina 20mg"}
        ]
    }
    
    return medicamentos.get(condicion, [])

# ==============================================================================
# FUNCIONES DE EXPORTACIÓN Y FORMATO
# ==============================================================================

def formatear_json_para_his(json_data: Dict) -> str:
    """
    Formatea el JSON según los requerimientos específicos del HIS-MINSA
    """
    import json
    
    # Formato específico con indentación y orden de campos
    return json.dumps(json_data, 
                     indent=2, 
                     ensure_ascii=False, 
                     sort_keys=False)

def generar_resumen_atencion(paciente: Dict, diagnosticos: List[Dict]) -> str:
    """
    Genera un resumen textual de la atención para documentación
    """
    resumen = f"""
RESUMEN DE ATENCIÓN - {paciente['nombre_completo']}
{'=' * 50}
DNI: {paciente['dni']}
Edad: {paciente['edad']} años
Sexo: {'Masculino' if paciente['sexo'] == 'M' else 'Femenino'}
Curso de vida: {paciente['curso_vida']}
Fecha de atención: {paciente['fecha_atencion']}

EVALUACIÓN ANTROPOMÉTRICA:
- Peso: {paciente['antropometria']['peso']} kg
- Talla: {paciente['antropometria']['talla']} cm
- IMC: {paciente['antropometria']['imc']} ({paciente['antropometria']['clasificacion_imc']})
- PAB: {paciente['antropometria']['pab']} cm
- PA: {paciente['antropometria']['presion_sistolica']}/{paciente['antropometria']['presion_diastolica']} mmHg

FACTORES DE RIESGO:
"""
    
    for factor in paciente.get('factores_riesgo', []):
        if factor in FACTORES_RIESGO:
            resumen += f"- {FACTORES_RIESGO[factor]['nombre']}\n"
    
    resumen += f"\nTOTAL CÓDIGOS GENERADOS: {len(diagnosticos)}\n"
    
    return resumen