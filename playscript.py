
import sys
import argparse
from pathlib import Path
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Definiciones léxicas
# ---------------------------------------------------------------------------
RESERVADAS = {
    "CANCION", "PLAYLIST", "AGREGAR", "QUITAR", "A", "DE", "REPRODUCIR",
    "PAUSAR", "VOLUMEN", "MOSTRAR", "SI", "ENTONCES", "FIN",
}
INICIOS_INSTRUCCION = {
    "CANCION", "PLAYLIST", "AGREGAR", "QUITAR", "REPRODUCIR", "PAUSAR",
    "VOLUMEN", "MOSTRAR", "SI",
}


@dataclass
class Token:
    tipo: str      # CANCION, ..., ID, NUMERO, CADENA, OP_REL, PUNTO_Y_COMA, EOF
    lexema: str
    linea: int
    col: int


@dataclass
class Error:
    fase: str
    mensaje: str
    linea: int
    col: int = 0

    def __str__(self):
        ubic = f"línea {self.linea}" + (f", col {self.col}" if self.col else "")
        return f"[Error {self.fase}] {ubic}: {self.mensaje}"


def _letra(c):  return ("a" <= c <= "z") or ("A" <= c <= "Z")
def _digito(c): return "0" <= c <= "9"
def _alnum_(c): return _letra(c) or _digito(c) or c == "_"


def _es_identificador(p):
    """[a-z][a-z0-9_]*"""
    return ("a" <= p[0] <= "z") and all(("a" <= c <= "z") or _digito(c) or c == "_" for c in p)


# ---------------------------------------------------------------------------
# 1. ANÁLISIS LÉXICO
# ---------------------------------------------------------------------------
def analizar_lexico(src):
    tokens, errores = [], []
    i, n, linea, ini = 0, len(src), 1, 0

    def err(msg, col):
        errores.append(Error("léxico", msg, linea, col))

    while i < n:
        c = src[i]
        col = i - ini + 1


import sys
import argparse
from pathlib import Path
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Definiciones léxicas
# ---------------------------------------------------------------------------
RESERVADAS = {
    "CANCION", "PLAYLIST", "AGREGAR", "QUITAR", "A", "DE", "REPRODUCIR",
    "PAUSAR", "VOLUMEN", "MOSTRAR", "SI", "ENTONCES", "FIN",
}
INICIOS_INSTRUCCION = {
    "CANCION", "PLAYLIST", "AGREGAR", "QUITAR", "REPRODUCIR", "PAUSAR",
    "VOLUMEN", "MOSTRAR", "SI",
}


@dataclass
class Token:
    tipo: str      # CANCION, ..., ID, NUMERO, CADENA, OP_REL, PUNTO_Y_COMA, EOF
    lexema: str
    linea: int
    col: int


@dataclass
class Error:
    fase: str
    mensaje: str
    linea: int
    col: int = 0

    def __str__(self):
        ubic = f"línea {self.linea}" + (f", col {self.col}" if self.col else "")
        return f"[Error {self.fase}] {ubic}: {self.mensaje}"


def _letra(c):  return ("a" <= c <= "z") or ("A" <= c <= "Z")
def _digito(c): return "0" <= c <= "9"
def _alnum_(c): return _letra(c) or _digito(c) or c == "_"


def _es_identificador(p):
    """[a-z][a-z0-9_]*"""
    return ("a" <= p[0] <= "z") and all(("a" <= c <= "z") or _digito(c) or c == "_" for c in p)


