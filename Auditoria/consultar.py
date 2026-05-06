"""
=============================================================
  SHOPCONTROL - MÓDULO DE AUDITORIA
  Arquivo: consultar.py
  Descrição: Sistema completo de consultas e relatórios
             de auditoria do ShopControl
=============================================================
"""

import json
import os
from datetime import datetime, timedelta
from collections import Counter

# ─────────────────────────────────────────────
#   CONFIGURAÇÕES
# ─────────────────────────────────────────────

PASTA_DADOS       = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dados")
ARQUIVO_REGISTROS = os.path.join(PASTA_DADOS, "auditoria_registros.json")
ARQUIVO_ALERTAS   = os.path.join(PASTA_DADOS, "auditoria_alertas.json")
PASTA_RELATORIOS  = os.path.join(PASTA_DADOS, "relatorios")

os.makedirs(PASTA_RELATORIOS, exist_ok=True)

# ─────────────────────────────────────────────
#   CARREGAMENTO DE DADOS
# ─────────────────────────────────────────────

def _carregar_registros() -> list:
    if not os.path.exists(ARQUIVO_REGISTROS):
        return []
    with open(ARQUIVO_REGISTROS, "r", encoding="utf-8") as f:
        dados = json.load(f)
    return dados.get("registros", [])

def _carregar_alertas() -> dict:
    if not os.path.exists(ARQUIVO_ALERTAS):
        return {"alertas_ativos": [], "alertas_resolvidos": []}
    with open(ARQUIVO_ALERTAS, "r", encoding="utf-8") as f:
        return json.load(f)

def _salvar_relatorio(nome_arquivo: str, conteudo: str) -> str:
    caminho = os.path.join(PASTA_RELATORIOS, nome_arquivo)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(conteudo)
    return caminho

# ─────────────────────────────────────────────
#   FILTROS BASE
# ─────────────────────────────────────────────

def _filtrar(
    registros: list,
    nivel: str = None,
    categoria: str = None,
    usuario: str = None,
    shopping: str = None,
    resultado: str = None,
    data_inicio: str = None,
    data_fim: str = None,
    hora_inicio: str = None,
    hora_fim: str = None,
    periodo_dia: str = None,
    acao_contem: str = None,
) -> list:
    r = registros

    if nivel:
        r = [x for x in r if x.get("nivel") == nivel.upper()]
    if categoria:
        r = [x for x in r if categoria.lower() in x.get("categoria", "").lower()]
    if usuario:
        r = [x for x in r if usuario.lower() in x.get("usuario_sistema", "").lower()]
    if shopping:
        r = [x for x in r if x.get("shopping") and shopping.lower() in x["shopping"].lower()]
    if resultado:
        r = [x for x in r if x.get("resultado") == resultado.upper()]
    if data_inicio:
        r = [x for x in r if x.get("timestamp", "") >= data_inicio]
    if data_fim:
        r = [x for x in r if x.get("timestamp", "") <= data_fim + "T23:59:59"]
    if hora_inicio:
        r = [x for x in r if x.get("hora", "00:00:00") >= hora_inicio]
    if hora_fim:
        r = [x for x in r if x.get("hora", "00:00:00") <= hora_fim]
    if periodo_dia:
        r = [x for x in r if x.get("periodo_dia", "").lower() == periodo_dia.lower()]
    if acao_contem:
        r = [x for x in r if acao_contem.lower() in x.get("acao", "").lower()]

    return sorted(r, key=lambda x: x.get("timestamp", ""), reverse=True)

# ─────────────────────────────────────────────
#   CONSULTAS RÁPIDAS
# ─────────────────────────────────────────────

def consulta_hoje() -> list:
    hoje = datetime.now().strftime("%Y-%m-%d")
    return _filtrar(_carregar_registros(), data_inicio=hoje, data_fim=hoje)

def consulta_semana() -> list:
    inicio = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    fim = datetime.now().strftime("%Y-%m-%d")
    return _filtrar(_carregar_registros(), data_inicio=inicio, data_fim=fim)

