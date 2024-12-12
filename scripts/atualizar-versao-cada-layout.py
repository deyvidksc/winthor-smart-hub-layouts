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

# # Função para verificar se há diferenças entre dois branches
# def has_diff_between_branches(repo, trunk_branch, current_branch):
#     # Tente acessar os branches remotos explicitamente
#     branch1 = f'refs/remotes/origin/{trunk_branch}'  # Se for um branch remoto
#     branch2 = f'refs/remotes/origin/{current_branch}'  # Se for um branch remoto
    
#     commit1 = repo.commit(branch1)
#     commit2 = repo.commit(branch2)

#     # Obter o diff entre os dois commits
#     diffs = commit1.diff(commit2)
#     return len(diffs) > 0  # Retorna True se houver diferenças

# Função para verificar se há diferenças entre dois branches
def has_diff_between_branches(repo, trunk_branch, current_branch):
    # Obtém o commit de cada branch
    branch1 = f'refs/remotes/origin/{trunk_branch}'  # Se for um branch remoto
    branch2 = f'refs/remotes/origin/{current_branch}'  # Se for um branch remoto

    # Cria um objeto para comparar os commits
    diff = repo.git.diff(branch1_commit.hexsha, branch2_commit.hexsha)

    # Se houver diferenças entre os dois commits, o diff não será vazio
    return bool(diff)


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
            if 'versao.json' in filenames:
                print(f"Alterando versao.json na pasta: {dirpath}")
                update_version_json(dirpath)

        # Fazer commit e push das alterações
        commit_and_push(repo, current_branch, token)
    else:
        print(f"Não há diferenças entre os branches '{trunk_branch}' e '{current_branch}'.")

if __name__ == "__main__":
    main()
