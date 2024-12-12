import os
import git
import logging

def save_branch_name(branch_name):
    """Salva o nome da branch atual em um arquivo chamado branch-name.txt"""
    # Obtém o nome da branch atual
    #repo = git.Repo('.')
    
    #head = repo.head    
    #branch_name = head.name
    print("branch_name " + branch_name)    

#branch_name = repo.active_branch.name
#print(f"A branch atual é: {branch_name}")
    
    # Cria o arquivo e escreve o nome da branch
    with open('branch-name.txt', 'w') as f:
        f.write(branch_name)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    save_branch_name(branch_name)
