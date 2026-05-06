"""
======================================================
  ShopControl - Monitoramento de Prédios
  Módulo 3: Monitoramento de Ambientes
======================================================

Este arquivo é responsável por monitorar tudo que
acontece DENTRO dos shoppings em tempo real:
  - Fluxo de pessoas por ambiente
  - Comportamentos suspeitos (IA)
  - Reconhecimento de rostos
  - Alertas e incidentes
  - Horários de pico
  - Temperatura e qualidade do ar

Banco de dados: dados/monitoramento_predios.json
"""

import json
import os
import uuid
import random
from datetime import datetime, timedelta


# ──────────────────────────────────────────────
#  CONFIGURAÇÃO
# ──────────────────────────────────────────────

PASTA_DADOS = os.path.join(os.path.dirname(__file__), "..", "dados")
ARQUIVO = os.path.join(PASTA_DADOS, "monitoramento_predios.json")

# Referências aos outros módulos
ARQUIVO_USUARIOS   = os.path.join(PASTA_DADOS, "usuarios.json")
ARQUIVO_AMBIENTES  = os.path.join(PASTA_DADOS, "ambientes.json")
ARQUIVO_EQUIPAMENTOS = os.path.join(PASTA_DADOS, "equipamentos.json")


# ──────────────────────────────────────────────
#  TIPOS DE EVENTOS
# ──────────────────────────────────────────────

# Nível de alerta de cada tipo de evento
TIPOS_EVENTO = {

    # ── Fluxo Normal ──
    "pessoa_detectada":           {"nivel": "info",    "descricao": "Pessoa detectada passando pelo ambiente"},
    "contagem_atualizada":        {"nivel": "info",    "descricao": "Contagem de pessoas no ambiente atualizada"},
    "horario_pico_identificado":  {"nivel": "info",    "descricao": "Horário de pico identificado no ambiente"},
    "ambiente_lotado":            {"nivel": "atencao", "descricao": "Ambiente acima da capacidade máxima"},
    "ambiente_vazio":             {"nivel": "info",    "descricao": "Ambiente sem pessoas detectadas"},
    "ambiente_normalizado":       {"nivel": "info",    "descricao": "Fluxo do ambiente voltou ao normal"},

    # ── Comportamentos Suspeitos (IA) ──
    "pessoa_parada_suspeita":     {"nivel": "atencao", "descricao": "Pessoa parada por tempo anormal em local incomum"},
    "movimentacao_suspeita":      {"nivel": "atencao", "descricao": "Movimentação suspeita detectada (andar em círculos, observar)"},
    "objeto_abandonado":          {"nivel": "critico", "descricao": "Objeto abandonado detectado no ambiente"},
    "aglomeracao_repentina":      {"nivel": "atencao", "descricao": "Aglomeração repentina de pessoas"},
    "pessoa_correndo":            {"nivel": "atencao", "descricao": "Pessoa correndo dentro do shopping"},
    "briga_suspeita":             {"nivel": "critico", "descricao": "Possível briga ou confronto detectado"},
    "furto_suspeito":             {"nivel": "critico", "descricao": "Comportamento de furto detectado pela IA"},
    "vandalismo":                 {"nivel": "critico", "descricao": "Possível vandalismo detectado"},
    "pessoa_caida":               {"nivel": "critico", "descricao": "Pessoa caída no chão detectada"},

    # ── Controle de Acesso ──
    "acesso_area_restrita":       {"nivel": "critico", "descricao": "Pessoa acessou área restrita sem autorização"},
    "tentativa_forcada_entrada":  {"nivel": "critico", "descricao": "Tentativa de forçar entrada em local restrito"},
    "acesso_fora_horario":        {"nivel": "atencao", "descricao": "Acesso em horário não autorizado"},
    "tailgating":                 {"nivel": "atencao", "descricao": "Pessoa passou junto com outra pela catraca (tailgating)"},

    # ── Reconhecimento (IA Facial) ──
    "rosto_identificado":         {"nivel": "info",    "descricao": "Rosto reconhecido — usuário cadastrado"},
    "rosto_nao_identificado":     {"nivel": "info",    "descricao": "Rosto não cadastrado no sistema"},
    "pessoa_lista_atencao":       {"nivel": "critico", "descricao": "Pessoa da lista de atenção detectada"},
    "usuario_bloqueado_detectado":{"nivel": "critico", "descricao": "Usuário com acesso bloqueado detectado nas dependências"},
    "reconhecimento_falhou":      {"nivel": "info",    "descricao": "Câmera não conseguiu reconhecer o rosto (baixa qualidade)"},

    # ── Ambiente / Sensores ──
    "temperatura_alta":           {"nivel": "atencao", "descricao": "Temperatura acima do limite no ambiente"},
    "temperatura_baixa":          {"nivel": "atencao", "descricao": "Temperatura abaixo do limite no ambiente"},
    "qualidade_ar_ruim":          {"nivel": "atencao", "descricao": "Qualidade do ar fora do padrão"},
    "fumaca_detectada":           {"nivel": "critico", "descricao": "Fumaça detectada — possível incêndio"},
    "gas_detectado":              {"nivel": "critico", "descricao": "Gás detectado no ambiente"},
    "sensor_presenca_ativado":    {"nivel": "info",    "descricao": "Sensor de presença ativado"},
    "iluminacao_falha":           {"nivel": "atencao", "descricao": "Falha na iluminação do ambiente"},

    # ── Equipamentos ──
    "camera_offline":             {"nivel": "atencao", "descricao": "Câmera ficou offline"},
    "camera_online":              {"nivel": "info",    "descricao": "Câmera voltou a funcionar"},
    "camera_obstruida":           {"nivel": "atencao", "descricao": "Câmera possivelmente obstruída ou danificada"},
    "sensor_falha":               {"nivel": "atencao", "descricao": "Sensor com falha de leitura"},
}