# ---------------------------------------------------------------------------
# 1. ANÁLISIS LÉXICO
# ---------------------------------------------------------------------------
def analizar_lexico(src):
    tokens, errores = [], []
    i, n, linea, ini = 0, len(src), 1, 0

    def err(msg, col):
        errores.append(Error("léxico", msg, linea, col))

    while i < n:
        c = src[i]
        col = i - ini + 1

        if c == "\n":
            linea += 1; i += 1; ini = i; continue
        if c in " \t\r":
            i += 1; continue
        if src.startswith("//", i):                       # comentario
            while i < n and src[i] != "\n":
                i += 1
            continue

        if _letra(c):                                     # palabra
            j = i
            while j < n and _alnum_(src[j]):
                j += 1
            p = src[i:j]
            if p in RESERVADAS:
                tokens.append(Token(p, p, linea, col))
            elif _es_identificador(p):
                tokens.append(Token("ID", p, linea, col))
            else:
                err(f"'{p}' no es palabra reservada ni identificador válido "
                    f"(las reservadas van en MAYÚSCULAS exactas y los "
                    f"identificadores en minúsculas: [a-z][a-z0-9_]*)", col)
            i = j
            continue

        if _digito(c):                                    # número
            j = i
            while j < n and _digito(src[j]):
                j += 1
            if j < n and _alnum_(src[j]):                 # ej. 2sensor
                k = j
                while k < n and _alnum_(src[k]):
                    k += 1
                err(f"'{src[i:k]}' no es válido: un número no puede "
                    f"mezclarse con letras ni empezar un identificador", col)
                i = k
            else:
                tokens.append(Token("NUMERO", src[i:j], linea, col))
                i = j
            continue

        if c == '"':                                      # cadena
            j = i + 1
            while j < n and src[j] not in '"\n':
                j += 1
            if j >= n or src[j] == "\n":
                err("cadena sin cerrar (falta la comilla de cierre)", col)
                i = j
            else:
                tokens.append(Token("CADENA", src[i + 1:j], linea, col))
                i = j + 1
            continue

        if c in "<>=!":                                   # operadores
            if i + 1 < n and src[i + 1] == "=":
                tokens.append(Token("OP_REL", c + "=", linea, col)); i += 2
            elif c in "<>":
                tokens.append(Token("OP_REL", c, linea, col)); i += 1
            else:
                err(f"operador incompleto '{c}' (se esperaba '=='"
                    f"{' o ' + repr('!=') if c == '!' else ''})", col)
                i += 1
            continue

        if c == ";":
            tokens.append(Token("PUNTO_Y_COMA", ";", linea, col)); i += 1
            continue

        err(f"carácter no permitido '{c}'", col)
        i += 1

    tokens.append(Token("EOF", "", linea, i - ini + 1))
    return tokens, errores


# ---------------------------------------------------------------------------
# 2. ANÁLISIS SINTÁCTICO
# ---------------------------------------------------------------------------
@dataclass
class Nodo:
    tipo: str
    linea: int
    datos: dict = field(default_factory=dict)


class _ErrSint(Exception):
    def __init__(self, error):
        self.error = error


def _desc(t):
    if t.tipo == "EOF":
        return "el fin del archivo"
    if t.tipo == "CADENA":
        return f'"{t.lexema}"'
    return f"'{t.lexema}'"


