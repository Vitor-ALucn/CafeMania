import mysql.connector
from mysql.connector import Error
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
import json
import sys
import os

# Função para caminhos em ambiente empacotado
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class CafeteriaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("☕ Sistema Cafeteria - PDV & Produção")
        self.root.geometry("1400x800")
        self.root.state('zoomed')
        
        # Configurações iniciais
        self.usuario_logado = None
        self.cliente_selecionado = None
        self.carrinho = []
        self.total_venda = 0.0
        
        # Estilos
        self.setup_styles()
        
        # Painéis principais
        self.setup_main_panels()
        
        # Inicializar banco
        self.inicializar_banco()
        
        # Tela de login
        self.tela_login()

    def setup_styles(self):
        """Configura estilos da interface"""
        estilo = ttk.Style()
        estilo.theme_use('clam')
        estilo.configure('Titulo.TLabel', font=('Arial', 16, 'bold'), background='#2c3e50', foreground='white')
        estilo.configure('Card.TFrame', background='white', borderwidth=2, relief='groove')
        estilo.configure('BotaoVermelho.TButton', background='#e74c3c', foreground='white', font=('Arial', 10, 'bold'))
        estilo.configure('BotaoVerde.TButton', background='#27ae60', foreground='white', font=('Arial', 10, 'bold'))
        estilo.configure('BotaoAzul.TButton', background='#3498db', foreground='white', font=('Arial', 10, 'bold'))
        estilo.configure('Header.TLabel', font=('Arial', 12, 'bold'), background='#f8f9fa')

    def setup_main_panels(self):
        """Configura os painéis principais da aplicação"""
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Painel de Vendas (PDV) - 60%
        self.pdv_frame = ttk.Frame(self.main_paned, style='Card.TFrame')
        self.main_paned.add(self.pdv_frame, weight=6)
        
        # Painel de Produção - 40%
        self.producao_frame = ttk.Frame(self.main_paned, style='Card.TFrame')
        self.main_paned.add(self.producao_frame, weight=4)
        
        # Status bar
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_var = tk.StringVar(value="Aguardando login...")
        ttk.Label(self.status_bar, textvariable=self.status_var, font=('Arial', 9), foreground='#7f8c8d').pack(side=tk.LEFT)

    def tela_login(self):
        """Exibe a tela de login"""
        self.limpar_tela()
        
        login_frame = ttk.Frame(self.root)
        login_frame.pack(expand=True)
        
        ttk.Label(login_frame, text="LOGIN DO SISTEMA", style='Titulo.TLabel', padding=20).pack(fill=tk.X)
        
        form_frame = ttk.Frame(login_frame, padding=30)
        form_frame.pack()
        
        ttk.Label(form_frame, text="Usuário:", font=('Arial', 11)).grid(row=0, column=0, sticky=tk.W, pady=10)
        self.usuario_entry = ttk.Entry(form_frame, width=30, font=('Arial', 11))
        self.usuario_entry.grid(row=0, column=1, pady=10)
        
        ttk.Label(form_frame, text="Senha:", font=('Arial', 11)).grid(row=1, column=0, sticky=tk.W, pady=10)
        self.senha_entry = ttk.Entry(form_frame, width=30, font=('Arial', 11), show="*")
        self.senha_entry.grid(row=1, column=1, pady=10)
        
        btn_frame = ttk.Frame(login_frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Cancelar", command=self.root.quit).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Entrar", command=self.autenticar, style='BotaoVerde.TButton').pack(side=tk.LEFT, padx=10)
        
        self.usuario_entry.focus()

    def autenticar(self):
        """Autentica o usuário no sistema"""
        usuario = self.usuario_entry.get()
        senha = self.senha_entry.get()
        
        conexao = self.criar_conexao()
        if not conexao:
            return
        
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = "SELECT * FROM Usuario WHERE nomeUsuario = %s"
            cursor.execute(sql, (usuario,))
            usuario_data = cursor.fetchone()
            
            if usuario_data and usuario_data['senhaUsuario'] == senha:
                self.usuario_logado = usuario_data
                self.registrar_log("Login")
                self.atualizar_status()
                self.setup_interface_principal()
            else:
                messagebox.showerror("Erro", "Usuário ou senha incorretos!")
        except Error as e:
            messagebox.showerror("Erro", f"Erro ao autenticar: {e}")
        finally:
            cursor.close()
            conexao.close()

    def registrar_log(self, acao):
        """Registra ações no log do sistema"""
        if not self.usuario_logado:
            return
            
        conexao = self.criar_conexao()
        if not conexao:
            return
        
        cursor = conexao.cursor()
        try:
            sql = "INSERT INTO LogAcoes (idUsuario, acao) VALUES (%s, %s)"
            cursor.execute(sql, (self.usuario_logado['idUsuario'], acao))
            conexao.commit()
        except Error as e:
            print(f"Erro ao registrar log: {e}")
        finally:
            cursor.close()
            conexao.close()

    def atualizar_status(self):
        """Atualiza a barra de status com informações do usuário"""
        if self.usuario_logado:
            cargo = self.obter_cargo(self.usuario_logado['idCargo'])
            self.status_var.set(f"Usuário: {self.usuario_logado['nomeUsuario']} | Cargo: {cargo} | Sistema pronto")
        else:
            self.status_var.set("Aguardando login...")

    def obter_cargo(self, id_cargo):
        """Obtém o nome do cargo pelo ID"""
        conexao = self.criar_conexao()
        if not conexao:
            return "N/A"
        
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = "SELECT nomeCargo FROM CargoUsuario WHERE idCargo = %s"
            cursor.execute(sql, (id_cargo,))
            cargo = cursor.fetchone()
            return cargo['nomeCargo'] if cargo else "N/A"
        except Error:
            return "N/A"
        finally:
            cursor.close()
            conexao.close()

    def setup_interface_principal(self):
        """Configura a interface principal após login"""
        self.limpar_tela()
        
        # Configurar PDV
        self.setup_pdv()
        
        # Configurar Produção
        self.setup_producao()
        
        # Atualizar dados iniciais
        self.atualizar_produtos_pdv()
        self.atualizar_relatorio_producao()

    def limpar_tela(self):
        """Limpa a tela atual para exibir nova interface"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Recriar estrutura básica
        self.setup_main_panels()

    def inicializar_banco(self):
        """Cria todas as tabelas necessárias com base na estrutura fornecida"""
        conexao = self.criar_conexao()
        if not conexao:
            return False
        
        cursor = conexao.cursor()
        
        # Dicionário de tabelas com ordem de criação (respeitando dependências)
        tabelas = {
            "CargoUsuario": """
                CREATE TABLE IF NOT EXISTS CargoUsuario (
                    idCargo INT AUTO_INCREMENT PRIMARY KEY,
                    nomeCargo VARCHAR(50) NOT NULL,
                    getNome VARCHAR(50) NOT NULL
                )
            """,
            "Categoria": """
                CREATE TABLE IF NOT EXISTS Categoria (
                    idCategoria INT AUTO_INCREMENT PRIMARY KEY,
                    nomeCategoria VARCHAR(100) NOT NULL
                )
            """,
            "Fornecedor": """
                CREATE TABLE IF NOT EXISTS Fornecedor (
                    idFornecedor INT AUTO_INCREMENT PRIMARY KEY,
                    nomeFornecedor VARCHAR(100) NOT NULL,
                    cnpj VARCHAR(20) NOT NULL,
                    emailFornecedor VARCHAR(100),
                    telefone VARCHAR(20)
                )
            """,
            "Cliente": """
                CREATE TABLE IF NOT EXISTS Cliente (
                    idCliente INT AUTO_INCREMENT PRIMARY KEY,
                    nomeCliente VARCHAR(100) NOT NULL,
                    emailCliente VARCHAR(100),
                    enderecoCliente VARCHAR(255),
                    telefone VARCHAR(20),
                    totalPontos INT DEFAULT 0
                )
            """,
            "Usuario": """
                CREATE TABLE IF NOT EXISTS Usuario (
                    idUsuario INT AUTO_INCREMENT PRIMARY KEY,
                    nomeUsuario VARCHAR(100) NOT NULL,
                    cpfUsuario VARCHAR(20) NOT NULL,
                    email VARCHAR(100),
                    senhaUsuario VARCHAR(100) NOT NULL,
                    idCargo INT NOT NULL,
                    FOREIGN KEY (idCargo) REFERENCES CargoUsuario(idCargo)
                )
            """,
            "Produto": """
                CREATE TABLE IF NOT EXISTS Produto (
                    idProduto INT AUTO_INCREMENT PRIMARY KEY,
                    nomeProduto VARCHAR(100) NOT NULL,
                    descricaoProduto TEXT,
                    precoVenda DECIMAL(10,2) NOT NULL,
                    precoCompra DECIMAL(10,2) NOT NULL,
                    estoqueAtual INT DEFAULT 0,
                    estoqueMinimo INT NOT NULL,
                    estoqueMaximo INT NOT NULL,
                    unMedida VARCHAR(20) DEFAULT 'unidade',
                    idCategoria INT NOT NULL,
                    FOREIGN KEY (idCategoria) REFERENCES Categoria(idCategoria)
                )
            """,
            "FornecedorProduto": """
                CREATE TABLE IF NOT EXISTS FornecedorProduto (
                    idFornecedor INT NOT NULL,
                    idProduto INT NOT NULL,
                    precoFornecedor DECIMAL(10,2) NOT NULL,
                    PRIMARY KEY (idFornecedor, idProduto),
                    FOREIGN KEY (idFornecedor) REFERENCES Fornecedor(idFornecedor),
                    FOREIGN KEY (idProduto) REFERENCES Produto(idProduto)
                )
            """,
            "Venda": """
                CREATE TABLE IF NOT EXISTS Venda (
                    idVenda INT AUTO_INCREMENT PRIMARY KEY,
                    idUsuario INT NOT NULL,
                    idCliente INT,
                    valorTotal DECIMAL(10,2) NOT NULL,
                    descontoAplicado DECIMAL(10,2) DEFAULT 0,
                    dataHora DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (idUsuario) REFERENCES Usuario(idUsuario),
                    FOREIGN KEY (idCliente) REFERENCES Cliente(idCliente)
                )
            """,
            "ItemVenda": """
                CREATE TABLE IF NOT EXISTS ItemVenda (
                    idItem INT AUTO_INCREMENT PRIMARY KEY,
                    idVenda INT NOT NULL,
                    idProduto INT NOT NULL,
                    quantidade INT NOT NULL,
                    precoVenda DECIMAL(10,2) NOT NULL,
                    subTotal DECIMAL(10,2) NOT NULL,
                    FOREIGN KEY (idVenda) REFERENCES Venda(idVenda),
                    FOREIGN KEY (idProduto) REFERENCES Produto(idProduto)
                )
            """,
            "Pagamento": """
                CREATE TABLE IF NOT EXISTS Pagamento (
                    idPagamento INT AUTO_INCREMENT PRIMARY KEY,
                    idVenda INT NOT NULL,
                    formaPagamento VARCHAR(50) NOT NULL,
                    valorPago DECIMAL(10,2) NOT NULL,
                    statusPagamento VARCHAR(20) DEFAULT 'Pendente',
                    FOREIGN KEY (idVenda) REFERENCES Venda(idVenda)
                )
            """,
            "PontosCliente": """
                CREATE TABLE IF NOT EXISTS PontosCliente (
                    idOperacao INT AUTO_INCREMENT PRIMARY KEY,
                    idCliente INT NOT NULL,
                    tipoOperacao VARCHAR(20) NOT NULL,
                    pontos INT NOT NULL,
                    dataHora DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (idCliente) REFERENCES Cliente(idCliente)
                )
            """,
            "MovimentacaoEstoque": """
                CREATE TABLE IF NOT EXISTS MovimentacaoEstoque (
                    idMovimentacao INT AUTO_INCREMENT PRIMARY KEY,
                    idProduto INT NOT NULL,
                    idUsuario INT NOT NULL,
                    tipoMovimentacao VARCHAR(50) NOT NULL,
                    quantidade INT NOT NULL,
                    dataHora DATETIME DEFAULT CURRENT_TIMESTAMP,
                    motivo TEXT,
                    FOREIGN KEY (idProduto) REFERENCES Produto(idProduto),
                    FOREIGN KEY (idUsuario) REFERENCES Usuario(idUsuario)
                )
            """,
            "LogAcoes": """
                CREATE TABLE IF NOT EXISTS LogAcoes (
                    idLog INT AUTO_INCREMENT PRIMARY KEY,
                    idUsuario INT NOT NULL,
                    dataHora DATETIME DEFAULT CURRENT_TIMESTAMP,
                    acao TEXT NOT NULL,
                    FOREIGN KEY (idUsuario) REFERENCES Usuario(idUsuario)
                )
            """
        }
        
        # Inserir dados iniciais (exemplos)
        dados_iniciais = [
            ("CargoUsuario", "INSERT INTO CargoUsuario (nomeCargo, getNome) VALUES (%s, %s)", 
             [("Administrador", "Admin"), ("Caixa", "Caixa"), ("Estoquista", "Estoquista")]),
            
            ("Categoria", "INSERT INTO Categoria (nomeCategoria) VALUES (%s)", 
             [("Bebidas"), ("Lanches"), ("Sobremesas")]),
            
            ("Fornecedor", "INSERT INTO Fornecedor (nomeFornecedor, cnpj, emailFornecedor, telefone) VALUES (%s, %s, %s, %s)", 
             [("Café do Brasil", "12.345.678/0001-90", "contato@cafebrasil.com", "11 99999-9999")]),
            
            ("Cliente", "INSERT INTO Cliente (nomeCliente, emailCliente, enderecoCliente, telefone, totalPontos) VALUES (%s, %s, %s, %s, %s)", 
             [("João Silva", "joao@email.com", "Rua A, 123", "11 98765-4321", 0)]),
            
            ("Usuario", "INSERT INTO Usuario (nomeUsuario, cpfUsuario, email, senhaUsuario, idCargo) VALUES (%s, %s, %s, %s, %s)", 
             [("admin", "000.000.000-00", "admin@cafeteria.com", "admin123", 1)]),
            
            ("Produto", "INSERT INTO Produto (nomeProduto, descricaoProduto, precoVenda, precoCompra, estoqueAtual, estoqueMinimo, estoqueMaximo, unMedida, idCategoria) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
             [("Café Expresso", "Café tradicional", 5.00, 2.00, 50, 10, 100, "unidade", 1),
              ("Bolo de Cenoura", "Bolo caseiro", 8.00, 3.00, 20, 5, 50, "fatia", 3)]),
            
            ("FornecedorProduto", "INSERT INTO FornecedorProduto (idFornecedor, idProduto, precoFornecedor) VALUES (%s, %s, %s)", 
             [(1, 1, 2.00), (1, 2, 3.00)]),
        ]
        
        try:
            # Criar tabelas na ordem correta
            for nome_tabela, sql in tabelas.items():
                cursor.execute(sql)
            
            # Inserir dados iniciais
            for tabela, sql, dados in dados_iniciais:
                try:
                    cursor.executemany(sql, dados)
                except Error:
                    pass  # Ignorar duplicatas
            
            conexao.commit()
            return True
        except Error as e:
            messagebox.showerror("Erro de Banco", f"Erro ao inicializar banco: {e}")
            return False
        finally:
            cursor.close()
            conexao.close()

    def criar_conexao(self):
        """Cria conexão com o banco de dados MySQL"""
        try:
            conexao = mysql.connector.connect(
                host='localhost',
                database='cafeteria_db',
                user='root',
                password=''
            )
            if conexao.is_connected():
                return conexao
        except Error as e:
            messagebox.showerror("Erro", f"Erro ao conectar ao banco: {e}\nVerifique se o MySQL está rodando.")
            return None

    # =============== CONFIGURAÇÃO DO PDV ===============
    def setup_pdv(self):
        # Título do PDV
        titulo_pdv = ttk.Label(self.pdv_frame, text="PONTO DE VENDA (PDV)", style='Titulo.TLabel')
        titulo_pdv.pack(fill=tk.X, pady=10)
        
        # Barra de ferramentas
        toolbar = ttk.Frame(self.pdv_frame)
        toolbar.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(toolbar, text="Novo Cliente", command=self.selecionar_cliente, style='BotaoAzul.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Finalizar Venda", command=self.finalizar_venda, style='BotaoVerde.TButton').pack(side=tk.RIGHT, padx=5)
        
        # Cliente selecionado
        self.cliente_var = tk.StringVar(value="Cliente: Nenhum selecionado")
        ttk.Label(toolbar, textvariable=self.cliente_var, foreground='#3498db').pack(side=tk.LEFT, padx=10)
        
        # Frame para busca de produtos
        busca_frame = ttk.Frame(self.pdv_frame)
        busca_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(busca_frame, text="Buscar Produto:").pack(side=tk.LEFT, padx=5)
        self.busca_entry = ttk.Entry(busca_frame, font=('Arial', 12))
        self.busca_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.busca_entry.bind('<KeyRelease>', self.filtrar_produtos_pdv)
        
        # Lista de produtos
        produtos_frame = ttk.Frame(self.pdv_frame)
        produtos_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar_y = ttk.Scrollbar(produtos_frame)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x = ttk.Scrollbar(produtos_frame, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.produtos_tree = ttk.Treeview(
            produtos_frame, 
            columns=('ID', 'Produto', 'Preço', 'Estoque', 'Categoria'),
            show='headings',
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )
        
        self.produtos_tree.heading('ID', text='ID')
        self.produtos_tree.heading('Produto', text='Produto')
        self.produtos_tree.heading('Preço', text='Preço (R$)')
        self.produtos_tree.heading('Estoque', text='Estoque')
        self.produtos_tree.heading('Categoria', text='Categoria')
        
        self.produtos_tree.column('ID', width=50, anchor=tk.CENTER)
        self.produtos_tree.column('Produto', width=250, anchor=tk.W)
        self.produtos_tree.column('Preço', width=100, anchor=tk.E)
        self.produtos_tree.column('Estoque', width=100, anchor=tk.CENTER)
        self.produtos_tree.column('Categoria', width=150, anchor=tk.CENTER)
        
        self.produtos_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar_y.config(command=self.produtos_tree.yview)
        scrollbar_x.config(command=self.produtos_tree.xview)
        
        self.produtos_tree.bind('<Double-1>', self.adicionar_ao_carrinho)
        
        # Carrinho de compras
        carrinho_frame = ttk.LabelFrame(self.pdv_frame, text="Carrinho de Compras")
        carrinho_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.carrinho_tree = ttk.Treeview(
            carrinho_frame, 
            columns=('ID', 'Produto', 'Qtd', 'Preço', 'Subtotal'),
            show='headings'
        )
        
        self.carrinho_tree.heading('ID', text='ID')
        self.carrinho_tree.heading('Produto', text='Produto')
        self.carrinho_tree.heading('Qtd', text='Qtd')
        self.carrinho_tree.heading('Preço', text='Preço Unit.')
        self.carrinho_tree.heading('Subtotal', text='Subtotal')
        
        self.carrinho_tree.column('ID', width=50, anchor=tk.CENTER)
        self.carrinho_tree.column('Produto', width=200, anchor=tk.W)
        self.carrinho_tree.column('Qtd', width=70, anchor=tk.CENTER)
        self.carrinho_tree.column('Preço', width=100, anchor=tk.E)
        self.carrinho_tree.column('Subtotal', width=100, anchor=tk.E)
        
        self.carrinho_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Total e botões
        total_frame = ttk.Frame(self.pdv_frame)
        total_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.total_label = ttk.Label(total_frame, text="TOTAL: R$ 0.00", font=('Arial', 18, 'bold'), foreground='#e74c3c')
        self.total_label.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(total_frame, text="Remover Item", command=self.remover_do_carrinho, style='BotaoVermelho.TButton').pack(side=tk.RIGHT, padx=5)

    # =============== CONFIGURAÇÃO DA PRODUÇÃO ===============
    def setup_producao(self):
        # Título da Produção
        titulo_producao = ttk.Label(self.producao_frame, text="CONTROLE DE PRODUÇÃO", style='Titulo.TLabel')
        titulo_producao.pack(fill=tk.X, pady=10)
        
        # Frame para seleção de produto e quantidade
        selecao_frame = ttk.Frame(self.producao_frame)
        selecao_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(selecao_frame, text="Produto:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.produto_var = tk.StringVar()
        self.produto_combo = ttk.Combobox(selecao_frame, textvariable=self.produto_var, font=('Arial', 12), state='readonly')
        self.produto_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(selecao_frame, text="Quantidade:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.qtd_producao = ttk.Spinbox(selecao_frame, from_=1, to=1000, increment=1, font=('Arial', 12), width=10)
        self.qtd_producao.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(selecao_frame, text="Unidade:").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.unidade_label = ttk.Label(selecao_frame, text="", font=('Arial', 12, 'bold'), foreground='#3498db')
        self.unidade_label.grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)
        
        self.produto_combo.bind('<<ComboboxSelected>>', self.atualizar_unidade_producao)
        
        ttk.Button(selecao_frame, text="REGISTRAR PRODUÇÃO", command=self.registrar_producao, 
                  style='BotaoVerde.TButton', width=25).grid(row=2, column=0, columnspan=4, pady=15)
        
        # Relatório de produção
        relatorio_frame = ttk.LabelFrame(self.producao_frame, text="Últimas Movimentações de Estoque")
        relatorio_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.producao_tree = ttk.Treeview(
            relatorio_frame, 
            columns=('ID', 'Produto', 'Quantidade', 'Tipo', 'Data', 'Usuário'),
            show='headings'
        )
        
        self.producao_tree.heading('ID', text='ID')
        self.producao_tree.heading('Produto', text='Produto')
        self.producao_tree.heading('Quantidade', text='Quantidade')
        self.producao_tree.heading('Tipo', text='Tipo')
        self.producao_tree.heading('Data', text='Data/Hora')
        self.producao_tree.heading('Usuário', text='Usuário')
        
        self.producao_tree.column('ID', width=50, anchor=tk.CENTER)
        self.producao_tree.column('Produto', width=150, anchor=tk.W)
        self.producao_tree.column('Quantidade', width=100, anchor=tk.E)
        self.producao_tree.column('Tipo', width=100, anchor=tk.CENTER)
        self.producao_tree.column('Data', width=150, anchor=tk.CENTER)
        self.producao_tree.column('Usuário', width=100, anchor=tk.CENTER)
        
        scrollbar_y = ttk.Scrollbar(relatorio_frame, orient=tk.VERTICAL, command=self.producao_tree.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.producao_tree.configure(yscrollcommand=scrollbar_y.set)
        
        self.producao_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Atualizar relatório inicial
        self.atualizar_relatorio_producao()

    # =============== MÉTODOS DO PDV ===============
    def atualizar_produtos_pdv(self):
        """Atualiza a lista de produtos disponíveis para venda"""
        for item in self.produtos_tree.get_children():
            self.produtos_tree.delete(item)
        
        conexao = self.criar_conexao()
        if not conexao:
            return
        
        cursor = conexao.cursor(dictionary=True)
        sql = """
            SELECT p.idProduto, p.nomeProduto, p.precoVenda, p.estoqueAtual, c.nomeCategoria
            FROM Produto p
            JOIN Categoria c ON p.idCategoria = c.idCategoria
            WHERE p.estoqueAtual > 0
            ORDER BY p.nomeProduto
        """
        
        try:
            cursor.execute(sql)
            produtos = cursor.fetchall()
            
            for produto in produtos:
                self.produtos_tree.insert('', tk.END, values=(
                    produto['idProduto'],
                    produto['nomeProduto'],
                    f"{produto['precoVenda']:.2f}",
                    produto['estoqueAtual'],
                    produto['nomeCategoria']
                ))
        except Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar produtos: {e}")
        finally:
            cursor.close()
            conexao.close()

    def filtrar_produtos_pdv(self, event=None):
        """Filtra produtos com base no texto digitado"""
        texto_busca = self.busca_entry.get().lower()
        
        for item in self.produtos_tree.get_children():
            self.produtos_tree.delete(item)
        
        conexao = self.criar_conexao()
        if not conexao:
            return
        
        cursor = conexao.cursor(dictionary=True)
        sql = """
            SELECT p.idProduto, p.nomeProduto, p.precoVenda, p.estoqueAtual, c.nomeCategoria
            FROM Produto p
            JOIN Categoria c ON p.idCategoria = c.idCategoria
            WHERE p.estoqueAtual > 0 AND LOWER(p.nomeProduto) LIKE %s
            ORDER BY p.nomeProduto
        """
        
        try:
            cursor.execute(sql, (f"%{texto_busca}%",))
            produtos = cursor.fetchall()
            
            for produto in produtos:
                self.produtos_tree.insert('', tk.END, values=(
                    produto['idProduto'],
                    produto['nomeProduto'],
                    f"{produto['precoVenda']:.2f}",
                    produto['estoqueAtual'],
                    produto['nomeCategoria']
                ))
        except Error as e:
            messagebox.showerror("Erro", f"Erro ao filtrar produtos: {e}")
        finally:
            cursor.close()
            conexao.close()

    def adicionar_ao_carrinho(self, event=None):
        """Adiciona produto selecionado ao carrinho"""
        selecionado = self.produtos_tree.selection()
        if not selecionado:
            return
        
        item = self.produtos_tree.item(selecionado[0])
        valores = item['values']
        
        produto_id = int(valores[0])
        nome = valores[1]
        preco = float(valores[2])
        estoque = int(valores[3])
        
        qtd_janela = tk.Toplevel(self.root)
        qtd_janela.title(f"Quantidade para {nome}")
        qtd_janela.geometry("300x150")
        qtd_janela.transient(self.root)
        qtd_janela.grab_set()
        
        ttk.Label(qtd_janela, text=f"Quantidade de {nome}:").pack(pady=10)
        
        qtd_var = tk.StringVar(value="1")
        qtd_entry = ttk.Spinbox(qtd_janela, from_=1, to=estoque, textvariable=qtd_var, font=('Arial', 12), width=10)
        qtd_entry.pack(pady=5)
        qtd_entry.focus()
        
        def confirmar_quantidade():
            try:
                qtd = int(qtd_var.get())
                if qtd <= 0 or qtd > estoque:
                    messagebox.showerror("Erro", "Quantidade inválida!")
                    return
                
                # Verificar se produto já está no carrinho
                for item in self.carrinho:
                    if item['id'] == produto_id:
                        item['quantidade'] += qtd
                        item['subtotal'] = item['quantidade'] * preco
                        self.atualizar_carrinho()
                        qtd_janela.destroy()
                        return
                
                # Adicionar novo item ao carrinho
                self.carrinho.append({
                    'id': produto_id,
                    'nome': nome,
                    'quantidade': qtd,
                    'preco': preco,
                    'subtotal': qtd * preco
                })
                
                self.atualizar_carrinho()
                qtd_janela.destroy()
                
            except ValueError:
                messagebox.showerror("Erro", "Por favor, insira um número válido!")
        
        ttk.Button(qtd_janela, text="Confirmar", command=confirmar_quantidade, style='BotaoVerde.TButton').pack(pady=10)
        qtd_janela.bind('<Return>', lambda e: confirmar_quantidade())

    def atualizar_carrinho(self):
        """Atualiza a exibição do carrinho"""
        for item in self.carrinho_tree.get_children():
            self.carrinho_tree.delete(item)
        
        self.total_venda = 0.0
        
        for item in self.carrinho:
            self.carrinho_tree.insert('', tk.END, values=(
                item['id'],
                item['nome'],
                item['quantidade'],
                f"R$ {item['preco']:.2f}",
                f"R$ {item['subtotal']:.2f}"
            ))
            self.total_venda += item['subtotal']
        
        self.total_label.config(text=f"TOTAL: R$ {self.total_venda:.2f}")

    def remover_do_carrinho(self):
        """Remove item selecionado do carrinho"""
        selecionado = self.carrinho_tree.selection()
        if not selecionado:
            messagebox.showinfo("Informação", "Selecione um item para remover!")
            return
        
        if messagebox.askyesno("Confirmar", "Deseja remover este item do carrinho?"):
            item_id = self.carrinho_tree.item(selecionado[0])['values'][0]
            self.carrinho = [item for item in self.carrinho if item['id'] != item_id]
            self.atualizar_carrinho()

    def selecionar_cliente(self):
        """Abre a interface para selecionar cliente"""
        janela = tk.Toplevel(self.root)
        janela.title("Selecionar Cliente")
        janela.geometry("500x400")
        janela.transient(self.root)
        janela.grab_set()
        
        frame = ttk.Frame(janela, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Buscar Cliente:").pack(anchor=tk.W, pady=(0,5))
        busca_var = tk.StringVar()
        busca_entry = ttk.Entry(frame, textvariable=busca_var, width=40)
        busca_entry.pack(fill=tk.X, pady=(0,10))
        
        # Treeview para clientes
        tree = ttk.Treeview(frame, columns=('ID', 'Nome', 'Email', 'Pontos'), show='headings')
        tree.heading('ID', text='ID')
        tree.heading('Nome', text='Nome')
        tree.heading('Email', text='Email')
        tree.heading('Pontos', text='Pontos')
        
        tree.column('ID', width=50, anchor=tk.CENTER)
        tree.column('Nome', width=150)
        tree.column('Email', width=150)
        tree.column('Pontos', width=80, anchor=tk.CENTER)
        
        tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Botões
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Cancelar", command=janela.destroy).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Selecionar", command=lambda: self.confirmar_selecao_cliente(tree, janela), 
                  style='BotaoVerde.TButton').pack(side=tk.RIGHT)
        
        # Carregar clientes
        conexao = self.criar_conexao()
        if conexao:
            cursor = conexao.cursor(dictionary=True)
            try:
                cursor.execute("SELECT * FROM Cliente ORDER BY nomeCliente")
                clientes = cursor.fetchall()
                
                for cliente in clientes:
                    tree.insert('', tk.END, values=(
                        cliente['idCliente'],
                        cliente['nomeCliente'],
                        cliente['emailCliente'],
                        cliente['totalPontos']
                    ))
            except Error as e:
                messagebox.showerror("Erro", f"Erro ao carregar clientes: {e}")
            finally:
                cursor.close()
                conexao.close()
        
        busca_entry.bind('<KeyRelease>', lambda e: self.filtrar_clientes(tree, busca_var.get()))

    def filtrar_clientes(self, tree, texto):
        """Filtra clientes na treeview"""
        for item in tree.get_children():
            tree.delete(item)
        
        conexao = self.criar_conexao()
        if conexao:
            cursor = conexao.cursor(dictionary=True)
            try:
                cursor.execute("SELECT * FROM Cliente WHERE nomeCliente LIKE %s ORDER BY nomeCliente", (f"%{texto}%",))
                clientes = cursor.fetchall()
                
                for cliente in clientes:
                    tree.insert('', tk.END, values=(
                        cliente['idCliente'],
                        cliente['nomeCliente'],
                        cliente['emailCliente'],
                        cliente['totalPontos']
                    ))
            except Error:
                pass
            finally:
                cursor.close()
                conexao.close()

    def confirmar_selecao_cliente(self, tree, janela):
        """Confirma a seleção do cliente"""
        selecionado = tree.selection()
        if not selecionado:
            messagebox.showinfo("Informação", "Selecione um cliente!")
            return
        
        item = tree.item(selecionado[0])
        valores = item['values']
        
        self.cliente_selecionado = {
            'id': valores[0],
            'nome': valores[1],
            'pontos': valores[3]
        }
        
        self.cliente_var.set(f"Cliente: {valores[1]} ({valores[3]} pontos)")
        janela.destroy()

    def finalizar_venda(self):
        """Finaliza a venda e registra no banco"""
        if not self.carrinho:
            messagebox.showinfo("Informação", "O carrinho está vazio!")
            return
        
        # Verificar estoque
        conexao = self.criar_conexao()
        if not conexao:
            return
        
        cursor = conexao.cursor(dictionary=True)
        try:
            # Verificar estoque para cada produto
            for item in self.carrinho:
                cursor.execute("SELECT estoqueAtual FROM Produto WHERE idProduto = %s", (item['id'],))
                produto = cursor.fetchone()
                if produto['estoqueAtual'] < item['quantidade']:
                    messagebox.showerror("Erro", f"Estoque insuficiente para {item['nome']}!")
                    return
            
            # Confirmar venda
            if messagebox.askyesno("Confirmar Venda", f"Finalizar venda no valor de R$ {self.total_venda:.2f}?"):
                # Registrar venda
                sql_venda = """
                    INSERT INTO Venda (idUsuario, idCliente, valorTotal, descontoAplicado)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql_venda, (
                    self.usuario_logado['idUsuario'],
                    self.cliente_selecionado['id'] if self.cliente_selecionado else None,
                    self.total_venda,
                    0.0
                ))
                venda_id = cursor.lastrowid
                
                # Registrar itens
                for item in self.carrinho:
                    sql_item = """
                        INSERT INTO ItemVenda (idVenda, idProduto, quantidade, precoVenda, subTotal)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql_item, (
                        venda_id,
                        item['id'],
                        item['quantidade'],
                        item['preco'],
                        item['subtotal']
                    ))
                    
                    # Atualizar estoque
                    sql_estoque = """
                        UPDATE Produto SET estoqueAtual = estoqueAtual - %s 
                        WHERE idProduto = %s
                    """
                    cursor.execute(sql_estoque, (item['quantidade'], item['id']))
                    
                    # Registrar movimentação de estoque
                    sql_mov = """
                        INSERT INTO MovimentacaoEstoque (idProduto, idUsuario, tipoMovimentacao, 
                                                      quantidade, motivo)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql_mov, (
                        item['id'],
                        self.usuario_logado['idUsuario'],
                        'Venda',
                        item['quantidade'],
                        f"Venda ID: {venda_id}"
                    ))
                
                # Registrar pagamento
                sql_pag = """
                    INSERT INTO Pagamento (idVenda, formaPagamento, valorPago, statusPagamento)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql_pag, (
                    venda_id,
                    "Dinheiro",
                    self.total_venda,
                    "Concluído"
                ))
                
                # Atualizar pontos do cliente
                if self.cliente_selecionado:
                    pontos = int(self.total_venda // 10)  # 1 ponto a cada R$10
                    sql_pontos = """
                        UPDATE Cliente SET totalPontos = totalPontos + %s 
                        WHERE idCliente = %s
                    """
                    cursor.execute(sql_pontos, (pontos, self.cliente_selecionado['id']))
                    
                    # Registrar histórico de pontos
                    sql_historico = """
                        INSERT INTO PontosCliente (idCliente, tipoOperacao, pontos)
                        VALUES (%s, %s, %s)
                    """
                    cursor.execute(sql_historico, (
                        self.cliente_selecionado['id'],
                        "Compra",
                        pontos
                    ))
                
                conexao.commit()
                
                # Limpar carrinho
                self.carrinho = []
                self.total_venda = 0.0
                self.cliente_selecionado = None
                self.cliente_var.set("Cliente: Nenhum selecionado")
                self.atualizar_carrinho()
                self.atualizar_produtos_pdv()
                self.atualizar_relatorio_producao()
                
                messagebox.showinfo("Sucesso", f"Venda registrada com sucesso!\nID: {venda_id}\nTotal: R$ {self.total_venda:.2f}")
        
        except Error as e:
            conexao.rollback()
            messagebox.showerror("Erro", f"Erro ao registrar venda: {e}")
        finally:
            cursor.close()
            conexao.close()

    # =============== MÉTODOS DA PRODUÇÃO ===============
    def atualizar_produtos_producao(self):
        """Atualiza a lista de produtos para produção"""
        conexao = self.criar_conexao()
        if not conexao:
            return
        
        cursor = conexao.cursor(dictionary=True)
        sql = "SELECT idProduto, nomeProduto, unMedida FROM Produto ORDER BY nomeProduto"
        
        try:
            cursor.execute(sql)
            produtos = cursor.fetchall()
            
            self.produto_combo['values'] = [p['nomeProduto'] for p in produtos]
            if produtos:
                self.produto_combo.current(0)
                self.atualizar_unidade_producao()
        except Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar produtos para produção: {e}")
        finally:
            cursor.close()
            conexao.close()

    def atualizar_unidade_producao(self, event=None):
        """Atualiza o rótulo da unidade de medida"""
        produto_nome = self.produto_var.get()
        
        conexao = self.criar_conexao()
        if not conexao:
            return
        
        cursor = conexao.cursor(dictionary=True)
        sql = "SELECT unMedida FROM Produto WHERE nomeProduto = %s"
        
        try:
            cursor.execute(sql, (produto_nome,))
            produto = cursor.fetchone()
            
            if produto:
                unidade = produto['unMedida']
                self.unidade_label.config(text=unidade)
        except Error as e:
            messagebox.showerror("Erro", f"Erro ao buscar unidade: {e}")
        finally:
            cursor.close()
            conexao.close()

    def registrar_producao(self):
        """Registra uma nova produção"""
        produto_nome = self.produto_var.get()
        try:
            quantidade = int(self.qtd_producao.get())
        except ValueError:
            messagebox.showerror("Erro", "Quantidade inválida!")
            return
        
        if quantidade <= 0:
            messagebox.showerror("Erro", "A quantidade deve ser maior que zero!")
            return
        
        conexao = self.criar_conexao()
        if not conexao:
            return
        
        cursor = conexao.cursor(dictionary=True)
        try:
            # Obter ID do produto
            sql_id = "SELECT idProduto FROM Produto WHERE nomeProduto = %s"
            cursor.execute(sql_id, (produto_nome,))
            produto = cursor.fetchone()
            
            if not produto:
                messagebox.showerror("Erro", "Produto não encontrado!")
                return
            
            produto_id = produto['idProduto']
            
            # Registrar movimentação de estoque
            sql_mov = """
                INSERT INTO MovimentacaoEstoque (idProduto, idUsuario, tipoMovimentacao, 
                                              quantidade, motivo)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql_mov, (
                produto_id,
                self.usuario_logado['idUsuario'],
                'Produção',
                quantidade,
                "Registro de produção"
            ))
            
            # Atualizar estoque
            sql_estoque = """
                UPDATE Produto SET estoqueAtual = estoqueAtual + %s 
                WHERE idProduto = %s
            """
            cursor.execute(sql_estoque, (quantidade, produto_id))
            
            conexao.commit()
            
            # Limpar campos
            self.qtd_producao.delete(0, tk.END)
            self.qtd_producao.insert(0, "1")
            
            # Atualizar interfaces
            self.atualizar_produtos_pdv()
            self.atualizar_relatorio_producao()
            
            messagebox.showinfo("Sucesso", f"Produção registrada com sucesso!\n{quantidade} unidades de {produto_nome} adicionadas ao estoque.")
            
        except Error as e:
            conexao.rollback()
            messagebox.showerror("Erro", f"Erro ao registrar produção: {e}")
        finally:
            cursor.close()
            conexao.close()

    def atualizar_relatorio_producao(self):
        """Atualiza o relatório de movimentações de estoque"""
        for item in self.producao_tree.get_children():
            self.producao_tree.delete(item)
        
        conexao = self.criar_conexao()
        if not conexao:
            return
        
        cursor = conexao.cursor(dictionary=True)
        sql = """
            SELECT m.idMovimentacao, p.nomeProduto, m.quantidade, m.tipoMovimentacao, 
                   m.dataHora, u.nomeUsuario
            FROM MovimentacaoEstoque m
            JOIN Produto p ON m.idProduto = p.idProduto
            JOIN Usuario u ON m.idUsuario = u.idUsuario
            ORDER BY m.dataHora DESC
            LIMIT 20
        """
        
        try:
            cursor.execute(sql)
            movimentacoes = cursor.fetchall()
            
            for mov in movimentacoes:
                self.producao_tree.insert('', tk.END, values=(
                    mov['idMovimentacao'],
                    mov['nomeProduto'],
                    mov['quantidade'],
                    mov['tipoMovimentacao'],
                    mov['dataHora'].strftime('%d/%m/%Y %H:%M'),
                    mov['nomeUsuario']
                ))
        except Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar relatório: {e}")
        finally:
            cursor.close()
            conexao.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = CafeteriaApp(root)
    root.mainloop()