NIVEIS_ALERTA = ["info", "atencao", "critico"]

SHOPPINGS = ["Shopping 1", "Shopping 2", "Shopping 3", "Shopping 4"]

PERIODOS_DIA = {
    "madrugada": (0, 6),
    "manha":     (6, 12),
    "tarde":     (12, 18),
    "noite":     (18, 24),
}


# ──────────────────────────────────────────────
#  FUNÇÕES AUXILIARES
# ──────────────────────────────────────────────

def _garantir_pasta():
    if not os.path.exists(PASTA_DADOS):
        os.makedirs(PASTA_DADOS)


def _carregar():
    _garantir_pasta()
    if not os.path.exists(ARQUIVO):
        dados = {
            "metadados": {
                "criado_em": datetime.now().isoformat(),
                "total_eventos": 0,
                "versao": "1.0"
            },
            "eventos": [],
            "alertas_ativos": [],
            "contagem_atual": {}   # ambiente_id → quantidade de pessoas agora
        }
        _salvar(dados)
        return dados
    with open(ARQUIVO, "r", encoding="utf-8") as f:
        return json.load(f)


def _salvar(dados):
    _garantir_pasta()
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)


def _gerar_id():
    return str(uuid.uuid4())[:8].upper()


def _carregar_ambientes():
    """Carrega a lista de ambientes do ambientes.json."""
    if not os.path.exists(ARQUIVO_AMBIENTES):
        return []
    with open(ARQUIVO_AMBIENTES, "r", encoding="utf-8") as f:
        return json.load(f).get("ambientes", [])


def _carregar_usuarios():
    """Carrega a lista de usuários do usuarios.json."""
    if not os.path.exists(ARQUIVO_USUARIOS):
        return []
    with open(ARQUIVO_USUARIOS, "r", encoding="utf-8") as f:
        return json.load(f).get("usuarios", [])


def _periodo_do_dia(hora=None):
    """Retorna o período do dia (manhã, tarde, noite, madrugada)."""
    if hora is None:
        hora = datetime.now().hour
    for periodo, (inicio, fim) in PERIODOS_DIA.items():
        if inicio <= hora < fim:
            return periodo
    return "noite"


def _buscar_ambiente_por_id(id_ambiente):
    for a in _carregar_ambientes():
        if a["id"] == id_ambiente:
            return a
    return None


def _buscar_usuario_por_id(id_usuario):
    for u in _carregar_usuarios():
        if u["id"] == id_usuario:
            return u
    return None


# ──────────────────────────────────────────────
#  REGISTRAR EVENTO (Create)
# ──────────────────────────────────────────────

