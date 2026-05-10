"""
╔══════════════════════════════════════════════════════════╗
║           ShopControl — Dashboard Principal              ║
║     Sistema de Controle de Acesso Inteligente            ║
║                  Rede de 4 Shoppings                     ║
╚══════════════════════════════════════════════════════════╝

Execução: python dashboard.py

Conecta com todos os módulos:
  - Controle de Acesso/usuarios.py
  - Controle de Acesso/ambientes.py
  - Monitoramento de Ambientes/monitoramento_predios.py
  - Monitoramento de Ambientes/monitoramento_estacionamento.py
  - Auditoria/registros.py
"""

import sys
import os
import json
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea, QTableWidget,
    QTableWidgetItem, QHeaderView, QLineEdit, QComboBox,
    QDialog, QFormLayout, QMessageBox, QSizePolicy, QSpacerItem,
    QStackedWidget, QGridLayout, QTextEdit, QProgressBar,
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QIcon, QPixmap, QPainter,
    QLinearGradient, QBrush, QPen, QFontDatabase,
)


# ══════════════════════════════════════════════════════════
#  PALETA DE CORES — Tema escuro profissional
# ══════════════════════════════════════════════════════════

CORES = {
    # Fundos
    "bg_escuro":      "#0A0E1A",
    "bg_sidebar":     "#0D1120",
    "bg_card":        "#111827",
    "bg_card2":       "#161D2F",
    "bg_input":       "#1C2438",
    "bg_hover":       "#1E2A40",
    "bg_tabela":      "#0F1623",

    # Texto
    "texto_principal":"#E8EDF5",
    "texto_sec":      "#7A8BA8",
    "texto_muted":    "#4A5568",

    # Acentos
    "azul":           "#3B7FE8",
    "azul_claro":     "#5B9BFF",
    "azul_glow":      "#1A4A9A",
    "verde":          "#10B981",
    "verde_claro":    "#34D399",
    "vermelho":       "#EF4444",
    "vermelho_claro": "#F87171",
    "amarelo":        "#F59E0B",
    "amarelo_claro":  "#FCD34D",
    "roxo":           "#8B5CF6",
    "ciano":          "#06B6D4",

    # Bordas
    "borda":          "#1E2D45",
    "borda_azul":     "#2A4A7F",
}

# ══════════════════════════════════════════════════════════
#  ESTILOS GLOBAIS (QSS — CSS do PyQt6)
# ══════════════════════════════════════════════════════════

ESTILO_GLOBAL = f"""
QMainWindow, QDialog {{
    background-color: {CORES['bg_escuro']};
}}
QWidget {{
    background-color: transparent;
    color: {CORES['texto_principal']};
    font-family: 'Segoe UI', 'SF Pro Display', Arial;
    font-size: 13px;
}}
QScrollBar:vertical {{
    background: {CORES['bg_card']};
    width: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {CORES['borda_azul']};
    border-radius: 3px;
    min-height: 30px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar:horizontal {{
    background: {CORES['bg_card']};
    height: 6px;
}}
QScrollBar::handle:horizontal {{
    background: {CORES['borda_azul']};
    border-radius: 3px;
}}
QTableWidget {{
    background-color: {CORES['bg_tabela']};
    border: 1px solid {CORES['borda']};
    border-radius: 8px;
    gridline-color: {CORES['borda']};
    color: {CORES['texto_principal']};
    selection-background-color: {CORES['bg_hover']};
    font-size: 12px;
}}
QTableWidget::item {{
    padding: 8px 12px;
    border-bottom: 1px solid {CORES['borda']};
}}
QTableWidget::item:selected {{
    background-color: {CORES['bg_hover']};
    color: {CORES['azul_claro']};
}}
QHeaderView::section {{
    background-color: {CORES['bg_card2']};
    color: {CORES['texto_sec']};
    padding: 10px 12px;
    border: none;
    border-bottom: 1px solid {CORES['borda']};
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
}}
QLineEdit {{
    background-color: {CORES['bg_input']};
    border: 1px solid {CORES['borda']};
    border-radius: 8px;
    padding: 10px 14px;
    color: {CORES['texto_principal']};
    font-size: 13px;
}}
QLineEdit:focus {{
    border: 1px solid {CORES['azul']};
    background-color: {CORES['bg_hover']};
}}
QComboBox {{
    background-color: {CORES['bg_input']};
    border: 1px solid {CORES['borda']};
    border-radius: 8px;
    padding: 10px 14px;
    color: {CORES['texto_principal']};
    font-size: 13px;
    min-width: 140px;
}}
QComboBox:focus {{
    border: 1px solid {CORES['azul']};
}}
QComboBox::drop-down {{
    border: none;
    width: 30px;
}}
QComboBox QAbstractItemView {{
    background-color: {CORES['bg_card2']};
    border: 1px solid {CORES['borda']};
    color: {CORES['texto_principal']};
    selection-background-color: {CORES['bg_hover']};
    outline: none;
}}
QTextEdit {{
    background-color: {CORES['bg_input']};
    border: 1px solid {CORES['borda']};
    border-radius: 8px;
    padding: 10px;
    color: {CORES['texto_principal']};
}}
QProgressBar {{
    background-color: {CORES['bg_card2']};
    border: none;
    border-radius: 4px;
    height: 6px;
    text-align: center;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {CORES['azul']}, stop:1 {CORES['azul_claro']});
    border-radius: 4px;
}}
QMessageBox {{
    background-color: {CORES['bg_card']};
}}
QMessageBox QLabel {{
    color: {CORES['texto_principal']};
}}
QMessageBox QPushButton {{
    background-color: {CORES['azul']};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    min-width: 80px;
}}
"""


# ══════════════════════════════════════════════════════════
#  COMPONENTES REUTILIZÁVEIS
# ══════════════════════════════════════════════════════════

def btn_primario(texto, cor=None):
    """Botão primário azul estilizado."""
    b = QPushButton(texto)
    cor = cor or CORES['azul']
    b.setStyleSheet(f"""
        QPushButton {{
            background-color: {cor};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 13px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: {CORES['azul_claro']};
        }}
        QPushButton:pressed {{
            background-color: {CORES['azul_glow']};
        }}
    """)
    return b


def btn_secundario(texto):
    """Botão secundário transparente."""
    b = QPushButton(texto)
    b.setStyleSheet(f"""
        QPushButton {{
            background-color: transparent;
            color: {CORES['texto_sec']};
            border: 1px solid {CORES['borda']};
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 13px;
        }}
        QPushButton:hover {{
            background-color: {CORES['bg_hover']};
            color: {CORES['texto_principal']};
            border-color: {CORES['borda_azul']};
        }}
    """)
    return b


def separador():
    """Linha separadora horizontal."""
    linha = QFrame()
    linha.setFrameShape(QFrame.Shape.HLine)
    linha.setStyleSheet(f"background-color: {CORES['borda']}; max-height: 1px;")
    return linha


def label_titulo(texto, tamanho=22):
    """Label de título grande."""
    l = QLabel(texto)
    l.setStyleSheet(f"""
        color: {CORES['texto_principal']};
        font-size: {tamanho}px;
        font-weight: 700;
        letter-spacing: -0.5px;
    """)
    return l


def label_sec(texto, tamanho=12):
    """Label secundário."""
    l = QLabel(texto)
    l.setStyleSheet(f"color: {CORES['texto_sec']}; font-size: {tamanho}px;")
    return l


def card_frame(padding=20, radius=12):
    """Frame estilizado como card."""
    f = QFrame()
    f.setStyleSheet(f"""
        QFrame {{
            background-color: {CORES['bg_card']};
            border: 1px solid {CORES['borda']};
            border-radius: {radius}px;
            padding: {padding}px;
        }}
    """)
    return f


def badge(texto, cor):
    """Badge colorido de status."""
    l = QLabel(f"  {texto}  ")
    l.setAlignment(Qt.AlignmentFlag.AlignCenter)
    l.setStyleSheet(f"""
        background-color: {cor}22;
        color: {cor};
        border: 1px solid {cor}44;
        border-radius: 10px;
        padding: 3px 8px;
        font-size: 11px;
        font-weight: 600;
    """)
    l.setFixedHeight(22)
    return l


# ══════════════════════════════════════════════════════════
#  CAMADA DE DADOS — Lê os JSONs do projeto
# ══════════════════════════════════════════════════════════

def _pasta_dados():
    """Localiza a pasta dados/ relativa ao dashboard.py."""
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "dados")


def _ler_json(nome_arquivo):
    caminho = os.path.join(_pasta_dados(), nome_arquivo)
    if not os.path.exists(caminho):
        return {}
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


