import pandas as pd
import numpy as np
import requests
from dateutil.parser import parse
import streamlit as st

url = 'https://loto.akroweb.fr/loto-historique-tirages'
html = requests.get(url).content
df_list = pd.read_html(html)
data = df_list[0][[2, 4, 5, 6, 7, 8, 9]]
colnames = ['date_txt', 'boule_1', 'boule_2', 'boule_3', 'boule_4', 'boule_5', 'chance']
data.columns = colnames

data['date_txt'] = data['date_txt'].str.replace('janvier','january')
data['date_txt'] = data['date_txt'].str.replace('fevrier','february')
data['date_txt'] = data['date_txt'].str.replace('mars','march')
data['date_txt'] = data['date_txt'].str.replace('avril','april')
data['date_txt'] = data['date_txt'].str.replace('mai','may')
data['date_txt'] = data['date_txt'].str.replace('juin','june')
data['date_txt'] = data['date_txt'].str.replace('juillet','july')
data['date_txt'] = data['date_txt'].str.replace('aout','august')
data['date_txt'] = data['date_txt'].str.replace('septembre','september')
data['date_txt'] = data['date_txt'].str.replace('octobre','october')
data['date_txt'] = data['date_txt'].str.replace('novembre','november')
data['date_txt'] = data['date_txt'].str.replace('decembre','december')

data['tirage_liste'] = data[['boule_1', 'boule_2', 'boule_3', 'boule_4', 'boule_5']].values.tolist()

data['date'] = ''
for i in range (0, len(data)):
    data['date'][i] = parse(data['date_txt'][i]).strftime('%d/%m/%Y')

data = data[['date','boule_1', 'boule_2', 'boule_3', 'boule_4', 'boule_5', 'tirage_liste', 'chance']]

data_duplicated = data[data.duplicated(subset=['tirage_liste'], keep = False)].sort_values('tirage_liste')


# Comptage des boules
num_list = list(range(1, 50))
comptage = pd.DataFrame(0, columns= ['comptage'], index=num_list)

# Parcourir chaque tirage
for _, row in data.iterrows():
    # Récupérer les numéros du tirage
    tirage = row[['boule_1', 'boule_2', 'boule_3', 'boule_4', 'boule_5']].values
    
    # Compter le nombre de tirage de chaque boule
    for i in range(len(tirage)):
        comptage.at[tirage[i], 'comptage'] += 1

comptage['num_boule'] = comptage.index
comptage['num_boule'] = comptage['num_boule'].astype(str)

top5 = comptage.sort_values('comptage', ascending=False).head(5)
top5['rank'] = top5['comptage'].rank(method='min', ascending=False)
top5 = top5[['rank', 'num_boule', 'comptage']]

flop5 = comptage.sort_values('comptage', ascending=True).head(5)
flop5['rank'] = flop5['comptage'].rank(method = 'min', ascending= True)
flop5 = flop5[['rank', 'num_boule', 'comptage']]

# Duos

# Initialiser une matrice de co-occurrence
co_occurrence_matrix = pd.DataFrame(0, index=num_list, columns=num_list)

# Parcourir chaque tirage
for _, row in data.iterrows():
    # Récupérer les numéros du tirage
    tirage = row[['boule_1', 'boule_2', 'boule_3', 'boule_4', 'boule_5']].values
    
    # Ajouter les co-occurrences dans la matrice
    for i in range(len(tirage)):
        for j in range(i + 1, len(tirage)):  # Éviter les doublons (i, j) et (j, i)
            co_occurrence_matrix.at[tirage[i], tirage[j]] += 1
            co_occurrence_matrix.at[tirage[j], tirage[i]] += 1

duos = pd.DataFrame(columns= ['duos','comptage'])

n = 0
for i in range(1,50):
    for j in range(1,50):
        if i < j:
            duos.loc[n,'duos'] = str(i)+"-"+str(j)
            duos.loc[n,'comptage'] = co_occurrence_matrix.at[i,j]
            n += 1

topduos = duos.sort_values('comptage', ascending=False).head(5)
topduos['rank'] = topduos['comptage'].rank(method = 'min', ascending= False)
topduos = topduos[['rank', 'duos', 'comptage']]

flopduos = duos.sort_values('comptage', ascending=True).head(5)
flopduos['rank'] = flopduos['comptage'].rank(method = 'min', ascending= True)
flopduos = flopduos[['rank', 'duos', 'comptage']]




st.sidebar.title("Sommaire")

pages = ["Statistiques du loto", "Résultat d'une grille"]

page = st.sidebar.radio("Aller vers la page :", pages)


if page == pages[0] :

    
    st.title('Statistiques du loto')
    
    st.write("Les résultats des tirage du loto est du hasard mais cela ne va pas dire que chaque numéro sera tiré autant de fois que son voisin.")
    st.write("")

    st.write("Nous allons voir que certains numéros sont plus fréquents que d'autres, et il en va de même pour les duos")



    st.header("Top et Flop des numéros tirés")


    col1, col2 = st.columns(2)
    
    with col1:
        st.write(top5.to_html(), unsafe_allow_html=True,
                 hide_index=True)
        
    with col2:
        st.write(flop5.to_html(), unsafe_allow_html=True, 
                 hide_index=True)
        
    st.write("Le premier de la classe est le numéro 41 alors qu'arrive bon dernier le numéro 39.")
    

    st.header("Top et Flop des duos")

    col3, col4 = st.columns(2)
    
    with col3:
        st.write(topduos.to_html(), unsafe_allow_html=True,
                 hide_index=True)
        
    with col4:
        st.write(flopduos.to_html(), unsafe_allow_html=True,
                 hide_index=True)
    
    st.write("Pour les duos, le couple phare est le 7-11 alors que les couple 10-42 et 5-8 ne sont pas très appréciés")


    st.write("Une remarque pour la boule numéro 3 qui est dans le top 3 avec la boule numéro 13 mais dans les derniers avec la boule numéro 21")



