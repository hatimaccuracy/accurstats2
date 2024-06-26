import pandas as pd
from pathlib import Path


supported_extensions = ['.csv', '.xls', '.xlsx']
in_folder = Path("input")

#### Execution sur tout les fichiers dans le répértoire input
for file in in_folder.iterdir():

    #### Indication et extraction du nom du fichier
    print("Traitement du fichier: ", end="")
    print(file)
    filename = str(file)[6:].split('.')[0]
    extension = file.suffix

    #### Verification d'extension tabulaire
    if extension not in supported_extensions:

        print('Attention! Fichier non supporté')
        print(file.suffix)

    else:
        #### Paramètres spécifiques aux fichiers csv demandés aux utilisateurs
        if extension ==".csv":
            delimiter = input("Veuillez specifier la délimitation: ")
            dec = input("Veuillez specifier la délimitation décimale (, ou .): ")
            data = pd.read_csv(file, delimiter=delimiter, decimal = dec)

        else:
            data = pd.read_excel(file)
        #### Extraction et affichage des noms des features
        columns = data.columns
        print("Features:")
        for i in range(len(columns)):
            print(str(i) + ":" + columns[i])

        #### Extraction du target de la part de l'utilisateur
        flag = False
        while(not flag):
            try:
                target_index = int(input("Saisir numéro target:"))
                if (target_index<len(columns)):
                    flag = True
            except:
                print("Mauvaise entrée, ressayer...")
        target = columns[target_index]

        #### Extraction de column des dates et conversion en format compatible avec AccurStats
        flag_d = False
        try:
            data[columns[0]] = pd.to_datetime( data[columns[0]], dayfirst=True)
            data[columns[0]] = data[columns[0]].dt.strftime('%d/%m/%Y')
        except:
            flag_d = True
            date_column = int(input("Entrez indice de dates:"))
            data[columns[date_column]] =pd.to_datetime(data[columns[date_column]], dayfirst=True)
            data[columns[date_column]] = data[columns[date_column]].dt.strftime('%Y/%m/%d')
        if (not flag_d):
            date_column = 0

        #### Determination des non_targets
        non_targets = []
        for l in range(len(columns)):
            if l == date_column or l == target_index:
                continue
            else:
                non_targets.append(columns[l])
        non_targets.insert(0,columns[date_column])
        #### Cleaning de data, dans ce script, il faut que dans une ligne, TOUT LES COLUMNS AIT UNE VALEUR DEFINIE...
        # data.dropna(subset=[target], inplace= True)

        data.dropna(inplace=True)


        #### Export du fichier target et fichier non_target
        target_out_name = 'output/target_'+filename+'.csv'
        data[[columns[date_column], target]].to_csv(target_out_name, index=False,sep=';', decimal =',')
        non_target_out_name = 'output/n_target_' + filename + '.csv'
        data[non_targets].to_csv(non_target_out_name, index=False,sep=';', decimal=',')
        file.rename(Path('done')/file.name)