def consulta_mes() -> list:
    inicio = datetime.now().replace(day=1).strftime("%Y-%m-%d")
    fim = datetime.now().strftime("%Y-%m-%d")
    return _filtrar(_carregar_registros(), data_inicio=inicio, data_fim=fim)

def consulta_por_usuario(usuario: str) -> list:
    return _filtrar(_carregar_registros(), usuario=usuario)

def consulta_por_shopping(shopping: str) -> list:
    return _filtrar(_carregar_registros(), shopping=shopping)

def consulta_criticos() -> list:
    r = _carregar_registros()
    return _filtrar(r, nivel="CRITICO") + _filtrar(r, nivel="ERRO")

def consulta_falhas() -> list:
    return _filtrar(_carregar_registros(), resultado="FALHA")

def consulta_acessos_negados() -> list:
    return _filtrar(_carregar_registros(), resultado="NEGADO")

def consulta_por_periodo_dia(periodo: str) -> list:
    """Período: Manhã, Tarde, Noite, Madrugada"""
    return _filtrar(_carregar_registros(), periodo_dia=periodo)

def consulta_por_hora(hora_inicio: str, hora_fim: str) -> list:
    """Ex: hora_inicio='08:00:00', hora_fim='12:00:00'"""
    return _filtrar(_carregar_registros(), hora_inicio=hora_inicio, hora_fim=hora_fim)

def consulta_livre(
    nivel=None, categoria=None, usuario=None, shopping=None,
    resultado=None, data_inicio=None, data_fim=None,
    hora_inicio=None, hora_fim=None, periodo_dia=None, acao_contem=None
) -> list:
    return _filtrar(
        _carregar_registros(),
        nivel=nivel, categoria=categoria, usuario=usuario,
        shopping=shopping, resultado=resultado,
        data_inicio=data_inicio, data_fim=data_fim,
        hora_inicio=hora_inicio, hora_fim=hora_fim,
        periodo_dia=periodo_dia, acao_contem=acao_contem
    )

# ─────────────────────────────────────────────
#   ANÁLISES E MÉTRICAS
# ─────────────────────────────────────────────

def _analisar(registros: list) -> dict:
    if not registros:
        return {}

    niveis    = Counter(r.get("nivel") for r in registros)
    cats      = Counter(r.get("categoria") for r in registros)
    usuarios  = Counter(r.get("usuario_sistema") for r in registros)
    shoppings = Counter(r.get("shopping") for r in registros if r.get("shopping"))
    resultados= Counter(r.get("resultado") for r in registros)
    periodos  = Counter(r.get("periodo_dia") for r in registros)
    horas     = Counter(r.get("hora", "")[:2] for r in registros)

    hora_pico = max(horas, key=horas.get) + "h" if horas else "-"

    return {
        "total": len(registros),
        "por_nivel": dict(niveis),
        "por_categoria": dict(cats),
        "por_resultado": dict(resultados),
        "por_periodo_dia": dict(periodos),
        "hora_pico": hora_pico,
        "usuario_mais_ativo": usuarios.most_common(1)[0] if usuarios else ("-", 0),
        "shopping_mais_registros": shoppings.most_common(1)[0] if shoppings else ("-", 0),
        "top_usuarios": usuarios.most_common(5),
        "top_categorias": cats.most_common(5),
    }

# ─────────────────────────────────────────────
#   GERAÇÃO DE RELATÓRIOS (TXT)
# ─────────────────────────────────────────────

def _linha(char="─", tam=62):
    return char * tam

def _cabecalho(titulo: str, subtitulo: str = "") -> str:
    agora = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    linhas = []
    linhas.append(_linha("═"))
    linhas.append(f"  SHOPCONTROL — SISTEMA DE SEGURANÇA INTELIGENTE")
    linhas.append(f"  {titulo}")
    if subtitulo:
        linhas.append(f"  {subtitulo}")
    linhas.append(f"  Gerado em: {agora}")
    linhas.append(_linha("═"))
    return "\n".join(linhas)

