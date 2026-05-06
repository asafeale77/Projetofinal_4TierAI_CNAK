"""
╔══════════════════════════════════════════════════════════════════╗
║         MÓDULO DE MONITORAMENTO DE ESTACIONAMENTO                ║
║              ShopControl - Rede de Shoppings                     ║
╚══════════════════════════════════════════════════════════════════╝

Este módulo monitora TUDO que acontece no estacionamento:
  - Entrada e saída de veículos (leitura de placas LPR)
  - Ocupação de vagas em tempo real
  - Comportamentos suspeitos por câmeras IA
  - Veículos na lista de atenção
  - Tempo de permanência
  - Controle de vagas especiais (PCD, idoso, VIP, elétrico)
  - Histórico completo por placa
  - Relatórios e estatísticas para o dashboard

Banco de dados: dados/monitoramento_estacionamento.json
"""

import json
import os
import uuid
import random
import string
from datetime import datetime, timedelta


# ─────────────────────────────────────────────
#  CONFIGURAÇÃO
# ─────────────────────────────────────────────

PASTA_DADOS          = os.path.join(os.path.dirname(__file__), "..", "dados")
ARQUIVO              = os.path.join(PASTA_DADOS, "monitoramento_estacionamento.json")
ARQUIVO_USUARIOS     = os.path.join(PASTA_DADOS, "usuarios.json")
ARQUIVO_AMBIENTES    = os.path.join(PASTA_DADOS, "ambientes.json")
ARQUIVO_EQUIPAMENTOS = os.path.join(PASTA_DADOS, "equipamentos.json")


# ─────────────────────────────────────────────
#  TIPOS DE EVENTOS DO ESTACIONAMENTO
# ─────────────────────────────────────────────

TIPOS_EVENTO = {

    # ── Entrada e Saída ───────────────────────
    "veiculo_entrou":               {"nivel": "info",    "descricao": "Veículo entrou no estacionamento"},
    "veiculo_saiu":                 {"nivel": "info",    "descricao": "Veículo saiu do estacionamento"},
    "veiculo_sem_saida_registrada": {"nivel": "atencao", "descricao": "Veículo presente sem saída registrada (possível falha de leitura)"},
    "veiculo_permanencia_longa":    {"nivel": "atencao", "descricao": "Veículo com permanência acima do tempo esperado"},
    "veiculo_pernoite":             {"nivel": "atencao", "descricao": "Veículo identificado em pernoite no estacionamento"},

    # ── Leitura de Placas ─────────────────────
    "placa_lida_entrada":           {"nivel": "info",    "descricao": "Placa lida com sucesso na entrada"},
    "placa_lida_saida":             {"nivel": "info",    "descricao": "Placa lida com sucesso na saída"},
    "placa_nao_reconhecida":        {"nivel": "atencao", "descricao": "Placa não reconhecida pelo leitor LPR"},
    "placa_bloqueada":              {"nivel": "critico", "descricao": "Placa na lista de bloqueio detectada"},
    "placa_lista_atencao":          {"nivel": "critico", "descricao": "Placa na lista de atenção detectada"},
    "placa_veiculo_furtado":        {"nivel": "critico", "descricao": "Placa de veículo com boletim de furto/roubo"},
    "placa_adulterada":             {"nivel": "critico", "descricao": "Possível adulteração de placa detectada (IA)"},
    "placa_clonada_suspeita":       {"nivel": "critico", "descricao": "Suspeita de placa clonada — mesmo veículo em locais distintos"},
    "placa_diplomatica":            {"nivel": "atencao", "descricao": "Veículo com placa diplomática detectado"},
    "placa_oficial":                {"nivel": "info",    "descricao": "Veículo oficial/governo detectado"},

    # ── Vagas ─────────────────────────────────
    "vaga_ocupada":                 {"nivel": "info",    "descricao": "Vaga ocupada por veículo"},
    "vaga_liberada":                {"nivel": "info",    "descricao": "Vaga liberada"},
    "vaga_pcd_uso_indevido":        {"nivel": "critico", "descricao": "Vaga PCD ocupada por veículo sem credencial"},
    "vaga_idoso_uso_indevido":      {"nivel": "atencao", "descricao": "Vaga idoso ocupada por veículo sem credencial"},
    "vaga_vip_uso_indevido":        {"nivel": "atencao", "descricao": "Vaga VIP ocupada por não credenciado"},
    "vaga_eletrico_uso_indevido":   {"nivel": "atencao", "descricao": "Vaga de veículo elétrico usada por não elétrico"},
    "estacionamento_lotado":        {"nivel": "atencao", "descricao": "Estacionamento atingiu capacidade máxima"},
    "estacionamento_quase_lotado":  {"nivel": "info",    "descricao": "Estacionamento com mais de 80% de ocupação"},
    "vagas_criticas":               {"nivel": "atencao", "descricao": "Menos de 10 vagas disponíveis"},

    # ── Comportamentos Suspeitos (IA) ─────────
    "pessoa_entre_carros_suspeita": {"nivel": "atencao", "descricao": "Pessoa entre veículos com comportamento suspeito"},
    "furto_veiculo_suspeito":       {"nivel": "critico", "descricao": "Possível tentativa de furto de veículo (IA)"},
    "furto_carga_suspeito":         {"nivel": "critico", "descricao": "Possível furto de carga/pertences no veículo"},
    "vandalismo_veiculo":           {"nivel": "critico", "descricao": "Possível vandalismo em veículo detectado"},
    "pessoa_agachada_veiculo":      {"nivel": "atencao", "descricao": "Pessoa agachada próxima a veículo (suspeito)"},
    "veiculo_abandonado":           {"nivel": "atencao", "descricao": "Veículo possivelmente abandonado (tempo excessivo)"},
    "movimentacao_noturna":         {"nivel": "atencao", "descricao": "Movimentação suspeita no período noturno"},
    "acesso_area_restrita_estac":   {"nivel": "critico", "descricao": "Acesso não autorizado à área restrita do estacionamento"},
    "pessoa_dormindo_veiculo":      {"nivel": "atencao", "descricao": "Pessoa dormindo dentro de veículo"},
    "briga_estacionamento":         {"nivel": "critico", "descricao": "Possível briga no estacionamento detectada"},
    "pessoa_caida_estac":           {"nivel": "critico", "descricao": "Pessoa caída no estacionamento detectada"},
    "veiculo_manobra_suspeita":     {"nivel": "atencao", "descricao": "Veículo realizando manobras suspeitas (IA)"},
    "veiculo_velocidade_alta":      {"nivel": "atencao", "descricao": "Veículo em velocidade acima do permitido"},
    "veiculo_contramao":            {"nivel": "atencao", "descricao": "Veículo na contramão dentro do estacionamento"},
    "veiculo_fuga":                 {"nivel": "critico", "descricao": "Veículo em fuga — passou cancela sem pagar/autorizar"},

    # ── Cancelas e Equipamentos ───────────────
    "cancela_forcada":              {"nivel": "critico", "descricao": "Tentativa de forçar a cancela"},
    "cancela_falha":                {"nivel": "atencao", "descricao": "Cancela com falha de operação"},
    "cancela_aberta_sem_veiculo":   {"nivel": "atencao", "descricao": "Cancela aberta sem veículo detectado"},
    "leitor_placa_offline":         {"nivel": "atencao", "descricao": "Leitor de placas ficou offline"},
    "leitor_placa_online":          {"nivel": "info",    "descricao": "Leitor de placas voltou online"},
    "sensor_vaga_falha":            {"nivel": "atencao", "descricao": "Sensor de vaga com falha"},
    "camera_estac_offline":         {"nivel": "atencao", "descricao": "Câmera do estacionamento offline"},
    "interfone_acionado":           {"nivel": "info",    "descricao": "Interfone de emergência acionado"},

    # ── Pagamento ─────────────────────────────
    "pagamento_realizado":          {"nivel": "info",    "descricao": "Pagamento de estacionamento realizado"},
    "pagamento_recusado":           {"nivel": "atencao", "descricao": "Pagamento recusado no totem"},
    "totem_falha":                  {"nivel": "atencao", "descricao": "Totem de pagamento com falha"},
    "saida_sem_pagamento":          {"nivel": "critico", "descricao": "Veículo saiu sem efetuar pagamento"},
    "mensalista_acesso":            {"nivel": "info",    "descricao": "Acesso de mensalista registrado"},
    "mensalista_vencido":           {"nivel": "atencao", "descricao": "Mensalista com contrato vencido tentou acessar"},

    # ── Emergência ────────────────────────────
    "fumaca_estac":                 {"nivel": "critico", "descricao": "Fumaça detectada no estacionamento"},
    "incendio_veiculo":             {"nivel": "critico", "descricao": "Possível incêndio em veículo detectado (câmera térmica)"},
    "gas_estac":                    {"nivel": "critico", "descricao": "Gás detectado no estacionamento"},
    "alagamento_estac":             {"nivel": "critico", "descricao": "Sensor de alagamento ativado no estacionamento"},
    "falta_energia_estac":          {"nivel": "critico", "descricao": "Falta de energia no estacionamento"},
    "sirene_emergencia":            {"nivel": "critico", "descricao": "Sirene de emergência acionada"},
}

