☕ Coffeemanager - Sistema de Cafeteria CLI

Sistema de gerenciamento completo para cafeterias desenvolvido em linha de comando (CLI) com Node.js e MySQL. Projeto acadêmico focado em operações essenciais de uma cafeteria: vendas, controle de estoque, gestão de clientes e relatórios financeiros.

⚙️ Requisitos de Sistema

Node.js v14+
XAMPP 8.0+ (para servidor Apache e MySQL integrados)
MySQL Workbench 8.0+ (para gerenciamento visual do banco de dados)
Sistema Operacional: Windows, Linux ou macOS (testado em Windows 10/11)

📥 Instalação

1 Pré-requisitos (Configuração do Banco de Dados)
 1. Configure o XAMPP:
 2. Inicie o painel de controle do XAMPP
 3. Inicie os módulos MySQL
"Verifique se o MySQL está rodando na porta 3306"

Clone o repositório:

git clone https://github.com/seuusuario/cafeteria-cli.git
cd cafeteria-cli

Instale as dependências:

npm install readline-sync mysql2

🗂️ Estrutura do Projeto

cafeteria-cli/
├── app.js                  # Arquivo principal - ponto de entrada
├── db.js                   # Conexão com o banco de dados MySQL
├── estrutura.sql           # Script SQL para criar a estrutura do banco
├── package.json            # Dependências e scripts do projeto
├── utils/
│   └── caixa.js            # Utilitários para gestão de caixa
└── comandos/
    ├── auth.js             # Sistema de autenticação
    ├── venda.js            # Gestão de vendas

▶️ Como Usar
1 - Inicie o XAMPP:
 Abra o painel de controle do XAMPP
 Certifique-se de que os serviços Apache e MySQL estão em execução
2 - Inicie o sistema
 "node app.js" no terminal do prompt de comando do Windows
3 - Crie um login com suas preferências.
4 - Caso de certo essa é a interface:
   --- 📊 RELATÓRIOS E CAIXA ---
   1. 💰 Abrir Caixa
   2. 📉 Fechar Caixa e Gerar Relatório
   3. 📈 Vendas do Dia
   4. ⚠️ Alertas (Estoque e Validade)
   0. 🔙 Voltar

Dentro desse reposotório esta a documentação completo do código.