def registrar_evento(
    tipo_evento,
    shopping,
    id_ambiente,
    id_camera=None,
    id_usuario_detectado=None,
    quantidade_pessoas=None,
    temperatura=None,
    descricao_extra=None,
    confianca_ia=None,
    coordenadas_frame=None,
):
    """
    Registra um evento de monitoramento no JSON.

    Parâmetros:
        tipo_evento           : Tipo do evento (ver TIPOS_EVENTO)
        shopping              : Em qual shopping ocorreu
        id_ambiente           : ID do ambiente onde ocorreu
        id_camera             : ID da câmera/sensor que detectou (opcional)
        id_usuario_detectado  : ID do usuário reconhecido (opcional)
        quantidade_pessoas    : Contagem de pessoas no momento (opcional)
        temperatura           : Temperatura registrada (opcional)
        descricao_extra       : Texto livre adicional (opcional)
        confianca_ia          : % de confiança da IA na detecção (0-100)
        coordenadas_frame     : Posição no frame da câmera ex: {"x":120,"y":340}
    """

    if tipo_evento not in TIPOS_EVENTO:
        print(f"[ERRO] Tipo de evento '{tipo_evento}' desconhecido.")
        return None

    info_tipo   = TIPOS_EVENTO[tipo_evento]
    ambiente    = _buscar_ambiente_por_id(id_ambiente)
    usuario     = _buscar_usuario_por_id(id_usuario_detectado) if id_usuario_detectado else None
    agora       = datetime.now()

    evento = {
        "id":                   _gerar_id(),
        "tipo":                 tipo_evento,
        "nivel_alerta":         info_tipo["nivel"],
        "descricao":            info_tipo["descricao"],
        "descricao_extra":      descricao_extra,

        # ── Localização ──
        "shopping":             shopping,
        "id_ambiente":          id_ambiente,
        "nome_ambiente":        ambiente["nome"] if ambiente else "Desconhecido",
        "piso":                 ambiente.get("piso") if ambiente else None,
        "ala":                  ambiente.get("ala") if ambiente else None,

        # ── Tempo ──
        "data_hora":            agora.isoformat(),
        "data":                 agora.strftime("%Y-%m-%d"),
        "hora":                 agora.strftime("%H:%M:%S"),
        "periodo_dia":          _periodo_do_dia(agora.hour),
        "dia_semana":           agora.strftime("%A"),

        # ── Detecção ──
        "id_camera":            id_camera,
        "confianca_ia":         confianca_ia,      # Ex: 94.5 (%)
        "coordenadas_frame":    coordenadas_frame, # Posição no vídeo

        # ── Pessoa detectada ──
        "id_usuario_detectado": id_usuario_detectado,
        "nome_usuario":         usuario["nome"] if usuario else None,
        "perfil_usuario":       usuario["perfil"] if usuario else None,

        # ── Métricas ──
        "quantidade_pessoas":   quantidade_pessoas,
        "temperatura":          temperatura,

        # ── Resolução ──
        "resolvido":            False,
        "resolvido_em":         None,
        "resolvido_por":        None,
        "acao_tomada":          None,
    }

    dados = _carregar()
    dados["eventos"].append(evento)
    dados["metadados"]["total_eventos"] += 1
    dados["metadados"]["ultima_atualizacao"] = agora.isoformat()

    # Atualiza contagem atual do ambiente
    if quantidade_pessoas is not None:
        dados["contagem_atual"][id_ambiente] = {
            "quantidade": quantidade_pessoas,
            "atualizado_em": agora.isoformat(),
            "nome_ambiente": ambiente["nome"] if ambiente else "?"
        }

    # Se for crítico, adiciona aos alertas ativos
    if info_tipo["nivel"] == "critico":
        alerta = {
            "id_evento":    evento["id"],
            "tipo":         tipo_evento,
            "descricao":    info_tipo["descricao"],
            "shopping":     shopping,
            "ambiente":     evento["nome_ambiente"],
            "data_hora":    agora.isoformat(),
            "resolvido":    False,
        }
        dados["alertas_ativos"].append(alerta)
        print(f"[🚨 ALERTA CRÍTICO] {info_tipo['descricao']} — {evento['nome_ambiente']} ({shopping})")

    _salvar(dados)
    return evento


# ──────────────────────────────────────────────
#  LISTAR E BUSCAR (Read)
# ──────────────────────────────────────────────

