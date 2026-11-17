#!/usr/bin/env python3
from playscript import compilar

BASE = '''CANCION t1 "Bohemian Rhapsody" "Queen" 354;
CANCION t2 "Yellow" "Coldplay" 269;
PLAYLIST fav;
'''

CASOS = [
    # ---------------- VÁLIDOS ----------------
    ("V1 programa completo", BASE + '''AGREGAR t1 A fav;
AGREGAR t2 A fav;
VOLUMEN 70;
SI VOLUMEN > 80
ENTONCES VOLUMEN 50;
FIN
REPRODUCIR fav;
QUITAR t2 DE fav;
MOSTRAR fav;
''', "", ""),
    ("V2 con comentarios y pausa", '''// mi playlist
PLAYLIST rock;
PAUSAR;
''', "", ""),
    ("V3 condicional con >=", BASE + '''VOLUMEN 90;
SI VOLUMEN >= 90
ENTONCES PAUSAR;
FIN
''', "", ""),
    ("V4 espacios extra / una sola línea", 'PLAYLIST   a ;   VOLUMEN    0 ;', "", ""),
    ("V5 mostrar playlist vacía", 'PLAYLIST vacia;\nMOSTRAR vacia;', "", ""),

    # ---------------- LÉXICOS ----------------
    ("L1 carácter @", 'PLAYLIST @rock;', "léxico", "'@'"),
    ("L2 cadena sin cerrar", 'CANCION t1 "Yellow 10;', "léxico", "cadena sin cerrar"),
    ("L3 identificador empieza con número", 'PLAYLIST 2rock;', "léxico", "'2rock'"),
    ("L4 reservada en minúsculas/mixta", 'Playlist rock;', "léxico", "'Playlist'"),
    ("L5 operador '=' suelto", BASE + 'SI VOLUMEN = 5 ENTONCES PAUSAR; FIN', "léxico", "'='"),

    # ---------------- SINTÁCTICOS ----------------
    ("S1 falta A", BASE + 'AGREGAR t1 fav;', "sintáctico", "'A'"),
    ("S2 falta ;", BASE + 'VOLUMEN 70\nPAUSAR;', "sintáctico", "falta ';'"),
    ("S3 SI sin FIN", BASE + 'SI VOLUMEN > 80 ENTONCES VOLUMEN 50;', "sintáctico", "FIN"),
    ("S4 FIN sin SI", BASE + 'FIN', "sintáctico", "sin un 'SI'"),
    ("S5 canción incompleta", 'CANCION t1 "Yellow";', "sintáctico", "artista"),
    ("S6 condición mal formada", BASE + 'SI 80 > VOLUMEN ENTONCES PAUSAR; FIN', "sintáctico", "VOLUMEN"),
    ("S7 programa vacío", '// nada', "sintáctico", "al menos una instrucción"),

    # ---------------- SEMÁNTICOS ----------------
    ("M1 canción no declarada", 'PLAYLIST rock;\nAGREGAR tema9 A rock;', "semántico", "no ha sido declarado"),
    ("M2 volumen fuera de rango", 'VOLUMEN 150;', "semántico", "entre 0 y 100"),
    ("M3 reproducir una canción", BASE + 'REPRODUCIR t1;', "semántico", "requiere una playlist"),
    ("M4 identificador duplicado", 'PLAYLIST a;\nPLAYLIST a;', "semántico", "ya fue declarado"),
    ("M5 agregar duplicada", BASE + 'AGREGAR t1 A fav;\nAGREGAR t1 A fav;', "semántico", "ya está en la playlist"),
    ("M6 quitar la que no está", BASE + 'QUITAR t1 DE fav;', "semántico", "no está en la playlist"),
    ("M7 duración 0", 'CANCION t1 "X" "Y" 0;', "semántico", "mayor que 0"),
    ("M8 tipos invertidos en AGREGAR", BASE + 'AGREGAR fav A t1;', "semántico", "requiere una"),
    ("M9 rango en condición", 'SI VOLUMEN > 500 ENTONCES PAUSAR; FIN', "semántico", "fuera del rango"),
]


def main():
    fallos = 0
    for nombre, src, fase, texto in CASOS:
        r = compilar(src)
        ok = (r.fase_fallida == fase) and (not texto or any(texto in e.mensaje for e in r.errores))
        fallos += not ok
        estado = "OK   " if ok else "FALLA"
        detalle = "válido" if not fase else f"error {fase}"
        print(f"[{estado}] {nombre:<38} -> {detalle}")
        if not ok:
            print(f"        obtenido: fase={r.fase_fallida!r}, errores={[str(e) for e in r.errores]}")
    print(f"\n{len(CASOS) - fallos}/{len(CASOS)} pruebas correctas")
    raise SystemExit(1 if fallos else 0)


if __name__ == "__main__":
    main()
