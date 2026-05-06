"""
======================================================
  ShopControl - CRUD de Usuários
  Módulo 1: Gerenciamento de Controle de Acesso
======================================================

Este arquivo é responsável por TODA a lógica de usuários:
  - Criar usuário (Create)
  - Ler/Listar usuários (Read)
  - Atualizar usuário (Update)
  - Deletar usuário (Delete)

O "banco de dados" é o arquivo: dados/usuarios.json
"""

import json
import os
import uuid
from datetime import datetime


# ──────────────────────────────────────────────
#  CONFIGURAÇÃO DO ARQUIVO JSON (banco de dados)
# ──────────────────────────────────────────────

# Caminho para a pasta de dados e o arquivo JSON
PASTA_DADOS = os.path.join(os.path.dirname(__file__), "..", "dados")
ARQUIVO_USUARIOS = os.path.join(PASTA_DADOS, "usuarios.json")


# ──────────────────────────────────────────────
#  CLASSES / TIPOS DE USUÁRIO
#  Aqui definimos todas as categorias possíveis
# ──────────────────────────────────────────────

# Perfis de acesso ao sistema
PERFIS = [
    "Administrador",      # Gerencia o sistema inteiro
    "Operador",           # Monitora câmeras e eventos
    "Segurança",          # Portaria e controle de acesso
    "Funcionário Loja",   # Trabalha em uma loja específica
    "Lojista (Dono)",     # Dono/locatário de uma loja
    "Funcionário Shopping", # Trabalha para o shopping (limpeza, manutenção)
    "Visitante",          # Frequentador comum
    "Cliente VIP",        # Cliente com cadastro especial
    "Contratado",         # Prestador de serviço temporário
    "Entregador",         # Faz entregas no shopping
]

# Faixas etárias
FAIXAS_ETARIAS = {
    "Criança":      (0, 12),
    "Adolescente":  (13, 17),
    "Jovem Adulto": (18, 29),
    "Adulto":       (30, 59),
    "Idoso":        (60, 120),
}

# Níveis de acesso (0 = sem acesso, 3 = acesso total)
NIVEIS_ACESSO = {
    0: "Sem Acesso",
    1: "Nível 1 - Áreas Comuns",
    2: "Nível 2 - Áreas Restritas",
    3: "Nível 3 - Acesso Total",
}

# Os 4 shoppings da rede
SHOPPINGS = ["Shopping 1", "Shopping 2", "Shopping 3", "Shopping 4", "Todos"]

# Status possíveis do usuário
STATUS_USUARIO = ["Ativo", "Inativo", "Pendente", "Bloqueado", "Suspenso"]


# ──────────────────────────────────────────────
#  FUNÇÕES AUXILIARES (uso interno)
# ──────────────────────────────────────────────

def _garantir_pasta_dados():
    """Cria a pasta 'dados' se ela não existir."""
    if not os.path.exists(PASTA_DADOS):
        os.makedirs(PASTA_DADOS)
        print(f"[INFO] Pasta criada: {PASTA_DADOS}")


