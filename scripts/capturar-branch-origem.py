import os
import git
import argparse

def save_branch_name(branch_name):
    """Salva o nome da branch atual em um arquivo chamado branch-name.txt"""
    print("branch_name " + branch_name)    
    
    # Create the file with the branch name
    with open('branch-name.txt', 'w') as f:
    f.write(branch_name)
    
    # Use Git commands (assuming you want to stage the file)
    repo = git.Repo('.')
    repo.index.add(['branch-name.txt'])

if __name__ == "__main__": 
    parser = argparse.ArgumentParser(description='Save branch name to a file')
    parser.add_argument('--branch-name', type=str, required=True, help='The name of the branch')
    args = parser.parse_args()
    save_branch_name(args.branch_name)