# ─────────────────────────────────────────────
#  CONFIGURAÇÕES DOS SHOPPINGS
# ─────────────────────────────────────────────

SHOPPINGS = ["Shopping 1", "Shopping 2", "Shopping 3", "Shopping 4"]

# Capacidade e divisão de vagas por shopping
CONFIG_SHOPPINGS = {
    "Shopping 1": {
        "total_vagas": 800,
        "vagas_pcd": 32,
        "vagas_idoso": 24,
        "vagas_vip": 20,
        "vagas_eletrico": 10,
        "vagas_moto": 40,
        "andares": ["Térreo", "1º Subsolo", "2º Subsolo"],
        "cancelas_entrada": ["Cancela Norte", "Cancela Sul"],
        "cancelas_saida": ["Cancela Norte Saída", "Cancela Sul Saída"]
    },
    "Shopping 2": {
        "total_vagas": 650,
        "vagas_pcd": 26,
        "vagas_idoso": 20,
        "vagas_vip": 15,
        "vagas_eletrico": 8,
        "vagas_moto": 30,
        "andares": ["Térreo", "1º Subsolo"],
        "cancelas_entrada": ["Cancela Principal", "Cancela Lateral"],
        "cancelas_saida": ["Cancela Principal Saída", "Cancela Lateral Saída"]
    },
    "Shopping 3": {
        "total_vagas": 1000,
        "vagas_pcd": 40,
        "vagas_idoso": 30,
        "vagas_vip": 25,
        "vagas_eletrico": 15,
        "vagas_moto": 50,
        "andares": ["Térreo", "1º Subsolo", "2º Subsolo", "3º Subsolo"],
        "cancelas_entrada": ["Cancela A", "Cancela B", "Cancela C"],
        "cancelas_saida": ["Cancela A Saída", "Cancela B Saída", "Cancela C Saída"]
    },
    "Shopping 4": {
        "total_vagas": 500,
        "vagas_pcd": 20,
        "vagas_idoso": 16,
        "vagas_vip": 10,
        "vagas_eletrico": 6,
        "vagas_moto": 25,
        "andares": ["Térreo", "1º Subsolo"],
        "cancelas_entrada": ["Cancela Única Entrada"],
        "cancelas_saida": ["Cancela Única Saída"]
    }
}

TIPOS_VEICULO = ["carro", "moto", "caminhonete", "van", "caminhão", "ônibus"]
TIPOS_VAGA    = ["comum", "pcd", "idoso", "vip", "eletrico", "moto", "carga"]
PERIODOS_DIA  = {
    "madrugada": (0, 6),
    "manha":     (6, 12),
    "tarde":     (12, 18),
    "noite":     (18, 24),
}
NIVEIS_ALERTA = ["info", "atencao", "critico"]


# ─────────────────────────────────────────────
#  FUNÇÕES AUXILIARES
# ─────────────────────────────────────────────

def _garantir_pasta():
    if not os.path.exists(PASTA_DADOS):
        os.makedirs(PASTA_DADOS)


