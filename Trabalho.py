# Trabalho.py (versão revisada)
import json
import sqlite3
from typing import Optional, List, Dict, Any


class Dissertacoes:
    """Modelo simples para representar uma dissertação (objetos de uso local)."""
    def __init__(self, titulo: str, autor: str, ano: int, texto: str, argumentacao: str):
        self.titulo = titulo
        self.autor = autor
        self.ano = ano
        self.texto = texto
        self.argumentacao = argumentacao


class Modelo:
    def __init__(self, id: int, nome: str, descricao: str, json_data: Dict[str, Any]):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.json_data = json_data or {}


class Regra:
    def __init__(self, id: int, nome: str, descricao: str, json_data: Dict[str, Any]):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.json_data = json_data or {}


class DB:
    """Camada simples de acesso ao SQLite.

    - Use db.init_schema() uma vez (por exemplo ao iniciar o app) para criar as tabelas.
    - Suporta uso com `with DB(path) as db:` por meio de context manager.
    """

    def __init__(self, path: str = 'dissertacoes.db', create_schema: bool = False):
        self.path = path
        self.conexao = sqlite3.connect(path)
        self.conexao.row_factory = sqlite3.Row
        self.cursor = self.conexao.cursor()
        if create_schema:
            self.init_schema()

    def __enter__(self) -> "DB":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def close(self) -> None:
        try:
            self.conexao.commit()
            self.conexao.close()
        except Exception:
            pass

    def _execute(self, query: str, params: tuple = (), commit: bool = False) -> Optional[sqlite3.Cursor]:
        """Executa uma query e trata exceções centralmente."""
        try:
            cur = self.cursor.execute(query, params)
            if commit:
                self.conexao.commit()
            return cur
        except Exception as e:
            print(f"Erro ao executar query: {e}\nSQL: {query}\nPARAMS: {params}")
            return None

    def init_schema(self) -> None:
        """Cria tabelas necessárias (executa cada DDL separadamente)."""
        tabelas = [
            ('''
                CREATE TABLE IF NOT EXISTS modelos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    descricao TEXT,
                    json_data TEXT
                );
            '''),

            ('''
                CREATE TABLE IF NOT EXISTS regras (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    descricao TEXT,
                    json_data TEXT
                );
            '''),

            ('''
                CREATE TABLE IF NOT EXISTS exemplos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT,
                    autor TEXT,
                    modelo_id INTEGER,
                    texto TEXT,
                    FOREIGN KEY(modelo_id) REFERENCES modelos(id)
                );
            '''),

            ('''
                CREATE TABLE IF NOT EXISTS redacao (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    estudante TEXT,
                    modelo_id INTEGER,
                    titulo TEXT,
                    FOREIGN KEY(modelo_id) REFERENCES modelos(id)
                );
            '''),

            ('''
                CREATE TABLE IF NOT EXISTS versoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    redacao_id INTEGER,
                    numero_versao INTEGER,
                    texto TEXT,
                    FOREIGN KEY(redacao_id) REFERENCES redacao(id)
                );
            '''),

            ('''
                CREATE TABLE IF NOT EXISTS redacao_regras (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    redacao_id INTEGER,
                    regra_id INTEGER,
                    FOREIGN KEY(redacao_id) REFERENCES redacao(id),
                    FOREIGN KEY(regra_id) REFERENCES regras(id)
                );
            ''')
        ]

        for ddl in tabelas:
            self._execute(ddl, commit=True)

    def _inserir(self, tabela: str, dados: Dict[str, Any]) -> Optional[int]:
        if not dados:
            return None
        colunas = ', '.join(dados.keys())
        valores_placeholders = ', '.join(['?'] * len(dados))
        query = f"INSERT INTO {tabela} ({colunas}) VALUES ({valores_placeholders})"
        cur = self._execute(query, tuple(dados.values()), commit=True)
        try:
            return cur.lastrowid if cur else None
        except Exception:
            return None

    def inserir_modelo(self, nome: str, descricao: str, json_data: Dict[str, Any]) -> Optional[int]:
        return self._inserir('modelos', {'nome': nome, 'descricao': descricao, 'json_data': json.dumps(json_data or {})})

    def inserir_regra(self, nome: str, descricao: str, json_data: Dict[str, Any]) -> Optional[int]:
        return self._inserir('regras', {'nome': nome, 'descricao': descricao, 'json_data': json.dumps(json_data or {})})

    def inserir_exemplo(self, titulo: str, autor: str, modelo_id: int, texto: str) -> Optional[int]:
        return self._inserir('exemplos', {'titulo': titulo, 'autor': autor, 'modelo_id': modelo_id, 'texto': texto})

    def inserir_redacao(self, estudante: str, modelo_id: int, titulo: str) -> Optional[int]:
        return self._inserir('redacao', {'estudante': estudante, 'modelo_id': modelo_id, 'titulo': titulo})

    def inserir_versao(self, redacao_id: int, numero_versao: int, texto: str) -> Optional[int]:
        return self._inserir('versoes', {'redacao_id': redacao_id, 'numero_versao': numero_versao, 'texto': texto})

    def _row_to_modelo(self, row: sqlite3.Row) -> Modelo:
        data = json.loads(row['json_data']) if row and row['json_data'] else {}
        return Modelo(row['id'], row['nome'], row['descricao'], data)

    def _row_to_regra(self, row: sqlite3.Row) -> Regra:
        data = json.loads(row['json_data']) if row and row['json_data'] else {}
        return Regra(row['id'], row['nome'], row['descricao'], data)

    def buscar_modelo_por_id(self, modelo_id: int) -> Optional[Modelo]:
        cur = self._execute("SELECT * FROM modelos WHERE id = ?", (modelo_id,))
        linha = cur.fetchone() if cur else None
        return self._row_to_modelo(linha) if linha else None

    def buscar_regra_por_id(self, regra_id: int) -> Optional[Regra]:
        cur = self._execute("SELECT * FROM regras WHERE id = ?", (regra_id,))
        linha = cur.fetchone() if cur else None
        return self._row_to_regra(linha) if linha else None

    def buscar_exemplo_por_id(self, exemplo_id: int) -> Optional[Dict[str, Any]]:
        cur = self._execute("SELECT * FROM exemplos WHERE id = ?", (exemplo_id,))
        linha = cur.fetchone() if cur else None
        return dict(linha) if linha else None

    def buscar_redacao(self, id: int) -> Optional[Dict[str, Any]]:
        cur = self._execute("SELECT * FROM redacao WHERE id = ?", (id,))
        linha = cur.fetchone() if cur else None
        return dict(linha) if linha else None

    def buscar_versoes_redacao(self, redacao_id: int) -> List[Dict[str, Any]]:
        cur = self._execute("SELECT * FROM versoes WHERE redacao_id = ?", (redacao_id,))
        return [dict(l) for l in cur.fetchall()] if cur else []

    def _listar(self, tabela: str, cls=None) -> List[Any]:
        cur = self._execute(f"SELECT * FROM {tabela}")
        linhas = cur.fetchall() if cur else []
        if cls:
            lista = []
            for l in linhas:
                json_data = json.loads(l['json_data']) if l['json_data'] else {}
                lista.append(cls(l['id'], l['nome'], l['descricao'], json_data))
            return lista
        return [dict(l) for l in linhas]

    def listar_regras(self) -> List[Regra]:
        return self._listar('regras', Regra)

    def listar_modelos(self) -> List[Modelo]:
        return self._listar('modelos', Modelo)

    def atualizar(self, tabela: str, id: int, dados: Dict[str, Any]) -> bool:
        if not dados:
            return False
        sets = ', '.join([f"{k} = ?" for k in dados.keys()])
        valores = list(dados.values()) + [id]
        return self._execute(f"UPDATE {tabela} SET {sets} WHERE id = ?", tuple(valores), commit=True) is not None

    def atualizar_modelo(self, id: int, nome: Optional[str] = None, descricao: Optional[str] = None, json_data: Optional[Dict[str, Any]] = None) -> bool:
        modelo = self.buscar_modelo_por_id(id)
        if not modelo:
            return False
        nome = nome if nome is not None else modelo.nome
        descricao = descricao if descricao is not None else modelo.descricao
        json_data = json_data if json_data is not None else modelo.json_data
        return self.atualizar('modelos', id, {'nome': nome, 'descricao': descricao, 'json_data': json.dumps(json_data)})

    def atualizar_regra(self, id: int, nome: Optional[str] = None, descricao: Optional[str] = None, json_data: Optional[Dict[str, Any]] = None) -> bool:
        regra = self.buscar_regra_por_id(id)
        if not regra:
            return False
        nome = nome if nome is not None else regra.nome
        descricao = descricao if descricao is not None else regra.descricao
        json_data = json_data if json_data is not None else regra.json_data
        return self.atualizar('regras', id, {'nome': nome, 'descricao': descricao, 'json_data': json.dumps(json_data)})

    def atualizar_exemplo(self, id: int, titulo: Optional[str] = None, autor: Optional[str] = None, modelo_id: Optional[int] = None, texto: Optional[str] = None) -> bool:
        exemplo = self.buscar_exemplo_por_id(id)
        if not exemplo:
            return False
        titulo = titulo if titulo is not None else exemplo['titulo']
        autor = autor if autor is not None else exemplo['autor']
        modelo_id = modelo_id if modelo_id is not None else exemplo['modelo_id']
        texto = texto if texto is not None else exemplo['texto']
        return self.atualizar('exemplos', id, {'titulo': titulo, 'autor': autor, 'modelo_id': modelo_id, 'texto': texto})

    def _remover(self, tabela: str, id: int) -> bool:
        return self._execute(f"DELETE FROM {tabela} WHERE id = ?", (id,), commit=True) is not None

    def remover_modelo(self, modelo_id: int) -> bool:
        return self._remover('modelos', modelo_id)

    def remover_regra(self, regra_id: int) -> bool:
        return self._remover('regras', regra_id)

    def remover_exemplo(self, exemplo_id: int) -> bool:
        return self._remover('exemplos', exemplo_id)

    def remover_redacao(self, redacao_id: int) -> bool:
        return self._remover('redacao', redacao_id)

    def remover_versao(self, versao_id: int) -> bool:
        return self._remover('versoes', versao_id)

    @staticmethod
    def ler_redacao_de_arquivo(caminho_arquivo: str) -> Optional[str]:
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
                return arquivo.read()
        except FileNotFoundError:
            print(f"Arquivo não encontrado: {caminho_arquivo}")
        except Exception as e:
            print(f"Erro ao ler arquivo {caminho_arquivo}: {e}")
        return None

    @staticmethod
    def salvar_redacao_em_arquivo(db: 'DB', estudante: str, modelo_id: int, titulo: str, texto: str) -> Optional[Dict[str, Any]]:
        """Salva redação (cria redacao e versão) e retorna metadados e feedback.

        Retorna dict com: redacao_id, versao_id, feedback, numero_versao
        """
        try:
            # Busca redação existente
            cur = db._execute(
                "SELECT id FROM redacao WHERE estudante = ? AND modelo_id = ? AND titulo = ?",
                (estudante, modelo_id, titulo)
            )
            linha = cur.fetchone() if cur else None

            redacao_id = linha['id'] if linha else db.inserir_redacao(estudante, modelo_id, titulo)
            if redacao_id is None:
                raise RuntimeError("Não foi possível criar/recuperar redacao_id")

            cur = db._execute(
                "SELECT MAX(numero_versao) as ultima_versao FROM versoes WHERE redacao_id = ?",
                (redacao_id,)
            )
            resultado = cur.fetchone() if cur else None
            numero_versao = (resultado['ultima_versao'] or 0) + 1 if resultado is not None else 1

            versao_id = db.inserir_versao(redacao_id, numero_versao, texto)
            if versao_id is None:
                raise RuntimeError("Não foi possível inserir a versão da redação")

            # Lazy import para evitar import circular com Corretor.py
            from Corretor import CorretorRedacao  # import local

            corretor = CorretorRedacao(db)
            feedback = corretor.analisar_redacao(texto, modelo_id)

            return {
                'redacao_id': redacao_id,
                'versao_id': versao_id,
                'feedback': feedback,
                'numero_versao': numero_versao
            }
        except Exception as e:
            print(f"Erro ao salvar redação: {e}")
            return None
