# ============================================================
# TRABALHO DE INTELIGÊNCIA ARTIFICIAL
# Problema dos Jarros D'Água (4L e 3L)
# Algoritmos: BFS, DFS e IDDFS
# ============================================================

from collections import deque
import time

# ============================================================
# 1. FORMALIZAÇÃO DO PROBLEMA
# ============================================================

CAP_JARRO_4 = 4
CAP_JARRO_3 = 3
ESTADO_INICIAL = (0, 0)


def objetivo(estado):
    """Testa se o estado é objetivo: 2 litros em qualquer jarro."""
    x, y = estado
    return x == 2 or y == 2


def sucessores(estado):
    """Gera todos os estados sucessores válidos a partir de um estado."""
    x, y = estado
    filhos = []

    # 1. Encher jarro de 4L
    if x < CAP_JARRO_4:
        filhos.append(((CAP_JARRO_4, y), "Encher jarro 4L"))

    # 2. Encher jarro de 3L
    if y < CAP_JARRO_3:
        filhos.append(((x, CAP_JARRO_3), "Encher jarro 3L"))

    # 3. Esvaziar jarro de 4L
    if x > 0:
        filhos.append(((0, y), "Esvaziar jarro 4L"))

    # 4. Esvaziar jarro de 3L
    if y > 0:
        filhos.append(((x, 0), "Esvaziar jarro 3L"))

    # 5. Transferir 4L -> 3L
    if x > 0 and y < CAP_JARRO_3:
        d = min(x, CAP_JARRO_3 - y)
        filhos.append(((x - d, y + d),
                       f"Transferir {d}L do jarro 4L para o 3L"))

    # 6. Transferir 3L -> 4L
    if y > 0 and x < CAP_JARRO_4:
        d = min(y, CAP_JARRO_4 - x)
        filhos.append(((x + d, y - d),
                       f"Transferir {d}L do jarro 3L para o 4L"))

    return filhos


# ============================================================
# 2. ESTRUTURA DE NÓ (ÁRVORE DE BUSCA)
# ============================================================

class No:
    __slots__ = ('estado', 'pai', 'acao', 'profundidade', 'filhos')

    def __init__(self, estado, pai=None, acao=None, profundidade=0):
        self.estado = estado
        self.pai = pai
        self.acao = acao
        self.profundidade = profundidade
        self.filhos = []   # lista de filhos gerados (para a árvore)

    def caminho(self):
        """Reconstrói o caminho da raiz até este nó."""
        nos = []
        atual = self
        while atual is not None:
            nos.append(atual)
            atual = atual.pai
        return list(reversed(nos))


# ============================================================
# 3. BUSCA EM LARGURA (BFS)
# ============================================================

def bfs(estado_inicial):
    inicio = time.perf_counter()
    raiz = No(estado_inicial)
    if objetivo(raiz.estado):
        return raiz, raiz, 1, 0, time.perf_counter() - inicio

    fronteira = deque([raiz])
    explorados = {raiz.estado}
    nos_gerados = 1

    while fronteira:
        no = fronteira.popleft()
        for estado_filho, acao in sucessores(no.estado):
            if estado_filho not in explorados:
                filho = No(estado_filho, no, acao, no.profundidade + 1)
                no.filhos.append(filho)          # <-- constrói a árvore
                nos_gerados += 1
                if objetivo(estado_filho):
                    return filho, raiz, nos_gerados, filho.profundidade, \
                           time.perf_counter() - inicio
                explorados.add(estado_filho)
                fronteira.append(filho)

    return None, raiz, nos_gerados, 0, time.perf_counter() - inicio


# ============================================================
# 4. BUSCA EM PROFUNDIDADE (DFS)
# ============================================================

