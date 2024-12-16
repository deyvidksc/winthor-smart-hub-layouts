import os
import json
import git
import sys
import subprocess
from git import Repo

# Função para clonar o repositório
def clone_repo(repo_url, token, local_dir):
    repo_url_with_token = repo_url.replace("https://", f"https://{token}:x-oauth-basic@")
    repo = Repo.clone_from(repo_url_with_token, local_dir)
    return repo


# Função para verificar se há diferenças entre dois branches
def has_diff_between_branches(repo, origin_branch, base_branch,):
    # Acessando os branches remotos explicitamente
    branch1 = f'refs/remotes/origin/{origin_branch}'  # Se for um branch remoto
    branch2 = f'refs/remotes/origin/{base_branch}'  # Se for um branch remoto
    
    # Obtendo os commits de cada branch
    commits1 = list(repo.iter_commits(branch1))
    commits2 = list(repo.iter_commits(branch2))
    
    # Criando sets para facilitar a comparação
    commits1_set = set(commit.hexsha for commit in commits1)
    commits2_set = set(commit.hexsha for commit in commits2)

    # Encontrando commits exclusivos para cada branch
    unique_commits1 = commits1_set - commits2_set
    unique_commits2 = commits2_set - commits1_set

    # Se houver commits exclusivos, significa que há diferenças
    if unique_commits1 or unique_commits2:
        return True

    # Caso não tenha commits exclusivos, comparando as diferenças nos arquivos dos commits
    for commit1 in commits1:
        for commit2 in commits2:
            # Obtendo as diferenças entre os commits
            diffs = commit1.diff(commit2)
            if diffs:
                return True  # Se houver qualquer diferença, retorna True

    return False  # Caso não haja diferenças entre os commits


def get_commit_from_branch(repo, branch_name): 
    """
    Obtém o commit de um branch remoto específico.
    """
    try:
        commit = repo.commit(f'refs/remotes/origin/{branch_name}')
    except Exception as e:
        print(f"Erro ao acessar o commit do branch {branch_name}: {e}")
        raise
    return commit

def prepare_tree_parser(commit): 
    """
    Prepara e retorna a árvore (tree) de um commit.
    """
    return commit.tree

def has_changes_in_directory(repo, origin_branch, base_branch, directory): 
    """
    Verifica se há alterações no diretório especificado entre dois branches.
    
    Parameters:
    - repo: O repositório GitPython.
    - origin_branch: O branch de origem.
    - base_branch: O branch de destino.
    - directory: O diretório a ser comparado.
    
    Retorna:
    - True se houver alterações no diretório, False caso contrário.
    """
    # Obtendo os commits dos branches
    commit_trunk = get_commit_from_branch(repo, origin_branch)
    commit_current = get_commit_from_branch(repo, base_branch)

    # Preparando as árvores dos commits
    old_tree = prepare_tree_parser(commit_trunk)
    new_tree = prepare_tree_parser(commit_current)

    # Comparando os diffs entre os dois commits no diretório especificado
    diffs = repo.git.diff(old_tree, new_tree, '--', directory)

    # Se houver qualquer diferença, retorna True
    return bool(diffs.strip())  # Se a string de diffs não estiver vazia, significa que há diferenças

 
# Função para ler a versão de version.txt
def get_version_from_file():
    version_file_path = 'version.txt'
    if not os.path.exists(version_file_path):
        print(f"Arquivo {version_file_path} não encontrado.")
        return None

    with open(version_file_path, 'r') as file:
        return file.read().strip()

# Função para atualizar o arquivo versao.json com a versão de version.txt
def update_version_json(directory):
    version_file_path = os.path.join(directory, 'versao.json')

    if not os.path.exists(version_file_path):
        print(f"Arquivo versao.json não encontrado em {directory}.")
        return

    with open(version_file_path, 'r') as f:
        data = json.load(f)

    # Obtendo a versão do arquivo version.txt
    versao = get_version_from_file()
    if not versao:
        print("Versão não encontrada no arquivo version.txt.")
        return

    print(f"Versão do arquivo version.txt: {versao}.")
    # Definindo a versão obtida de version.txt no arquivo JSON
    data['versao'] = versao

    # Atualizar o arquivo JSON
    with open(version_file_path, 'w') as f:
        json.dump(data, f, indent=4)

    print(f"Versão atualizada para {versao} no arquivo versao.json em {directory}")
