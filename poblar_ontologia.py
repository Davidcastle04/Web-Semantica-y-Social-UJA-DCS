"""
poblar_ontologia.py
====================
Aplicación para poblar automáticamente una ontología OWL a partir de un
fichero CSV usando la biblioteca RDFlib.

Asignatura : Web Semántica y Social
Universidad: Universidad de Jaén
Autor      : David Castillo Serrano
Versión    : 1.0

Descripción
-----------
El script lee un fichero CSV con datos de comidas e ingredientes y genera
un fichero RDF/XML listo para abrirse en Protégé. Cada fila del CSV se
convierte en un individuo (NamedIndividual) de la ontología, con todas sus
propiedades de datos (DataProperty) y de objeto (ObjectProperty).

Estructura del CSV
------------------
Columnas esperadas:
    tipo                  - 'comida' o 'ingrediente'
    nombre                - nombre del individuo (sin espacios)
    clase                 - clase OWL (Plato, Bebida, Ingrediente...)
    tiempo_preparacion    - int (minutos, solo comidas)
    kilocalorias          - int (solo comidas)
    precio                - float (euros)
    sabor                 - string ('dulce' o 'salado')
    para_cuantas_personas - int (solo comidas)
    requiereRefrigeracion - boolean ('true'/'false')
    pertenece_a_piramide  - nombre del grupo nutricional
    necesita              - método de cocción
    procedente_de         - lugar de origen
    contiene              - ingredientes separados por '|' (solo comidas)
    es_tipo               - tipo de comida (Desayuno, Almuerzo, Cena...)

Uso
---
    python poblar_ontologia.py
    python poblar_ontologia.py --csv mi_fichero.csv --salida mi_ontologia.rdf
"""

import csv
import argparse
from pathlib import Path
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL, XSD


# ---------------------------------------------------------------------------
# CONSTANTES Y NAMESPACES
# ---------------------------------------------------------------------------

# IRI base de la ontología. 
IRI_BASE = "http://www.semanticweb.org/admin/ontologies/2026/2/untitled-ontology-7"

# Ficheros por defecto
CSV_POR_DEFECTO    = "datos.csv"
SALIDA_POR_DEFECTO = "ontologia_poblada.rdf"


# ---------------------------------------------------------------------------
# CLASE PRINCIPAL
# ---------------------------------------------------------------------------

