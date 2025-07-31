"""
Sistema Bancário Simples

Este módulo implementa um sistema bancário simples com cadastro de clientes, contas correntes,
operações de depósito, saque, extrato e controle de transações diárias. O sistema utiliza
programação orientada a objetos e registra logs das operações realizadas.

Principais classes:
- Cliente, PessoaFisica
- Conta, ContaCorrente
- Historico, Transacao, Saque, Deposito
- ContasIterador

Principais funções:
- depositar, sacar, exibir_extrato, criar_cliente, criar_conta, listar_contas
- menu, filtrar_cliente, recuperar_conta_cliente, validar_cpf, input_int, input_float

Autor: Paulo
Data: 2025
"""

import textwrap
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime

LIMITE_TRANSACOES_DIA = 2


class ContasIterador:
    """
    Iterador personalizado para exibir contas formatadas.
    """

    def __init__(self, contas):
        self.contas = contas
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self.contas):
            raise StopIteration
        conta = self.contas[self._index]
        self._index += 1
        return f"""Agência:\t{conta.agencia}
Número:\t\t{conta.numero}
Titular:\t{conta.cliente.nome}
Saldo:\t\tR$ {conta.saldo:.2f}
"""


class Cliente:
    """
    Representa um cliente do banco.
    """

    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []
        self.indice_conta = 0

    def realizar_transacao(self, conta, transacao):
        """
        Executa uma transação na conta, respeitando o limite diário.
        """
        if len(conta.historico.transacoes_do_dia()) >= LIMITE_TRANSACOES_DIA:
            print("\n@@@ Você excedeu o número de transações permitidas para hoje! @@@")
            return
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        """
        Adiciona uma conta ao cliente.
        """
        self.contas.append(conta)


class PessoaFisica(Cliente):
    """
    Representa uma pessoa física, herda de Cliente.
    """

    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf


class Conta:
    """
    Classe base para contas bancárias.
    """

    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        """
        Cria uma nova conta para o cliente.
        """
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        """
        Realiza um saque, validando saldo e valor.
        """
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("\n@@@ Operação falhou! Você não tem saldo suficiente. @@@")

        elif valor > 0:
            self._saldo -= valor
            print("\n=== Saque realizado com sucesso! ===")
            return True

        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")

        return False

    def depositar(self, valor):
        """
        Realiza um depósito, validando valor.
        """
        if valor > 0:
            self._saldo += valor
            print("\n=== Depósito realizado com sucesso! ===")
        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False

        return True


