"""
======================================================
  ShopControl - CRUD de Ambientes
  Módulo 1: Gerenciamento de Controle de Acesso
======================================================

Este arquivo gerencia todos os AMBIENTES físicos dos shoppings:
  - Lojas (comerciais, alimentação, serviços, lazer...)
  - Áreas comuns (corredores, praças, banheiros...)
  - Infraestrutura (estacionamento, portarias, admin...)
  - Cada ambiente tem: localização, piso, ala, câmeras, status

O "banco de dados" é o arquivo: dados/ambientes.json
"""

import json
import os
import uuid
from datetime import datetime


# ──────────────────────────────────────────────
#  CONFIGURAÇÃO DO ARQUIVO JSON
# ──────────────────────────────────────────────

PASTA_DADOS = os.path.join(os.path.dirname(__file__), "..", "dados")
ARQUIVO_AMBIENTES = os.path.join(PASTA_DADOS, "ambientes.json")


# ──────────────────────────────────────────────
#  CATEGORIAS DE AMBIENTES
# ──────────────────────────────────────────────

CATEGORIAS = [
    "Loja - Moda Feminina",
    "Loja - Moda Masculina",
    "Loja - Moda Infantil",
    "Loja - Moda Unissex",
    "Loja - Calçados",
    "Loja - Acessórios e Bolsas",
    "Loja - Joias e Relógios",
    "Loja - Óticas",
    "Loja - Perfumaria e Cosméticos",
    "Loja - Esportes",
    "Loja - Eletrônicos e Tecnologia",
    "Loja - Casa e Decoração",
    "Loja - Brinquedos e Infantil",
    "Loja - Livraria e Papelaria",
    "Loja - Pet Shop",
    "Loja - Outros",
    "Alimentação - Restaurante",
    "Alimentação - Lanchonete",
    "Alimentação - Cafeteria",
    "Alimentação - Outros",
    "Lazer - Cinema",
    "Lazer - Games e Diversões",
    "Lazer - Academia",
    "Lazer - Outros",
    "Serviços - Banco",
    "Serviços - Saúde e Beleza",
    "Serviços - Telefonia",
    "Serviços - Câmbio",
    "Serviços - Turismo",
    "Serviços - Outros",
    "Área Comum - Corredor",
    "Área Comum - Praça",
    "Área Comum - Banheiro",
    "Área Comum - Elevador/Escada",
    "Estacionamento",
    "Administrativo",
    "Segurança",
    "Infraestrutura",
]

PISOS = [
    "Subsolo 2",
    "Subsolo 1",
    "Térreo",
    "Piso L1",
    "Piso L2",
    "Piso L3",
    "Cobertura",
]

ALAS = ["Ala A", "Ala B", "Ala C", "Ala D", "Central", "Norte", "Sul", "Leste", "Oeste"]

STATUS_AMBIENTE = ["Ativo", "Inativo", "Em Reforma", "Desativado", "Em Implantação"]

SHOPPINGS = ["Shopping 1", "Shopping 2", "Shopping 3", "Shopping 4"]


# ──────────────────────────────────────────────
#  FUNÇÕES AUXILIARES
# ──────────────────────────────────────────────

def _garantir_pasta_dados():
    if not os.path.exists(PASTA_DADOS):
        os.makedirs(PASTA_DADOS)


def _carregar_json():
    _garantir_pasta_dados()
    if not os.path.exists(ARQUIVO_AMBIENTES):
        dados_iniciais = {
            "metadados": {
                "criado_em": datetime.now().isoformat(),
                "total_ambientes": 0,
                "versao": "1.0"
            },
            "ambientes": []
        }
        _salvar_json(dados_iniciais)
        return dados_iniciais
    with open(ARQUIVO_AMBIENTES, "r", encoding="utf-8") as f:
        return json.load(f)


def _salvar_json(dados):
    _garantir_pasta_dados()
    with open(ARQUIVO_AMBIENTES, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)


def _gerar_id():
    return str(uuid.uuid4())[:8].upper()


# ──────────────────────────────────────────────
#  C R U D — CREATE
# ──────────────────────────────────────────────

def criar_ambiente(
    nome,
    categoria,
    shopping,
    piso,
    ala=None,
    numero_loja=None,
    area_m2=None,
    capacidade_pessoas=None,
    tem_camera=True,
    quantidade_cameras=1,
    tem_sensor_presenca=False,
    responsavel=None,
    telefone_contato=None,
    horario_abertura="10:00",
    horario_fechamento="22:00",
    tipo_publico=None,
    subcategorias=None,
    observacoes=""
):
    """
    Cadastra um novo ambiente no shopping.

    Parâmetros principais:
        nome               : Nome do ambiente/loja
        categoria          : Tipo do ambiente (ver lista CATEGORIAS)
        shopping           : Em qual shopping está
        piso               : Piso onde está localizado
        ala                : Ala do shopping (opcional)
        numero_loja        : Número da loja (ex: "L142", "A23")
        area_m2            : Área em metros quadrados
        capacidade_pessoas : Quantas pessoas comporta
        tem_camera         : Se há câmera de monitoramento
        quantidade_cameras : Número de câmeras instaladas
        tem_sensor_presenca: Se há sensor de presença (mapa de calor)
        responsavel        : Nome do responsável/lojista
        tipo_publico       : Público alvo (ex: "Feminino", "Masculino", "Infantil", "Todos")
        subcategorias      : Lista de subcategorias (ex: ["Calçados femininos", "Bolsas"])
    """

    dados = _carregar_json()

    # Verifica se já existe ambiente com mesmo nome no mesmo shopping e piso
    for amb in dados["ambientes"]:
        if (amb["nome"].lower() == nome.lower() and
            amb["shopping"] == shopping and
            amb["piso"] == piso):
            print(f"[ERRO] Ambiente '{nome}' já existe no {shopping} - {piso}!")
            return None

    novo_ambiente = {
        # ── Identificação ──
        "id": _gerar_id(),
        "nome": nome,
        "categoria": categoria,
        "subcategorias": subcategorias or [],

        # ── Localização ──
        "shopping": shopping,
        "piso": piso,
        "ala": ala,
        "numero_loja": numero_loja,

        # ── Características Físicas ──
        "area_m2": area_m2,
        "capacidade_pessoas": capacidade_pessoas,

        # ── Monitoramento (integra com módulo de câmeras) ──
        "tem_camera": tem_camera,
        "quantidade_cameras": quantidade_cameras,
        "tem_sensor_presenca": tem_sensor_presenca,
        "ids_cameras": [],          # Será preenchido pelo módulo de equipamentos

        # ── Dados Comerciais ──
        "responsavel": responsavel,
        "telefone_contato": telefone_contato,
        "horario_abertura": horario_abertura,
        "horario_fechamento": horario_fechamento,
        "tipo_publico": tipo_publico or "Todos",

        # ── Status ──
        "status": "Ativo",

        # ── Análise e Mapa de Calor (preenchido pelo monitoramento) ──
        "total_visitas": 0,
        "media_visitas_dia": 0,
        "horario_pico": None,
        "faixa_etaria_predominante": None,
        "genero_predominante": None,
        "tempo_medio_permanencia_min": 0,

        # ── Auditoria ──
        "criado_em": datetime.now().isoformat(),
        "atualizado_em": datetime.now().isoformat(),
        "observacoes": observacoes,
    }

    dados["ambientes"].append(novo_ambiente)
    dados["metadados"]["total_ambientes"] = len(dados["ambientes"])
    dados["metadados"]["ultima_atualizacao"] = datetime.now().isoformat()
    _salvar_json(dados)

    print(f"[OK] Ambiente '{nome}' cadastrado — {shopping} | {piso} | {ala or 'Sem ala'}")
    return novo_ambiente


# ──────────────────────────────────────────────
#  C R U D — READ
# ──────────────────────────────────────────────

def listar_ambientes(filtro_shopping=None, filtro_categoria=None, filtro_piso=None, filtro_status=None):
    dados = _carregar_json()
    ambientes = dados["ambientes"]
    if filtro_shopping:
        ambientes = [a for a in ambientes if a["shopping"] == filtro_shopping]
    if filtro_categoria:
        ambientes = [a for a in ambientes if filtro_categoria.lower() in a["categoria"].lower()]
    if filtro_piso:
        ambientes = [a for a in ambientes if a["piso"] == filtro_piso]
    if filtro_status:
        ambientes = [a for a in ambientes if a["status"] == filtro_status]
    return ambientes