class Parser:
    def __init__(self, tokens):
        self.t = tokens
        self.pos = 0
        self.errores = []

    @property
    def act(self):
        return self.t[self.pos]

    def _fallo(self, msg, tok):
        return _ErrSint(Error("sintáctico", msg, tok.linea, tok.col))

    def esperar(self, tipo, nombre):
        tok = self.act
        if tok.tipo != tipo:
            if tipo == "PUNTO_Y_COMA" and self.pos > 0:
                prev = self.t[self.pos - 1]
                raise self._fallo(
                    f"falta ';' al final de la instrucción (después de {_desc(prev)}); "
                    f"se encontró {_desc(tok)}", prev)
            raise self._fallo(f"se esperaba {nombre} pero se encontró {_desc(tok)}", tok)
        self.pos += 1
        return tok

    # --- programa --------------------------------------------------------
    def programa(self):
        instrs = []
        while self.act.tipo != "EOF":
            inicio = self.pos
            try:
                instrs.append(self.instruccion())
            except _ErrSint as e:
                self.errores.append(e.error)
                self._sincronizar(inicio)
        if not instrs and not self.errores:
            self.errores.append(Error("sintáctico",
                                      "el programa debe tener al menos una instrucción", 1))
        return Nodo("Programa", 1, {"instrucciones": instrs})

    def _sincronizar(self, inicio):
        """Modo pánico: salta hasta después de ';' / FIN o antes de una nueva instrucción."""
        if self.pos == inicio:
            self.pos += 1
        while self.act.tipo not in ("EOF", "PUNTO_Y_COMA", "FIN") \
                and self.act.tipo not in INICIOS_INSTRUCCION:
            self.pos += 1
        if self.act.tipo in ("PUNTO_Y_COMA", "FIN"):
            self.pos += 1

    # --- instrucciones ---------------------------------------------------
    def instruccion(self):
        k = self.act.tipo
        if k == "SI":
            return self.condicional()
        if k in ("VOLUMEN", "REPRODUCIR", "PAUSAR", "MOSTRAR"):
            return self.accion()
        if k == "CANCION":
            t = self.act; self.pos += 1
            idt = self.esperar("ID", "un identificador")
            titulo = self.esperar("CADENA", "el título entre comillas")
            artista = self.esperar("CADENA", "el artista entre comillas")
            dur = self.esperar("NUMERO", "la duración (número de segundos)")
            self.esperar("PUNTO_Y_COMA", "';'")
            return Nodo("Cancion", t.linea, {"id": idt.lexema, "titulo": titulo.lexema,
                                             "artista": artista.lexema,
                                             "duracion": int(dur.lexema)})
        if k == "PLAYLIST":
            t = self.act; self.pos += 1
            idt = self.esperar("ID", "un identificador")
            self.esperar("PUNTO_Y_COMA", "';'")
            return Nodo("Playlist", t.linea, {"id": idt.lexema})
        if k == "AGREGAR":
            t = self.act; self.pos += 1
            a = self.esperar("ID", "el identificador de la canción")
            self.esperar("A", "la palabra reservada 'A'")
            b = self.esperar("ID", "el identificador de la playlist")
            self.esperar("PUNTO_Y_COMA", "';'")
            return Nodo("Agregar", t.linea, {"cancion": a.lexema, "playlist": b.lexema})
        if k == "QUITAR":
            t = self.act; self.pos += 1
            a = self.esperar("ID", "el identificador de la canción")
            self.esperar("DE", "la palabra reservada 'DE'")
            b = self.esperar("ID", "el identificador de la playlist")
            self.esperar("PUNTO_Y_COMA", "';'")
            return Nodo("Quitar", t.linea, {"cancion": a.lexema, "playlist": b.lexema})
        if k == "FIN":
            raise self._fallo("'FIN' sin un 'SI' que lo abra", self.act)
        raise self._fallo(f"se esperaba el inicio de una instrucción pero se encontró "
                          f"{_desc(self.act)}", self.act)

    def accion(self):
        k, t = self.act.tipo, self.act
        if k == "VOLUMEN":
            self.pos += 1
            num = self.esperar("NUMERO", "un número")
            self.esperar("PUNTO_Y_COMA", "';'")
            return Nodo("Volumen", t.linea, {"valor": int(num.lexema)})
        if k in ("REPRODUCIR", "MOSTRAR"):
            self.pos += 1
            idt = self.esperar("ID", "el identificador de una playlist")
            self.esperar("PUNTO_Y_COMA", "';'")
            return Nodo("Reproducir" if k == "REPRODUCIR" else "Mostrar",
                        t.linea, {"id": idt.lexema})
        if k == "PAUSAR":
            self.pos += 1
            self.esperar("PUNTO_Y_COMA", "';'")
            return Nodo("Pausar", t.linea)
        raise self._fallo("se esperaba una acción (VOLUMEN, REPRODUCIR, PAUSAR o MOSTRAR) "
                          f"pero se encontró {_desc(t)}", t)

    def condicional(self):
        t = self.act
        self.pos += 1                                     # SI
        try:
            self.esperar("VOLUMEN", "'VOLUMEN' (la condición solo compara el volumen)")
            op = self.esperar("OP_REL", "un operador relacional (> < == != >= <=)")
            num = self.esperar("NUMERO", "un número")
            self.esperar("ENTONCES", "'ENTONCES'")
            acc = self.accion()
            self.esperar("FIN", "'FIN' para cerrar el SI")
        except _ErrSint as e:
            # recuperación: descartar hasta consumir el FIN de este SI
            while self.act.tipo not in ("EOF", "FIN"):
                self.pos += 1
            if self.act.tipo == "FIN":
                self.pos += 1
            raise e
        return Nodo("Condicional", t.linea, {"op": op.lexema, "valor": int(num.lexema),
                                             "accion": acc})