def listar_eventos(
    filtro_shopping=None,
    filtro_nivel=None,
    filtro_tipo=None,
    filtro_ambiente=None,
    filtro_data=None,
    filtro_periodo=None,
    apenas_nao_resolvidos=False,
    limite=50
):
    """
    Lista eventos com filtros opcionais.

    Exemplos:
        listar_eventos(filtro_nivel="critico")
        listar_eventos(filtro_shopping="Shopping 1", filtro_data="2026-05-09")
        listar_eventos(apenas_nao_resolvidos=True)
    """
    dados = _carregar()
    eventos = dados["eventos"]

    if filtro_shopping:
        eventos = [e for e in eventos if e["shopping"] == filtro_shopping]
    if filtro_nivel:
        eventos = [e for e in eventos if e["nivel_alerta"] == filtro_nivel]
    if filtro_tipo:
        eventos = [e for e in eventos if filtro_tipo in e["tipo"]]
    if filtro_ambiente:
        eventos = [e for e in eventos if filtro_ambiente.lower() in e["nome_ambiente"].lower()]
    if filtro_data:
        eventos = [e for e in eventos if e["data"] == filtro_data]
    if filtro_periodo:
        eventos = [e for e in eventos if e["periodo_dia"] == filtro_periodo]
    if apenas_nao_resolvidos:
        eventos = [e for e in eventos if not e["resolvido"]]

    # Mais recentes primeiro
    eventos = sorted(eventos, key=lambda e: e["data_hora"], reverse=True)
    return eventos[:limite]


def listar_alertas_ativos():
    """Retorna todos os alertas críticos ainda não resolvidos."""
    dados = _carregar()
    return [a for a in dados["alertas_ativos"] if not a["resolvido"]]


def buscar_evento_por_id(id_evento):
    dados = _carregar()
    for e in dados["eventos"]:
        if e["id"] == id_evento:
            return e
    return None


def contagem_atual_ambientes(shopping=None):
    """
    Retorna quantas pessoas estão agora em cada ambiente.
    Usado pelo dashboard para mostrar ocupação em tempo real.
    """
    dados = _carregar()
    contagem = dados.get("contagem_atual", {})
    if shopping:
        ambientes = _carregar_ambientes()
        ids_shopping = {a["id"] for a in ambientes if a["shopping"] == shopping}
        contagem = {k: v for k, v in contagem.items() if k in ids_shopping}
    return contagem


def eventos_de_hoje(shopping=None):
    """Atalho: retorna todos os eventos de hoje."""
    hoje = datetime.now().strftime("%Y-%m-%d")
    return listar_eventos(filtro_shopping=shopping, filtro_data=hoje, limite=500)


def eventos_criticos_nao_resolvidos():
    """Atalho: eventos críticos que ainda precisam de ação."""
    return listar_eventos(filtro_nivel="critico", apenas_nao_resolvidos=True, limite=100)


# ──────────────────────────────────────────────
#  RESOLVER EVENTO (Update)
# ──────────────────────────────────────────────

def resolver_evento(id_evento, resolvido_por, acao_tomada):
    """
    Marca um evento como resolvido.

    Exemplo:
        resolver_evento("ABC12345", "Carlos Lima", "Segurança foi ao local, situação normalizada")
    """
    dados = _carregar()

    for i, e in enumerate(dados["eventos"]):
        if e["id"] == id_evento:
            dados["eventos"][i]["resolvido"]    = True
            dados["eventos"][i]["resolvido_em"] = datetime.now().isoformat()
            dados["eventos"][i]["resolvido_por"] = resolvido_por
            dados["eventos"][i]["acao_tomada"]  = acao_tomada
            break
    else:
        print(f"[ERRO] Evento '{id_evento}' não encontrado.")
        return False

    # Remove dos alertas ativos se estiver lá
    for i, a in enumerate(dados["alertas_ativos"]):
        if a["id_evento"] == id_evento:
            dados["alertas_ativos"][i]["resolvido"] = True
            break

    _salvar(dados)
    print(f"[OK] Evento '{id_evento}' marcado como resolvido.")
    return True


# ──────────────────────────────────────────────
#  ESTATÍSTICAS E ANÁLISES
# ──────────────────────────────────────────────

