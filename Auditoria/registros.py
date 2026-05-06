"""
=============================================================
  SHOPCONTROL - MÓDULO DE AUDITORIA
  Arquivo: registros.py
  Descrição: Sistema completo de registro e auditoria de
             todas as ações realizadas no sistema ShopControl
=============================================================
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from enum import Enum

# ─────────────────────────────────────────────
#   CONFIGURAÇÕES
# ─────────────────────────────────────────────

PASTA_DADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dados")
ARQUIVO_REGISTROS = os.path.join(PASTA_DADOS, "auditoria_registros.json")
ARQUIVO_ALERTAS   = os.path.join(PASTA_DADOS, "auditoria_alertas.json")

os.makedirs(PASTA_DADOS, exist_ok=True)

# ─────────────────────────────────────────────
#   ENUMERAÇÕES
# ─────────────────────────────────────────────

class NivelRegistro(Enum):
    INFO     = "INFO"
    AVISO    = "AVISO"
    ALERTA   = "ALERTA"
    CRITICO  = "CRITICO"
    ERRO     = "ERRO"

class CategoriaAcao(Enum):
    AUTENTICACAO    = "Autenticação"
    USUARIOS        = "Usuários"
    AMBIENTES       = "Ambientes"
    EQUIPAMENTOS    = "Equipamentos"
    MONITORAMENTO   = "Monitoramento"
    ESTACIONAMENTO  = "Estacionamento"
    MODULOS         = "Módulos do Sistema"
    RELATORIOS      = "Relatórios"
    SISTEMA         = "Sistema"
    SEGURANCA       = "Segurança"
    ACESSO          = "Controle de Acesso"

class ResultadoAcao(Enum):
    SUCESSO  = "SUCESSO"
    FALHA    = "FALHA"
    NEGADO   = "NEGADO"
    PENDENTE = "PENDENTE"

# ─────────────────────────────────────────────
#   ESTRUTURA DO BANCO DE DADOS
# ─────────────────────────────────────────────

def _carregar_registros() -> dict:
    if not os.path.exists(ARQUIVO_REGISTROS):
        estrutura = {
            "metadados": {
                "criado_em": datetime.now().isoformat(),
                "versao": "1.0",
                "total_registros": 0,
                "ultima_atualizacao": datetime.now().isoformat()
            },
            "registros": [],
            "estatisticas": {
                "total_por_nivel": {
                    "INFO": 0, "AVISO": 0, "ALERTA": 0, "CRITICO": 0, "ERRO": 0
                },
                "total_por_categoria": {},
                "total_por_shopping": {},
                "total_falhas": 0,
                "total_sucessos": 0,
                "total_acessos_negados": 0
            }
        }
        _salvar_registros(estrutura)
        return estrutura
    with open(ARQUIVO_REGISTROS, "r", encoding="utf-8") as f:
        return json.load(f)

def _salvar_registros(dados: dict):
    dados["metadados"]["ultima_atualizacao"] = datetime.now().isoformat()
    dados["metadados"]["total_registros"] = len(dados["registros"])
    with open(ARQUIVO_REGISTROS, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def _carregar_alertas() -> dict:
    if not os.path.exists(ARQUIVO_ALERTAS):
        estrutura = {
            "metadados": {
                "criado_em": datetime.now().isoformat(),
                "total_alertas": 0
            },
            "alertas_ativos": [],
            "alertas_resolvidos": []
        }
        _salvar_alertas(estrutura)
        return estrutura
    with open(ARQUIVO_ALERTAS, "r", encoding="utf-8") as f:
        return json.load(f)

def _salvar_alertas(dados: dict):
    dados["metadados"]["total_alertas"] = len(dados["alertas_ativos"])
    with open(ARQUIVO_ALERTAS, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

# ─────────────────────────────────────────────
#   FUNÇÃO PRINCIPAL DE REGISTRO
# ─────────────────────────────────────────────

def registrar(
    acao: str,
    categoria: str,
    nivel: str = "INFO",
    resultado: str = "SUCESSO",
    usuario_sistema: str = "sistema",
    shopping: str = None,
    modulo_origem: str = None,
    detalhes: dict = None,
    dado_anterior: dict = None,
    dado_novo: dict = None,
    ip_origem: str = None,
    observacao: str = None
) -> str:
    """
    Registra qualquer ação no sistema de auditoria.
    Retorna o ID do registro criado.
    """
    dados = _carregar_registros()

    agora = datetime.now()
    hora = agora.hour
    if 6 <= hora < 12:
        periodo = "Manhã"
    elif 12 <= hora < 18:
        periodo = "Tarde"
    elif 18 <= hora < 24:
        periodo = "Noite"
    else:
        periodo = "Madrugada"

    registro_id = str(uuid.uuid4())[:8].upper()

    registro = {
        "id": registro_id,
        "timestamp": agora.isoformat(),
        "data": agora.strftime("%d/%m/%Y"),
        "hora": agora.strftime("%H:%M:%S"),
        "periodo_dia": periodo,
        "dia_semana": agora.strftime("%A"),
        "acao": acao,
        "categoria": categoria,
        "nivel": nivel,
        "resultado": resultado,
        "usuario_sistema": usuario_sistema,
        "shopping": shopping,
        "modulo_origem": modulo_origem,
        "ip_origem": ip_origem or "127.0.0.1",
        "detalhes": detalhes or {},
        "dado_anterior": dado_anterior,
        "dado_novo": dado_novo,
        "observacao": observacao,
        "resolvido": True if nivel not in ["ALERTA", "CRITICO", "ERRO"] else False
    }

    dados["registros"].append(registro)

    # Atualiza estatísticas
    est = dados["estatisticas"]
    est["total_por_nivel"][nivel] = est["total_por_nivel"].get(nivel, 0) + 1
    est["total_por_categoria"][categoria] = est["total_por_categoria"].get(categoria, 0) + 1
    if shopping:
        est["total_por_shopping"][shopping] = est["total_por_shopping"].get(shopping, 0) + 1
    if resultado == "SUCESSO":
        est["total_sucessos"] += 1
    elif resultado == "FALHA":
        est["total_falhas"] += 1
    elif resultado == "NEGADO":
        est["total_acessos_negados"] += 1

    _salvar_registros(dados)

    # Se for alerta ou crítico, adiciona também na fila de alertas
    if nivel in ["ALERTA", "CRITICO", "ERRO"]:
        _criar_alerta(registro_id, acao, categoria, nivel, usuario_sistema, shopping, detalhes, observacao)

    return registro_id

# ─────────────────────────────────────────────
#   ATALHOS DE REGISTRO POR CATEGORIA
# ─────────────────────────────────────────────

def reg_login(usuario: str, sucesso: bool, ip: str = None, motivo_falha: str = None, shopping: str = None):
    if sucesso:
        registrar(
            acao="Login realizado com sucesso",
            categoria=CategoriaAcao.AUTENTICACAO.value,
            nivel=NivelRegistro.INFO.value,
            resultado=ResultadoAcao.SUCESSO.value,
            usuario_sistema=usuario,
            ip_origem=ip,
            shopping=shopping,
            detalhes={"metodo": "usuario_senha"}
        )
    else:
        registrar(
            acao="Tentativa de login falhou",
            categoria=CategoriaAcao.AUTENTICACAO.value,
            nivel=NivelRegistro.AVISO.value,
            resultado=ResultadoAcao.FALHA.value,
            usuario_sistema=usuario,
            ip_origem=ip,
            shopping=shopping,
            detalhes={"motivo": motivo_falha or "Senha incorreta"},
            observacao=f"Falha de autenticação para o usuário: {usuario}"
        )

def reg_logout(usuario: str, shopping: str = None):
    registrar(
        acao="Logout realizado",
        categoria=CategoriaAcao.AUTENTICACAO.value,
        nivel=NivelRegistro.INFO.value,
        resultado=ResultadoAcao.SUCESSO.value,
        usuario_sistema=usuario,
        shopping=shopping
    )

def reg_usuario_bloqueado(usuario: str, tentativas: int, ip: str = None):
    registrar(
        acao=f"Usuário bloqueado por excesso de tentativas",
        categoria=CategoriaAcao.SEGURANCA.value,
        nivel=NivelRegistro.CRITICO.value,
        resultado=ResultadoAcao.NEGADO.value,
        usuario_sistema=usuario,
        ip_origem=ip,
        detalhes={"tentativas": tentativas, "limite": 5},
        observacao=f"Conta bloqueada após {tentativas} tentativas consecutivas"
    )

def reg_cadastro_usuario(admin: str, nome_novo: str, perfil: str, shopping: str = None):
    registrar(
        acao=f"Novo usuário cadastrado: {nome_novo}",
        categoria=CategoriaAcao.USUARIOS.value,
        nivel=NivelRegistro.INFO.value,
        resultado=ResultadoAcao.SUCESSO.value,
        usuario_sistema=admin,
        shopping=shopping,
        detalhes={"nome": nome_novo, "perfil": perfil}
    )

def reg_edicao_usuario(admin: str, nome: str, campos_alterados: list, antes: dict = None, depois: dict = None, shopping: str = None):
    registrar(
        acao=f"Usuário editado: {nome}",
        categoria=CategoriaAcao.USUARIOS.value,
        nivel=NivelRegistro.AVISO.value,
        resultado=ResultadoAcao.SUCESSO.value,
        usuario_sistema=admin,
        shopping=shopping,
        detalhes={"campos_alterados": campos_alterados},
        dado_anterior=antes,
        dado_novo=depois
    )

def reg_exclusao_usuario(admin: str, nome: str, motivo: str = None, shopping: str = None):
    registrar(
        acao=f"Usuário excluído: {nome}",
        categoria=CategoriaAcao.USUARIOS.value,
        nivel=NivelRegistro.ALERTA.value,
        resultado=ResultadoAcao.SUCESSO.value,
        usuario_sistema=admin,
        shopping=shopping,
        detalhes={"nome_excluido": nome},
        observacao=motivo or "Sem motivo informado"
    )

def reg_ambiente(admin: str, acao_tipo: str, nome_ambiente: str, shopping: str = None):
    nivel = NivelRegistro.INFO.value if acao_tipo == "cadastro" else NivelRegistro.AVISO.value
    registrar(
        acao=f"Ambiente {acao_tipo}: {nome_ambiente}",
        categoria=CategoriaAcao.AMBIENTES.value,
        nivel=nivel,
        resultado=ResultadoAcao.SUCESSO.value,
        usuario_sistema=admin,
        shopping=shopping,
        detalhes={"ambiente": nome_ambiente, "operacao": acao_tipo}
    )

def reg_equipamento(admin: str, acao_tipo: str, equipamento: str, local: str = None, shopping: str = None):
    registrar(
        acao=f"Equipamento {acao_tipo}: {equipamento}",
        categoria=CategoriaAcao.EQUIPAMENTOS.value,
        nivel=NivelRegistro.INFO.value,
        resultado=ResultadoAcao.SUCESSO.value,
        usuario_sistema=admin,
        shopping=shopping,
        detalhes={"equipamento": equipamento, "local": local, "operacao": acao_tipo}
    )

def reg_equipamento_falha(equipamento: str, tipo_falha: str, local: str, shopping: str = None):
    registrar(
        acao=f"Falha em equipamento: {equipamento}",
        categoria=CategoriaAcao.EQUIPAMENTOS.value,
        nivel=NivelRegistro.CRITICO.value,
        resultado=ResultadoAcao.FALHA.value,
        usuario_sistema="sistema",
        shopping=shopping,
        detalhes={"equipamento": equipamento, "falha": tipo_falha, "local": local},
        observacao=f"Equipamento {equipamento} em {local} reportou: {tipo_falha}"
    )

def reg_alerta_monitoramento(tipo_alerta: str, local: str, shopping: str, nivel: str = "ALERTA", detalhes_extras: dict = None):
    registrar(
        acao=f"Alerta de monitoramento: {tipo_alerta}",
        categoria=CategoriaAcao.MONITORAMENTO.value,
        nivel=nivel,
        resultado=ResultadoAcao.PENDENTE.value,
        usuario_sistema="camera_ia",
        shopping=shopping,
        detalhes={"tipo": tipo_alerta, "local": local, **(detalhes_extras or {})}
    )

def reg_alerta_estacionamento(tipo_alerta: str, placa: str, local: str, shopping: str):
    registrar(
        acao=f"Alerta no estacionamento: {tipo_alerta}",
        categoria=CategoriaAcao.ESTACIONAMENTO.value,
        nivel=NivelRegistro.ALERTA.value,
        resultado=ResultadoAcao.PENDENTE.value,
        usuario_sistema="sistema_lpr",
        shopping=shopping,
        detalhes={"tipo": tipo_alerta, "placa": placa, "local": local}
    )

def reg_modulo_sistema(admin: str, modulo: str, acao: str):
    nivel = NivelRegistro.AVISO.value if acao == "desativado" else NivelRegistro.INFO.value
    registrar(
        acao=f"Módulo do sistema {acao}: {modulo}",
        categoria=CategoriaAcao.MODULOS.value,
        nivel=nivel,
        resultado=ResultadoAcao.SUCESSO.value,
        usuario_sistema=admin,
        detalhes={"modulo": modulo, "acao": acao}
    )

def reg_acesso_negado(usuario: str, recurso: str, motivo: str, ip: str = None):
    registrar(
        acao=f"Acesso negado ao recurso: {recurso}",
        categoria=CategoriaAcao.ACESSO.value,
        nivel=NivelRegistro.ALERTA.value,
        resultado=ResultadoAcao.NEGADO.value,
        usuario_sistema=usuario,
        ip_origem=ip,
        detalhes={"recurso": recurso, "motivo": motivo},
        observacao=f"Usuário {usuario} tentou acessar {recurso} sem permissão"
    )

def reg_relatorio(usuario: str, tipo_relatorio: str, periodo: str, shopping: str = None):
    registrar(
        acao=f"Relatório gerado: {tipo_relatorio}",
        categoria=CategoriaAcao.RELATORIOS.value,
        nivel=NivelRegistro.INFO.value,
        resultado=ResultadoAcao.SUCESSO.value,
        usuario_sistema=usuario,
        shopping=shopping,
        detalhes={"tipo": tipo_relatorio, "periodo": periodo}
    )

def reg_backup(usuario: str, sucesso: bool, tamanho_mb: float = None):
    registrar(
        acao="Backup do sistema realizado" if sucesso else "Falha ao realizar backup",
        categoria=CategoriaAcao.SISTEMA.value,
        nivel=NivelRegistro.INFO.value if sucesso else NivelRegistro.CRITICO.value,
        resultado=ResultadoAcao.SUCESSO.value if sucesso else ResultadoAcao.FALHA.value,
        usuario_sistema=usuario,
        detalhes={"tamanho_mb": tamanho_mb}
    )

def reg_erro_sistema(modulo: str, descricao_erro: str, traceback: str = None):
    registrar(
        acao=f"Erro no sistema: {modulo}",
        categoria=CategoriaAcao.SISTEMA.value,
        nivel=NivelRegistro.ERRO.value,
        resultado=ResultadoAcao.FALHA.value,
        usuario_sistema="sistema",
        modulo_origem=modulo,
        detalhes={"erro": descricao_erro, "traceback": traceback},
        observacao=f"Erro crítico detectado em {modulo}"
    )

# ─────────────────────────────────────────────
#   GESTÃO DE ALERTAS
# ─────────────────────────────────────────────

def _criar_alerta(registro_id, acao, categoria, nivel, usuario, shopping, detalhes, observacao):
    dados = _carregar_alertas()
    alerta = {
        "id": f"ALT-{str(uuid.uuid4())[:6].upper()}",
        "registro_id": registro_id,
        "timestamp": datetime.now().isoformat(),
        "acao": acao,
        "categoria": categoria,
        "nivel": nivel,
        "usuario": usuario,
        "shopping": shopping,
        "detalhes": detalhes or {},
        "observacao": observacao,
        "resolvido": False,
        "resolvido_por": None,
        "resolvido_em": None,
        "resolucao": None
    }
    dados["alertas_ativos"].append(alerta)
    _salvar_alertas(dados)

def resolver_alerta(alerta_id: str, resolvido_por: str, resolucao: str) -> bool:
    dados = _carregar_alertas()
    for i, alerta in enumerate(dados["alertas_ativos"]):
        if alerta["id"] == alerta_id:
            alerta["resolvido"] = True
            alerta["resolvido_por"] = resolvido_por
            alerta["resolvido_em"] = datetime.now().isoformat()
            alerta["resolucao"] = resolucao
            dados["alertas_resolvidos"].append(alerta)
            dados["alertas_ativos"].pop(i)
            _salvar_alertas(dados)
            registrar(
                acao=f"Alerta resolvido: {alerta_id}",
                categoria=CategoriaAcao.SEGURANCA.value,
                nivel=NivelRegistro.INFO.value,
                resultado=ResultadoAcao.SUCESSO.value,
                usuario_sistema=resolvido_por,
                detalhes={"alerta_id": alerta_id, "resolucao": resolucao}
            )
            return True
    return False

def listar_alertas_ativos(nivel_minimo: str = None, shopping: str = None) -> list:
    dados = _carregar_alertas()
    alertas = dados["alertas_ativos"]
    if nivel_minimo:
        ordem = ["INFO", "AVISO", "ALERTA", "CRITICO", "ERRO"]
        idx = ordem.index(nivel_minimo) if nivel_minimo in ordem else 0
        alertas = [a for a in alertas if ordem.index(a["nivel"]) >= idx]
    if shopping:
        alertas = [a for a in alertas if a.get("shopping") == shopping]
    return sorted(alertas, key=lambda x: x["timestamp"], reverse=True)

# ─────────────────────────────────────────────
#   CONSULTAS
# ─────────────────────────────────────────────

def listar_registros(
    limite: int = 50,
    nivel: str = None,
    categoria: str = None,
    usuario: str = None,
    shopping: str = None,
    resultado: str = None,
    data_inicio: str = None,
    data_fim: str = None
) -> list:
    dados = _carregar_registros()
    registros = dados["registros"]

    if nivel:
        registros = [r for r in registros if r["nivel"] == nivel]
    if categoria:
        registros = [r for r in registros if r["categoria"] == categoria]
    if usuario:
        registros = [r for r in registros if r["usuario_sistema"] == usuario]
    if shopping:
        registros = [r for r in registros if r.get("shopping") == shopping]
    if resultado:
        registros = [r for r in registros if r["resultado"] == resultado]
    if data_inicio:
        registros = [r for r in registros if r["data"] >= data_inicio]
    if data_fim:
        registros = [r for r in registros if r["data"] <= data_fim]

    return sorted(registros, key=lambda x: x["timestamp"], reverse=True)[:limite]

def obter_estatisticas() -> dict:
    dados = _carregar_registros()
    alertas = _carregar_alertas()
    est = dados["estatisticas"]
    return {
        "total_registros": dados["metadados"]["total_registros"],
        "total_por_nivel": est["total_por_nivel"],
        "total_por_categoria": est["total_por_categoria"],
        "total_por_shopping": est["total_por_shopping"],
        "total_falhas": est["total_falhas"],
        "total_sucessos": est["total_sucessos"],
        "total_acessos_negados": est["total_acessos_negados"],
        "alertas_ativos": len(alertas["alertas_ativos"]),
        "alertas_resolvidos": len(alertas["alertas_resolvidos"])
    }

def registros_de_hoje() -> list:
    hoje = datetime.now().strftime("%d/%m/%Y")
    dados = _carregar_registros()
    return [r for r in dados["registros"] if r["data"] == hoje]

def registros_criticos_nao_resolvidos() -> list:
    dados = _carregar_registros()
    return [
        r for r in dados["registros"]
        if r["nivel"] in ["CRITICO", "ERRO"] and not r.get("resolvido", True)
    ]

# ─────────────────────────────────────────────
#   MENU INTERATIVO
# ─────────────────────────────────────────────

def _exibir_registro(r: dict):
    icones = {"INFO": "ℹ️", "AVISO": "⚠️", "ALERTA": "🚨", "CRITICO": "🔴", "ERRO": "💥"}
    icone = icones.get(r["nivel"], "•")
    print(f"\n  {icone} [{r['id']}] {r['data']} {r['hora']}")
    print(f"     Ação    : {r['acao']}")
    print(f"     Categoria: {r['categoria']} | Nível: {r['nivel']} | Resultado: {r['resultado']}")
    print(f"     Usuário : {r['usuario_sistema']} | Shopping: {r.get('shopping', '-')}")
    if r.get("observacao"):
        print(f"     Obs     : {r['observacao']}")

def menu():
    while True:
        print("\n" + "="*60)
        print("  🔍 SHOPCONTROL — AUDITORIA / REGISTROS")
        print("="*60)
        est = obter_estatisticas()
        print(f"  Total de registros : {est['total_registros']}")
        print(f"  Alertas ativos     : {est['alertas_ativos']}")
        print(f"  Erros/Críticos     : {est['total_por_nivel'].get('CRITICO',0) + est['total_por_nivel'].get('ERRO',0)}")
        print("="*60)
        print("  1. Ver últimos 20 registros")
        print("  2. Filtrar por nível (INFO/AVISO/ALERTA/CRITICO/ERRO)")
        print("  3. Filtrar por categoria")
        print("  4. Filtrar por usuário")
        print("  5. Filtrar por shopping")
        print("  6. Ver registros de hoje")
        print("  7. Ver alertas ativos")
        print("  8. Resolver um alerta")
        print("  9. Ver estatísticas completas")
        print(" 10. Simular registros de exemplo")
        print("  0. Sair")
        print("="*60)
        op = input("  Escolha: ").strip()

        if op == "1":
            regs = listar_registros(limite=20)
            if not regs:
                print("\n  Nenhum registro encontrado.")
            for r in regs:
                _exibir_registro(r)

        elif op == "2":
            nivel = input("  Nível (INFO/AVISO/ALERTA/CRITICO/ERRO): ").strip().upper()
            regs = listar_registros(nivel=nivel)
            print(f"\n  {len(regs)} registro(s) encontrado(s):")
            for r in regs:
                _exibir_registro(r)

        elif op == "3":
            print("  Categorias: Autenticação, Usuários, Ambientes, Equipamentos,")
            print("              Monitoramento, Estacionamento, Módulos do Sistema,")
            print("              Relatórios, Sistema, Segurança, Controle de Acesso")
            cat = input("  Categoria: ").strip()
            regs = listar_registros(categoria=cat)
            print(f"\n  {len(regs)} registro(s):")
            for r in regs:
                _exibir_registro(r)

        elif op == "4":
            usuario = input("  Nome do usuário: ").strip()
            regs = listar_registros(usuario=usuario)
            print(f"\n  {len(regs)} registro(s) de '{usuario}':")
            for r in regs:
                _exibir_registro(r)

        elif op == "5":
            shopping = input("  Shopping (ex: Shopping 1): ").strip()
            regs = listar_registros(shopping=shopping)
            print(f"\n  {len(regs)} registro(s) de '{shopping}':")
            for r in regs:
                _exibir_registro(r)

        elif op == "6":
            regs = registros_de_hoje()
            print(f"\n  {len(regs)} registro(s) hoje:")
            for r in regs:
                _exibir_registro(r)

        elif op == "7":
            alertas = listar_alertas_ativos()
            if not alertas:
                print("\n  ✅ Nenhum alerta ativo no momento.")
            for a in alertas:
                print(f"\n  🚨 [{a['id']}] {a['nivel']} — {a['acao']}")
                print(f"     Shopping: {a.get('shopping','-')} | Usuário: {a['usuario']}")
                print(f"     Obs: {a.get('observacao','-')}")

        elif op == "8":
            alertas = listar_alertas_ativos()
            if not alertas:
                print("\n  Nenhum alerta ativo.")
            else:
                alerta_id = input("  ID do alerta a resolver: ").strip().upper()
                resolvido_por = input("  Seu nome: ").strip()
                resolucao = input("  Descrição da resolução: ").strip()
                if resolver_alerta(alerta_id, resolvido_por, resolucao):
                    print(f"\n  ✅ Alerta {alerta_id} resolvido com sucesso!")
                else:
                    print(f"\n  ❌ Alerta {alerta_id} não encontrado.")

        elif op == "9":
            est = obter_estatisticas()
            print("\n  📊 ESTATÍSTICAS COMPLETAS:")
            print(f"  Total de registros : {est['total_registros']}")
            print(f"  Sucessos           : {est['total_sucessos']}")
            print(f"  Falhas             : {est['total_falhas']}")
            print(f"  Acessos negados    : {est['total_acessos_negados']}")
            print(f"  Alertas ativos     : {est['alertas_ativos']}")
            print(f"  Alertas resolvidos : {est['alertas_resolvidos']}")
            print("\n  Por nível:")
            for nivel, total in est["total_por_nivel"].items():
                print(f"    {nivel:10}: {total}")
            print("\n  Por categoria:")
            for cat, total in est["total_por_categoria"].items():
                print(f"    {cat:30}: {total}")
            print("\n  Por shopping:")
            for sh, total in est["total_por_shopping"].items():
                print(f"    {sh:20}: {total}")

        elif op == "10":
            print("\n  Simulando registros de exemplo...")
            reg_login("admin", True, "192.168.1.10", shopping="Shopping 1")
            reg_login("funcionario01", False, "192.168.1.55", motivo_falha="Senha incorreta", shopping="Shopping 2")
            reg_login("funcionario01", False, "192.168.1.55", motivo_falha="Senha incorreta", shopping="Shopping 2")
            reg_usuario_bloqueado("funcionario01", 5, "192.168.1.55")
            reg_cadastro_usuario("admin", "Maria Silva", "Visitante", "Shopping 1")
            reg_edicao_usuario("admin", "João Ferreira", ["telefone", "email"],
                               antes={"telefone": "11999999999"},
                               depois={"telefone": "11888888888"},
                               shopping="Shopping 1")
            reg_exclusao_usuario("admin", "Carlos Lima", "Funcionário desligado", "Shopping 3")
            reg_ambiente("admin", "cadastro", "Praça de Alimentação", "Shopping 2")
            reg_equipamento("tecnico01", "instalado", "Câmera IP HD-400", "Entrada Principal", "Shopping 1")
            reg_equipamento_falha("Câmera IP HD-400", "Sem sinal de vídeo", "Corredor Ala B", "Shopping 3")
            reg_alerta_monitoramento("Aglomeração suspeita", "Praça Central", "Shopping 1", "ALERTA")
            reg_alerta_monitoramento("Fumaça detectada", "Estacionamento Subsolo", "Shopping 2", "CRITICO",
                                     {"temperatura": "42°C", "camera": "CAM-017"})
            reg_alerta_estacionamento("Veículo em lista negra", "ABC-1234", "Cancela Entrada", "Shopping 4")
            reg_modulo_sistema("admin", "Módulo de Mapa de Calor", "ativado")
            reg_acesso_negado("visitante_temp", "Painel Administrativo", "Sem permissão", "192.168.1.99")
            reg_relatorio("admin", "Relatório de Segurança Mensal", "Maio 2026", "Shopping 1")
            reg_backup("sistema", True, 245.7)
            reg_logout("admin", "Shopping 1")
            print("  ✅ 18 registros de exemplo criados com sucesso!")

        elif op == "0":
            print("\n  Saindo do módulo de registros...\n")
            break
        else:
            print("\n  ❌ Opção inválida.")

if __name__ == "__main__":
    menu()