import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import win32print
import fdb
import sys
import traceback
import json
import os

class EtiquetasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Impressão de Etiquetas - v4.0")
        self.root.geometry("1100x700")

        self.impressora_etiquetas = None
             
        # Variáveis
        self.selecionados = []
        self.fila_impressao = []
        self.fonte_padrao = ('Arial', 10)
        self.fonte_titulo = ('Arial', 12, 'bold')
        self.config_file = "config.json"
        self.pesquisa_em_andamento = False
        
        # Configurar interface
        self.criar_interface()
        
        # Carregar configuração salva
        self.carregar_configuracao()
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling for the canvas"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _on_close(self):
        """Clean up bindings when closing window"""
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")
        self.root.destroy()
        
    def log_error(self, error_msg, exception):
        """Registra erros no console e exibe mensagem ao usuário"""
        print(error_msg)
        traceback.print_exc()
        messagebox.showerror("Erro", error_msg)
    
    def carregar_configuracao(self):
        """Carrega o último caminho do banco de dados usado"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    if 'ultimo_banco' in config and os.path.exists(config['ultimo_banco']):
                        self.lbl_arquivo.config(text=config['ultimo_banco'])
                        self.status_bar.config(text=f"Banco carregado: {config['ultimo_banco']}")
                    self.impressora_etiquetas = config.get("impressora_etiquetas", None)
                    if self.impressora_etiquetas:
                        self.lbl_impressora.config(text=self.impressora_etiquetas)
        except Exception as e:
            self.log_error(f"[ERRO] Ao carregar configuração: {e}", e)

    def salvar_configuracao(self, caminho):
        """Salva o caminho do banco de dados para uso futuro"""
        try:
            config = {'ultimo_banco': caminho}
            config["impressora_etiquetas"] = self.impressora_etiquetas
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            self.log_error(f"[ERRO] Ao salvar configuração: {e}", e)

    def selecionar_impressora(self):
        impressoras = [p[2] for p in win32print.EnumPrinters(5)]
        impressoras = impressoras + [p[2] for p in win32print.EnumPrinters(2)]

        # Janela de seleção
        janela = tk.Toplevel(self.root)
        janela.title("Selecionar Impressora")
        janela.geometry("800x120")
        janela.resizable(False, False)

        tk.Label(janela, text="Escolha a impressora:", font=self.fonte_padrao).pack(pady=10)

        combo = ttk.Combobox(janela, values=impressoras, font=self.fonte_padrao, state="readonly")
        combo.pack(pady=5)
        combo.set(self.impressora_etiquetas or win32print.GetDefaultPrinter())

        def confirmar():
            selecionada = combo.get()
            self.impressora_etiquetas = selecionada
            self.lbl_impressora.config(text=selecionada)
            self.salvar_configuracao(self.lbl_arquivo.cget("text"))
            ##messagebox.showinfo("Impressora Selecionada", f"Impressora '{selecionada}' salva com sucesso.")
            janela.destroy()

        btn_confirmar = tk.Button(janela, text="Confirmar", command=confirmar, font=self.fonte_padrao, bg="#4CAF50", fg="white")
        btn_confirmar.pack(pady=5)

    def criar_interface(self):
        # Frame de banco de dados
        frame_db = tk.LabelFrame(self.root, text="Conexão com Banco de Dados", 
                               font=self.fonte_titulo, padx=10, pady=10)
        frame_db.pack(pady=5, padx=10, fill=tk.X)
        
        btn_db = tk.Button(frame_db, text="Selecionar Banco de Dados", 
                         command=self.selecionar_arquivo, font=self.fonte_padrao)
        btn_db.pack(side=tk.LEFT)
            
        self.lbl_arquivo = tk.Label(frame_db, text="Nenhum arquivo selecionado", 
                                  font=self.fonte_padrao, fg="gray")
        self.lbl_arquivo.pack(side=tk.LEFT, padx=10)
        
        # Frame de impressora
        frame_impressora = tk.LabelFrame(self.root, text="Configuração de Impressora", 
                                      font=self.fonte_titulo, padx=10, pady=10)
        frame_impressora.pack(pady=5, padx=10, fill=tk.X)
        
        btn_impressora = tk.Button(frame_impressora, text="Selecionar Impressora",
                                  command=self.selecionar_impressora, font=self.fonte_padrao)
        btn_impressora.pack(side=tk.LEFT)
        
        self.lbl_impressora = tk.Label(frame_impressora, text="Nenhuma impressora selecionada", 
                                     font=self.fonte_padrao, fg="gray")
        self.lbl_impressora.pack(side=tk.LEFT, padx=10)
        
        # Frame de busca
        frame_busca = tk.LabelFrame(self.root, text="Pesquisa", 
                                  font=self.fonte_titulo, padx=10, pady=10)
        frame_busca.pack(pady=5, padx=10, fill=tk.X)
        
        tk.Label(frame_busca, text="Nº Nota:", font=self.fonte_padrao).grid(row=0, column=0, padx=5)
        self.entry_nota = tk.Entry(frame_busca, width=15, font=self.fonte_padrao)
        self.entry_nota.grid(row=0, column=1, padx=5)
        self.entry_nota.bind('<Return>', lambda event: self.pesquisar())
        
        tk.Label(frame_busca, text="Código:", font=self.fonte_padrao).grid(row=0, column=2, padx=5)
        self.entry_codigo = tk.Entry(frame_busca, width=15, font=self.fonte_padrao)
        self.entry_codigo.grid(row=0, column=3, padx=5)
        self.entry_codigo.bind('<Return>', lambda event: self.pesquisar())
        
        tk.Label(frame_busca, text="Descrição:", font=self.fonte_padrao).grid(row=0, column=4, padx=5)
        self.entry_desc = tk.Entry(frame_busca, width=40, font=self.fonte_padrao)
        self.entry_desc.grid(row=0, column=5, padx=5)
        self.entry_desc.bind('<Return>', lambda event: self.pesquisar())
        
        self.btn_pesquisar = tk.Button(frame_busca, text="Pesquisar", command=self.pesquisar, 
                                     font=self.fonte_padrao, state=tk.NORMAL)
        self.btn_pesquisar.grid(row=0, column=6, padx=5)
        
        # Frame de resultados
        self.frame_resultados = tk.Frame(self.root)
        self.frame_resultados.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Canvas e barras de rolagem
        self.canvas = tk.Canvas(self.frame_resultados, borderwidth=0)
        self.scrollbar_y = ttk.Scrollbar(self.frame_resultados, orient="vertical", command=self.canvas.yview)
        self.scrollbar_x = ttk.Scrollbar(self.frame_resultados, orient="horizontal", command=self.canvas.xview)
        
        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        # Vincular eventos do mouse para rolagem
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar_y.pack(side="right", fill="y")
        self.scrollbar_x.pack(side="bottom", fill="x")
        
        # Frame de botões
        frame_botoes = tk.Frame(self.root)
        frame_botoes.pack(pady=5)
        
        # Botão para adicionar à fila
        btn_adicionar_fila = tk.Button(frame_botoes, text="Adicionar à Fila", 
                                     command=self.adicionar_a_fila, 
                                     font=self.fonte_padrao, bg="#2196F3", fg="white")
        btn_adicionar_fila.pack(side=tk.LEFT, padx=5)
        
        # Botão para imprimir diretamente
        btn_imprimir_direto = tk.Button(frame_botoes, text="Imprimir Selecionados", 
                                       command=self.imprimir_selecionados_diretamente, 
                                       font=self.fonte_padrao, bg="#4CAF50", fg="white")
        btn_imprimir_direto.pack(side=tk.LEFT, padx=5)
        
        # Botão para ver fila
        btn_ver_fila = tk.Button(frame_botoes, text="Ver Fila de Impressão", 
                               command=self.mostrar_fila_impressao, 
                               font=self.fonte_padrao, bg="#FF9800", fg="white")
        btn_ver_fila.pack(side=tk.LEFT, padx=5)
        
        # Barra de status
        self.status_bar = tk.Label(self.root, text="Pronto", bd=1, relief=tk.SUNKEN, 
                                 anchor=tk.W, font=self.fonte_padrao)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Configurar fechamento da janela
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def bloquear_controles_pesquisa(self, bloquear):
        """Bloqueia ou desbloqueia os controles durante uma pesquisa"""
        state = tk.DISABLED if bloquear else tk.NORMAL
        self.btn_pesquisar.config(state=state)
        self.entry_nota.config(state=state)
        self.entry_codigo.config(state=state)
        self.entry_desc.config(state=state)
        self.root.update()  # Atualiza a interface imediatamente
    
    from tkinter import simpledialog  # adicione se ainda não tiver

    def selecionar_arquivo(self):
        caminho = filedialog.askopenfilename(
            filetypes=[("Firebird Database", "*.fdb"), ("Todos os arquivos", "*.*")],
            title="Selecione o arquivo do banco de dados"
        )

        if not caminho:
            caminho = simpledialog.askstring(
                "Caminho manual",
                "Digite o caminho do banco (ex: \\\\192.168.1.10\\dados\\empresa.fdb):"
            )

        if caminho:
            self.lbl_arquivo.config(text=caminho)
            self.status_bar.config(text=f"Banco de dados selecionado: {caminho}")
            self.salvar_configuracao(caminho)

    def conectar_firebird(self, caminho):
        try:
            # Normalizar barras
            caminho = caminho.replace('/', '\\')

            # Detectar se é caminho estilo config.json: //servidor/C/...
            if caminho.startswith("\\\\") or caminho.startswith("//"):
                partes = caminho.strip("\\/").split("\\")
                if len(partes) >= 2:
                    host = partes[0]
                    # Se o segundo elemento for "C", montar corretamente
                    if partes[1].upper() == "C":
                        caminho_local = "C:\\" + "\\".join(partes[2:])
                    else:
                        caminho_local = "\\".join(partes[1:])
                    print(f"[INFO] Caminho de rede estilo config.json detectado")
                    print(f"[INFO] Host: {host}")
                    print(f"[INFO] Caminho local no servidor: {caminho_local}")
                else:
                    raise ValueError("[ERRO] Caminho de rede inválido")
            else:
                host = 'localhost'
                caminho_local = caminho
                print(f"[INFO] Caminho local detectado")

            print(f"[LOG] Tentando conectar: host={host}, database={caminho_local}")

            conexao = fdb.connect(
                host=host,
                database=caminho_local,
                user='SYSDBA',
                password='masterkey',
                charset='UTF8'
            )

            print("[LOG] Conexão estabelecida com sucesso")
            return conexao

        except Exception as e:
            print("[ERRO] Falha ao conectar ao banco de dados:")
            print(e)
            return None
    
    def pesquisar(self):
        if self.pesquisa_em_andamento:
            return
            
        try:
            self.pesquisa_em_andamento = True
            self.bloquear_controles_pesquisa(True)
            
            termo_nota = self.entry_nota.get().strip()
            termo_codigo = self.entry_codigo.get().strip().lower()
            termo_desc = self.entry_desc.get().strip().lower()
            
            # Limpar resultados anteriores
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            self.selecionados = []
            
            # Obter conexão com o banco de dados
            caminho_db = self.lbl_arquivo.cget("text")
            if caminho_db == "Nenhum arquivo selecionado":
                messagebox.showwarning("Aviso", "Selecione um banco de dados primeiro")
                return
            
            conexao = self.conectar_firebird(caminho_db)
            if not conexao:
                return
            
            try:
                cursor = conexao.cursor()
                
                if termo_nota:  # Priorizar busca por número da nota
                    # Primeiro verificar se há múltiplas notas com o mesmo número
                    sql_notas = """SELECT t.ent_nrnota, t.ent_data_entrada, c.nome, c.id_cliente
                                 FROM tentradas t
                                 JOIN cliente c ON c.id_cliente = t.for_idfornecedor
                                 WHERE t.ent_nrnota = ?"""
                    cursor.execute(sql_notas, [termo_nota])
                    notas = cursor.fetchall()
                    
                    if len(notas) > 1:
                        # Mostrar tela de seleção para o usuário escolher qual nota
                        nota_selecionada = self.selecionar_nota(notas)
                        if not nota_selecionada:
                            return  # Usuário cancelou
                        
                        # Buscar itens apenas da nota selecionada
                        sql = """SELECT p.id_produto as codigo, p.descricao, p.referencia, i.quantidade
                                 FROM tentrada_itens i
                                 JOIN tentradas t ON t.ent_identrada = i.ent_identrada
                                 JOIN produto p ON p.id_produto = i.prd_idproduto 
                                 WHERE t.ent_nrnota = ? AND t.for_idfornecedor = ?"""
                        cursor.execute(sql, [termo_nota, nota_selecionada['id_fornecedor']])
                    else:
                        # Buscar itens normalmente (apenas uma nota encontrada)
                        sql = """SELECT p.id_produto as codigo, p.descricao, p.referencia, i.quantidade
                                 FROM tentrada_itens i
                                 JOIN tentradas t ON t.ent_identrada = i.ent_identrada
                                 JOIN produto p ON p.id_produto = i.prd_idproduto 
                                 WHERE t.ent_nrnota = ?"""
                        cursor.execute(sql, [termo_nota])
                else:
                    # Consulta SQL padrão (sem busca por nota)
                    sql = """SELECT p.id_produto as codigo, p.descricao, p.referencia, 0 as quantidade
                             FROM produto p 
                             WHERE p.ativo = 'S'"""
                    parametros = []
                    
                    if termo_codigo:
                        sql += " AND p.id_produto = ?"
                        parametros.append(termo_codigo.upper())
                    elif termo_desc:
                        sql += " AND (LOWER(p.descricao) LIKE ? OR LOWER(p.referencia) LIKE ?)"
                        parametros.append(f"%{termo_desc}%")
                        parametros.append(f"%{termo_desc}%")
                        
                    sql += " ORDER BY p.id_produto"
                    cursor.execute(sql, parametros)
                
                resultados = cursor.fetchall()
                
                if not resultados:
                    self.status_bar.config(text="Nenhum resultado encontrado")
                    messagebox.showinfo("Informação", "Nenhum produto encontrado com os critérios informados")
                    return
                
                self.criar_lista_resultados(resultados)
                self.status_bar.config(text=f"Encontrados {len(resultados)} itens")
                
            except Exception as e:
                error_msg = f"Erro ao consultar o banco de dados:\n{str(e)}"
                self.log_error(error_msg, e)
            finally:
                conexao.close()
                self.bloquear_controles_pesquisa(False)
                self.pesquisa_em_andamento = False
                
        except Exception as e:
            error_msg = f"Erro inesperado na pesquisa:\n{str(e)}"
            self.log_error(error_msg, e)
            self.bloquear_controles_pesquisa(False)
            self.pesquisa_em_andamento = False

    def selecionar_nota(self, notas):
        """Abre uma janela para o usuário selecionar qual nota deseja visualizar"""
        janela = tk.Toplevel(self.root)
        janela.title("Selecionar Nota Fiscal")
        janela.geometry("600x400")  # Aumentei a altura para caber os botões
        janela.resizable(False, False)
        janela.transient(self.root)
        janela.grab_set()
        
        # Frame principal
        frame_principal = tk.Frame(janela, padx=10, pady=10)
        frame_principal.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame_principal, 
                text="Foram encontradas múltiplas notas com o mesmo número.\nSelecione a nota desejada:",
                font=self.fonte_titulo).pack(pady=10)
        
        # Frame para a treeview com scrollbar
        frame_tree = tk.Frame(frame_principal)
        frame_tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Treeview para mostrar as notas
        colunas = ("Número", "Data Entrada", "Fornecedor")
        tree = ttk.Treeview(frame_tree, columns=colunas, show="headings", selectmode="browse")
        
        # Scrollbar para a treeview
        scrollbar = ttk.Scrollbar(frame_tree, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Configurar colunas
        tree.heading("Número", text="Número")
        tree.column("Número", width=100, anchor=tk.CENTER)
        
        tree.heading("Data Entrada", text="Data Entrada")
        tree.column("Data Entrada", width=120, anchor=tk.CENTER)
        
        tree.heading("Fornecedor", text="Fornecedor")
        tree.column("Fornecedor", width=300, anchor=tk.W)
        
        # Adicionar itens à treeview
        for nota in notas:
            tree.insert("", tk.END, values=(
                nota[0],  # Número da nota
                nota[1].strftime("%d/%m/%Y") if nota[1] else "N/A",  # Data formatada
                nota[2]   # Nome do fornecedor
            ), tags=(nota[3],))  # Armazenar ID do fornecedor nas tags
        
        # Empacotar treeview e scrollbar
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Variável para armazenar o resultado
        resultado = None
        
        def confirmar_selecao():
            nonlocal resultado
            selecionado = tree.selection()
            if not selecionado:
                messagebox.showwarning("Aviso", "Selecione uma nota para continuar")
                return
                
            item = tree.item(selecionado[0])
            # Recuperar o ID do fornecedor das tags
            id_fornecedor = item['tags'][0]
            
            resultado = {
                'numero': item['values'][0],
                'data_entrada': item['values'][1],
                'fornecedor': item['values'][2],
                'id_fornecedor': id_fornecedor
            }
            janela.destroy()
        
        def cancelar():
            nonlocal resultado
            resultado = None
            janela.destroy()
        
        # Frame de botões
        frame_botoes = tk.Frame(frame_principal)
        frame_botoes.pack(fill=tk.X, pady=10)
        
        btn_cancelar = tk.Button(frame_botoes, text="Cancelar", command=cancelar,
                            font=self.fonte_padrao)
        btn_cancelar.pack(side=tk.RIGHT, padx=5)
        
        btn_confirmar = tk.Button(frame_botoes, text="Selecionar", command=confirmar_selecao,
                                font=self.fonte_padrao, bg="#4CAF50", fg="white")
        btn_confirmar.pack(side=tk.RIGHT, padx=5)
        
        # Permitir seleção com duplo clique também
        def on_double_click(event):
            confirmar_selecao()
        
        tree.bind("<Double-1>", on_double_click)
        
        # Centralizar a janela
        janela.update_idletasks()
        x = (self.root.winfo_width() - janela.winfo_width()) // 2 + self.root.winfo_x()
        y = (self.root.winfo_height() - janela.winfo_height()) // 2 + self.root.winfo_y()
        janela.geometry(f"+{x}+{y}")
        
        # Focar na treeview
        tree.focus_set()
        
        # Selecionar o primeiro item por padrão
        if tree.get_children():
            tree.selection_set(tree.get_children()[0])
            tree.focus(tree.get_children()[0])
        
        # Esperar até que a janela seja fechada
        self.root.wait_window(janela)
        
        return resultado
    
    def criar_lista_resultados(self, resultados):
        # Limpar frame primeiro
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Configurar colunas com larguras adequadas
        colunas = [
            ("", 50),
            ("Código", 120),
            ("Descrição", 400),
            ("Referência", 150),
            ("Qtd. Etiquetas", 120)
        ]
        
        # Cabeçalhos
        for col_idx, (texto, largura) in enumerate(colunas):
            lbl = tk.Label(self.scrollable_frame, text=texto, font=self.fonte_padrao, 
                        borderwidth=1, relief="solid", padx=5, pady=5)
            lbl.grid(row=0, column=col_idx, sticky="ew")
            self.scrollable_frame.grid_columnconfigure(col_idx, minsize=largura)
        
        # Checkbox para selecionar todos (na coluna 0)
        self.var_selecionar_todos = tk.BooleanVar()
        chk_todos = tk.Checkbutton(self.scrollable_frame, variable=self.var_selecionar_todos,
                                command=self.toggle_selecionar_todos)
        chk_todos.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        # Adicionar linha separadora após cabeçalho
        separator = ttk.Separator(self.scrollable_frame, orient='horizontal')
        separator.grid(row=1, column=0, columnspan=5, sticky='ew', pady=2)
        
        # Adicionar cada resultado como uma linha
        self.selecionados = []
        for idx, item in enumerate(resultados, start=1):
            codigo, descricao, referencia, quantidade = item
            
            var_selecao = tk.BooleanVar()
            var_qtd = tk.StringVar(value=str(quantidade) if quantidade > 0 else "1")
            
            # Linha do item (usa row=idx*2 porque pulamos linhas para os separadores)
            row_pos = idx * 2
            
            # Checkbox de seleção
            chk = tk.Checkbutton(self.scrollable_frame, variable=var_selecao,
                            command=self.atualizar_selecionar_todos)
            chk.grid(row=row_pos, column=0, sticky="w", padx=10, pady=2)
            
            # Código
            lbl_codigo = tk.Label(self.scrollable_frame, text=codigo, font=self.fonte_padrao)
            lbl_codigo.grid(row=row_pos, column=1, sticky="w", padx=5, pady=2)
            
            # Descrição
            lbl_desc = tk.Label(self.scrollable_frame, text=descricao, font=self.fonte_padrao, 
                            wraplength=380, justify="left", anchor="w")
            lbl_desc.grid(row=row_pos, column=2, sticky="w", padx=5, pady=2)
            
            # Referência
            lbl_ref = tk.Label(self.scrollable_frame, text=referencia, font=self.fonte_padrao)
            lbl_ref.grid(row=row_pos, column=3, sticky="w", padx=5, pady=2)
            
            # Quantidade
            entry_qtd = tk.Entry(self.scrollable_frame, textvariable=var_qtd, 
                            width=5, font=self.fonte_padrao)
            entry_qtd.grid(row=row_pos, column=4, sticky="w", padx=5, pady=2)
            
            # Adicionar linha separadora (na próxima linha ímpar)
            if idx < len(resultados):
                separator = ttk.Separator(self.scrollable_frame, orient='horizontal')
                separator.grid(row=row_pos+1, column=0, columnspan=5, sticky='ew', pady=2)
            
            self.selecionados.append({
                "codigo": codigo,
                "descricao": descricao,
                "referencia": referencia,
                "var_selecao": var_selecao,
                "var_qtd": var_qtd,
                "row_pos": row_pos,
                "widgets": [chk, lbl_codigo, lbl_desc, lbl_ref, entry_qtd]
            })
        
        # Ajustar o canvas após adicionar os widgets
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        # Focar o canvas para garantir que o mouse scroll funcione
        self.canvas.focus_set()

    def toggle_selecionar_todos(self):
        """Marca ou desmarca todos os checkboxes baseado no checkbox principal"""
        estado = self.var_selecionar_todos.get()
        for item in self.selecionados:
            item["var_selecao"].set(estado)

    def atualizar_selecionar_todos(self):
        """Atualiza o estado do checkbox 'Selecionar Todos' baseado nos checkboxes individuais"""
        if not self.selecionados:
            return
        
        # Verifica se todos estão selecionados
        todos_selecionados = all(item["var_selecao"].get() for item in self.selecionados)
        # Verifica se nenhum está selecionado
        nenhum_selecionado = all(not item["var_selecao"].get() for item in self.selecionados)
        
        # Atualiza o checkbox principal
        if todos_selecionados:
            self.var_selecionar_todos.set(True)
        elif nenhum_selecionado:
            self.var_selecionar_todos.set(False)
        else:
            # Estado misto (alguns selecionados, outros não)
            self.var_selecionar_todos.set(False)
    def imprimir_selecionados_diretamente(self):
        """Imprime os itens selecionados sem adicionar à fila"""
        try:
            fila = []
            for item in self.selecionados:
                if item["var_selecao"].get():
                    try:
                        qtd = int(item["var_qtd"].get())
                        if qtd <= 0:
                            raise ValueError
                        
                        for _ in range(qtd):
                            fila.append({
                                "codigo": item["codigo"],
                                "descricao": item["descricao"],
                                "referencia": item["referencia"]
                            })
                    except ValueError:
                        messagebox.showwarning("Aviso", f"Quantidade inválida para o item {item['codigo']}")
                        return
            
            if not fila:
                messagebox.showwarning("Aviso", "Nenhum item selecionado para impressão")
                return
            
            epl_texto = self.gerar_epl(fila)
            self.imprimir(epl_texto)
            
            self.status_bar.config(text=f"Impressão concluída - {len(fila)} etiquetas enviadas")
            
        except Exception as e:
            error_msg = f"Erro ao imprimir selecionados:\n{str(e)}"
            self.log_error(error_msg, e)

    def adicionar_a_fila(self):
        try:
            adicionados = 0
            itens_para_remover = []
            
            for item in self.selecionados:
                if item["var_selecao"].get():
                    try:
                        qtd = int(item["var_qtd"].get())
                        if qtd <= 0:
                            raise ValueError
                        
                        # Verificar se o item já está na fila
                        item_existente = next((x for x in self.fila_impressao if x["codigo"] == item["codigo"]), None)
                        
                        if item_existente:
                            item_existente["quantidade"] += qtd
                        else:
                            self.fila_impressao.append({
                                "codigo": item["codigo"],
                                "descricao": item["descricao"],
                                "referencia": item["referencia"],
                                "quantidade": qtd
                            })
                        adicionados += 1
                        itens_para_remover.append(item)
                    except ValueError:
                        messagebox.showwarning("Aviso", f"Quantidade inválida para o item {item['codigo']}")
                        return
            
            if adicionados == 0:
                messagebox.showwarning("Aviso", "Nenhum item selecionado para adicionar à fila")
                return
            
            # Remover itens adicionados da tela de seleção
            for item in itens_para_remover:
                # Remover widgets do item
                for widget in item["widgets"]:
                    widget.destroy()
                
                # Remover separador se existir (está na linha row_pos+1)
                for widget in self.scrollable_frame.grid_slaves(row=item["row_pos"]+1):
                    if isinstance(widget, ttk.Separator):
                        widget.destroy()
            
            # Atualizar lista de selecionados
            self.selecionados = [item for item in self.selecionados if item not in itens_para_remover]
            
            # Reorganizar a numeração das linhas restantes
            for new_idx, item in enumerate(self.selecionados, start=1):
                new_row = new_idx * 2
                item["row_pos"] = new_row
                for col, widget in enumerate(item["widgets"]):
                    widget.grid(row=new_row, column=col)
                
                # Recolocar separador
                if new_idx < len(self.selecionados):
                    separator = ttk.Separator(self.scrollable_frame, orient='horizontal')
                    separator.grid(row=new_row+1, column=0, columnspan=5, sticky='ew', pady=2)
            
            self.status_bar.config(text=f"{adicionados} itens adicionados à fila de impressão")
            
        except Exception as e:
            error_msg = f"Erro ao adicionar à fila:\n{str(e)}"
            self.log_error(error_msg, e)    

    def mostrar_fila_impressao(self):
        if not self.fila_impressao:
            messagebox.showinfo("Informação", "A fila de impressão está vazia")
            return
        
        # Criar nova janela para a fila de impressão
        janela_fila = tk.Toplevel(self.root)
        janela_fila.title("Fila de Impressão")
        janela_fila.geometry("800x500")
        
        # Frame principal
        frame_principal = tk.Frame(janela_fila)
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview para mostrar a fila
        colunas = ("Código", "Descrição", "Referência", "Quantidade")
        self.tree_fila = ttk.Treeview(frame_principal, columns=colunas, show="headings", selectmode="browse")
        
        for col in colunas:
            self.tree_fila.heading(col, text=col)
            self.tree_fila.column(col, width=150, anchor=tk.W)
        
        self.tree_fila.column("Quantidade", width=80, anchor=tk.CENTER)
        
        # Adicionar itens à treeview
        for item in self.fila_impressao:
            self.tree_fila.insert("", tk.END, values=(
                item["codigo"],
                item["descricao"],
                item["referencia"],
                item["quantidade"]
            ))
        
        self.tree_fila.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Frame de botões
        frame_botoes = tk.Frame(frame_principal)
        frame_botoes.pack(fill=tk.X, pady=5)
        
        # Botão para editar quantidade
        btn_editar = tk.Button(frame_botoes, text="Editar Quantidade", 
                             command=lambda: self.editar_quantidade(janela_fila),
                             font=self.fonte_padrao)
        btn_editar.pack(side=tk.LEFT, padx=5)
        
        # Botão para remover item
        btn_remover = tk.Button(frame_botoes, text="Remover Item", 
                              command=lambda: self.remover_item(janela_fila),
                              font=self.fonte_padrao)
        btn_remover.pack(side=tk.LEFT, padx=5)
        
        # Botão para imprimir
        btn_imprimir = tk.Button(frame_botoes, text="Imprimir Fila", 
                               command=lambda: self.imprimir_fila(janela_fila),
                               font=self.fonte_padrao, bg="#4CAF50", fg="white")
        btn_imprimir.pack(side=tk.RIGHT, padx=5)
        
        # Botão para limpar fila
        btn_limpar = tk.Button(frame_botoes, text="Limpar Fila", 
                             command=lambda: self.limpar_fila(janela_fila),
                             font=self.fonte_padrao, bg="#F44336", fg="white")
        btn_limpar.pack(side=tk.RIGHT, padx=5)
    
    def editar_quantidade(self, janela):
        selecionado = self.tree_fila.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um item para editar")
            return
        
        item = self.tree_fila.item(selecionado)
        valores = item["values"]
        
        # Janela de edição
        janela_edicao = tk.Toplevel(janela)
        janela_edicao.title("Editar Quantidade")
        janela_edicao.geometry("300x150")
        
        tk.Label(janela_edicao, text=f"Editar quantidade para:", font=self.fonte_padrao).pack(pady=5)
        tk.Label(janela_edicao, text=f"{valores[0]} - {valores[1]}", font=self.fonte_padrao).pack(pady=5)
        
        frame_quantidade = tk.Frame(janela_edicao)
        frame_quantidade.pack(pady=10)
        
        tk.Label(frame_quantidade, text="Quantidade:", font=self.fonte_padrao).pack(side=tk.LEFT)
        
        var_qtd = tk.StringVar(value=valores[3])
        entry_qtd = tk.Entry(frame_quantidade, textvariable=var_qtd, width=5, font=self.fonte_padrao)
        entry_qtd.pack(side=tk.LEFT, padx=5)
        
        def salvar_edicao():
            try:
                nova_qtd = int(var_qtd.get())
                if nova_qtd <= 0:
                    raise ValueError
                
                # Atualizar na treeview
                self.tree_fila.item(selecionado, values=(
                    valores[0],
                    valores[1],
                    valores[2],
                    nova_qtd
                ))
                
                # Atualizar na fila de impressão
                for item in self.fila_impressao:
                    if item["codigo"] == valores[0]:
                        item["quantidade"] = nova_qtd
                        break
                
                janela_edicao.destroy()
            except ValueError:
                messagebox.showwarning("Aviso", "Digite uma quantidade válida (número inteiro positivo)")
        
        btn_salvar = tk.Button(janela_edicao, text="Salvar", command=salvar_edicao,
                              font=self.fonte_padrao, bg="#4CAF50", fg="white")
        btn_salvar.pack(pady=10)
    
    def remover_item(self, janela):
        selecionado = self.tree_fila.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um item para remover")
            return
        
        item = self.tree_fila.item(selecionado)
        codigo = item["values"][0]
        
        # Remover da treeview
        self.tree_fila.delete(selecionado)
        
        # Remover da fila de impressão
        self.fila_impressao = [x for x in self.fila_impressao if x["codigo"] != codigo]
        
        if not self.fila_impressao:
            janela.destroy()
    
    def limpar_fila(self, janela):
        if messagebox.askyesno("Confirmar", "Deseja realmente limpar toda a fila de impressão?"):
            self.fila_impressao = []
            janela.destroy()
    
    def imprimir_fila(self, janela):
        if not self.fila_impressao:
            messagebox.showwarning("Aviso", "A fila de impressão está vazia")
            return
        
        try:
            # Preparar lista de etiquetas para impressão
            etiquetas = []
            for item in self.fila_impressao:
                for _ in range(item["quantidade"]):
                    etiquetas.append({
                        "codigo": item["codigo"],
                        "descricao": item["descricao"],
                        "referencia": item.get("referencia", "")
                    })
            
            epl_texto = self.gerar_epl(etiquetas)
            self.imprimir(epl_texto)
            
            # Limpar fila após impressão
            self.fila_impressao = []
            janela.destroy()
            
            self.status_bar.config(text=f"Impressão concluída - {len(etiquetas)} etiquetas enviadas")
            
        except Exception as e:
            error_msg = f"Erro ao imprimir fila:\n{str(e)}"
            self.log_error(error_msg, e)
    
    def formatar_nome(self, nome, referencia):
        nome = nome.strip().replace('\n', ' ') if nome else ""
        referencia = referencia.strip() if referencia else ""
        
        palavras = nome.split()
        linha1 = []
        linha2 = []
        contador = 0
        
        for palavra in palavras:
            if contador + len(palavra) <= 18 and not linha2:
                linha1.append(palavra)
                contador += len(palavra) + 1
            else:
                linha2.append(palavra)
        
        linha1 = ' '.join(linha1)[:18] if linha1 else ""
        linha2 = ' '.join(linha2)[:18] if linha2 else ""
        ref_formatada = referencia[:12] if referencia else ""
        
        return linha1, linha2, ref_formatada
        
    def gerar_epl(self, etiquetas):
        blocos = []
        i = 0
        while i < len(etiquetas):
            item1 = etiquetas[i]
            linha1, linha2, ref1 = self.formatar_nome(item1["descricao"], item1["referencia"])
            cod1 = item1["codigo"]
            
            epl = f"""
