import json  
from Trabalho import DB  
from Trabalho import Modelo

class CorretorModelo():
    def __init__(self, banco):
        self.banco = banco

    def carregar_modelos(self):
        modelos = []
        consulta = "SELECT * FROM modelos"
        resultados = self.banco.cursor.execute(consulta).fetchall()
        for linha in resultados:
            modelo = Modelo(
                id=linha['id'],
                nome=linha['nome'],
                descricao=linha['descricao'],
                json_data=json.loads(linha['json_data'])
            )
            modelos.append(modelo)
        return modelos

    def analisar_redacao(self, redacao_texto, modelo_id):
        modelo = self.banco.buscar_modelo_por_id(modelo_id)
        if not modelo:
            raise ValueError("Modelo não encontrado")
        
        regras = self.banco.listar_regras()
        comentarios = self.aplicar_regras(redacao_texto, regras)
        return comentarios

    def aplicar_regras(self, redacao_texto, regras):
        comentarios = []
        texto_lower = redacao_texto.lower()

        for regra in regras:
            if regra.nome == "Tamanho mínimo":
                minimo = regra.json_data.get('min_palavras', 0)
                qtd = len(redacao_texto.split())
                if qtd < minimo:
                    comentarios.append({
                        "regra": regra.nome,
                        "comentario": f"A redação possui {qtd} palavras, o mínimo exigido é {minimo}."
                    })
                else:
                    comentarios.append({
                        "regra": regra.nome,
                        "status": "ok",
                        "comentario": regra.json_data.get("mensagem_ok", "Tamanho mínimo adequado.")
                    })

            elif regra.nome == "Uso da 1ª pessoa":
                proibidos = regra.json_data.get('proibidos', [])
                encontrados = [p for p in proibidos if p in texto_lower]
                if encontrados:
                    comentarios.append({
                        "regra": regra.nome,
                        "comentario": f"Uso inadequado da 1ª pessoa: {', '.join(encontrados)}."
                    })
                else:
                    comentarios.append({
                        "regra": regra.nome,
                        "status": "ok",
                        "comentario": regra.json_data.get("mensagem_ok", "Não há uso da 1ª pessoa.")
                    })

            elif regra.nome == "Proposta de intervenção":
                itens = regra.json_data.get("itens_necessarios", [])
                faltando = [i for i in itens if i not in texto_lower]
                if faltando:
                    comentarios.append({
                        "regra": regra.nome,
                        "comentario": f"Faltam itens na proposta de intervenção: {', '.join(faltando)}."
                    })
                else:
                    comentarios.append({
                        "regra": regra.nome,
                        "status": "ok",
                        "comentario": regra.json_data.get("mensagem_ok", "Proposta de intervenção adequada.")
                    })

            elif regra.nome == "Pertinência dos argumentos":
                palavras_chave = regra.json_data.get('palavras_chave', ["porque", "portanto", "logo", "assim", "pois"])
                minimo_argumentos = regra.json_data.get('minimo_argumentos', 1)
                contagem = sum(texto_lower.count(p) for p in palavras_chave)
                if contagem < minimo_argumentos:
                    comentarios.append({
                        "regra": regra.nome,
                        "comentario": f"Faltam argumentos suficientes, apenas {contagem} detectado(s)."
                    })
                else:
                    comentarios.append({
                        "regra": regra.nome,
                        "status": "ok",
                        "comentario": regra.json_data.get("mensagem_ok", "Argumentação adequada.")
                    })

            elif regra.nome == "Coesão textual":
                conectivos = regra.json_data.get('conectivos', ["além disso", "portanto", "logo", "assim", "por outro lado", "no entanto", "entretanto"])
                conectivos_minimos = regra.json_data.get('conectivos_minimos', 0)
                contagem_conectivos = sum(texto_lower.count(c) for c in conectivos)
                if contagem_conectivos < conectivos_minimos:
                    comentarios.append({
                        "regra": regra.nome,
                        "comentario": f"Faltam conectivos adequados, apenas {contagem_conectivos} detectado(s)."
                    })
                else:
                    comentarios.append({
                        "regra": regra.nome,
                        "status": "ok",
                        "comentario": regra.json_data.get("mensagem_ok", "Coesão textual adequada.")
                    })

            elif regra.nome == "Domínio da norma-padrão":
                comentarios.append({
                    "regra": regra.nome,
                    "status": "ok",
                    "comentario": regra.json_data.get("mensagem_ok", "Domínio da norma-padrão adequado.")
                })

            elif regra.nome == "Estrutura dissertativo-argumentativa":
                comentarios.append({
                    "regra": regra.nome,
                    "status": "ok",
                    "comentario": regra.json_data.get("mensagem_ok", "Estrutura dissertativo-argumentativa adequada.")
                })

            elif regra.nome == "Repetição vocabular":
                limite = regra.json_data.get('limite_repeticoes', 5)
                palavras = texto_lower.split()
                repeticoes = {p: palavras.count(p) for p in set(palavras) if palavras.count(p) > limite}
                if repeticoes:
                    comentarios.append({
                        "regra": regra.nome,
                        "comentario": f"Repetição excessiva: {', '.join(repeticoes.keys())}."
                    })
                else:
                    comentarios.append({
                        "regra": regra.nome,
                        "status": "ok",
                        "comentario": regra.json_data.get("mensagem_ok", "Vocabulário adequado.")
                    })

            elif regra.nome == "Referenciação":
                comentarios.append({
                    "regra": regra.nome,
                    "status": "ok",
                    "comentario": regra.json_data.get("mensagem_ok", "Referenciação adequada.")
                })

            elif regra.nome == "Adequação ao tema":
                palavras_chave = regra.json_data.get("palavras_chave", [])
                faltando = [p for p in palavras_chave if p not in texto_lower]
                if faltando:
                    comentarios.append({
                        "regra": regra.nome,
                        "comentario": f"Faltam palavras-chave do tema: {', '.join(faltando)}."
                    })
                else:
                    comentarios.append({
                        "regra": regra.nome,
                        "status": "ok",
                        "comentario": regra.json_data.get("mensagem_ok", "Tema adequado.")
                    })

        return comentarios

    def popular_regras_padrao(self):
        regras = [
            {
                "nome": "Domínio da norma-padrão",
                "descricao": "Avalia desvios gramaticais, ortográficos, de concordância, regência e pontuação.",
                "json_data": {
                    "tipos_erros": ["acentuação", "pontuação", "concordância", "regência", "ortografia"],
                    "mensagem_ok": "A redação demonstra bom domínio da norma-padrão da língua portuguesa.",
                    "mensagem_erro": "Foram identificados desvios em relação à norma-padrão, comprometendo a correção gramatical."
                }
            },
            {
                "nome": "Adequação ao tema",
                "descricao": "Verifica se o texto aborda o tema proposto.",
                "json_data": {
                    "palavras_chave": [],
                    "mensagem_ok": "O texto desenvolve o tema proposto de maneira adequada.",
                    "mensagem_fuga": "Desenvolvimento tangencial ou fuga parcial ao tema.",
                    "mensagem_fuga_total": "Fuga total ao tema. O texto não atende ao propósito solicitado."
                }
            },
            {
                "nome": "Estrutura dissertativo-argumentativa",
                "descricao": "Confere se há introdução, desenvolvimento e conclusão com progressão.",
                "json_data": {
                    "mensagem_ok": "O texto apresenta estrutura dissertativo-argumentativa adequada.",
                    "mensagem_erro": "Ausência de elementos essenciais à estrutura dissertativa."
                }
            },
            {
                "nome": "Pertinência dos argumentos",
                "descricao": "Avalia consistência e relevância dos argumentos apresentados.",
                "json_data": {
                    "mensagem_ok": "Argumentos consistentes e bem relacionados à tese.",
                    "mensagem_erro": "Argumentação insuficiente, repetitiva ou desconexa.",
                    "palavras_chave": ["porque", "portanto", "logo", "assim", "pois"],
                    "minimo_argumentos": 1
                }
            },
            {
                "nome": "Coesão textual",
                "descricao": "Analisa uso de conectivos e mecanismos de articulação textual.",
                "json_data": {
                    "conectivos_minimos": 3,
                    "mensagem_ok": "Há boa articulação entre as partes do texto.",
                    "mensagem_erro": "Faltam conectores adequados, prejudicando a progressão das ideias."
                }
            },
            {
                "nome": "Repetição vocabular",
                "descricao": "Detecta repetição excessiva de termos que prejudicam a fluidez.",
                "json_data": {
                    "limite_repeticoes": 5,
                    "mensagem_ok": "O vocabulário apresenta variedade e precisão.",
                    "mensagem_erro": "Repetição vocabular compromete a clareza do texto."
                }
            },
            {
                "nome": "Referenciação",
                "descricao": "Verifica se pronomes e substituições ajudam a manter coesão referencial.",
                "json_data": {
                    "mensagem_ok": "Mecanismos de coesão referencial bem utilizados.",
                    "mensagem_erro": "Problemas de referenciação prejudicam a progressão textual."
                }
            },
            {
                "nome": "Proposta de intervenção",
                "descricao": "Avalia se a proposta possui agente, ação, meio, efeito e detalhamento.",
                "json_data": {
                    "itens_necessarios": ["agente", "acao", "meio", "efeito", "detalhamento"],
                    "mensagem_ok": "A proposta de intervenção é completa, coerente e detalhada.",
                    "mensagem_incompleta": "A proposta de intervenção está presente, porém incompleta.",
                    "mensagem_ausente": "Ausência de proposta de intervenção relacionada ao tema."
                }
            },
            {
                "nome": "Tamanho mínimo",
                "descricao": "Verifica se o texto possui quantidade mínima de palavras.",
                "json_data": {
                    "min_palavras": 120,
                    "mensagem_ok": "A extensão do texto é adequada.",
                    "mensagem_erro": "Texto com extensão insuficiente para avaliação."
                }
            },
            {
                "nome": "Uso da 1ª pessoa",
                "descricao": "Detecta marcas de subjetividade inadequadas ao gênero dissertativo.",
                "json_data": {
                    "proibidos": ["eu", "meu", "minha", "acho", "acredito"],
                    "mensagem_ok": "Não há marcas de 1ª pessoa.",
                    "mensagem_erro": "Uso inadequado da 1ª pessoa compromete a formalidade do gênero."
                }
            }
        ]

        for r in regras:
            self.banco.inserir_regra(r["nome"], r["descricao"], r["json_data"])
