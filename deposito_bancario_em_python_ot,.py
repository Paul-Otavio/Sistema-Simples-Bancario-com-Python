menu = """
[d] Depositar
[s] Sacar
[e] Extrato
[q] Sair

=> """

saldo = 0
limite = 500
extrato = ""
numero_saques = 0
LIMITE_SAQUES = 3

def exibir_mensagem(mensagem):
    print(f"\n{mensagem}\n")

while True:
    opcao = input(menu)

    if opcao == "d":
        valor = float(input("Informe o valor do depósito: "))
        if valor > 0:
            saldo += valor
            extrato += f"Depósito: R$ {valor:.2f}\n"
            exibir_mensagem("Depósito realizado com sucesso!")
        else:
            exibir_mensagem("Operação falhou! O valor informado é inválido.")
    
    elif opcao == "s":
        valor = float(input("Informe o valor do saque: "))

        if valor <= 0:
            exibir_mensagem("Operação falhou! O valor informado é inválido.")
        elif valor > saldo:
            exibir_mensagem("Operação falhou! Você não possui saldo suficiente.")
        elif valor > limite:
            exibir_mensagem("Operação falhou! O valor do saque excedeu o limite.")
        elif numero_saques >= LIMITE_SAQUES:
            exibir_mensagem("Operação falhou! Número de saques excedido.")
        else:
            saldo -= valor
            extrato += f"Saque: R$ {valor:.2f}\n"
            numero_saques += 1
            exibir_mensagem("Saque realizado com sucesso!")
    
    elif opcao == "e":
        exibir_mensagem("============= EXTRATO ==============")
        print("Não foram realizadas movimentações." if not extrato else extrato)
        print(f"\nSaldo: R$ {saldo:.2f}")
        exibir_mensagem("===================================")
    
    elif opcao == "q":
        exibir_mensagem("Saindo do sistema. Até logo!")
        break

    else:
        exibir_mensagem("Operação inválida, por favor selecione uma opção válida.")