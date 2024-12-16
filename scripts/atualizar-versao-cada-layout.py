import os
import json
import git
import sys
from git import Repo

# Função para clonar o repositório
def clone_repo(repo_url, token, local_dir):
    repo_url_with_token = repo_url.replace("https://", f"https://{token}:x-oauth-basic@")
    repo = Repo.clone_from(repo_url_with_token, local_dir)
    return repo

# Função para verificar se há diferenças entre dois branches
def has_diff_between_branches(repo, trunk_branch, current_branch):
    # Acessando os branches remotos explicitamente
    branch1 = f'refs/remotes/origin/{trunk_branch}'  # Se for um branch remoto
    branch2 = f'refs/remotes/origin/{current_branch}'  # Se for um branch remoto
    
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
    
    
    
def has_changes_in_directory(repo, trunk_branch, current_branch, directory):
    # Acessando os branches remotos diretamente
    branch_trunk = f'refs/remotes/origin/{trunk_branch}'
    branch_current = f'refs/remotes/origin/{current_branch}'

    # Obtendo os commits dos branches remotos
    commit_trunk = repo.commit(branch_trunk)
    commit_current = repo.commit(branch_current)

    # Obtendo a diferença entre os dois commits para o diretório especificado
    diffs = commit_trunk.diff(commit_current, paths=directory)

    # Se houver qualquer diferença, retorna True (alterações encontradas)
    return len(diffs) > 0
    
 
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

# Função principal
def main():
    if len(sys.argv) < 4:
        print("Erro: é necessário passar o token, o branch origem e o branch destino.")
        sys.exit(1)

    # Parâmetros
    token = sys.argv[1]
    trunk_branch = sys.argv[2]
    current_branch = sys.argv[3]
    repo_url = "https://github.com/deyvidksc/winthor-smart-hub-layouts.git"
    local_folder = "/tmp/git_repo"  # Defina o diretório local onde o repositório será clonado

    # Clonar o repositório
    repo = clone_repo(repo_url, token, local_folder)

    # Verificar diferenças entre os branches
    if has_diff_between_branches(repo, trunk_branch, current_branch):
        print(f"O branch '{current_branch}' tem diferenças em relação ao '{trunk_branch}'.")

        # Iterar pelas pastas e atualizar o versao.json
        for dirpath, dirnames, filenames in os.walk(local_folder):
            # Verificando se o diretório contém um arquivo versao.json
            if 'versao.json' in filenames:
                print(f"Verificando alterações na pasta: {dirpath}")
                # Verificando se houve alterações no diretório entre os dois branches remotos
                if has_changes_in_directory(repo, trunk_branch, current_branch, dirpath):
                    print(f"Alterações detectadas em: {dirpath}")
                    # Se houver alterações, atualizar o versao.json
                    update_version_json(dirpath)

        # Fazer commit e push das alterações
        commit_and_push(repo, current_branch, token)
    else:
        print(f"Não há diferenças entre os branches '{trunk_branch}' e '{current_branch}'.")

if __name__ == "__main__":
    main()
