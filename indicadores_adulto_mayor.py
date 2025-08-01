#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Definición de Indicadores para Curso de Vida Adulto Mayor (60+ años)
Sistema HISMINSA - Supervisión de Indicadores
"""

# Diccionario completo de indicadores adulto mayor
INDICADORES_ADULTO_MAYOR = {
    "paquete_atencion_integral": {
        "nombre": "Paquete de Atención Integral",
        "descripcion": "Conjunto de 7 componentes obligatorios para adultos mayores",
        "edad_min": 60,
        "edad_max": 150,
        "es_paquete": True,
        "frecuencia": "1 vez al año",
        "meta": 100,
        "denominador_especial": "40% población REUNIS"
    },
    
    "vacam": {
        "nombre": "VACAM - Valoración Clínica del Adulto Mayor",
        "descripcion": "Valoración clínica integral con clasificación funcional",
        "edad_min": 60,
        "edad_max": 150,
        "reglas": [
            {
                "codigo": "99387",
                "descripcion": "VACAM completo",
                "tipo_dx": "D",
                "lab_valores": ["AS", "E", "AF", "GC"],
                "lab_descripcion": "AS=Autosuficiente, E=Enfermo, AF=Anciano Frágil, GC=Geriátrico Complejo",
                "obligatorio": True
            },
            {
                "codigo": "99215.03",
                "descripcion": "VACAM alternativo",
                "tipo_dx": "D",
                "lab_valores": ["AS", "E", "AF", "GC"],
                "lab_descripcion": "AS=Autosuficiente, E=Enfermo, AF=Anciano Frágil, GC=Geriátrico Complejo",
                "alternativo": True
            },
            {
                "codigo": "99401",
                "descripcion": "Consejería integral",
                "tipo_dx": "D",
                "lab_valores": [""],
                "obligatorio_post_vacam": True
            }
        ],
        "requiere_uno_mas_consejeria": True,
        "frecuencia": "1 vez al año",
        "meta": 100,
        "denominador_especial": "40% población REUNIS"
    },
    
    "agudeza_visual": {
        "nombre": "Tamizaje de Agudeza Visual y Catarata",
        "descripcion": "Evaluación de agudeza visual y detección de cataratas",
        "edad_min": 60,
        "edad_max": 150,
        "reglas": {
            "opcion_a": {
                "codigos": [
                    {
                        "codigo": "99173",
                        "descripcion": "Determinación agudeza visual",
                        "tipo_dx": "D",
                        "lab_multiple": True,
                        "lab_descripcion": "Lab1: Ojo derecho, Lab2: Ojo izquierdo"
                    }
                ]
            },
            "opcion_b": {
                "codigos": [
                    {
                        "codigo": "Z010",
                        "descripcion": "Examen ojos y visión",
                        "tipo_dx": "D",
                        "lab_valores": ["N", "A"]
                    },
                    {
                        "codigo": "99173",
                        "descripcion": "Determinación agudeza visual",
                        "tipo_dx": "D",
                        "lab_multiple": True,
                        "lab_descripcion": "Lab1: Ojo derecho, Lab2: Ojo izquierdo"
                    }
                ],
                "requiere_ambos": True
            }
        },
        "frecuencia": "1 vez al año",
        "meta": 100,
        "denominador_especial": "40% población REUNIS"
    },
    
    "tamizaje_salud_mental": {
        "nombre": "Tamizaje Integral de Salud Mental",
        "descripcion": "5 tamizajes de salud mental más consejería obligatoria",
        "edad_min": 60,
        "edad_max": 150,
        "reglas": [
            {
                "codigo": "96150.01",
                "descripcion": "Tamizaje violencia intrafamiliar",
                "tipo_dx": "D",
                "lab_valores": ["", "G", "TPE", "JUD"],
                "obligatorio": True
            },
            {
                "codigo": "96150.03",
                "descripcion": "Tamizaje trastornos depresivos",
                "tipo_dx": "D",
                "lab_valores": ["", "G", "TPE", "JUD"],
                "obligatorio": True
            },
            {
                "codigo": "96150.04",
                "descripcion": "Tamizaje psicosis",
                "tipo_dx": "D",
                "lab_valores": ["", "G", "TPE", "JUD"],
                "obligatorio": True
            },
            {
                "codigo": "96150.02",
                "descripcion": "Tamizaje consumo alcohol/drogas",
                "tipo_dx": "D",
                "lab_valores": ["", "G", "TPE", "JUD"],
                "obligatorio": True
            },
            {
                "codigo": "96150.07",
                "descripcion": "Tamizaje deterioro cognitivo",
                "tipo_dx": "D",
                "lab_valores": ["", "G", "TPE", "JUD"],
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
        "meta": 100,
        "denominador_especial": "40% población REUNIS"
    },
    
    "evaluacion_oral": {
        "nombre": "Evaluación Oral Completa",
        "descripcion": "Evaluación integral del sistema estomatognático",
        "edad_min": 60,
        "edad_max": 150,
        "reglas": [
            {
                "codigo": "D0150",
                "descripcion": "Evaluación oral completa",
                "tipo_dx": "D",
                "lab_valores": ["", "CM"],
                "lab_descripcion": "En blanco o CM=Caso Médico"
            }
        ],
        "frecuencia": "1 vez al año",
        "meta": 100,
        "denominador_especial": "40% población REUNIS"
    },
    
    "vacuna_neumococo": {
        "nombre": "Vacuna Neumococo",
        "descripcion": "Vacunación contra neumococo para adultos mayores",
        "edad_min": 60,
        "edad_max": 150,
        "reglas": [
            {
                "codigo": "90670",
                "descripcion": "Vacuna neumococo",
                "tipo_dx": "D",
                "lab_valores": [""]
            }
        ],
        "frecuencia": "Dosis única",
        "meta": 100,
        "denominador_especial": "40% población REUNIS"
    },
    
    "vacuna_influenza": {
        "nombre": "Vacuna Influenza",
        "descripcion": "Vacunación anual contra influenza",
        "edad_min": 60,
        "edad_max": 150,
        "reglas": [
            {
                "codigo": "90658",
                "descripcion": "Vacuna influenza",
                "tipo_dx": "D",
                "lab_valores": [""]
            }
        ],
        "frecuencia": "1 vez al año",
        "meta": 100,
        "denominador_especial": "60% población REUNIS"
    },
    
    "consejeria_integral": {
        "nombre": "Consejería Integral para Adulto Mayor",
        "descripcion": "Consejería integral abordando múltiples temas de salud",
        "edad_min": 60,
        "edad_max": 150,
        "reglas": [
            {
                "codigo": "99401",
                "descripcion": "Consejería integral AM",
                "tipo_dx": "D",
                "lab_valores": [""]
            }
        ],
        "frecuencia": "1 vez al año",
        "meta": 100,
        "denominador_especial": "40% población REUNIS"
    },
    
    "valoracion_clinica_lab": {
        "nombre": "Valoración Clínica y Tamizaje Laboratorial",
        "descripcion": "Valoración clínica con laboratorio obligatorio en adultos mayores",
        "edad_min": 60,
        "edad_max": 150,
        "reglas": [
            {
                "codigo": "Z019",
                "descripcion": "Valoración clínica",
                "tipo_dx": "D",
                "lab_valores": ["DNT"],
                "obligatorio": True
            },
            {
                "codigo": "Z017",
                "descripcion": "Tamizaje laboratorial",
                "tipo_dx": "D",
                "lab_valores": [""],
                "obligatorio": True
            },
            {
                "codigo": "99401.13",
                "descripcion": "Consejería estilos vida saludable",
                "tipo_dx": "D",
                "lab_valores": [""],
                "obligatorio": True
            }
        ],
        "requiere_todos": True,
        "frecuencia": "1 vez al año",
        "meta": 100,
        "denominador_especial": "40% población REUNIS"
    },
    
    "vacuna_covid19": {
        "nombre": "Vacuna COVID-19",
        "descripcion": "Vacunación contra COVID-19 cada 6 meses",
        "edad_min": 60,
        "edad_max": 150,
        "reglas": [
            {
                "codigo": "90749.01",
                "descripcion": "Vacuna COVID-19",
                "tipo_dx": ["D", "DU"],
                "lab_valores": ["", "DU"],
                "lab_descripcion": "DU=Extramural"
            }
        ],
        "frecuencia": "Cada 6 meses",
        "meta": 100,
        "denominador_especial": "100% población RENIEC"
    },
    
    "visita_familiar": {
        "nombre": "Visita Familiar Integral",
        "descripcion": "Visita domiciliaria integral al adulto mayor",
        "edad_min": 60,
        "edad_max": 150,
        "reglas": [
            {
                "codigo": "C0011",
                "descripcion": "Visita familiar integral",
                "tipo_dx": "D",
                "lab_valores": ["1"]
            }
        ],
        "frecuencia": "1 vez al año",
        "meta": 100,
        "denominador_especial": "40% población REUNIS"
    },
    
    "cancer_cuello_uterino": {
        "nombre": "Tamizaje Cáncer Cuello Uterino",
        "descripcion": "Tamizaje para mujeres de 60-64 años",
        "genero": "F",
        "edad_min": 60,
        "edad_max": 64,
        "reglas": [
            {
                "codigo": "88141",
                "descripcion": "Papanicolaou",
                "tipo_dx": "D",
                "lab_valores": ["N", "A"],
                "lab_descripcion": "N=Normal, A=Anormal"
            }
        ],
        "frecuencia": "Según normativa",
        "meta": 100,
        "denominador_especial": "20% mujeres 60-64 afiliadas SIS"
    },
    
    "cancer_prostata": {
        "nombre": "Tamizaje Cáncer Próstata",
        "descripcion": "Tamizaje para varones de 60-75 años",
        "genero": "M",
        "edad_min": 60,
        "edad_max": 75,
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
        "denominador_especial": "15% varones 60-75 afiliados SIS"
    },
    
    "cancer_colon_recto": {
        "nombre": "Tamizaje Cáncer Colon y Recto",
        "descripcion": "Tamizaje para adultos de 60-70 años",
        "edad_min": 60,
        "edad_max": 70,
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
        "denominador_especial": "15% población 60-70 afiliados SIS"
    },
    
    "cancer_piel": {
        "nombre": "Tamizaje Cáncer de Piel",
        "descripcion": "Evaluación de lesiones sospechosas de piel",
        "edad_min": 60,
        "edad_max": 70,
        "reglas": [
            {
                "codigo": "Z128",
                "descripcion": "Tamizaje cáncer piel",
                "tipo_dx": "D",
                "lab_valores": ["N", "A"],
                "lab_descripcion": "N=Normal, A=Anormal"
            }
        ],
        "frecuencia": "Cada 3 años",
        "meta": 100,
        "denominador_especial": "15% población 60-70 afiliados SIS"
    },
    
    "examen_clinico_mama": {
        "nombre": "Examen Clínico de Mama",
        "descripcion": "Examen clínico para mujeres de 60-69 años",
        "genero": "F",
        "edad_min": 60,
        "edad_max": 69,
        "reglas": [
            {
                "codigo": "99386.03",
                "descripcion": "Examen clínico de mama",
                "tipo_dx": "D",
                "lab_valores": ["N", "A"],
                "lab_descripcion": "N=Normal, A=Anormal"
            }
        ],
        "frecuencia": "1 vez al año",
        "meta": 100,
        "denominador_especial": "20% mujeres 60-69 afiliadas SIS"
    },
    
    "sintomaticos_respiratorios": {
        "nombre": "Identificación de Sintomáticos Respiratorios",
        "descripcion": "Identificación y toma de muestra de sintomáticos respiratorios",
        "edad_min": 60,
        "edad_max": 150,
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
        "frecuencia": "Según demanda",
        "meta": 100,
        "denominador_especial": "3% de atenciones"
    }
}

# Definición del Paquete de Atención Integral
PAQUETE_INTEGRAL_ADULTO_MAYOR = {
    "nombre": "Paquete de Atención Integral Adulto Mayor",
    "descripcion": "7 componentes obligatorios para adultos mayores de 60+ años",
    "componentes_minimos": [
        {
            "componente": "VACAM - Valoración Clínica",
            "indicador": "vacam",
            "obligatorio": True,
            "requiere_clasificacion": True
        },
        {
            "componente": "Tamizaje Agudeza Visual",
            "indicador": "agudeza_visual",
            "obligatorio": True
        },
        {
            "componente": "Tamizaje Integral Salud Mental",
            "indicador": "tamizaje_salud_mental",
            "obligatorio": True,
            "requiere_5_tamizajes": True
        },
        {
            "componente": "Evaluación Oral Completa",
            "indicador": "evaluacion_oral",
            "obligatorio": True
        },
        {
            "componente": "Vacuna Influenza",
            "indicador": "vacuna_influenza",
            "obligatorio": True
        },
        {
            "componente": "Consejería Integral",
            "indicador": "consejeria_integral",
            "obligatorio": True
        },
        {
            "componente": "Valoración Clínica y Laboratorio",
            "indicador": "valoracion_clinica_lab",
            "obligatorio": True,
            "laboratorio_siempre": True
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
    if indicador_key not in INDICADORES_ADULTO_MAYOR:
        return None
    
    indicador = INDICADORES_ADULTO_MAYOR[indicador_key]
    
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
    if indicador_key == "vacam":
        return verificar_vacam(df_edad)
    elif indicador_key == "agudeza_visual":
        return verificar_agudeza_visual(df_edad)
    elif indicador_key == "tamizaje_salud_mental":
        return verificar_tamizaje_salud_mental(df_edad)
    elif indicador_key == "valoracion_clinica_lab":
        return verificar_valoracion_clinica_lab(df_edad)
    elif indicador_key == "paquete_atencion_integral":
        return verificar_paquete_integral_resumido(df_edad)
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
    
    return df_codigo

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

def verificar_vacam(df):
    """Verificación especial para VACAM"""
    dni_cumple = set()
    
    for dni in df['pac_Numero_Documento'].unique():
        df_dni = df[df['pac_Numero_Documento'] == dni]
        
        # Verificar VACAM (99387 o 99215.03) con clasificación obligatoria
        tiene_vacam_99387 = not df_dni[
            (df_dni['Codigo_Item'] == '99387') & 
            (df_dni['Tipo_Diagnostico'] == 'D') &
            (df_dni['Valor_Lab'].isin(['AS', 'E', 'AF', 'GC']))
        ].empty
        
        tiene_vacam_99215 = not df_dni[
            (df_dni['Codigo_Item'] == '99215.03') & 
            (df_dni['Tipo_Diagnostico'] == 'D') &
            (df_dni['Valor_Lab'].isin(['AS', 'E', 'AF', 'GC']))
        ].empty
        
        # Verificar consejería posterior
        tiene_consejeria = not df_dni[
            (df_dni['Codigo_Item'] == '99401') & 
            (df_dni['Tipo_Diagnostico'] == 'D')
        ].empty
        
        # Necesita uno de los VACAM + consejería
        if (tiene_vacam_99387 or tiene_vacam_99215) and tiene_consejeria:
            dni_cumple.add(dni)
    
    return df[df['pac_Numero_Documento'].isin(list(dni_cumple))]

def verificar_agudeza_visual(df):
    """Verificación especial para agudeza visual con opciones"""
    dni_cumple = set()
    
    for dni in df['pac_Numero_Documento'].unique():
        df_dni = df[df['pac_Numero_Documento'] == dni]
        
        # Opción A: Solo 99173
        tiene_opcion_a = not df_dni[
            (df_dni['Codigo_Item'] == '99173') & 
            (df_dni['Tipo_Diagnostico'] == 'D')
        ].empty
        
        # Opción B: Z010 + 99173
        tiene_z010 = not df_dni[
            (df_dni['Codigo_Item'] == 'Z010') & 
            (df_dni['Tipo_Diagnostico'] == 'D') &
            (df_dni['Valor_Lab'].isin(['N', 'A']))
        ].empty
        
        tiene_99173 = not df_dni[
            (df_dni['Codigo_Item'] == '99173') & 
            (df_dni['Tipo_Diagnostico'] == 'D')
        ].empty
        
        tiene_opcion_b = tiene_z010 and tiene_99173
        
        # Cumple si tiene opción A o B
        if tiene_opcion_a or tiene_opcion_b:
            dni_cumple.add(dni)
    
    return df[df['pac_Numero_Documento'].isin(list(dni_cumple))]

def verificar_tamizaje_salud_mental(df):
    """Verificación de los 5 tamizajes de salud mental + consejería"""
    dni_cumple = set()
    
    tamizajes_requeridos = [
        '96150.01',  # Violencia
        '96150.03',  # Depresión
        '96150.04',  # Psicosis
        '96150.02',  # Alcohol/drogas
        '96150.07'   # Deterioro cognitivo
    ]
    
    for dni in df['pac_Numero_Documento'].unique():
        df_dni = df[df['pac_Numero_Documento'] == dni]
        cumple_todos = True
        
        # Verificar cada tamizaje
        for codigo in tamizajes_requeridos:
            tiene_tamizaje = not df_dni[
                (df_dni['Codigo_Item'] == codigo) & 
                (df_dni['Tipo_Diagnostico'] == 'D') &
                (df_dni['Valor_Lab'].isna() | df_dni['Valor_Lab'].isin(['', 'G', 'TPE', 'JUD']))
            ].empty
            
            if not tiene_tamizaje:
                cumple_todos = False
                break
        
        # Verificar consejería obligatoria
        if cumple_todos:
            tiene_consejeria = not df_dni[
                (df_dni['Codigo_Item'] == '99402.09') & 
                (df_dni['Tipo_Diagnostico'] == 'D')
            ].empty
            
            if tiene_consejeria:
                dni_cumple.add(dni)
    
    return df[df['pac_Numero_Documento'].isin(list(dni_cumple))]

def verificar_valoracion_clinica_lab(df):
    """Verificación de valoración clínica con laboratorio obligatorio"""
    dni_cumple = set()
    
    for dni in df['pac_Numero_Documento'].unique():
        df_dni = df[df['pac_Numero_Documento'] == dni]
        
        # Los 3 componentes son obligatorios
        tiene_valoracion = not df_dni[
            (df_dni['Codigo_Item'] == 'Z019') & 
            (df_dni['Tipo_Diagnostico'] == 'D') &
            (df_dni['Valor_Lab'] == 'DNT')
        ].empty
        
        tiene_laboratorio = not df_dni[
            (df_dni['Codigo_Item'] == 'Z017') & 
            (df_dni['Tipo_Diagnostico'] == 'D')
        ].empty
        
        tiene_consejeria = not df_dni[
            (df_dni['Codigo_Item'] == '99401.13') & 
            (df_dni['Tipo_Diagnostico'] == 'D')
        ].empty
        
        if tiene_valoracion and tiene_laboratorio and tiene_consejeria:
            dni_cumple.add(dni)
    
    return df[df['pac_Numero_Documento'].isin(list(dni_cumple))]

def verificar_paquete_integral_resumido(df):
    """Verificación rápida del paquete integral para el indicador resumen"""
    dni_con_paquete = set()
    
    for dni in df['pac_Numero_Documento'].unique():
        resultado = verificar_paquete_integral(df, dni)
        if resultado['completo']:
            dni_con_paquete.add(dni)
    
    return df[df['pac_Numero_Documento'].isin(list(dni_con_paquete))]

def calcular_estadisticas_indicador(df, indicador_key, poblacion_total=None):
    """Calcula estadísticas de cumplimiento para un indicador"""
    df_cumple = verificar_cumplimiento_indicador(df, indicador_key)
    
    if df_cumple is None:
        return None
    
    indicador = INDICADORES_ADULTO_MAYOR[indicador_key]
    
    # Contar DNIs únicos que cumplen
    dni_cumplen = df_cumple['pac_Numero_Documento'].nunique()
    
    # Calcular denominador
    if poblacion_total and 'denominador_especial' in indicador:
        if "%" in indicador['denominador_especial']:
            porcentaje = float(indicador['denominador_especial'].split('%')[0])
            
            # Casos especiales por fuente
            if "RENIEC" in indicador['denominador_especial']:
                denominador = poblacion_total  # 100% RENIEC
            elif "REUNIS" in indicador['denominador_especial']:
                denominador = int(poblacion_total * porcentaje / 100)
            else:
                # SIS u otros
                denominador = int(poblacion_total * porcentaje / 100)
        else:
            denominador = poblacion_total * 0.4  # 40% por defecto
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
    
    for componente in PAQUETE_INTEGRAL_ADULTO_MAYOR['componentes_minimos']:
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