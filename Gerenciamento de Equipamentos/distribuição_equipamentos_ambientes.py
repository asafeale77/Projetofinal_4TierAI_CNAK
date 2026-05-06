"""
╔══════════════════════════════════════════════════════════════════╗
║        MÓDULO DE DISTRIBUIÇÃO DE EQUIPAMENTOS NOS AMBIENTES      ║
║                 ShopControl - Rede de Shoppings                  ║
╚══════════════════════════════════════════════════════════════════╝

Este módulo conecta equipamentos.py com ambientes.py,
registrando qual equipamento está instalado em qual ambiente.
"""

import json
import os
import random
from datetime import datetime


# ─────────────────────────────────────────────
#  CAMINHOS DOS ARQUIVOS
# ─────────────────────────────────────────────

PASTA_DADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'dados')
ARQUIVO_DISTRIBUICAO  = os.path.join(PASTA_DADOS, 'distribuicao.json')
ARQUIVO_EQUIPAMENTOS  = os.path.join(PASTA_DADOS, 'equipamentos.json')
ARQUIVO_AMBIENTES     = os.path.join(PASTA_DADOS, 'ambientes.json')


# ─────────────────────────────────────────────
#  TIPOS DE POSIÇÃO DE INSTALAÇÃO
# ─────────────────────────────────────────────

POSICOES_INSTALACAO = [
    "teto_centro",
    "teto_canto",
    "parede_alta",
    "parede_media",
    "parede_externa",
    "poste_externo",
    "coluna_estrutural",
    "entrada_porta",
    "balcão",
    "piso_embutido",
    "rack_sala_tecnica",
    "fachada_externa",
    "cancela",
    "guarita",
    "totem_standalone"
]

SHOPPINGS = ["Shopping 1", "Shopping 2", "Shopping 3", "Shopping 4"]


# ─────────────────────────────────────────────
#  FUNÇÕES DE BANCO DE DADOS
# ─────────────────────────────────────────────

def _inicializar_banco():
    os.makedirs(PASTA_DADOS, exist_ok=True)
    if not os.path.exists(ARQUIVO_DISTRIBUICAO):
        estrutura = {
            "metadados": {
                "criado_em": datetime.now().isoformat(),
                "ultima_atualizacao": datetime.now().isoformat(),
                "total_distribuicoes": 0,
                "versao": "1.0"
            },
            "distribuicoes": []
        }
        _salvar_dados(estrutura)
        print("✅ Banco 'distribuicao.json' criado com sucesso!")


def _carregar_dados():
    _inicializar_banco()
    with open(ARQUIVO_DISTRIBUICAO, 'r', encoding='utf-8') as f:
        return json.load(f)