def _salvar_json(nome_arquivo, dados):
    os.makedirs(_pasta_dados(), exist_ok=True)
    caminho = os.path.join(_pasta_dados(), nome_arquivo)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)


def get_usuarios():
    return _ler_json("usuarios.json").get("usuarios", [])


def get_ambientes():
    return _ler_json("ambientes.json").get("ambientes", [])


def get_eventos_predios():
    return _ler_json("monitoramento_predios.json").get("eventos", [])


def get_alertas_predios():
    return _ler_json("monitoramento_predios.json").get("alertas_ativos", [])


def get_veiculos_ativos():
    return _ler_json("monitoramento_estacionamento.json").get("veiculos_ativos", {})


def get_vagas():
    return _ler_json("monitoramento_estacionamento.json").get("vagas_status", {})


def get_alertas_estac():
    return _ler_json("monitoramento_estacionamento.json").get("alertas_ativos", [])


def get_registros():
    return _ler_json("registros.json").get("registros", [])


def get_modulos():
    return _ler_json("modulos.json").get("modulos", [])


# ══════════════════════════════════════════════════════════
#  CARD DE ESTATÍSTICA
# ══════════════════════════════════════════════════════════

class CardEstat(QFrame):
    def __init__(self, titulo, valor, subtitulo="", cor=None, icone=""):
        super().__init__()
        self.cor = cor or CORES['azul']
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {CORES['bg_card']};
                border: 1px solid {CORES['borda']};
                border-radius: 12px;
                padding: 0px;
            }}
            QFrame:hover {{
                border: 1px solid {self.cor}55;
                background-color: {CORES['bg_card2']};
            }}
        """)
        self.setMinimumHeight(110)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(6)

        # Topo: título + ícone
        topo = QHBoxLayout()
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet(f"color: {CORES['texto_sec']}; font-size: 12px; font-weight: 500;")
        topo.addWidget(lbl_titulo)
        topo.addStretch()
        if icone:
            lbl_icone = QLabel(icone)
            lbl_icone.setStyleSheet(f"font-size: 18px;")
            topo.addWidget(lbl_icone)
        lay.addLayout(topo)

        # Valor grande
        lbl_valor = QLabel(str(valor))
        lbl_valor.setStyleSheet(f"""
            color: {self.cor};
            font-size: 32px;
            font-weight: 700;
            letter-spacing: -1px;
        """)
        lay.addWidget(lbl_valor)

        # Subtítulo
        if subtitulo:
            lbl_sub = QLabel(subtitulo)
            lbl_sub.setStyleSheet(f"color: {CORES['texto_muted']}; font-size: 11px;")
            lay.addWidget(lbl_sub)

        # Barra colorida no fundo
        barra = QFrame()
        barra.setFixedHeight(3)
        barra.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {self.cor}, stop:1 transparent);
            border-radius: 2px;
            border: none;
        """)
        lay.addWidget(barra)


# ══════════════════════════════════════════════════════════
#  ITEM DO MENU LATERAL
# ══════════════════════════════════════════════════════════