def _bloco_analise(analise: dict) -> str:
    if not analise:
        return "  Nenhum dado para análise.\n"
    linhas = []
    linhas.append(f"\n  📊 RESUMO GERAL")
    linhas.append(_linha())
    linhas.append(f"  Total de registros    : {analise['total']}")
    linhas.append(f"  Hora de maior atividade: {analise['hora_pico']}")

    u, qt = analise["usuario_mais_ativo"]
    linhas.append(f"  Usuário mais ativo    : {u} ({qt} ações)")

    sh, qt2 = analise["shopping_mais_registros"]
    linhas.append(f"  Shopping + registros  : {sh} ({qt2} registros)")

    linhas.append(f"\n  Por resultado:")
    for k, v in analise["por_resultado"].items():
        barra = "█" * min(v, 30)
        linhas.append(f"    {k:10}: {barra} {v}")

    linhas.append(f"\n  Por nível:")
    icones = {"INFO":"ℹ", "AVISO":"⚠", "ALERTA":"!", "CRITICO":"✖", "ERRO":"✖✖"}
    for k, v in analise["por_nivel"].items():
        ic = icones.get(k, "•")
        linhas.append(f"    {ic} {k:10}: {v}")

    linhas.append(f"\n  Por período do dia:")
    for k, v in analise["por_periodo_dia"].items():
        linhas.append(f"    {k:12}: {v}")

    linhas.append(f"\n  Top categorias:")
    for cat, qt in analise["top_categorias"]:
        linhas.append(f"    • {cat}: {qt}")

    return "\n".join(linhas)

def _listar_registros_txt(registros: list, limite: int = 50) -> str:
    icones = {"INFO":"ℹ", "AVISO":"⚠", "ALERTA":"!", "CRITICO":"✖", "ERRO":"✖✖"}
    linhas = []
    for r in registros[:limite]:
        ic = icones.get(r.get("nivel",""), "•")
        linhas.append(f"\n  {ic} [{r.get('id','-')}] {r.get('data','-')} {r.get('hora','-')}")
        linhas.append(f"     Ação     : {r.get('acao','-')}")
        linhas.append(f"     Categoria: {r.get('categoria','-')}  |  Nível: {r.get('nivel','-')}  |  Resultado: {r.get('resultado','-')}")
        linhas.append(f"     Usuário  : {r.get('usuario_sistema','-')}  |  Shopping: {r.get('shopping') or '-'}")
        if r.get("observacao"):
            linhas.append(f"     Obs      : {r['observacao']}")
        if r.get("dado_anterior") or r.get("dado_novo"):
            linhas.append(f"     Antes    : {json.dumps(r.get('dado_anterior'), ensure_ascii=False)}")
            linhas.append(f"     Depois   : {json.dumps(r.get('dado_novo'), ensure_ascii=False)}")
        linhas.append(f"     {_linha('·', 55)}")
    return "\n".join(linhas)

# ── Relatório Diário ──────────────────────────

def relatorio_diario(data: str = None, salvar: bool = True) -> str:
    data = data or datetime.now().strftime("%Y-%m-%d")
    regs = _filtrar(_carregar_registros(), data_inicio=data, data_fim=data)
    alertas = _carregar_alertas()
    alertas_dia = [a for a in alertas["alertas_ativos"]
                   if a.get("timestamp", "").startswith(data)]
    analise = _analisar(regs)

    linhas = [_cabecalho(
        "RELATÓRIO DIÁRIO DE AUDITORIA",
        f"Data: {datetime.strptime(data, '%Y-%m-%d').strftime('%d/%m/%Y')}"
    )]

    linhas.append(_bloco_analise(analise))

    linhas.append(f"\n\n  🚨 ALERTAS ATIVOS DO DIA ({len(alertas_dia)})")
    linhas.append(_linha())
    if alertas_dia:
        for a in alertas_dia:
            linhas.append(f"  [{a['id']}] {a['nivel']} — {a['acao']}")
            linhas.append(f"       Shopping: {a.get('shopping','-')} | {a.get('observacao','-')}")
    else:
        linhas.append("  Nenhum alerta ativo neste dia. ✅")

    linhas.append(f"\n\n  📋 DETALHAMENTO DOS REGISTROS")
    linhas.append(_linha())
    linhas.append(_listar_registros_txt(regs))

    linhas.append(f"\n\n{_linha('═')}")
    linhas.append(f"  Fim do relatório — {len(regs)} registro(s) no total")
    linhas.append(_linha("═"))

    conteudo = "\n".join(linhas)
    if salvar:
        nome = f"relatorio_diario_{data}.txt"
        caminho = _salvar_relatorio(nome, conteudo)
        print(f"\n  💾 Relatório salvo em: {caminho}")
    return conteudo

