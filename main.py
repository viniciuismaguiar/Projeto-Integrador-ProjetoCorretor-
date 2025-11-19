import sys
import os
from Trabalho import DB
from Corretor import CorretorRedacao

# ====================== BANCO ======================
def inicializar_banco(db_path="dissertacoes.db"):
    db = DB(path=db_path)
    db.init_schema()
    return db

# ====================== MODELOS ======================
def listar_modelos(db):
    modelos = db.listar_modelos()
    if not modelos:
        print("Nenhum modelo encontrado.")
        return None

    print("\nModelos disponíveis:")
    for modelo in modelos:
        print(f"ID: {modelo.id} | Nome: {modelo.nome} | Descrição: {modelo.descricao}")
    print()

    return modelos

def solicitar_modelo(db):
    modelos = listar_modelos(db)
    if not modelos:
        escolha = input("Deseja criar um modelo padrão agora? (s/n): ").strip().lower()
        if escolha == 's':
            nome = input("Nome do novo modelo: ").strip()
            descricao = input("Descrição: ").strip()
            modelo_id = db.inserir_modelo(nome, descricao, {})
            print(f"Modelo criado com ID {modelo_id}.")
            return modelo_id
        return None

    while True:
        resp = input("Digite o ID do modelo ou 'novo' / 'lista': ").strip().lower()
        if resp == 'lista':
            listar_modelos(db)
            continue
        if resp == 'novo':
            nome = input("Nome do novo modelo: ").strip()
            descricao = input("Descrição: ").strip()
            modelo_id = db.inserir_modelo(nome, descricao, {})
            print(f"Modelo criado com ID {modelo_id}.")
            return modelo_id
        try:
            modelo_id = int(resp)
            modelo = db.buscar_modelo_por_id(modelo_id)
            if modelo:
                return modelo_id
            print("ID não encontrado.")
        except ValueError:
            print("Entrada inválida. Digite número, 'novo' ou 'lista'.")

# ====================== REDAÇÕES ======================
def ler_arquivo_txt(caminho):
    if not os.path.isfile(caminho):
        print("Arquivo não encontrado.")
        return None
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        return None

def garantir_redacao(db, estudante, modelo_id, titulo):
    cur = db.cursor.execute(
        "SELECT id FROM redacao WHERE estudante = ? AND modelo_id = ? AND titulo = ?",
        (estudante, modelo_id, titulo)
    )
    linha = cur.fetchone()
    if linha:
        return linha['id']
    return db.inserir_redacao(estudante, modelo_id, titulo)

def proxima_versao_numero(db, redacao_id):
    cur = db.cursor.execute("SELECT MAX(numero_versao) AS ultima FROM versoes WHERE redacao_id = ?", (redacao_id,))
    linha = cur.fetchone()
    return (linha['ultima'] or 0) + 1

def salvar_versao(db, redacao_id, numero, texto):
    return db.inserir_versao(redacao_id, numero, texto)

# ====================== RELATÓRIO COM CORES ======================
def imprimir_relatorio(feedback, caminho_saida=None):
    GREEN = "\033[92m"
    RED = "\033[91m"
    RESET = "\033[0m"
    CYAN = "\033[96m"
    linhas = ["----- RELATÓRIO DE CORREÇÃO -----"]

    for c in feedback:
        if "resumo" in c:
            linhas.append(f"{CYAN}Pontuação total: {c['total_pontos']}/{c['total_max']}{RESET}")
            linhas.append(f"{CYAN}Nota final (0 a 10): {c['nota_final']}{RESET}")
            linhas.append("-" * 30)
        else:
            cor = GREEN if c['status'] == "ok" else RED
            linhas.append(f"Regra: {c['regra']}")
            linhas.append(f"Status: {cor}{c['status'].upper()}{RESET}")
            linhas.append(f"Comentário: {c['comentario']}")
            linhas.append(f"Pontos obtidos: {c['pontos']}/{c['max']}")
            linhas.append("-" * 30)

    texto_final = "\n".join(linhas)
    print("\n" + texto_final + "\n")

    if caminho_saida:
        try:
            with open(caminho_saida, "w", encoding="utf-8") as f:
                f.write(texto_final)
            print(f"Relatório salvo em: {caminho_saida}")
        except Exception as e:
            print(f"Erro ao salvar: {e}")

# ====================== REGRAS PADRÃO ======================
def assegurar_regras_padrao(db):
    cur = db.cursor.execute("SELECT COUNT(*) AS c FROM regras")
    if cur.fetchone()['c'] == 0:
        print("Inserindo regras padrão...")
        corretor = CorretorRedacao(db)
        try:
            corretor.popular_regras_padrao()
        except Exception as e:
            print(f"Atenção: não foi possível popular regras no DB: {e}")
        print("Regras verificadas/inseridas.")

# ====================== MAIN ======================
def main():
    print("=== CORRETOR DE REDAÇÕES ===")
    db = inicializar_banco()
    assegurar_regras_padrao(db)
    modelo_id = solicitar_modelo(db)
    if modelo_id is None:
        print("Nenhum modelo selecionado. Saindo.")
        return

    estudante = input("Nome do estudante: ").strip()
    titulo = input("Título da redação: ").strip()

    print("\n=== Entrada da redação ===")
    print("1 - Ler arquivo TXT")
    print("2 - Digitar no CMD")
    opcao = input("Opção: ").strip()

    if opcao == "1":
        caminho = input("Caminho do arquivo TXT: ").strip()
        texto = ler_arquivo_txt(caminho)
        if texto is None:
            print("Erro na leitura. Encerrando.")
            return
    elif opcao == "2":
        print("\nDigite sua redação. Digite 'FIM' para encerrar.")
        linhas = []
        while True:
            try:
                linha = input()
            except EOFError:
                break
            if linha.strip().upper() == "FIM":
                break
            linhas.append(linha)
        texto = "\n".join(linhas)
        if len(texto.strip()) == 0:
            print("Nenhum texto escrito. Encerrando.")
            return
    else:
        print("Opção inválida.")
        return

    redacao_id = garantir_redacao(db, estudante, modelo_id, titulo)
    numero = proxima_versao_numero(db, redacao_id)
    versao_id = salvar_versao(db, redacao_id, numero, texto)
    print(f"\nRedação salva como versão {numero} (ID da versão: {versao_id})")

    corretor = CorretorRedacao(db)
    feedback = corretor.analisar_redacao(texto, modelo_id)
    imprimir_relatorio(feedback)

    if input("Salvar relatório em arquivo? (s/n): ").strip().lower() == "s":
        nome = f"relatorio_redacao_{redacao_id}_v{numero}.txt"
        imprimir_relatorio(feedback, nome)


if __name__ == "__main__":
    main()
