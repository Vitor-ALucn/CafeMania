// app.js
const readlineSync = require('readline-sync');
const auth = require('./comandos/auth');
const cliente = require('./comandos/cliente');
const produto = require('./comandos/produto');
const venda = require('./comandos/venda');
const estoque = require('./comandos/estoque');
const relatorio = require('./comandos/relatorio');

let usuarioLogado = null;

// Menu principal após login
const menuPrincipal = async () => { 
  // Verifica se há caixa aberto (não obrigatório para exibição, mas útil)
  console.log('\n' + '='.repeat(50));
  console.log('☕ COFFEEMANAGER - Sistema de Cafeteria (SENAI)');
  console.log('='.repeat(50));
  console.log(`👤 Usuário: ${usuarioLogado.nome} (${usuarioLogado.perfil})`);
  console.log('='.repeat(50));

  console.log('\nEscolha uma opção:');
  console.log('1. 📝 Nova Venda');
  console.log('2. 👤 Clientes');
  console.log('3. 📦 Produtos');
  console.log('4. 🔄 Estoque');
  console.log('5. 📊 Relatórios e Caixa');
  console.log('6. 🚪 Sair da conta');
  console.log('0. ❌ Sair do sistema');

  const op = readlineSync.question('\n> ');

  switch (op) {
    case '1':
      await venda.novo(usuarioLogado.id);
      return menuPrincipal();
    case '2':
      await exibirMenuCliente(cliente);
      return menuPrincipal();
    case '3':
      await produto.menu();
      return menuPrincipal();
    case '4':
      await estoque.menu();
      return menuPrincipal();
    case '5':
      await relatorio.menu(usuarioLogado);
      return menuPrincipal();
    case '6':
      usuarioLogado = null;
      console.log('\n✅ Sessão encerrada.');
      return menuAutenticacao();
    case '0':
      console.log('\n👋 Obrigado por usar o CoffeeManager! Até logo.');
      process.exit(0);
    default:
      console.log('\n⚠️ Opção inválida. Tente novamente.');
      return menuPrincipal();
  }
};

async function exibirMenuCliente(cliente) {
  let opcao;
  do {
    console.clear();
    console.log(`\n=== Bem-vindo(a), ${cliente.nome}! ===`);
    console.log("1. Vendas");
    console.log("2. Produtos");
    console.log("3. Clientes");
    console.log("4. Relatórios");
    console.log("5. Meu Perfil");
    console.log("6. Sair");
    
    opcao = readlineSync.question("\nEscolha uma opção: ");
    
    switch(opcao) {
      case '1':
        await require('./comandos/venda').novo(cliente.id);
        break;
      case '2':
        await require('./comandos/produto').menu(cliente.id);
        break;
      case '3':
        await require('./comandos/cliente').menu(cliente.id);
        break;
      case '4':
        await require('./comandos/relatorio').menu(cliente.id);
        break;
      case '5':
        await require('./comandos/perfil').menu(cliente.id);
        break;
      case '6':
        console.log("Até logo!");
        return;
      default:
        console.log("Opção inválida!");
    }
    
    if (opcao !== '6') {
      readlineSync.question("\nPressione ENTER para continuar...");
    }
  } while (opcao !== '6');
}

// Menu de autenticação (login / cadastro)
const menuAutenticacao = async () => {
  console.log('\n🔐 AUTENTICAÇÃO - CoffeeManager');
  console.log('1. 🔑 Login');
  console.log('2. ✍️ Cadastrar Usuário');
  console.log('0. ❌ Sair');

  const op = readlineSync.question('\n> ');

  if (op === '1') {
    const user = await auth.login();
    if (user) {
      usuarioLogado = user;
      return menuPrincipal();
    }
  } else if (op === '2') {
    await auth.cadastrar();
  } else if (op === '0') {
    console.log('\n👋 Saindo do sistema...');
    process.exit(0);
  } else {
    console.log('\n⚠️ Opção inválida.');
  }

  return menuAutenticacao();
};

// Iniciar sistema
console.log('Bem-vindo ao CoffeeManager – Sistema de Cafeteria via Terminal (SENAI)');
menuAutenticacao();