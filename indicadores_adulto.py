#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Definición de Indicadores para Curso de Vida Adulto (30-59 años)
Sistema HISMINSA - Supervisión de Indicadores
"""

# Diccionario completo de indicadores adulto
INDICADORES_ADULTO = {
    "evaluacion_oral": {
        "nombre": "Evaluación Oral Completa",
        "descripcion": "Porcentaje de adultos con Evaluación Oral Completa",
        "edad_min": 30,
        "edad_max": 59,
        "reglas": [
            {
                "codigo": "D0150",
                "descripcion": "Evaluación Oral Completa",
                "tipo_dx": "D",
                "lab_valores": ["", "N", "R", "G", "CM"],
                "lab_descripcion": "En blanco, N=Normal, R=Repetido, G=Gestante, CM=Caso Médico"
            }
        ],
        "frecuencia": "1 vez al año",
        "meta": 100
    },
    
    "tamizaje_violencia": {
        "nombre": "Tamizaje Violencia - WAST",
        "descripcion": "Porcentaje de Adultos con Tamizaje para Detectar Violencia",
        "edad_min": 30,
        "edad_max": 59,
        "reglas": [
            {
                "codigo": "96150.01",
                "descripcion": "Tamizaje WAST para violencia",
                "tipo_dx": "D",
                "lab_valores": ["", "G", "TPE", "JUD"],
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
    
    "agudeza_visual": {
        "nombre": "Tamizaje de Agudeza Visual",
        "descripcion": "Porcentaje de Adultos con Tamizaje de Agudeza Visual",
        "edad_min": 30,
        "edad_max": 59,
        "reglas": [
            {
                "codigo": "99173",
                "descripcion": "Determinación de agudeza visual",
                "tipo_dx": "D",
                "lab_valores": ["20", "25", "30", "40", "50", "70", "100", "200", "400", "800"],
                "lab_multiple": True,
                "lab_descripcion": "Lab1: Ojo derecho, Lab2: Ojo izquierdo"
            }
        ],
        "frecuencia": "1 vez al año",
        "meta": 100
    },
    
    "valoracion_nutricional": {
        "nombre": "Valoración Nutricional",
        "descripcion": "Porcentaje de adultos con Valoración nutricional",
        "edad_min": 30,
        "edad_max": 59,
        "reglas": [
            {
                "codigo": "99209.02",
                "descripcion": "Cálculo de IMC",
                "tipo_dx": "D",
                "obligatorio": True
            },
            {
                "codigo": "99209.03",
                "descripcion": "Evaluación del perímetro abdominal",
                "tipo_dx": "D",
                "lab_valores": ["", "RSM", "RSA", "RMA"],
                "lab_descripcion": "RSM=Riesgo Bajo, RSA=Riesgo Alto, RMA=Riesgo Muy Alto",
                "obligatorio": True
            }
        ],
        "requiere_ambos": True,
        "frecuencia": "1 vez al año",
        "meta": 100
    },
    
    "vacuna_influenza": {
        "nombre": "Vacuna Influenza",
        "descripcion": "Porcentaje de Adultos con Vacuna Influenza",
        "edad_min": 30,
        "edad_max": 59,
        "reglas": [
            {
                "codigo": "90658",
                "descripcion": "Vacuna Influenza",
                "tipo_dx": "D",
                "lab_valores": [""]
            }
        ],
        "frecuencia": "1 dosis anual",
        "meta": 100,
        "denominador_especial": "12% población INEI"
    },
    
    "sintomaticos_respiratorios": {
        "nombre": "Tamizaje Sintomáticos Respiratorios",
        "descripcion": "Porcentaje de adultos con tamizaje para sintomáticos respiratorios",
        "edad_min": 30,
        "edad_max": 59,
        "reglas": [
            {
                "codigo": "U200",
                "descripcion": "Identificación sintomático respiratorio",
                "tipo_dx": ["D", "R"],
                "lab_valores": [""]
            },
            {
                "codigo": "U2142",
                "descripcion": "Toma de muestra",
                "tipo_dx": "D",
                "lab_valores": ["1"]
            }
        ],
        "frecuencia": "Según necesidad",
        "meta": 100,
        "denominador_especial": "3% de atenciones"
    },
    
    "tamizaje_vih": {
        "nombre": "Tamizaje VIH",
        "descripcion": "Porcentaje de Adultos tamizados con pruebas rápidas para VIH",
        "edad_min": 30,
        "edad_max": 59,
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
                    "tipo": "rapida_negativa",
                    "codigo": "86703.01",
                    "descripcion": "Prueba rápida VIH negativo",
                    "tipo_dx": "D",
                    "lab_valores": ["RN"]
                },
                {
                    "tipo": "rapida_reactiva",
                    "codigo": "86703.02",
                    "descripcion": "Prueba rápida VIH reactivo",
                    "tipo_dx": "D",
                    "lab_valores": ["RP"]
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
    
    "tamizaje_hepatitis_b": {
        "nombre": "Tamizaje Hepatitis B",
        "descripcion": "Porcentaje de adultos tamizados con pruebas rápidas para Hepatitis B",
        "edad_min": 30,
        "edad_max": 59,
        "reglas": [
            {
                "codigo": "87342",
                "descripcion": "Tamizaje Hepatitis B",
                "tipo_dx": "D",
                "lab_valores": ["RN", "RP"],
                "lab_descripcion": "RN=Reactivo Negativo, RP=Reactivo Positivo"
            }
        ],
        "frecuencia": "1 vez al año",
        "meta": 100
    },
    
    "tamizaje_alcohol_drogas": {
        "nombre": "Tamizaje en Alcohol y Drogas",
        "descripcion": "Detectar trastornos de comportamiento por consumo de alcohol y drogas",
        "edad_min": 30,
        "edad_max": 59,
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
    
    "cancer_cuello_uterino": {
        "nombre": "Tamizaje Cáncer Cuello Uterino",
        "descripcion": "Porcentaje de Mujeres Adultas con Tamizaje para Cáncer de Cuello Uterino",
        "genero": "F",
        "edad_min": 30,
        "edad_max": 59,
        "reglas": [
            {
                "codigo": "87621",
                "descripcion": "Detección Molecular VPH",
                "tipo_dx": "D",
                "lab_valores": ["N", "A"],
                "edad_min": 30,
                "edad_max": 49
            },
            {
                "codigo": "88141.01",
                "descripcion": "Inspección Visual con Ácido Acético",
                "tipo_dx": "D",
                "lab_valores": ["N", "A"],
                "edad_min": 30,
                "edad_max": 49
            },
            {
                "codigo": "88141",
                "descripcion": "Papanicolaou",
                "tipo_dx": "D",
                "lab_valores": ["N", "A"],
                "edad_min": 30,
                "edad_max": 59
            }
        ],
        "requiere_uno": True,
        "frecuencia": "Según método",
        "meta": 100,
        "denominador_especial": "20% población femenina afiliada SIS"
    },
    
    "cancer_prostata": {
        "nombre": "Tamizaje Cáncer Próstata",
        "descripcion": "Porcentaje de Adultos Varones de 50 a 59 años con Tamizaje para Detección de Cáncer de Próstata",
        "genero": "M",
        "edad_min": 50,
        "edad_max": 59,
        "reglas": [
            {
                "codigo": "84152",
                "descripcion": "Dosaje PSA",
                "tipo_dx": "D",
                "lab_valores": ["N", "A"],
                "lab_descripcion": "N=Normal, A=Anormal"
            }
        ],
        "frecuencia": "1 vez al año",
        "meta": 100,
        "denominador_especial": "15% varones 50-59 afiliados SIS"
    },
    
    "cancer_colon_recto": {
        "nombre": "Tamizaje Cáncer Colon y Recto",
        "descripcion": "Porcentaje de Personas Adultas con Tamizaje para Detección de Cáncer de Colon y Recto",
        "edad_min": 50,
        "edad_max": 59,
        "reglas": [
            {
                "codigo": "82270",
                "descripcion": "Test sangre oculta en heces",
                "tipo_dx": "D",
                "lab_valores": ["N", "A"],
                "lab_descripcion": "N=Normal, A=Anormal"
            }
        ],
        "frecuencia": "Cada 2 años",
        "meta": 100,
        "denominador_especial": "15% población 50-59 afiliados SIS"
    },
    
    "trastornos_depresivos": {
        "nombre": "Tamizaje Trastornos Depresivos (PHQ-9)",
        "descripcion": "Porcentaje de Adultos con Tamizaje para Detectar Trastornos Depresivos",
        "edad_min": 30,
        "edad_max": 59,
        "reglas": [
            {
                "codigo": "96150.03",
                "descripcion": "Tamizaje PHQ-9",
                "tipo_dx": "D",
                "lab_valores": ["", "G", "TPE", "JUD"],
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
    
    "plan_atencion_elaborado": {
        "nombre": "Plan de Atención Integral Elaborado",
        "descripcion": "Porcentaje de Adultos con Plan de Atención Integral Elaborado",
        "edad_min": 30,
        "edad_max": 59,
        "reglas": [
            {
                "codigo": "99801",
                "descripcion": "Plan de Atención Integral",
                "tipo_dx": "D",
                "lab_valores": ["1"],
                "lab_descripcion": "1=Plan elaborado"
            }
        ],
        "frecuencia": "Al inicio del año",
        "meta": 100
    },
    
    "plan_atencion_ejecutado": {
        "nombre": "Plan de Atención Integral Ejecutado",
        "descripcion": "Adultos con Plan de Atención Integral Ejecutado",
        "edad_min": 30,
        "edad_max": 59,
        "reglas": [
            {
                "codigo": "99801",
                "descripcion": "Plan de Atención Integral",
                "tipo_dx": "D",
                "lab_valores": ["TA"],
                "lab_descripcion": "TA=Plan ejecutado"
            }
        ],
        "frecuencia": "Al completar paquete",
        "meta": 100
    },
    
    "consejeria_ssr": {
        "nombre": "Consejería Salud Sexual y Reproductiva",
        "descripcion": "Porcentaje de adultos con consejería en Salud Sexual y Reproductiva",
        "edad_min": 30,
        "edad_max": 59,
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
    
    "valoracion_clinica_sin_factores": {
        "nombre": "Valoración Clínica SIN Factores de Riesgo",
        "descripcion": "Valoración clínica sin factores de riesgo (sin laboratorio para 30-39 años)",
        "edad_min": 30,
        "edad_max": 59,
        "reglas": [
            {
                "codigo": "Z019",
                "descripcion": "Valoración clínica",
                "tipo_dx": "D",
                "lab_valores": ["DNT"],
                "obligatorio": True
            },
            {
                "codigo": "99199.22",
                "descripcion": "Tamizaje Presión Arterial",
                "tipo_dx": "D",
                "lab_valores": ["N", "A"],
                "obligatorio": True
            }
        ],
        "requiere_todos": True,
        "frecuencia": "1 vez al año",
        "meta": 100,
        "nota": "Laboratorio Z017 solo para 40-59 años"
    },
    
    "valoracion_clinica_con_factores": {
        "nombre": "Valoración Clínica CON Factores de Riesgo",
        "descripcion": "Valoración clínica con factores de riesgo y consejería (laboratorio según edad)",
        "edad_min": 30,
        "edad_max": 59,
        "reglas": [
            {
                "codigo": "Z019",
                "descripcion": "Valoración clínica",
                "tipo_dx": "D",
                "lab_valores": ["DNT"],
                "obligatorio": True
            },
            {
                "codigo": "99199.22",
                "descripcion": "Tamizaje Presión Arterial",
                "tipo_dx": "D",
                "lab_valores": ["N", "A"],
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
        "meta": 100,
        "nota": "Laboratorio Z017 para 40-59 años o 30-39 con factores"
    }
}

# Definición del Paquete de Atención Integral
PAQUETE_INTEGRAL_ADULTO = {
    "nombre": "Paquete de Cuidado Integral Adulto",
    "descripcion": "Conjunto articulado de cuidados esenciales para adultos 30-59 años",
    "componentes_minimos": [
        {
            "componente": "Valoración Clínica",
            "indicador": "valoracion_clinica_sin_factores",
            "obligatorio": True,
            "nota": "Usar valoracion_clinica_con_factores si hay factores de riesgo"
        },
        {
            "componente": "Tamizaje Trastornos Depresivos",
            "indicador": "trastornos_depresivos",
            "obligatorio": True
        },
        {
            "componente": "Tamizaje Violencia",
            "indicador": "tamizaje_violencia",
            "obligatorio": True
        },
        {
            "componente": "Tamizaje VIH",
            "indicador": "tamizaje_vih",
            "obligatorio": True
        },
        {
            "componente": "Tamizaje Agudeza Visual",
            "indicador": "agudeza_visual",
            "obligatorio": True
        },
        {
            "componente": "Evaluación Oral Completa",
            "indicador": "evaluacion_oral",
            "obligatorio": True
        },
        {
            "componente": "Tamizaje Alcohol y Drogas",
            "indicador": "tamizaje_alcohol_drogas",
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
    Verifica el cumplimiento de un indicador específico
    Retorna DataFrame con DNIs que cumplen y detalles
    """
    if indicador_key not in INDICADORES_ADULTO:
        return None
    
    indicador = INDICADORES_ADULTO[indicador_key]
    
    # Filtrar por edad
    df_edad = df[
        (df['edad_anos'] >= indicador['edad_min']) & 
        (df['edad_anos'] <= indicador['edad_max'])
    ]
    
    # Filtrar por género si aplica
    if 'genero' in indicador:
        df_edad = df_edad[df_edad['pac_Genero'] == indicador['genero']]
    
    # Filtrar por fechas si se especifican
    if fecha_inicio and fecha_fin:
        df_edad = df_edad[
            (df_edad['Fecha_Atencion'] >= fecha_inicio) & 
            (df_edad['Fecha_Atencion'] <= fecha_fin)
        ]
    
    # Verificar reglas según tipo de indicador
    if indicador_key == "tamizaje_vih":
        return verificar_tamizaje_vih(df_edad)
    elif 'requiere_ambos' in indicador and indicador['requiere_ambos']:
        return verificar_indicador_multiple(df_edad, indicador)
    elif 'requiere_uno' in indicador and indicador['requiere_uno']:
        return verificar_indicador_opciones(df_edad, indicador)
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
        (df['Codigo_Item'].isin(['86703.01', '86703.02'])) & 
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