def _carregar():
    _garantir_pasta()
    if not os.path.exists(ARQUIVO):
        dados = {
            "metadados": {
                "criado_em": datetime.now().isoformat(),
                "ultima_atualizacao": datetime.now().isoformat(),
                "total_eventos": 0,
                "versao": "1.0"
            },
            "eventos": [],
            "alertas_ativos": [],
            "veiculos_presentes": {},   # placa → dados do veículo
            "ocupacao_atual": {},       # shopping → contagem atual
            "historico_placas": {},     # placa → lista de visitas
            "lista_bloqueio": [],       # placas bloqueadas
            "lista_atencao": [],        # placas em observação
        }
        _salvar(dados)
        print("✅ Banco 'monitoramento_estacionamento.json' criado com sucesso!")
        return dados
    with open(ARQUIVO, "r", encoding="utf-8") as f:
        return json.load(f)


def _salvar(dados):
    _garantir_pasta()
    dados["metadados"]["ultima_atualizacao"] = datetime.now().isoformat()
    dados["metadados"]["total_eventos"] = len(dados.get("eventos", []))
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)


def _gerar_id():
    return "EST-" + ''.join(random.choices(string.digits, k=8))


def _periodo_do_dia(hora=None):
    if hora is None:
        hora = datetime.now().hour
    for periodo, (inicio, fim) in PERIODOS_DIA.items():
        if inicio <= hora < fim:
            return periodo
    return "noite"


def _carregar_usuarios():
    if not os.path.exists(ARQUIVO_USUARIOS):
        return []
    with open(ARQUIVO_USUARIOS, "r", encoding="utf-8") as f:
        return json.load(f).get("usuarios", [])


def _buscar_usuario_por_placa(placa: str):
    """Busca usuário cadastrado pela placa do veículo."""
    for u in _carregar_usuarios():
        veiculo = u.get("veiculo", {})
        if isinstance(veiculo, dict):
            if veiculo.get("placa", "").upper() == placa.upper():
                return u
        elif isinstance(veiculo, list):
            for v in veiculo:
                if v.get("placa", "").upper() == placa.upper():
                    return u
    return None


def _formatar_duracao(minutos: int) -> str:
    if minutos < 60:
        return f"{minutos} min"
    horas = minutos // 60
    mins  = minutos % 60
    if horas < 24:
        return f"{horas}h {mins}min"
    dias = horas // 24
    hrs  = horas % 24
    return f"{dias}d {hrs}h {mins}min"


def _gerar_placa_br() -> str:
    """Gera uma placa brasileira aleatória (Mercosul ou antiga)."""
    if random.random() > 0.5:
        # Mercosul: ABC1D23
        letras = ''.join(random.choices(string.ascii_uppercase, k=3))
        num1   = random.randint(0, 9)
        letra2 = random.choice(string.ascii_uppercase)
        num2   = random.randint(10, 99)
        return f"{letras}{num1}{letra2}{num2}"
    else:
        # Antiga: ABC-1234
        letras = ''.join(random.choices(string.ascii_uppercase, k=3))
        nums   = ''.join(random.choices(string.digits, k=4))
        return f"{letras}-{nums}"


# ─────────────────────────────────────────────
#  LISTA DE BLOQUEIO E ATENÇÃO
# ─────────────────────────────────────────────

def adicionar_placa_bloqueio(placa: str, motivo: str, adicionado_por: str) -> bool:
    """Adiciona uma placa à lista de bloqueio."""
    dados = _carregar()
    placa = placa.upper()
    for p in dados["lista_bloqueio"]:
        if p["placa"] == placa:
            print(f"⚠️  Placa '{placa}' já está na lista de bloqueio.")
            return False
    dados["lista_bloqueio"].append({
        "placa": placa,
        "motivo": motivo,
        "adicionado_por": adicionado_por,
        "data": datetime.now().isoformat()
    })
    _salvar(dados)
    print(f"✅ Placa '{placa}' adicionada à lista de bloqueio.")
    return True


def adicionar_placa_atencao(placa: str, motivo: str, adicionado_por: str) -> bool:
    """Adiciona uma placa à lista de atenção."""
    dados = _carregar()
    placa = placa.upper()
    for p in dados["lista_atencao"]:
        if p["placa"] == placa:
            print(f"⚠️  Placa '{placa}' já está na lista de atenção.")
            return False
    dados["lista_atencao"].append({
        "placa": placa,
        "motivo": motivo,
        "adicionado_por": adicionado_por,
        "data": datetime.now().isoformat()
    })
    _salvar(dados)
    print(f"✅ Placa '{placa}' adicionada à lista de atenção.")
    return True


def remover_placa_lista(placa: str, lista: str = "bloqueio") -> bool:
    """Remove uma placa da lista de bloqueio ou atenção."""
    dados = _carregar()
    placa = placa.upper()
    chave = f"lista_{lista}"
    antes = len(dados[chave])
    dados[chave] = [p for p in dados[chave] if p["placa"] != placa]
    if len(dados[chave]) < antes:
        _salvar(dados)
        print(f"✅ Placa '{placa}' removida da lista de {lista}.")
        return True
    print(f"⚠️  Placa '{placa}' não encontrada na lista de {lista}.")
    return False


def _verificar_placa(placa: str, dados: dict) -> str:
    """
    Verifica o status de uma placa.
    Retorna: 'bloqueada', 'atencao', ou 'normal'
    """
    placa = placa.upper()
    for p in dados.get("lista_bloqueio", []):
        if p["placa"] == placa:
            return "bloqueada"
    for p in dados.get("lista_atencao", []):
        if p["placa"] == placa:
            return "atencao"
    return "normal"


# ─────────────────────────────────────────────
#  REGISTRAR EVENTO
# ─────────────────────────────────────────────

