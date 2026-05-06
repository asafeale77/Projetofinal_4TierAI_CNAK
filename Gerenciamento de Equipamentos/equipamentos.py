"""
╔══════════════════════════════════════════════════════════════╗
║           MÓDULO DE GERENCIAMENTO DE EQUIPAMENTOS            ║
║              ShopControl - Rede de Shoppings                 ║
╚══════════════════════════════════════════════════════════════╝
"""

import json
import os
import random
import string
from datetime import datetime, timedelta


# ─────────────────────────────────────────────
#  CONFIGURAÇÃO DO BANCO DE DADOS (JSON)
# ─────────────────────────────────────────────

PASTA_DADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'dados')
ARQUIVO_EQUIPAMENTOS = os.path.join(PASTA_DADOS, 'equipamentos.json')


# ─────────────────────────────────────────────
#  CATÁLOGO COMPLETO DE TIPOS DE EQUIPAMENTOS
# ─────────────────────────────────────────────

TIPOS_EQUIPAMENTO = {

    # ── CÂMERAS ────────────────────────────────────────────────────────
    "camera_dome":               "Câmera Dome (teto, visão 360°)",
    "camera_bullet":             "Câmera Bullet (externa, longa distância)",
    "camera_ptz":                "Câmera PTZ (pan/tilt/zoom motorizado)",
    "camera_fisheye":            "Câmera Fisheye (visão panorâmica total)",
    "camera_termica":            "Câmera Térmica (detecta calor corporal)",
    "camera_ia_facial":          "Câmera IA — Reconhecimento Facial",
    "camera_ia_comportamento":   "Câmera IA — Análise de Comportamento",
    "camera_ia_contagem":        "Câmera IA — Contagem de Pessoas",
    "camera_ia_fila":            "Câmera IA — Detecção de Filas",
    "camera_ia_abandono":        "Câmera IA — Objeto Abandonado",
    "camera_ia_placa":           "Câmera IA — Leitura de Placas (LPR/ANPR)",
    "camera_ia_multidao":        "Câmera IA — Detecção de Multidão/Aglomeração",
    "camera_360_imersiva":       "Câmera 360° Imersiva (cobertura total do ambiente)",
    "camera_miniatura":          "Câmera Miniatura (discreta, embutida)",
    "camera_speed_dome":         "Camera Speed Dome (alta velocidade de rotação)",
    "camera_box":                "Câmera Box (industrial, alta resolução)",

    # ── SENSORES ───────────────────────────────────────────────────────
    "sensor_presenca_pir":       "Sensor de Presença PIR (infravermelho passivo)",
    "sensor_presenca_microondas":"Sensor de Presença por Micro-ondas",
    "sensor_contagem_bidirecional": "Sensor de Contagem Bidirecional (entrada/saída)",
    "sensor_peso":               "Sensor de Peso (detecta ocupação por peso)",
    "sensor_temperatura":        "Sensor de Temperatura Ambiente",
    "sensor_umidade":            "Sensor de Umidade",
    "sensor_qualidade_ar":       "Sensor de Qualidade do Ar (CO2, VOC)",
    "sensor_fumaca":             "Sensor de Fumaça",
    "sensor_gas":                "Sensor de Gás (vazamento)",
    "sensor_vibracão":           "Sensor de Vibração (anti-intrusão)",
    "sensor_porta_janela":       "Sensor de Abertura (porta/janela)",
    "sensor_nivel_som":          "Sensor de Nível de Som (detecção de barulho suspeito)",
    "sensor_luz":                "Sensor de Luminosidade",
    "sensor_inundacao":          "Sensor de Inundação/Alagamento",
    "sensor_ocupacao_vaga":      "Sensor de Ocupação de Vaga (estacionamento)",
    "sensor_radar_movimento":    "Sensor Radar de Movimento",
    "sensor_lidar":              "Sensor LiDAR (mapeamento 3D do ambiente)",
    "sensor_biometrico_digital": "Sensor Biométrico — Digital",
    "sensor_biometrico_facial":  "Sensor Biométrico — Facial",
    "sensor_biometrico_iris":    "Sensor Biométrico — Íris",
    "sensor_biometrico_voz":     "Sensor Biométrico — Voz",
    "sensor_rfid":               "Sensor RFID (rastreamento de crachás/tags)",
    "sensor_nfc":                "Sensor NFC (aproximação de cartão/celular)",
    "sensor_bluetooth_beacon":   "Sensor Bluetooth Beacon (rastreamento indoor)",
    "sensor_wifi_probe":         "Sensor Wi-Fi Probe (rastreamento por Wi-Fi)",
    "sensor_ultrasonico":        "Sensor Ultrassônico (medição de distância/presença)",

    # ── CONTROLE DE ACESSO ────────────────────────────────────────────
    "catraca_full_height":       "Catraca Full Height (segurança máxima)",
    "catraca_meia_altura":       "Catraca Meia Altura (fluxo rápido)",
    "catraca_biometrica":        "Catraca Biométrica (digital + facial)",
    "porta_giratoria":           "Porta Giratória de Segurança",
    "eclusa_seguranca":          "Eclusa de Segurança (sala de bloqueio)",
    "leitor_cartao_rfid":        "Leitor de Cartão RFID/Crachá",
    "leitor_qrcode":             "Leitor de QR Code",
    "teclado_senha":             "Teclado de Senha (controle de acesso)",
    "interfone_video":           "Interfone com Vídeo",
    "fechadura_eletromagnetica": "Fechadura Eletromagnética",
    "fechadura_biometrica":      "Fechadura Biométrica",
    "controlador_acesso":        "Controlador de Acesso (central do sistema)",
    "torniquete_optical":        "Torniquete Óptico (vidro, entrada elegante)",

    # ── ESTACIONAMENTO ────────────────────────────────────────────────
    "leitor_placa_lpr":          "Leitor de Placas LPR (entrada/saída)",
    "cancela_automatica":        "Cancela Automática",
    "cancela_com_leitor":        "Cancela com Leitor de Placa Integrado",
    "totem_pagamento_estac":     "Totem de Pagamento de Estacionamento",
    "display_vagas":             "Display de Vagas Disponíveis",
    "sensor_vaga_individual":    "Sensor de Vaga Individual (LED verde/vermelho)",
    "guia_vaga_led":             "Guia de Vagas por LED (direcionamento)",
    "camera_estac_cobertura":    "Câmera de Cobertura do Estacionamento",
    "interfone_estac":           "Interfone de Emergência no Estacionamento",
    "carregador_veiculo_eletrico":"Carregador de Veículo Elétrico (EV)",
    "sistema_gestao_vagas":      "Sistema Central de Gestão de Vagas",

    # ── REDE E INFRAESTRUTURA ─────────────────────────────────────────
    "roteador_industrial":       "Roteador Industrial (rede local)",
    "switch_poe":                "Switch PoE (alimenta câmeras via cabo)",
    "access_point_wifi6":        "Access Point Wi-Fi 6 (cobertura wireless)",
    "nvr_gravador":              "NVR — Gravador de Vídeo em Rede",
    "dvr_gravador":              "DVR — Gravador de Vídeo Digital",
    "servidor_ia":               "Servidor de IA (processamento local)",
    "servidor_armazenamento":    "Servidor de Armazenamento (NAS/SAN)",
    "no_edge_computing":         "Nó de Edge Computing (IA na borda)",
    "ups_nobreak":               "UPS/Nobreak (energia ininterrupta)",
    "rack_equipamentos":         "Rack de Equipamentos",
    "patch_panel":               "Patch Panel",
    "fibra_optica_conversor":    "Conversor de Fibra Óptica",

    # ── ALARME E EMERGÊNCIA ───────────────────────────────────────────
    "central_alarme":            "Central de Alarme",
    "sirene_externa":            "Sirene Externa",
    "sirene_interna":            "Sirene Interna",
    "botao_panico":              "Botão de Pânico",
    "detector_metal_portatil":   "Detector de Metal Portátil",
    "portal_detector_metal":     "Portal Detector de Metal",
    "sistema_spda":              "SPDA — Para-raios",
    "extintor_automatico":       "Extintor Automático (sprinkler)",
    "central_incendio":          "Central de Alarme de Incêndio",
    "detector_fumaca_optical":   "Detector de Fumaça Óptico (teto)",
    "detector_calor":            "Detector de Calor (cozinhas/estac.)",
    "luz_emergencia":            "Iluminação de Emergência",
    "placa_saida_emergencia":    "Placa de Saída de Emergência (LED)",

    # ── COMUNICAÇÃO E INTERAÇÃO ───────────────────────────────────────
    "totem_informacao":          "Totem de Informação Interativo",
    "totem_autoatendimento":     "Totem de Autoatendimento",
    "painel_led_externo":        "Painel LED Externo (publicidade/info)",
    "display_digital_interno":   "Display Digital Interno (sinalização)",
    "alto_falante_ip":           "Alto-falante IP (comunicação/alarme)",
    "microfone_ambiente":        "Microfone Ambiente (detecção de som)",
    "intercomunicador":          "Intercomunicador (segurança)",
    "radio_comunicador_base":    "Rádio Comunicador — Base",

    # ── MONITORAMENTO INTELIGENTE ─────────────────────────────────────
    "terminal_mapa_calor":       "Terminal de Mapa de Calor (visualização local)",
    "estacao_monitoramento":     "Estação de Monitoramento (operador)",
    "videowall":                 "Videowall (parede de monitores — sala CFTV)",
    "monitor_operador":          "Monitor do Operador",
    "tablet_seguranca":          "Tablet de Segurança (patrulha móvel)",
    "dispositivo_wearable":      "Dispositivo Wearable (câmera corporal)",
    "drone_seguranca":           "Drone de Segurança (área externa)",

    # ── ENERGIA ───────────────────────────────────────────────────────
    "painel_solar":              "Painel Solar (energia auxiliar)",
    "medidor_energia":           "Medidor de Energia Inteligente",
    "controlador_carga":         "Controlador de Carga",
    "gerador_backup":            "Gerador de Backup",
}