def buscar_por_id(id_ambiente):
    dados = _carregar_json()
    for a in dados["ambientes"]:
        if a["id"] == id_ambiente:
            return a
    return None


def buscar_por_nome(nome_parcial):
    dados = _carregar_json()
    return [a for a in dados["ambientes"] if nome_parcial.lower() in a["nome"].lower()]


def listar_por_shopping_e_piso(shopping, piso):
    return listar_ambientes(filtro_shopping=shopping, filtro_piso=piso)


def obter_estatisticas():
    dados = _carregar_json()
    ambientes = dados["ambientes"]
    if not ambientes:
        return {"total": 0}
    stats = {
        "total": len(ambientes),
        "por_shopping": {},
        "por_categoria": {},
        "por_piso": {},
        "por_status": {},
        "com_camera": sum(1 for a in ambientes if a["tem_camera"]),
        "com_sensor": sum(1 for a in ambientes if a["tem_sensor_presenca"]),
        "total_cameras": sum(a["quantidade_cameras"] for a in ambientes),
    }
    for a in ambientes:
        for chave, campo in [("por_shopping","shopping"),("por_categoria","categoria"),("por_piso","piso"),("por_status","status")]:
            v = a.get(campo, "?")
            stats[chave][v] = stats[chave].get(v, 0) + 1
    return stats


# ──────────────────────────────────────────────
#  C R U D — UPDATE
# ──────────────────────────────────────────────

def atualizar_ambiente(id_ambiente, **campos):
    PROTEGIDOS = {"id", "criado_em"}
    dados = _carregar_json()
    for i, a in enumerate(dados["ambientes"]):
        if a["id"] == id_ambiente:
            for campo, valor in campos.items():
                if campo in PROTEGIDOS:
                    continue
                dados["ambientes"][i][campo] = valor
            dados["ambientes"][i]["atualizado_em"] = datetime.now().isoformat()
            _salvar_json(dados)
            print(f"[OK] Ambiente '{a['nome']}' atualizado.")
            return dados["ambientes"][i]
    print(f"[ERRO] Ambiente '{id_ambiente}' não encontrado.")
    return None


def alterar_status_ambiente(id_ambiente, novo_status):
    if novo_status not in STATUS_AMBIENTE:
        print(f"[ERRO] Status inválido. Use: {STATUS_AMBIENTE}")
        return None
    return atualizar_ambiente(id_ambiente, status=novo_status)


def registrar_visita_ambiente(id_ambiente):
    """Chamado pelo módulo de monitoramento quando detecta pessoa no ambiente."""
    dados = _carregar_json()
    for i, a in enumerate(dados["ambientes"]):
        if a["id"] == id_ambiente:
            dados["ambientes"][i]["total_visitas"] += 1
            dados["ambientes"][i]["atualizado_em"] = datetime.now().isoformat()
            _salvar_json(dados)
            return True
    return False


# ──────────────────────────────────────────────
#  C R U D — DELETE
# ──────────────────────────────────────────────

def deletar_ambiente(id_ambiente):
    dados = _carregar_json()
    antes = len(dados["ambientes"])
    dados["ambientes"] = [a for a in dados["ambientes"] if a["id"] != id_ambiente]
    if len(dados["ambientes"]) < antes:
        dados["metadados"]["total_ambientes"] = len(dados["ambientes"])
        _salvar_json(dados)
        print(f"[OK] Ambiente removido.")
        return True
    print(f"[ERRO] Ambiente não encontrado.")
    return False


# ──────────────────────────────────────────────
#  POPULAÇÃO INICIAL — TODOS OS AMBIENTES
#  Baseado nas lojas reais do shopping fornecidas
# ──────────────────────────────────────────────