def registrar_evento(
    tipo_evento: str,
    shopping: str,
    placa: str = "",
    tipo_veiculo: str = "carro",
    cancela: str = "",
    andar: str = "",
    numero_vaga: str = "",
    tipo_vaga: str = "comum",
    id_camera: str = "",
    confianca_ia: float = None,
    descricao_extra: str = "",
    dados_pagamento: dict = None,
    usuario_id: str = ""
) -> dict:
    """
    Registra um evento de monitoramento do estacionamento.

    Parâmetros:
        tipo_evento     → Tipo do evento (ver TIPOS_EVENTO)
        shopping        → Shopping onde ocorreu
        placa           → Placa do veículo (se aplicável)
        tipo_veiculo    → Tipo do veículo (carro, moto, etc.)
        cancela         → Nome da cancela (entrada/saída)
        andar           → Andar do estacionamento
        numero_vaga     → Número ou identificação da vaga
        tipo_vaga       → Tipo da vaga (comum, pcd, idoso, vip...)
        id_camera       → ID da câmera que detectou
        confianca_ia    → Confiança da leitura IA (0-100)
        descricao_extra → Texto livre adicional
        dados_pagamento → Dados do pagamento se aplicável
        usuario_id      → ID do usuário cadastrado (se identificado)
    """
    if tipo_evento not in TIPOS_EVENTO:
        print(f"⚠️  Tipo de evento '{tipo_evento}' inválido.")
        return None

    if shopping not in SHOPPINGS:
        print(f"⚠️  Shopping '{shopping}' inválido.")
        return None

    info    = TIPOS_EVENTO[tipo_evento]
    agora   = datetime.now()
    placa   = placa.upper() if placa else ""
    dados   = _carregar()

    # Verifica status da placa
    status_placa = _verificar_placa(placa, dados) if placa else "normal"

    # Busca usuário pela placa
    usuario = _buscar_usuario_por_placa(placa) if placa else None

    # Calcula tempo de permanência se for saída
    tempo_permanencia_min = None
    if tipo_evento == "veiculo_saiu" and placa in dados["veiculos_presentes"]:
        entrada = dados["veiculos_presentes"][placa].get("entrada_em")
        if entrada:
            delta = agora - datetime.fromisoformat(entrada)
            tempo_permanencia_min = int(delta.total_seconds() / 60)

    evento = {
        "id":                   _gerar_id(),
        "tipo":                 tipo_evento,
        "nivel_alerta":         info["nivel"],
        "descricao":            info["descricao"],
        "descricao_extra":      descricao_extra,

        # ── Localização ──
        "shopping":             shopping,
        "cancela":              cancela,
        "andar":                andar,
        "numero_vaga":          numero_vaga,
        "tipo_vaga":            tipo_vaga,

        # ── Veículo ──
        "placa":                placa,
        "tipo_veiculo":         tipo_veiculo,
        "status_placa":         status_placa,

        # ── Usuário identificado ──
        "usuario_id":           usuario_id or (usuario["id"] if usuario else ""),
        "usuario_nome":         usuario["nome"] if usuario else "",
        "usuario_perfil":       usuario.get("perfil", "") if usuario else "",

        # ── Tempo ──
        "data_hora":            agora.isoformat(),
        "data":                 agora.strftime("%Y-%m-%d"),
        "hora":                 agora.strftime("%H:%M:%S"),
        "periodo_dia":          _periodo_do_dia(agora.hour),
        "dia_semana":           agora.strftime("%A"),
        "tempo_permanencia_min":tempo_permanencia_min,

        # ── Detecção ──
        "id_camera":            id_camera,
        "confianca_ia":         confianca_ia,

        # ── Pagamento ──
        "dados_pagamento":      dados_pagamento or {},

        # ── Resolução ──
        "resolvido":            False,
        "resolvido_em":         None,
        "resolvido_por":        None,
        "acao_tomada":          None,
    }

    dados["eventos"].append(evento)

    # ── Atualiza veículos presentes ──
    if tipo_evento == "veiculo_entrou" and placa:
        dados["veiculos_presentes"][placa] = {
            "placa":        placa,
            "tipo_veiculo": tipo_veiculo,
            "shopping":     shopping,
            "andar":        andar,
            "cancela":      cancela,
            "entrada_em":   agora.isoformat(),
            "status_placa": status_placa,
            "usuario_nome": usuario["nome"] if usuario else ""
        }
    elif tipo_evento == "veiculo_saiu" and placa in dados["veiculos_presentes"]:
        del dados["veiculos_presentes"][placa]

    # ── Atualiza ocupação atual por shopping ──
    if shopping not in dados["ocupacao_atual"]:
        cfg = CONFIG_SHOPPINGS.get(shopping, {})
        dados["ocupacao_atual"][shopping] = {
            "veiculos_presentes": 0,
            "total_vagas": cfg.get("total_vagas", 500),
            "vagas_livres": cfg.get("total_vagas", 500),
            "percentual_ocupacao": 0.0
        }
    if tipo_evento == "veiculo_entrou":
        dados["ocupacao_atual"][shopping]["veiculos_presentes"] += 1
    elif tipo_evento == "veiculo_saiu":
        dados["ocupacao_atual"][shopping]["veiculos_presentes"] = max(
            0, dados["ocupacao_atual"][shopping]["veiculos_presentes"] - 1
        )
    presentes = dados["ocupacao_atual"][shopping]["veiculos_presentes"]
    total     = dados["ocupacao_atual"][shopping]["total_vagas"]
    dados["ocupacao_atual"][shopping]["vagas_livres"] = max(0, total - presentes)
    dados["ocupacao_atual"][shopping]["percentual_ocupacao"] = round(presentes / total * 100, 1)

    # ── Atualiza histórico da placa ──
    if placa:
        if placa not in dados["historico_placas"]:
            dados["historico_placas"][placa] = []
        dados["historico_placas"][placa].append({
            "tipo":      tipo_evento,
            "shopping":  shopping,
            "data_hora": agora.isoformat(),
            "andar":     andar,
            "cancela":   cancela
        })

    # ── Alertas automáticos por status da placa ──
    nivel_final = info["nivel"]
    if placa and status_placa == "bloqueada" and nivel_final != "critico":
        nivel_final = "critico"
        evento["nivel_alerta"] = "critico"
    elif placa and status_placa == "atencao" and nivel_final == "info":
        nivel_final = "atencao"
        evento["nivel_alerta"] = "atencao"

    # ── Adiciona aos alertas ativos se necessário ──
    if nivel_final in ["atencao", "critico"]:
        dados["alertas_ativos"].append({
            "id_evento":  evento["id"],
            "tipo":       tipo_evento,
            "descricao":  info["descricao"],
            "nivel":      nivel_final,
            "shopping":   shopping,
            "placa":      placa,
            "cancela":    cancela,
            "data_hora":  agora.isoformat(),
            "resolvido":  False,
        })
        if nivel_final == "critico":
            print(f"🚨 ALERTA CRÍTICO: {info['descricao']} | Placa: {placa or 'N/A'} | {shopping}")
        else:
            print(f"⚠️  ATENÇÃO: {info['descricao']} | Placa: {placa or 'N/A'} | {shopping}")

    _salvar(dados)
    return evento