def verificar_indicador_opciones(df, indicador):
    """Verifica indicadores donde se requiere al menos una opción"""
    dni_cumple = set()
    
    for regla in indicador['reglas']:
        df_temp = df[
            (df['Codigo_Item'] == regla['codigo']) &
            (df['Tipo_Diagnostico'] == regla['tipo_dx'])
        ]
        
        if 'edad_min' in regla:
            df_temp = df_temp[
                (df_temp['edad_anos'] >= regla['edad_min']) &
                (df_temp['edad_anos'] <= regla['edad_max'])
            ]
        
        if 'lab_valores' in regla:
            df_temp = df_temp[df_temp['Valor_Lab'].isin(regla['lab_valores'])]
        
        dni_cumple.update(df_temp['pac_Numero_Documento'].unique())
    
    return df[df['pac_Numero_Documento'].isin(list(dni_cumple))]

def calcular_estadisticas_indicador(df, indicador_key, poblacion_total=None):
    """Calcula estadísticas de cumplimiento para un indicador"""
    df_cumple = verificar_cumplimiento_indicador(df, indicador_key)
    
    if df_cumple is None:
        return None
    
    indicador = INDICADORES_ADULTO[indicador_key]
    
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
        if 'genero' in indicador:
            df_elegible = df_elegible[df_elegible['pac_Genero'] == indicador['genero']]
        
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
    """Verifica el cumplimiento del paquete integral completo"""
    if dni:
        df = df[df['pac_Numero_Documento'] == dni]
    
    resultados = {
        'dni': dni,
        'componentes': {},
        'completo': False
    }
    
    # Verificar cada componente
    cumplimientos = []
    
    for componente in PAQUETE_INTEGRAL_ADULTO['componentes_minimos']:
        if 'indicador' in componente:
            # Usar indicador existente
            df_cumple = verificar_cumplimiento_indicador(df, componente['indicador'])
            cumple = dni in df_cumple['pac_Numero_Documento'].unique() if df_cumple is not None else False
            resultados['componentes'][componente['componente']] = cumple
            cumplimientos.append(cumple)
        else:
            # Verificar reglas específicas por edad y factores
            if componente['componente'] == "Valoración Clínica":
                edad = df[df['pac_Numero_Documento'] == dni]['edad_anos'].iloc[0] if not df.empty else 0
                
                # Detectar si tiene factores de riesgo
                factores_riesgo = ['E65X', 'E669', 'E6691', 'E6692', 'E6693', 'E6690', 
                                  'Z720', 'Z721', 'Z723', 'Z724', 'Z783', 'Z784']
                tiene_factores = not df[(df['pac_Numero_Documento'] == dni) & 
                                      (df['Codigo_Item'].isin(factores_riesgo))].empty
                
                # Usar el indicador apropiado
                if tiene_factores:
                    df_cumple = verificar_cumplimiento_indicador(df, 'valoracion_clinica_con_factores')
                else:
                    df_cumple = verificar_cumplimiento_indicador(df, 'valoracion_clinica_sin_factores')
                
                cumple = dni in df_cumple['pac_Numero_Documento'].unique() if df_cumple is not None else False
                
                # Verificar laboratorio adicional según edad
                if cumple and (edad >= 40 or (30 <= edad <= 39 and tiene_factores)):
                    tiene_lab = not df[(df['pac_Numero_Documento'] == dni) & 
                                     (df['Codigo_Item'] == 'Z017') & 
                                     (df['Tipo_Diagnostico'] == 'D')].empty
                    cumple = cumple and tiene_lab
                
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