# Status possíveis de um equipamento
STATUS_EQUIPAMENTO = [
    "operacional",
    "em_manutencao",
    "com_defeito",
    "desativado",
    "em_instalacao",
    "aguardando_peca",
    "substituido"
]

# Marcas reais do mercado de segurança
MARCAS = [
    "Hikvision", "Dahua", "Axis", "Bosch Security", "Hanwha",
    "Vivotek", "Pelco", "Genetec", "Milestone", "Intelbras",
    "Geutebruck", "Avigilon", "Mobotix", "Sony Security",
    "Panasonic Security", "Samsung Techwin", "Honeywell Security",
    "Suprema", "ZKTeco", "Control iD", "Nicehash", "Came",
    "Nice", "Perto", "Tecnohold", "Speedmaq", "Sense", "Paradox"
]

# Shoppings da rede
SHOPPINGS = ["Shopping 1", "Shopping 2", "Shopping 3", "Shopping 4"]


# ─────────────────────────────────────────────
#  FUNÇÕES DE BANCO DE DADOS
# ─────────────────────────────────────────────

def _inicializar_banco():
    os.makedirs(PASTA_DADOS, exist_ok=True)
    if not os.path.exists(ARQUIVO_EQUIPAMENTOS):
        estrutura = {
            "metadados": {
                "criado_em": datetime.now().isoformat(),
                "ultima_atualizacao": datetime.now().isoformat(),
                "total_equipamentos": 0,
                "versao": "1.0"
            },
            "equipamentos": []
        }
        _salvar_dados(estrutura)
        print("✅ Banco 'equipamentos.json' criado com sucesso!")