if page == pages[1] : 

    st.title("Résultat d'une grille")

    st.write("")
    st.write("Choisissez 5 numéros et le numéro chance pour voir vos résulats depuis le 06/10/2008")
    
    st.write("")

    boules = []
    boule_compl = []
    for i in range(1,50):
        boules.append(i)
    
    for i in range(1,11):
        boule_compl.append(i)
    

    tirage = st.multiselect(
    "Choisissez vos 5 numéros", boules, [6,20,22,34,19],
    max_selections = 5)
    tirage.sort()

    num_chance = st.select_slider(
    "Numéro Chance", boule_compl, 5)


           
    data['tirage'] = 0
    data['num_chance'] = 0
    for i in range (0, len(data)):
        data['tirage'][i] = len(set(tirage) & set(data['tirage_liste'][i]))
    data.loc[data['chance'] == num_chance, 'num_chance'] = 1


    data['resultat'] = 'Pas de résultat'
    data.loc[(data['tirage'] == 5) & (data['num_chance'] == 1) , 'resultat'] = "5 numéros + complementaire"
    data.loc[(data['tirage'] == 5) & (data['num_chance'] == 0) , 'resultat'] = "5 numéros"
    data.loc[(data['tirage'] == 4) & (data['num_chance'] == 1) , 'resultat'] = "4 numéros + complementaire"
    data.loc[(data['tirage'] == 4) & (data['num_chance'] == 0) , 'resultat'] = "4 numéros"
    data.loc[(data['tirage'] == 3) & (data['num_chance'] == 1) , 'resultat'] = "3 numéros + complementaire"
    data.loc[(data['tirage'] == 3) & (data['num_chance'] == 0) , 'resultat'] = "3 numéros"
    data.loc[(data['tirage'] == 2) & (data['num_chance'] == 1) , 'resultat'] = "2 numéros + complementaire"
    data.loc[(data['tirage'] == 2) & (data['num_chance'] == 0) , 'resultat'] = "2 numéros"
    data.loc[(data['tirage'] == 1) & (data['num_chance'] == 1) , 'resultat'] = "1 numéro + complementaire"
    data.loc[(data['tirage'] == 0) & (data['num_chance'] == 1) , 'resultat'] = "0 numéro + complémentaire"

    data['achat'] = 2.2
    data['montant'] = 0
    
    data.loc[(data['tirage'] == 5) & (data['num_chance'] == 1) , 'montant'] = 2000000
    data.loc[(data['tirage'] == 5) & (data['num_chance'] == 0) , 'montant'] = 13000
    data.loc[(data['tirage'] == 4) & (data['num_chance'] == 1) , 'montant'] = 360
    data.loc[(data['tirage'] == 4) & (data['num_chance'] == 0) , 'montant'] = 130
    data.loc[(data['tirage'] == 3) & (data['num_chance'] == 1) , 'montant'] = 26
    data.loc[(data['tirage'] == 3) & (data['num_chance'] == 0) , 'montant'] = 10
    data.loc[(data['tirage'] == 2) & (data['num_chance'] == 1) , 'montant'] = 7.5
    data.loc[(data['tirage'] == 2) & (data['num_chance'] == 0) , 'montant'] = 3.1
    data.loc[(data['tirage'] == 1) & (data['num_chance'] == 1) , 'montant'] = 2.2
    data.loc[(data['tirage'] == 0) & (data['num_chance'] == 1) , 'montant'] = 2.2

    data['resultat'].value_counts()

    for i in range(1,6):
        print("Nombre de tirage avec ",i," boule: ",len(data.loc[data['tirage']== i]))

    data = data[['date','boule_1', 'boule_2', 'boule_3', 'boule_4', 'boule_5', 'tirage_liste',
             'chance', 'tirage', 'resultat', 'achat', 'montant']]
    
    data['montant €'] = data['montant'].map("{:,.0f}".format)
    
    st.write("Palmarès de ces boules")

    count_result = pd.DataFrame(data['resultat'].value_counts().reset_index(name= 'comptage'))



    st.write(count_result.to_html(), unsafe_allow_html=True,)




    st.write("Tirages avec au moins 4 boules trouvées")

    st.write(
        data.loc[data['tirage']>= 4][['date','tirage_liste', 'chance', 'resultat', 'montant €']].to_html(), unsafe_allow_html=True,
        hide_index=True)
    
    cout_achat = data['achat'].sum()
    gain = data['montant'].sum()
    result_total = (data['montant'].sum()- data['achat'].sum())

    
    st.write(f"Cout d'achat: {cout_achat:,.0f} €")
    st.write(f"Gains: {gain:,.0f} €")
    st.write(f"Resultat: {result_total:,.0f} €")

    st.write("")

    st.write("Le calcul du coût est de 2.20€ par grille et le calcul des gains est fait avec ce tableau")

    file_image = r'resultat.jpg'
    st.image(file_image, caption= "Grille résultat")


   

    
    















 
