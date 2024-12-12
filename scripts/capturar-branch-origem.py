import os
import git
import logging

def save_branch_name():
    """Salva o nome da branch atual em um arquivo chamado branch-name.txt"""
     logging.info("acessou save_branch_name")
    # Obtém o nome da branch atual
    repo = git.Repo('.')
    logging.info("repositório: "+repo)
    head = repo.head    
    branch_name = head.name
    logging.info("branch_name: "+branch_name)
    # Cria o arquivo e escreve o nome da branch
    with open('branch-name.txt', 'w') as f:
        f.write(branch_name)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    save_branch_name()