# Função para atualizar o arquivo versao.json
# def update_version_json(directory):
#     version_file_path = os.path.join(directory, 'versao.json')

#     if not os.path.exists(version_file_path):
#         print(f"Arquivo versao.json não encontrado em {directory}.")
#         return

#     with open(version_file_path, 'r') as f:
#         data = json.load(f)

#     # Incrementar a versão
#     current_version = data.get('versao', '1.0.0.0')
#     new_version = increment_version(current_version)
#     data['versao'] = new_version

#     # Atualizar o JSON
#     with open(version_file_path, 'w') as f:
#         json.dump(data, f, indent=4)

#     print(f"Versão atualizada para {new_version} no arquivo versao.json em {directory}")

# # Função para incrementar a versão
# def increment_version(version):
#     version_parts = version.split('.')
#     build = int(version_parts[3])
#     build += 1
#     version_parts[3] = str(build)
#     return '.'.join(version_parts)

# Função para fazer commit e push das alterações
def commit_and_push(repo, branch, token):
    # Adiciona todas as mudanças ao índice
    repo.git.add(update=True) 
    # Realiza o commit
    repo.index.commit("Atualizando a versão no arquivo versao.json")
    # URL do repositório com autenticação via token
    remote_url = f'https://{token}@github.com/deyvidksc/winthor-smart-hub-layouts.git'
    # Acessa o remote
    origin = repo.remotes.origin
    # Configura a URL com o token de autenticação
    origin.set_url(remote_url)
    # Realiza o push para o branch remoto
    origin.push(refspec=f"{branch}:{branch}")



def get_changed_files(base_branch, compare_branch):
    """
    Retorna uma lista de arquivos alterados entre os dois branches.
    """
    command = ["git", "diff", "--name-only", f"{base_branch}...{compare_branch}"]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Erro ao executar git diff: {result.stderr}")
    return result.stdout.splitlines()

def get_folders_to_check():
    """
    Retorna uma lista de todas as pastas do repositório, excluindo as pastas indesejadas.
    """
    # Lista de pastas a serem ignoradas
    excluded_folders = [".github", ".idea", ".version-control", ".git", "target"]
    
    # Obtém todas as pastas no repositório, excluindo as indesejadas
    folders_to_check = []
    for root, dirs, files in os.walk("."):
        # Filtra as pastas indesejadas
        dirs[:] = [d for d in dirs if d not in excluded_folders]
        if root != "." and any(file for file in files):  # Ignora a raiz se não tiver arquivos
            folders_to_check.append(root)
    
    return folders_to_check

def check_changes_in_folders(changed_files, folders_to_check):
    """
    Verifica se houve alterações nas pastas especificadas.
    """
    for file in changed_files:
        for folder in folders_to_check:
            if file.startswith(folder):
                return True
    return False

# Função principal
def main():
    if len(sys.argv) < 4:
        print("Erro: é necessário passar o token, o branch origem e o branch destino.")
        sys.exit(1)

    # Parâmetros
    token = sys.argv[1]
    origin_branch = sys.argv[2]
    base_branch = sys.argv[3]
    repo_url = "https://github.com/deyvidksc/winthor-smart-hub-layouts.git"
    local_folder = "/tmp/git_repo"  # Defina o diretório local onde o repositório será clonado

    # Clonar o repositório
    repo = clone_repo(repo_url, token, local_folder)

    # Verificar diferenças entre os branches
    if has_diff_between_branches(repo, origin_branch, base_branch):
        print(f"O branch '{origin_branch}' tem diferenças em relação ao '{base_branch}'.")
 
        try:               
            # Iterar pelas pastas e atualizar o versao.json
            for dirpath, dirnames, filenames in os.walk(local_folder):
                # Verificando se o diretório contém um arquivo versao.json
                if 'versao.json' in filenames:
                    print(f"Verificando alterações na pasta: {dirpath}")
                    # Verificando se houve alterações no diretório entre os dois branches remotos
                    if has_changes_in_directory(repo, origin_branch, base_branch, dirpath):
                        print(f"Alterações detectadas em: {dirpath}")
                        # Se houver alterações, atualizar o versao.json
                        update_version_json(dirpath)       
        except Exception as e:
            print(f"Erro: {e}")
            sys.exit(1)


        # Fazer commit e push das alterações
        commit_and_push(repo, base_branch, token)
    else:
        print(f"Não há diferenças entre os branches '{origin_branch}' e '{base_branch}'.")

if __name__ == "__main__":
    main()