# ─────────────────────────────────────────────
#  LISTAR / BUSCAR
# ─────────────────────────────────────────────

def listar_eventos(
    filtro_shopping: str = None,
    filtro_nivel: str = None,
    filtro_tipo: str = None,
    filtro_placa: str = None,
    filtro_data: str = None,
    filtro_periodo: str = None,
    filtro_andar: str = None,
    apenas_nao_resolvidos: bool = False,
    limite: int = 50
) -> list:
    """Lista eventos com filtros opcionais."""
    dados   = _carregar()
    eventos = dados["eventos"]

    if filtro_shopping:
        eventos = [e for e in eventos if e["shopping"] == filtro_shopping]
    if filtro_nivel:
        eventos = [e for e in eventos if e["nivel_alerta"] == filtro_nivel]
    if filtro_tipo:
        eventos = [e for e in eventos if filtro_tipo in e["tipo"]]
    if filtro_placa:
        eventos = [e for e in eventos if filtro_placa.upper() in e["placa"]]
    if filtro_data:
        eventos = [e for e in eventos if e["data"] == filtro_data]
    if filtro_periodo:
        eventos = [e for e in eventos if e["periodo_dia"] == filtro_periodo]
    if filtro_andar:
        eventos = [e for e in eventos if filtro_andar.lower() in e["andar"].lower()]
    if apenas_nao_resolvidos:
        eventos = [e for e in eventos if not e["resolvido"]]

    return sorted(eventos, key=lambda e: e["data_hora"], reverse=True)[:limite]


def listar_alertas_ativos() -> list:
    dados = _carregar()
    return [a for a in dados["alertas_ativos"] if not a["resolvido"]]


def veiculos_presentes(shopping: str = None) -> dict:
    """Retorna veículos atualmente no estacionamento."""
    dados = _carregar()
    vp    = dados.get("veiculos_presentes", {})
    if shopping:
        vp = {k: v for k, v in vp.items() if v["shopping"] == shopping}
    return vp


def ocupacao_atual(shopping: str = None) -> dict:
    """Retorna a ocupação atual dos estacionamentos."""
    dados = _carregar()
    oc    = dados.get("ocupacao_atual", {})
    if shopping:
        return {shopping: oc.get(shopping, {})}
    return oc


def historico_placa(placa: str) -> list:
    """Retorna o histórico completo de visitas de uma placa."""
    dados = _carregar()
    return dados["historico_placas"].get(placa.upper(), [])


def eventos_de_hoje(shopping: str = None) -> list:
    hoje = datetime.now().strftime("%Y-%m-%d")
    return listar_eventos(filtro_shopping=shopping, filtro_data=hoje, limite=500)


def eventos_criticos_nao_resolvidos() -> list:
    return listar_eventos(filtro_nivel="critico", apenas_nao_resolvidos=True, limite=100)


def buscar_evento_por_id(id_evento: str) -> dict:
    dados = _carregar()
    for e in dados["eventos"]:
        if e["id"] == id_evento:
            return e
    return None


# ─────────────────────────────────────────────
#  RESOLVER EVENTO
# ─────────────────────────────────────────────

def resolver_evento(id_evento: str, resolvido_por: str, acao_tomada: str) -> bool:
    """Marca um evento como resolvido e remove dos alertas ativos."""
    dados = _carregar()
    for i, e in enumerate(dados["eventos"]):
        if e["id"] == id_evento:
            dados["eventos"][i]["resolvido"]     = True
            dados["eventos"][i]["resolvido_em"]  = datetime.now().isoformat()
            dados["eventos"][i]["resolvido_por"] = resolvido_por
            dados["eventos"][i]["acao_tomada"]   = acao_tomada
            break
    else:
        print(f"⚠️  Evento '{id_evento}' não encontrado.")
        return False

    for i, a in enumerate(dados["alertas_ativos"]):
        if a["id_evento"] == id_evento:
            dados["alertas_ativos"][i]["resolvido"] = True
            break

    _salvar(dados)
    print(f"✅ Evento '{id_evento}' resolvido por '{resolvido_por}'.")
    return True


# ─────────────────────────────────────────────
#  ESTATÍSTICAS E RELATÓRIOS
# ─────────────────────────────────────────────

def obter_estatisticas(shopping: str = None) -> dict:
    """
    Estatísticas completas do estacionamento.
    Usado pelo dashboard e módulo de análise.
    """
    eventos = listar_eventos(filtro_shopping=shopping, limite=99999)
    if not eventos:
        return {"total": 0}

    stats = {
        "total_eventos":         len(eventos),
        "alertas_ativos":        len(listar_alertas_ativos()),
        "nao_resolvidos":        len([e for e in eventos if not e["resolvido"]]),
        "veiculos_presentes_agora": len(veiculos_presentes(shopping)),
        "por_nivel":             {},
        "por_tipo":              {},
        "por_shopping":          {},
        "por_periodo_dia":       {},
        "por_dia_semana":        {},
        "por_andar":             {},
        "por_tipo_veiculo":      {},
        "horarios_pico":         {},
        "placas_mais_frequentes":[],
        "tempo_medio_permanencia_min": 0,
        "total_entradas_hoje":   0,
        "total_saidas_hoje":     0,
    }

    hoje              = datetime.now().strftime("%Y-%m-%d")
    contagem_placas   = {}
    permanencias      = []

    for e in eventos:
        for chave, valor in [
            ("por_nivel",      e.get("nivel_alerta", "?")),
            ("por_tipo",       e.get("tipo", "?")),
            ("por_shopping",   e.get("shopping", "?")),
            ("por_periodo_dia",e.get("periodo_dia", "?")),
            ("por_dia_semana", e.get("dia_semana", "?")),
            ("por_andar",      e.get("andar", "sem_andar")),
            ("por_tipo_veiculo",e.get("tipo_veiculo", "?")),
        ]:
            stats[chave][valor] = stats[chave].get(valor, 0) + 1

        hora = e.get("hora", "00:00:00")[:2]
        stats["horarios_pico"][hora] = stats["horarios_pico"].get(hora, 0) + 1

        if e.get("placa"):
            contagem_placas[e["placa"]] = contagem_placas.get(e["placa"], 0) + 1

        if e.get("tempo_permanencia_min"):
            permanencias.append(e["tempo_permanencia_min"])

        if e["data"] == hoje:
            if e["tipo"] == "veiculo_entrou":
                stats["total_entradas_hoje"] += 1
            elif e["tipo"] == "veiculo_saiu":
                stats["total_saidas_hoje"] += 1

    if permanencias:
        stats["tempo_medio_permanencia_min"] = int(sum(permanencias) / len(permanencias))

    ranking_placas = sorted(contagem_placas.items(), key=lambda x: x[1], reverse=True)
    stats["placas_mais_frequentes"] = ranking_placas[:10]

    return stats