# ── Relatório de Segurança ────────────────────

def relatorio_seguranca(dias: int = 7, shopping: str = None, salvar: bool = True) -> str:
    inicio = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d")
    fim = datetime.now().strftime("%Y-%m-%d")
    todos = _filtrar(_carregar_registros(), data_inicio=inicio, data_fim=fim, shopping=shopping)
    criticos = [r for r in todos if r.get("nivel") in ["CRITICO", "ERRO"]]
    alertas_r = [r for r in todos if r.get("nivel") == "ALERTA"]
    negados   = [r for r in todos if r.get("resultado") == "NEGADO"]
    falhas    = [r for r in todos if r.get("resultado") == "FALHA"]
    alertas_db = _carregar_alertas()

    linhas = [_cabecalho(
        "RELATÓRIO DE SEGURANÇA",
        f"Período: últimos {dias} dias | Shopping: {shopping or 'Todos'}"
    )]

    linhas.append(f"\n  🔐 RESUMO DE SEGURANÇA")
    linhas.append(_linha())
    linhas.append(f"  Registros críticos/erros : {len(criticos)}")
    linhas.append(f"  Alertas de segurança     : {len(alertas_r)}")
    linhas.append(f"  Acessos negados          : {len(negados)}")
    linhas.append(f"  Falhas registradas       : {len(falhas)}")
    linhas.append(f"  Alertas ativos agora     : {len(alertas_db['alertas_ativos'])}")
    linhas.append(f"  Alertas resolvidos       : {len(alertas_db['alertas_resolvidos'])}")

    linhas.append(f"\n\n  🔴 OCORRÊNCIAS CRÍTICAS/ERROS ({len(criticos)})")
    linhas.append(_linha())
    linhas.append(_listar_registros_txt(criticos, 30))

    linhas.append(f"\n\n  🚫 ACESSOS NEGADOS ({len(negados)})")
    linhas.append(_linha())
    linhas.append(_listar_registros_txt(negados, 20))

    linhas.append(f"\n\n  ⚠ ALERTAS ({len(alertas_r)})")
    linhas.append(_linha())
    linhas.append(_listar_registros_txt(alertas_r, 20))

    linhas.append(f"\n\n  🚨 ALERTAS AINDA ATIVOS NO SISTEMA")
    linhas.append(_linha())
    ativos = alertas_db["alertas_ativos"]
    if ativos:
        for a in ativos:
            linhas.append(f"  [{a['id']}] {a['nivel']} — {a['acao']}")
            linhas.append(f"       {a.get('observacao') or a.get('detalhes','')}")
    else:
        linhas.append("  Nenhum alerta ativo no momento. ✅")

    linhas.append(f"\n\n{_linha('═')}")
    linhas.append(f"  Fim do relatório de segurança")
    linhas.append(_linha("═"))

    conteudo = "\n".join(linhas)
    if salvar:
        slug = (shopping or "todos").replace(" ", "_").lower()
        nome = f"relatorio_seguranca_{slug}_{fim}.txt"
        caminho = _salvar_relatorio(nome, conteudo)
        print(f"\n  💾 Relatório salvo em: {caminho}")
    return conteudo

# ── Relatório por Usuário ─────────────────────