def obter_estatisticas(shopping=None):
    """
    Retorna análises e estatísticas do monitoramento.
    Usado pelo dashboard e pelo módulo de mapa de calor.
    """
    eventos = listar_eventos(filtro_shopping=shopping, limite=99999)

    if not eventos:
        return {"total": 0}

    stats = {
        "total_eventos":        len(eventos),
        "por_nivel":            {},
        "por_tipo":             {},
        "por_shopping":         {},
        "por_ambiente":         {},
        "por_periodo_dia":      {},
        "por_dia_semana":       {},
        "alertas_ativos":       len(listar_alertas_ativos()),
        "eventos_criticos":     0,
        "nao_resolvidos":       0,
        "ambientes_mais_movimentados": [],
        "horarios_pico":        {},
    }

    contagem_ambientes = {}

    for e in eventos:
        nivel   = e.get("nivel_alerta", "info")
        tipo    = e.get("tipo", "?")
        shop    = e.get("shopping", "?")
        amb     = e.get("nome_ambiente", "?")
        periodo = e.get("periodo_dia", "?")
        dia     = e.get("dia_semana", "?")
        hora    = e.get("hora", "00:00:00")[:2]  # só a hora

        for chave, valor in [
            ("por_nivel", nivel), ("por_tipo", tipo),
            ("por_shopping", shop), ("por_ambiente", amb),
            ("por_periodo_dia", periodo), ("por_dia_semana", dia)
        ]:
            stats[chave][valor] = stats[chave].get(valor, 0) + 1

        if nivel == "critico":
            stats["eventos_criticos"] += 1
        if not e.get("resolvido"):
            stats["nao_resolvidos"] += 1

        # Contagem por ambiente para ranking
        contagem_ambientes[amb] = contagem_ambientes.get(amb, 0) + 1

        # Horários de pico
        stats["horarios_pico"][hora] = stats["horarios_pico"].get(hora, 0) + 1

    # Top 5 ambientes mais movimentados
    ranking = sorted(contagem_ambientes.items(), key=lambda x: x[1], reverse=True)
    stats["ambientes_mais_movimentados"] = ranking[:5]

    return stats


def ambientes_sem_monitoramento():
    """
    Retorna ambientes que nunca geraram nenhum evento —
    podem estar sem câmera funcionando.
    """
    todos_ambientes = _carregar_ambientes()
    dados = _carregar()
    ids_com_evento = {e["id_ambiente"] for e in dados["eventos"]}
    sem_evento = [a for a in todos_ambientes if a["id"] not in ids_com_evento]
    return sem_evento


# ──────────────────────────────────────────────
#  LIMPAR HISTÓRICO (Delete)
# ──────────────────────────────────────────────

def limpar_eventos_antigos(dias=90):
    """
    Remove eventos mais antigos que X dias.
    Recomendado rodar periodicamente para não crescer demais.
    """
    dados = _carregar()
    corte = datetime.now() - timedelta(days=dias)
    antes = len(dados["eventos"])
    dados["eventos"] = [
        e for e in dados["eventos"]
        if datetime.fromisoformat(e["data_hora"]) >= corte
    ]
    removidos = antes - len(dados["eventos"])
    dados["metadados"]["total_eventos"] = len(dados["eventos"])
    _salvar(dados)
    print(f"[OK] {removidos} evento(s) removidos (mais de {dias} dias).")
    return removidos


# ──────────────────────────────────────────────
#  SIMULAÇÃO — Popular com dados de exemplo
# ──────────────────────────────────────────────

def simular_monitoramento(quantidade=50):
    """
    Gera eventos simulados para testar o sistema.
    Simula o que as câmeras e sensores gerariam em tempo real.
    """
    print(f"\n[INFO] Simulando {quantidade} eventos de monitoramento...")

    ambientes = _carregar_ambientes()
    if not ambientes:
        print("[ERRO] Nenhum ambiente cadastrado. Rode o ambientes.py primeiro!")
        return

    tipos = list(TIPOS_EVENTO.keys())

    # Distribuição realista — maioria são eventos normais, poucos críticos
    pesos = []
    for t in tipos:
        nivel = TIPOS_EVENTO[t]["nivel"]
        if nivel == "info":      pesos.append(60)
        elif nivel == "atencao": pesos.append(25)
        else:                    pesos.append(15)

    for i in range(quantidade):
        ambiente = random.choice(ambientes)
        tipo = random.choices(tipos, weights=pesos, k=1)[0]

        registrar_evento(
            tipo_evento=tipo,
            shopping=ambiente["shopping"],
            id_ambiente=ambiente["id"],
            quantidade_pessoas=random.randint(0, ambiente.get("capacidade_pessoas", 50) or 50),
            temperatura=round(random.uniform(18.0, 32.0), 1),
            confianca_ia=round(random.uniform(75.0, 99.9), 1),
        )

    print(f"[OK] {quantidade} eventos simulados com sucesso!")
    stats = obter_estatisticas()
    print(f"\nTotal de eventos: {stats['total_eventos']}")
    print(f"Alertas críticos: {stats['eventos_criticos']}")
    print(f"Alertas ativos  : {stats['alertas_ativos']}")