def relatorio_ocupacao_por_shopping() -> dict:
    """Relatório de ocupação em tempo real por shopping."""
    oc = ocupacao_atual()
    relatorio = {}
    for sh in SHOPPINGS:
        cfg  = CONFIG_SHOPPINGS.get(sh, {})
        info = oc.get(sh, {})
        presentes = info.get("veiculos_presentes", 0)
        total     = cfg.get("total_vagas", 500)
        livres    = max(0, total - presentes)
        pct       = round(presentes / total * 100, 1) if total > 0 else 0
        relatorio[sh] = {
            "total_vagas":        total,
            "veiculos_presentes": presentes,
            "vagas_livres":       livres,
            "percentual_ocupado": pct,
            "vagas_pcd":          cfg.get("vagas_pcd", 0),
            "vagas_idoso":        cfg.get("vagas_idoso", 0),
            "vagas_vip":          cfg.get("vagas_vip", 0),
            "vagas_eletrico":     cfg.get("vagas_eletrico", 0),
            "andares":            cfg.get("andares", []),
        }
    return relatorio


def veiculos_com_permanencia_longa(horas: int = 8, shopping: str = None) -> list:
    """Retorna veículos presentes há mais de X horas."""
    vp     = veiculos_presentes(shopping)
    agora  = datetime.now()
    limite = timedelta(hours=horas)
    resultado = []
    for placa, info in vp.items():
        entrada = datetime.fromisoformat(info["entrada_em"])
        duracao = agora - entrada
        if duracao >= limite:
            resultado.append({
                **info,
                "duracao_min": int(duracao.total_seconds() / 60),
                "duracao_fmt": _formatar_duracao(int(duracao.total_seconds() / 60))
            })
    return sorted(resultado, key=lambda x: x["duracao_min"], reverse=True)


def limpar_eventos_antigos(dias: int = 90) -> int:
    """Remove eventos com mais de X dias."""
    dados  = _carregar()
    corte  = datetime.now() - timedelta(days=dias)
    antes  = len(dados["eventos"])
    dados["eventos"] = [
        e for e in dados["eventos"]
        if datetime.fromisoformat(e["data_hora"]) >= corte
    ]
    removidos = antes - len(dados["eventos"])
    _salvar(dados)
    print(f"✅ {removidos} evento(s) removidos (mais de {dias} dias).")
    return removidos


# ─────────────────────────────────────────────
#  SIMULAÇÃO — Gerar dados de teste
# ─────────────────────────────────────────────

def simular_monitoramento(quantidade: int = 100):
    """
    Simula eventos reais do estacionamento para popular o sistema.
    Em produção, esses eventos viriam dos leitores LPR e câmeras.
    """
    print(f"\n🚗 Simulando {quantidade} eventos do estacionamento...\n")

    tipos    = list(TIPOS_EVENTO.keys())
    # Distribuição realista
    pesos = []
    for t in tipos:
        nivel = TIPOS_EVENTO[t]["nivel"]
        if nivel == "info":      pesos.append(65)
        elif nivel == "atencao": pesos.append(25)
        else:                    pesos.append(10)

    sucesso = 0
    for _ in range(quantidade):
        shopping = random.choice(SHOPPINGS)
        cfg      = CONFIG_SHOPPINGS[shopping]
        tipo     = random.choices(tipos, weights=pesos, k=1)[0]
        placa    = _gerar_placa_br()
        andar    = random.choice(cfg["andares"])
        veiculo  = random.choice(TIPOS_VEICULO)
        cancela  = random.choice(
            cfg["cancelas_entrada"] if "entrada" in tipo else cfg["cancelas_saida"]
        ) if "cancela" not in tipo else random.choice(
            cfg["cancelas_entrada"] + cfg["cancelas_saida"]
        )
        vaga     = f"{andar[0]}{random.randint(1,999):03d}"
        confianca = round(random.uniform(85.0, 99.9), 1)

        e = registrar_evento(
            tipo_evento=tipo,
            shopping=shopping,
            placa=placa,
            tipo_veiculo=veiculo,
            cancela=cancela,
            andar=andar,
            numero_vaga=vaga,
            confianca_ia=confianca,
        )
        if e:
            sucesso += 1

    print(f"\n✅ {sucesso} eventos simulados com sucesso!")
    stats = obter_estatisticas()
    print(f"\n📊 Resumo:")
    print(f"   Total eventos           : {stats['total_eventos']}")
    print(f"   Alertas ativos          : {stats['alertas_ativos']}")
    print(f"   Veículos presentes agora: {stats['veiculos_presentes_agora']}")
    print(f"   Entradas hoje           : {stats['total_entradas_hoje']}")
    print(f"   Saídas hoje             : {stats['total_saidas_hoje']}")


# ─────────────────────────────────────────────
#  MENU INTERATIVO
# ─────────────────────────────────────────────