def _carregar_json():
    """
    Lê o arquivo JSON e retorna os dados.
    Se o arquivo não existir, cria um novo vazio.
    """
    _garantir_pasta_dados()

    if not os.path.exists(ARQUIVO_USUARIOS):
        # Cria o arquivo com estrutura vazia
        dados_iniciais = {
            "metadados": {
                "criado_em": datetime.now().isoformat(),
                "total_usuarios": 0,
                "versao": "1.0"
            },
            "usuarios": []
        }
        _salvar_json(dados_iniciais)
        print(f"[INFO] Arquivo criado: {ARQUIVO_USUARIOS}")
        return dados_iniciais

    with open(ARQUIVO_USUARIOS, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def _salvar_json(dados):
    """Salva os dados no arquivo JSON (sobrescreve)."""
    _garantir_pasta_dados()
    with open(ARQUIVO_USUARIOS, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=4)


def _determinar_faixa_etaria(idade):
    """Determina automaticamente a faixa etária pela idade."""
    for faixa, (minimo, maximo) in FAIXAS_ETARIAS.items():
        if minimo <= idade <= maximo:
            return faixa
    return "Não informado"


def _gerar_id():
    """Gera um ID único para o usuário."""
    return str(uuid.uuid4())[:8].upper()


# ──────────────────────────────────────────────
#  C R U D  —  CREATE (Criar usuário)
# ──────────────────────────────────────────────

def criar_usuario(
    nome,
    cpf,
    email,
    telefone,
    senha,
    perfil,
    shopping_principal,
    nivel_acesso=1,
    idade=None,
    nome_loja=None,
    cargo=None,
    placa_veiculo=None,
    shoppings_acesso=None,
    observacoes=""
):
    """
    Cria um novo usuário e salva no JSON.

    Parâmetros:
        nome              : Nome completo
        cpf               : CPF (só números ou formatado)
        email             : E-mail
        telefone          : Telefone/celular
        senha             : Senha (em produção real, usar hash!)
        perfil            : Tipo de usuário (ver lista PERFIS)
        shopping_principal: Shopping onde frequenta/trabalha principalmente
        nivel_acesso      : 0 a 3 (ver NIVEIS_ACESSO)
        idade             : Idade em anos (opcional)
        nome_loja         : Se for lojista ou funcionário de loja
        cargo             : Cargo/função
        placa_veiculo     : Placa do carro (para controle do estacionamento)
        shoppings_acesso  : Lista de shoppings que pode acessar
        observacoes       : Anotações livres

    Retorna:
        dict com os dados do usuário criado, ou None se CPF já existir
    """

    # Verifica se CPF já está cadastrado
    if buscar_por_cpf(cpf):
        print(f"[ERRO] CPF {cpf} já está cadastrado!")
        return None

    # Valida perfil
    if perfil not in PERFIS:
        print(f"[ERRO] Perfil '{perfil}' inválido. Use um dos: {PERFIS}")
        return None

    # Valida shopping
    if shopping_principal not in SHOPPINGS:
        print(f"[ERRO] Shopping '{shopping_principal}' inválido.")
        return None

    # Determina faixa etária automaticamente
    faixa_etaria = _determinar_faixa_etaria(idade) if idade else "Não informado"

    # Monta o objeto do usuário — aqui está toda a riqueza de informações!
    novo_usuario = {
        # ── Identificação ──
        "id": _gerar_id(),
        "nome": nome,
        "cpf": cpf,
        "email": email,
        "telefone": telefone,
        "senha": senha,  # ⚠️ Em produção: usar hashlib.sha256(senha.encode()).hexdigest()

        # ── Perfil e Acesso ──
        "perfil": perfil,
        "nivel_acesso": nivel_acesso,
        "nivel_acesso_descricao": NIVEIS_ACESSO.get(nivel_acesso, "Desconhecido"),
        "status": "Pendente",  # Começa como pendente até ser aprovado

        # ── Dados Pessoais ──
        "idade": idade,
        "faixa_etaria": faixa_etaria,

        # ── Dados Profissionais (para funcionários/lojistas) ──
        "nome_loja": nome_loja,       # Ex: "Nike", "McDonald's"
        "cargo": cargo,               # Ex: "Vendedor", "Gerente", "Segurança"

        # ── Shoppings ──
        "shopping_principal": shopping_principal,
        "shoppings_acesso": shoppings_acesso or [shopping_principal],

        # ── Veículo (integra com módulo de estacionamento) ──
        "placa_veiculo": placa_veiculo,

        # ── Comportamento e Análise (vai crescendo com o uso) ──
        "historico_visitas": [],       # Será preenchido pelo módulo de monitoramento
        "lojas_frequentadas": [],      # IA vai preenchendo isso
        "tempo_medio_permanencia": 0,  # Em minutos
        "horario_preferido": None,     # Ex: "manhã", "tarde", "noite"
        "frequencia_visitas": 0,       # Quantas vezes visitou
        "ultima_visita": None,

        # ── Preferências e Perfil Comportamental ──
        "preferencias": {
            "categorias_lojas": [],    # Ex: ["Moda", "Alimentação", "Eletrônicos"]
            "forma_pagamento": None,   # Ex: "Cartão", "PIX", "Dinheiro"
            "grupo_social": None,      # Ex: "Família", "Casal", "Solo", "Amigos"
        },

        # ── Auditoria ──
        "criado_em": datetime.now().isoformat(),
        "atualizado_em": datetime.now().isoformat(),
        "criado_por": "sistema",
        "observacoes": observacoes,
    }

    # Carrega dados existentes, adiciona o novo usuário e salva
    dados = _carregar_json()
    dados["usuarios"].append(novo_usuario)
    dados["metadados"]["total_usuarios"] = len(dados["usuarios"])
    dados["metadados"]["ultima_atualizacao"] = datetime.now().isoformat()
    _salvar_json(dados)

    print(f"[OK] Usuário '{nome}' cadastrado com ID: {novo_usuario['id']}")
    return novo_usuario


# ──────────────────────────────────────────────
#  C R U D  —  READ (Ler / Buscar usuários)
# ──────────────────────────────────────────────

def listar_usuarios(filtro_status=None, filtro_perfil=None, filtro_shopping=None):
    """
    Lista todos os usuários, com filtros opcionais.

    Exemplos:
        listar_usuarios()                          → todos
        listar_usuarios(filtro_status="Ativo")     → só ativos
        listar_usuarios(filtro_perfil="Visitante") → só visitantes
        listar_usuarios(filtro_shopping="Shopping 1")
    """
    dados = _carregar_json()
    usuarios = dados["usuarios"]

    # Aplica filtros se fornecidos
    if filtro_status:
        usuarios = [u for u in usuarios if u["status"] == filtro_status]
    if filtro_perfil:
        usuarios = [u for u in usuarios if u["perfil"] == filtro_perfil]
    if filtro_shopping:
        usuarios = [u for u in usuarios if u["shopping_principal"] == filtro_shopping]

    return usuarios


def buscar_por_id(id_usuario):
    """Busca um usuário pelo ID único."""
    dados = _carregar_json()
    for usuario in dados["usuarios"]:
        if usuario["id"] == id_usuario:
            return usuario
    return None


def buscar_por_cpf(cpf):
    """Busca um usuário pelo CPF."""
    # Remove formatação do CPF para comparação
    cpf_limpo = cpf.replace(".", "").replace("-", "").strip()
    dados = _carregar_json()
    for usuario in dados["usuarios"]:
        cpf_banco = usuario["cpf"].replace(".", "").replace("-", "").strip()
        if cpf_banco == cpf_limpo:
            return usuario
    return None


def buscar_por_nome(nome_parcial):
    """Busca usuários pelo nome (parcial, sem maiúsculas/minúsculas)."""
    dados = _carregar_json()
    nome_lower = nome_parcial.lower()
    return [u for u in dados["usuarios"] if nome_lower in u["nome"].lower()]


def buscar_por_placa(placa):
    """Busca usuário pela placa do veículo (integração com estacionamento)."""
    dados = _carregar_json()
    placa_limpa = placa.upper().strip()
    for usuario in dados["usuarios"]:
        if usuario.get("placa_veiculo") and usuario["placa_veiculo"].upper() == placa_limpa:
            return usuario
    return None


def obter_estatisticas():
    """
    Retorna um resumo estatístico dos usuários.
    Útil para o dashboard mostrar os cards de totais.
    """
    dados = _carregar_json()
    usuarios = dados["usuarios"]

    if not usuarios:
        return {"total": 0}

    stats = {
        "total": len(usuarios),
        "por_status": {},
        "por_perfil": {},
        "por_shopping": {},
        "por_faixa_etaria": {},
    }

    for u in usuarios:
        # Por status
        s = u.get("status", "Desconhecido")
        stats["por_status"][s] = stats["por_status"].get(s, 0) + 1

        # Por perfil
        p = u.get("perfil", "Desconhecido")
        stats["por_perfil"][p] = stats["por_perfil"].get(p, 0) + 1

        # Por shopping
        sh = u.get("shopping_principal", "Desconhecido")
        stats["por_shopping"][sh] = stats["por_shopping"].get(sh, 0) + 1

        # Por faixa etária
        fe = u.get("faixa_etaria", "Não informado")
        stats["por_faixa_etaria"][fe] = stats["por_faixa_etaria"].get(fe, 0) + 1

    return stats


# ──────────────────────────────────────────────
#  C R U D  —  UPDATE (Atualizar usuário)
# ──────────────────────────────────────────────

def atualizar_usuario(id_usuario, **campos):
    """
    Atualiza campos de um usuário existente.

    Exemplo de uso:
        atualizar_usuario("ABC12345", status="Ativo", nivel_acesso=2)
        atualizar_usuario("ABC12345", placa_veiculo="XYZ-9999")

    Campos protegidos (não podem ser alterados aqui):
        id, cpf, criado_em, criado_por
    """
    CAMPOS_PROTEGIDOS = {"id", "cpf", "criado_em", "criado_por"}

    dados = _carregar_json()

    for i, usuario in enumerate(dados["usuarios"]):
        if usuario["id"] == id_usuario:

            # Atualiza apenas os campos permitidos
            for campo, valor in campos.items():
                if campo in CAMPOS_PROTEGIDOS:
                    print(f"[AVISO] Campo '{campo}' é protegido e não pode ser alterado.")
                    continue

                # Atualiza faixa etária automaticamente se idade mudar
                if campo == "idade" and valor is not None:
                    dados["usuarios"][i]["faixa_etaria"] = _determinar_faixa_etaria(valor)

                # Atualiza descrição do nível de acesso
                if campo == "nivel_acesso":
                    dados["usuarios"][i]["nivel_acesso_descricao"] = NIVEIS_ACESSO.get(valor, "Desconhecido")

                dados["usuarios"][i][campo] = valor

            dados["usuarios"][i]["atualizado_em"] = datetime.now().isoformat()
            _salvar_json(dados)
            print(f"[OK] Usuário '{usuario['nome']}' atualizado.")
            return dados["usuarios"][i]

    print(f"[ERRO] Usuário com ID '{id_usuario}' não encontrado.")
    return None


def alterar_status(id_usuario, novo_status):
    """
    Atalho para mudar o status de um usuário.
    Status possíveis: Ativo, Inativo, Pendente, Bloqueado, Suspenso
    """
    if novo_status not in STATUS_USUARIO:
        print(f"[ERRO] Status '{novo_status}' inválido. Use: {STATUS_USUARIO}")
        return None
    return atualizar_usuario(id_usuario, status=novo_status)


def registrar_visita(id_usuario, shopping, local=None):
    """
    Registra uma visita do usuário. Chamado pelo módulo de monitoramento
    quando a câmera/sensor detecta a pessoa.
    """
    usuario = buscar_por_id(id_usuario)
    if not usuario:
        return None

    visita = {
        "data_hora": datetime.now().isoformat(),
        "shopping": shopping,
        "local": local,  # Ex: "Entrada Principal", "Praça de Alimentação"
    }

    dados = _carregar_json()
    for i, u in enumerate(dados["usuarios"]):
        if u["id"] == id_usuario:
            dados["usuarios"][i]["historico_visitas"].append(visita)
            dados["usuarios"][i]["frequencia_visitas"] += 1
            dados["usuarios"][i]["ultima_visita"] = visita["data_hora"]
            dados["usuarios"][i]["atualizado_em"] = datetime.now().isoformat()
            break

    _salvar_json(dados)
    return visita


# ──────────────────────────────────────────────
#  C R U D  —  DELETE (Deletar usuário)
# ──────────────────────────────────────────────

def deletar_usuario(id_usuario):
    """
    Remove um usuário permanentemente do JSON.

    ⚠️ Atenção: em sistemas reais, prefira usar alterar_status(id, "Inativo")
    ao invés de deletar, para manter o histórico.
    """
    dados = _carregar_json()
    usuarios_antes = len(dados["usuarios"])

    dados["usuarios"] = [u for u in dados["usuarios"] if u["id"] != id_usuario]

    if len(dados["usuarios"]) < usuarios_antes:
        dados["metadados"]["total_usuarios"] = len(dados["usuarios"])
        _salvar_json(dados)
        print(f"[OK] Usuário com ID '{id_usuario}' removido.")
        return True

    print(f"[ERRO] Usuário com ID '{id_usuario}' não encontrado.")
    return False


# ──────────────────────────────────────────────
#  MENU INTERATIVO (para testar no terminal)
# ──────────────────────────────────────────────

def _exibir_usuario(u):
    """Formata e exibe os dados de um usuário no terminal."""
    print("\n" + "─" * 50)
    print(f"  ID         : {u['id']}")
    print(f"  Nome       : {u['nome']}")
    print(f"  CPF        : {u['cpf']}")
    print(f"  E-mail     : {u['email']}")
    print(f"  Perfil     : {u['perfil']}")
    print(f"  Status     : {u['status']}")
    print(f"  Shopping   : {u['shopping_principal']}")
    print(f"  Nível Acs. : {u['nivel_acesso_descricao']}")
    if u.get("idade"):
        print(f"  Idade      : {u['idade']} anos ({u['faixa_etaria']})")
    if u.get("nome_loja"):
        print(f"  Loja       : {u['nome_loja']} — {u.get('cargo', '')}")
    if u.get("placa_veiculo"):
        print(f"  Veículo    : {u['placa_veiculo']}")
    print(f"  Cadastrado : {u['criado_em'][:10]}")
    print("─" * 50)


def menu():
    """Menu interativo para testar o CRUD no terminal."""
    while True:
        print("\n╔══════════════════════════════════╗")
        print("║   ShopControl — Gestão Usuários  ║")
        print("╠══════════════════════════════════╣")
        print("║  1. Cadastrar novo usuário        ║")
        print("║  2. Listar todos os usuários      ║")
        print("║  3. Buscar por nome               ║")
        print("║  4. Buscar por CPF                ║")
        print("║  5. Buscar por placa do veículo   ║")
        print("║  6. Alterar status do usuário     ║")
        print("║  7. Ver estatísticas              ║")
        print("║  8. Deletar usuário               ║")
        print("║  0. Sair                          ║")
        print("╚══════════════════════════════════╝")

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":
            print("\n── NOVO USUÁRIO ──")
            print(f"Perfis disponíveis: {', '.join(PERFIS)}")
            print(f"Shoppings: {', '.join(SHOPPINGS)}")
            print(f"Níveis de acesso: {NIVEIS_ACESSO}")

            nome        = input("Nome completo: ").strip()
            cpf         = input("CPF: ").strip()
            email       = input("E-mail: ").strip()
            telefone    = input("Telefone: ").strip()
            senha       = input("Senha: ").strip()
            perfil      = input("Perfil: ").strip()
            shopping    = input("Shopping principal: ").strip()
            nivel_str   = input("Nível de acesso (0-3): ").strip()
            idade_str   = input("Idade (Enter para pular): ").strip()
            nome_loja   = input("Nome da loja (Enter para pular): ").strip() or None
            cargo       = input("Cargo (Enter para pular): ").strip() or None
            placa       = input("Placa do veículo (Enter para pular): ").strip() or None

            criar_usuario(
                nome=nome, cpf=cpf, email=email, telefone=telefone, senha=senha,
                perfil=perfil, shopping_principal=shopping,
                nivel_acesso=int(nivel_str) if nivel_str.isdigit() else 1,
                idade=int(idade_str) if idade_str.isdigit() else None,
                nome_loja=nome_loja, cargo=cargo, placa_veiculo=placa
            )

        elif opcao == "2":
            usuarios = listar_usuarios()
            if not usuarios:
                print("\n[INFO] Nenhum usuário cadastrado ainda.")
            else:
                print(f"\n── {len(usuarios)} USUÁRIO(S) CADASTRADO(S) ──")
                for u in usuarios:
                    _exibir_usuario(u)

        elif opcao == "3":
            nome = input("Digite parte do nome: ").strip()
            resultados = buscar_por_nome(nome)
            print(f"\n── {len(resultados)} resultado(s) ──")
            for u in resultados:
                _exibir_usuario(u)

        elif opcao == "4":
            cpf = input("CPF: ").strip()
            u = buscar_por_cpf(cpf)
            if u:
                _exibir_usuario(u)
            else:
                print("[INFO] CPF não encontrado.")

        elif opcao == "5":
            placa = input("Placa do veículo: ").strip()
            u = buscar_por_placa(placa)
            if u:
                _exibir_usuario(u)
            else:
                print("[INFO] Placa não encontrada.")

        elif opcao == "6":
            id_usr = input("ID do usuário: ").strip()
            print(f"Status possíveis: {', '.join(STATUS_USUARIO)}")
            novo_status = input("Novo status: ").strip()
            alterar_status(id_usr, novo_status)

        elif opcao == "7":
            stats = obter_estatisticas()
            print("\n── ESTATÍSTICAS ──")
            print(f"  Total de usuários : {stats['total']}")
            if stats['total'] > 0:
                print(f"  Por status        : {stats['por_status']}")
                print(f"  Por perfil        : {stats['por_perfil']}")
                print(f"  Por shopping      : {stats['por_shopping']}")
                print(f"  Por faixa etária  : {stats['por_faixa_etaria']}")

        elif opcao == "8":
            id_usr = input("ID do usuário a deletar: ").strip()
            confirmar = input(f"Tem certeza? (s/n): ").strip().lower()
            if confirmar == "s":
                deletar_usuario(id_usr)

        elif opcao == "0":
            print("\nAté logo!")
            break

        else:
            print("[AVISO] Opção inválida.")


# ──────────────────────────────────────────────
#  PONTO DE ENTRADA
# ──────────────────────────────────────────────

if __name__ == "__main__":
    """
    Quando você rodar: python usuarios.py
    Vai abrir o menu interativo no terminal.
    """
    menu()