# ──────────────────────────────────────────────
#  MENU INTERATIVO
# ──────────────────────────────────────────────

def _exibir_evento(e):
    icones = {"info": "ℹ️ ", "atencao": "⚠️ ", "critico": "🚨"}
    print("\n" + "─" * 58)
    print(f"  {icones.get(e['nivel_alerta'],'  ')} [{e['nivel_alerta'].upper()}] {e['tipo']}")
    print(f"  ID        : {e['id']}")
    print(f"  Descrição : {e['descricao']}")
    print(f"  Local     : {e['nome_ambiente']} | {e['piso']} | {e['shopping']}")
    print(f"  Data/Hora : {e['data_hora'][:19].replace('T',' ')} ({e['periodo_dia']})")
    if e.get("nome_usuario"):
        print(f"  Usuário   : {e['nome_usuario']} ({e['perfil_usuario']})")
    if e.get("quantidade_pessoas") is not None:
        print(f"  Pessoas   : {e['quantidade_pessoas']}")
    if e.get("temperatura"):
        print(f"  Temp.     : {e['temperatura']}°C")
    if e.get("confianca_ia"):
        print(f"  IA conf.  : {e['confianca_ia']}%")
    status = "✅ Resolvido" if e["resolvido"] else "❌ Pendente"
    print(f"  Status    : {status}")
    if e["resolvido"]:
        print(f"  Ação      : {e.get('acao_tomada','')}")
    print("─" * 58)