def relatorio_usuario(usuario: str, salvar: bool = True) -> str:
    regs = consulta_por_usuario(usuario)
    analise = _analisar(regs)

    linhas = [_cabecalho(
        "RELATÓRIO DE ATIVIDADE POR USUÁRIO",
        f"Usuário: {usuario} | Total de ações: {len(regs)}"
    )]

    if not regs:
        linhas.append(f"\n  Nenhum registro encontrado para '{usuario}'.")
    else:
        linhas.append(_bloco_analise(analise))

        # Linha do tempo resumida
        linhas.append(f"\n\n  🕐 LINHA DO TEMPO (últimas 30 ações)")
        linhas.append(_linha())
        linhas.append(_listar_registros_txt(regs, 30))

        # Ações suspeitas do usuário
        suspeitas = [r for r in regs if r.get("nivel") in ["ALERTA","CRITICO","ERRO"]
                     or r.get("resultado") in ["FALHA","NEGADO"]]
        linhas.append(f"\n\n  ⚠ AÇÕES SUSPEITAS DO USUÁRIO ({len(suspeitas)})")
        linhas.append(_linha())
        if suspeitas:
            linhas.append(_listar_registros_txt(suspeitas))
        else:
            linhas.append("  Nenhuma ação suspeita registrada. ✅")

    linhas.append(f"\n\n{_linha('═')}")
    linhas.append("  Fim do relatório de usuário")
    linhas.append(_linha("═"))

    conteudo = "\n".join(linhas)
    if salvar:
        slug = usuario.replace(" ", "_").lower()
        nome = f"relatorio_usuario_{slug}.txt"
        caminho = _salvar_relatorio(nome, conteudo)
        print(f"\n  💾 Relatório salvo em: {caminho}")
    return conteudo

# ── Relatório por Shopping ────────────────────

def relatorio_shopping(shopping: str, dias: int = 30, salvar: bool = True) -> str:
    inicio = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d")
    fim = datetime.now().strftime("%Y-%m-%d")
    regs = _filtrar(_carregar_registros(), shopping=shopping, data_inicio=inicio, data_fim=fim)
    analise = _analisar(regs)

    linhas = [_cabecalho(
        f"RELATÓRIO POR SHOPPING",
        f"{shopping} | Últimos {dias} dias"
    )]

    linhas.append(_bloco_analise(analise))

    # Alertas desse shopping
    alertas_db = _carregar_alertas()
    alertas_sh = [a for a in alertas_db["alertas_ativos"]
                  if shopping.lower() in (a.get("shopping") or "").lower()]
    linhas.append(f"\n\n  🚨 ALERTAS ATIVOS NESTE SHOPPING ({len(alertas_sh)})")
    linhas.append(_linha())
    if alertas_sh:
        for a in alertas_sh:
            linhas.append(f"  [{a['id']}] {a['nivel']} — {a['acao']}")
    else:
        linhas.append("  Nenhum alerta ativo. ✅")

    linhas.append(f"\n\n  📋 REGISTROS DO SHOPPING")
    linhas.append(_linha())
    linhas.append(_listar_registros_txt(regs, 40))

    linhas.append(f"\n\n{_linha('═')}")
    linhas.append(f"  Fim do relatório — {shopping}")
    linhas.append(_linha("═"))

    conteudo = "\n".join(linhas)
    if salvar:
        slug = shopping.replace(" ", "_").lower()
        nome = f"relatorio_shopping_{slug}_{fim}.txt"
        caminho = _salvar_relatorio(nome, conteudo)
        print(f"\n  💾 Relatório salvo em: {caminho}")
    return conteudo

# ── Relatório Executivo Mensal ────────────────

