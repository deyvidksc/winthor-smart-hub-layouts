import os
import git

def save_branch_name():
    """Salva o nome da branch atual em um arquivo chamado branch-name.txt"""

    # Obtém o nome da branch atual
    repo = git.Repo('.')
    branch_name = repo.active_branch.name

    # Cria o arquivo e escreve o nome da branch
    with open('branch-name.txt', 'w') as f:
        f.write(branch_name)

if __name__ == "__main__":
    save_branch_name()
