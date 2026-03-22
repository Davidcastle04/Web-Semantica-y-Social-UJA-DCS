 # Poblador de Ontologías con la dependecia de RDFlib

**Asignatura:** Web Semántica y Social  
**Universidad:** Universidad de Jaén  
**Autor:** David Castillo Serrano  

Aplicación Python que lee un fichero CSV y genera automáticamente un fichero
RDF/XML con los individuos de la ontología, listo para abrirse en Protégé.

---

## Estructura del repositorio

```
rdflib_proyecto/
├── poblar_ontologia.py     # Script principal
├── datos_ontologia.csv     # Datos de ejemplo (comidas e ingredientes)
├── requirements.txt        # Dependencias Python
└── README.md               # Este fichero
```

---

## Requisitos previos

- Python **3.8 o superior**
- pip (gestor de paquetes de Python)
- Git (para clonar el repositorio)

Comprueba tu versión de Python con:

```bash
python3 --version
```

---

## Instalación del entorno en Linux

### 1. Clonar el repositorio

```bash
git clone https://github.com/Davidcastle04/Web-Semantica-y-Social-UJA-DCS
cd Web-Semantica-y-Social-UJA-DCS
```

### 2. Crear el entorno virtual (.venv)

El entorno virtual aisla las dependencias del proyecto del resto del sistema.
Así no afecta a otros proyectos Python que tengas instalados.

```bash
python3 -m venv .venv
```

Esto crea una carpeta oculta `.venv/` dentro del proyecto.

### 3. Activar el entorno virtual

```bash
source .venv/bin/activate
```

Sabrás que está activo porque el prompt del terminal cambia y muestra `(.venv)`:

```
(.venv) david@MacBook-Air-de-David Web-Semantica-y-Social-UJA-DCS %
```

> **Importante:** Debemos activar el entorno virtual cada vez que abramos un
> terminal nuevo para trabajar en este proyecto.

### 4. Instalar las dependencias

Con el entorno activado, instala las dependencias del fichero `requirements.txt`:

```bash
pip install -r requirements.txt
```

Esto instalará únicamente **RDFlib** y las dependencias que necesita.

Para verificar que se instaló correctamente:

```bash
python3 -c "import rdflib; print(rdflib.__version__)"
```

### 5. Desactivar el entorno virtual

```bash
deactivate
# O bien cerramos el terminal (No es obligatorio cerrarlo , si queda abierto no pasaria nada)
```

---

## Uso del script

### Ejecución básica (usa los ficheros por defecto)

```bash
python3 poblar_ontologia.py
```

Esto lee el archivo que haya en la raiz datos.csv y nos generara un archivo llamado `ontologia_poblada.rdf`.

### Opciones avanzadas

```bash
# Especificar un CSV y un fichero de salida distintos
python3 poblar_ontologia.py --csv mis_datos.csv --salida mi_ontologia.rdf

# Cambiar el IRI base de la ontología
python3 poblar_ontologia.py --iri http://mi.dominio.org/miontologia

# Ver la ayuda completa
python3 poblar_ontologia.py --help
```

### Salida esperada en consola

```
=======================================================
  POBLADOR DE ONTOLOGÍAS CON RDFlib
  Web Semántica y Social — Univ. de Jaén
=======================================================

[INFO] Ontología inicializada: http://www.semanticweb.org/david/...
[INFO] Leyendo CSV: datos_ontologia.csv
  [+] Comida: Tortilla_Francesa (Plato)
  [+] Comida: Ensalada_Verde (Plato)
  ...
[INFO] Cargadas 8 comidas y 11 ingredientes.
[INFO] Total triples en el grafo: 143

=======================================================
  RESUMEN DE INDIVIDUOS EN EL GRAFO
=======================================================
  Ingrediente                    11 individuos
  Plato                          7 individuos
  Bebida                         1 individuos
=======================================================

[OK] Ontología guardada en: /ruta/al/proyecto/ontologia_poblada.rdf
     Triples totales: 143

[INFO] Abre el fichero generado en Protégé:
       File → Open → ontologia_poblada.rdf
```

---

## Abrir el resultado en Protégé

1. Abre Protégé
2. `File → Open`
3. Selecciona el fichero `ontologia_poblada.rdf`
4. Ve a la pestaña **Individuals** para ver los individuos cargados
5. Para lanzar el razonador: `Reasoner → HermiT → Start reasoner`

---

## Formato del CSV

El fichero CSV tiene las siguientes columnas:

| Columna | Tipo | Descripción |
|---|---|---|
| `tipo` | string | `comida` o `ingrediente` |
| `nombre` | string | Nombre del individuo (sin espacios) |
| `clase` | string | Clase OWL (`Plato`, `Bebida`, `Ingrediente`...) |
| `tiempo_preparacion` | int | Minutos (solo comidas) |
| `kilocalorias` | int | Kilocalorías (solo comidas) |
| `precio` | float | Precio en euros |
| `sabor` | string | `dulce` o `salado` |
| `para_cuantas_personas` | int | Número de personas (solo comidas) |
| `requiereRefrigeracion` | boolean | `true` o `false` |
| `pertenece_a_piramide` | string | Grupo nutricional (`Verduras`, `Proteinas`...) |
| `necesita` | string | Método de cocción (`Frito`, `Crudo`...) |
| `procedente_de` | string | Lugar de origen |
| `contiene` | string | Ingredientes separados por `\|` (solo comidas) |
| `es_tipo` | string | Tipo de comida (`Desayuno`, `Almuerzo`...) |

Las celdas vacías se ignoran automáticamente.

### Ejemplo de fila

```csv
comida,Ensalada_Verde,Plato,10,60,3.00,salado,2,true,Verduras,Crudo,Espana,Lechuga|Pepino|Tomate,Almuerzo
```

---

## Adaptar el script a otra ontología

El script está diseñado para ser genérico. Para usarlo con una ontología
diferente solo necesitas:

1. **Cambiar el IRI base** en la constante `IRI_BASE` del fichero Python,
   o pasarlo por argumento con `--iri`.

2. **Adaptar el CSV** con las columnas que correspondan a tus propiedades.

3. **Modificar los métodos** `_procesar_comida` y `_procesar_ingrediente`
   (o añadir nuevos) para mapear las columnas del CSV a tus propiedades OWL.

---

## Dependencias

```
rdflib>=6.0.0
```

Instaladas automáticamente con `pip install -r requirements.txt`.

---