def relatorio_executivo_mensal(salvar: bool = True) -> str:
    agora = datetime.now()
    inicio = agora.replace(day=1).strftime("%Y-%m-%d")
    fim = agora.strftime("%Y-%m-%d")
    todos = _filtrar(_carregar_registros(), data_inicio=inicio, data_fim=fim)
    analise = _analisar(todos)
    alertas_db = _carregar_alertas()

    mes_nome = agora.strftime("%B/%Y")
    linhas = [_cabecalho(
        "RELATÓRIO EXECUTIVO MENSAL",
        f"Período: {mes_nome} | Rede de 4 Shoppings"
    )]

    linhas.append(f"\n  📈 VISÃO GERAL DA REDE")
    linhas.append(_linha())
    linhas.append(f"  Total de eventos registrados : {analise.get('total', 0)}")
    linhas.append(f"  Alertas críticos             : {analise.get('por_nivel',{}).get('CRITICO',0)}")
    linhas.append(f"  Erros do sistema             : {analise.get('por_nivel',{}).get('ERRO',0)}")
    linhas.append(f"  Falhas totais                : {analise.get('por_resultado',{}).get('FALHA',0)}")
    linhas.append(f"  Acessos negados              : {analise.get('por_resultado',{}).get('NEGADO',0)}")
    linhas.append(f"  Alertas ainda ativos         : {len(alertas_db['alertas_ativos'])}")
    linhas.append(f"  Alertas resolvidos no mês    : {len(alertas_db['alertas_resolvidos'])}")

    linhas.append(_bloco_analise(analise))

    # Por shopping
    linhas.append(f"\n\n  🏬 DISTRIBUIÇÃO POR SHOPPING")
    linhas.append(_linha())
    por_sh = analise.get("por_resultado", {})
    shoppings_cont = Counter(
        r.get("shopping") for r in todos if r.get("shopping")
    )
    if shoppings_cont:
        for sh, qt in shoppings_cont.most_common():
            criticos_sh = len([r for r in todos
                               if r.get("shopping") == sh
                               and r.get("nivel") in ["CRITICO","ERRO"]])
            linhas.append(f"  {sh:25}: {qt:4} eventos | {criticos_sh} críticos")
    else:
        linhas.append("  Nenhum dado por shopping no período.")

    # Equipamentos com falha
    falhas_equip = [r for r in todos if "Falha em equipamento" in r.get("acao","")]
    linhas.append(f"\n\n  🔧 FALHAS DE EQUIPAMENTOS ({len(falhas_equip)})")
    linhas.append(_linha())
    if falhas_equip:
        linhas.append(_listar_registros_txt(falhas_equip, 15))
    else:
        linhas.append("  Nenhuma falha de equipamento registrada. ✅")

    # Conclusão
    total_criticos = analise.get("por_nivel",{}).get("CRITICO",0)
    if total_criticos == 0:
        status_geral = "✅ SISTEMA OPERANDO NORMALMENTE"
    elif total_criticos <= 3:
        status_geral = "⚠ ATENÇÃO — ALGUNS EVENTOS CRÍTICOS"
    else:
        status_geral = "🔴 ATENÇÃO — MÚLTIPLOS EVENTOS CRÍTICOS"

    linhas.append(f"\n\n  📌 CONCLUSÃO EXECUTIVA")
    linhas.append(_linha())
    linhas.append(f"  Status geral da rede: {status_geral}")
    linhas.append(f"  Recomendação: {'Manutenção preventiva recomendada.' if total_criticos > 0 else 'Continuar monitoramento padrão.'}")

    linhas.append(f"\n\n{_linha('═')}")
    linhas.append(f"  Fim do relatório executivo — {mes_nome}")
    linhas.append(_linha("═"))

    conteudo = "\n".join(linhas)
    if salvar:
        nome = f"relatorio_executivo_{agora.strftime('%Y_%m')}.txt"
        caminho = _salvar_relatorio(nome, conteudo)
        print(f"\n  💾 Relatório salvo em: {caminho}")
    return conteudo

# ── Relatório de Equipamentos ─────────────────

