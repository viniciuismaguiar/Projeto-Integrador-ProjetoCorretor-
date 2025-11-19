import json
import os
import re
from typing import Optional


# ======================================================
#  CLASSE REGRA
# ======================================================
class Regra:
    def __init__(self, nome: str, descricao: str, func):
        self.nome = nome
        self.descricao = descricao
        self.func = func  # função que avalia a regra

    def aplicar(self, texto: str):
        """Executa a função da regra e retorna (status, comentario)."""
        try:
            return self.func(texto)
        except Exception as e:
            return ("erro", f"Erro ao aplicar regra '{self.nome}': {str(e)}")


# ======================================================
#  CORRETOR
# ======================================================
class CorretorRedacao:
    def __init__(self, db: Optional[object] = None):
        self.db = db
        self.modelos_file = "modelos.json"
        self.regras = self._criar_regras_em_memoria()

        if not os.path.exists(self.modelos_file):
            self.salvar_modelos([])

        try:
            self.carregar_modelos()
        except Exception:
            self.salvar_modelos([])

    # ====================== MODELOS ======================
    def carregar_modelos(self):
        with open(self.modelos_file, "r", encoding="utf-8") as f:
            data = f.read().strip()
            if data == "":
                return []
            return json.loads(data)

    def salvar_modelos(self, modelos):
        with open(self.modelos_file, "w", encoding="utf-8") as f:
            json.dump(modelos, f, indent=4, ensure_ascii=False)

    def criar_modelo(self, nome: str, descricao: str):
        modelos = self.carregar_modelos()
        novo_id = 1 if not modelos else max(m["id"] for m in modelos) + 1
        modelo = {"id": novo_id, "nome": nome, "descricao": descricao}
        modelos.append(modelo)
        self.salvar_modelos(modelos)
        return novo_id

    # ====================== REGRAS ======================
    def _criar_regras_em_memoria(self):
        def r_norma(texto: str):
            if re.search(r"[^a-zA-Z0-9\s.,;:!?()\-áéíóúâêôãõçÁÉÍÓÚÂÊÔÃÕÇ\"'ªº%€$ººº\[\]]", texto):
                return ("erro", "Foram encontrados caracteres incomuns que sugerem erro de escrita.")
            return ("ok", "Bom domínio da norma-padrão.")

        def r_tema(texto: str):
            if len(texto.split()) < 30:
                return ("erro", "O texto é curto; pode não estar desenvolvendo o tema.")
            return ("ok", "O texto parece tratar do tema de forma inicial.")

        def r_argumentos(texto: str):
            argumentos = len(re.findall(r"\b(portanto|logo|pois|assim|desse modo|por isso|consequentemente)\b", texto.lower()))
            if argumentos < 1:
                return ("erro", "Poucos conectores argumentativos (pouca articulação de argumentos).")
            return ("ok", "Há presença de conectores argumentativos.")

        def r_conectivos(texto: str):
            conectivos = len(re.findall(r"\b(e|mas|porém|entretanto|assim|além disso|portanto)\b", texto.lower()))
            if conectivos < 1:
                return ("erro", "Pouca utilização de conectivos para garantir coesão textual.")
            return ("ok", "Uso adequado de conectivos.")

        def r_tamanho(texto: str):
            palavras = len(texto.split())
            if palavras < 120:
                return ("erro", f"Texto curto: {palavras} palavras (mínimo recomendado: 120).")
            return ("ok", "Tamanho adequado conforme critério mínimo.")

        def r_primeira_pessoa(texto: str):
            if re.search(r"\b(eu|minha|meu|acho|penso)\b", texto.lower()):
                return ("erro", "Uso de 1ª pessoa identificado (evitar em dissertativo-argumentativo).")
            return ("ok", "Não há marcas claras de 1ª pessoa.")

        regras = [
            Regra("Norma-padrão", "Avalia uso formal da escrita.", r_norma),
            Regra("Adequação ao tema", "Verifica cobertura do tema.", r_tema),
            Regra("Pertinência dos argumentos", "Identifica conectores argumentativos.", r_argumentos),
            Regra("Coesão textual", "Analisa uso de conectivos.", r_conectivos),
            Regra("Tamanho mínimo", "Verifica se há ao menos 120 palavras.", r_tamanho),
            Regra("Uso da 1ª pessoa", "Garantir impessoalidade do texto.", r_primeira_pessoa),
        ]
        return regras

    # ====================== POPULAR REGRAS NO DB ======================
    def popular_regras_padrao(self):
        if not self.db:
            raise RuntimeError("Nenhuma instância de DB fornecida ao corretor.")
        cur = self.db._execute("SELECT COUNT(*) as c FROM regras")
        if cur:
            c = cur.fetchone()['c']
            if c > 0:
                return
        for regra in self.regras:
            try:
                self.db.inserir_regra(regra.nome, regra.descricao, {})
            except Exception:
                pass

    # ====================== ANÁLISE COM PONTOS ======================
    def analisar_redacao(self, texto: str, modelo_id: Optional[int] = None):
        feedback = []
        total = 0
        max_total = len(self.regras) * 10  # cada regra vale 10 pontos

        for regra in self.regras:
            status, comentario = regra.aplicar(texto)
            pontos = 10 if status == "ok" else 0
            total += pontos
            feedback.append({
                "regra": regra.nome,
                "status": status,
                "comentario": comentario,
                "pontos": pontos,
                "max": 10
            })

        # resumo final
        feedback.append({
            "resumo": True,
            "total_pontos": total,
            "total_max": max_total,
            "nota_final": round((total / max_total) * 10, 2)
        })

        return feedback
