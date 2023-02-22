import datetime
import os
from typing import Iterable
from git import Repo
import numpy as np
from model import Author, Folder
from tqdm import tqdm

PATH_REPO = "../tabnews.com.br"

base_repo = Repo(PATH_REPO)

#Recupera a branch atual do projeto
head = base_repo.active_branch

#Esse array vai aramazenar todas as pastas e subpastas do projeto e suas alterações
folderList: Iterable[Folder] = []
#Esse array vai aramazenar todos os autores do projeto e suas alterações
authors = []

#Recupera a lista de commits do projeto em ordem reversa para começar do commit mais antigo
commit_list = reversed(list(base_repo.iter_commits(head)))

#Recupera o total de commits para mostrar o progresso
total_commits = len(list(base_repo.iter_commits(head)))

#Contador para eventualmente limitar o loop
count = 0

#Ultimo commit para comparar com o atual
latest_commit = None

# Utilitario para recuperar o nome das pastas
def get_names_from_path(path):
    names = []
    while path != "":
        path, name = os.path.split(path)
        # If as extension
        if name.find(".") == -1:
            names.append(name)
    return names

# Função responsavel por atualizar os dados do autor, você pode ler ela depois para entender melhor
def update_author_data(author, email,  commit, authors_param: Iterable[Author]):
    if len(authors_param) == 0:
        new_author = Author(author, email)
        new_author.add_change(commit.stats.total["insertions"], commit.stats.total["deletions"], commit.stats.total["files"], commit.stats.total["lines"], commit.committed_datetime)
        authors_param.append(new_author)

    author_exists = False
    for author_saved in authors_param:
        if author_saved.name == author and author_saved.email == email:
            author_saved.add_change(commit.stats.total["insertions"], commit.stats.total["deletions"], commit.stats.total["files"], commit.stats.total["lines"], commit.committed_datetime)
            author_exists = True

    if not author_exists:
        new_author = Author(author, email)
        new_author.add_change(commit.stats.total["insertions"], commit.stats.total["deletions"], commit.stats.total["files"], commit.stats.total["lines"], commit.committed_datetime)
        authors_param.append(new_author)

# Data de inicio do processo           
datetime_start = datetime.datetime.now()



print("Starting time", datetime_start)
# Loop para percorrer todos os commits
for commit in tqdm(commit_list, desc="Progress: ", colour="blue", total=total_commits, ncols = 100):
    #Limitador de commits caso o projeto seja muito grande
    if count == 1000:
        pass
        #break
    #Identifica o autor do commit e atualiza os dados dele
    update_author_data(commit.committer.name,commit.committer.email, commit, authors)

    #Verifica se o commit atual é o primeiro commit do projeto, se for o priemiro commit, significa que todos os arquivos foram adicionados, então não é necessário fazer a comparação com o commit anterior.
    if latest_commit is not None:
        #Recupera a diferença entre o commit atual e o commit anterior
        diff = latest_commit.diff(commit)
        #Percorre a diferença para atualizar os dados das pastas
        for file in diff:
            #Recupera o nome das pastas do arquivo
            folderThree  = get_names_from_path(file.a_path)
            #Recupera a pasta raiz do arquivo
            fileFolder = folderThree[0] if len(folderThree) > 0 else None
            #Percorre as pastas para atualizar os dados
            for index, folder in enumerate(folderThree):
                for folderAppended in folderList:
                    #Verifica se a pasta já existe na lista de pastas
                    if folderAppended.name == folder:
                        #Se a pasta ja existe, adiciona o contador de alterações
                        folderAppended.count_change()
                        #Verifica o tipo de alteração do arquivo
                        if file.change_type == "A":
                            #Se o arquivo foi adicionado, adiciona o arquivo na pasta e adiciona o contador de alterações da pasta
                            folderAppended.count_change()
                            folderAppended.add_file(file.a_path)
                        elif file.change_type == "D":
                            #Se o arquivo foi deletado, remove o arquivo da pasta e adiciona o contador de alterações da pasta
                            folderAppended.count_change()
                            folderAppended.remove_file(file.a_path)
                        elif file.change_type == "M":
                            #Se o arquivo foi modificado, adiciona o contador de alterações do arquivo
                            folderAppended.count_file_change(file.a_path)
                            folderAppended.count_change()
                        elif file.change_type == "R":
                            #Se o arquivo foi renomeado, remove o arquivo da pasta e adiciona o contador de alterações da pasta
                            folderAppended.remove_file(file.b_path)
                            folderAppended.add_file(file.a_path)
                            folderAppended.count_change()
                        elif file.change_type == "T":
                            folderAppended.count_change()
                            folderAppended.remove_file(file.b_path)
                            folderAppended.add_file(file.a_path)
                        break
                else:
                    #Se a pasta não existe, cria uma nova pasta e adiciona na lista de pastas
                    newFolder = Folder(folder,  folderThree[index + 1] if index + 1 < len(folderThree) else None)
                    newFolder.count_change()
                    if file.change_type == "A":
                        newFolder.add_file(file.a_path)
                    folderList.append(newFolder)
    else:
        #Se o commit atual for o primeiro commit, adiciona todos os arquivos na lista de pastas
        for file in commit.stats.files:
            folderThree  = get_names_from_path(file)
            fileFolder = folderThree[0] if len(folderThree) > 0 else None
            for index, folder in enumerate(folderThree):
                newFolder = Folder(folder,  folderThree[index + 1] if index + 1 < len(folderThree) else None)
                newFolder.count_change()
                newFolder.add_file(file)
                folderList.append(newFolder)
            
    count += 1
    #Atualiza o commit anterior
    latest_commit = commit