# ---------------------------------------------------------------------------
# 3. ANÁLISIS SEMÁNTICO
# ---------------------------------------------------------------------------
class Semantico:
    def __init__(self):
        self.tabla = {}          # nombre -> dict(tipo, linea, ...)
        self.errores = []
        self.advertencias = []

    def _e(self, msg, linea):
        self.errores.append(Error("semántico", msg, linea))

    def _usar(self, nombre, esperado, linea, contexto):
        """Verifica declaración y tipo. Devuelve la entrada o None."""
        ent = self.tabla.get(nombre)
        if ent is None:
            self._e(f"'{nombre}' se usa en {contexto} pero no ha sido declarado", linea)
            return None
        if ent["tipo"] != esperado:
            self._e(f"'{nombre}' es una {ent['tipo']} (declarada en línea {ent['linea']}), "
                    f"pero {contexto} requiere una {esperado}", linea)
            return None
        return ent

    def analizar(self, ast):
        for n in ast.datos["instrucciones"]:
            self.visitar(n)

    def visitar(self, n):
        d, ln = n.datos, n.linea
        if n.tipo == "Cancion":
            if d["id"] in self.tabla:
                self._e(f"'{d['id']}' ya fue declarado en la línea {self.tabla[d['id']]['linea']}", ln)
            else:
                self.tabla[d["id"]] = {"tipo": "cancion", "linea": ln, "titulo": d["titulo"],
                                       "artista": d["artista"], "duracion": d["duracion"]}
            if d["duracion"] <= 0:
                self._e(f"la duración de '{d['id']}' debe ser mayor que 0 (es {d['duracion']})", ln)
        elif n.tipo == "Playlist":
            if d["id"] in self.tabla:
                self._e(f"'{d['id']}' ya fue declarado en la línea {self.tabla[d['id']]['linea']}", ln)
            else:
                self.tabla[d["id"]] = {"tipo": "playlist", "linea": ln, "canciones": []}
        elif n.tipo == "Agregar":
            c = self._usar(d["cancion"], "cancion", ln, "AGREGAR (primer operando)")
            p = self._usar(d["playlist"], "playlist", ln, "AGREGAR ... A (segundo operando)")
            if c and p:
                if d["cancion"] in p["canciones"]:
                    self._e(f"'{d['cancion']}' ya está en la playlist '{d['playlist']}'", ln)
                else:
                    p["canciones"].append(d["cancion"])
        elif n.tipo == "Quitar":
            c = self._usar(d["cancion"], "cancion", ln, "QUITAR (primer operando)")
            p = self._usar(d["playlist"], "playlist", ln, "QUITAR ... DE (segundo operando)")
            if c and p:
                if d["cancion"] in p["canciones"]:
                    p["canciones"].remove(d["cancion"])
                else:
                    self._e(f"'{d['cancion']}' no está en la playlist '{d['playlist']}'", ln)
        elif n.tipo in ("Reproducir", "Mostrar"):
            p = self._usar(d["id"], "playlist", ln, n.tipo.upper())
            if p and n.tipo == "Reproducir" and not p["canciones"]:
                self.advertencias.append(
                    f"[Advertencia semántica] línea {ln}: se reproduce la playlist "
                    f"'{d['id']}' pero está vacía en ese punto")
        elif n.tipo == "Volumen":
            if not 0 <= d["valor"] <= 100:
                self._e(f"VOLUMEN debe estar entre 0 y 100 (se recibió {d['valor']})", ln)
        elif n.tipo == "Condicional":
            if not 0 <= d["valor"] <= 100:
                self._e(f"la condición compara VOLUMEN con {d['valor']}, fuera del rango 0-100", ln)
            self.visitar(d["accion"])


# ---------------------------------------------------------------------------
# Intérprete simple (opcional): simula la ejecución del programa ya validado
# ---------------------------------------------------------------------------
def ejecutar(ast, salida=print):
    canciones, playlists, vol = {}, {}, 50
    cmp = {">": lambda a, b: a > b, "<": lambda a, b: a < b, "==": lambda a, b: a == b,
           "!=": lambda a, b: a != b, ">=": lambda a, b: a >= b, "<=": lambda a, b: a <= b}

    def correr(n):
        nonlocal vol
        d = n.datos
        if n.tipo == "Cancion":
            canciones[d["id"]] = d
        elif n.tipo == "Playlist":
            playlists[d["id"]] = []
        elif n.tipo == "Agregar":
            playlists[d["playlist"]].append(d["cancion"])
            salida(f"+ '{canciones[d['cancion']]['titulo']}' agregada a {d['playlist']}")
        elif n.tipo == "Quitar":
            playlists[d["playlist"]].remove(d["cancion"])
            salida(f"- '{canciones[d['cancion']]['titulo']}' quitada de {d['playlist']}")
        elif n.tipo == "Volumen":
            vol = d["valor"]; salida(f"Volumen = {vol}")
        elif n.tipo == "Pausar":
            salida("Reproducción en pausa")
        elif n.tipo == "Reproducir":
            salida(f"Reproduciendo '{d['id']}' (volumen {vol}):")
            for c in playlists[d["id"]]:
                salida(f"   > {canciones[c]['titulo']} - {canciones[c]['artista']}")
        elif n.tipo == "Mostrar":
            salida(f"Playlist '{d['id']}':")
            total = 0
            for c in playlists[d["id"]]:
                s = canciones[c]
                total += s["duracion"]
                salida(f"   * {s['titulo']} - {s['artista']} ({s['duracion']//60}:{s['duracion']%60:02d})")
            salida(f"   Total: {total//60}:{total%60:02d}")
        elif n.tipo == "Condicional":
            if cmp[d["op"]](vol, d["valor"]):
                salida(f"(condición VOLUMEN {d['op']} {d['valor']} cumplida)")
                correr(d["accion"])

    for n in ast.datos["instrucciones"]:
        correr(n)