def relatorio_equipamentos(shopping: str = None, salvar: bool = True) -> str:
    todos = _filtrar(_carregar_registros(), categoria="Equipamentos", shopping=shopping)
    falhas = [r for r in todos if r.get("resultado") == "FALHA"]
    instalados = [r for r in todos if "instalado" in r.get("acao","").lower()
                  or "cadastrado" in r.get("acao","").lower()]

    linhas = [_cabecalho(
        "RELATÓRIO DE EQUIPAMENTOS",
        f"Shopping: {shopping or 'Todos'}"
    )]
    linhas.append(f"\n  Total de eventos de equipamentos : {len(todos)}")
    linhas.append(f"  Instalações/cadastros            : {len(instalados)}")
    linhas.append(f"  Falhas registradas               : {len(falhas)}")

    linhas.append(f"\n\n  ⚠ FALHAS DE EQUIPAMENTOS ({len(falhas)})")
    linhas.append(_linha())
    linhas.append(_listar_registros_txt(falhas))

    linhas.append(f"\n\n  ✅ INSTALAÇÕES REALIZADAS ({len(instalados)})")
    linhas.append(_linha())
    linhas.append(_listar_registros_txt(instalados))

    linhas.append(f"\n\n{_linha('═')}")
    linhas.append("  Fim do relatório de equipamentos")
    linhas.append(_linha("═"))

    conteudo = "\n".join(linhas)
    if salvar:
        slug = (shopping or "todos").replace(" ","_").lower()
        nome = f"relatorio_equipamentos_{slug}.txt"
        caminho = _salvar_relatorio(nome, conteudo)
        print(f"\n  💾 Relatório salvo em: {caminho}")
    return conteudo

# ─────────────────────────────────────────────
#   EXIBIÇÃO NO TERMINAL
# ─────────────────────────────────────────────

def _exibir_registro(r: dict):
    icones = {"INFO":"ℹ️", "AVISO":"⚠️", "ALERTA":"🚨", "CRITICO":"🔴", "ERRO":"💥"}
    ic = icones.get(r.get("nivel",""), "•")
    print(f"\n  {ic} [{r.get('id','-')}] {r.get('data','-')} {r.get('hora','-')}")
    print(f"     Ação     : {r.get('acao','-')}")
    print(f"     Categoria: {r.get('categoria','-')} | Nível: {r.get('nivel','-')} | Resultado: {r.get('resultado','-')}")
    print(f"     Usuário  : {r.get('usuario_sistema','-')} | Shopping: {r.get('shopping') or '-'}")
    if r.get("observacao"):
        print(f"     Obs      : {r['observacao']}")

def _exibir_lista(regs: list, titulo: str, limite: int = 30):
    print(f"\n  {'─'*55}")
    print(f"  {titulo} — {len(regs)} registro(s)")
    print(f"  {'─'*55}")
    if not regs:
        print("  Nenhum registro encontrado.")
    for r in regs[:limite]:
        _exibir_registro(r)
    if len(regs) > limite:
        print(f"\n  ... e mais {len(regs)-limite} registro(s). Gere um relatório para ver todos.")

# ─────────────────────────────────────────────
#   MENU INTERATIVO
# ─────────────────────────────────────────────

