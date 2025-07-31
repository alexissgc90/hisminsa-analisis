# 🏥 Generador JSON HISMINSA

Sistema inteligente para generar archivos JSON de indicadores de salud compatibles con HIS-MINSA.

## 🚀 Características Principales

### 1. **Registro Inteligente de Pacientes**
- Cálculo automático de IMC y clasificación nutricional
- Detección automática de factores de riesgo
- Determinación del curso de vida según edad
- Validación de datos en tiempo real

### 2. **Evaluación Antropométrica Avanzada**
- Cálculo de IMC con clasificación OMS
- Evaluación de perímetro abdominal
- Clasificación de presión arterial
- Determinación automática de valores LAB

### 3. **Gestión de Factores de Riesgo**
- Detección automática por IMC
- Selección manual de factores adicionales
- Códigos CIE-10 apropiados
- Integración con indicadores

### 4. **Generación Flexible de Indicadores**
- **Modo Paquete Completo**: Todos los códigos del paquete integral
- **Modo Individual**: Selección específica de indicadores
- **Modo Personalizado**: Control total sobre códigos

### 5. **Reglas Inteligentes por Edad**
- Jóvenes (18-29): Sin laboratorio obligatorio
- Adultos (30-39): Laboratorio condicional
- Adultos (40-59): Laboratorio obligatorio
- Adultos Mayores (60+): Todos los tamizajes

## 📋 Cómo Usar

### Paso 1: Iniciar la Aplicación
```bash
# Windows
Doble clic en ejecutar_generador.bat

# O desde terminal
streamlit run generador_json_hisminsa.py
```

### Paso 2: Registrar Paciente

1. **Datos Básicos**
   - DNI (8 dígitos)
   - Nombres y apellidos
   - Fecha de nacimiento (dos opciones):
     - 📅 Calendario: Selector visual (desde 1900)
     - ⌨️ Escribir fecha: Formato DD/MM/AAAA (ej: 27/07/1930)
   - Sexo
   - Fecha de atención

2. **Antropometría**
   - Peso y talla → Calcula IMC automáticamente
   - Perímetro abdominal
   - Presión arterial
   - Los valores LAB se asignan automáticamente

3. **Factores de Riesgo**
   - Sobrepeso/obesidad (detectado por IMC)
   - Alcohol, tabaco, drogas
   - Otros factores

4. **Indicadores**
   - Seleccionar modo (paquete/individual/personalizado)
   - Marcar indicadores necesarios
   - Incluir plan de atención si corresponde

### Paso 3: Generar JSON

1. Ir a "💾 Generar JSON"
2. Configurar día HIS y tipo de corrección
3. Revisar vista previa
4. Descargar archivo JSON

## 🔧 Características Especiales

### Valores LAB Automáticos
- **Z019**: DNT (Diagnóstico No Transmisible)
- **99199.22**: N/A según presión arterial
- **99209.04**: RSM/RSA según IMC y PAB
- **99387/99215.03**: AS (Autosuficiente)
- **99801**: 1 (Elaborado) / TA (Ejecutado)

### Optimizaciones Automáticas
- Elimina códigos duplicados
- Agrupa consejerías de salud mental (una sola 99402.09)
- Maneja secuencias especiales (VIH, VACAM)
- Aplica reglas por edad

### Validaciones
- Coherencia de diagnósticos
- Secuencias requeridas
- Valores LAB apropiados
- Factores de riesgo

## 📊 Estructura del JSON Generado

```json
{
  "fecha_exportacion": "2024-01-15T10:30:00",
  "dia_his": "15",
  "fecha_atencion": "2024-01-15",
  "tipo_correccion": "registro_nuevo",
  "total_pacientes": 1,
  "pacientes": [
    {
      "dni": "12345678",
      "nombre": "APELLIDO APELLIDO NOMBRES",
      "edad": "35",
      "sexo": "M",
      "diagnosticos": [
        {
          "codigo": "Z019",
          "descripcion": "Z019 - Valoración clínica",
          "tipo": "D",
          "lab": "DNT"
        }
      ]
    }
  ]
}
```

## 🎯 Casos de Uso

### 1. Paquete Integral Nuevo
- Paciente sin atenciones previas
- Generar todos los códigos del paquete
- Incluir plan elaborado y ejecutado

### 2. Completar Indicadores Faltantes
- Paciente con atención parcial
- Seleccionar solo indicadores pendientes
- No duplicar códigos existentes

### 3. Corrección de Valores LAB
- Modificar valores LAB incorrectos
- Usar modo "Todos los códigos"
- Ajustar valores según evaluación

### 4. Factores de Riesgo
- Registrar nuevos factores detectados
- Generar códigos CIE-10 apropiados
- Incluir en el paquete integral

## ⚙️ Configuración Avanzada

### Personalizar Indicadores
1. Editar archivos `indicadores_*.py`
2. Agregar/modificar reglas
3. Reiniciar la aplicación

### Agregar Nuevos Factores
1. Editar `utils_generador.py`
2. Agregar en `CODIGOS_FACTORES_RIESGO_DETALLADOS`
3. Actualizar mapeos

## 🐛 Solución de Problemas

### "No se muestran indicadores"
- Verificar que se completaron los datos básicos
- Confirmar que la edad está en rango válido
- Asegurarse de ingresar fecha de nacimiento correcta

### "Valores LAB incorrectos"
- Revisar antropometría ingresada
- Verificar clasificación de IMC
- Comprobar presión arterial

### "JSON no se genera"
- Verificar que hay pacientes registrados
- Revisar que se seleccionaron indicadores
- Comprobar validaciones

## 📝 Notas Importantes

1. **Siempre verificar** el JSON antes de importar al HIS
2. **Guardar respaldo** de JSONs generados
3. **Validar coherencia** de diagnósticos
4. **Respetar secuencias** (VIH, VACAM, etc.)

## 🤝 Soporte

Para dudas o mejoras, revisar:
- Documentación de indicadores
- Archivos de configuración
- Logs de la aplicación

---

*Desarrollado para optimizar el registro de indicadores en HIS-MINSA*