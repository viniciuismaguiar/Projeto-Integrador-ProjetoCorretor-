import json
import sqlite3
from Corretor import CorretorModelo

class Dissertacoes():
    def __init__(self , titulo, autor, ano, texto, argumentacao):
        self.titulo = titulo
        self.autor = autor
        self.ano = ano
        self.texto = texto
        self.argumentacao = argumentacao
        pass

class Modelo():
    def __init__(self, id,  nome, descricao, json_data):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.json_data = json_data
        pass

class Regra():
    def __init__(self, id, nome, descricao, json_data):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.json_data = json_data
        pass

class DB:
    def __init__(self, path='dissertacoes.db'):
        self.conexao = sqlite3.connect(path)
        self.conexao.row_factory = sqlite3.Row
        self.cursor = self.conexao.cursor()

    def init_schema(self):
        schema = '''
        CREATE TABLE IF NOT EXISTS modelos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            json_data TEXT
        );
        CREATE TABLE IF NOT EXISTS regras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            json_data TEXT
        );
        CREATE TABLE IF NOT EXISTS exemplos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            autor TEXT,
            modelo_id INTEGER,
            texto TEXT,
            FOREIGN KEY(modelo_id) REFERENCES modelos(id)
        );
        CREATE TABLE IF NOT EXISTS redacao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            estudante TEXT,
            modelo_id INTEGER,
            titulo TEXT,
            FOREIGN KEY(modelo_id) REFERENCES modelos(id)
        );
        CREATE TABLE IF NOT EXISTS versoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            redacao_id INTEGER,
            numero_versao INTEGER,
            texto TEXT,
            FOREIGN KEY(redacao_id) REFERENCES redacao(id)
        );
        CREATE TABLE IF NOT EXISTS redacao_regras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            redacao_id INTEGER,
            regra_id INTEGER,
            FOREIGN KEY(redacao_id) REFERENCES redacao(id),
            FOREIGN KEY(regra_id) REFERENCES regras(id)
        );
        '''
        self.cursor.executescript(schema)
        self.conexao.commit()

    def inserir_modelo(self, nome, descricao, json_data):
        self.cursor.execute(
            "INSERT INTO modelos (nome, descricao, json_data) VALUES (?, ?, ?)",
            (nome, descricao, json.dumps(json_data))
        )
        self.conexao.commit()
        return self.cursor.lastrowid

    def inserir_regra(self, nome, descricao, json_data):
        self.cursor.execute(
            "INSERT INTO regras (nome, descricao, json_data) VALUES (?, ?, ?)",
            (nome, descricao, json.dumps(json_data))
        )
        self.conexao.commit()
        return self.cursor.lastrowid
    
    def inserir_exemplo(self, titulo, autor, modelo_id, texto):
        self.cursor.execute(
            "INSERT INTO exemplos (titulo, autor, modelo_id, texto) VALUES (?, ?, ?, ?)",
            (titulo, autor, modelo_id, texto)
        )
        self.conexao.commit()
        return self.cursor.lastrowid
    
    def inserir_redacao(self, estudante, modelo_id, titulo):
        self.cursor.execute(
            "INSERT INTO redacao (estudante, modelo_id, titulo) VALUES (?, ?, ?)",
            (estudante, modelo_id, titulo)
        )
        self.conexao.commit()
        return self.cursor.lastrowid
    
    def inserir_versao(self, redacao_id, numero_versao, texto):
        self.cursor.execute(
            "INSERT INTO versoes (redacao_id, numero_versao, texto) VALUES (?, ?, ?)",
            (redacao_id, numero_versao, texto)
        )
        self.conexao.commit()
        return self.cursor.lastrowid
    def buscar_modelo_por_id(self, modelo_id):
        self.cursor.execute(
            "SELECT * FROM modelos WHERE id = ?",
            (modelo_id,)
        )
        linha = self.cursor.fetchone()
        if linha:
            return Modelo(
                id=linha['id'],
                nome=linha['nome'],
                descricao=linha['descricao'],
                json_data=json.loads(linha['json_data'])
            )
        return None
    
    def listar_modelos(self):
        self.cursor.execute("SELECT * FROM modelos")
        linhas = self.cursor.fetchall()
        modelos = []
        for linha in linhas:
            modelos.append(Modelo(
                id=linha['id'],
                nome=linha['nome'],
                descricao=linha['descricao'],
                json_data=json.loads(linha['json_data'])
            ))
        return modelos
    
    def buscar_regra_por_id(self, regra_id):
        self.cursor.execute(
            "SELECT * FROM regras WHERE id = ?",
            (regra_id,)
        )
        linha = self.cursor.fetchone()
        if linha:
            return Regra(
                id=linha['id'],
                nome=linha['nome'],
                descricao=linha['descricao'],
                json_data=json.loads(linha['json_data'])
            )
        return None
    
    def listar_regras(self):
        self.cursor.execute("SELECT * FROM regras")
        linhas = self.cursor.fetchall()
        regras = []
        for linha in linhas:
            regras.append(Regra(
                id=linha['id'],
                nome=linha['nome'],
                descricao=linha['descricao'],
                json_data=json.loads(linha['json_data'])
            ))
        return regras
    
    def buscar_exemplo_por_id(self, exemplo_id):
        self.cursor.execute(
            "SELECT * FROM exemplos WHERE id = ?",
            (exemplo_id,)
        )
        linha = self.cursor.fetchone()
        if linha:
            return {
                'id': linha['id'],
                'titulo': linha['titulo'],
                'autor': linha['autor'],
                'modelo_id': linha['modelo_id'],
                'texto': linha['texto']
            }
        return None
    
    def buscar_redacao(self, id):
        self.cursor.execute(
            "SELECT * FROM redacao WHERE id = ?",
            (id,))
        return self.cursor.fetchone()
    
    def buscar_versoes_redacao(self, redacao_id):
        self.cursor.execute(
            "SELECT * FROM versoes WHERE redacao_id = ?",
            (redacao_id,))
        return self.cursor.fetchall()
    
    def atualizar_modelo(self, id, nome = None, descricao = None, json_data = None):
        modelo = self.buscar_modelo_por_id(id)
        if not modelo:
            return False
        nome = nome if nome is not None else modelo.nome
        descricao = descricao if descricao is not None else modelo.descricao
        json_data = json_data if json_data is not None else modelo.json_data
        self.cursor.execute(
            "UPDATE modelos SET nome = ?, descricao = ?, json_data = ? WHERE id = ?",
            (nome, descricao, json.dumps(json_data), id)
        )
        self.conexao.commit()
        return True
    
    def atualizar_regra(self, id, nome = None, descricao = None, json_data = None):
        regra = self.buscar_regra_por_id(id)
        if not regra:
            return False
        nome = nome if nome is not None else regra.nome
        descricao = descricao if descricao is not None else regra.descricao
        json_data = json_data if json_data is not None else regra.json_data
        self.cursor.execute(
            "UPDATE regras SET nome = ?, descricao = ?, json_data = ? WHERE id = ?",
            (nome, descricao, json.dumps(json_data), id)
        )
        self.conexao.commit()
        return True
    
    def atualizar_exemplo(self, id, titulo = None, autor = None, modelo_id = None, texto = None):
        exemplo = self.buscar_exemplo_por_id(id)
        if not exemplo:
            return False
        titulo = titulo if titulo is not None else exemplo['titulo']
        autor = autor if autor is not None else exemplo['autor']
        modelo_id = modelo_id if modelo_id is not None else exemplo['modelo_id']
        texto = texto if texto is not None else exemplo['texto']
        self.cursor.execute(
            "UPDATE exemplos SET titulo = ?, autor = ?, modelo_id = ?, texto = ? WHERE id = ?",
            (titulo, autor, modelo_id, texto, id)
        )
        self.conexao.commit()
        return True

    def remover_modelo(self, modelo_id):
        self.cursor.execute(
            "DELETE FROM modelos WHERE id = ?",
            (modelo_id,)
        )
        self.conexao.commit()

    def remover_regra(self, regra_id):
        self.cursor.execute(
            "DELETE FROM regras WHERE id = ?",
            (regra_id,)
        )
        self.conexao.commit()

    def remover_exemplo(self, exemplo_id):
        self.cursor.execute(
            "DELETE FROM exemplos WHERE id = ?",
            (exemplo_id,)
        )
        self.conexao.commit()

    def remover_redacao(self, redacao_id):
        self.cursor.execute(
            "DELETE FROM redacao WHERE id = ?",
            (redacao_id,)
        )
        self.conexao.commit()
        return True
    
    def remover_versao(self, versao_id):
        self.cursor.execute(
            "DELETE FROM versoes WHERE id = ?",
            (versao_id,)
        )
        self.conexao.commit()
        return True
    
    @staticmethod
    def ler_redacao_de_arquivo(caminho_arquivo):
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
                return arquivo.read()
        except FileNotFoundError:
            print(f"Erro ao ler redação do arquivo: {caminho_arquivo}")
            return None
        except Exception as e:
            print(f"Erro inesperado ao ler redação do arquivo: {e}")
            return None
    

    @staticmethod
    def salvar_redacao_em_arquivo(db, estudante, modelo_id, titulo, texto):
        try:
            db.cursor.execute(
                "SELECT id FROM redacao WHERE estudante = ? AND modelo_id = ? AND titulo = ?",
                (estudante, modelo_id, titulo)
            )
            linha = db.cursor.fetchone()
            if linha:
                redacao_id = linha['id']
            else:
                redacao_id = db.inserir_redacao(estudante, modelo_id, titulo)

            db.cursor.execute(
                "SELECT MAX(numero_versao) as ultima_versao FROM versoes WHERE redacao_id = ?",
                (redacao_id,)
            )
            resultado = db.cursor.fetchone()
            numero_versao = (resultado['ultima_versao'] or 0) + 1

            versao_id = db.inserir_versao(redacao_id, numero_versao, texto)
            corretor = CorretorModelo().avaliar(texto)
            feedback = corretor.avaliar(texto)

            return {
                'redacao_id': redacao_id,
                'versao_id': versao_id,
                'feedback': feedback,
                'numero_versao': numero_versao,
            }
        except Exception as e:
            print(f"Erro ao salvar redação: {e}")
            return None