class ItemMenu(QPushButton):
    def __init__(self, texto, icone="", pagina=0):
        super().__init__()
        self.pagina = pagina
        self.ativo = False
        self.texto = texto
        self.icone = icone
        self.setText(f"  {icone}  {texto}")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(44)
        self._atualizar_estilo()

    def _atualizar_estilo(self):
        if self.ativo:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {CORES['azul']}18;
                    color: {CORES['azul_claro']};
                    border: none;
                    border-left: 3px solid {CORES['azul']};
                    border-radius: 0px;
                    text-align: left;
                    padding-left: 16px;
                    font-size: 13px;
                    font-weight: 600;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {CORES['texto_sec']};
                    border: none;
                    border-left: 3px solid transparent;
                    border-radius: 0px;
                    text-align: left;
                    padding-left: 16px;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background-color: {CORES['bg_hover']};
                    color: {CORES['texto_principal']};
                }}
            """)

    def set_ativo(self, ativo):
        self.ativo = ativo
        self._atualizar_estilo()


# ══════════════════════════════════════════════════════════
#  TELA DE LOGIN
# ══════════════════════════════════════════════════════════

class TelaLogin(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ShopControl — Login")
        self.setFixedSize(900, 580)
        self.setStyleSheet(f"background-color: {CORES['bg_escuro']};")
        self.login_ok = False
        self._build()

    def _build(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # ── Lado esquerdo — identidade ──
        esq = QFrame()
        esq.setFixedWidth(380)
        esq.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #0D1B3E, stop:0.5 #0A1628, stop:1 #061020);
            border-right: 1px solid {CORES['borda']};
        """)
        lay_esq = QVBoxLayout(esq)
        lay_esq.setContentsMargins(50, 60, 50, 40)
        lay_esq.setSpacing(0)

        # Logo
        logo_frame = QFrame()
        logo_frame.setFixedSize(72, 72)
        logo_frame.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {CORES['azul']}, stop:1 {CORES['roxo']});
            border-radius: 18px;
        """)
        logo_lay = QVBoxLayout(logo_frame)
        logo_ico = QLabel("🏬")
        logo_ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_ico.setStyleSheet("font-size: 32px; background: transparent;")
        logo_lay.addWidget(logo_ico)
        lay_esq.addWidget(logo_frame)
        lay_esq.addSpacing(24)

        # Nome
        nome = QLabel("ShopControl")
        nome.setStyleSheet(f"""
            color: white;
            font-size: 28px;
            font-weight: 700;
            letter-spacing: -0.5px;
            background: transparent;
        """)
        lay_esq.addWidget(nome)

        sub = QLabel("Sistema de Controle de Acesso\nInteligente para Shoppings")
        sub.setStyleSheet(f"color: {CORES['texto_sec']}; font-size: 13px; background: transparent; line-height: 1.5;")
        lay_esq.addSpacing(8)
        lay_esq.addWidget(sub)

        lay_esq.addSpacing(40)
        linha = QFrame()
        linha.setFixedHeight(1)
        linha.setStyleSheet(f"background: {CORES['borda']}; border: none;")
        lay_esq.addWidget(linha)
        lay_esq.addSpacing(30)

        # Shoppings
        shops_label = QLabel("Rede de Shoppings")
        shops_label.setStyleSheet(f"color: {CORES['texto_muted']}; font-size: 11px; font-weight: 600; letter-spacing: 1px; background: transparent;")
        lay_esq.addWidget(shops_label)
        lay_esq.addSpacing(12)

        for nome_sh in ["Shopping 1", "Shopping 2", "Shopping 3", "Shopping 4"]:
            sh = QLabel(f"  ●  {nome_sh}")
            sh.setStyleSheet(f"color: {CORES['texto_sec']}; font-size: 13px; background: transparent;")
            lay_esq.addWidget(sh)
            lay_esq.addSpacing(4)

        lay_esq.addStretch()

        rodape = QLabel("© 2026 ShopControl. Todos os direitos reservados.")
        rodape.setStyleSheet(f"color: {CORES['texto_muted']}; font-size: 10px; background: transparent;")
        lay_esq.addWidget(rodape)

        lay.addWidget(esq)

        # ── Lado direito — formulário ──
        dir = QFrame()
        dir.setStyleSheet(f"background-color: {CORES['bg_escuro']};")
        lay_dir = QVBoxLayout(dir)
        lay_dir.setContentsMargins(60, 0, 60, 0)
        lay_dir.setAlignment(Qt.AlignmentFlag.AlignCenter)

        titulo = QLabel("Bem-vindo de volta 👋")
        titulo.setStyleSheet(f"""
            color: {CORES['texto_principal']};
            font-size: 26px;
            font-weight: 700;
        """)
        lay_dir.addWidget(titulo)
        lay_dir.addSpacing(6)

        subtitulo = QLabel("Faça login para acessar o painel de controle.")
        subtitulo.setStyleSheet(f"color: {CORES['texto_sec']}; font-size: 13px;")
        lay_dir.addWidget(subtitulo)
        lay_dir.addSpacing(36)

        # Credenciais hint
        hint = QFrame()
        hint.setStyleSheet(f"""
            background-color: {CORES['azul']}15;
            border: 1px solid {CORES['azul']}30;
            border-radius: 8px;
            padding: 12px;
        """)
        hint_lay = QVBoxLayout(hint)
        hint_lay.setContentsMargins(14, 10, 14, 10)
        hint_tit = QLabel("🔑  Credenciais de acesso")
        hint_tit.setStyleSheet(f"color: {CORES['azul_claro']}; font-size: 12px; font-weight: 600;")
        hint_lay.addWidget(hint_tit)
        hint_info = QLabel("Usuário: admin        Senha: shopping@2024")
        hint_info.setStyleSheet(f"color: {CORES['texto_sec']}; font-size: 12px; font-family: monospace;")
        hint_lay.addWidget(hint_info)
        lay_dir.addWidget(hint)
        lay_dir.addSpacing(24)

        # Campo usuário
        lbl_user = QLabel("Usuário")
        lbl_user.setStyleSheet(f"color: {CORES['texto_sec']}; font-size: 12px; font-weight: 600;")
        lay_dir.addWidget(lbl_user)
        lay_dir.addSpacing(6)
        self.campo_user = QLineEdit()
        self.campo_user.setPlaceholderText("admin")
        self.campo_user.setText("admin")
        self.campo_user.setFixedHeight(44)
        lay_dir.addWidget(self.campo_user)
        lay_dir.addSpacing(16)

        # Campo senha
        lbl_pass = QLabel("Senha")
        lbl_pass.setStyleSheet(f"color: {CORES['texto_sec']}; font-size: 12px; font-weight: 600;")
        lay_dir.addWidget(lbl_pass)
        lay_dir.addSpacing(6)
        self.campo_pass = QLineEdit()
        self.campo_pass.setPlaceholderText("••••••••••••")
        self.campo_pass.setText("shopping@2024")
        self.campo_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.campo_pass.setFixedHeight(44)
        lay_dir.addWidget(self.campo_pass)
        lay_dir.addSpacing(6)

        # Mensagem de erro
        self.lbl_erro = QLabel("")
        self.lbl_erro.setStyleSheet(f"color: {CORES['vermelho']}; font-size: 12px;")
        lay_dir.addWidget(self.lbl_erro)
        lay_dir.addSpacing(20)

        # Botão entrar
        self.btn_entrar = btn_primario("  Entrar no Sistema  →")
        self.btn_entrar.setFixedHeight(48)
        self.btn_entrar.clicked.connect(self._fazer_login)
        lay_dir.addWidget(self.btn_entrar)

        self.campo_pass.returnPressed.connect(self._fazer_login)
        lay.addWidget(dir)

    def _fazer_login(self):
        user = self.campo_user.text().strip()
        passwd = self.campo_pass.text().strip()
        if user == "admin" and passwd == "shopping@2024":
            self.login_ok = True
            self.accept()
        else:
            self.lbl_erro.setText("⚠  Usuário ou senha inválidos.")
            self.campo_pass.clear()
            self.campo_pass.setFocus()


# ══════════════════════════════════════════════════════════
#  PÁGINA: PAINEL GERAL
# ══════════════════════════════════════════════════════════

class PaginaPainel(QWidget):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(30, 24, 30, 24)
        lay.setSpacing(20)

        # Título
        topo = QHBoxLayout()
        topo.addWidget(label_titulo("Painel de Controle de Acesso"))
        topo.addStretch()
        lbl_hora = QLabel(datetime.now().strftime("%d/%m/%Y  %H:%M"))
        lbl_hora.setStyleSheet(f"color: {CORES['texto_sec']}; font-size: 13px;")
        topo.addWidget(lbl_hora)
        lay.addLayout(topo)

        # Cards de estatística
        grid = QGridLayout()
        grid.setSpacing(14)

        usuarios = get_usuarios()
        ambientes = get_ambientes()
        veiculos = get_veiculos_ativos()
        alertas_p = [a for a in get_alertas_predios() if not a.get("resolvido")]
        alertas_e = [a for a in get_alertas_estac() if not a.get("resolvido")]
        total_alertas = len(alertas_p) + len(alertas_e)

        ativos = sum(1 for u in usuarios if u.get("status") == "Ativo")
        total_amb = len(ambientes)
        amb_ativos = sum(1 for a in ambientes if a.get("status") == "Ativo")

        cards = [
            ("Usuários Ativos",      ativos,         f"de {len(usuarios)} cadastrados",  CORES['azul'],    "👥"),
            ("Ambientes Monitorados",amb_ativos,     f"de {total_amb} ambientes",        CORES['verde'],   "🏢"),
            ("Veículos no Estac.",   len(veiculos),  "dentro agora",                     CORES['amarelo'], "🚗"),
            ("Alertas Ativos",       total_alertas,  "precisam de atenção",              CORES['vermelho'] if total_alertas > 0 else CORES['verde'], "🚨"),
        ]
        for i, (tit, val, sub, cor, ico) in enumerate(cards):
            grid.addWidget(CardEstat(tit, val, sub, cor, ico), 0, i)

        lay.addLayout(grid)

        # Segunda linha
        segunda = QHBoxLayout()
        segunda.setSpacing(14)

        # Últimos usuários cadastrados
        card_users = card_frame()
        lay_cu = QVBoxLayout(card_users)
        lay_cu.setContentsMargins(16, 16, 16, 16)
        lay_cu.setSpacing(10)
        lay_cu.addWidget(label_titulo("Últimos Cadastros", 15))
        lay_cu.addWidget(separador())

        tabela_u = QTableWidget()
        tabela_u.setColumnCount(4)
        tabela_u.setHorizontalHeaderLabels(["Nome", "Perfil", "Shopping", "Status"])
        tabela_u.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        tabela_u.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        tabela_u.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        tabela_u.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        tabela_u.verticalHeader().setVisible(False)
        tabela_u.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tabela_u.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        tabela_u.setMinimumHeight(220)

        ultimos = list(reversed(usuarios))[:8]
        tabela_u.setRowCount(len(ultimos))
        status_cores = {
            "Ativo": CORES['verde'], "Pendente": CORES['amarelo'],
            "Inativo": CORES['texto_sec'], "Bloqueado": CORES['vermelho'],
        }
        for row, u in enumerate(ultimos):
            tabela_u.setItem(row, 0, QTableWidgetItem(u.get("nome", "")))
            tabela_u.setItem(row, 1, QTableWidgetItem(u.get("perfil", "")))
            tabela_u.setItem(row, 2, QTableWidgetItem(u.get("shopping_principal", "")))
            status = u.get("status", "")
            item_s = QTableWidgetItem(f"  {status}  ")
            item_s.setForeground(QColor(status_cores.get(status, CORES['texto_sec'])))
            tabela_u.setItem(row, 3, item_s)
            tabela_u.setRowHeight(row, 36)

        lay_cu.addWidget(tabela_u)
        segunda.addWidget(card_users, 3)

        # Alertas ativos
        card_alertas = card_frame()
        lay_ca = QVBoxLayout(card_alertas)
        lay_ca.setContentsMargins(16, 16, 16, 16)
        lay_ca.setSpacing(10)
        topo_alert = QHBoxLayout()
        topo_alert.addWidget(label_titulo("Alertas Ativos", 15))
        topo_alert.addStretch()
        if total_alertas > 0:
            b = badge(f"{total_alertas} ativo(s)", CORES['vermelho'])
            topo_alert.addWidget(b)
        lay_ca.addLayout(topo_alert)
        lay_ca.addWidget(separador())

        todos_alertas = alertas_p + alertas_e
        if not todos_alertas:
            sem = QLabel("✅  Nenhum alerta ativo no momento")
            sem.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sem.setStyleSheet(f"color: {CORES['verde']}; font-size: 13px; padding: 40px;")
            lay_ca.addWidget(sem)
        else:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("border: none;")
            cont = QWidget()
            cont.setStyleSheet("background: transparent;")
            lay_cont = QVBoxLayout(cont)
            lay_cont.setSpacing(8)
            for a in todos_alertas[:10]:
                item = QFrame()
                item.setStyleSheet(f"""
                    background-color: {CORES['vermelho']}10;
                    border: 1px solid {CORES['vermelho']}30;
                    border-radius: 8px;
                    padding: 10px;
                """)
                item_lay = QVBoxLayout(item)
                item_lay.setContentsMargins(12, 8, 12, 8)
                item_lay.setSpacing(3)
                desc = QLabel(f"🚨  {a.get('descricao', a.get('tipo', ''))}")
                desc.setStyleSheet(f"color: {CORES['vermelho_claro']}; font-size: 12px; font-weight: 600;")
                desc.setWordWrap(True)
                item_lay.addWidget(desc)
                local = a.get('ambiente') or a.get('setor', '')
                info = QLabel(f"{a.get('shopping', '')}  ·  {local}  ·  {a.get('data_hora', '')[:16].replace('T', ' ')}")
                info.setStyleSheet(f"color: {CORES['texto_muted']}; font-size: 11px;")
                item_lay.addWidget(info)
                lay_cont.addWidget(item)
            lay_cont.addStretch()
            scroll.setWidget(cont)
            lay_ca.addWidget(scroll)

        segunda.addWidget(card_alertas, 2)
        lay.addLayout(segunda)

        # Ocupação estacionamento
        card_estac = card_frame()
        lay_estac = QVBoxLayout(card_estac)
        lay_estac.setContentsMargins(16, 14, 16, 14)
        lay_estac.setSpacing(10)
        lay_estac.addWidget(label_titulo("Ocupação dos Estacionamentos", 15))
        lay_estac.addWidget(separador())

        vagas = get_vagas()
        grid_estac = QGridLayout()
        grid_estac.setSpacing(12)
        col = 0
        for chave, v in list(vagas.items())[:8]:
            perc = v.get("percentual_ocupacao", 0)
            cor_barra = CORES['verde'] if perc < 75 else CORES['amarelo'] if perc < 90 else CORES['vermelho']
            bloco = QFrame()
            bloco.setStyleSheet(f"""
                background: {CORES['bg_card2']};
                border: 1px solid {CORES['borda']};
                border-radius: 8px;
            """)
            lay_b = QVBoxLayout(bloco)
            lay_b.setContentsMargins(14, 10, 14, 10)
            lay_b.setSpacing(5)
            lbl_nome = QLabel(f"{v['shopping']} — {v['setor']}")
            lbl_nome.setStyleSheet(f"color: {CORES['texto_sec']}; font-size: 11px; font-weight: 600;")
            lay_b.addWidget(lbl_nome)
            barra = QProgressBar()
            barra.setValue(int(perc))
            barra.setStyleSheet(f"""
                QProgressBar {{
                    background-color: {CORES['bg_input']};
                    border: none;
                    border-radius: 4px;
                    height: 8px;
                    text-align: center;
                }}
                QProgressBar::chunk {{
                    background-color: {cor_barra};
                    border-radius: 4px;
                }}
            """)
            barra.setTextVisible(False)
            barra.setFixedHeight(8)
            lay_b.addWidget(barra)
            lbl_num = QLabel(f"{v.get('ocupadas', 0)}/{v.get('total', 0)} vagas  ({perc}%)")
            lbl_num.setStyleSheet(f"color: {CORES['texto_muted']}; font-size: 11px;")
            lay_b.addWidget(lbl_num)
            row_g = col // 4
            col_g = col % 4
            grid_estac.addWidget(bloco, row_g, col_g)
            col += 1

        lay_estac.addLayout(grid_estac)
        lay.addWidget(card_estac)


# ══════════════════════════════════════════════════════════
#  PÁGINA: USUÁRIOS
# ══════════════════════════════════════════════════════════

class PaginaUsuarios(QWidget):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(30, 24, 30, 24)
        lay.setSpacing(16)

        # Título + botão
        topo = QHBoxLayout()
        topo.addWidget(label_titulo("Cadastro de Usuários"))
        topo.addStretch()
        btn_novo = btn_primario("  +  Novo Usuário")
        btn_novo.clicked.connect(self._abrir_cadastro)
        topo.addWidget(btn_novo)
        lay.addLayout(topo)

        # Cards de resumo
        usuarios = get_usuarios()
        total   = len(usuarios)
        ativos  = sum(1 for u in usuarios if u.get("status") == "Ativo")
        pendentes = sum(1 for u in usuarios if u.get("status") == "Pendente")
        bloqueados = sum(1 for u in usuarios if u.get("status") == "Bloqueado")

        grid = QGridLayout()
        grid.setSpacing(12)
        for i, (tit, val, cor) in enumerate([
            ("Total", total, CORES['azul']),
            ("Ativos", ativos, CORES['verde']),
            ("Pendentes", pendentes, CORES['amarelo']),
            ("Bloqueados", bloqueados, CORES['vermelho']),
        ]):
            grid.addWidget(CardEstat(tit, val, cor=cor), 0, i)
        lay.addLayout(grid)

        # Filtros
        filtros = QHBoxLayout()
        filtros.setSpacing(10)
        self.busca = QLineEdit()
        self.busca.setPlaceholderText("🔍  Buscar por nome, CPF ou e-mail...")
        self.busca.setFixedHeight(40)
        self.busca.textChanged.connect(self._filtrar)
        filtros.addWidget(self.busca, 3)

        self.combo_status = QComboBox()
        self.combo_status.setFixedHeight(40)
        self.combo_status.addItems(["Todos os status", "Ativo", "Pendente", "Inativo", "Bloqueado"])
        self.combo_status.currentTextChanged.connect(self._filtrar)
        filtros.addWidget(self.combo_status)

        self.combo_perfil = QComboBox()
        self.combo_perfil.setFixedHeight(40)
        self.combo_perfil.addItems(["Todos os perfis", "Administrador", "Funcionário Shopping",
                                     "Funcionário Loja", "Lojista (Dono)", "Visitante",
                                     "Cliente VIP", "Contratado", "Segurança", "Operador"])
        self.combo_perfil.currentTextChanged.connect(self._filtrar)
        filtros.addWidget(self.combo_perfil)

        self.combo_shop = QComboBox()
        self.combo_shop.setFixedHeight(40)
        self.combo_shop.addItems(["Todos os shoppings", "Shopping 1", "Shopping 2",
                                   "Shopping 3", "Shopping 4", "Todos"])
        self.combo_shop.currentTextChanged.connect(self._filtrar)
        filtros.addWidget(self.combo_shop)
        lay.addLayout(filtros)

        # Tabela
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(8)
        self.tabela.setHorizontalHeaderLabels(["ID", "Nome", "Perfil", "Status", "E-mail", "Shopping", "Faixa Etária", "Ações"])
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabela.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabela.setMinimumHeight(380)
        lay.addWidget(self.tabela)

        self._carregar_tabela()

        # Rodapé
        self.lbl_count = QLabel()
        self.lbl_count.setStyleSheet(f"color: {CORES['texto_muted']}; font-size: 12px;")
        lay.addWidget(self.lbl_count)
        self._atualizar_count()

    def _carregar_tabela(self, usuarios=None):
        if usuarios is None:
            usuarios = get_usuarios()
        status_cores = {
            "Ativo": CORES['verde'], "Pendente": CORES['amarelo'],
            "Inativo": CORES['texto_sec'], "Bloqueado": CORES['vermelho'],
            "Suspenso": CORES['roxo'],
        }
        self.tabela.setRowCount(len(usuarios))
        for row, u in enumerate(usuarios):
            self.tabela.setItem(row, 0, QTableWidgetItem(u.get("id", "")))
            self.tabela.setItem(row, 1, QTableWidgetItem(u.get("nome", "")))
            self.tabela.setItem(row, 2, QTableWidgetItem(u.get("perfil", "")))
            status = u.get("status", "")
            item_s = QTableWidgetItem(f"  {status}  ")
            item_s.setForeground(QColor(status_cores.get(status, CORES['texto_sec'])))
            self.tabela.setItem(row, 3, item_s)
            self.tabela.setItem(row, 4, QTableWidgetItem(u.get("email", "")))
            self.tabela.setItem(row, 5, QTableWidgetItem(u.get("shopping_principal", "")))
            self.tabela.setItem(row, 6, QTableWidgetItem(u.get("faixa_etaria", "")))

            # Botão ver detalhes
            btn_ver = QPushButton("Ver")
            btn_ver.setStyleSheet(f"""
                QPushButton {{
                    background-color: {CORES['azul']}22;
                    color: {CORES['azul_claro']};
                    border: 1px solid {CORES['azul']}44;
                    border-radius: 5px;
                    padding: 4px 12px;
                    font-size: 11px;
                }}
                QPushButton:hover {{ background-color: {CORES['azul']}44; }}
            """)
            usuario_ref = u
            btn_ver.clicked.connect(lambda _, usr=usuario_ref: self._ver_usuario(usr))
            self.tabela.setCellWidget(row, 7, btn_ver)
            self.tabela.setRowHeight(row, 38)

    def _filtrar(self):
        busca = self.busca.text().lower()
        status = self.combo_status.currentText()
        perfil = self.combo_perfil.currentText()
        shop   = self.combo_shop.currentText()

        usuarios = get_usuarios()
        if busca:
            usuarios = [u for u in usuarios if
                       busca in u.get("nome", "").lower() or
                       busca in u.get("cpf", "").lower() or
                       busca in u.get("email", "").lower()]
        if status != "Todos os status":
            usuarios = [u for u in usuarios if u.get("status") == status]
        if perfil != "Todos os perfis":
            usuarios = [u for u in usuarios if u.get("perfil") == perfil]
        if shop != "Todos os shoppings":
            usuarios = [u for u in usuarios if u.get("shopping_principal") == shop]

        self._carregar_tabela(usuarios)
        self._atualizar_count(len(usuarios))

    def _atualizar_count(self, n=None):
        total = len(get_usuarios())
        n = n if n is not None else total
        self.lbl_count.setText(f"Exibindo {n} de {total} usuários")

    def _abrir_cadastro(self):
        dlg = DialogCadastroUsuario(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._carregar_tabela()
            self._atualizar_count()

    def _ver_usuario(self, usuario):
        dlg = DialogVerUsuario(usuario, self)
        dlg.exec()


class DialogVerUsuario(QDialog):
    def __init__(self, usuario, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Usuário — {usuario.get('nome', '')}")
        self.setFixedSize(500, 580)
        self.setStyleSheet(f"background-color: {CORES['bg_card']}; border-radius: 12px;")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(30, 30, 30, 20)
        lay.setSpacing(14)

        # Cabeçalho
        topo = QHBoxLayout()
        avatar = QLabel("👤")
        avatar.setFixedSize(52, 52)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {CORES['azul']}, stop:1 {CORES['roxo']});
            border-radius: 26px;
            font-size: 24px;
        """)
        topo.addWidget(avatar)
        topo.addSpacing(12)
        info_topo = QVBoxLayout()
        nome_l = QLabel(usuario.get("nome", ""))
        nome_l.setStyleSheet(f"color: {CORES['texto_principal']}; font-size: 17px; font-weight: 700;")
        info_topo.addWidget(nome_l)
        perfil_l = QLabel(f"{usuario.get('perfil', '')}  ·  {usuario.get('shopping_principal', '')}")
        perfil_l.setStyleSheet(f"color: {CORES['texto_sec']}; font-size: 12px;")
        info_topo.addWidget(perfil_l)
        topo.addLayout(info_topo)
        topo.addStretch()
        status = usuario.get("status", "")
        cores_s = {"Ativo": CORES['verde'], "Pendente": CORES['amarelo'],
                   "Bloqueado": CORES['vermelho'], "Inativo": CORES['texto_sec']}
        lay.addLayout(topo)
        lay.addWidget(badge(status, cores_s.get(status, CORES['texto_sec'])))
        lay.addWidget(separador())

        # Campos
        campos = [
            ("ID do Sistema", usuario.get("id", "")),
            ("CPF", usuario.get("cpf", "")),
            ("E-mail", usuario.get("email", "")),
            ("Telefone", usuario.get("telefone", "")),
            ("Nível de Acesso", usuario.get("nivel_acesso_descricao", "")),
            ("Idade", f"{usuario.get('idade', '?')} anos  ({usuario.get('faixa_etaria', '')})"),
            ("Placa do Veículo", usuario.get("placa_veiculo", "Não informada")),
            ("Loja / Cargo", f"{usuario.get('nome_loja', '')}  {usuario.get('cargo', '')}".strip() or "—"),
            ("Cadastrado em", usuario.get("criado_em", "")[:10]),
            ("Última atualização", usuario.get("atualizado_em", "")[:10]),
        ]
        for label, valor in campos:
            linha = QHBoxLayout()
            lbl = QLabel(f"{label}:")
            lbl.setFixedWidth(160)
            lbl.setStyleSheet(f"color: {CORES['texto_sec']}; font-size: 12px;")
            val = QLabel(str(valor) if valor else "—")
            val.setStyleSheet(f"color: {CORES['texto_principal']}; font-size: 13px;")
            val.setWordWrap(True)
            linha.addWidget(lbl)
            linha.addWidget(val)
            lay.addLayout(linha)

        lay.addStretch()
        btn_fechar = btn_secundario("Fechar")
        btn_fechar.clicked.connect(self.reject)
        lay.addWidget(btn_fechar)