def _carregar_dados():
    _inicializar_banco()
    with open(ARQUIVO_EQUIPAMENTOS, 'r', encoding='utf-8') as f:
        return json.load(f)


def _salvar_dados(dados):
    os.makedirs(PASTA_DADOS, exist_ok=True)
    dados['metadados']['ultima_atualizacao'] = datetime.now().isoformat()
    dados['metadados']['total_equipamentos'] = len(dados['equipamentos'])
    with open(ARQUIVO_EQUIPAMENTOS, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def _gerar_id(tipo: str) -> str:
    prefixo = tipo[:3].upper()
    codigo = ''.join(random.choices(string.digits, k=6))
    return f"{prefixo}-{codigo}"


def _gerar_numero_serie() -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


# ─────────────────────────────────────────────
#  CRUD — CRIAR
# ─────────────────────────────────────────────

def criar_equipamento(
    tipo: str,
    marca: str,
    modelo: str,
    shopping: str,
    numero_serie: str = None,
    data_instalacao: str = None,
    data_garantia: str = None,
    ip_rede: str = None,
    resolucao: str = None,
    observacoes: str = ""
) -> dict:
    """
    Cadastra um novo equipamento no sistema.

    Parâmetros:
        tipo            → Tipo do equipamento (ver TIPOS_EQUIPAMENTO)
        marca           → Fabricante
        modelo          → Modelo específico
        shopping        → Shopping onde está instalado
        numero_serie    → Número de série (gerado automaticamente se vazio)
        data_instalacao → Data de instalação (padrão: hoje)
        data_garantia   → Data de fim de garantia
        ip_rede         → IP na rede local (para câmeras/equipamentos conectados)
        resolucao       → Resolução (para câmeras, ex: "4K", "1080p")
        observacoes     → Observações adicionais
    """
    if tipo not in TIPOS_EQUIPAMENTO:
        print(f"⚠️  Tipo inválido. Use listar_tipos() para ver as opções.")
        return None

    if shopping not in SHOPPINGS:
        print(f"⚠️  Shopping inválido. Opções: {', '.join(SHOPPINGS)}")
        return None

    dados = _carregar_dados()

    # Verifica número de série duplicado
    ns = numero_serie or _gerar_numero_serie()
    for eq in dados['equipamentos']:
        if eq['numero_serie'] == ns:
            print(f"⚠️  Já existe equipamento com o número de série '{ns}'.")
            return None

    novo = {
        "id": _gerar_id(tipo),
        "tipo": tipo,
        "descricao_tipo": TIPOS_EQUIPAMENTO[tipo],
        "marca": marca,
        "modelo": modelo,
        "shopping": shopping,
        "numero_serie": ns,
        "status": "em_instalacao",
        "ip_rede": ip_rede or "",
        "resolucao": resolucao or "",
        "data_instalacao": data_instalacao or datetime.now().strftime("%Y-%m-%d"),
        "data_garantia": data_garantia or "",
        "ambiente_id": None,
        "ambiente_nome": "Não distribuído",
        "observacoes": observacoes,
        "ultimo_ping": None,
        "online": False,
        "historico_manutencao": [],
        "alertas_ativos": [],
        "criado_em": datetime.now().isoformat(),
        "atualizado_em": datetime.now().isoformat()
    }

    dados['equipamentos'].append(novo)
    _salvar_dados(dados)
    print(f"✅ Equipamento cadastrado! ID: {novo['id']} | NS: {novo['numero_serie']}")
    return novo


# ─────────────────────────────────────────────
#  CRUD — LISTAR / BUSCAR
# ─────────────────────────────────────────────

def listar_equipamentos(
    shopping: str = None,
    tipo: str = None,
    status: str = None
) -> list:
    """Lista equipamentos com filtros opcionais."""
    dados = _carregar_dados()
    eqs = dados['equipamentos']

    if shopping:
        eqs = [e for e in eqs if e['shopping'] == shopping]
    if tipo:
        eqs = [e for e in eqs if e['tipo'] == tipo]
    if status:
        eqs = [e for e in eqs if e['status'] == status]

    return eqs


def buscar_por_id(equip_id: str) -> dict:
    dados = _carregar_dados()
    for e in dados['equipamentos']:
        if e['id'] == equip_id:
            return e
    print(f"⚠️  Equipamento '{equip_id}' não encontrado.")
    return None


def buscar_por_serie(numero_serie: str) -> dict:
    dados = _carregar_dados()
    for e in dados['equipamentos']:
        if e['numero_serie'] == numero_serie:
            return e
    print(f"⚠️  Número de série '{numero_serie}' não encontrado.")
    return None


def listar_tipos() -> dict:
    """Exibe todos os tipos de equipamentos disponíveis."""
    return TIPOS_EQUIPAMENTO


# ─────────────────────────────────────────────
#  CRUD — ATUALIZAR
# ─────────────────────────────────────────────

def atualizar_equipamento(equip_id: str, **campos) -> dict:
    """Atualiza campos de um equipamento."""
    campos_permitidos = [
        'marca', 'modelo', 'status', 'ip_rede', 'resolucao',
        'data_garantia', 'observacoes', 'online', 'ultimo_ping'
    ]
    dados = _carregar_dados()
    for i, e in enumerate(dados['equipamentos']):
        if e['id'] == equip_id:
            for campo, valor in campos.items():
                if campo in campos_permitidos:
                    dados['equipamentos'][i][campo] = valor
            dados['equipamentos'][i]['atualizado_em'] = datetime.now().isoformat()
            _salvar_dados(dados)
            print(f"✅ Equipamento '{equip_id}' atualizado!")
            return dados['equipamentos'][i]
    print(f"⚠️  Equipamento '{equip_id}' não encontrado.")
    return None


def alterar_status(equip_id: str, novo_status: str, motivo: str = "") -> dict:
    """Altera o status de um equipamento e registra no histórico."""
    if novo_status not in STATUS_EQUIPAMENTO:
        print(f"⚠️  Status inválido. Opções: {', '.join(STATUS_EQUIPAMENTO)}")
        return None

    dados = _carregar_dados()
    for i, e in enumerate(dados['equipamentos']):
        if e['id'] == equip_id:
            status_anterior = e['status']
            dados['equipamentos'][i]['status'] = novo_status
            dados['equipamentos'][i]['atualizado_em'] = datetime.now().isoformat()

            # Registra no histórico de manutenção
            if novo_status in ['em_manutencao', 'com_defeito', 'operacional']:
                dados['equipamentos'][i]['historico_manutencao'].append({
                    "data": datetime.now().isoformat(),
                    "status_anterior": status_anterior,
                    "novo_status": novo_status,
                    "motivo": motivo or "Não informado"
                })

            _salvar_dados(dados)
            print(f"✅ Status de '{equip_id}': {status_anterior} → {novo_status}")
            return dados['equipamentos'][i]

    print(f"⚠️  Equipamento '{equip_id}' não encontrado.")
    return None


def registrar_manutencao(
    equip_id: str,
    descricao: str,
    tecnico: str,
    custo: float = 0.0
) -> dict:
    """Registra uma manutenção realizada no equipamento."""
    dados = _carregar_dados()
    for i, e in enumerate(dados['equipamentos']):
        if e['id'] == equip_id:
            registro = {
                "data": datetime.now().isoformat(),
                "tipo": "manutencao",
                "descricao": descricao,
                "tecnico": tecnico,
                "custo": custo,
                "status_anterior": e['status']
            }
            dados['equipamentos'][i]['historico_manutencao'].append(registro)
            dados['equipamentos'][i]['status'] = "operacional"
            dados['equipamentos'][i]['atualizado_em'] = datetime.now().isoformat()
            _salvar_dados(dados)
            print(f"✅ Manutenção registrada para '{equip_id}'.")
            return dados['equipamentos'][i]
    print(f"⚠️  Equipamento '{equip_id}' não encontrado.")
    return None


# ─────────────────────────────────────────────
#  CRUD — DELETAR
# ─────────────────────────────────────────────

def deletar_equipamento(equip_id: str) -> bool:
    dados = _carregar_dados()
    for i, e in enumerate(dados['equipamentos']):
        if e['id'] == equip_id:
            dados['equipamentos'].pop(i)
            _salvar_dados(dados)
            print(f"🗑️  Equipamento '{equip_id}' removido.")
            return True
    print(f"⚠️  Equipamento '{equip_id}' não encontrado.")
    return False


# ─────────────────────────────────────────────
#  ESTATÍSTICAS E RELATÓRIOS
# ─────────────────────────────────────────────

def obter_estatisticas(shopping: str = None) -> dict:
    """Retorna estatísticas dos equipamentos — útil para o dashboard."""
    eqs = listar_equipamentos(shopping=shopping)

    por_status = {}
    for s in STATUS_EQUIPAMENTO:
        por_status[s] = len([e for e in eqs if e['status'] == s])

    por_tipo = {}
    for tipo in TIPOS_EQUIPAMENTO:
        qtd = len([e for e in eqs if e['tipo'] == tipo])
        if qtd > 0:
            por_tipo[tipo] = qtd

    por_shopping = {}
    for sh in SHOPPINGS:
        por_shopping[sh] = len([e for e in eqs if e['shopping'] == sh])

    return {
        "total": len(eqs),
        "operacionais": por_status.get("operacional", 0),
        "em_manutencao": por_status.get("em_manutencao", 0),
        "com_defeito": por_status.get("com_defeito", 0),
        "nao_distribuidos": len([e for e in eqs if e['ambiente_id'] is None]),
        "por_status": por_status,
        "por_tipo": por_tipo,
        "por_shopping": por_shopping,
        "cameras_total": len([e for e in eqs if 'camera' in e['tipo']]),
        "sensores_total": len([e for e in eqs if 'sensor' in e['tipo']]),
    }


def listar_equipamentos_com_defeito() -> list:
    """Retorna todos os equipamentos com problema — para relatório de manutenção."""
    dados = _carregar_dados()
    return [e for e in dados['equipamentos']
            if e['status'] in ['com_defeito', 'em_manutencao', 'aguardando_peca']]


def equipamentos_garantia_vencendo(dias: int = 30) -> list:
    """Retorna equipamentos com garantia vencendo nos próximos X dias."""
    dados = _carregar_dados()
    resultado = []
    limite = datetime.now() + timedelta(days=dias)
    for e in dados['equipamentos']:
        if e.get('data_garantia'):
            try:
                venc = datetime.strptime(e['data_garantia'], "%Y-%m-%d")
                if datetime.now() <= venc <= limite:
                    resultado.append(e)
            except ValueError:
                pass
    return resultado


# ─────────────────────────────────────────────
#  POPULAR COM DADOS INICIAIS (EXEMPLOS)
# ─────────────────────────────────────────────

def popular_equipamentos_iniciais():
    """
    Popula o sistema com equipamentos de exemplo para os 4 shoppings.
    Representa uma instalação típica de segurança real.
    """
    exemplos = []

    for shopping in SHOPPINGS:

        # Câmeras principais
        for tipo in ["camera_dome", "camera_bullet", "camera_ptz",
                     "camera_ia_facial", "camera_ia_comportamento",
                     "camera_ia_contagem", "camera_ia_placa"]:
            exemplos.append({
                "tipo": tipo, "marca": random.choice(["Hikvision", "Dahua", "Axis", "Intelbras"]),
                "modelo": f"DS-{random.randint(1000,9999)}", "shopping": shopping,
                "resolucao": random.choice(["4K", "2K", "1080p", "1080p"]),
                "data_garantia": "2027-12-31"
            })

        # Sensores
        for tipo in ["sensor_presenca_pir", "sensor_contagem_bidirecional",
                     "sensor_fumaca", "sensor_temperatura", "sensor_qualidade_ar",
                     "sensor_rfid", "sensor_bluetooth_beacon"]:
            exemplos.append({
                "tipo": tipo, "marca": random.choice(["Bosch Security", "Honeywell Security", "Paradox"]),
                "modelo": f"SN-{random.randint(100,999)}", "shopping": shopping,
                "data_garantia": "2027-06-30"
            })

        # Controle de acesso
        for tipo in ["catraca_biometrica", "leitor_cartao_rfid",
                     "leitor_qrcode", "fechadura_eletromagnetica"]:
            exemplos.append({
                "tipo": tipo, "marca": random.choice(["Control iD", "ZKTeco", "Suprema"]),
                "modelo": f"CA-{random.randint(100,999)}", "shopping": shopping,
                "data_garantia": "2026-12-31"
            })

        # Estacionamento
        for tipo in ["leitor_placa_lpr", "cancela_automatica",
                     "sensor_vaga_individual", "display_vagas", "totem_pagamento_estac"]:
            exemplos.append({
                "tipo": tipo, "marca": random.choice(["Hikvision", "Perto", "Speedmaq"]),
                "modelo": f"EST-{random.randint(100,999)}", "shopping": shopping,
                "data_garantia": "2027-03-31"
            })

        # Rede e infraestrutura
        for tipo in ["nvr_gravador", "switch_poe", "servidor_ia",
                     "ups_nobreak", "access_point_wifi6"]:
            exemplos.append({
                "tipo": tipo, "marca": random.choice(["Hikvision", "Cisco", "APC", "Ubiquiti"]),
                "modelo": f"INF-{random.randint(100,999)}", "shopping": shopping,
                "data_garantia": "2028-01-31"
            })

        # Alarme e emergência
        for tipo in ["central_alarme", "botao_panico", "detector_fumaca_optical",
                     "luz_emergencia", "sirene_interna"]:
            exemplos.append({
                "tipo": tipo, "marca": random.choice(["Bosch Security", "Paradox", "Honeywell Security"]),
                "modelo": f"ALM-{random.randint(100,999)}", "shopping": shopping,
                "data_garantia": "2027-09-30"
            })

        # Comunicação
        for tipo in ["totem_informacao", "display_digital_interno",
                     "alto_falante_ip", "estacao_monitoramento"]:
            exemplos.append({
                "tipo": tipo, "marca": random.choice(["Samsung Techwin", "Sony Security", "Panasonic Security"]),
                "modelo": f"COM-{random.randint(100,999)}", "shopping": shopping,
                "data_garantia": "2026-06-30"
            })

    print(f"\n📦 Cadastrando {len(exemplos)} equipamentos nos 4 shoppings...\n")
    sucesso = 0
    for eq in exemplos:
        resultado = criar_equipamento(**eq)
        if resultado:
            sucesso += 1
    print(f"\n✅ {sucesso} equipamentos cadastrados com sucesso!")


# ─────────────────────────────────────────────
#  MENU INTERATIVO
# ─────────────────────────────────────────────

def _exibir_equipamento(e: dict):
    print(f"""
  🔧 {e['descricao_tipo']} (ID: {e['id']})
  ├─ Marca/Modelo  : {e['marca']} {e['modelo']}
  ├─ Shopping      : {e['shopping']}
  ├─ Status        : {e['status'].upper()}
  ├─ Nº Série      : {e['numero_serie']}
  ├─ Resolução     : {e['resolucao'] or 'N/A'}
  ├─ IP na rede    : {e['ip_rede'] or 'N/A'}
  ├─ Ambiente      : {e['ambiente_nome']}
  ├─ Instalação    : {e['data_instalacao']}
  ├─ Garantia até  : {e['data_garantia'] or 'N/A'}
  └─ Manutenções   : {len(e['historico_manutencao'])} registros
""")


def menu():
    _inicializar_banco()
    while True:
        print("""
╔══════════════════════════════════════════════════╗
║       EQUIPAMENTOS DO SISTEMA - ShopControl      ║
╠══════════════════════════════════════════════════╣
║  1.  Listar todos os equipamentos                ║
║  2.  Listar por shopping                         ║
║  3.  Listar por tipo                             ║
║  4.  Listar com defeito/manutenção               ║
║  5.  Buscar por ID                               ║
║  6.  Buscar por número de série                  ║
║  7.  Cadastrar novo equipamento                  ║
║  8.  Alterar status                              ║
║  9.  Registrar manutenção                        ║
║  10. Deletar equipamento                         ║
║  11. Estatísticas gerais                         ║
║  12. Ver tipos de equipamentos disponíveis       ║
║  13. Popular com dados iniciais (4 shoppings)    ║
║  0.  Sair                                        ║
╚══════════════════════════════════════════════════╝
        """)
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            eqs = listar_equipamentos()
            print(f"\n📋 {len(eqs)} equipamento(s) encontrado(s):")
            for e in eqs:
                _exibir_equipamento(e)

        elif opcao == "2":
            print(f"Shoppings: {', '.join(SHOPPINGS)}")
            sh = input("Shopping: ").strip()
            eqs = listar_equipamentos(shopping=sh)
            print(f"\n📋 {len(eqs)} equipamento(s) em {sh}:")
            for e in eqs:
                _exibir_equipamento(e)

        elif opcao == "3":
            print("\nTipos disponíveis:")
            for k, v in TIPOS_EQUIPAMENTO.items():
                print(f"  {k:<35} → {v}")
            tipo = input("\nDigite o tipo: ").strip()
            eqs = listar_equipamentos(tipo=tipo)
            for e in eqs:
                _exibir_equipamento(e)

        elif opcao == "4":
            eqs = listar_equipamentos_com_defeito()
            print(f"\n⚠️  {len(eqs)} equipamento(s) com problema:")
            for e in eqs:
                _exibir_equipamento(e)

        elif opcao == "5":
            eid = input("ID do equipamento: ").strip().upper()
            e = buscar_por_id(eid)
            if e:
                _exibir_equipamento(e)

        elif opcao == "6":
            ns = input("Número de série: ").strip()
            e = buscar_por_serie(ns)
            if e:
                _exibir_equipamento(e)

        elif opcao == "7":
            print("\n── Cadastrar novo equipamento ──")
            print("\nCategorias de tipos (digite listar para ver todos):")
            entrada = input("Tipo (ou 'listar'): ").strip()
            if entrada == 'listar':
                for k, v in TIPOS_EQUIPAMENTO.items():
                    print(f"  {k:<35} → {v}")
                tipo = input("\nTipo escolhido: ").strip()
            else:
                tipo = entrada
            marca = input("Marca: ").strip()
            modelo = input("Modelo: ").strip()
            print(f"Shoppings: {', '.join(SHOPPINGS)}")
            shopping = input("Shopping: ").strip()
            resolucao = input("Resolução (câmeras, opcional): ").strip()
            ip = input("IP na rede (opcional): ").strip()
            obs = input("Observações (opcional): ").strip()
            criar_equipamento(tipo, marca, modelo, shopping,
                              resolucao=resolucao, ip_rede=ip, observacoes=obs)

        elif opcao == "8":
            eid = input("ID do equipamento: ").strip().upper()
            print(f"Status: {', '.join(STATUS_EQUIPAMENTO)}")
            novo_status = input("Novo status: ").strip()
            motivo = input("Motivo: ").strip()
            alterar_status(eid, novo_status, motivo)

        elif opcao == "9":
            eid = input("ID do equipamento: ").strip().upper()
            desc = input("Descrição da manutenção: ").strip()
            tec = input("Técnico responsável: ").strip()
            custo_str = input("Custo (R$, opcional): ").strip()
            custo = float(custo_str) if custo_str else 0.0
            registrar_manutencao(eid, desc, tec, custo)

        elif opcao == "10":
            eid = input("ID do equipamento a deletar: ").strip().upper()
            confirm = input("⚠️  Digite 'SIM' para confirmar: ").strip()
            if confirm == "SIM":
                deletar_equipamento(eid)

        elif opcao == "11":
            stats = obter_estatisticas()
            print(f"""
📊 Estatísticas:
  Total           : {stats['total']}
  Operacionais    : {stats['operacionais']}
  Em manutenção   : {stats['em_manutencao']}
  Com defeito     : {stats['com_defeito']}
  Não distribuídos: {stats['nao_distribuidos']}
  Câmeras (total) : {stats['cameras_total']}
  Sensores (total): {stats['sensores_total']}
  Por shopping    : {json.dumps(stats['por_shopping'], indent=4, ensure_ascii=False)}
""")

        elif opcao == "12":
            print("\n📦 Tipos de equipamentos disponíveis:\n")
            for k, v in TIPOS_EQUIPAMENTO.items():
                print(f"  {k:<40} → {v}")

        elif opcao == "13":
            popular_equipamentos_iniciais()

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