print("Finish time", datetime.datetime.now())
print("Total time", datetime.datetime.now() - datetime_start)

#Apartir daqui já temos a lista de pastas com os dados atualizados, agora manipular os dados para gerar o gráfico

#Remove as pastas que começam com ponto, pois são pastas ocultas, aqui tambem poderiamos remover pastas sem arquivos e alterações
folderList = [folder for folder in folderList if folder.name[0] != "."]
#Cria um array com todas as alterações de cada pasta
fodler_series = [folder.times_changed for folder in folderList]
#Cria um array com o nome de cada pasta
folder_names = [f'Folder: {folder.parent if folder.parent is not None else ""}/{folder.name} | Changes: {folder.times_changed}' for folder in folderList]
#Cria um array aleatório para posicionar as bolhas no gráfico
x = [random.uniform(0, len(folder_names)*count) for i in range(len(folder_names))]
y = [random.uniform(0, len(folder_names)*count) for i in range(len(folder_names))]


#Cria um array com o nome de cada autor
authors_data_set_names = [f'Author: {author.name} | Changes: {author.times_changed}' for author in authors]
#Cria um array aleatório para posicionar as bolhas no gráfico
x_author = [random.uniform(0, len(folder_names)*count) for i in range(len(authors_data_set_names))]
y_author = [random.uniform(0, len(folder_names)*count) for i in range(len(authors_data_set_names))]
#Cria um array com todas as alterações de cada autor
s_author = [author.times_changed for author in authors]

#Esses dados são posicionais, ou seja o primeiro valor do array de alterações se refere ao primeiro valor do array de nomes


#Coloquei os imports aqui para não poluir o código acima que é o código principal e o mais importante
import random
import matplotlib.pyplot as plt
import mpld3 as mpld3
from mpld3 import plugins
import matplotlib.colors as mcolors


#Você não precisa entender esse código, ele é apenas para evitar que as bolhas se sobreponham, mas se quiser se aventurar, fique a vontade
def colision_detect(x, y, n, series):
    collision = True
    while collision:
        collision = False
        for i in range(n):
            for j in range(i + 1, n):
                d = np.sqrt((x[i] - x[j])**2 + (y[i] - y[j])**2)
                if d < series[i] + series[j]:
                #collision = True
                # ajuste de posição da bolha
                    x[i] += np.sign(x[j] - x[i]) * series[i] * 0.1
                    y[i] += np.sign(y[j] - y[i]) * series[i] * 0.1
    return x, y





#Cria o gráfico com 2 colunas e 1 linha
fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(20, 20))
alphas = np.clip(fodler_series, 100, 20) / 100


#Chama a função para evitar que as bolhas se sobreponham, embora o algoritmo de detecção de colisão não seja tão eficiente pois não tem recursividade, ao menos deixa o gráfico mais bonito
colision_detect(x, y, len(folder_names), fodler_series)
colision_detect(x_author, y_author, len(s_author), s_author)

#Gera cores aleatórias para as bolhas do grafico de pastas                
colors = []
for i in range(len(folder_names)):
    r, g, b = np.random.rand(3)
    colors.append(mcolors.to_hex((r, g, b)))


#Cria as bolhas no gráfico
scatter = ax[0].scatter(x, y, s=fodler_series, alpha=alphas, c=colors)
scatter2 = ax[1].scatter(x_author, y_author, s=s_author, alpha=alphas)

#Cria o tooltip para cada bolha
tooltip = plugins.PointHTMLTooltip(scatter, folder_names)
tooltip2 = plugins.PointHTMLTooltip(scatter2, authors_data_set_names)
plugins.connect(fig, tooltip)
plugins.connect(fig, tooltip2)

ax[0].set_axis_off()
ax[0].set_title('Repository insights: Changes in folders')
ax[1].set_title('Repository insights: Changes in authors')
ax[1].set_axis_off()

#Salva o gráfico em um arquivo html
mpld3.save_html(fig, "index.html")
#Mostra o gráfico no navegador
mpld3.show(fig)