class PobladorOntologia:
    """
    Clase principal que gestiona la carga del CSV y la generación del RDF.

    Atributos
    ---------
    grafo : rdflib.Graph
        Grafo RDF que se irá llenando con los triples.
    iri_base : str
        IRI base de la ontología.
    ns : rdflib.Namespace
        Namespace de la ontología (IRI_BASE + '#').

    Ejemplo de uso
    --------------
    >>> poblador = PobladorOntologia()
    >>> poblador.cargar_csv("datos_ontologia.csv")
    >>> poblador.guardar("ontologia_poblada.rdf")
    """

    def __init__(self, iri_base=IRI_BASE):
        """
        Inicializa el grafo RDF y declara los prefijos más comunes.

        Parámetros
        ----------
        iri_base : str
            IRI base de la ontología.
        """
        self.iri_base = iri_base
        self.ns = Namespace(iri_base + "#")
        self.grafo = Graph()

        # Registrar prefijos para que el XML sea legible
        self.grafo.bind("owl",     OWL)
        self.grafo.bind("rdf",     RDF)
        self.grafo.bind("rdfs",    RDFS)
        self.grafo.bind("xsd",     XSD)
        self.grafo.bind("comidas", self.ns)

        # Declarar la ontología
        ontologia_uri = URIRef(iri_base)
        self.grafo.add((ontologia_uri, RDF.type, OWL.Ontology))
        self.grafo.add((
            ontologia_uri,
            RDFS.comment,
            Literal("Ontología poblada automáticamente con RDFlib desde CSV.",
                    lang="es")
        ))

        print(f"[INFO] Ontología inicializada: {iri_base}")

    # ------------------------------------------------------------------
    # MÉTODOS PRIVADOS DE UTILIDAD
    # ------------------------------------------------------------------

    def _uri(self, nombre):
        """
        Devuelve la URI completa de un recurso dado su nombre local.

        Parámetros
        ----------
        nombre : str
            Nombre local del recurso (ej. 'Gazpacho', 'Plato').

        Retorna
        -------
        URIRef
            URI completa del recurso.
        """
        nombre_limpio = nombre.strip().replace(" ", "_")
        return self.ns[nombre_limpio]

    def _anadir_individual(self, nombre, clase):
        """
        Declara un individuo NamedIndividual con su clase OWL.

        Parámetros
        ----------
        nombre : str
            Nombre local del individuo.
        clase : str
            Nombre local de la clase OWL a la que pertenece.

        Retorna
        -------
        URIRef
            URI del individuo creado.
        """
        uri       = self._uri(nombre)
        clase_uri = self._uri(clase)
        self.grafo.add((uri, RDF.type,   OWL.NamedIndividual))
        self.grafo.add((uri, RDF.type,   clase_uri))
        self.grafo.add((uri, RDFS.label, Literal(nombre, lang="es")))
        return uri

    def _anadir_data_property(self, sujeto, propiedad, valor, tipo_xsd=XSD.string):
        """
        Añade un triple DataProperty si el valor no está vacío.

        Parámetros
        ----------
        sujeto : URIRef
            URI del individuo al que se añade la propiedad.
        propiedad : str
            Nombre local de la DataProperty.
        valor : str
            Valor como cadena de texto (se convierte al tipo indicado).
        tipo_xsd : URIRef
            Tipo XSD del literal. Por defecto XSD.string.
        """
        if not valor or valor.strip() == "":
            return
        prop_uri = self._uri(propiedad)
        try:
            self.grafo.add((sujeto, prop_uri, Literal(valor.strip(), datatype=tipo_xsd)))
        except Exception as e:
            print(f"  [AVISO] No se pudo añadir {propiedad}='{valor}': {e}")

    def _anadir_object_property(self, sujeto, propiedad, objeto_nombre):
        """
        Añade un triple ObjectProperty si el objeto no está vacío.
        Si el objeto destino no existe aún en el grafo, se crea minimamente.

        Parámetros
        ----------
        sujeto : URIRef
            URI del individuo origen.
        propiedad : str
            Nombre local de la ObjectProperty.
        objeto_nombre : str
            Nombre local del individuo destino.
        """
        if not objeto_nombre or objeto_nombre.strip() == "":
            return
        prop_uri   = self._uri(propiedad)
        objeto_uri = self._uri(objeto_nombre)

        # Si el objeto destino no existe, lo creamos mínimamente
        if (objeto_uri, RDF.type, OWL.NamedIndividual) not in self.grafo:
            self.grafo.add((objeto_uri, RDF.type, OWL.NamedIndividual))

        self.grafo.add((sujeto, prop_uri, objeto_uri))

    # ------------------------------------------------------------------
    # PROCESADO DE FILAS
    # ------------------------------------------------------------------

    def _procesar_comida(self, fila):
        """
        Convierte una fila de tipo 'comida' en un individuo OWL con todas
        sus DataProperties y ObjectProperties.

        Parámetros
        ----------
        fila : dict
            Diccionario con las columnas del CSV para esa fila.
        """
        nombre = fila["nombre"].strip()
        clase  = fila["clase"].strip()

        print(f"  [+] Comida: {nombre} ({clase})")
        uri = self._anadir_individual(nombre, clase)

        # DataProperties numéricas y booleanas
        self._anadir_data_property(uri, "tiempo_preparacion",
                                   fila.get("tiempo_preparacion",""), XSD.int)
        self._anadir_data_property(uri, "kilocalorias",
                                   fila.get("kilocalorias",""), XSD.int)
        self._anadir_data_property(uri, "precio",
                                   fila.get("precio",""), XSD.float)
        self._anadir_data_property(uri, "sabor",
                                   fila.get("sabor",""), XSD.string)
        self._anadir_data_property(uri, "para_cuantas_personas",
                                   fila.get("para_cuantas_personas",""), XSD.int)
        self._anadir_data_property(uri, "requiereRefrigeracion",
                                   fila.get("requiereRefrigeracion",""), XSD.boolean)

        # ObjectProperties simples (apuntan a un único individuo)
        self._anadir_object_property(uri, "pertenece_a_piramide",
                                     fila.get("pertenece_a_piramide",""))
        self._anadir_object_property(uri, "necesita",
                                     fila.get("necesita",""))
        self._anadir_object_property(uri, "procedente_de",
                                     fila.get("procedente_de",""))
        self._anadir_object_property(uri, "es_tipo",
                                     fila.get("es_tipo",""))

        # ObjectProperty múltiple: contiene (ingredientes separados por '|')
        ingredientes = fila.get("contiene", "")
        if ingredientes.strip():
            for ing in ingredientes.split("|"):
                ing = ing.strip()
                if ing:
                    self._anadir_object_property(uri, "contiene", ing)

    def _procesar_ingrediente(self, fila):
        """
        Convierte una fila de tipo 'ingrediente' en un individuo OWL con
        sus propiedades básicas.

        Parámetros
        ----------
        fila : dict
            Diccionario con las columnas del CSV para esa fila.
        """
        nombre = fila["nombre"].strip()
        clase  = fila["clase"].strip()

        print(f"  [+] Ingrediente: {nombre}")
        uri = self._anadir_individual(nombre, clase)

        self._anadir_data_property(uri, "precio",
                                   fila.get("precio",""), XSD.float)
        self._anadir_data_property(uri, "requiereRefrigeracion",
                                   fila.get("requiereRefrigeracion",""), XSD.boolean)
        self._anadir_object_property(uri, "pertenece_a_piramide",
                                     fila.get("pertenece_a_piramide",""))
        self._anadir_object_property(uri, "procedente_de",
                                     fila.get("procedente_de",""))

    # ------------------------------------------------------------------
    # MÉTODOS PÚBLICOS
    # ------------------------------------------------------------------

    def cargar_csv(self, ruta_csv):
        """
        Lee el CSV fila a fila y llama al método adecuado según el tipo
        de cada fila ('comida' o 'ingrediente').

        Parámetros
        ----------
        ruta_csv : str
            Ruta al fichero CSV con los datos de la ontología.

        Excepciones
        -----------
        FileNotFoundError
            Si el fichero CSV no existe en la ruta indicada.
        """
        ruta = Path(ruta_csv)
        if not ruta.exists():
            raise FileNotFoundError(f"No se encontró el CSV: {ruta_csv}")

        print(f"[INFO] Leyendo CSV: {ruta_csv}")
        comidas_cargadas      = 0
        ingredientes_cargados = 0

        with open(ruta, newline="", encoding="utf-8") as f:
            lector = csv.DictReader(f)
            for num_fila, fila in enumerate(lector, start=2):
                tipo = fila.get("tipo", "").strip().lower()
                if tipo == "comida":
                    self._procesar_comida(fila)
                    comidas_cargadas += 1
                elif tipo == "ingrediente":
                    self._procesar_ingrediente(fila)
                    ingredientes_cargados += 1
                else:
                    print(f"  [AVISO] Fila {num_fila}: tipo '{tipo}' desconocido, se omite.")

        print(f"[INFO] Cargadas {comidas_cargadas} comidas y "
              f"{ingredientes_cargados} ingredientes.")
        print(f"[INFO] Total triples en el grafo: {len(self.grafo)}")

    def guardar(self, ruta_salida=SALIDA_POR_DEFECTO):
        """
        Serializa el grafo RDF en formato XML y lo guarda en disco.

        El fichero resultante se puede abrir directamente en Protégé
        con File → Open → seleccionar el .rdf generado.

        Parámetros
        ----------
        ruta_salida : str
            Ruta del fichero de salida. Por defecto 'ontologia_poblada.rdf'.
        """
        ruta = Path(ruta_salida)
        self.grafo.serialize(destination=str(ruta), format="xml")
        print(f"\n[OK] Ontología guardada en: {ruta.resolve()}")
        print(f"     Triples totales: {len(self.grafo)}")

    def mostrar_resumen(self):
        """
        Imprime en consola un resumen de los individuos cargados,
        agrupados por clase OWL, usando una consulta SPARQL interna.

        Útil para verificar que la carga fue correcta antes de
        abrir el fichero en Protégé.
        """
        print("\n" + "="*55)
        print("  RESUMEN DE INDIVIDUOS EN EL GRAFO")
        print("="*55)

        consulta = """
        PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl:  <http://www.w3.org/2002/07/owl#>

        SELECT ?clase (COUNT(?ind) AS ?total)
        WHERE {
            ?ind rdf:type owl:NamedIndividual .
            ?ind rdf:type ?clase .
            FILTER (?clase != owl:NamedIndividual)
        }
        GROUP BY ?clase
        ORDER BY DESC(?total)
        """
        resultados = list(self.grafo.query(consulta))
        if not resultados:
            print("  (Sin resultados)")
        for fila in resultados:
            clase = str(fila.clase).split("#")[-1]
            print(f"  {clase:<30} {fila.total} individuos")
        print("="*55)

        print("\n  COMIDAS CARGADAS (nombre | kcal | tipo):")
        print("  " + "-"*50)
        consulta2 = f"""
        PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl:     <http://www.w3.org/2002/07/owl#>
        PREFIX comidas: <{self.iri_base}#>

        SELECT ?nombre ?kcal ?tipo
        WHERE {{
            ?ind rdf:type owl:NamedIndividual .
            ?ind comidas:kilocalorias ?kcal .
            OPTIONAL {{
                ?ind comidas:es_tipo ?tipoUri .
                BIND(STRAFTER(STR(?tipoUri), "#") AS ?tipo)
            }}
            BIND(STRAFTER(STR(?ind), "#") AS ?nombre)
        }}
        ORDER BY ?nombre
        """
        for fila in self.grafo.query(consulta2):
            tipo = str(fila.tipo) if fila.tipo else "—"
            print(f"  {str(fila.nombre):<30} {str(fila.kcal):<6} kcal  {tipo}")