def _salvar_dados(dados):
    os.makedirs(PASTA_DADOS, exist_ok=True)
    dados['metadados']['ultima_atualizacao'] = datetime.now().isoformat()
    dados['metadados']['total_distribuicoes'] = len(dados['distribuicoes'])
    with open(ARQUIVO_DISTRIBUICAO, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def _carregar_equipamentos() -> list:
    if not os.path.exists(ARQUIVO_EQUIPAMENTOS):
        print("⚠️  equipamentos.json não encontrado. Rode equipamentos.py primeiro.")
        return []
    with open(ARQUIVO_EQUIPAMENTOS, 'r', encoding='utf-8') as f:
        return json.load(f).get('equipamentos', [])


def _carregar_ambientes() -> list:
    if not os.path.exists(ARQUIVO_AMBIENTES):
        print("⚠️  ambientes.json não encontrado. Rode ambientes.py primeiro.")
        return []
    with open(ARQUIVO_AMBIENTES, 'r', encoding='utf-8') as f:
        return json.load(f).get('ambientes', [])


def _atualizar_equipamento_ambiente(equip_id: str, ambiente_id: str, ambiente_nome: str):
    """Atualiza o campo ambiente_id e ambiente_nome no equipamentos.json."""
    if not os.path.exists(ARQUIVO_EQUIPAMENTOS):
        return
    with open(ARQUIVO_EQUIPAMENTOS, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    for i, e in enumerate(dados['equipamentos']):
        if e['id'] == equip_id:
            dados['equipamentos'][i]['ambiente_id'] = ambiente_id
            dados['equipamentos'][i]['ambiente_nome'] = ambiente_nome
            dados['equipamentos'][i]['status'] = 'operacional'
            dados['equipamentos'][i]['atualizado_em'] = datetime.now().isoformat()
            break
    with open(ARQUIVO_EQUIPAMENTOS, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def _gerar_id() -> str:
    import string
    return 'DIST-' + ''.join(__import__('random').choices(string.digits, k=6))


# ─────────────────────────────────────────────
#  CRIAR — DISTRIBUIR EQUIPAMENTO
# ─────────────────────────────────────────────

def distribuir_equipamento(
    equip_id: str,
    ambiente_id: str,
    posicao: str = "teto_centro",
    altura_instalacao_m: float = 3.0,
    angulo_visao: str = "",
    tecnico_instalador: str = "",
    observacoes: str = ""
) -> dict:
    """
    Associa um equipamento a um ambiente físico.

    Parâmetros:
        equip_id            → ID do equipamento (de equipamentos.json)
        ambiente_id         → ID do ambiente (de ambientes.json)
        posicao             → Onde foi instalado (ver POSICOES_INSTALACAO)
        altura_instalacao_m → Altura em metros da instalação
        angulo_visao        → Ângulo/direção da câmera (ex: "Norte", "Entrada")
        tecnico_instalador  → Nome do técnico que instalou
        observacoes         → Observações adicionais
    """
    dados = _carregar_dados()

    # Verifica se equipamento existe
    equipamentos = _carregar_equipamentos()
    equip = next((e for e in equipamentos if e['id'] == equip_id), None)
    if not equip:
        print(f"⚠️  Equipamento '{equip_id}' não encontrado em equipamentos.json.")
        return None

    # Verifica se ambiente existe
    ambientes = _carregar_ambientes()
    ambiente = next((a for a in ambientes if a['id'] == ambiente_id), None)
    if not ambiente:
        print(f"⚠️  Ambiente '{ambiente_id}' não encontrado em ambientes.json.")
        return None

    # Verifica se equipamento já está distribuído
    for d in dados['distribuicoes']:
        if d['equip_id'] == equip_id and d['ativo']:
            print(f"⚠️  Equipamento '{equip_id}' já está distribuído em '{d['ambiente_nome']}'.")
            print(f"    Use transferir_equipamento() para movê-lo.")
            return None

    # Valida posição
    if posicao not in POSICOES_INSTALACAO:
        print(f"⚠️  Posição inválida. Opções: {', '.join(POSICOES_INSTALACAO)}")
        return None

    nova_dist = {
        "id": _gerar_id(),
        "equip_id": equip_id,
        "equip_tipo": equip['tipo'],
        "equip_descricao": equip['descricao_tipo'],
        "equip_marca": equip['marca'],
        "equip_modelo": equip['modelo'],
        "ambiente_id": ambiente_id,
        "ambiente_nome": ambiente.get('nome', ambiente_id),
        "shopping": equip['shopping'],
        "piso": ambiente.get('piso', ''),
        "ala": ambiente.get('ala', ''),
        "posicao_instalacao": posicao,
        "altura_instalacao_m": altura_instalacao_m,
        "angulo_visao": angulo_visao,
        "tecnico_instalador": tecnico_instalador,
        "observacoes": observacoes,
        "ativo": True,
        "data_instalacao": datetime.now().isoformat(),
        "data_remocao": None,
        "historico_transferencias": []
    }

    dados['distribuicoes'].append(nova_dist)
    _salvar_dados(dados)

    # Atualiza o equipamentos.json com o ambiente
    _atualizar_equipamento_ambiente(
        equip_id,
        ambiente_id,
        ambiente.get('nome', ambiente_id)
    )

    print(f"✅ '{equip['descricao_tipo']}' instalado em '{ambiente.get('nome', ambiente_id)}'!")
    return nova_dist


# ─────────────────────────────────────────────
#  LISTAR / BUSCAR
# ─────────────────────────────────────────────

def listar_distribuicoes(
    shopping: str = None,
    ambiente_id: str = None,
    tipo_equip: str = None,
    apenas_ativos: bool = True
) -> list:
    """
    Lista distribuições com filtros opcionais.

    Parâmetros:
        shopping     → Filtra por shopping
        ambiente_id  → Filtra por ambiente específico
        tipo_equip   → Filtra por tipo de equipamento
        apenas_ativos→ Se True, mostra só instalações ativas
    """
    dados = _carregar_dados()
    dists = dados['distribuicoes']

    if apenas_ativos:
        dists = [d for d in dists if d['ativo']]
    if shopping:
        dists = [d for d in dists if d['shopping'] == shopping]
    if ambiente_id:
        dists = [d for d in dists if d['ambiente_id'] == ambiente_id]
    if tipo_equip:
        dists = [d for d in dists if d['equip_tipo'] == tipo_equip]

    return dists


def buscar_por_equipamento(equip_id: str) -> dict:
    """Retorna a distribuição ativa de um equipamento específico."""
    dados = _carregar_dados()
    for d in dados['distribuicoes']:
        if d['equip_id'] == equip_id and d['ativo']:
            return d
    print(f"⚠️  Equipamento '{equip_id}' não está distribuído em nenhum ambiente.")
    return None


def listar_equipamentos_por_ambiente(ambiente_id: str) -> list:
    """Retorna todos os equipamentos instalados em um ambiente."""
    return listar_distribuicoes(ambiente_id=ambiente_id)


def listar_ambientes_sem_cobertura(shopping: str = None) -> list:
    """
    Retorna ambientes que não têm nenhum equipamento instalado.
    Útil para identificar pontos cegos no sistema de segurança.
    """
    ambientes = _carregar_ambientes()
    distribuicoes = listar_distribuicoes(shopping=shopping)
    ambientes_cobertos = set(d['ambiente_id'] for d in distribuicoes)

    sem_cobertura = []
    for a in ambientes:
        if shopping and a.get('shopping') != shopping:
            continue
        if a['id'] not in ambientes_cobertos:
            sem_cobertura.append(a)

    return sem_cobertura


def listar_equipamentos_nao_distribuidos(shopping: str = None) -> list:
    """Retorna equipamentos que ainda não foram instalados em nenhum ambiente."""
    equipamentos = _carregar_equipamentos()
    distribuicoes = listar_distribuicoes()
    equips_distribuidos = set(d['equip_id'] for d in distribuicoes)

    nao_distribuidos = []
    for e in equipamentos:
        if shopping and e.get('shopping') != shopping:
            continue
        if e['id'] not in equips_distribuidos:
            nao_distribuidos.append(e)

    return nao_distribuidos


# ─────────────────────────────────────────────
#  TRANSFERIR EQUIPAMENTO
# ─────────────────────────────────────────────

def transferir_equipamento(
    equip_id: str,
    novo_ambiente_id: str,
    motivo: str = "",
    tecnico: str = ""
) -> dict:
    """
    Move um equipamento de um ambiente para outro.
    Mantém o histórico da transferência.
    """
    dados = _carregar_dados()
    ambientes = _carregar_ambientes()

    novo_ambiente = next((a for a in ambientes if a['id'] == novo_ambiente_id), None)
    if not novo_ambiente:
        print(f"⚠️  Ambiente destino '{novo_ambiente_id}' não encontrado.")
        return None

    for i, d in enumerate(dados['distribuicoes']):
        if d['equip_id'] == equip_id and d['ativo']:
            ambiente_anterior = d['ambiente_nome']

            # Registra histórico
            dados['distribuicoes'][i]['historico_transferencias'].append({
                "data": datetime.now().isoformat(),
                "de_ambiente": d['ambiente_id'],
                "de_ambiente_nome": d['ambiente_nome'],
                "para_ambiente": novo_ambiente_id,
                "para_ambiente_nome": novo_ambiente.get('nome', novo_ambiente_id),
                "motivo": motivo,
                "tecnico": tecnico
            })

            # Atualiza para novo ambiente
            dados['distribuicoes'][i]['ambiente_id'] = novo_ambiente_id
            dados['distribuicoes'][i]['ambiente_nome'] = novo_ambiente.get('nome', novo_ambiente_id)
            dados['distribuicoes'][i]['piso'] = novo_ambiente.get('piso', '')
            dados['distribuicoes'][i]['ala'] = novo_ambiente.get('ala', '')

            _salvar_dados(dados)

            # Atualiza equipamentos.json
            _atualizar_equipamento_ambiente(
                equip_id,
                novo_ambiente_id,
                novo_ambiente.get('nome', novo_ambiente_id)
            )

            print(f"✅ Equipamento '{equip_id}' transferido:")
            print(f"   {ambiente_anterior} → {novo_ambiente.get('nome', novo_ambiente_id)}")
            return dados['distribuicoes'][i]

    print(f"⚠️  Equipamento '{equip_id}' não está distribuído. Use distribuir_equipamento() primeiro.")
    return None


# ─────────────────────────────────────────────
#  REMOVER DISTRIBUIÇÃO
# ─────────────────────────────────────────────

def remover_distribuicao(equip_id: str, motivo: str = "") -> bool:
    """
    Remove um equipamento do ambiente onde está instalado.
    Mantém o registro histórico (não deleta, só desativa).
    """
    dados = _carregar_dados()

    for i, d in enumerate(dados['distribuicoes']):
        if d['equip_id'] == equip_id and d['ativo']:
            dados['distribuicoes'][i]['ativo'] = False
            dados['distribuicoes'][i]['data_remocao'] = datetime.now().isoformat()
            dados['distribuicoes'][i]['motivo_remocao'] = motivo or "Não informado"
            _salvar_dados(dados)

            # Limpa o ambiente no equipamentos.json
            _atualizar_equipamento_ambiente(equip_id, None, "Não distribuído")

            print(f"✅ Equipamento '{equip_id}' removido do ambiente '{d['ambiente_nome']}'.")
            return True

    print(f"⚠️  Equipamento '{equip_id}' não está distribuído.")
    return False


# ─────────────────────────────────────────────
#  RELATÓRIOS E ESTATÍSTICAS
# ─────────────────────────────────────────────

def obter_estatisticas(shopping: str = None) -> dict:
    """Retorna estatísticas completas da distribuição — útil para o dashboard."""
    dists = listar_distribuicoes(shopping=shopping)
    ambientes = _carregar_ambientes()
    equipamentos = _carregar_equipamentos()

    if shopping:
        ambientes = [a for a in ambientes if a.get('shopping') == shopping]
        equipamentos = [e for e in equipamentos if e.get('shopping') == shopping]

    sem_cobertura = listar_ambientes_sem_cobertura(shopping=shopping)
    nao_distribuidos = listar_equipamentos_nao_distribuidos(shopping=shopping)

    por_tipo = {}
    for d in dists:
        tipo = d['equip_tipo']
        por_tipo[tipo] = por_tipo.get(tipo, 0) + 1

    por_shopping = {}
    for sh in SHOPPINGS:
        por_shopping[sh] = len([d for d in dists if d['shopping'] == sh])

    cameras_instaladas = len([d for d in dists if 'camera' in d['equip_tipo']])
    sensores_instalados = len([d for d in dists if 'sensor' in d['equip_tipo']])
    total_ambientes = len(ambientes)
    ambientes_cobertos = total_ambientes - len(sem_cobertura)

    return {
        "total_distribuicoes": len(dists),
        "total_ambientes": total_ambientes,
        "ambientes_cobertos": ambientes_cobertos,
        "ambientes_sem_cobertura": len(sem_cobertura),
        "cobertura_percentual": round((ambientes_cobertos / total_ambientes * 100), 1) if total_ambientes > 0 else 0,
        "equipamentos_nao_distribuidos": len(nao_distribuidos),
        "cameras_instaladas": cameras_instaladas,
        "sensores_instalados": sensores_instalados,
        "por_tipo": por_tipo,
        "por_shopping": por_shopping
    }


def relatorio_cobertura_por_shopping() -> dict:
    """
    Gera relatório de cobertura por shopping.
    Mostra % de ambientes cobertos em cada shopping.
    """
    relatorio = {}
    for sh in SHOPPINGS:
        ambientes = [a for a in _carregar_ambientes() if a.get('shopping') == sh]
        dists = listar_distribuicoes(shopping=sh)
        cobertos = set(d['ambiente_id'] for d in dists)
        total = len(ambientes)
        cobertura = len([a for a in ambientes if a['id'] in cobertos])
        relatorio[sh] = {
            "total_ambientes": total,
            "ambientes_cobertos": cobertura,
            "ambientes_sem_cobertura": total - cobertura,
            "percentual": round((cobertura / total * 100), 1) if total > 0 else 0,
            "total_equipamentos": len(dists),
            "cameras": len([d for d in dists if 'camera' in d['equip_tipo']]),
            "sensores": len([d for d in dists if 'sensor' in d['equip_tipo']])
        }
    return relatorio


def mapa_ambiente(ambiente_id: str) -> dict:
    """
    Retorna o mapa completo de um ambiente:
    quais equipamentos estão lá, posição, ângulo, etc.
    Útil para o dashboard mostrar o layout do ambiente.
    """
    ambientes = _carregar_ambientes()
    ambiente = next((a for a in ambientes if a['id'] == ambiente_id), None)
    if not ambiente:
        print(f"⚠️  Ambiente '{ambiente_id}' não encontrado.")
        return None

    equipamentos_no_ambiente = listar_equipamentos_por_ambiente(ambiente_id)

    return {
        "ambiente": ambiente,
        "total_equipamentos": len(equipamentos_no_ambiente),
        "equipamentos": [
            {
                "id": d['equip_id'],
                "tipo": d['equip_tipo'],
                "descricao": d['equip_descricao'],
                "marca": d['equip_marca'],
                "modelo": d['equip_modelo'],
                "posicao": d['posicao_instalacao'],
                "altura_m": d['altura_instalacao_m'],
                "angulo": d['angulo_visao'],
                "instalado_em": d['data_instalacao'][:10]
            }
            for d in equipamentos_no_ambiente
        ],
        "cameras": [d for d in equipamentos_no_ambiente if 'camera' in d['equip_tipo']],
        "sensores": [d for d in equipamentos_no_ambiente if 'sensor' in d['equip_tipo']],
        "controle_acesso": [d for d in equipamentos_no_ambiente if any(
            x in d['equip_tipo'] for x in ['catraca', 'leitor', 'fechadura', 'porta', 'eclusa']
        )]
    }


# ─────────────────────────────────────────────
#  POPULAR COM DADOS INICIAIS
# ─────────────────────────────────────────────

def popular_distribuicao_inicial():
    """
    Distribui automaticamente os equipamentos nos ambientes.
    Requer que equipamentos.json e ambientes.json já existam.
    """
    equipamentos = _carregar_equipamentos()
    ambientes    = _carregar_ambientes()

    if not equipamentos:
        print("⚠️  Nenhum equipamento encontrado. Rode equipamentos.py → opção 13 primeiro.")
        return
    if not ambientes:
        print("⚠️  Nenhum ambiente encontrado. Rode ambientes.py → opção 8 primeiro.")
        return

    print(f"\n📦 Iniciando distribuição automática...")
    print(f"   Equipamentos disponíveis : {len(equipamentos)}")
    print(f"   Ambientes disponíveis    : {len(ambientes)}\n")

    # Agrupa ambientes por shopping
    ambientes_por_shopping = {}
    for sh in SHOPPINGS:
        ambientes_por_shopping[sh] = [a for a in ambientes if a.get('shopping') == sh]

    sucesso = 0
    pulados = 0

    for equip in equipamentos:
        sh = equip.get('shopping')
        ambientes_sh = ambientes_por_shopping.get(sh, [])
        if not ambientes_sh:
            pulados += 1
            continue

        # Escolhe ambiente compatível com o tipo de equipamento
        tipo = equip['tipo']
        ambiente_escolhido = None

        if 'estac' in tipo or 'placa' in tipo or 'cancela' in tipo or 'vaga' in tipo:
            candidatos = [a for a in ambientes_sh if 'stacionamento' in a.get('nome', '').lower()
                         or 'cancela' in a.get('nome', '').lower()
                         or 'garagem' in a.get('nome', '').lower()]
        elif 'entrada' in tipo or 'catraca' in tipo or 'porta' in tipo:
            candidatos = [a for a in ambientes_sh if 'ntrada' in a.get('nome', '').lower()
                         or 'portaria' in a.get('nome', '').lower()
                         or 'acesso' in a.get('nome', '').lower()]
        elif 'servidor' in tipo or 'nvr' in tipo or 'rack' in tipo or 'switch' in tipo:
            candidatos = [a for a in ambientes_sh if 'monitoramento' in a.get('nome', '').lower()
                         or 'administra' in a.get('nome', '').lower()
                         or 'técnica' in a.get('nome', '').lower()
                         or 'servidor' in a.get('nome', '').lower()]
        elif 'alarme' in tipo or 'incendio' in tipo or 'central' in tipo:
            candidatos = [a for a in ambientes_sh if 'administra' in a.get('nome', '').lower()
                         or 'segurança' in a.get('nome', '').lower()
                         or 'central' in a.get('nome', '').lower()]
        else:
            candidatos = ambientes_sh

        if candidatos:
            ambiente_escolhido = random.choice(candidatos)
        else:
            ambiente_escolhido = random.choice(ambientes_sh)

        # Define posição baseada no tipo
        if 'camera' in tipo:
            posicao = random.choice(["teto_centro", "teto_canto", "parede_alta", "coluna_estrutural"])
            altura = round(random.uniform(2.5, 5.0), 1)
            angulo = random.choice(["Norte", "Sul", "Leste", "Oeste", "Entrada", "Saída", "Central"])
        elif 'sensor' in tipo:
            posicao = random.choice(["teto_centro", "parede_media", "parede_alta"])
            altura = round(random.uniform(2.0, 3.5), 1)
            angulo = ""
        elif 'catraca' in tipo or 'porta' in tipo or 'leitor' in tipo:
            posicao = random.choice(["entrada_porta", "parede_media", "balcão"])
            altura = round(random.uniform(0.9, 1.5), 1)
            angulo = ""
        elif 'cancela' in tipo or 'leitor_placa' in tipo:
            posicao = "cancela"
            altura = 1.2
            angulo = random.choice(["Entrada", "Saída"])
        elif 'totem' in tipo or 'display' in tipo:
            posicao = random.choice(["totem_standalone", "parede_media", "balcão"])
            altura = 1.8
            angulo = ""
        else:
            posicao = random.choice(POSICOES_INSTALACAO)
            altura = 2.0
            angulo = ""

        resultado = distribuir_equipamento(
            equip_id=equip['id'],
            ambiente_id=ambiente_escolhido['id'],
            posicao=posicao,
            altura_instalacao_m=altura,
            angulo_visao=angulo,
            tecnico_instalador="Equipe de Instalação ShopControl"
        )

        if resultado:
            sucesso += 1
        else:
            pulados += 1

    print(f"\n✅ Distribuição concluída!")
    print(f"   Instalados com sucesso : {sucesso}")
    print(f"   Pulados/já distribuídos: {pulados}")

    stats = obter_estatisticas()
    print(f"\n📊 Cobertura geral: {stats['cobertura_percentual']}% dos ambientes cobertos")


# ─────────────────────────────────────────────
#  MENU INTERATIVO
# ─────────────────────────────────────────────

def _exibir_distribuicao(d: dict):
    print(f"""
  📍 {d['equip_descricao']} (ID: {d['equip_id']})
  ├─ Marca/Modelo  : {d['equip_marca']} {d['equip_modelo']}
  ├─ Ambiente      : {d['ambiente_nome']}
  ├─ Shopping      : {d['shopping']}
  ├─ Piso/Ala      : {d.get('piso','?')} / {d.get('ala','?')}
  ├─ Posição       : {d['posicao_instalacao']}
  ├─ Altura        : {d['altura_instalacao_m']}m
  ├─ Ângulo/Dir.   : {d['angulo_visao'] or 'N/A'}
  ├─ Técnico       : {d['tecnico_instalador'] or 'N/A'}
  ├─ Instalado em  : {d['data_instalacao'][:10]}
  └─ Transferências: {len(d['historico_transferencias'])}
""")


def menu():
    _inicializar_banco()
    while True:
        print("""
╔══════════════════════════════════════════════════════╗
║    DISTRIBUIÇÃO DE EQUIPAMENTOS - ShopControl        ║
╠══════════════════════════════════════════════════════╣
║  1.  Listar todas as distribuições                   ║
║  2.  Listar por shopping                             ║
║  3.  Listar por ambiente                             ║
║  4.  Listar por tipo de equipamento                  ║
║  5.  Buscar por equipamento (ID)                     ║
║  6.  Ver mapa completo de um ambiente                ║
║  7.  Instalar equipamento em ambiente                ║
║  8.  Transferir equipamento de ambiente              ║
║  9.  Remover equipamento do ambiente                 ║
║  10. Ambientes SEM cobertura (pontos cegos)          ║
║  11. Equipamentos NÃO distribuídos                   ║
║  12. Relatório de cobertura por shopping             ║
║  13. Estatísticas gerais                             ║
║  14. Distribuição automática (popular inicial)       ║
║  0.  Sair                                            ║
╚══════════════════════════════════════════════════════╝
        """)
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            dists = listar_distribuicoes()
            print(f"\n📋 {len(dists)} equipamento(s) distribuído(s):")
            for d in dists:
                _exibir_distribuicao(d)

        elif opcao == "2":
            print(f"Shoppings: {', '.join(SHOPPINGS)}")
            sh = input("Shopping: ").strip()
            dists = listar_distribuicoes(shopping=sh)
            print(f"\n📋 {len(dists)} equipamento(s) em {sh}:")
            for d in dists:
                _exibir_distribuicao(d)

        elif opcao == "3":
            amb_id = input("ID do ambiente: ").strip()
            dists = listar_equipamentos_por_ambiente(amb_id)
            print(f"\n📋 {len(dists)} equipamento(s) no ambiente '{amb_id}':")
            for d in dists:
                _exibir_distribuicao(d)

        elif opcao == "4":
            tipo = input("Tipo de equipamento: ").strip()
            dists = listar_distribuicoes(tipo_equip=tipo)
            for d in dists:
                _exibir_distribuicao(d)

        elif opcao == "5":
            eid = input("ID do equipamento: ").strip().upper()
            d = buscar_por_equipamento(eid)
            if d:
                _exibir_distribuicao(d)

        elif opcao == "6":
            amb_id = input("ID do ambiente: ").strip()
            mapa = mapa_ambiente(amb_id)
            if mapa:
                print(f"\n🗺️  Mapa do ambiente: {mapa['ambiente'].get('nome', amb_id)}")
                print(f"   Total de equipamentos : {mapa['total_equipamentos']}")
                print(f"   Câmeras               : {len(mapa['cameras'])}")
                print(f"   Sensores              : {len(mapa['sensores'])}")
                print(f"   Controle de acesso    : {len(mapa['controle_acesso'])}")
                print("\n   Equipamentos instalados:")
                for e in mapa['equipamentos']:
                    print(f"   • {e['descricao']} — {e['posicao']} @ {e['altura_m']}m")

        elif opcao == "7":
            print("\n── Instalar equipamento em ambiente ──")
            eid = input("ID do equipamento: ").strip().upper()
            amb = input("ID do ambiente: ").strip()
            print(f"Posições: {', '.join(POSICOES_INSTALACAO)}")
            pos = input("Posição: ").strip() or "teto_centro"
            alt = input("Altura em metros (ex: 3.0): ").strip()
            alt = float(alt) if alt else 3.0
            ang = input("Ângulo/Direção (opcional): ").strip()
            tec = input("Técnico instalador (opcional): ").strip()
            obs = input("Observações (opcional): ").strip()
            distribuir_equipamento(eid, amb, pos, alt, ang, tec, obs)

        elif opcao == "8":
            eid = input("ID do equipamento a transferir: ").strip().upper()
            novo_amb = input("ID do novo ambiente: ").strip()
            motivo = input("Motivo da transferência: ").strip()
            tec = input("Técnico responsável: ").strip()
            transferir_equipamento(eid, novo_amb, motivo, tec)

        elif opcao == "9":
            eid = input("ID do equipamento a remover: ").strip().upper()
            motivo = input("Motivo da remoção: ").strip()
            confirm = input("⚠️  Digite 'SIM' para confirmar: ").strip()
            if confirm == "SIM":
                remover_distribuicao(eid, motivo)

        elif opcao == "10":
            print(f"\nShoppings: {', '.join(SHOPPINGS)} (ou Enter para todos)")
            sh = input("Filtrar por shopping (opcional): ").strip() or None
            sem_cob = listar_ambientes_sem_cobertura(shopping=sh)
            print(f"\n⚠️  {len(sem_cob)} ambiente(s) SEM cobertura:")
            for a in sem_cob[:20]:
                print(f"   • {a.get('nome', a['id'])} — {a.get('shopping','')} {a.get('piso','')}")
            if len(sem_cob) > 20:
                print(f"   ... e mais {len(sem_cob)-20} ambientes.")

        elif opcao == "11":
            print(f"\nShoppings: {', '.join(SHOPPINGS)} (ou Enter para todos)")
            sh = input("Filtrar por shopping (opcional): ").strip() or None
            nao_dist = listar_equipamentos_nao_distribuidos(shopping=sh)
            print(f"\n📦 {len(nao_dist)} equipamento(s) NÃO distribuído(s):")
            for e in nao_dist[:20]:
                print(f"   • [{e['id']}] {e['descricao_tipo']} — {e['marca']} {e['modelo']} ({e['shopping']})")
            if len(nao_dist) > 20:
                print(f"   ... e mais {len(nao_dist)-20} equipamentos.")

        elif opcao == "12":
            rel = relatorio_cobertura_por_shopping()
            print("\n📊 Relatório de Cobertura por Shopping:\n")
            for sh, dados in rel.items():
                barra = "█" * int(dados['percentual'] / 5) + "░" * (20 - int(dados['percentual'] / 5))
                print(f"  {sh}")
                print(f"  [{barra}] {dados['percentual']}%")
                print(f"  Ambientes: {dados['ambientes_cobertos']}/{dados['total_ambientes']} cobertos")
                print(f"  Equipamentos: {dados['total_equipamentos']} | Câmeras: {dados['cameras']} | Sensores: {dados['sensores']}\n")

        elif opcao == "13":
            stats = obter_estatisticas()
            print(f"""
📊 Estatísticas Gerais:
  Total distribuições       : {stats['total_distribuicoes']}
  Total ambientes           : {stats['total_ambientes']}
  Ambientes cobertos        : {stats['ambientes_cobertos']}
  Ambientes sem cobertura   : {stats['ambientes_sem_cobertura']}
  Cobertura geral           : {stats['cobertura_percentual']}%
  Equip. não distribuídos   : {stats['equipamentos_nao_distribuidos']}
  Câmeras instaladas        : {stats['cameras_instaladas']}
  Sensores instalados       : {stats['sensores_instalados']}
  Por shopping: {json.dumps(stats['por_shopping'], indent=4, ensure_ascii=False)}
""")

        elif opcao == "14":
            popular_distribuicao_inicial()

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