def verificar_valoracion_clinica_30_39(df, dni):
    """Verifica valoración clínica para 30-39 años"""
    df_dni = df[df['pac_Numero_Documento'] == dni]
    
    # Verificar componentes obligatorios
    tiene_valoracion = not df_dni[
        (df_dni['Codigo_Item'] == 'Z019') & 
        (df_dni['Tipo_Diagnostico'] == 'D') &
        (df_dni['Valor_Lab'] == 'DNT')
    ].empty
    
    tiene_presion = not df_dni[
        (df_dni['Codigo_Item'] == '99199.22') & 
        (df_dni['Tipo_Diagnostico'] == 'D')
    ].empty
    
    tiene_consejeria = not df_dni[
        (df_dni['Codigo_Item'] == '99401.13') & 
        (df_dni['Tipo_Diagnostico'] == 'D')
    ].empty
    
    # Verificar si tiene factores de riesgo
    factores_riesgo = ['E65X', 'E669', 'E6691', 'E6692', 'E6693', 'E6690', 
                      'Z720', 'Z721', 'Z723', 'Z724', 'Z783', 'Z784']
    
    tiene_factores = not df_dni[df_dni['Codigo_Item'].isin(factores_riesgo)].empty
    
    # Si tiene factores, debe tener laboratorio
    if tiene_factores:
        tiene_lab = not df_dni[
            (df_dni['Codigo_Item'] == 'Z017') & 
            (df_dni['Tipo_Diagnostico'] == 'D')
        ].empty
        return tiene_valoracion and tiene_presion and tiene_consejeria and tiene_lab
    else:
        return tiene_valoracion and tiene_presion and tiene_consejeria

def verificar_valoracion_clinica_40_59(df, dni):
    """Verifica valoración clínica para 40-59 años"""
    df_dni = df[df['pac_Numero_Documento'] == dni]
    
    tiene_valoracion = not df_dni[
        (df_dni['Codigo_Item'] == 'Z019') & 
        (df_dni['Tipo_Diagnostico'] == 'D') &
        (df_dni['Valor_Lab'] == 'DNT')
    ].empty
    
    tiene_lab = not df_dni[
        (df_dni['Codigo_Item'] == 'Z017') & 
        (df_dni['Tipo_Diagnostico'] == 'D')
    ].empty
    
    tiene_presion = not df_dni[
        (df_dni['Codigo_Item'] == '99199.22') & 
        (df_dni['Tipo_Diagnostico'] == 'D')
    ].empty
    
    tiene_consejeria = not df_dni[
        (df_dni['Codigo_Item'] == '99401.13') & 
        (df_dni['Tipo_Diagnostico'] == 'D')
    ].empty
    
    return tiene_valoracion and tiene_lab and tiene_presion and tiene_consejeria