class ContaCorrente(Conta):
    """
    Especialização de Conta para contas correntes.
    """

    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    @classmethod
    def nova_conta(cls, cliente, numero, limite, limite_saques):
        """
        Cria uma nova conta corrente.
        """
        return cls(numero, cliente, limite, limite_saques)

    def sacar(self, valor):
        """
        Realiza saque considerando limites específicos.
        """
        numero_saques = len(
            [
                transacao
                for transacao in self.historico.transacoes
                if transacao["tipo"] == Saque.__name__
            ]
        )

        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite:
            print("\n@@@ Operação falhou! O valor do saque excede o limite. @@@")

        elif excedeu_saques:
            print("\n@@@ Operação falhou! Número máximo de saques excedido. @@@")

        else:
            return super().sacar(valor)

        return False

    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """


class Historico:
    """
    Gerencia o histórico de transações de uma conta.
    """

    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        """
        Adiciona uma transação ao histórico.
        """
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )

    def gerar_relatorio(self, tipo_transacao=None):
        """
        Gera relatório filtrado por tipo de transação.
        """
        for transacao in self._transacoes:
            if (
                tipo_transacao is None
                or transacao["tipo"].lower() == tipo_transacao.lower()
            ):
                yield transacao

    def transacoes_do_dia(self):
        """
        Retorna transações realizadas no dia atual.
        """
        data_atual = datetime.utcnow().date()
        transacoes = []
        for transacao in self._transacoes:
            data_transacao = datetime.strptime(
                transacao["data"], "%d-%m-%Y %H:%M:%S"
            ).date()
            if data_atual == data_transacao:
                transacoes.append(transacao)
        return transacoes


class Transacao(ABC):
    """
    Classe abstrata para transações bancárias.
    """

    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    """
    Implementação de transação de saque.
    """

    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    """
    Implementação de transação de depósito.
    """

    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


def log_transacao(func):
    """
    Decorador para registrar logs das operações em arquivo.
    """

    def envelope(*args, **kwargs):
        resultado = func(*args, **kwargs)
        with open("transacoes.log", "a") as log_file:
            log_file.write(
                f"{datetime.now()}: {func.__name__.upper()} - args: {args}, kwargs: {kwargs}\n"
            )
        return resultado

    return envelope


def menu():
    """
    Exibe o menu principal do sistema e retorna a opção escolhida.
    """

    menu = """\n
    ================ MENU ================
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova conta
    [lc]\tListar contas
    [nu]\tNovo usuário
    [q]\tSair
    => """
    return input(textwrap.dedent(menu))


def filtrar_cliente(cpf, clientes):
    """
    Busca um cliente pelo CPF.
    """

    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None


def recuperar_conta_cliente(cliente):
    """
    Permite ao usuário selecionar uma conta do cliente.
    """

    if not cliente.contas:
        print("\n@@@ Cliente não possui conta! @@@")
        return

    print("\nSelecione a conta:")
    for i, conta in enumerate(cliente.contas, start=1):
        print(f"[{i}] Agência: {conta.agencia}, Número: {conta.numero}")

    opcao = input_int("Digite o número da conta: ") - 1  # Usando input_int para evitar exceção
    if 0 <= opcao < len(cliente.contas):
        return cliente.contas[opcao]
    else:
        print("\n@@@ Opção inválida! @@@")
        return


def input_int(msg):
    """
    Entrada segura de número inteiro.
    """

    while True:
        try:
            return int(input(msg))
        except ValueError:
            print("\n@@@ Entrada inválida! Digite um número inteiro. @@@")


def input_float(msg):
    """
    Entrada segura de número float positivo.
    """

    while True:
        try:
            valor = float(input(msg))
            if valor <= 0:
                print("\n@@@ O valor deve ser positivo. @@@")
                continue
            return valor
        except ValueError:
            print("\n@@@ Entrada inválida! Digite um número válido. @@@")


@log_transacao
def depositar(clientes):
    """
    Realiza operação de depósito para um cliente.
    """

    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    valor = input_float("Informe o valor do depósito: ")  # Use input_float aqui
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


@log_transacao
def sacar(clientes):
    """
    Realiza operação de saque para um cliente.
    """

    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    valor = input_float("Informe o valor do saque: ")
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


@log_transacao
def exibir_extrato(clientes):
    """
    Exibe o extrato de uma conta do cliente.
    """

    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n================ EXTRATO ================")
    extrato = ""
    tem_transacao = False
    for transacao in conta.historico.gerar_relatorio():
        tem_transacao = True
        extrato += f"\n{transacao['data']}\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}"

    if not tem_transacao:
        extrato = "Não foram realizadas movimentações"

    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("==========================================")


@log_transacao
def criar_cliente(clientes):
    """
    Cadastra um novo cliente, validando CPF e duplicidade.
    """

    cpf = input("Informe o CPF (somente número): ")
    if not validar_cpf(cpf):
        print("\n@@@ CPF inválido! @@@")
        return
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\n@@@ Já existe cliente com esse CPF! @@@")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input(
        "Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): "
    )

    cliente = PessoaFisica(
        nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco
    )

    clientes.append(cliente)

    print("\n=== Cliente criado com sucesso! ===")


@log_transacao
def criar_conta(numero_conta, clientes, contas):
    """
    Cria uma nova conta corrente para um cliente existente.
    Permite ao usuário configurar o limite de saques diários ou usar o padrão.
    """

    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado, fluxo de criação de conta encerrado! @@@")
        return

    try:
        limite = float(input("Informe o limite de saque (padrão 500): ") or 500)
    except ValueError:
        print("\n@@@ Limite inválido, usando padrão 500. @@@")
        limite = 500

    try:
        limite_saques = int(input("Informe o limite de saques diários (padrão 3): ") or 3)
    except ValueError:
        print("\n@@@ Limite de saques inválido, usando padrão 3. @@@")
        limite_saques = 3

    conta = ContaCorrente.nova_conta(
        cliente=cliente, numero=numero_conta, limite=limite, limite_saques=limite_saques
    )
    contas.append(conta)
    cliente.contas.append(conta)

    print("\n=== Conta criada com sucesso! ===")


def listar_contas(contas):
    """
    Exibe todas as contas cadastradas.
    """

    for conta in ContasIterador(contas):
        print("=" * 100)
        print(textwrap.dedent(str(conta)))


def validar_cpf(cpf):
    """
    Valida o CPF:
    - Deve conter 11 dígitos numéricos.
    - Não pode ser uma sequência repetida.
    - Valida dígitos verificadores conforme algoritmo oficial.
    """
    if not (cpf.isdigit() and len(cpf) == 11):
        return False
    if cpf == cpf[0] * 11:
        return False

    # Validação dos dígitos verificadores
    def calc_digito(cpf, peso):
        soma = sum(int(digito) * (peso - idx) for idx, digito in enumerate(cpf[:peso-1]))
        resto = (soma * 10) % 11
        return '0' if resto == 10 else str(resto)

    digito1 = calc_digito(cpf, 10)
    digito2 = calc_digito(cpf, 11)
    return cpf[-2:] == digito1 + digito2


def main():
    """
    Função principal que executa o loop do sistema bancário.
    """

    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            depositar(clientes)

        elif opcao == "s":
            sacar(clientes)

        elif opcao == "e":
            exibir_extrato(clientes)

        elif opcao == "nu":
            criar_cliente(clientes)

        elif opcao == "nc":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "q":
            break

        else:
            print(
                "\n@@@ Operação inválida, por favor selecione novamente a operação desejada. @@@"
            )


if __name__ == "__main__":
    main()