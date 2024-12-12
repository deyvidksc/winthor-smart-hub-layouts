import os
import subprocess
import git

def save_branch_name():
    # Obter o nome da branch
    branch_name = os.environ['GITHUB_HEAD_REF']

    # Criar o arquivo e escrever o nome da branch
    with open('.branch-name.txt', 'w') as f:
        f.write(branch_name)

    # Inicializar o repositório Git
    repo = git.Repo('.')

    # Verificar se houve alterações e commitar/pushar
    if repo.is_dirty():
        repo.git.add('branch-name.txt')
        repo.git.commit(m="Salvar nome da branch no arquivo")
        repo.git.push('origin', 'main')
    else:
        print("Nenhuma alteração no arquivo branch-name.txt, nada para commit.")

# Verificar se o arquivo existe antes de executar o script
if not os.path.isfile('branch-name.txt'):
    print("O arquivo branch-name.txt é necessário para continuar. Abortando.")
    exit(1)

# Executar a função principal
save_branch_name()