def dfs(estado_inicial, limite=1000):
    inicio = time.perf_counter()
    raiz = No(estado_inicial)
    if objetivo(raiz.estado):
        return raiz, raiz, 1, 0, time.perf_counter() - inicio

    pilha = [raiz]
    explorados = set()
    nos_gerados = 1

    while pilha:
        no = pilha.pop()
        if no.estado in explorados:
            continue
        explorados.add(no.estado)

        if no.profundidade >= limite:
            continue

        for estado_filho, acao in reversed(sucessores(no.estado)):
            if estado_filho not in explorados:
                filho = No(estado_filho, no, acao, no.profundidade + 1)
                no.filhos.append(filho)      # <-- constrói a árvore
                nos_gerados += 1
                if objetivo(estado_filho):
                    return filho, raiz, nos_gerados, filho.profundidade, \
                           time.perf_counter() - inicio
                pilha.append(filho)

    return None, raiz, nos_gerados, 0, time.perf_counter() - inicio


# ============================================================
# 5. BUSCA COM APROFUNDAMENTO ITERATIVO (IDDFS)
# ============================================================

def busca_profundidade_limitada(no, limite, explorados_no_caminho, contador):
    """Busca em profundidade com limite, evitando ciclos no caminho atual."""
    contador[0] += 1
    if objetivo(no.estado):
        return no
    if no.profundidade >= limite:
        return None

    for estado_filho, acao in sucessores(no.estado):
        if estado_filho not in explorados_no_caminho:
            filho = No(estado_filho, no, acao, no.profundidade + 1)
            no.filhos.append(filho)          # <-- constrói a árvore
            explorados_no_caminho.add(estado_filho)
            resultado = busca_profundidade_limitada(
                filho, limite, explorados_no_caminho, contador)
            if resultado is not None:
                return resultado
            explorados_no_caminho.remove(estado_filho)
    return None


def iddfs(estado_inicial, limite_max=50):
    inicio = time.perf_counter()
    total_nos = 0
    raiz = No(estado_inicial)

    for limite in range(limite_max + 1):
        contador = [0]
        # limpa filhos a cada iteração (re-trabalho do IDDFS)
        def limpar(no):
            no.filhos = []
            for f in no.filhos:
                limpar(f)
        limpar(raiz)

        explorados = {estado_inicial}
        resultado = busca_profundidade_limitada(raiz, limite, explorados, contador)
        total_nos += contador[0]
        if resultado is not None:
            return resultado, raiz, total_nos, resultado.profundidade, \
                   time.perf_counter() - inicio

    return None, raiz, total_nos, 0, time.perf_counter() - inicio


# ============================================================
# 6. IMPRESSÃO DA ÁRVORE DE BUSCA
# ============================================================

def imprimir_arvore(no, prefixo="", ultimo=True, caminho_solucao=None):
    """
    Imprime a árvore de busca de forma hierárquica.
    Destaca os nós que pertencem ao caminho da solução.
    """
    if caminho_solucao is None:
        caminho_solucao = set()

    no_caminho = no.estado in caminho_solucao and any(
        n.estado == no.estado for n in caminho_solucao) if isinstance(
        caminho_solucao, list) else False

    # Marca visual
    if no.pai is None:
        marca = "  [RAIZ]"
        print(f"{no.estado}{marca}")
    else:
        conector = "└── " if ultimo else "├── "
        destaque = "  ★ SOLUÇÃO" if objetivo(no.estado) else ""
        print(f"{prefixo}{conector}{no.estado}  <- {no.acao}{destaque}")

    novo_prefixo = prefixo + ("    " if ultimo else "│   ") if no.pai else ""
    for i, filho in enumerate(no.filhos):
        imprimir_arvore(filho, novo_prefixo, i == len(no.filhos) - 1,
                        caminho_solucao)


def imprimir_arvore_com_caminho(raiz, no_solucao):
    """
    Imprime a árvore de busca completa, marcando com ► os nós
    que pertencem ao caminho da solução.
    """
    if no_solucao is None:
        return
    ids_caminho = {id(n) for n in no_solucao.caminho()}

    def _rec(no, prefixo="", ultimo=True):
        conector = "└── " if ultimo else "├── "
        eh_caminho = id(no) in ids_caminho

        if no.pai is None:
            marcador = "► " if eh_caminho else "  "
            print(f"{marcador}{no.estado}  [RAIZ]")
        else:
            marcador = "► " if eh_caminho else "  "
            destaque = "  ★ OBJETIVO" if objetivo(no.estado) else ""
            print(f"{marcador}{prefixo}{conector}{no.estado}  <- {no.acao}{destaque}")

        novo_prefixo = prefixo + ("    " if ultimo else "│   ") if no.pai else ""
        for i, filho in enumerate(no.filhos):
            _rec(filho, novo_prefixo, i == len(no.filhos) - 1)

    _rec(raiz)


