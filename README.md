# Projeto Corretor de Redações

Este projeto implementa um sistema de **avaliação automática de redações** utilizando **Python** e **SQLite**.  
O objetivo é permitir que textos sejam cadastrados, armazenados e analisados automaticamente com base em **modelos** e **regras de correção** definidas no banco de dados.


## Estrutura do Projeto

ProjetoCorretor:
- **Trabalho.py** # Gerencia o banco de dados SQLite e funções principais
- **Corretor.py**  # Contém o algoritmo de correção textual
- **dissertacoes.db**  # Banco de dados local (gerado automaticamente)
- **redacoes/**  # Pasta com textos para teste
    - **redacao1.txt**
- **README.md**  # Documentação do projeto



## Tecnologias Utilizadas

- **Python 3.x**
- **SQLite3** (banco de dados local)
- **JSON** (para armazenamento das regras e modelos)
- **Programação Orientada a Objetos**



## Estrutura de Classes

### `Dissertacoes`
Representa uma dissertação de exemplo armazenada no banco.  
**Atributos principais:**
- `titulo`
- `autor`
- `ano`
- `texto`
- `argumentacao`



### `Modelo`
Representa o modelo de correção utilizado pelo sistema.  
**Campos armazenados:**
- `id`, `nome`, `descricao`, `json_data`



### `Regra`
Define regras de avaliação, como tamanho mínimo ou coerência textual.  
**Campos armazenados:**
- `id`, `nome`, `descricao`, `json_data`



### `DB`
Gerencia toda a comunicação com o banco de dados SQLite.  
**Principais métodos:**
- `init_schema()` → Cria as tabelas principais do banco.  
- `inserir_*()` → Insere novos registros (modelos, regras, redações, versões, etc).  
- `buscar_*()` → Recupera registros específicos.  
- `listar_*()` → Retorna listas completas de tabelas.  
- `atualizar_*()` → Atualiza registros existentes.  
- `remover_*()` → Exclui registros.  
- `ler_redacao_de_arquivo()` → Lê textos de um arquivo `.txt`.  
- `salvar_redacao_em_arquivo()` → Salva uma redação no banco e gera feedback via `CorretorModelo`.



## Integração com o Corretor

O arquivo `Corretor.py` contém a classe `CorretorModelo`, responsável por:
- Aplicar regras definidas no banco;
- Gerar comentários automáticos sobre o texto;
- Retornar feedback ao usuário.



## Como Executar o Projeto

1. Clonar ou baixar o projeto

    - Baixe os arquivos do projeto ou clone via Git:

    - git clone https://github.com/viniciuismaguiar/Projeto-Integrador-ProjetoCorretor-.git
    
2. Acessar o diretório do projeto
    - `cd ProjetoCorretor`

3. Verificar se o Python está instalado
    - `python --version`


- **Caso não esteja, instale o Python 3.x** 

4. Executar o script principal

    - Abra o terminal dentro da pasta do projeto e execute:

        - `python Trabalho.py`


- O banco de dados será criado automaticamente (caso não exista), e as tabelas serão inicializadas na primeira execução.

5. Testar o sistema com uma redação

pode ser criado um arquivo `.txt` dentro da pasta `redacoes/` e utilizar o seguinte exemplo de código no terminal interativo do Python:

        
```python
from Trabalho import DB
from Corretor import CorretorModelo
db = DB()
db.init_schema()
texto = db.ler_redacao_de_arquivo("redacoes/redacao1.txt")
resultado = db.salvar_redacao_em_arquivo(db, "João", 1, "Tema: Educação", texto)
print(resultado["feedback"])
```

## Observações:

1. O banco de dados (dissertacoes.db) é criado automaticamente na primeira execução.

2. As redações podem ser adicionadas manualmente na pasta redacoes/.

3. O sistema pode ser expandido com novas regras de correção ou modelos.

4. É possível integrar uma interface gráfica futuramente ou uma API web para uso remoto.