def _exibir_evento(e: dict):
    icones = {"info": "ℹ️ ", "atencao": "⚠️ ", "critico": "🚨"}
    status_placa_icon = {"bloqueada": "🔴", "atencao": "🟡", "normal": "🟢"}
    print("\n" + "─" * 62)
    print(f"  {icones.get(e['nivel_alerta'],'  ')} [{e['nivel_alerta'].upper()}] {e['tipo']}")
    print(f"  ID         : {e['id']}")
    print(f"  Descrição  : {e['descricao']}")
    print(f"  Shopping   : {e['shopping']} | {e.get('andar','')} | Vaga: {e.get('numero_vaga','?')}")
    print(f"  Cancela    : {e.get('cancela','N/A')}")
    if e.get("placa"):
        sp = status_placa_icon.get(e.get("status_placa","normal"),"")
        print(f"  Placa      : {e['placa']} {sp} | Tipo: {e.get('tipo_veiculo','?')}")
    if e.get("usuario_nome"):
        print(f"  Usuário    : {e['usuario_nome']} ({e.get('usuario_perfil','')})")
    print(f"  Data/Hora  : {e['data_hora'][:19].replace('T',' ')} ({e['periodo_dia']})")
    if e.get("tempo_permanencia_min") is not None:
        print(f"  Permanência: {_formatar_duracao(e['tempo_permanencia_min'])}")
    if e.get("confianca_ia"):
        print(f"  IA conf.   : {e['confianca_ia']}%")
    status = "✅ Resolvido" if e["resolvido"] else "❌ Pendente"
    print(f"  Status     : {status}")
    print("─" * 62)