def menu():
    while True:
        alertas = listar_alertas_ativos()
        print(f"\n╔══════════════════════════════════════════╗")
        print(f"║   ShopControl — Monitoramento Prédios    ║")
        if alertas:
            print(f"║   🚨 {len(alertas)} ALERTA(S) CRÍTICO(S) ATIVO(S)       ║")
        print(f"╠══════════════════════════════════════════╣")
        print(f"║  1.  Registrar evento manualmente         ║")
        print(f"║  2.  Ver eventos de hoje                  ║")
        print(f"║  3.  Ver alertas críticos ativos          ║")
        print(f"║  4.  Buscar por ambiente                  ║")
        print(f"║  5.  Buscar por shopping                  ║")
        print(f"║  6.  Buscar por nível (info/atencao/crit) ║")
        print(f"║  7.  Buscar por período do dia            ║")
        print(f"║  8.  Resolver um evento                   ║")
        print(f"║  9.  Estatísticas gerais                  ║")
        print(f"║  10. Contagem atual por ambiente          ║")
        print(f"║  11. Ambientes sem monitoramento          ║")
        print(f"║  12. Simular eventos (teste)              ║")
        print(f"║  13. Limpar eventos antigos               ║")
        print(f"║  0.  Sair                                 ║")
        print(f"╚══════════════════════════════════════════╝")

        opcao = input("\nEscolha: ").strip()

        if opcao == "1":
            print(f"\nShoppings: {', '.join(SHOPPINGS)}")
            shop = input("Shopping: ").strip()
            amb_id = input("ID do ambiente: ").strip()
            print(f"\nTipos disponíveis:")
            for i, t in enumerate(TIPOS_EVENTO.keys()):
                print(f"  {i+1}. {t}")
            idx = input("Número do tipo: ").strip()
            tipo = list(TIPOS_EVENTO.keys())[int(idx)-1]
            qtd_str = input("Quantidade de pessoas (Enter pular): ").strip()
            temp_str = input("Temperatura °C (Enter pular): ").strip()
            extra = input("Descrição extra (Enter pular): ").strip() or None
            registrar_evento(
                tipo_evento=tipo,
                shopping=shop,
                id_ambiente=amb_id,
                quantidade_pessoas=int(qtd_str) if qtd_str.isdigit() else None,
                temperatura=float(temp_str) if temp_str else None,
                descricao_extra=extra,
            )

        elif opcao == "2":
            eventos = eventos_de_hoje()
            print(f"\n── {len(eventos)} evento(s) hoje ──")
            for e in eventos[:20]:
                _exibir_evento(e)

        elif opcao == "3":
            alertas = listar_alertas_ativos()
            print(f"\n── {len(alertas)} alerta(s) crítico(s) ativo(s) ──")
            for a in alertas:
                print(f"\n  🚨 [{a['shopping']}] {a['ambiente']}")
                print(f"     {a['descricao']}")
                print(f"     {a['data_hora'][:19].replace('T',' ')}")
                print(f"     ID do evento: {a['id_evento']}")

        elif opcao == "4":
            nome = input("Nome do ambiente (parcial): ").strip()
            eventos = listar_eventos(filtro_ambiente=nome, limite=20)
            print(f"\n── {len(eventos)} evento(s) ──")
            for e in eventos:
                _exibir_evento(e)

        elif opcao == "5":
            print(f"Shoppings: {', '.join(SHOPPINGS)}")
            shop = input("Shopping: ").strip()
            eventos = listar_eventos(filtro_shopping=shop, limite=20)
            print(f"\n── {len(eventos)} evento(s) no {shop} ──")
            for e in eventos:
                _exibir_evento(e)

        elif opcao == "6":
            print("Níveis: info, atencao, critico")
            nivel = input("Nível: ").strip()
            eventos = listar_eventos(filtro_nivel=nivel, limite=20)
            print(f"\n── {len(eventos)} evento(s) com nível '{nivel}' ──")
            for e in eventos:
                _exibir_evento(e)

        elif opcao == "7":
            print("Períodos: manha, tarde, noite, madrugada")
            periodo = input("Período: ").strip()
            eventos = listar_eventos(filtro_periodo=periodo, limite=20)
            print(f"\n── {len(eventos)} evento(s) no período '{periodo}' ──")
            for e in eventos:
                _exibir_evento(e)

        elif opcao == "8":
            id_ev = input("ID do evento: ").strip()
            resp = input("Resolvido por (nome): ").strip()
            acao = input("Ação tomada: ").strip()
            resolver_evento(id_ev, resp, acao)

        elif opcao == "9":
            print(f"\nShoppings: {', '.join(SHOPPINGS)} (Enter = todos)")
            shop = input("Shopping (opcional): ").strip() or None
            s = obter_estatisticas(shopping=shop)
            print(f"\n── ESTATÍSTICAS ──")
            print(f"  Total de eventos    : {s['total_eventos']}")
            print(f"  Eventos críticos    : {s['eventos_criticos']}")
            print(f"  Alertas ativos      : {s['alertas_ativos']}")
            print(f"  Não resolvidos      : {s['nao_resolvidos']}")
            print(f"  Por nível           : {s['por_nivel']}")
            print(f"  Por período do dia  : {s['por_periodo_dia']}")
            print(f"  Top ambientes       : {s['ambientes_mais_movimentados']}")
            print(f"  Horários de pico    : {dict(sorted(s['horarios_pico'].items()))}")

        elif opcao == "10":
            print(f"\nShoppings: {', '.join(SHOPPINGS)} (Enter = todos)")
            shop = input("Shopping (opcional): ").strip() or None
            contagem = contagem_atual_ambientes(shopping=shop)
            print(f"\n── OCUPAÇÃO ATUAL ({len(contagem)} ambientes) ──")
            for id_amb, info in sorted(contagem.items(), key=lambda x: x[1]["quantidade"], reverse=True):
                print(f"  {info['nome_ambiente']}: {info['quantidade']} pessoas")

        elif opcao == "11":
            sem = ambientes_sem_monitoramento()
            print(f"\n── {len(sem)} ambiente(s) sem nenhum evento registrado ──")
            for a in sem[:15]:
                print(f"  {a['shopping']} | {a['piso']} | {a['nome']} (ID: {a['id']})")

        elif opcao == "12":
            qtd = input("Quantos eventos simular? [50]: ").strip()
            simular_monitoramento(int(qtd) if qtd.isdigit() else 50)

        elif opcao == "13":
            dias = input("Remover eventos mais antigos que quantos dias? [90]: ").strip()
            limpar_eventos_antigos(int(dias) if dias.isdigit() else 90)

        elif opcao == "0":
            print("Até logo!")
            break
        else:
            print("[AVISO] Opção inválida.")


if __name__ == "__main__":
    menu()