N
q720
Q240
S2
D15
B32,16,0,1,3,5,80,B,"{cod1}"
A38,130,0,4,1,1,N,"{linha1}"
A38,155,0,4,1,1,N,"{linha2}"
A38,180,0,4,1,1,N,"{ref1}"
"""
            
            if i + 1 < len(etiquetas):
                item2 = etiquetas[i + 1]
                linha1_2, linha2_2, ref2 = self.formatar_nome(item2["descricao"], item2["referencia"])
                cod2 = item2["codigo"]
                epl += f"""
B388,16,0,1,3,5,80,B,"{cod2}"
A388,130,0,4,1,1,N,"{linha1_2}"
A388,155,0,4,1,1,N,"{linha2_2}"
A388,180,0,4,1,1,N,"{ref2}"
"""
            
            if i + 2 < len(etiquetas):
                item3 = etiquetas[i + 2]
                linha1_3, linha2_3, ref3 = self.formatar_nome(item3["descricao"], item3["referencia"])
                cod3 = item3["codigo"]
                epl += f"""
B744,16,0,1,3,5,80,B,"{cod3}"
A744,130,0,4,1,1,N,"{linha1_3}"
A744,155,0,4,1,1,N,"{linha2_3}"
A744,180,0,4,1,1,N,"{ref3}"
"""
            
            epl += "P1\n"
            blocos.append(epl)
            i += 3
        
        return "".join(blocos)
    
    def imprimir(self, epl_texto):
        try:
            if not self.impressora_etiquetas:
                messagebox.showwarning("Aviso", "Selecione uma impressora primeiro")
                return
                
            hPrinter = win32print.OpenPrinter(self.impressora_etiquetas)
            try:
                hJob = win32print.StartDocPrinter(hPrinter, 1, ("Etiquetas", None, "RAW"))
                try:
                    win32print.StartPagePrinter(hPrinter)
                    win32print.WritePrinter(hPrinter, epl_texto.encode('utf-8'))
                    win32print.EndPagePrinter(hPrinter)
                finally:
                    win32print.EndDocPrinter(hPrinter)
            finally:
                win32print.ClosePrinter(hPrinter)
                
        except Exception as e:
            error_msg = f"Erro ao imprimir:\n{str(e)}"
            self.log_error(error_msg, e)

if __name__ == "__main__":
    root = tk.Tk()
    app = EtiquetasApp(root)
    root.mainloop()