# ---------------------------------------------------------------------------
# Orquestación
# ---------------------------------------------------------------------------
@dataclass
class Resultado:
    fase_fallida: str = ""
    errores: list = field(default_factory=list)
    advertencias: list = field(default_factory=list)
    tokens: list = field(default_factory=list)
    ast: Nodo = None
    tabla: dict = field(default_factory=dict)

    @property
    def ok(self):
        return not self.errores


def compilar(src):
    r = Resultado()
    r.tokens, errs = analizar_lexico(src)
    if errs:
        r.fase_fallida, r.errores = "léxico", errs
        return r
    p = Parser(r.tokens)
    r.ast = p.programa()
    if p.errores:
        r.fase_fallida, r.errores = "sintáctico", p.errores
        return r
    s = Semantico()
    s.analizar(r.ast)
    r.tabla, r.advertencias = s.tabla, s.advertencias
    if s.errores:
        r.fase_fallida, r.errores = "semántico", s.errores
    return r


def _imprimir_ast(n, nivel=0):
    pad = "  " * nivel
    if isinstance(n, Nodo):
        simples = {k: v for k, v in n.datos.items() if not isinstance(v, (Nodo, list))}
        print(f"{pad}{n.tipo} (línea {n.linea}) {simples if simples else ''}")
        for v in n.datos.values():
            if isinstance(v, Nodo):
                _imprimir_ast(v, nivel + 1)
            elif isinstance(v, list):
                for x in v:
                    _imprimir_ast(x, nivel + 1)


def main():
    ap = argparse.ArgumentParser(description="Compilador PlayScript")
    ap.add_argument("archivo", nargs="?", type=Path, help="archivo fuente (.ps)")
    ap.add_argument("--tokens", action="store_true", help="mostrar tokens")
    ap.add_argument("--ast", action="store_true", help="mostrar árbol sintáctico")
    ap.add_argument("--tabla", action="store_true", help="mostrar tabla de símbolos")
    ap.add_argument("--ejecutar", action="store_true", help="simular la ejecución")
    a = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    archivo = a.archivo
    if archivo is None:
        archivo = Path(__file__).resolve().with_name("programa.ps")
        if not archivo.exists():
            archivo = None

    if archivo is None:
        print("Sin archivo fuente. Se usará una playlist de ejemplo.")
        src = """CANCION tema "Mi canción" "Mi artista" 180;
PLAYLIST favoritas;
AGREGAR tema A favoritas;
MOSTRAR favoritas;
"""
    else:
        try:
            src = archivo.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as error:
            ap.exit(2, f"No se pudo leer {archivo}: {error}\n")

    r = compilar(src)

    if a.tokens:
        print("== TOKENS ==")
        print(f"{'LÍNEA':<6}{'COL':<5}{'TOKEN':<14}LEXEMA")
        for t in r.tokens:
            if t.tipo != "EOF":
                print(f"{t.linea:<6}{t.col:<5}{t.tipo:<14}{t.lexema}")
        print()
    if r.ok and a.ast:
        print("== ÁRBOL SINTÁCTICO ==")
        _imprimir_ast(r.ast)
        print()
    if a.tabla and r.tabla:
        print("== TABLA DE SÍMBOLOS ==")
        for nom, e in r.tabla.items():
            extra = (f"canciones={e['canciones']}" if e["tipo"] == "playlist"
                     else f"'{e['titulo']}' - {e['artista']} ({e['duracion']}s)")
            print(f"{nom:<16}{e['tipo']:<10}línea {e['linea']:<4}{extra}")
        print()

    for adv in r.advertencias:
        print(adv)
    if not r.ok:
        for e in r.errores:
            print(e)
        print(f"\nCompilación fallida: {len(r.errores)} error(es) en la fase {r.fase_fallida}.")
        sys.exit(1)

    print("Compilación exitosa: léxico OK, sintáctico OK, semántico OK.")
    if a.ejecutar or a.archivo is None:
        print("\n== EJECUCIÓN (simulada) ==")
        ejecutar(r.ast)


if __name__ == "__main__":
    main()