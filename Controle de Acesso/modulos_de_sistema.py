"""
╔══════════════════════════════════════════════════════════════╗
║         MÓDULO DE GERENCIAMENTO DE MÓDULOS DO SISTEMA        ║
║              ShopControl - Rede de Shoppings                 ║
╚══════════════════════════════════════════════════════════════╝
"""

import json
import os
from datetime import datetime


# ─────────────────────────────────────────────
#  CONFIGURAÇÃO DO BANCO DE DADOS (JSON)
# ─────────────────────────────────────────────

PASTA_DADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'dados')
ARQUIVO_MODULOS = os.path.join(PASTA_DADOS, 'modulos.json')


# ─────────────────────────────────────────────
#  TIPOS E PERMISSÕES
# ─────────────────────────────────────────────

PERFIS_USUARIOS = [
    "administrador",
    "supervisor",
    "segurança",
    "operador",
    "lojista",
    "funcionario_shopping",
    "funcionario_loja",
    "visitante"
]

STATUS_MODULO = ["ativo", "inativo", "manutenção", "em_desenvolvimento"]

CATEGORIAS_MODULO = [
    "controle_acesso",
    "equipamentos",
    "monitoramento",
    "auditoria",
    "analise",
    "relatorios",
    "segurança",
    "estacionamento"
]


# ─────────────────────────────────────────────
#  FUNÇÕES DE BANCO DE DADOS
# ─────────────────────────────────────────────

def _inicializar_banco():
    """Cria a pasta dados/ e o arquivo modulos.json se não existirem."""
    os.makedirs(PASTA_DADOS, exist_ok=True)
    if not os.path.exists(ARQUIVO_MODULOS):
        estrutura_inicial = {
            "metadados": {
                "criado_em": datetime.now().isoformat(),
                "ultima_atualizacao": datetime.now().isoformat(),
                "total_modulos": 0,
                "versao": "1.0"
            },
            "modulos": []
        }
        _salvar_dados(estrutura_inicial)
        print("✅ Banco de dados 'modulos.json' criado com sucesso!")


def _carregar_dados():
    """Lê e retorna os dados do arquivo JSON."""
    _inicializar_banco()
    with open(ARQUIVO_MODULOS, 'r', encoding='utf-8') as f:
        return json.load(f)