# ---------------------------------------------------------------------------
# ARGUMENTOS DE LÍNEA DE COMANDOS
# ---------------------------------------------------------------------------

def parsear_argumentos():
    """
    Define y parsea los argumentos de línea de comandos del script.

    Retorna
    -------
    argparse.Namespace
        Objeto con los atributos: csv, salida, iri.
    """
    parser = argparse.ArgumentParser(
        prog="poblar_ontologia",
        description=(
            "Pobla una ontología OWL/RDF a partir de un fichero CSV "
            "usando RDFlib. Genera un fichero .rdf listo para Protégé."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python poblar_ontologia.py
  python poblar_ontologia.py --csv mis_datos.csv --salida mi_onto.rdf
  python poblar_ontologia.py --iri http://mi.dominio.org/miontologia
        """
    )
    parser.add_argument(
        "--csv",
        default=CSV_POR_DEFECTO,
        help=f"Ruta al fichero CSV (por defecto: {CSV_POR_DEFECTO})"
    )
    parser.add_argument(
        "--salida",
        default=SALIDA_POR_DEFECTO,
        help=f"Ruta del .rdf de salida (por defecto: {SALIDA_POR_DEFECTO})"
    )
    parser.add_argument(
        "--iri",
        default=IRI_BASE,
        help=f"IRI base de la ontología (por defecto: {IRI_BASE})"
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# PUNTO DE ENTRADA
# ---------------------------------------------------------------------------

def main():
    """
    Función principal del script.

    Flujo de ejecución:
        1. Parsear argumentos de línea de comandos.
        2. Crear instancia de PobladorOntologia.
        3. Cargar los datos desde el CSV.
        4. Mostrar resumen SPARQL en consola.
        5. Serializar y guardar el grafo como RDF/XML.
    """
    args = parsear_argumentos()

    print("="*55)
    print("  POBLADOR DE ONTOLOGÍAS CON RDFlib")
    print("  Web Semántica y Social — Univ. de Jaén")
    print("="*55 + "\n")

    poblador = PobladorOntologia(iri_base=args.iri)

    try:
        poblador.cargar_csv(args.csv)
    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}")
        print("  Comprueba que el fichero CSV existe y la ruta es correcta.")
        return

    poblador.mostrar_resumen()
    poblador.guardar(args.salida)

    print("\n[INFO] Abre el fichero generado en Protégé:")
    print(f"       File → Open → {args.salida}")
    print("[INFO] Lanza el razonador: Reasoner → HermiT → Start reasoner\n")


if __name__ == "__main__":
    main()