class DialogCadastroUsuario(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Novo Usuário")
        self.setFixedSize(520, 640)
        self.setStyleSheet(f"background-color: {CORES['bg_card']};")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(30, 30, 30, 24)
        lay.setSpacing(14)

        tit = QLabel("👤  Novo Cadastro de Usuário")
        tit.setStyleSheet(f"color: {CORES['texto_principal']}; font-size: 17px; font-weight: 700;")
        lay.addWidget(tit)
        lay.addWidget(separador())

        grid = QGridLayout()
        grid.setSpacing(12)

        self.campos = {}

        def add_campo(label, chave, row, col, placeholder="", password=False, span=1):
            lbl = QLabel(label)
            lbl.setStyleSheet(f"color: {CORES['texto_sec']}; font-size: 12px; font-weight: 600;")
            campo = QLineEdit()
            campo.setPlaceholderText(placeholder)
            campo.setFixedHeight(40)
            if password:
                campo.setEchoMode(QLineEdit.EchoMode.Password)
            self.campos[chave] = campo
            grid.addWidget(lbl, row * 2, col, 1, span)
            grid.addWidget(campo, row * 2 + 1, col, 1, span)

        def add_combo(label, chave, opcoes, row, col):
            lbl = QLabel(label)
            lbl.setStyleSheet(f"color: {CORES['texto_sec']}; font-size: 12px; font-weight: 600;")
            combo = QComboBox()
            combo.setFixedHeight(40)
            combo.addItems(opcoes)
            self.campos[chave] = combo
            grid.addWidget(lbl, row * 2, col)
            grid.addWidget(combo, row * 2 + 1, col)

        add_campo("Nome completo", "nome", 0, 0, "Ex: Maria da Silva", span=2)
        add_campo("CPF", "cpf", 1, 0, "000.000.000-00")
        add_campo("E-mail", "email", 1, 1, "email@exemplo.com")
        add_campo("Telefone", "telefone", 2, 0, "(11) 99999-0000")
        add_campo("Senha", "senha", 2, 1, "••••••••", password=True)
        add_combo("Perfil", "perfil", [
            "Visitante", "Funcionário Loja", "Lojista (Dono)",
            "Funcionário Shopping", "Cliente VIP", "Contratado",
            "Entregador", "Segurança", "Operador", "Administrador"
        ], 3, 0)
        add_combo("Shopping", "shopping", [
            "Shopping 1", "Shopping 2", "Shopping 3", "Shopping 4", "Todos"
        ], 3, 1)
        add_combo("Nível de Acesso", "nivel", [
            "Nível 1 - Áreas Comuns",
            "Nível 2 - Áreas Restritas",
            "Nível 3 - Acesso Total",
        ], 4, 0)
        add_campo("Idade", "idade", 4, 1, "Ex: 25")
        add_campo("Placa do Veículo", "placa", 5, 0, "ABC-1234 (opcional)")
        add_campo("Loja / Cargo", "loja_cargo", 5, 1, "Ex: Nike — Vendedor")

        lay.addLayout(grid)
        lay.addStretch()

        btns = QHBoxLayout()
        btn_cancel = btn_secundario("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btn_salvar = btn_primario("💾  Salvar Cadastro")
        btn_salvar.clicked.connect(self._salvar)
        btns.addWidget(btn_cancel)
        btns.addStretch()
        btns.addWidget(btn_salvar)
        lay.addLayout(btns)

    def _salvar(self):
        nome  = self.campos["nome"].text().strip()
        cpf   = self.campos["cpf"].text().strip()
        email = self.campos["email"].text().strip()
        senha = self.campos["senha"].text().strip()

        if not nome or not cpf or not email or not senha:
            QMessageBox.warning(self, "Atenção", "Preencha pelo menos: Nome, CPF, E-mail e Senha.")
            return

        dados = _ler_json("usuarios.json")
        if not dados:
            dados = {"metadados": {"total_usuarios": 0}, "usuarios": []}

        for u in dados["usuarios"]:
            if u.get("cpf", "").replace(".", "").replace("-", "") == cpf.replace(".", "").replace("-", ""):
                QMessageBox.warning(self, "CPF já cadastrado", f"O CPF {cpf} já está no sistema.")
                return

        import uuid
        nivel_map = {
            "Nível 1 - Áreas Comuns": 1,
            "Nível 2 - Áreas Restritas": 2,
            "Nível 3 - Acesso Total": 3,
        }
        nivel_texto = self.campos["nivel"].currentText()
        nivel_num = nivel_map.get(nivel_texto, 1)
        idade_str = self.campos["idade"].text().strip()
        idade = int(idade_str) if idade_str.isdigit() else None

        def faixa(i):
            if not i: return "Não informado"
            if i <= 12: return "Criança"
            if i <= 17: return "Adolescente"
            if i <= 29: return "Jovem Adulto"
            if i <= 59: return "Adulto"
            return "Idoso"

        novo = {
            "id": str(uuid.uuid4())[:8].upper(),
            "nome": nome, "cpf": cpf, "email": email,
            "telefone": self.campos["telefone"].text().strip(),
            "senha": senha,
            "perfil": self.campos["perfil"].currentText(),
            "nivel_acesso": nivel_num,
            "nivel_acesso_descricao": nivel_texto,
            "status": "Pendente",
            "idade": idade,
            "faixa_etaria": faixa(idade),
            "nome_loja": None, "cargo": None,
            "shopping_principal": self.campos["shopping"].currentText(),
            "shoppings_acesso": [self.campos["shopping"].currentText()],
            "placa_veiculo": self.campos["placa"].text().strip() or None,
            "historico_visitas": [], "lojas_frequentadas": [],
            "tempo_medio_permanencia": 0, "horario_preferido": None,
            "frequencia_visitas": 0, "ultima_visita": None,
            "preferencias": {"categorias_lojas": [], "forma_pagamento": None, "grupo_social": None},
            "criado_em": datetime.now().isoformat(),
            "atualizado_em": datetime.now().isoformat(),
            "criado_por": "dashboard",
            "observacoes": "",
        }

        dados["usuarios"].append(novo)
        dados["metadados"]["total_usuarios"] = len(dados["usuarios"])
        _salvar_json("usuarios.json", dados)

        QMessageBox.information(self, "Sucesso", f"Usuário '{nome}' cadastrado com sucesso!\nID: {novo['id']}")
        self.accept()


# ══════════════════════════════════════════════════════════
#  PÁGINA: MONITORAMENTO
# ══════════════════════════════════════════════════════════

class PaginaMonitoramento(QWidget):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(30, 24, 30, 24)
        lay.setSpacing(16)

        lay.addWidget(label_titulo("Monitoramento em Tempo Real"))

        # Tabs manuais
        tabs = QHBoxLayout()
        self.btn_predios = QPushButton("🏢  Prédios / Internos")
        self.btn_estac   = QPushButton("🚗  Estacionamento")
        for btn in [self.btn_predios, self.btn_estac]:
            btn.setFixedHeight(38)
            btn.setCheckable(True)
            tabs.addWidget(btn)
        tabs.addStretch()
        self.btn_predios.setChecked(True)
        self.btn_predios.clicked.connect(lambda: self._trocar_tab(0))
        self.btn_estac.clicked.connect(lambda: self._trocar_tab(1))
        self._estilo_tab_btn()
        lay.addLayout(tabs)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._tab_predios())
        self.stack.addWidget(self._tab_estac())
        lay.addWidget(self.stack)

    def _estilo_tab_btn(self):
        for i, btn in enumerate([self.btn_predios, self.btn_estac]):
            ativo = btn.isChecked()
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {'%s22' % CORES['azul'] if ativo else 'transparent'};
                    color: {CORES['azul_claro'] if ativo else CORES['texto_sec']};
                    border: 1px solid {'%s44' % CORES['azul'] if ativo else CORES['borda']};
                    border-radius: 8px;
                    padding: 8px 18px;
                    font-size: 13px;
                    font-weight: {'600' if ativo else '400'};
                }}
                QPushButton:hover {{ background-color: {CORES['bg_hover']}; }}
            """)

    def _trocar_tab(self, idx):
        self.stack.setCurrentIndex(idx)
        self.btn_predios.setChecked(idx == 0)
        self.btn_estac.setChecked(idx == 1)
        self._estilo_tab_btn()

    def _tab_predios(self):
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)

        eventos = get_eventos_predios()
        alertas = [a for a in get_alertas_predios() if not a.get("resolvido")]

        # Cards rápidos
        grid = QGridLayout()
        grid.setSpacing(12)
        grid.addWidget(CardEstat("Total de Eventos", len(eventos), cor=CORES['azul'], icone="📊"), 0, 0)
        criticos = sum(1 for e in eventos if e.get("nivel_alerta") == "critico")
        grid.addWidget(CardEstat("Eventos Críticos", criticos, cor=CORES['vermelho'], icone="🚨"), 0, 1)
        atencao = sum(1 for e in eventos if e.get("nivel_alerta") == "atencao")
        grid.addWidget(CardEstat("Em Atenção", atencao, cor=CORES['amarelo'], icone="⚠️"), 0, 2)
        grid.addWidget(CardEstat("Alertas Ativos", len(alertas), cor=CORES['roxo'], icone="🔔"), 0, 3)
        lay.addLayout(grid)

        # Tabela de eventos
        card = card_frame()
        lay_card = QVBoxLayout(card)
        lay_card.setContentsMargins(16, 14, 16, 14)
        topo_t = QHBoxLayout()
        topo_t.addWidget(label_titulo("Eventos Recentes", 15))
        topo_t.addStretch()
        b = badge("AO VIVO", CORES['verde'])
        topo_t.addWidget(b)
        lay_card.addLayout(topo_t)
        lay_card.addWidget(separador())

        tabela = QTableWidget()
        tabela.setColumnCount(6)
        tabela.setHorizontalHeaderLabels(["Data/Hora", "Tipo", "Nível", "Ambiente", "Shopping", "Usuário"])
        tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        tabela.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        tabela.verticalHeader().setVisible(False)
        tabela.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        recentes = list(reversed(eventos))[:30]
        tabela.setRowCount(len(recentes))
        nivel_cores = {"info": CORES['azul'], "atencao": CORES['amarelo'], "critico": CORES['vermelho']}
        for row, e in enumerate(recentes):
            tabela.setItem(row, 0, QTableWidgetItem(e.get("data_hora", "")[:16].replace("T", " ")))
            tabela.setItem(row, 1, QTableWidgetItem(e.get("tipo", "").replace("_", " ")))
            nivel = e.get("nivel_alerta", "info")
            item_n = QTableWidgetItem(f"  {nivel.upper()}  ")
            item_n.setForeground(QColor(nivel_cores.get(nivel, CORES['texto_sec'])))
            tabela.setItem(row, 2, item_n)
            tabela.setItem(row, 3, QTableWidgetItem(e.get("nome_ambiente", "")))
            tabela.setItem(row, 4, QTableWidgetItem(e.get("shopping", "")))
            tabela.setItem(row, 5, QTableWidgetItem(e.get("nome_usuario", "—") or "—"))
            tabela.setRowHeight(row, 36)

        lay_card.addWidget(tabela)
        lay.addWidget(card)
        return w

    def _tab_estac(self):
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)

        veiculos = get_veiculos_ativos()
        alertas  = [a for a in get_alertas_estac() if not a.get("resolvido")]
        vagas    = get_vagas()
        total_vagas   = sum(v.get("total", 0) for v in vagas.values())
        ocupadas_vagas = sum(v.get("ocupadas", 0) for v in vagas.values())

        grid = QGridLayout()
        grid.setSpacing(12)
        grid.addWidget(CardEstat("Veículos Dentro", len(veiculos), "agora", CORES['azul'], "🚗"), 0, 0)
        grid.addWidget(CardEstat("Vagas Ocupadas", ocupadas_vagas, f"de {total_vagas}", CORES['amarelo'], "🅿️"), 0, 1)
        grid.addWidget(CardEstat("Vagas Livres", total_vagas - ocupadas_vagas, "disponíveis", CORES['verde'], "✅"), 0, 2)
        grid.addWidget(CardEstat("Alertas", len(alertas), "no estac.", CORES['vermelho'] if alertas else CORES['verde'], "🚨"), 0, 3)
        lay.addLayout(grid)

        # Veículos ativos
        card = card_frame()
        lay_card = QVBoxLayout(card)
        lay_card.setContentsMargins(16, 14, 16, 14)
        lay_card.addWidget(label_titulo("Veículos no Estacionamento Agora", 15))
        lay_card.addWidget(separador())

        tabela = QTableWidget()
        tabela.setColumnCount(6)
        tabela.setHorizontalHeaderLabels(["Placa", "Modelo", "Shopping", "Setor", "Vaga", "Entrada"])
        tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        tabela.verticalHeader().setVisible(False)
        tabela.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        tabela.setRowCount(len(veiculos))
        for row, (placa, v) in enumerate(veiculos.items()):
            tabela.setItem(row, 0, QTableWidgetItem(placa))
            tabela.setItem(row, 1, QTableWidgetItem(v.get("modelo", "—") or "—"))
            tabela.setItem(row, 2, QTableWidgetItem(v.get("shopping", "")))
            tabela.setItem(row, 3, QTableWidgetItem(v.get("setor", "")))
            tabela.setItem(row, 4, QTableWidgetItem(v.get("numero_vaga", "—") or "—"))
            entrada = v.get("entrada_em", "")[:16].replace("T", " ")
            tabela.setItem(row, 5, QTableWidgetItem(entrada))
            tabela.setRowHeight(row, 36)

        lay_card.addWidget(tabela)
        lay.addWidget(card)
        return w


# ══════════════════════════════════════════════════════════
#  PÁGINA: AMBIENTES
# ══════════════════════════════════════════════════════════

class PaginaAmbientes(QWidget):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(30, 24, 30, 24)
        lay.setSpacing(16)

        lay.addWidget(label_titulo("Ambientes dos Shoppings"))

        ambientes = get_ambientes()

        # Cards
        grid = QGridLayout()
        grid.setSpacing(12)
        total   = len(ambientes)
        ativos  = sum(1 for a in ambientes if a.get("status") == "Ativo")
        cameras = sum(a.get("quantidade_cameras", 0) for a in ambientes)
        sensores = sum(1 for a in ambientes if a.get("tem_sensor_presenca"))
        for i, (tit, val, cor, ico) in enumerate([
            ("Total de Ambientes", total, CORES['azul'], "🏢"),
            ("Ativos", ativos, CORES['verde'], "✅"),
            ("Câmeras Instaladas", cameras, CORES['amarelo'], "📷"),
            ("Com Sensor de Presença", sensores, CORES['roxo'], "📡"),
        ]):
            grid.addWidget(CardEstat(tit, val, cor=cor, icone=ico), 0, i)
        lay.addLayout(grid)

        # Filtros
        filtros = QHBoxLayout()
        filtros.setSpacing(10)
        self.busca_amb = QLineEdit()
        self.busca_amb.setPlaceholderText("🔍  Buscar ambiente...")
        self.busca_amb.setFixedHeight(40)
        self.busca_amb.textChanged.connect(self._filtrar_amb)
        filtros.addWidget(self.busca_amb, 2)

        self.combo_shop_amb = QComboBox()
        self.combo_shop_amb.setFixedHeight(40)
        self.combo_shop_amb.addItems(["Todos", "Shopping 1", "Shopping 2", "Shopping 3", "Shopping 4"])
        self.combo_shop_amb.currentTextChanged.connect(self._filtrar_amb)
        filtros.addWidget(self.combo_shop_amb)

        self.combo_cat_amb = QComboBox()
        self.combo_cat_amb.setFixedHeight(40)
        cats = ["Todas as categorias"] + sorted(list(set(a.get("categoria", "") for a in ambientes)))
        self.combo_cat_amb.addItems(cats)
        self.combo_cat_amb.currentTextChanged.connect(self._filtrar_amb)
        filtros.addWidget(self.combo_cat_amb, 2)
        lay.addLayout(filtros)

        # Tabela
        self.tabela_amb = QTableWidget()
        self.tabela_amb.setColumnCount(7)
        self.tabela_amb.setHorizontalHeaderLabels(["ID", "Nome", "Categoria", "Shopping", "Piso", "Ala", "Status"])
        self.tabela_amb.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabela_amb.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tabela_amb.verticalHeader().setVisible(False)
        self.tabela_amb.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabela_amb.setMinimumHeight(400)
        lay.addWidget(self.tabela_amb)

        self.lbl_count_amb = QLabel()
        self.lbl_count_amb.setStyleSheet(f"color: {CORES['texto_muted']}; font-size: 12px;")
        lay.addWidget(self.lbl_count_amb)

        self._carregar_tabela_amb()

    def _carregar_tabela_amb(self, ambientes=None):
        if ambientes is None:
            ambientes = get_ambientes()
        status_cores = {
            "Ativo": CORES['verde'], "Inativo": CORES['texto_sec'],
            "Em Reforma": CORES['amarelo'], "Desativado": CORES['vermelho'],
        }
        self.tabela_amb.setRowCount(len(ambientes))
        for row, a in enumerate(ambientes):
            self.tabela_amb.setItem(row, 0, QTableWidgetItem(a.get("id", "")))
            self.tabela_amb.setItem(row, 1, QTableWidgetItem(a.get("nome", "")))
            self.tabela_amb.setItem(row, 2, QTableWidgetItem(a.get("categoria", "")))
            self.tabela_amb.setItem(row, 3, QTableWidgetItem(a.get("shopping", "")))
            self.tabela_amb.setItem(row, 4, QTableWidgetItem(a.get("piso", "")))
            self.tabela_amb.setItem(row, 5, QTableWidgetItem(a.get("ala", "") or "—"))
            status = a.get("status", "Ativo")
            item_s = QTableWidgetItem(f"  {status}  ")
            item_s.setForeground(QColor(status_cores.get(status, CORES['texto_sec'])))
            self.tabela_amb.setItem(row, 6, item_s)
            self.tabela_amb.setRowHeight(row, 36)
        self.lbl_count_amb.setText(f"Exibindo {len(ambientes)} de {len(get_ambientes())} ambientes")

    def _filtrar_amb(self):
        busca = self.busca_amb.text().lower()
        shop  = self.combo_shop_amb.currentText()
        cat   = self.combo_cat_amb.currentText()
        ams   = get_ambientes()
        if busca:
            ams = [a for a in ams if busca in a.get("nome", "").lower()]
        if shop != "Todos":
            ams = [a for a in ams if a.get("shopping") == shop]
        if cat != "Todas as categorias":
            ams = [a for a in ams if a.get("categoria") == cat]
        self._carregar_tabela_amb(ams)


# ══════════════════════════════════════════════════════════
#  PÁGINA: AUDITORIA
# ══════════════════════════════════════════════════════════

class PaginaAuditoria(QWidget):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(30, 24, 30, 24)
        lay.setSpacing(16)

        lay.addWidget(label_titulo("Registros de Auditoria"))

        registros = get_registros()

        grid = QGridLayout()
        grid.setSpacing(12)
        total  = len(registros)
        criticos = sum(1 for r in registros if r.get("nivel") == "critico")
        hoje_r = datetime.now().strftime("%Y-%m-%d")
        hoje_c = sum(1 for r in registros if r.get("data_hora", "")[:10] == hoje_r)
        for i, (tit, val, cor, ico) in enumerate([
            ("Total de Registros", total, CORES['azul'], "📋"),
            ("Hoje", hoje_c, CORES['verde'], "📅"),
            ("Críticos", criticos, CORES['vermelho'], "🚨"),
            ("Módulos Monitorados", 6, CORES['roxo'], "🧩"),
        ]):
            grid.addWidget(CardEstat(tit, val, cor=cor, icone=ico), 0, i)
        lay.addLayout(grid)

        # Filtros
        filtros = QHBoxLayout()
        filtros.setSpacing(10)
        self.busca_reg = QLineEdit()
        self.busca_reg.setPlaceholderText("🔍  Buscar nos registros...")
        self.busca_reg.setFixedHeight(40)
        self.busca_reg.textChanged.connect(self._filtrar_reg)
        filtros.addWidget(self.busca_reg, 3)

        self.combo_nivel_reg = QComboBox()
        self.combo_nivel_reg.setFixedHeight(40)
        self.combo_nivel_reg.addItems(["Todos os níveis", "info", "aviso", "critico"])
        self.combo_nivel_reg.currentTextChanged.connect(self._filtrar_reg)
        filtros.addWidget(self.combo_nivel_reg)
        lay.addLayout(filtros)

        # Tabela
        self.tabela_reg = QTableWidget()
        self.tabela_reg.setColumnCount(6)
        self.tabela_reg.setHorizontalHeaderLabels(["Data/Hora", "Ação", "Nível", "Usuário", "Shopping", "Resultado"])
        self.tabela_reg.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabela_reg.verticalHeader().setVisible(False)
        self.tabela_reg.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabela_reg.setMinimumHeight(400)
        lay.addWidget(self.tabela_reg)

        self.lbl_count_reg = QLabel()
        self.lbl_count_reg.setStyleSheet(f"color: {CORES['texto_muted']}; font-size: 12px;")
        lay.addWidget(self.lbl_count_reg)

        self._carregar_tabela_reg()

    def _carregar_tabela_reg(self, registros=None):
        if registros is None:
            registros = get_registros()
        recentes = list(reversed(registros))[:100]
        nivel_cores = {"info": CORES['azul'], "aviso": CORES['amarelo'], "critico": CORES['vermelho']}
        self.tabela_reg.setRowCount(len(recentes))
        for row, r in enumerate(recentes):
            self.tabela_reg.setItem(row, 0, QTableWidgetItem(r.get("data_hora", "")[:16].replace("T", " ")))
            self.tabela_reg.setItem(row, 1, QTableWidgetItem(r.get("tipo_acao", r.get("acao", "")).replace("_", " ")))
            nivel = r.get("nivel", "info")
            item_n = QTableWidgetItem(f"  {nivel.upper()}  ")
            item_n.setForeground(QColor(nivel_cores.get(nivel, CORES['texto_sec'])))
            self.tabela_reg.setItem(row, 2, item_n)
            self.tabela_reg.setItem(row, 3, QTableWidgetItem(r.get("usuario", r.get("realizado_por", "")) or "sistema"))
            self.tabela_reg.setItem(row, 4, QTableWidgetItem(r.get("shopping", "") or "—"))
            resultado = r.get("resultado", "sucesso")
            item_res = QTableWidgetItem(resultado)
            item_res.setForeground(QColor(CORES['verde'] if resultado == "sucesso" else CORES['vermelho']))
            self.tabela_reg.setItem(row, 5, item_res)
            self.tabela_reg.setRowHeight(row, 36)
        self.lbl_count_reg.setText(f"Exibindo {len(recentes)} registros")

    def _filtrar_reg(self):
        busca = self.busca_reg.text().lower()
        nivel = self.combo_nivel_reg.currentText()
        regs  = get_registros()
        if busca:
            regs = [r for r in regs if
                   busca in r.get("tipo_acao", r.get("acao", "")).lower() or
                   busca in r.get("usuario", r.get("realizado_por", "")).lower()]
        if nivel != "Todos os níveis":
            regs = [r for r in regs if r.get("nivel") == nivel]
        self._carregar_tabela_reg(regs)


# ══════════════════════════════════════════════════════════
#  JANELA PRINCIPAL
# ══════════════════════════════════════════════════════════

class JanelaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ShopControl — Painel de Controle de Acesso")
        self.setMinimumSize(1280, 780)
        self.resize(1440, 860)
        self.setStyleSheet(ESTILO_GLOBAL)
        self._build()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._atualizar_hora)
        self._timer.start(60000)

    def _build(self):
        central = QWidget()
        central.setStyleSheet(f"background-color: {CORES['bg_escuro']};")
        self.setCentralWidget(central)
        lay_main = QHBoxLayout(central)
        lay_main.setContentsMargins(0, 0, 0, 0)
        lay_main.setSpacing(0)

        # ── SIDEBAR ──
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {CORES['bg_sidebar']};
                border-right: 1px solid {CORES['borda']};
            }}
        """)
        lay_side = QVBoxLayout(sidebar)
        lay_side.setContentsMargins(0, 0, 0, 0)
        lay_side.setSpacing(0)

        # Logo no sidebar
        logo_area = QFrame()
        logo_area.setFixedHeight(72)
        logo_area.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {CORES['azul_glow']}, stop:1 transparent);
            border-bottom: 1px solid {CORES['borda']};
        """)
        logo_lay = QHBoxLayout(logo_area)
        logo_lay.setContentsMargins(18, 0, 18, 0)
        ico = QLabel("🏬")
        ico.setStyleSheet("font-size: 24px;")
        logo_lay.addWidget(ico)
        nome_app = QLabel("ShopControl")
        nome_app.setStyleSheet(f"""
            color: white;
            font-size: 16px;
            font-weight: 700;
            letter-spacing: -0.3px;
        """)
        logo_lay.addWidget(nome_app)
        logo_lay.addStretch()
        lay_side.addWidget(logo_area)
        lay_side.addSpacing(8)

        # Itens do menu
        menus = [
            ("Painel Geral",      "📊", 0),
            ("Usuários",          "👥", 1),
            ("Ambientes",         "🏢", 2),
            ("Monitoramento",     "📷", 3),
            ("Auditoria",         "📋", 4),
        ]
        self.itens_menu = []
        for texto, icone, pagina in menus:
            item = ItemMenu(texto, icone, pagina)
            item.clicked.connect(lambda _, p=pagina, i=item: self._navegar(p, i))
            lay_side.addWidget(item)
            self.itens_menu.append(item)

        self.itens_menu[0].set_ativo(True)

        lay_side.addStretch()

        # Separador
        lay_side.addWidget(separador())

        # Usuário logado
        user_area = QFrame()
        user_area.setFixedHeight(70)
        user_area.setStyleSheet("background: transparent;")
        user_lay = QHBoxLayout(user_area)
        user_lay.setContentsMargins(16, 10, 16, 10)
        avatar = QLabel("A")
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {CORES['azul']}, stop:1 {CORES['roxo']});
            color: white;
            font-size: 14px;
            font-weight: 700;
            border-radius: 18px;
        """)
        user_lay.addWidget(avatar)
        user_lay.addSpacing(8)
        user_info = QVBoxLayout()
        lbl_nome = QLabel("Admin")
        lbl_nome.setStyleSheet(f"color: {CORES['texto_principal']}; font-size: 13px; font-weight: 600;")
        lbl_cargo = QLabel("Administrador")
        lbl_cargo.setStyleSheet(f"color: {CORES['texto_muted']}; font-size: 11px;")
        user_info.addWidget(lbl_nome)
        user_info.addWidget(lbl_cargo)
        user_lay.addLayout(user_info)
        lay_side.addWidget(user_area)
        lay_main.addWidget(sidebar)

        # ── CONTEÚDO PRINCIPAL ──
        conteudo = QFrame()
        conteudo.setStyleSheet(f"background-color: {CORES['bg_escuro']};")
        lay_cont = QVBoxLayout(conteudo)
        lay_cont.setContentsMargins(0, 0, 0, 0)
        lay_cont.setSpacing(0)

        # Header
        header = QFrame()
        header.setFixedHeight(58)
        header.setStyleSheet(f"""
            background-color: {CORES['bg_sidebar']};
            border-bottom: 1px solid {CORES['borda']};
        """)
        lay_header = QHBoxLayout(header)
        lay_header.setContentsMargins(24, 0, 24, 0)

        self.lbl_pagina = QLabel("Painel Geral")
        self.lbl_pagina.setStyleSheet(f"color: {CORES['texto_principal']}; font-size: 15px; font-weight: 600;")
        lay_header.addWidget(self.lbl_pagina)
        lay_header.addStretch()

        # Alertas no header
        alertas_p = [a for a in get_alertas_predios() if not a.get("resolvido")]
        alertas_e = [a for a in get_alertas_estac() if not a.get("resolvido")]
        total_al  = len(alertas_p) + len(alertas_e)
        if total_al > 0:
            btn_alert = QPushButton(f"  🚨  {total_al} alerta(s)")
            btn_alert.setStyleSheet(f"""
                QPushButton {{
                    background-color: {CORES['vermelho']}22;
                    color: {CORES['vermelho_claro']};
                    border: 1px solid {CORES['vermelho']}44;
                    border-radius: 16px;
                    padding: 6px 16px;
                    font-size: 12px;
                    font-weight: 600;
                }}
            """)
            lay_header.addWidget(btn_alert)
            lay_header.addSpacing(12)

        self.lbl_hora_header = QLabel(datetime.now().strftime("%d/%m/%Y  %H:%M"))
        self.lbl_hora_header.setStyleSheet(f"color: {CORES['texto_sec']}; font-size: 12px;")
        lay_header.addWidget(self.lbl_hora_header)
        lay_cont.addWidget(header)

        # Stack de páginas
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"border: none; background: {CORES['bg_escuro']};")

        self.stack_paginas = QStackedWidget()
        self.stack_paginas.setStyleSheet(f"background: {CORES['bg_escuro']};")
        self.stack_paginas.addWidget(PaginaPainel())
        self.stack_paginas.addWidget(PaginaUsuarios())
        self.stack_paginas.addWidget(PaginaAmbientes())
        self.stack_paginas.addWidget(PaginaMonitoramento())
        self.stack_paginas.addWidget(PaginaAuditoria())

        scroll.setWidget(self.stack_paginas)
        lay_cont.addWidget(scroll)
        lay_main.addWidget(conteudo)

    def _navegar(self, pagina, item_clicado):
        for item in self.itens_menu:
            item.set_ativo(False)
        item_clicado.set_ativo(True)
        self.stack_paginas.setCurrentIndex(pagina)

        nomes = {0: "Painel Geral", 1: "Cadastro de Usuários",
                 2: "Ambientes dos Shoppings", 3: "Monitoramento em Tempo Real",
                 4: "Registros de Auditoria"}
        self.lbl_pagina.setText(nomes.get(pagina, ""))

    def _atualizar_hora(self):
        agora = datetime.now().strftime("%d/%m/%Y  %H:%M")
        self.lbl_hora_header.setText(agora)


# ══════════════════════════════════════════════════════════
#  PONTO DE ENTRADA
# ══════════════════════════════════════════════════════════

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("ShopControl")
    app.setOrganizationName("ShopControl Systems")

    # Tela de login
    login = TelaLogin()
    if login.exec() != QDialog.DialogCode.Accepted or not login.login_ok:
        sys.exit(0)

    # Dashboard principal
    janela = JanelaPrincipal()
    janela.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
