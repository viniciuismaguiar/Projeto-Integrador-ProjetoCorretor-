# Projeto Corretor de Redações

Este projeto implementa um sistema de **avaliação automática de redações** utilizando **Python** e **SQLite**.  
O objetivo é permitir que textos sejam cadastrados, armazenados e analisados automaticamente com base em **modelos** e **regras de correção** definidas no banco de dados.

Agora o projeto conta com um **script principal (`main.py`)**, que permite digitar ou ler redações de arquivo e gerar um **relatório detalhado com pontuação**, com cores destacando regras aprovadas ou com erro.

---

## Estrutura do Projeto

ProjetoIntegrador:
- **main.py**  # Script principal do corretor de redações
- **Trabalho.py** # Gerencia o banco de dados SQLite e funções principais
- **Corretor.py**  # Contém o algoritmo de correção textual e regras
- **dissertacoes.db**  # Banco de dados local (gerado automaticamente)
- **redacoes/**  # Pasta com textos para teste
    - **redacao1.txt**
- **README.md**  # Documentação do projeto

---

## Tecnologias Utilizadas

- **Python 3.x**
- **SQLite3** (banco de dados local)
- **JSON** (para armazenamento das regras e modelos)
- **Programação Orientada a Objetos**
- **Cores no terminal** (via códigos ANSI para feedback visual)

---

## Estrutura de Classes

### `Dissertacoes`
Representa uma dissertação armazenada no banco.  
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
- `salvar_redacao_em_arquivo()` → Salva uma redação no banco e gera feedback via `CorretorRedacao`.

---

## Integração com o Corretor

O arquivo `Corretor.py` contém a classe `CorretorRedacao`, responsável por:
- Aplicar regras definidas no banco ou em memória;
- Gerar comentários automáticos sobre o texto;
- Atribuir **pontuação por regra** e calcular nota final;
- Retornar feedback detalhado.

---

## Como Executar o Projeto

1. **Clonar ou baixar o projeto**

```bash
git clone https://github.com/viniciuismaguiar/Projeto-Integrador-ProjetoCorretor-.git
