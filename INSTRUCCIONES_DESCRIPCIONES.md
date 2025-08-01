# 📋 Configuración del archivo de descripciones

## Archivo requerido: `codigos_descripcion.xlsx`

Para que la aplicación muestre las descripciones completas de códigos CIE-10, establecimientos, UPS y etnias, necesitas crear un archivo Excel con la siguiente estructura:

### Estructura del archivo Excel

El archivo debe tener 4 hojas:

#### 1. Hoja "CIE10"
| Columna A (Código) | Columna B (Descripción) |
|-------------------|-------------------------|
| I10X | Hipertensión esencial (primaria) |
| J039 | Amigdalitis aguda, no especificada |
| K802 | Cirrosis alcohólica del hígado |
| Z001 | Examen de salud rutinario del niño |
| ... | ... |

#### 2. Hoja "Establecimientos"
| Columna A (ID) | Columna B (Nombre) |
|----------------|-------------------|
| 4768 | C.S. Miracosta |
| 4769 | P.S. Andanga |
| 4770 | P.S. Piedra Blanca |
| 4771 | P.S. Sangana |
| 4777 | C.S. San Antonio |
| 4778 | P.S. Tocmoche |
| 6660 | C.S. Incahuasi |
| 6798 | P.S. Moyán |
| 7095 | P.S. Uñican |
| ... | ... |

#### 3. Hoja "UPS"
| Columna A (Código) | Columna B (Descripción) |
|-------------------|-------------------------|
| 301202 | Atención Integral del Niño |
| 301203 | Atención Integral del Adolescente |
| 301204 | Atención Integral del Adulto |
| 302101 | Atención Odontológica Básica |
| 302303 | Atención Integral del Adulto Mayor |
| ... | ... |

#### 4. Hoja "Etnias"
| Columna A (ID) | Columna B (Descripción) |
|----------------|-------------------------|
| 40 | Mestizo |
| 58 | Otros |
| 1 | Quechua |
| 2 | Aymara |
| 3 | Asháninka |
| ... | ... |

## Instalación de dependencias

Para leer archivos Excel, necesitas instalar openpyxl:

```cmd
pip install openpyxl
```

## ¿Qué pasa si no tienes el archivo?

Si no existe el archivo `codigos_descripcion.xlsx`:
- Los códigos CIE-10 se mostrarán sin descripción
- Los establecimientos mostrarán solo el ID
- Los códigos UPS se mostrarán sin descripción
- Las etnias usarán un diccionario básico (40=Mestizo, 58=Otros)

## Cómo crear el archivo

1. Abre Excel o Google Sheets
2. Crea las 4 hojas con los nombres exactos: CIE10, Establecimientos, UPS, Etnias
3. En cada hoja, coloca los códigos en la columna A y las descripciones en la columna B
4. Guarda como `codigos_descripcion.xlsx` en la misma carpeta que los scripts

## Beneficios

Con el archivo de descripciones:
- **CIE10_Completo**: "I10X - Hipertensión esencial (primaria)"
- **Establecimiento_Completo**: "4768 - C.S. Miracosta"
- **UPS_Completo**: "301204 - Atención Integral del Adulto"
- **Etnia_Desc**: "Mestizo" (en lugar de solo el número 40)

Sin el archivo:
- **CIE10_Completo**: "I10X"
- **Establecimiento_Completo**: "4768"
- **UPS_Completo**: "301204"
- **Etnia_Desc**: "No especificado"