def popular_ambientes_iniciais():
    """
    Popula o banco com todos os ambientes reais do shopping.
    Distribuídos entre os 4 shoppings da rede.
    Execute apenas uma vez para inicializar.
    """

    print("\n[INFO] Iniciando população de ambientes...\n")

    # ══════════════════════════════════════════
    #  SHOPPING 1 — Ambientes de Infraestrutura
    # ══════════════════════════════════════════

    infra_s1 = [
        # Entradas e Portarias
        ("Entrada Principal Norte",     "Segurança",          "Térreo",  "Norte",   "EP-01", 80,   500),
        ("Entrada Principal Sul",       "Segurança",          "Térreo",  "Sul",     "EP-02", 80,   500),
        ("Entrada de Serviço",          "Segurança",          "Térreo",  "Oeste",   "ES-01", 30,   50),
        ("Portaria de Funcionários",    "Segurança",          "Térreo",  "Oeste",   "PF-01", 20,   30),
        ("Portaria de Fornecedores",    "Segurança",          "Subsolo 1","Oeste",  "PF-02", 40,   20),
        # Estacionamentos
        ("Estacionamento Térreo",       "Estacionamento",     "Térreo",  None,      "EST-T", 8000, 300),
        ("Estacionamento Subsolo 1",    "Estacionamento",     "Subsolo 1",None,     "EST-S1",6000, 250),
        ("Estacionamento Subsolo 2",    "Estacionamento",     "Subsolo 2",None,     "EST-S2",6000, 250),
        ("Cabine de Controle Estac.",   "Estacionamento",     "Térreo",  None,      "CCE-01",10,   2),
        ("Vaga VIP / PCD",              "Estacionamento",     "Térreo",  None,      "VIP-01",200,  20),
        # Áreas Comuns
        ("Praça Central",               "Área Comum - Praça", "Térreo",  "Central", "PC-01", 600,  300),
        ("Praça de Eventos",            "Área Comum - Praça", "Piso L1", "Central", "PE-01", 400,  200),
        ("Corredor Ala A - Térreo",     "Área Comum - Corredor","Térreo","Ala A",   "CA-T",  500,  150),
        ("Corredor Ala B - Térreo",     "Área Comum - Corredor","Térreo","Ala B",   "CB-T",  500,  150),
        ("Corredor Ala A - L1",         "Área Comum - Corredor","Piso L1","Ala A",  "CA-L1", 500,  150),
        ("Corredor Ala B - L1",         "Área Comum - Corredor","Piso L1","Ala B",  "CB-L1", 500,  150),
        ("Corredor Ala A - L2",         "Área Comum - Corredor","Piso L2","Ala A",  "CA-L2", 500,  150),
        ("Banheiro Masc. Térreo Ala A", "Área Comum - Banheiro","Térreo","Ala A",  "BM-T-A",60,   15),
        ("Banheiro Fem. Térreo Ala A",  "Área Comum - Banheiro","Térreo","Ala A",  "BF-T-A",60,   15),
        ("Banheiro Masc. Térreo Ala B", "Área Comum - Banheiro","Térreo","Ala B",  "BM-T-B",60,   15),
        ("Banheiro Fem. Térreo Ala B",  "Área Comum - Banheiro","Térreo","Ala B",  "BF-T-B",60,   15),
        ("Banheiro PCD Térreo",         "Área Comum - Banheiro","Térreo","Central", "BPCD-T",15,   2),
        ("Fraldário",                   "Área Comum - Banheiro","Piso L1","Central","FRA-01",10,   3),
        ("Elevador Central 1",          "Área Comum - Elevador/Escada","Térreo","Central","EL-01",8,5),
        ("Elevador Central 2",          "Área Comum - Elevador/Escada","Térreo","Central","EL-02",8,5),
        ("Escada Rolante Ala A",        "Área Comum - Elevador/Escada","Térreo","Ala A","ER-A",15, 20),
        ("Escada Rolante Ala B",        "Área Comum - Elevador/Escada","Térreo","Ala B","ER-B",15, 20),
        # Administrativo
        ("Administração do Shopping",   "Administrativo",     "Piso L3", "Central", "ADM-01",200, 30),
        ("Central de Monitoramento CFTV","Administrativo",    "Subsolo 1","Central","MON-01",50,  10),
        ("Sala de Reuniões",            "Administrativo",     "Piso L3", "Central", "RNI-01",40,  20),
        ("Recursos Humanos",            "Administrativo",     "Piso L3", "Central", "RH-01", 30,  10),
        # Infraestrutura
        ("Casa de Máquinas",            "Infraestrutura",     "Subsolo 2","Oeste",  "CM-01", 100, 5),
        ("Central Elétrica",            "Infraestrutura",     "Subsolo 2","Oeste",  "CE-01", 60,  5),
        ("Depósito Geral",              "Infraestrutura",     "Subsolo 1","Oeste",  "DEP-01",200, 10),
        ("Coleta de Lixo / Reciclagem", "Infraestrutura",     "Subsolo 1","Oeste",  "LIX-01",80,  5),
    ]

    for nome, cat, piso, ala, num, area, cap in infra_s1:
        criar_ambiente(
            nome=nome, categoria=cat, shopping="Shopping 1",
            piso=piso, ala=ala, numero_loja=num,
            area_m2=area, capacidade_pessoas=cap,
            tem_camera=True, quantidade_cameras=2 if "Estacionamento" in cat else 1,
            tem_sensor_presenca=("Corredor" in cat or "Praça" in cat)
        )

    # ══════════════════════════════════════════
    #  LOJAS — distribuídas pelos 4 shoppings
    #  Baseado na lista real fornecida
    # ══════════════════════════════════════════

    # Formato: (nome, categoria, [subcategorias], shopping, piso, ala, num_loja, area, cap, tipo_publico)
    lojas = [

        # ── MODA FEMININA ──
        ("Água de Coco",        "Loja - Moda Feminina",    ["Moda praia"],                          "Shopping 1","Térreo",  "Ala A","L001",80, 30,"Feminino"),
        ("Any Any",             "Loja - Moda Feminina",    ["Moda íntima","Lingerie"],               "Shopping 1","Térreo",  "Ala A","L002",60, 25,"Feminino"),
        ("Brooksfield Donna",   "Loja - Moda Feminina",    ["Vestuário feminino"],                   "Shopping 1","Piso L1", "Ala A","L003",90, 30,"Feminino"),
        ("Carmen Steffens",     "Loja - Moda Feminina",    ["Calçados femininos","Bolsas"],          "Shopping 1","Piso L1", "Ala B","L004",100,35,"Feminino"),
        ("Criatiff",            "Loja - Moda Feminina",    ["Vestuário feminino"],                   "Shopping 1","Térreo",  "Ala B","L005",70, 25,"Feminino"),
        ("Dress To",            "Loja - Moda Feminina",    ["Vestuário feminino"],                   "Shopping 2","Térreo",  "Ala A","L006",80, 30,"Feminino"),
        ("Emme",                "Loja - Moda Feminina",    ["Vestuário feminino"],                   "Shopping 2","Piso L1", "Ala A","L007",70, 25,"Feminino"),
        ("Farm",                "Loja - Moda Feminina",    ["Vestuário feminino"],                   "Shopping 2","Térreo",  "Ala B","L008",100,35,"Feminino"),
        ("Farm Etc",            "Loja - Moda Feminina",    ["Vestuário feminino","Acessórios"],      "Shopping 2","Piso L1", "Ala B","L009",60, 20,"Feminino"),
        ("Fillity",             "Loja - Moda Feminina",    ["Vestuário feminino"],                   "Shopping 2","Térreo",  "Ala A","L010",70, 25,"Feminino"),
        ("Gregory",             "Loja - Moda Feminina",    ["Vestuário feminino"],                   "Shopping 3","Térreo",  "Ala A","L011",80, 30,"Feminino"),
        ("Hope",                "Loja - Moda Feminina",    ["Moda íntima","Lingerie"],               "Shopping 3","Piso L1", "Ala A","L012",60, 25,"Feminino"),
        ("Intimissimi",         "Loja - Moda Feminina",    ["Moda íntima","Lingerie"],               "Shopping 3","Térreo",  "Ala B","L013",70, 25,"Feminino"),
        ("Jogê",                "Loja - Moda Feminina",    ["Moda íntima","Lingerie"],               "Shopping 3","Piso L1", "Ala B","L014",60, 20,"Feminino"),
        ("Lança Perfume",       "Loja - Moda Feminina",    ["Vestuário feminino"],                   "Shopping 3","Térreo",  "Ala A","L015",80, 30,"Feminino"),
        ("Le Lis",              "Loja - Moda Feminina",    ["Vestuário feminino","Utensílios"],      "Shopping 4","Térreo",  "Ala A","L016",120,40,"Feminino"),
        ("Lez a Lez",           "Loja - Moda Feminina",    ["Vestuário feminino"],                   "Shopping 4","Piso L1", "Ala A","L017",80, 30,"Feminino"),
        ("Lizie",               "Loja - Moda Feminina",    ["Vestuário feminino"],                   "Shopping 4","Térreo",  "Ala B","L018",70, 25,"Feminino"),
        ("Lofty Style",         "Loja - Moda Feminina",    ["Vestuário feminino"],                   "Shopping 4","Piso L1", "Ala B","L019",80, 30,"Feminino"),
        ("Maria Filó",          "Loja - Moda Feminina",    ["Vestuário feminino"],                   "Shopping 1","Piso L2", "Ala A","L020",90, 30,"Feminino"),
        ("Oh Boy!",             "Loja - Moda Feminina",    ["Vestuário feminino"],                   "Shopping 2","Piso L2", "Ala A","L021",80, 30,"Feminino"),
        ("One Up",              "Loja - Moda Feminina",    ["Vestuário feminino"],                   "Shopping 3","Piso L2", "Ala A","L022",70, 25,"Feminino"),
        ("Patbo",               "Loja - Moda Feminina",    ["Vestuário feminino"],                   "Shopping 4","Piso L2", "Ala A","L023",90, 30,"Feminino"),
        ("Shoulder",            "Loja - Moda Feminina",    ["Vestuário feminino"],                   "Shopping 1","Piso L2", "Ala B","L024",100,35,"Feminino"),
        ("The Girls Boutique",  "Loja - Moda Feminina",    ["Vestuário feminino"],                   "Shopping 2","Piso L2", "Ala B","L025",80, 30,"Feminino"),
        ("Youcom",              "Loja - Moda Unissex",     ["Vestuário feminino","Vestuário masculino"],"Shopping 3","Térreo","Ala A","L026",120,40,"Todos"),
        ("Zinzane",             "Loja - Moda Feminina",    ["Vestuário feminino"],                   "Shopping 4","Térreo",  "Ala B","L027",80, 30,"Feminino"),
        ("Loungerie",           "Loja - Moda Feminina",    ["Moda íntima","Lingerie"],               "Shopping 1","Piso L1", "Ala A","L028",60, 20,"Feminino"),
        ("Lupo",                "Loja - Moda Feminina",    ["Moda íntima","Lingerie"],               "Shopping 2","Piso L1", "Ala A","L029",60, 20,"Feminino"),
        ("Puket",               "Loja - Moda Feminina",    ["Moda íntima","Lingerie"],               "Shopping 3","Piso L1", "Ala A","L030",50, 20,"Feminino"),
        ("Scala",               "Loja - Moda Feminina",    ["Moda íntima","Lingerie"],               "Shopping 4","Piso L1", "Ala A","L031",50, 20,"Feminino"),
        ("Cia Marítima",        "Loja - Moda Feminina",    ["Moda praia"],                           "Shopping 1","Térreo",  "Ala B","L032",70, 25,"Feminino"),
        ("Prayas",              "Loja - Moda Feminina",    ["Moda praia"],                           "Shopping 2","Térreo",  "Ala B","L033",70, 25,"Feminino"),
        ("Liz",                 "Loja - Moda Feminina",    ["Moda íntima","Lingerie"],               "Shopping 3","Piso L1", "Ala B","L034",60, 20,"Feminino"),

        # ── MODA MASCULINA ──
        ("Aramis",              "Loja - Moda Masculina",   ["Vestuário masculino"],                  "Shopping 1","Térreo",  "Ala B","L035",90, 30,"Masculino"),
        ("Boss",                "Loja - Moda Unissex",     ["Vestuário unissex"],                    "Shopping 1","Piso L1", "Ala B","L036",120,40,"Todos"),
        ("Brooksfield",         "Loja - Moda Masculina",   ["Vestuário masculino"],                  "Shopping 2","Térreo",  "Ala A","L037",90, 30,"Masculino"),
        ("Cuor di Leone",       "Loja - Moda Masculina",   ["Vestuário masculino","Calçados"],       "Shopping 2","Piso L1", "Ala A","L038",80, 25,"Masculino"),
        ("Docthos",             "Loja - Moda Masculina",   ["Vestuário masculino"],                  "Shopping 3","Térreo",  "Ala A","L039",80, 30,"Masculino"),
        ("Harry's",             "Loja - Moda Masculina",   ["Vestuário masculino"],                  "Shopping 3","Piso L1", "Ala A","L040",80, 30,"Masculino"),
        ("Highstil",            "Loja - Moda Masculina",   ["Vestuário masculino","Calçados"],       "Shopping 4","Térreo",  "Ala A","L041",80, 25,"Masculino"),
        ("Hugo",                "Loja - Moda Masculina",   ["Vestuário masculino"],                  "Shopping 4","Piso L1", "Ala A","L042",120,40,"Masculino"),
        ("Oficina Reserva",     "Loja - Moda Masculina",   ["Vestuário masculino"],                  "Shopping 1","Piso L2", "Ala A","L043",90, 30,"Masculino"),
        ("Reserva",             "Loja - Moda Masculina",   ["Vestuário masculino"],                  "Shopping 2","Piso L2", "Ala A","L044",100,35,"Masculino"),
        ("Shorts Co",           "Loja - Moda Masculina",   ["Vestuário masculino"],                  "Shopping 3","Piso L2", "Ala A","L045",70, 25,"Masculino"),
        ("Via Veneto",          "Loja - Moda Masculina",   ["Vestuário masculino"],                  "Shopping 4","Piso L2", "Ala A","L046",90, 30,"Masculino"),
        ("Vila Romana",         "Loja - Moda Masculina",   ["Vestuário masculino"],                  "Shopping 1","Piso L2", "Ala B","L047",90, 30,"Masculino"),
        ("VR Collezioni",       "Loja - Moda Masculina",   ["Vestuário masculino"],                  "Shopping 2","Piso L2", "Ala B","L048",90, 30,"Masculino"),
        ("Ad Life Style",       "Loja - Moda Masculina",   ["Vestuário masculino","Calçados"],       "Shopping 3","Térreo",  "Ala B","L049",80, 25,"Masculino"),

        # ── MODA UNISSEX / GRANDES REDES ──
        ("C&A",                 "Loja - Moda Unissex",     ["Vestuário geral","Calçados","Lingerie"],"Shopping 1","Térreo",  "Ala A","L050",800,200,"Todos"),
        ("Renner",              "Loja - Moda Unissex",     ["Vestuário geral","Calçados","Cosméticos"],"Shopping 2","Térreo","Ala A","L051",800,200,"Todos"),
        ("Riachuelo",           "Loja - Moda Unissex",     ["Vestuário geral","Calçados","Cama"],    "Shopping 3","Térreo",  "Ala A","L052",800,200,"Todos"),
        ("Zara",                "Loja - Moda Unissex",     ["Vestuário feminino","Vestuário masculino","Infantil"],"Shopping 4","Térreo","Ala A","L053",600,150,"Todos"),
        ("Calvin Klein",        "Loja - Moda Unissex",     ["Vestuário unissex","Lingerie"],         "Shopping 1","Piso L1", "Ala A","L054",200,50,"Todos"),
        ("Colcci",              "Loja - Moda Unissex",     ["Vestuário unissex"],                    "Shopping 2","Piso L1", "Ala A","L055",150,40,"Todos"),
        ("Damyller",            "Loja - Moda Unissex",     ["Vestuário unissex"],                    "Shopping 3","Piso L1", "Ala A","L056",120,35,"Todos"),
        ("Dane-se",             "Loja - Moda Unissex",     ["Vestuário unissex"],                    "Shopping 4","Piso L1", "Ala A","L057",100,30,"Todos"),
        ("Diesel",              "Loja - Moda Unissex",     ["Vestuário unissex"],                    "Shopping 1","Piso L1", "Ala B","L058",150,40,"Todos"),
        ("Dra. Cherie",         "Loja - Moda Unissex",     ["Vestuário unissex"],                    "Shopping 2","Piso L1", "Ala B","L059",100,30,"Todos"),
        ("Dudalina",            "Loja - Moda Unissex",     ["Vestuário unissex"],                    "Shopping 3","Piso L1", "Ala B","L060",150,40,"Todos"),
        ("Ellus",               "Loja - Moda Unissex",     ["Vestuário unissex"],                    "Shopping 4","Piso L1", "Ala B","L061",150,40,"Todos"),
        ("Forum",               "Loja - Moda Unissex",     ["Vestuário unissex"],                    "Shopping 1","Piso L2", "Ala A","L062",150,40,"Todos"),
        ("Hering Store",        "Loja - Moda Unissex",     ["Vestuário unissex","Acessórios"],       "Shopping 2","Piso L2", "Ala A","L063",200,50,"Todos"),
        ("Lacoste",             "Loja - Moda Unissex",     ["Vestuário unissex"],                    "Shopping 3","Piso L2", "Ala A","L064",150,40,"Todos"),
        ("Levi's",              "Loja - Moda Unissex",     ["Vestuário unissex"],                    "Shopping 4","Piso L2", "Ala A","L065",150,40,"Todos"),
        ("M. Officer",          "Loja - Moda Unissex",     ["Vestuário unissex"],                    "Shopping 1","Piso L2", "Ala B","L066",150,40,"Todos"),
        ("Oakley",              "Loja - Moda Unissex",     ["Vestuário unissex"],                    "Shopping 2","Piso L2", "Ala B","L067",100,30,"Todos"),
        ("Osklen",              "Loja - Moda Unissex",     ["Vestuário unissex","Calçados"],         "Shopping 3","Piso L2", "Ala B","L068",200,50,"Todos"),
        ("Richards",            "Loja - Moda Unissex",     ["Vestuário unissex","Moda praia"],       "Shopping 4","Piso L2", "Ala B","L069",150,40,"Todos"),
        ("The North Face",      "Loja - Moda Unissex",     ["Vestuário geral"],                      "Shopping 1","Térreo",  "Ala A","L070",200,50,"Todos"),
        ("Tommy Hilfiger",      "Loja - Moda Unissex",     ["Vestuário unissex"],                    "Shopping 2","Térreo",  "Ala A","L071",200,50,"Todos"),
        ("Maze",                "Loja - Moda Unissex",     ["Moda jovem","Esporte"],                 "Shopping 3","Térreo",  "Ala A","L072",100,30,"Jovem"),

        # ── MODA INFANTIL ──
        ("Brooksfield Junior",  "Loja - Moda Infantil",    ["Vestuário infantil"],                   "Shopping 1","Piso L1", "Ala A","L073",80, 30,"Infantil"),
        ("Carter's",            "Loja - Moda Infantil",    ["Vestuário infantil"],                   "Shopping 2","Piso L1", "Ala A","L074",80, 30,"Infantil"),
        ("Malwee Kids",         "Loja - Moda Infantil",    ["Vestuário infantil"],                   "Shopping 3","Piso L1", "Ala A","L075",80, 30,"Infantil"),
        ("Milon",               "Loja - Moda Infantil",    ["Vestuário infantil"],                   "Shopping 4","Piso L1", "Ala A","L076",80, 30,"Infantil"),
        ("Paola Da Vinci",      "Loja - Moda Infantil",    ["Vestuário infantil"],                   "Shopping 1","Piso L1", "Ala B","L077",70, 25,"Infantil"),
        ("Reserva Mini",        "Loja - Moda Infantil",    ["Vestuário infantil"],                   "Shopping 2","Piso L1", "Ala B","L078",70, 25,"Infantil"),

        # ── CALÇADOS ──
        ("Adidas",              "Loja - Calçados",         ["Calçados esportivos","Vestuário esporte"],"Shopping 1","Térreo","Ala A","L079",150,40,"Todos"),
        ("Anacapri",            "Loja - Calçados",         ["Calçados femininos","Acessórios"],      "Shopping 1","Piso L1", "Ala A","L080",80, 25,"Feminino"),
        ("Arezzo",              "Loja - Calçados",         ["Calçados femininos","Bolsas"],          "Shopping 2","Térreo",  "Ala A","L081",100,30,"Feminino"),
        ("Artwalk",             "Loja - Calçados",         ["Calçados esportivos"],                  "Shopping 2","Piso L1", "Ala A","L082",80, 25,"Todos"),
        ("Asics",               "Loja - Calçados",         ["Calçados esportivos","Artigos esportivos"],"Shopping 3","Térreo","Ala A","L083",100,30,"Todos"),
        ("Clube Melissa",       "Loja - Calçados",         ["Calçados femininos","Calçados infantis"],"Shopping 3","Piso L1","Ala A","L084",80,25,"Feminino"),
        ("CNS",                 "Loja - Calçados",         ["Calçados masculinos","Acessórios"],     "Shopping 4","Térreo",  "Ala A","L085",80, 25,"Masculino"),
        ("Conexão Original",    "Loja - Calçados",         ["Calçados esportivos"],                  "Shopping 4","Piso L1", "Ala A","L086",80, 25,"Todos"),
        ("Corello",             "Loja - Calçados",         ["Calçados femininos","Bolsas"],          "Shopping 1","Térreo",  "Ala B","L087",80, 25,"Feminino"),
        ("Crocs",               "Loja - Calçados",         ["Calçados femininos","Calçados infantis","Calçados masculinos"],"Shopping 2","Piso L1","Ala B","L088",70,25,"Todos"),
        ("CS Club",             "Loja - Calçados",         ["Calçados femininos","Acessórios"],      "Shopping 3","Térreo",  "Ala B","L089",70, 20,"Feminino"),
        ("Danki",               "Loja - Calçados",         ["Calçados esportivos"],                  "Shopping 4","Piso L1", "Ala B","L090",70, 20,"Todos"),
        ("Democrata",           "Loja - Calçados",         ["Calçados masculinos"],                  "Shopping 1","Piso L2", "Ala A","L091",80, 25,"Masculino"),
        ("Fascar",              "Loja - Calçados",         ["Calçados masculinos","Acessórios"],     "Shopping 2","Piso L2", "Ala A","L092",80, 25,"Masculino"),
        ("Havaianas",           "Loja - Calçados",         ["Calçados femininos","Calçados masculinos","Calçados infantis"],"Shopping 3","Térreo","Ala A","L093",80,25,"Todos"),
        ("Jorge Bischoff",      "Loja - Calçados",         ["Calçados femininos","Acessórios"],      "Shopping 4","Térreo",  "Ala A","L094",80, 25,"Feminino"),
        ("Kings Sneakers",      "Loja - Calçados",         ["Calçados esportivos"],                  "Shopping 1","Piso L1", "Ala A","L095",80, 25,"Jovem"),
        ("Luiza Barcelos",      "Loja - Calçados",         ["Calçados femininos"],                   "Shopping 2","Piso L1", "Ala A","L096",80, 25,"Feminino"),
        ("Luz da Lua",          "Loja - Calçados",         ["Calçados femininos"],                   "Shopping 3","Piso L1", "Ala A","L097",70, 20,"Feminino"),
        ("Ophicina Footwear",   "Loja - Calçados",         ["Calçados esportivos"],                  "Shopping 4","Piso L1", "Ala A","L098",80, 25,"Todos"),
        ("Outer",               "Loja - Calçados",         ["Calçados geral"],                       "Shopping 1","Térreo",  "Ala B","L099",80, 25,"Todos"),
        ("Pampili",             "Loja - Calçados",         ["Calçados infantis"],                    "Shopping 2","Térreo",  "Ala B","L100",60, 20,"Infantil"),
        ("Pezinho e Cia",       "Loja - Calçados",         ["Calçados infantis","Artigos infantis"], "Shopping 3","Piso L1", "Ala B","L101",60, 20,"Infantil"),
        ("Piccadilly",          "Loja - Calçados",         ["Calçados femininos","Acessórios"],      "Shopping 4","Térreo",  "Ala B","L102",80, 25,"Feminino"),
        ("Santa Lolla",         "Loja - Calçados",         ["Calçados femininos"],                   "Shopping 1","Piso L2", "Ala A","L103",80, 25,"Feminino"),
        ("Schutz",              "Loja - Calçados",         ["Calçados femininos","Acessórios"],      "Shopping 2","Piso L2", "Ala A","L104",80, 25,"Feminino"),
        ("Usaflex",             "Loja - Calçados",         ["Calçados femininos","Bolsas"],          "Shopping 3","Piso L2", "Ala A","L105",80, 25,"Feminino"),
        ("Uza Calçados",        "Loja - Calçados",         ["Calçados femininos"],                   "Shopping 4","Piso L2", "Ala A","L106",70, 20,"Feminino"),
        ("Vans",                "Loja - Calçados",         ["Calçados geral","Vestuário unissex"],   "Shopping 1","Térreo",  "Ala A","L107",100,30,"Jovem"),
        ("World Tennis",        "Loja - Esportes",         ["Artigos esportivos"],                   "Shopping 2","Térreo",  "Ala A","L108",150,40,"Todos"),
        ("Zeferino",            "Loja - Calçados",         ["Calçados femininos"],                   "Shopping 3","Térreo",  "Ala B","L109",70, 20,"Feminino"),

        # ── ESPORTES ──
        ("Adidas (Esporte)",    "Loja - Esportes",         ["Artigos esportivos","Vestuário esporte"],"Shopping 4","Térreo","Ala A","L110",200,50,"Todos"),
        ("Centauro",            "Loja - Esportes",         ["Artigos esportivos","Calçados esportivos"],"Shopping 1","Térreo","Ala A","L111",400,100,"Todos"),
        ("Grandes Torcidas",    "Loja - Esportes",         ["Artigos esportivos","Moda jovem"],      "Shopping 2","Piso L1", "Ala A","L112",100,30,"Todos"),
        ("Live",                "Loja - Esportes",         ["Artigos esportivos","Moda jovem"],      "Shopping 3","Piso L1", "Ala A","L113",100,30,"Feminino"),
        ("Nação Rubro Negra",   "Loja - Esportes",         ["Artigos esportivos"],                   "Shopping 4","Piso L1", "Ala A","L114",80, 25,"Todos"),
        ("New Era",             "Loja - Esportes",         ["Moda jovem","Esporte"],                 "Shopping 1","Piso L1", "Ala B","L115",60, 20,"Jovem"),
        ("Ramp",                "Loja - Esportes",         ["Artigos esportivos","Moda jovem"],      "Shopping 2","Piso L1", "Ala B","L116",80, 25,"Jovem"),
        ("Track & Field",       "Loja - Esportes",         ["Moda jovem","Esporte"],                 "Shopping 3","Piso L1", "Ala B","L117",120,35,"Todos"),

        # ── ACESSÓRIOS E BOLSAS ──
        ("Bagaggio",            "Loja - Acessórios e Bolsas",["Artigos para viagem","Acessórios"],  "Shopping 1","Piso L1", "Ala A","L118",80, 25,"Todos"),
        ("Baummer Semijoias",   "Loja - Acessórios e Bolsas",["Bijuterias","Acessórios","Bolsas"],  "Shopping 1","Térreo",  "Ala A","L119",50, 15,"Feminino"),
        ("Cynthia Pamplona",    "Loja - Acessórios e Bolsas",["Bijuterias"],                        "Shopping 2","Térreo",  "Ala A","L120",40, 15,"Feminino"),
        ("Inovathi",            "Loja - Acessórios e Bolsas",["Artigos para viagem","Acessórios"],  "Shopping 3","Piso L1", "Ala A","L121",60, 20,"Todos"),
        ("Isla",                "Loja - Acessórios e Bolsas",["Bolsas","Acessórios"],               "Shopping 4","Térreo",  "Ala A","L122",60, 20,"Feminino"),
        ("Kipling",             "Loja - Acessórios e Bolsas",["Artigos para viagem","Acessórios"],  "Shopping 1","Piso L1", "Ala B","L123",80, 25,"Todos"),
        ("Maria Dolores",       "Loja - Acessórios e Bolsas",["Bolsas","Acessórios"],               "Shopping 2","Piso L1", "Ala B","L124",60, 20,"Feminino"),
        ("Morana",              "Loja - Acessórios e Bolsas",["Bolsas","Acessórios"],               "Shopping 3","Térreo",  "Ala B","L125",60, 20,"Feminino"),
        ("Samsonite",           "Loja - Acessórios e Bolsas",["Artigos para viagem","Acessórios"],  "Shopping 4","Piso L1", "Ala B","L126",80, 25,"Todos"),
        ("Stanley Adventurego", "Loja - Acessórios e Bolsas",["Utensílios","Bolsas"],               "Shopping 1","Piso L2", "Ala A","L127",60, 20,"Todos"),
        ("Victor Hugo",         "Loja - Acessórios e Bolsas",["Acessórios","Diversos"],             "Shopping 2","Piso L2", "Ala A","L128",80, 25,"Feminino"),
        ("Rahra",               "Loja - Acessórios e Bolsas",["Bolsas","Joias","Acessórios"],       "Shopping 3","Piso L2", "Ala A","L129",60, 20,"Feminino"),

        # ── JOIAS E RELÓGIOS ──
        ("Estasi",              "Loja - Joias e Relógios",  ["Joias","Relógios"],                   "Shopping 1","Piso L1", "Ala A","L130",50, 15,"Todos"),
        ("HStern",              "Loja - Joias e Relógios",  ["Joias","Relógios"],                   "Shopping 2","Piso L1", "Ala A","L131",60, 15,"Todos"),
        ("Monte Carlo",         "Loja - Joias e Relógios",  ["Joias","Relógios"],                   "Shopping 3","Piso L1", "Ala A","L132",50, 15,"Todos"),
        ("Pandora",             "Loja - Joias e Relógios",  ["Joias","Relógios"],                   "Shopping 4","Piso L1", "Ala A","L133",50, 15,"Feminino"),
        ("Pedrart",             "Loja - Joias e Relógios",  ["Joias","Relógios"],                   "Shopping 1","Térreo",  "Ala A","L134",40, 10,"Todos"),
        ("Swarovski",           "Loja - Joias e Relógios",  ["Joias","Relógios"],                   "Shopping 2","Térreo",  "Ala A","L135",60, 15,"Todos"),
        ("Vallentina Joias",    "Loja - Joias e Relógios",  ["Joias","Relógios"],                   "Shopping 3","Térreo",  "Ala A","L136",50, 15,"Todos"),
        ("Vivara",              "Loja - Joias e Relógios",  ["Joias","Relógios"],                   "Shopping 4","Piso L1", "Ala A","L137",60, 15,"Todos"),
        ("Vivara Life",         "Loja - Joias e Relógios",  ["Joias","Relógios"],                   "Shopping 4","Piso L1", "Ala B","L138",50, 15,"Todos"),

        # ── ÓTICAS ──
        ("AC Brazil",           "Loja - Óticas",            ["Óticas"],                              "Shopping 1","Térreo",  "Ala A","L139",40, 15,"Todos"),
        ("Chilli Beans",        "Loja - Óticas",            ["Óticas","Óculos e relógios"],          "Shopping 1","Piso L1", "Ala A","L140",60, 20,"Todos"),
        ("Chilli Beans 2",      "Loja - Óticas",            ["Óticas","Diversos"],                   "Shopping 2","Térreo",  "Ala A","L141",60, 20,"Todos"),
        ("Oculum",              "Loja - Óticas",            ["Óticas"],                              "Shopping 2","Piso L1", "Ala A","L142",50, 15,"Todos"),
        ("Óptica Premium",      "Loja - Óticas",            ["Óticas"],                              "Shopping 3","Térreo",  "Ala A","L143",50, 15,"Todos"),
        ("Ótica Chilli Beans",  "Loja - Óticas",            ["Óticas","Joias"],                      "Shopping 3","Piso L1", "Ala A","L144",60, 20,"Todos"),
        ("Ótica Versátil Prime","Loja - Óticas",            ["Óticas"],                              "Shopping 4","Térreo",  "Ala A","L145",50, 15,"Todos"),
        ("Óticas Carol",        "Loja - Óticas",            ["Óticas"],                              "Shopping 4","Piso L1", "Ala A","L146",50, 15,"Todos"),
        ("Óticas Diniz Prime",  "Loja - Óticas",            ["Óticas","Óculos e relógios"],          "Shopping 1","Piso L2", "Ala A","L147",60, 20,"Todos"),
        ("Ray Ban",             "Loja - Óticas",            ["Óticas"],                              "Shopping 2","Piso L2", "Ala A","L148",60, 20,"Todos"),
        ("Sunglass Hut",        "Loja - Óticas",            ["Óticas"],                              "Shopping 3","Piso L2", "Ala A","L149",50, 15,"Todos"),

        # ── PERFUMARIA E COSMÉTICOS ──
        ("Adcos",               "Loja - Perfumaria e Cosméticos",["Cosméticos","Perfumaria"],        "Shopping 1","Piso L1", "Ala A","L150",60, 20,"Feminino"),
        ("Avatim",              "Loja - Perfumaria e Cosméticos",["Perfumaria","Cosméticos"],        "Shopping 1","Térreo",  "Ala A","L151",60, 20,"Todos"),
        ("B.Stories",           "Loja - Perfumaria e Cosméticos",["Perfumaria","Cosméticos"],        "Shopping 2","Piso L1", "Ala A","L152",60, 20,"Feminino"),
        ("Bel Cosméticos",      "Loja - Perfumaria e Cosméticos",["Cosméticos"],                    "Shopping 2","Térreo",  "Ala A","L153",50, 20,"Feminino"),
        ("Botocenter",          "Loja - Perfumaria e Cosméticos",["Estética"],                      "Shopping 3","Piso L1", "Ala A","L154",40, 10,"Feminino"),
        ("Creamy",              "Loja - Perfumaria e Cosméticos",["Cosméticos"],                    "Shopping 3","Térreo",  "Ala A","L155",50, 20,"Feminino"),
        ("Espumaria",           "Loja - Perfumaria e Cosméticos",["Cosméticos","Perfumaria"],        "Shopping 4","Piso L1", "Ala A","L156",60, 20,"Feminino"),
        ("Granado Pharmácias",  "Loja - Perfumaria e Cosméticos",["Perfumaria","Cosméticos"],        "Shopping 4","Térreo",  "Ala A","L157",80, 25,"Todos"),
        ("L'Occitane",          "Loja - Perfumaria e Cosméticos",["Cosméticos","Perfumaria"],        "Shopping 1","Piso L1", "Ala B","L158",80, 25,"Feminino"),
        ("L'Occitane Au Brésil","Loja - Perfumaria e Cosméticos",["Cosméticos","Perfumaria"],        "Shopping 2","Piso L1", "Ala B","L159",80, 25,"Feminino"),
        ("Lord Perfumaria",     "Loja - Perfumaria e Cosméticos",["Perfumaria","Cosméticos"],        "Shopping 3","Térreo",  "Ala B","L160",60, 20,"Todos"),
        ("MAC",                 "Loja - Perfumaria e Cosméticos",["Cosméticos"],                    "Shopping 4","Piso L1", "Ala B","L161",60, 20,"Feminino"),
        ("Me.Linda",            "Loja - Perfumaria e Cosméticos",["Cosméticos"],                    "Shopping 1","Térreo",  "Ala B","L162",50, 20,"Feminino"),
        ("Natura",              "Loja - Perfumaria e Cosméticos",["Cosméticos","Perfumaria"],        "Shopping 2","Piso L2", "Ala A","L163",80, 25,"Todos"),
        ("O Boticário",         "Loja - Perfumaria e Cosméticos",["Cosméticos","Perfumaria"],        "Shopping 3","Piso L2", "Ala A","L164",80, 25,"Todos"),
        ("Sephora",             "Loja - Perfumaria e Cosméticos",["Cosméticos","Perfumaria"],        "Shopping 4","Térreo",  "Ala A","L165",200,50,"Todos"),
        ("Shopping dos Cosméticos","Loja - Perfumaria e Cosméticos",["Cosméticos"],                 "Shopping 1","Piso L2", "Ala B","L166",60, 20,"Feminino"),
        ("Tania Bulhões",       "Loja - Perfumaria e Cosméticos",["Cosméticos"],                    "Shopping 2","Piso L2", "Ala B","L167",60, 20,"Feminino"),
        ("We Pink",             "Loja - Perfumaria e Cosméticos",["Cosméticos"],                    "Shopping 3","Piso L2", "Ala B","L168",50, 20,"Feminino"),
        ("Face Doctor",         "Loja - Perfumaria e Cosméticos",["Estética"],                      "Shopping 4","Piso L2", "Ala B","L169",40, 10,"Feminino"),

        # ── ELETRÔNICOS E TECNOLOGIA ──
        ("By Me",               "Loja - Eletrônicos e Tecnologia",["Celular","Acessórios","Games"],  "Shopping 1","Piso L1", "Ala A","L170",60, 20,"Todos"),
        ("Claro",               "Loja - Eletrônicos e Tecnologia",["Celular","Telefonia"],           "Shopping 1","Térreo",  "Ala A","L171",80, 25,"Todos"),
        ("Claro Vida Digital",  "Loja - Eletrônicos e Tecnologia",["Celular","Telefonia"],           "Shopping 2","Térreo",  "Ala A","L172",80, 25,"Todos"),
        ("Fast Shop",           "Loja - Eletrônicos e Tecnologia",["Eletrônicos","Informática"],     "Shopping 2","Piso L1", "Ala A","L173",200,50,"Todos"),
        ("Fujioka",             "Loja - Eletrônicos e Tecnologia",["Informática","Foto"],            "Shopping 3","Térreo",  "Ala A","L174",150,40,"Todos"),
        ("Go Case",             "Loja - Eletrônicos e Tecnologia",["Celular","Acessórios"],          "Shopping 3","Piso L1", "Ala A","L175",40, 15,"Todos"),
        ("iPlace",              "Loja - Eletrônicos e Tecnologia",["Informática","Eletrônicos"],     "Shopping 4","Térreo",  "Ala A","L176",150,40,"Todos"),
        ("Lig Celular",         "Loja - Eletrônicos e Tecnologia",["Celular","Acessórios"],          "Shopping 4","Piso L1", "Ala A","L177",50, 15,"Todos"),
        ("Samsung",             "Loja - Eletrônicos e Tecnologia",["Celular","Informática"],         "Shopping 1","Piso L1", "Ala B","L178",150,40,"Todos"),
        ("Talk",                "Loja - Eletrônicos e Tecnologia",["Celular","Acessórios"],          "Shopping 2","Piso L1", "Ala B","L179",50, 15,"Todos"),
        ("Tech Masters",        "Loja - Eletrônicos e Tecnologia",["Celular","Acessórios"],          "Shopping 3","Térreo",  "Ala B","L180",50, 15,"Todos"),
        ("TIM",                 "Loja - Eletrônicos e Tecnologia",["Celular","Telefonia"],           "Shopping 4","Térreo",  "Ala B","L181",80, 25,"Todos"),
        ("Vivo",                "Loja - Eletrônicos e Tecnologia",["Celular","Telefonia"],           "Shopping 1","Piso L2", "Ala A","L182",80, 25,"Todos"),
        ("Vivo 2",              "Loja - Eletrônicos e Tecnologia",["Celular","Telefonia"],           "Shopping 2","Piso L2", "Ala A","L183",80, 25,"Todos"),
        ("VX Case",             "Loja - Eletrônicos e Tecnologia",["Celular","Assistência técnica"], "Shopping 3","Piso L2", "Ala A","L184",50, 15,"Todos"),
        ("Xiaomi",              "Loja - Eletrônicos e Tecnologia",["Celular","Eletrônicos"],         "Shopping 4","Piso L2", "Ala A","L185",100,30,"Todos"),
        ("Made in Brazil Music","Loja - Eletrônicos e Tecnologia",["Instrumentos musicais"],         "Shopping 1","Piso L2", "Ala B","L186",200,50,"Todos"),

        # ── CASA E DECORAÇÃO ──
        ("Camicado",            "Loja - Casa e Decoração",  ["Cama","Mesa","Banho","Utensílios"],    "Shopping 1","Piso L1", "Ala A","L187",200,50,"Todos"),
        ("Casa Almeida",        "Loja - Casa e Decoração",  ["Cama","Mesa","Banho"],                 "Shopping 2","Piso L1", "Ala A","L188",150,40,"Todos"),
        ("Le Creuset",          "Loja - Casa e Decoração",  ["Utensílios"],                          "Shopping 3","Piso L1", "Ala A","L189",60, 20,"Todos"),
        ("Nespresso",           "Loja - Casa e Decoração",  ["Utensílios","Cafés"],                  "Shopping 4","Piso L1", "Ala A","L190",60, 20,"Todos"),
        ("Ortobom",             "Loja - Casa e Decoração",  ["Cama","Mesa","Banho"],                 "Shopping 1","Piso L2", "Ala A","L191",150,30,"Todos"),
        ("Tramontina",          "Loja - Casa e Decoração",  ["Utensílios"],                          "Shopping 2","Piso L2", "Ala A","L192",100,25,"Todos"),

        # ── BRINQUEDOS E INFANTIL ──
        ("Ciatoy",              "Loja - Brinquedos e Infantil",["Brinquedos"],                      "Shopping 1","Piso L1", "Ala B","L193",100,40,"Infantil"),
        ("Criamigos",           "Loja - Brinquedos e Infantil",["Brinquedos"],                      "Shopping 2","Piso L1", "Ala B","L194",100,40,"Infantil"),
        ("Panini",              "Loja - Brinquedos e Infantil",["Artigos esportivos","Brinquedos","Diversos"],"Shopping 3","Piso L1","Ala B","L195",60,25,"Infantil"),
        ("Pituquinhos Baby",    "Loja - Brinquedos e Infantil",["Artigos infantis"],                 "Shopping 4","Piso L1", "Ala B","L196",60, 20,"Infantil"),
        ("Ri Happy",            "Loja - Brinquedos e Infantil",["Brinquedos"],                      "Shopping 1","Piso L2", "Ala A","L197",200,60,"Infantil"),

        # ── LIVRARIA E PAPELARIA ──
        ("Leitura",             "Loja - Livraria e Papelaria",["Livraria","Papelaria"],              "Shopping 1","Piso L1", "Ala A","L198",200,60,"Todos"),
        ("Papel Craft",         "Loja - Livraria e Papelaria",["Papelaria","Acessórios"],            "Shopping 2","Térreo",  "Ala A","L199",80, 25,"Todos"),

        # ── PET SHOP ──
        ("Petz",                "Loja - Pet Shop",           ["Pet shop","Clínica veterinária"],     "Shopping 1","Piso L1", "Ala A","L200",300,50,"Todos"),

        # ── SERVIÇOS DE SAÚDE E BELEZA ──
        ("Alexandre Viana Hair","Serviços - Saúde e Beleza", ["Cabeleireiro","Manicure","Cosméticos"],"Shopping 1","Piso L2","Ala A","L201",80,20,"Feminino"),
        ("Arranjos Express",    "Serviços - Saúde e Beleza", ["Consertos","Costuras"],               "Shopping 2","Piso L1", "Ala A","L202",30, 5,"Todos"),
        ("Barbearia Elvis",     "Serviços - Saúde e Beleza", ["Barbearia","Tabacaria"],              "Shopping 3","Piso L1", "Ala A","L203",40, 10,"Masculino"),
        ("Doctor Feet",         "Serviços - Saúde e Beleza", ["Podologia","Estética"],               "Shopping 4","Piso L1", "Ala A","L204",40, 8,"Todos"),
        ("Unique Fitness Club", "Lazer - Academia",          ["Academia"],                           "Shopping 1","Piso L3", "Central","L205",800,100,"Todos"),

        # ── BANCOS E CÂMBIO ──
        ("BRB",                 "Serviços - Banco",          ["Banco"],                              "Shopping 1","Térreo",  "Ala A","L206",50, 20,"Todos"),
        ("Itaú Personnalité",   "Serviços - Banco",          ["Banco"],                              "Shopping 2","Térreo",  "Ala A","L207",60, 20,"Todos"),
        ("DayCâmbio",           "Serviços - Câmbio",         ["Câmbio"],                             "Shopping 3","Térreo",  "Ala A","L208",30, 10,"Todos"),
        ("Western Union",       "Serviços - Câmbio",         ["Câmbio"],                             "Shopping 4","Térreo",  "Ala A","L209",30, 10,"Todos"),
        ("CVC",                 "Serviços - Turismo",        ["Agência de turismo"],                 "Shopping 1","Piso L1", "Ala A","L210",40, 10,"Todos"),
        ("Drogasil",            "Serviços - Saúde e Beleza", ["Farmácia"],                           "Shopping 2","Térreo",  "Ala A","L211",100,30,"Todos"),

        # ── LAZER ──
        ("Kinoplex",            "Lazer - Cinema",            ["Cinema"],                             "Shopping 1","Piso L3", "Central","L212",1200,400,"Todos"),
        ("Boliche Striker",     "Lazer - Games e Diversões", ["Boliche"],                            "Shopping 2","Piso L3", "Central","L213",800,100,"Todos"),
        ("HotZone",             "Lazer - Games e Diversões", ["Diversões","Videogames"],             "Shopping 3","Piso L3", "Central","L214",600,150,"Jovem"),
        ("Parkclub",            "Lazer - Games e Diversões", ["Diversões","Videogames"],             "Shopping 4","Piso L3", "Central","L215",500,100,"Infantil"),
        ("Vila Trampolim",      "Lazer - Games e Diversões", ["Diversões"],                          "Shopping 1","Piso L3", "Central","L216",400,80,"Infantil"),
        ("60 Minutos Escape",   "Lazer - Outros",            ["Lazer"],                              "Shopping 2","Piso L3", "Central","L217",200,30,"Todos"),
        ("Stop & Go",           "Lazer - Outros",            ["Brinquedos","Lazer","Infantil"],      "Shopping 3","Piso L2", "Central","L218",200,40,"Infantil"),
        ("Baby Frota",          "Lazer - Outros",            ["Lazer","Outros serviços"],            "Shopping 4","Piso L2", "Central","L219",100,20,"Infantil"),
        ("P Diverte",           "Lazer - Outros",            ["Outros serviços"],                    "Shopping 1","Piso L2", "Central","L220",100,20,"Infantil"),

        # ── PRAÇA DE ALIMENTAÇÃO ──
        ("Praça de Alimentação S1","Alimentação - Outros",  ["Foodcourt"],                          "Shopping 1","Piso L2", "Central","PA-01",1500,400,"Todos"),
        ("Praça de Alimentação S2","Alimentação - Outros",  ["Foodcourt"],                          "Shopping 2","Piso L2", "Central","PA-02",1500,400,"Todos"),
        ("Praça de Alimentação S3","Alimentação - Outros",  ["Foodcourt"],                          "Shopping 3","Piso L2", "Central","PA-03",1500,400,"Todos"),
        ("Praça de Alimentação S4","Alimentação - Outros",  ["Foodcourt"],                          "Shopping 4","Piso L2", "Central","PA-04",1500,400,"Todos"),
        ("Empório Prime",       "Alimentação - Restaurante",["Delicatessen","Supermercado","Vegano"],"Shopping 1","Térreo",  "Ala A","L221",300,80,"Todos"),

        # ── SERVIÇOS DIVERSOS ──
        ("Agende-Lave",         "Serviços - Outros",        ["Lava rápido"],                        "Shopping 1","Subsolo 1","Oeste","L222",100,5,"Todos"),
        ("Park Serviços",       "Serviços - Outros",        ["Outros serviços"],                    "Shopping 2","Térreo",  "Ala A","L223",30, 5,"Todos"),
        ("Premier Renault",     "Serviços - Outros",        ["Diversos"],                           "Shopping 3","Térreo",  "Ala A","L224",200,20,"Todos"),
        ("Kimmi So",            "Loja - Outros",            ["Presentes","Souvenir"],               "Shopping 4","Piso L1", "Ala A","L225",40, 15,"Todos"),
        ("I Wanted",            "Loja - Outros",            ["Diversos"],                           "Shopping 1","Piso L1", "Ala A","L226",50, 15,"Todos"),
        ("Gabinete do Fio",     "Loja - Outros",            ["Acessórios","Vestuário feminino"],    "Shopping 2","Piso L1", "Ala A","L227",50, 15,"Feminino"),
    ]

    for dados_loja in lojas:
        nome, cat, subcats, shopping, piso, ala, num, area, cap, publico = dados_loja
        criar_ambiente(
            nome=nome,
            categoria=cat,
            subcategorias=subcats,
            shopping=shopping,
            piso=piso,
            ala=ala,
            numero_loja=num,
            area_m2=area,
            capacidade_pessoas=cap,
            tipo_publico=publico,
            tem_camera=True,
            quantidade_cameras=1,
            tem_sensor_presenca=True,
        )

    print("\n[CONCLUÍDO] Todos os ambientes foram cadastrados!")
    stats = obter_estatisticas()
    print(f"\nTotal de ambientes: {stats['total']}")
    print(f"Com câmera: {stats['com_camera']}")
    print(f"Com sensor de presença: {stats['com_sensor']}")
    print(f"Total de câmeras: {stats['total_cameras']}")
    print(f"\nPor shopping: {stats['por_shopping']}")