def menu():
    while True:
        alertas = listar_alertas_ativos()
        print(f"\n╔══════════════════════════════════════════════════╗")
        print(f"║    ShopControl — Monitoramento Estacionamento    ║")
        if alertas:
            print(f"║    🚨 {len(alertas)} ALERTA(S) ATIVO(S)                      ║")
        print(f"╠══════════════════════════════════════════════════╣")
        print(f"║  1.  Registrar evento manualmente                ║")
        print(f"║  2.  Ver eventos de hoje                         ║")
        print(f"║  3.  Ver alertas ativos                          ║")
        print(f"║  4.  Buscar por placa                            ║")
        print(f"║  5.  Buscar por shopping                         ║")
        print(f"║  6.  Buscar por nível (info/atencao/critico)     ║")
        print(f"║  7.  Buscar por período do dia                   ║")
        print(f"║  8.  Buscar por andar                            ║")
        print(f"║  9.  Ver veículos presentes agora                ║")
        print(f"║  10. Ver ocupação atual por shopping             ║")
        print(f"║  11. Ver histórico de uma placa                  ║")
        print(f"║  12. Veículos com permanência longa              ║")
        print(f"║  13. Lista de bloqueio — adicionar placa         ║")
        print(f"║  14. Lista de atenção — adicionar placa          ║")
        print(f"║  15. Remover placa de lista                      ║")
        print(f"║  16. Resolver evento                             ║")
        print(f"║  17. Relatório de ocupação por shopping          ║")
        print(f"║  18. Estatísticas gerais                         ║")
        print(f"║  19. Simular eventos (teste)                     ║")
        print(f"║  20. Limpar eventos antigos                      ║")
        print(f"║  0.  Sair                                        ║")
        print(f"╚══════════════════════════════════════════════════╝")

        opcao = input("\nEscolha: ").strip()

        if opcao == "1":
            print(f"\nShoppings: {', '.join(SHOPPINGS)}")
            shop  = input("Shopping: ").strip()
            placa = input("Placa do veículo (opcional): ").strip()
            print("\nTipos de evento:")
            tipos_lista = list(TIPOS_EVENTO.keys())
            for i, t in enumerate(tipos_lista):
                print(f"  {i+1:2}. {t}")
            idx  = input("Número do tipo: ").strip()
            tipo = tipos_lista[int(idx)-1] if idx.isdigit() else "veiculo_entrou"
            cfg  = CONFIG_SHOPPINGS.get(shop, {})
            print(f"Andares: {', '.join(cfg.get('andares', []))}")
            andar   = input("Andar: ").strip()
            cancela = input("Cancela: ").strip()
            vaga    = input("Número da vaga (opcional): ").strip()
            extra   = input("Descrição extra (opcional): ").strip()
            registrar_evento(tipo, shop, placa, cancela=cancela,
                             andar=andar, numero_vaga=vaga, descricao_extra=extra)

        elif opcao == "2":
            print(f"\nShoppings: {', '.join(SHOPPINGS)} (Enter = todos)")
            shop   = input("Shopping (opcional): ").strip() or None
            events = eventos_de_hoje(shop)
            print(f"\n── {len(events)} evento(s) hoje ──")
            for e in events[:20]:
                _exibir_evento(e)

        elif opcao == "3":
            alertas = listar_alertas_ativos()
            print(f"\n── {len(alertas)} alerta(s) ativo(s) ──")
            for a in alertas:
                icone = "🚨" if a["nivel"] == "critico" else "⚠️ "
                print(f"\n  {icone} [{a['nivel'].upper()}] {a['descricao']}")
                print(f"     Shopping : {a['shopping']}")
                print(f"     Placa    : {a.get('placa','N/A')}")
                print(f"     Cancela  : {a.get('cancela','N/A')}")
                print(f"     Horário  : {a['data_hora'][:19].replace('T',' ')}")
                print(f"     ID evento: {a['id_evento']}")

        elif opcao == "4":
            placa  = input("Placa (parcial ou completa): ").strip()
            events = listar_eventos(filtro_placa=placa)
            print(f"\n── {len(events)} evento(s) para placa '{placa}' ──")
            for e in events:
                _exibir_evento(e)

        elif opcao == "5":
            print(f"Shoppings: {', '.join(SHOPPINGS)}")
            shop   = input("Shopping: ").strip()
            events = listar_eventos(filtro_shopping=shop, limite=20)
            for e in events:
                _exibir_evento(e)

        elif opcao == "6":
            print("Níveis: info, atencao, critico")
            nivel  = input("Nível: ").strip()
            events = listar_eventos(filtro_nivel=nivel, limite=20)
            for e in events:
                _exibir_evento(e)

        elif opcao == "7":
            print("Períodos: manha, tarde, noite, madrugada")
            periodo = input("Período: ").strip()
            events  = listar_eventos(filtro_periodo=periodo, limite=20)
            for e in events:
                _exibir_evento(e)

        elif opcao == "8":
            andar  = input("Andar (ex: Térreo, 1º Subsolo): ").strip()
            events = listar_eventos(filtro_andar=andar, limite=20)
            for e in events:
                _exibir_evento(e)

        elif opcao == "9":
            print(f"\nShoppings: {', '.join(SHOPPINGS)} (Enter = todos)")
            shop = input("Shopping (opcional): ").strip() or None
            vp   = veiculos_presentes(shop)
            print(f"\n── {len(vp)} veículo(s) no estacionamento agora ──")
            for placa, info in vp.items():
                entrada = datetime.fromisoformat(info["entrada_em"])
                mins    = int((datetime.now() - entrada).total_seconds() / 60)
                sp      = {"bloqueada":"🔴","atencao":"🟡","normal":"🟢"}.get(info.get("status_placa","normal"),"")
                print(f"  {sp} {placa} | {info['tipo_veiculo']} | {info['shopping']} "
                      f"| {info['andar']} | {_formatar_duracao(mins)}"
                      + (f" | {info['usuario_nome']}" if info.get('usuario_nome') else ""))

        elif opcao == "10":
            rel = relatorio_ocupacao_por_shopping()
            print(f"\n── OCUPAÇÃO ATUAL ──\n")
            for sh, r in rel.items():
                pct   = r["percentual_ocupado"]
                barra = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
                print(f"  {sh}")
                print(f"  [{barra}] {pct}%")
                print(f"  Presentes: {r['veiculos_presentes']}/{r['total_vagas']} | "
                      f"Livres: {r['vagas_livres']} | "
                      f"PCD: {r['vagas_pcd']} | Idoso: {r['vagas_idoso']} | "
                      f"VIP: {r['vagas_vip']} | Elétrico: {r['vagas_eletrico']}\n")

        elif opcao == "11":
            placa = input("Placa: ").strip().upper()
            hist  = historico_placa(placa)
            print(f"\n── {len(hist)} visita(s) da placa '{placa}' ──")
            for h in hist:
                print(f"  {h['data_hora'][:19].replace('T',' ')} | {h['tipo']} | "
                      f"{h['shopping']} | {h.get('andar','')} | {h.get('cancela','')}")

        elif opcao == "12":
            horas = input("Mais de quantas horas? [8]: ").strip()
            horas = int(horas) if horas.isdigit() else 8
            print(f"\nShoppings: {', '.join(SHOPPINGS)} (Enter = todos)")
            shop  = input("Shopping (opcional): ").strip() or None
            vlong = veiculos_com_permanencia_longa(horas, shop)
            print(f"\n── {len(vlong)} veículo(s) com mais de {horas}h ──")
            for v in vlong:
                sp = {"bloqueada":"🔴","atencao":"🟡","normal":"🟢"}.get(v.get("status_placa","normal"),"")
                print(f"  {sp} {v['placa']} | {v['tipo_veiculo']} | {v['shopping']} "
                      f"| {v['andar']} | ⏱ {v['duracao_fmt']}")

        elif opcao == "13":
            placa  = input("Placa a bloquear: ").strip()
            motivo = input("Motivo: ").strip()
            resp   = input("Adicionado por: ").strip()
            adicionar_placa_bloqueio(placa, motivo, resp)

        elif opcao == "14":
            placa  = input("Placa para lista de atenção: ").strip()
            motivo = input("Motivo: ").strip()
            resp   = input("Adicionado por: ").strip()
            adicionar_placa_atencao(placa, motivo, resp)

        elif opcao == "15":
            placa = input("Placa a remover: ").strip()
            print("Lista: bloqueio / atencao")
            lista = input("Lista: ").strip()
            remover_placa_lista(placa, lista)

        elif opcao == "16":
            id_ev  = input("ID do evento: ").strip()
            resp   = input("Resolvido por: ").strip()
            acao   = input("Ação tomada: ").strip()
            resolver_evento(id_ev, resp, acao)

        elif opcao == "17":
            rel = relatorio_ocupacao_por_shopping()
            print(f"\n── RELATÓRIO COMPLETO ──")
            for sh, r in rel.items():
                print(f"\n  {sh}: {r['percentual_ocupado']}% ocupado")
                print(f"  Andares: {', '.join(r['andares'])}")

        elif opcao == "18":
            print(f"\nShoppings: {', '.join(SHOPPINGS)} (Enter = todos)")
            shop  = input("Shopping (opcional): ").strip() or None
            stats = obter_estatisticas(shop)
            print(f"\n── ESTATÍSTICAS ──")
            print(f"  Total eventos           : {stats['total_eventos']}")
            print(f"  Alertas ativos          : {stats['alertas_ativos']}")
            print(f"  Não resolvidos          : {stats['nao_resolvidos']}")
            print(f"  Veículos presentes agora: {stats['veiculos_presentes_agora']}")
            print(f"  Entradas hoje           : {stats['total_entradas_hoje']}")
            print(f"  Saídas hoje             : {stats['total_saidas_hoje']}")
            print(f"  Tempo médio permanência : {_formatar_duracao(stats['tempo_medio_permanencia_min'])}")
            print(f"  Por nível               : {stats['por_nivel']}")
            print(f"  Por período do dia      : {stats['por_periodo_dia']}")
            print(f"  Por tipo de veículo     : {stats['por_tipo_veiculo']}")
            print(f"  Top 10 placas frequentes: {stats['placas_mais_frequentes']}")
            print(f"  Horários de pico        : {dict(sorted(stats['horarios_pico'].items()))}")

        elif opcao == "19":
            qtd = input("Quantos eventos simular? [100]: ").strip()
            simular_monitoramento(int(qtd) if qtd.isdigit() else 100)

        elif opcao == "20":
            dias = input("Remover eventos mais antigos que X dias? [90]: ").strip()
            limpar_eventos_antigos(int(dias) if dias.isdigit() else 90)

        elif opcao == "0":
            print("\n👋 Até logo!\n")
            break
        else:
            print("⚠️  Opção inválida.")


# ─────────────────────────────────────────────
#  PONTO DE ENTRADA
# ─────────────────────────────────────────────

if __name__ == "__main__":
    menu()