def _salvar_dados(dados):
    """Salva os dados no arquivo JSON."""
    os.makedirs(PASTA_DADOS, exist_ok=True)
    dados['metadados']['ultima_atualizacao'] = datetime.now().isoformat()
    dados['metadados']['total_modulos'] = len(dados['modulos'])
    with open(ARQUIVO_MODULOS, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def _gerar_id():
    """Gera um ID único para o módulo."""
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


# ─────────────────────────────────────────────
#  CRUD — CRIAR
# ─────────────────────────────────────────────

def criar_modulo(
    nome: str,
    descricao: str,
    categoria: str,
    permissoes: list,
    shopping_ids: list = None,
    icone: str = "🔧",
    versao: str = "1.0.0",
    responsavel: str = ""
) -> dict:
    """
    Cadastra um novo módulo do sistema.

    Parâmetros:
        nome         → Nome do módulo (ex: "Controle de Acesso")
        descricao    → O que esse módulo faz
        categoria    → Categoria (ver CATEGORIAS_MODULO)
        permissoes   → Lista de perfis com acesso (ver PERFIS_USUARIOS)
        shopping_ids → Lista de shoppings onde está ativo (None = todos)
        icone        → Emoji representando o módulo
        versao       → Versão do módulo
        responsavel  → Nome do responsável pelo módulo

    Retorna:
        Dicionário com os dados do módulo criado
    """
    dados = _carregar_dados()

    # Verifica se já existe módulo com o mesmo nome
    for m in dados['modulos']:
        if m['nome'].lower() == nome.lower():
            print(f"⚠️  Já existe um módulo com o nome '{nome}'.")
            return None

    # Valida categoria
    if categoria not in CATEGORIAS_MODULO:
        print(f"⚠️  Categoria inválida. Opções: {', '.join(CATEGORIAS_MODULO)}")
        return None

    # Valida permissões
    permissoes_invalidas = [p for p in permissoes if p not in PERFIS_USUARIOS]
    if permissoes_invalidas:
        print(f"⚠️  Perfis inválidos: {', '.join(permissoes_invalidas)}")
        return None

    novo_modulo = {
        "id": _gerar_id(),
        "nome": nome,
        "descricao": descricao,
        "categoria": categoria,
        "icone": icone,
        "versao": versao,
        "status": "ativo",
        "permissoes": permissoes,
        "shopping_ids": shopping_ids if shopping_ids else ["todos"],
        "responsavel": responsavel,
        "configuracoes": {},
        "logs_atividade": [],
        "criado_em": datetime.now().isoformat(),
        "atualizado_em": datetime.now().isoformat(),
        "ativado_em": datetime.now().isoformat(),
        "desativado_em": None,
        "total_acessos": 0
    }

    dados['modulos'].append(novo_modulo)
    _salvar_dados(dados)
    print(f"✅ Módulo '{nome}' cadastrado com sucesso! ID: {novo_modulo['id']}")
    return novo_modulo


# ─────────────────────────────────────────────
#  CRUD — LISTAR / BUSCAR
# ─────────────────────────────────────────────

def listar_modulos(status: str = None, categoria: str = None) -> list:
    """
    Lista todos os módulos cadastrados.

    Parâmetros opcionais:
        status    → Filtra por status (ex: "ativo", "inativo")
        categoria → Filtra por categoria

    Retorna:
        Lista de módulos
    """
    dados = _carregar_dados()
    modulos = dados['modulos']

    if status:
        modulos = [m for m in modulos if m['status'] == status]
    if categoria:
        modulos = [m for m in modulos if m['categoria'] == categoria]

    return modulos


def buscar_por_id(modulo_id: str) -> dict:
    """Busca um módulo pelo ID."""
    dados = _carregar_dados()
    for m in dados['modulos']:
        if m['id'] == modulo_id:
            return m
    print(f"⚠️  Módulo com ID '{modulo_id}' não encontrado.")
    return None


def buscar_por_nome(nome: str) -> dict:
    """Busca um módulo pelo nome."""
    dados = _carregar_dados()
    for m in dados['modulos']:
        if m['nome'].lower() == nome.lower():
            return m
    print(f"⚠️  Módulo '{nome}' não encontrado.")
    return None


# ─────────────────────────────────────────────
#  CRUD — ATUALIZAR
# ─────────────────────────────────────────────

def atualizar_modulo(modulo_id: str, **campos) -> dict:
    """
    Atualiza os dados de um módulo.

    Parâmetros:
        modulo_id → ID do módulo a atualizar
        **campos  → Campos a atualizar (ex: descricao="nova desc", versao="2.0")

    Retorna:
        Módulo atualizado ou None se não encontrado
    """
    dados = _carregar_dados()
    campos_permitidos = ['nome', 'descricao', 'categoria', 'permissoes',
                         'shopping_ids', 'icone', 'versao', 'responsavel', 'configuracoes']

    for i, m in enumerate(dados['modulos']):
        if m['id'] == modulo_id:
            for campo, valor in campos.items():
                if campo in campos_permitidos:
                    dados['modulos'][i][campo] = valor
                else:
                    print(f"⚠️  Campo '{campo}' não pode ser atualizado diretamente.")
            dados['modulos'][i]['atualizado_em'] = datetime.now().isoformat()
            _salvar_dados(dados)
            print(f"✅ Módulo '{m['nome']}' atualizado com sucesso!")
            return dados['modulos'][i]

    print(f"⚠️  Módulo com ID '{modulo_id}' não encontrado.")
    return None


def ativar_modulo(modulo_id: str) -> dict:
    """Ativa um módulo desativado."""
    dados = _carregar_dados()
    for i, m in enumerate(dados['modulos']):
        if m['id'] == modulo_id:
            if m['status'] == 'ativo':
                print(f"⚠️  Módulo '{m['nome']}' já está ativo.")
                return m
            dados['modulos'][i]['status'] = 'ativo'
            dados['modulos'][i]['ativado_em'] = datetime.now().isoformat()
            dados['modulos'][i]['atualizado_em'] = datetime.now().isoformat()
            _salvar_dados(dados)
            print(f"✅ Módulo '{m['nome']}' ativado com sucesso!")
            return dados['modulos'][i]
    print(f"⚠️  Módulo com ID '{modulo_id}' não encontrado.")
    return None


def desativar_modulo(modulo_id: str, motivo: str = "") -> dict:
    """Desativa um módulo ativo."""
    dados = _carregar_dados()
    for i, m in enumerate(dados['modulos']):
        if m['id'] == modulo_id:
            if m['status'] == 'inativo':
                print(f"⚠️  Módulo '{m['nome']}' já está inativo.")
                return m
            dados['modulos'][i]['status'] = 'inativo'
            dados['modulos'][i]['desativado_em'] = datetime.now().isoformat()
            dados['modulos'][i]['atualizado_em'] = datetime.now().isoformat()
            if motivo:
                dados['modulos'][i]['logs_atividade'].append({
                    "evento": "desativado",
                    "motivo": motivo,
                    "data": datetime.now().isoformat()
                })
            _salvar_dados(dados)
            print(f"✅ Módulo '{m['nome']}' desativado. Motivo: {motivo or 'Não informado'}")
            return dados['modulos'][i]
    print(f"⚠️  Módulo com ID '{modulo_id}' não encontrado.")
    return None


def atualizar_permissoes(modulo_id: str, permissoes: list) -> dict:
    """Atualiza quais perfis têm acesso a um módulo."""
    permissoes_invalidas = [p for p in permissoes if p not in PERFIS_USUARIOS]
    if permissoes_invalidas:
        print(f"⚠️  Perfis inválidos: {', '.join(permissoes_invalidas)}")
        return None
    return atualizar_modulo(modulo_id, permissoes=permissoes)


# ─────────────────────────────────────────────
#  CRUD — DELETAR
# ─────────────────────────────────────────────

def deletar_modulo(modulo_id: str) -> bool:
    """
    Remove permanentemente um módulo do sistema.

    Retorna True se deletado, False se não encontrado.
    """
    dados = _carregar_dados()
    for i, m in enumerate(dados['modulos']):
        if m['id'] == modulo_id:
            nome = m['nome']
            dados['modulos'].pop(i)
            _salvar_dados(dados)
            print(f"🗑️  Módulo '{nome}' deletado permanentemente.")
            return True
    print(f"⚠️  Módulo com ID '{modulo_id}' não encontrado.")
    return False


# ─────────────────────────────────────────────
#  FUNÇÕES AUXILIARES
# ─────────────────────────────────────────────

def verificar_permissao(modulo_id: str, perfil_usuario: str) -> bool:
    """
    Verifica se um perfil de usuário tem permissão para acessar o módulo.

    Útil para o sistema de login — antes de abrir qualquer tela,
    o dashboard vai chamar essa função para verificar o acesso.
    """
    modulo = buscar_por_id(modulo_id)
    if not modulo:
        return False
    if modulo['status'] != 'ativo':
        print(f"⚠️  Módulo '{modulo['nome']}' está {modulo['status']}.")
        return False
    return perfil_usuario in modulo['permissoes']


def registrar_acesso(modulo_id: str, usuario_id: str, perfil: str):
    """Registra que um usuário acessou o módulo (para auditoria)."""
    dados = _carregar_dados()
    for i, m in enumerate(dados['modulos']):
        if m['id'] == modulo_id:
            dados['modulos'][i]['total_acessos'] += 1
            dados['modulos'][i]['logs_atividade'].append({
                "evento": "acesso",
                "usuario_id": usuario_id,
                "perfil": perfil,
                "data": datetime.now().isoformat()
            })
            _salvar_dados(dados)
            return
    print(f"⚠️  Módulo '{modulo_id}' não encontrado para registrar acesso.")


def obter_estatisticas() -> dict:
    """Retorna estatísticas gerais dos módulos — útil para o dashboard."""
    dados = _carregar_dados()
    modulos = dados['modulos']

    return {
        "total": len(modulos),
        "ativos": len([m for m in modulos if m['status'] == 'ativo']),
        "inativos": len([m for m in modulos if m['status'] == 'inativo']),
        "em_manutencao": len([m for m in modulos if m['status'] == 'manutenção']),
        "por_categoria": {
            cat: len([m for m in modulos if m['categoria'] == cat])
            for cat in CATEGORIAS_MODULO
        },
        "mais_acessados": sorted(modulos, key=lambda x: x['total_acessos'], reverse=True)[:5]
    }


# ─────────────────────────────────────────────
#  POPULAR COM DADOS INICIAIS DO PROJETO
# ─────────────────────────────────────────────

def popular_modulos_iniciais():
    """
    Popula o sistema com os módulos reais do projeto ShopControl.
    Chame essa função uma vez para inicializar o sistema.
    """
    modulos_do_projeto = [
        {
            "nome": "Controle de Acesso",
            "descricao": "Gerenciamento de usuários, perfis, login e permissões do sistema.",
            "categoria": "controle_acesso",
            "permissoes": ["administrador", "supervisor"],
            "icone": "🔐",
            "versao": "1.0.0",
            "responsavel": "Equipe de TI"
        },
        {
            "nome": "Gerenciamento de Equipamentos",
            "descricao": "Cadastro e distribuição de câmeras, sensores e equipamentos nos ambientes.",
            "categoria": "equipamentos",
            "permissoes": ["administrador", "supervisor", "operador"],
            "icone": "🎥",
            "versao": "1.0.0",
            "responsavel": "Equipe de TI"
        },
        {
            "nome": "Monitoramento de Prédios",
            "descricao": "Monitoramento em tempo real das câmeras e sensores dos ambientes internos.",
            "categoria": "monitoramento",
            "permissoes": ["administrador", "supervisor", "segurança", "operador"],
            "icone": "🏢",
            "versao": "1.0.0",
            "responsavel": "Equipe de Segurança"
        },
        {
            "nome": "Monitoramento de Estacionamento",
            "descricao": "Controle de entrada e saída de veículos, leitura de placas e vagas disponíveis.",
            "categoria": "estacionamento",
            "permissoes": ["administrador", "supervisor", "segurança", "operador"],
            "icone": "🚗",
            "versao": "1.0.0",
            "responsavel": "Equipe de Segurança"
        },
        {
            "nome": "Auditoria",
            "descricao": "Registro e consulta de todos os eventos e ações realizadas no sistema.",
            "categoria": "auditoria",
            "permissoes": ["administrador", "supervisor"],
            "icone": "📋",
            "versao": "1.0.0",
            "responsavel": "Equipe de TI"
        },
        {
            "nome": "Mapa de Calor",
            "descricao": "Análise de fluxo de pessoas, áreas mais frequentadas e geração de relatórios para locação.",
            "categoria": "analise",
            "permissoes": ["administrador", "supervisor", "lojista"],
            "icone": "🔥",
            "versao": "1.0.0",
            "responsavel": "Equipe de Análise"
        },
    ]

    print("\n📦 Populando módulos do sistema...\n")
    for m in modulos_do_projeto:
        criar_modulo(**m)
    print("\n✅ Todos os módulos iniciais foram cadastrados!")


# ─────────────────────────────────────────────
#  MENU INTERATIVO (PARA TESTAR NO TERMINAL)
# ─────────────────────────────────────────────

def _exibir_modulo(m: dict):
    """Exibe os dados de um módulo de forma legível no terminal."""
    print(f"""
  {m['icone']}  {m['nome']} (ID: {m['id']})
  ├─ Descrição  : {m['descricao']}
  ├─ Categoria  : {m['categoria']}
  ├─ Status     : {m['status'].upper()}
  ├─ Versão     : {m['versao']}
  ├─ Responsável: {m['responsavel']}
  ├─ Permissões : {', '.join(m['permissoes'])}
  ├─ Shoppings  : {', '.join(m['shopping_ids'])}
  ├─ Acessos    : {m['total_acessos']}
  └─ Criado em  : {m['criado_em'][:10]}
""")


def menu():
    """Menu interativo para testar o CRUD no terminal."""
    _inicializar_banco()
    while True:
        print("""
╔══════════════════════════════════════════════╗
║      MÓDULOS DO SISTEMA - ShopControl        ║
╠══════════════════════════════════════════════╣
║  1. Listar todos os módulos                  ║
║  2. Buscar módulo por ID                     ║
║  3. Buscar módulo por nome                   ║
║  4. Cadastrar novo módulo                    ║
║  5. Atualizar módulo                         ║
║  6. Ativar módulo                            ║
║  7. Desativar módulo                         ║
║  8. Atualizar permissões                     ║
║  9. Deletar módulo                           ║
║  10. Ver estatísticas                        ║
║  11. Popular com módulos iniciais do projeto ║
║  0. Sair                                     ║
╚══════════════════════════════════════════════╝
        """)
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            modulos = listar_modulos()
            if not modulos:
                print("\n⚠️  Nenhum módulo cadastrado ainda.")
            else:
                print(f"\n📋 {len(modulos)} módulo(s) encontrado(s):\n")
                for m in modulos:
                    _exibir_modulo(m)

        elif opcao == "2":
            mid = input("ID do módulo: ").strip().upper()
            m = buscar_por_id(mid)
            if m:
                _exibir_modulo(m)

        elif opcao == "3":
            nome = input("Nome do módulo: ").strip()
            m = buscar_por_nome(nome)
            if m:
                _exibir_modulo(m)

        elif opcao == "4":
            print("\n── Cadastrar novo módulo ──")
            nome = input("Nome: ").strip()
            descricao = input("Descrição: ").strip()
            print(f"Categorias disponíveis: {', '.join(CATEGORIAS_MODULO)}")
            categoria = input("Categoria: ").strip()
            print(f"Perfis disponíveis: {', '.join(PERFIS_USUARIOS)}")
            perms_input = input("Permissões (separadas por vírgula): ").strip()
            permissoes = [p.strip() for p in perms_input.split(',')]
            responsavel = input("Responsável: ").strip()
            icone = input("Ícone (emoji, opcional): ").strip() or "🔧"
            criar_modulo(nome, descricao, categoria, permissoes,
                        responsavel=responsavel, icone=icone)

        elif opcao == "5":
            mid = input("ID do módulo a atualizar: ").strip().upper()
            campo = input("Campo a atualizar (nome/descricao/versao/responsavel): ").strip()
            valor = input(f"Novo valor para '{campo}': ").strip()
            atualizar_modulo(mid, **{campo: valor})

        elif opcao == "6":
            mid = input("ID do módulo a ativar: ").strip().upper()
            ativar_modulo(mid)

        elif opcao == "7":
            mid = input("ID do módulo a desativar: ").strip().upper()
            motivo = input("Motivo (opcional): ").strip()
            desativar_modulo(mid, motivo)

        elif opcao == "8":
            mid = input("ID do módulo: ").strip().upper()
            print(f"Perfis disponíveis: {', '.join(PERFIS_USUARIOS)}")
            perms_input = input("Novas permissões (separadas por vírgula): ").strip()
            permissoes = [p.strip() for p in perms_input.split(',')]
            atualizar_permissoes(mid, permissoes)

        elif opcao == "9":
            mid = input("ID do módulo a deletar: ").strip().upper()
            confirm = input(f"⚠️  Tem certeza? Digite 'SIM' para confirmar: ").strip()
            if confirm == "SIM":
                deletar_modulo(mid)

        elif opcao == "10":
            stats = obter_estatisticas()
            print(f"""
📊 Estatísticas dos Módulos:
  Total     : {stats['total']}
  Ativos    : {stats['ativos']}
  Inativos  : {stats['inativos']}
  Manutenção: {stats['em_manutencao']}
  Por categoria: {json.dumps(stats['por_categoria'], indent=4, ensure_ascii=False)}
""")

        elif opcao == "11":
            popular_modulos_iniciais()

        elif opcao == "0":
            print("\n👋 Saindo...\n")
            break
        else:
            print("⚠️  Opção inválida.")


# ─────────────────────────────────────────────
#  PONTO DE ENTRADA
# ─────────────────────────────────────────────

if __name__ == "__main__":
    menu()