def menu():
    while True:
        print("\n" + "="*62)
        print("  🔎 SHOPCONTROL — CONSULTAS E RELATÓRIOS")
        print("="*62)
        print("  ── CONSULTAS RÁPIDAS ──────────────────────────────")
        print("   1. Registros de hoje")
        print("   2. Registros da semana")
        print("   3. Registros do mês")
        print("   4. Buscar por usuário")
        print("   5. Buscar por shopping")
        print("   6. Somente críticos / erros")
        print("   7. Somente falhas")
        print("   8. Somente acessos negados")
        print("   9. Buscar por período do dia (Manhã/Tarde/Noite)")
        print("  10. Buscar por faixa de horário")
        print("  11. Consulta avançada (filtros livres)")
        print("  ── RELATÓRIOS ─────────────────────────────────────")
        print("  12. Relatório diário")
        print("  13. Relatório de segurança (últimos N dias)")
        print("  14. Relatório por usuário")
        print("  15. Relatório por shopping")
        print("  16. Relatório executivo mensal")
        print("  17. Relatório de equipamentos")
        print("   0. Sair")
        print("="*62)
        op = input("  Escolha: ").strip()

        if op == "1":
            regs = consulta_hoje()
            _exibir_lista(regs, "HOJE")

        elif op == "2":
            regs = consulta_semana()
            _exibir_lista(regs, "ÚLTIMOS 7 DIAS")

        elif op == "3":
            regs = consulta_mes()
            _exibir_lista(regs, "ESTE MÊS")

        elif op == "4":
            u = input("  Nome do usuário: ").strip()
            regs = consulta_por_usuario(u)
            _exibir_lista(regs, f"USUÁRIO: {u}")

        elif op == "5":
            sh = input("  Shopping (ex: Shopping 1): ").strip()
            regs = consulta_por_shopping(sh)
            _exibir_lista(regs, f"SHOPPING: {sh}")

        elif op == "6":
            regs = consulta_criticos()
            _exibir_lista(regs, "CRÍTICOS E ERROS")

        elif op == "7":
            regs = consulta_falhas()
            _exibir_lista(regs, "FALHAS")

        elif op == "8":
            regs = consulta_acessos_negados()
            _exibir_lista(regs, "ACESSOS NEGADOS")

        elif op == "9":
            p = input("  Período (Manhã / Tarde / Noite / Madrugada): ").strip()
            regs = consulta_por_periodo_dia(p)
            _exibir_lista(regs, f"PERÍODO: {p}")

        elif op == "10":
            hi = input("  Hora início (ex: 08:00:00): ").strip()
            hf = input("  Hora fim    (ex: 12:00:00): ").strip()
            regs = consulta_por_hora(hi, hf)
            _exibir_lista(regs, f"HORÁRIO {hi} — {hf}")

        elif op == "11":
            print("\n  Preencha os filtros (deixe em branco para ignorar):")
            nivel    = input("  Nível (INFO/AVISO/ALERTA/CRITICO/ERRO): ").strip() or None
            cat      = input("  Categoria: ").strip() or None
            usuario  = input("  Usuário: ").strip() or None
            shopping = input("  Shopping: ").strip() or None
            resultado= input("  Resultado (SUCESSO/FALHA/NEGADO): ").strip() or None
            di       = input("  Data início (AAAA-MM-DD): ").strip() or None
            df       = input("  Data fim    (AAAA-MM-DD): ").strip() or None
            acao     = input("  Ação contém: ").strip() or None
            regs = consulta_livre(
                nivel=nivel, categoria=cat, usuario=usuario,
                shopping=shopping, resultado=resultado,
                data_inicio=di, data_fim=df, acao_contem=acao
            )
            _exibir_lista(regs, "CONSULTA AVANÇADA")

        elif op == "12":
            d = input("  Data (AAAA-MM-DD) ou ENTER para hoje: ").strip() or None
            conteudo = relatorio_diario(data=d)
            print("\n" + conteudo[:800] + "\n  [... relatório completo salvo no arquivo ...]")

        elif op == "13":
            dias = input("  Últimos quantos dias? (padrão 7): ").strip()
            dias = int(dias) if dias.isdigit() else 7
            sh = input("  Shopping específico (ENTER para todos): ").strip() or None
            conteudo = relatorio_seguranca(dias=dias, shopping=sh)
            print("\n" + conteudo[:800] + "\n  [... relatório completo salvo no arquivo ...]")

        elif op == "14":
            u = input("  Nome do usuário: ").strip()
            conteudo = relatorio_usuario(u)
            print("\n" + conteudo[:800] + "\n  [... relatório completo salvo no arquivo ...]")

        elif op == "15":
            sh = input("  Shopping (ex: Shopping 1): ").strip()
            dias = input("  Últimos quantos dias? (padrão 30): ").strip()
            dias = int(dias) if dias.isdigit() else 30
            conteudo = relatorio_shopping(sh, dias=dias)
            print("\n" + conteudo[:800] + "\n  [... relatório completo salvo no arquivo ...]")

        elif op == "16":
            conteudo = relatorio_executivo_mensal()
            print("\n" + conteudo[:800] + "\n  [... relatório completo salvo no arquivo ...]")

        elif op == "17":
            sh = input("  Shopping (ENTER para todos): ").strip() or None
            conteudo = relatorio_equipamentos(shopping=sh)
            print("\n" + conteudo[:800] + "\n  [... relatório completo salvo no arquivo ...]")

        elif op == "0":
            print("\n  Saindo do módulo de consultas...\n")
            break
        else:
            print("\n  ❌ Opção inválida.")

if __name__ == "__main__":
    menu()