def imprimir_caminho(no_solucao):
    """Imprime o caminho linear até a solução."""
    if no_solucao is None:
        print("  Nenhuma solução encontrada.")
        return
    caminho = no_solucao.caminho()
    print("\n  CAMINHO ATÉ A SOLUÇÃO:")
    for i, no in enumerate(caminho):
        if i == 0:
            print(f"    Passo {i}: {no.estado}  (estado inicial)")
        else:
            print(f"    Passo {i}: {no.estado}  <- {no.acao}")
    print(f"    >> Solução: {caminho[-1].estado} "
          f"(2 litros em um dos jarros)\n")


# ============================================================
# 7. PROGRAMA PRINCIPAL
# ============================================================

def executar_algoritmo(nome, funcao, estado_inicial):
    print("\n" + "=" * 70)
    print(f"  ALGORITMO: {nome}")
    print("=" * 70)

    no_sol, raiz, nos, prof, tempo = funcao(estado_inicial)

    print("\n  --- ÁRVORE DE BUSCA (► = caminho da solução) ---\n")
    imprimir_arvore_com_caminho(raiz, no_sol)

    imprimir_caminho(no_sol)

    print(f"  Métricas:")
    print(f"    Nós gerados........: {nos}")
    print(f"    Profundidade.......: {prof}")
    print(f"    Tempo..............: {tempo * 1000:.4f} ms")

    return nos, prof, tempo


def main():
    print("=" * 70)
    print("  PROBLEMA DOS JARROS D'ÁGUA (4L e 3L)")
    print("  Resolução por Busca sem Informação: BFS, DFS e IDDFS")
    print("=" * 70)

    # Entrada do estado inicial
    entrada = input("\nDigite o estado inicial (x y) ou ENTER para (0 0): ").strip()
    if entrada:
        try:
            partes = entrada.split()
            estado_inicial = (int(partes[0]), int(partes[1]))
            if not (0 <= estado_inicial[0] <= 4 and 0 <= estado_inicial[1] <= 3):
                print("Estado inválido. Usando (0, 0).")
                estado_inicial = ESTADO_INICIAL
        except Exception:
            print("Entrada inválida. Usando (0, 0).")
            estado_inicial = ESTADO_INICIAL
    else:
        estado_inicial = ESTADO_INICIAL

    print(f"\n  Estado inicial..: {estado_inicial}")
    print(f"  Objetivo........: obter 2 litros em qualquer jarro")
    print(f"  Capacidades.....: jarro A = 4L, jarro B = 3L")

    resultados = {}

    # ---------- BFS ----------
    resultados['BFS'] = executar_algoritmo(
        "BUSCA EM LARGURA (BFS)", bfs, estado_inicial)

    # ---------- DFS ----------
    resultados['DFS'] = executar_algoritmo(
        "BUSCA EM PROFUNDIDADE (DFS)", dfs, estado_inicial)

    # ---------- IDDFS ----------
    resultados['IDDFS'] = executar_algoritmo(
        "BUSCA COM APROFUNDAMENTO ITERATIVO (IDDFS)", iddfs, estado_inicial)

    # ---------- Comparação Final ----------
    print("\n" + "=" * 70)
    print("  ANÁLISE COMPARATIVA DOS ALGORITMOS")
    print("=" * 70)
    print(f"  {'Algoritmo':<10} {'Nós Gerados':<15} {'Profundidade':<15} {'Tempo (ms)':<15}")
    print("  " + "-" * 60)
    for alg, (nos, prof, tempo) in resultados.items():
        print(f"  {alg:<10} {nos:<15} {prof:<15} {tempo * 1000:<15.4f}")
    print("=" * 70)


if __name__ == "__main__":
    main()