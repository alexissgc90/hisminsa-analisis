# 🏥 Generador JSON Simple - HISMINSA

Versión simplificada y práctica para generar JSON de indicadores rápidamente.

## 🚀 Características

- **Solo lo esencial**: DNI + Fecha de nacimiento
- **Detección automática** del curso de vida
- **3 modos de generación**:
  - 📦 Paquete Completo (todos los indicadores)
  - 📋 Indicadores Individuales (selección manual)
  - ⚠️ Factores de Riesgo (casos patológicos)
- **Valores LAB por defecto** (normales/no patológicos)
- **Optimización automática** de códigos

## 📝 Uso Rápido

### 1. Iniciar la aplicación
```bash
# Doble clic en:
ejecutar_generador_simple.bat

# O desde terminal:
streamlit run generador_json_simple.py
```

### 2. Ingresar datos básicos
- **DNI**: 8 dígitos
- **Fecha de nacimiento**: DD/MM/AAAA (ej: 15/06/1980)
- **Datos opcionales**: Nombre completo y sexo (expandir para ver)

### 3. Seleccionar modo de generación

#### Opción A: Paquete Completo
- Genera todos los códigos del paquete integral
- Incluye plan de atención (opcional)
- Un clic y listo

#### Opción B: Indicadores Individuales
- Selecciona solo los indicadores que necesitas
- Ideal para completar faltantes
- Control total sobre qué generar

#### Opción C: Factores de Riesgo
- Para casos con patologías
- Agrega códigos CIE-10 de factores
- Ajusta valores LAB (presión alterada, riesgo nutricional)
- Incluye laboratorio para adultos 30-39 con factores

### 4. Descargar JSON
- Click en "⬇️ Descargar JSON"
- Archivo listo para importar en HIS-MINSA

## 🎯 Valores LAB Automáticos

Por defecto genera valores **normales/no patológicos**:
- `Z019` → `DNT` (Diagnóstico No Transmisible)
- `99199.22` → `N` (Presión Normal)
- `99209.02` → `N` (Nutricional Normal)
- `99209.04` → `RSM` (Nutricional - Riesgo Salud Metabólica por defecto)
- `99387/99215.03` → `AS` (VACAM Autosuficiente)
- `99801` → `1` (Plan Elaborado) / `TA` (Plan Ejecutado)

### Agudeza Visual (todos los cursos de vida):
- `Z010` → `N` (Examen de ojos y visión)
- `99173` → `20` (Determinación agudeza visual)
- `99401.16` → `` (Consejería salud ocular)

## ⚡ Reglas Automáticas

### Por Edad:
- **Jóvenes (18-29)**: Sin laboratorio obligatorio
- **Adultos (30-39)**: Laboratorio solo si hay factores de riesgo
- **Adultos (40-59)**: Laboratorio siempre incluido
- **Adultos Mayores (60+)**: Todos los tamizajes

### Optimizaciones:
- Elimina códigos duplicados
- Agrupa consejerías de salud mental (una sola 99402.09)
- Maneja secuencias especiales automáticamente

## 💡 Ejemplos de Uso

### Caso 1: Paciente sano sin factores
1. Ingresa DNI y fecha
2. Click en "Paquete Completo"
3. Descargar JSON

### Caso 2: Completar indicadores faltantes
1. Ingresa DNI y fecha
2. Tab "Indicadores Individuales"
3. Marca solo los que faltan
4. Descargar JSON

### Caso 3: Paciente con obesidad e hipertensión
1. Ingresa DNI y fecha
2. Tab "Factores de Riesgo"
3. Marca: Obesidad + Hipertensión
4. Marca: Presión alterada (A)
5. Descargar JSON

## 🔧 Configuración

En la barra lateral:
- **Día HIS**: Día del registro (1-31)
- **Fecha de atención**: Fecha real de la atención
- **Tipo**: registro_nuevo / correccion_paquete / actualizacion_indicador

## 📌 Notas Importantes

1. **Solo genera códigos CIE y valores LAB** (lo que lee HIS-MINSA)
2. **Valores por defecto son normales** (no patológicos)
3. **Para casos patológicos**, usar tab "Factores de Riesgo"
4. **Laboratorio en adultos 30-39** solo si hay factores de riesgo
5. **Formato JSON idéntico** al esperado por tu aplicación de automatización
6. **Agudeza visual incluida** automáticamente para todos los cursos de vida

---

*Versión simplificada para uso rápido y práctico*