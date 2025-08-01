#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Definición de Indicadores para Curso de Vida Joven (18-29 años)
Sistema HISMINSA - Supervisión de Indicadores
"""

# Diccionario completo de indicadores joven
INDICADORES_JOVEN = {
    "valoracion_clinica_sin_factores": {
        "nombre": "Valoración Clínica SIN Factores de Riesgo",
        "descripcion": "Valoración clínica sin factores de riesgo identificados",
        "edad_min": 18,
        "edad_max": 29,
        "reglas": [
            {
                "codigo": "Z019",
                "descripcion": "Valoración clínica",
                "tipo_dx": "D",
                "lab_valores": ["DNT"],
                "obligatorio": True
            }
        ],
        "requiere_todos": True,
        "frecuencia": "1 vez al año",
        "meta": 100
    },
    
    "valoracion_clinica_con_factores": {
        "nombre": "Valoración Clínica CON Factores de Riesgo",
        "descripcion": "Valoración clínica con factores de riesgo y consejería",
        "edad_min": 18,
        "edad_max": 29,
        "reglas": [
            {
                "codigo": "Z019",
                "descripcion": "Valoración clínica",
                "tipo_dx": "D",
                "lab_valores": ["DNT"],
                "obligatorio": True
            },
            {
                "codigo": "99401.13",
                "descripcion": "Consejería estilos vida",
                "tipo_dx": "D",
                "lab_valores": [""],
                "obligatorio": True
            }
        ],
        "requiere_todos": True,
        "frecuencia": "1 vez al año",
        "meta": 100
    },
    
    "evaluacion_nutricional": {
        "nombre": "Evaluación Nutricional y Antropométrica",
        "descripcion": "Evaluación del índice de masa corporal y del perímetro abdominal",
        "edad_min": 18,
        "edad_max": 29,
        "reglas": [
            {
                "codigo": "99209.04",
                "descripcion": "Evaluación nutricional antropométrica",
                "tipo_dx": "D",
                "lab_valores": ["", "RSA", "RMA", "RSM"],
                "lab_descripcion": "RSM=Riesgo Bajo, RSA=Riesgo Alto, RMA=Riesgo Muy Alto"
            },
            {
                "codigo": "99403.01",
                "descripcion": "Consejería alimentación saludable",
                "tipo_dx": "D",
                "lab_valores": [""]
            }
        ],
        "requiere_ambos": True,
        "frecuencia": "1 vez al año",
        "meta": 100
    },
    
    "tamizaje_violencia": {
        "nombre": "Tamizaje de Violencia Intrafamiliar",
        "descripcion": "Identificar factores de riesgo y fortalecer factores protectores de maltrato",
        "edad_min": 18,
        "edad_max": 29,
        "reglas": [
            {
                "codigo": "96150.01",
                "descripcion": "Tamizaje VIF",
                "tipo_dx": "D",
                "lab_valores": ["", "TPE", "JUD"],
                "obligatorio": True
            },
            {
                "codigo": "99402.09",
                "descripcion": "Consejería en salud mental",
                "tipo_dx": "D",
                "lab_valores": [""],
                "obligatorio": True
            }
        ],
        "requiere_ambos": True,
        "frecuencia": "1 vez al año",
        "meta": 100
    },
    
    "tamizaje_vih": {
        "nombre": "Tamizaje para Detección de VIH",
        "descripcion": "Tamizaje con prueba rápida para descarte de VIH",
        "edad_min": 18,
        "edad_max": 29,
        "reglas": {
            "pre_test": {
                "codigo": "99401.33",
                "descripcion": "Consejería pre test VIH",
                "tipo_dx": "D",
                "lab_valores": [""],
                "obligatorio": True
            },
            "pruebas": [
                {
                    "tipo": "dual",
                    "codigo": "86318.01",
                    "descripcion": "Prueba dual VIH/Sífilis",
                    "tipo_dx": "D",
                    "lab_especial": "Lab1: RN/RP (VIH), Lab2: RN/RP (Sífilis)"
                },
                {
                    "tipo": "rapida",
                    "codigo": "86703.01",
                    "descripcion": "Prueba rápida VIH",
                    "tipo_dx": "D",
                    "lab_valores": ["RN", "RP"]
                }
            ],
            "post_test": {
                "negativo": {
                    "codigo": "99401.34",
                    "descripcion": "Consejería post test negativo",
                    "tipo_dx": "D",
                    "lab_valores": [""]
                },
                "positivo": {
                    "codigo": "99403.03",
                    "descripcion": "Consejería post test positivo",
                    "tipo_dx": "D",
                    "lab_valores": [""]
                }
            }
        },
        "frecuencia": "1 vez al año",
        "meta": 100
    },
    
    "consejeria_integral": {
        "nombre": "Orientación y Consejería Integral",
        "descripcion": "Consejería integral en salud sexual, nutricional y mental",
        "edad_min": 18,
        "edad_max": 29,
        "reglas": [
            {
                "codigo": "99401",
                "descripcion": "Consejería integral",
                "tipo_dx": "D",
                "lab_valores": [""],
                "obligatorio": True
            },
            {
                "codigo": "99402.03",
                "descripcion": "Consejería salud sexual y reproductiva",
                "tipo_dx": "D",
                "lab_valores": ["1"],
                "obligatorio": True
            },
            {
                "codigo": "99403.01",
                "descripcion": "Consejería alimentación saludable",
                "tipo_dx": "D",
                "lab_valores": [""],
                "obligatorio": True
            },
            {
                "codigo": "99402.09",
                "descripcion": "Consejería salud mental",
                "tipo_dx": "D",
                "lab_valores": [""],
                "obligatorio": True
            }
        ],
        "requiere_todos": True,
        "frecuencia": "1 vez al año",
        "meta": 100
    },
    
    "sintomatico_respiratorio": {
        "nombre": "Sintomático Respiratorio Identificado",
        "descripcion": "Captación para sintomático respiratorio identificado",
        "edad_min": 18,
        "edad_max": 29,
        "reglas": [
            {
                "codigo": "Z030",
                "descripcion": "Sintomático identificado",
                "tipo_dx": ["D", "R"],
                "lab_descripcion": "Según grupo de riesgo"
            },
            {
                "codigo": "99199.58",
                "descripcion": "Recolección de muestra",
                "tipo_dx": "D",
                "lab_valores": ["1"]
            }
        ],
        "requiere_ambos": True,
        "frecuencia": "Según necesidad",
        "meta": 100,
        "denominador_especial": "3% de atenciones"
    },
    
    "evaluacion_oral": {
        "nombre": "Evaluación Oral Completa",
        "descripcion": "Registro y diagnóstico del sistema estomatognático",
        "edad_min": 18,
        "edad_max": 29,
        "reglas": [
            {
                "codigo": "D0150",
                "descripcion": "Evaluación oral completa",
                "tipo_dx": "D",
                "lab_valores": ["", "CM"],
                "condicion": ["N", "R"],
                "obligatorio": True
            },
            {
                "codigo": "D1330",
                "descripcion": "Instrucción de higiene oral",
                "tipo_dx": "D",
                "lab_valores": ["1"],
                "obligatorio": True
            },
            {
                "codigo": "D1310",
                "descripcion": "Asesoría nutricional",
                "tipo_dx": "D",
                "lab_valores": ["1"],
                "obligatorio": True
            }
        ],
        "requiere_todos": True,
        "frecuencia": "1 vez al año",
        "meta": 100
    },
    
    "consejeria_prevencion_cancer": {
        "nombre": "Consejería Preventiva en Factores de Riesgo para el Cáncer",
        "descripcion": "Consejerías para prevenir cáncer e identificar factores de riesgo",
        "edad_min": 18,
        "edad_max": 29,
        "reglas": [
            {
                "codigo": "99402.08",
                "descripcion": "Consejería factores riesgo cáncer",
                "tipo_dx": "D",
                "lab_valores": ["1", "2"],
                "lab_descripcion": "2 sesiones al año"
            }
        ],
        "frecuencia": "2 veces al año",
        "meta": 100
    },
    
    "consejeria_ssr": {
        "nombre": "Consejería en Salud Sexual y Reproductiva",
        "descripcion": "Proceso de diálogo para toma de decisiones en SSR",
        "edad_min": 18,
        "edad_max": 29,
        "reglas": [
            {
                "codigo": "99402.03",
                "descripcion": "Consejería/Orientación SSR",
                "tipo_dx": "D",
                "lab_valores": ["1"]
            }
        ],
        "frecuencia": "1 vez al año",
        "meta": 100
    },
    
    "plan_atencion_iniciado": {
        "nombre": "Plan de Atención Iniciado",
        "descripcion": "Plan de atención integral elaborado al inicio",
        "edad_min": 18,
        "edad_max": 29,
        "reglas": [
            {
                "codigo": "99801",
                "descripcion": "Plan de atención integral",
                "tipo_dx": "D",
                "lab_valores": ["1"],
                "lab_descripcion": "1=Plan iniciado"
            }
        ],
        "frecuencia": "Al inicio del año",
        "meta": 100
    },
    
    "plan_atencion_ejecutado": {
        "nombre": "Plan de Atención Ejecutado",
        "descripcion": "Plan de atención integral completado con todas las prestaciones",
        "edad_min": 18,
        "edad_max": 29,
        "reglas": [
            {
                "codigo": "99801",
                "descripcion": "Plan de atención integral",
                "tipo_dx": "D",
                "lab_valores": ["TA"],
                "lab_descripcion": "TA=Plan ejecutado"
            }
        ],
        "frecuencia": "Al completar paquete",
        "meta": 100,
        "requiere_paquete_completo": True
    },
    
    "tamizaje_alcohol_drogas": {
        "nombre": "Tamizaje en Alcohol y Drogas",
        "descripcion": "Detectar trastornos de comportamiento por consumo de alcohol y drogas",
        "edad_min": 18,
        "edad_max": 29,
        "reglas": [
            {
                "codigo": "96150.02",
                "descripcion": "Tamizaje alcohol y drogas",
                "tipo_dx": "D",
                "lab_valores": [""],
                "obligatorio": True
            },
            {
                "codigo": "99402.09",
                "descripcion": "Consejería salud mental",
                "tipo_dx": "D",
                "lab_valores": [""],
                "obligatorio": True
            }
        ],
        "requiere_ambos": True,
        "frecuencia": "1 vez al año",
        "meta": 100
    },
    
    "tamizaje_depresion": {
        "nombre": "Tamizaje en Trastornos Depresivos",
        "descripcion": "Detectar trastornos mentales como ansiedad y depresión",
        "edad_min": 18,
        "edad_max": 29,
        "reglas": [
            {
                "codigo": "96150.03",
                "descripcion": "Tamizaje depresión y ansiedad",
                "tipo_dx": "D",
                "lab_valores": [""],
                "obligatorio": True
            },
            {
                "codigo": "99402.09",
                "descripcion": "Consejería salud mental",
                "tipo_dx": "D",
                "lab_valores": [""],
                "obligatorio": True
            }
        ],
        "requiere_ambos": True,
        "frecuencia": "1 vez al año",
        "meta": 100
    },
    
    "acceso_anticonceptivos": {
        "nombre": "Acceso a Método Anticonceptivo",
        "descripcion": "Acceso informado y voluntario a método anticonceptivo",
        "edad_min": 18,
        "edad_max": 29,
        "reglas": {
            "atencion_pf": {
                "codigo": "99208",
                "descripcion": "Atención planificación familiar",
                "tipo_dx": "D",
                "lab_valores": [""]
            },
            "consejeria_pf": {
                "codigo": "99402.04",
                "descripcion": "Consejería PF",
                "tipo_dx": "D",
                "lab_valores": ["1"],
                "condicion": "Nueva, reingresante o cambio método"
            },
            "riesgo_reproductivo": {
                "codigo": "99208.14",
                "descripcion": "Evaluación riesgo reproductivo",
                "tipo_dx": "D",
                "lab_valores": ["RSM", "RSR", "RSA"],
                "lab_descripcion": "RSM=Riesgo Bajo, RSR=Regular, RSA=Alto"
            },
            "metodos": [
                {"codigo": "58300", "descripcion": "DIU", "tipo_dx": "D"},
                {"codigo": "58300.01", "descripcion": "SIU", "tipo_dx": "D"},
                {"codigo": "11975", "descripcion": "Implante", "tipo_dx": "D"},
                {"codigo": "99208.05", "descripcion": "Inyectable trimestral", "tipo_dx": "D"},
                {"codigo": "99208.04", "descripcion": "Inyectable mensual", "tipo_dx": "D"},
                {"codigo": "99208.02", "descripcion": "Condón masculino", "tipo_dx": "D"},
                {"codigo": "99208.06", "descripcion": "Condón femenino", "tipo_dx": "D"},
                {"codigo": "99208.13", "descripcion": "Oral combinado", "tipo_dx": "D"},
                {"codigo": "99208.12", "descripcion": "AOE", "tipo_dx": "D"},
                {"codigo": "99208.11", "descripcion": "Yuzpe", "tipo_dx": "D"},
                {"codigo": "99208.07", "descripcion": "MELA", "tipo_dx": "D"},
                {"codigo": "99208.08", "descripcion": "Ritmo", "tipo_dx": "D"},
                {"codigo": "99208.09", "descripcion": "Billings", "tipo_dx": "D"},
                {"codigo": "58611", "descripcion": "Ligadura trompas", "tipo_dx": "D"},
                {"codigo": "58605", "descripcion": "Ligadura laparoscópica", "tipo_dx": "D"},
                {"codigo": "55250", "descripcion": "Vasectomía", "tipo_dx": "D"}
            ]
        },
        "frecuencia": "Según demanda",
        "meta": 100
    }
}

# Definición del Paquete de Atención Integral para Joven
PAQUETE_INTEGRAL_JOVEN = {
    "nombre": "Paquete de Cuidado Integral Joven",
    "descripcion": "Atención integral de salud para jóvenes 18-29 años",
    "componentes_minimos": [
        {
            "componente": "Valoración Clínica",
            "indicador": "valoracion_clinica_sin_factores",
            "obligatorio": True,
            "nota": "Usar valoracion_clinica_con_factores si hay factores de riesgo"
        },
        {
            "componente": "Tamizaje Violencia Intrafamiliar",
            "indicador": "tamizaje_violencia",
            "obligatorio": True
        },
        {
            "componente": "Tamizaje Alcohol y Drogas",
            "indicador": "tamizaje_alcohol_drogas",
            "obligatorio": True
        },
        {
            "componente": "Tamizaje Depresión",
            "indicador": "tamizaje_depresion",
            "obligatorio": True
        },
        {
            "componente": "Evaluación Nutricional y Antropométrica",
            "indicador": "evaluacion_nutricional",
            "obligatorio": True
        },
        {
            "componente": "Consejería Salud Sexual y Reproductiva",
            "indicador": "consejeria_ssr",
            "obligatorio": True
        }
    ],
    "registro_paquete": {
        "inicio": {"codigo": "99801", "tipo_dx": "D", "lab": "1"},
        "fin": {"codigo": "99801", "tipo_dx": "D", "lab": "TA"}
    }
}

def verificar_cumplimiento_indicador(df, indicador_key, fecha_inicio=None, fecha_fin=None):
    """
    Verifica el cumplimiento de un indicador específico para jóvenes
    Retorna DataFrame con DNIs que cumplen y detalles
    """
    if indicador_key not in INDICADORES_JOVEN:
        return None
    
    indicador = INDICADORES_JOVEN[indicador_key]
    
    # Filtrar por edad
    df_edad = df[
        (df['edad_anos'] >= indicador['edad_min']) & 
        (df['edad_anos'] <= indicador['edad_max'])
    ]
    
    # Filtrar por fechas si se especifican
    if fecha_inicio and fecha_fin:
        df_edad = df_edad[
            (df_edad['Fecha_Atencion'] >= fecha_inicio) & 
            (df_edad['Fecha_Atencion'] <= fecha_fin)
        ]
    
    # Verificar reglas según tipo de indicador
    if indicador_key in ["valoracion_clinica_sin_factores", "valoracion_clinica_con_factores"]:
        return verificar_valoracion_clinica(df_edad, indicador_key)
    elif indicador_key == "tamizaje_vih":
        return verificar_tamizaje_vih(df_edad)
    elif indicador_key == "acceso_anticonceptivos":
        return verificar_anticonceptivos(df_edad)
    elif 'requiere_ambos' in indicador and indicador['requiere_ambos']:
        return verificar_indicador_multiple(df_edad, indicador)
    elif 'requiere_todos' in indicador and indicador['requiere_todos']:
        return verificar_indicador_todos(df_edad, indicador)
    else:
        return verificar_indicador_simple(df_edad, indicador)

def verificar_indicador_simple(df, indicador):
    """Verifica indicadores con una sola regla"""
    regla = indicador['reglas'][0]
    
    # Filtrar por código
    df_codigo = df[df['Codigo_Item'] == regla['codigo']]
    
    # Filtrar por tipo diagnóstico
    if isinstance(regla['tipo_dx'], list):
        df_codigo = df_codigo[df_codigo['Tipo_Diagnostico'].isin(regla['tipo_dx'])]
    else:
        df_codigo = df_codigo[df_codigo['Tipo_Diagnostico'] == regla['tipo_dx']]
    
    # Filtrar por valores Lab si aplica
    if 'lab_valores' in regla and regla['lab_valores']:
        if "" in regla['lab_valores']:
            # Incluir valores vacíos
            df_codigo = df_codigo[
                df_codigo['Valor_Lab'].isna() | 
                df_codigo['Valor_Lab'].isin(regla['lab_valores'])
            ]
        else:
            df_codigo = df_codigo[df_codigo['Valor_Lab'].isin(regla['lab_valores'])]
    
    # Filtrar por condición si aplica
    if 'condicion' in regla:
        df_codigo = df_codigo[df_codigo['Condicion_Establecimiento'].isin(regla['condicion'])]
    
    return df_codigo

def verificar_indicador_multiple(df, indicador):
    """Verifica indicadores que requieren múltiples códigos"""
    dfs_cumplimiento = []
    
    for regla in indicador['reglas']:
        df_temp = df[
            (df['Codigo_Item'] == regla['codigo']) &
            (df['Tipo_Diagnostico'] == regla['tipo_dx'])
        ]
        
        if 'lab_valores' in regla and regla['lab_valores']:
            if "" in regla['lab_valores']:
                df_temp = df_temp[
                    df_temp['Valor_Lab'].isna() | 
                    df_temp['Valor_Lab'].isin(regla['lab_valores'])
                ]
            else:
                df_temp = df_temp[df_temp['Valor_Lab'].isin(regla['lab_valores'])]
        
        dfs_cumplimiento.append(df_temp['pac_Numero_Documento'].unique())
    
    # Encontrar DNIs que tienen todos los códigos requeridos
    dni_comun = set(dfs_cumplimiento[0])
    for dni_set in dfs_cumplimiento[1:]:
        dni_comun = dni_comun.intersection(set(dni_set))
    
    return df[df['pac_Numero_Documento'].isin(list(dni_comun))]

def verificar_indicador_todos(df, indicador):
    """Verifica indicadores que requieren todos los componentes"""
    dni_cumple = set()
    
    # Agrupar por DNI
    for dni in df['pac_Numero_Documento'].unique():
        df_dni = df[df['pac_Numero_Documento'] == dni]
        cumple_todos = True
        
        for regla in indicador['reglas']:
            df_codigo = df_dni[
                (df_dni['Codigo_Item'] == regla['codigo']) &
                (df_dni['Tipo_Diagnostico'] == regla['tipo_dx'])
            ]
            
            if 'lab_valores' in regla and regla['lab_valores']:
                if "" in regla['lab_valores']:
                    df_codigo = df_codigo[
                        df_codigo['Valor_Lab'].isna() | 
                        df_codigo['Valor_Lab'].isin(regla['lab_valores'])
                    ]
                else:
                    df_codigo = df_codigo[df_codigo['Valor_Lab'].isin(regla['lab_valores'])]
            
            if df_codigo.empty:
                cumple_todos = False
                break
        
        if cumple_todos:
            dni_cumple.add(dni)
    
    return df[df['pac_Numero_Documento'].isin(list(dni_cumple))]

def verificar_valoracion_clinica(df, indicador_key):
    """Verificación para valoración clínica con o sin factores de riesgo"""
    # Usar la lógica estándar según el indicador específico
    return verificar_indicador_todos(df, INDICADORES_JOVEN[indicador_key])

def verificar_tamizaje_vih(df):
    """Verificación especial para tamizaje VIH con su flujo específico"""
    # Buscar pre-test
    df_pretest = df[
        (df['Codigo_Item'] == '99401.33') & 
        (df['Tipo_Diagnostico'] == 'D')
    ]
    
    # Buscar pruebas (dual o rápida)
    df_dual = df[
        (df['Codigo_Item'] == '86318.01') & 
        (df['Tipo_Diagnostico'] == 'D')
    ]
    
    df_rapida = df[
        (df['Codigo_Item'] == '86703.01') & 
        (df['Tipo_Diagnostico'] == 'D')
    ]
    
    # Buscar post-test
    df_posttest = df[
        (df['Codigo_Item'].isin(['99401.34', '99403.03'])) & 
        (df['Tipo_Diagnostico'] == 'D')
    ]
    
    # DNIs con flujo completo
    dni_pretest = set(df_pretest['pac_Numero_Documento'].unique())
    dni_prueba = set(df_dual['pac_Numero_Documento'].unique()) | set(df_rapida['pac_Numero_Documento'].unique())
    dni_posttest = set(df_posttest['pac_Numero_Documento'].unique())
    
    dni_completo = dni_pretest & dni_prueba & dni_posttest
    
    return df[df['pac_Numero_Documento'].isin(list(dni_completo))]

def verificar_anticonceptivos(df):
    """Verificación especial para acceso a anticonceptivos"""
    # Buscar atención PF
    df_atencion = df[
        (df['Codigo_Item'] == '99208') & 
        (df['Tipo_Diagnostico'] == 'D')
    ]
    
    # Buscar método anticonceptivo
    metodos_codigos = ["58300", "58300.01", "11975", "99208.05", "99208.04", 
                      "99208.02", "99208.06", "99208.13", "99208.12", "99208.11",
                      "99208.07", "99208.08", "99208.09", "58611", "58605", "55250"]
    
    df_metodo = df[
        (df['Codigo_Item'].isin(metodos_codigos)) & 
        (df['Tipo_Diagnostico'] == 'D')
    ]
    
    # Buscar evaluación riesgo reproductivo
    df_riesgo = df[
        (df['Codigo_Item'] == '99208.14') & 
        (df['Tipo_Diagnostico'] == 'D') &
        (df['Valor_Lab'].isin(['RSM', 'RSR', 'RSA']))
    ]
    
    # DNIs con atención completa
    dni_atencion = set(df_atencion['pac_Numero_Documento'].unique())
    dni_metodo = set(df_metodo['pac_Numero_Documento'].unique())
    dni_riesgo = set(df_riesgo['pac_Numero_Documento'].unique())
    
    # Debe tener atención, método y evaluación de riesgo
    dni_completo = dni_atencion & dni_metodo & dni_riesgo
    
    return df[df['pac_Numero_Documento'].isin(list(dni_completo))]

def calcular_estadisticas_indicador(df, indicador_key, poblacion_total=None):
    """Calcula estadísticas de cumplimiento para un indicador"""
    df_cumple = verificar_cumplimiento_indicador(df, indicador_key)
    
    if df_cumple is None:
        return None
    
    indicador = INDICADORES_JOVEN[indicador_key]
    
    # Contar DNIs únicos que cumplen
    dni_cumplen = df_cumple['pac_Numero_Documento'].nunique()
    
    # Calcular denominador
    if poblacion_total and 'denominador_especial' in indicador:
        if "%" in indicador['denominador_especial']:
            porcentaje = float(indicador['denominador_especial'].split('%')[0])
            denominador = int(poblacion_total * porcentaje / 100)
        else:
            denominador = poblacion_total * 0.3  # 30% por defecto
    else:
        # Contar población elegible en los datos
        df_elegible = df[
            (df['edad_anos'] >= indicador['edad_min']) & 
            (df['edad_anos'] <= indicador['edad_max'])
        ]
        
        denominador = df_elegible['pac_Numero_Documento'].nunique()
    
    porcentaje = (dni_cumplen / denominador * 100) if denominador > 0 else 0
    
    return {
        'indicador': indicador['nombre'],
        'numerador': dni_cumplen,
        'denominador': denominador,
        'porcentaje': round(porcentaje, 2),
        'meta': indicador['meta'],
        'brecha': round(indicador['meta'] - porcentaje, 2),
        'clasificacion': clasificar_cumplimiento(porcentaje)
    }

def clasificar_cumplimiento(porcentaje):
    """Clasifica el cumplimiento según rangos establecidos"""
    if porcentaje >= 80:
        return "Satisfactorio"
    elif porcentaje >= 70:
        return "Aceptable"
    elif porcentaje >= 60:
        return "En proceso"
    else:
        return "Crítico"

def verificar_paquete_integral(df, dni=None):
    """Verifica el cumplimiento del paquete integral completo para jóvenes"""
    if dni:
        df = df[df['pac_Numero_Documento'] == dni]
    
    resultados = {
        'dni': dni,
        'componentes': {},
        'completo': False
    }
    
    # Verificar cada componente
    cumplimientos = []
    
    for componente in PAQUETE_INTEGRAL_JOVEN['componentes_minimos']:
        # Usar indicador existente
        df_cumple = verificar_cumplimiento_indicador(df, componente['indicador'])
        cumple = dni in df_cumple['pac_Numero_Documento'].unique() if df_cumple is not None else False
        resultados['componentes'][componente['componente']] = cumple
        cumplimientos.append(cumple)
    
    # Verificar si tiene plan elaborado y ejecutado
    plan_elaborado = not df[
        (df['pac_Numero_Documento'] == dni) &
        (df['Codigo_Item'] == '99801') &
        (df['Tipo_Diagnostico'] == 'D') &
        (df['Valor_Lab'] == '1')
    ].empty
    
    plan_ejecutado = not df[
        (df['pac_Numero_Documento'] == dni) &
        (df['Codigo_Item'] == '99801') &
        (df['Tipo_Diagnostico'] == 'D') &
        (df['Valor_Lab'] == 'TA')
    ].empty
    
    resultados['plan_elaborado'] = plan_elaborado
    resultados['plan_ejecutado'] = plan_ejecutado
    resultados['completo'] = all(cumplimientos) and plan_ejecutado
    
    return resultados