# ──────────────────────────────────────────────
#  MENU INTERATIVO
# ──────────────────────────────────────────────

def _exibir_ambiente(a):
    print("\n" + "─" * 55)
    print(f"  ID           : {a['id']}")
    print(f"  Nome         : {a['nome']}")
    print(f"  Categoria    : {a['categoria']}")
    print(f"  Shopping     : {a['shopping']}")
    print(f"  Localização  : {a['piso']} | {a.get('ala','') or 'Sem ala'} | Nº {a.get('numero_loja','?')}")
    print(f"  Área         : {a.get('area_m2','?')} m²  |  Capacidade: {a.get('capacidade_pessoas','?')} pessoas")
    print(f"  Câmeras      : {a.get('quantidade_cameras',0)} câmera(s)")
    print(f"  Sensor Pres. : {'Sim' if a.get('tem_sensor_presenca') else 'Não'}")
    print(f"  Público Alvo : {a.get('tipo_publico','Todos')}")
    print(f"  Status       : {a['status']}")
    print(f"  Total Visitas: {a.get('total_visitas',0)}")
    print("─" * 55)


def menu():
    while True:
        print("\n╔══════════════════════════════════╗")
        print("║  ShopControl — Gestão Ambientes  ║")
        print("╠══════════════════════════════════╣")
        print("║  1. Cadastrar novo ambiente       ║")
        print("║  2. Listar ambientes              ║")
        print("║  3. Buscar por nome               ║")
        print("║  4. Filtrar por shopping          ║")
        print("║  5. Filtrar por categoria         ║")
        print("║  6. Alterar status                ║")
        print("║  7. Ver estatísticas              ║")
        print("║  8. Popular dados iniciais        ║")
        print("║  0. Sair                          ║")
        print("╚══════════════════════════════════╝")

        opcao = input("\nEscolha: ").strip()

        if opcao == "1":
            print(f"\nCategorias: {', '.join(CATEGORIAS[:5])}... (e mais)")
            print(f"Pisos: {', '.join(PISOS)}")
            print(f"Shoppings: {', '.join(SHOPPINGS)}")
            nome     = input("Nome: ").strip()
            cat      = input("Categoria: ").strip()
            shop     = input("Shopping: ").strip()
            piso     = input("Piso: ").strip()
            ala      = input("Ala (Enter pular): ").strip() or None
            num      = input("Número da loja: ").strip() or None
            area     = input("Área m² (Enter pular): ").strip()
            cap      = input("Capacidade pessoas (Enter pular): ").strip()
            cameras  = input("Quantidade de câmeras [1]: ").strip()
            sensor   = input("Tem sensor de presença? (s/n) [s]: ").strip()
            criar_ambiente(
                nome=nome, categoria=cat, shopping=shop, piso=piso,
                ala=ala, numero_loja=num,
                area_m2=float(area) if area else None,
                capacidade_pessoas=int(cap) if cap else None,
                quantidade_cameras=int(cameras) if cameras else 1,
                tem_sensor_presenca=(sensor.lower() != "n")
            )

        elif opcao == "2":
            ambientes = listar_ambientes()
            print(f"\n── {len(ambientes)} ambiente(s) ──")
            for a in ambientes:
                _exibir_ambiente(a)

        elif opcao == "3":
            nome = input("Nome (parcial): ").strip()
            for a in buscar_por_nome(nome):
                _exibir_ambiente(a)

        elif opcao == "4":
            print(f"Shoppings: {', '.join(SHOPPINGS)}")
            shop = input("Shopping: ").strip()
            for a in listar_ambientes(filtro_shopping=shop):
                _exibir_ambiente(a)

        elif opcao == "5":
            cat = input("Categoria (parcial): ").strip()
            for a in listar_ambientes(filtro_categoria=cat):
                _exibir_ambiente(a)

        elif opcao == "6":
            id_a = input("ID do ambiente: ").strip()
            print(f"Status: {', '.join(STATUS_AMBIENTE)}")
            novo = input("Novo status: ").strip()
            alterar_status_ambiente(id_a, novo)

        elif opcao == "7":
            s = obter_estatisticas()
            print(f"\n── ESTATÍSTICAS ──")
            print(f"  Total          : {s['total']}")
            print(f"  Com câmera     : {s['com_camera']}")
            print(f"  Com sensor     : {s['com_sensor']}")
            print(f"  Total câmeras  : {s['total_cameras']}")
            print(f"  Por shopping   : {s['por_shopping']}")
            print(f"  Por status     : {s['por_status']}")

        elif opcao == "8":
            conf = input("Isso vai popular o banco com todos os ambientes. Confirma? (s/n): ").strip()
            if conf.lower() == "s":
                popular_ambientes_iniciais()

        elif opcao == "0":
            print("Até logo!")
            break


if __name__ == "__main__":
    menu()