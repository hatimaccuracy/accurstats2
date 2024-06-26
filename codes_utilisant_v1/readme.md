# Codes utilisant Accur'Stats v1

### XSLXtoAccur

Input: Prend des fichiers en format tabulaires suivantes CSV, XLS, XLSX (sheet 1), les rends compatible avec l'entrée d'AccurStats v1 <br />

Output: Renvoie deux fichiers target_NOM_DE_FICHIER_INPUT.csv qui contient les dates et la target uniquement (série à expliquer), n_target_NOM_DE_FICHIER_INPUT.csv qui contient les dates et les drivers uniquement  <br />

Utilisation: Poser tous les fichiers tabulaires à exploiter dans le répértoire input, le programme renvoie les fichiers .csv à faire digerer par Accur'Stats dans le répertoire output puis déplace le fichier initial à done <br />

### AccurSCREENtoGraphs

Prétraitement: Notre base de données et divisée en deux (training et test), chaqu'un des fichiers subit un traitement par XSLXtoAccur, à la fin on obtient target_testing, n_target_testing et target_training, n_target_training, on renomme target_testing -> oo et n_target_testing -> n_oo et on execute Accur'Stats sur n_target_training et target_training. <br />

Input: Prend le fichier screening renvoyé par Accur'Stats->Selection de modele, et les différents fichiers en traitement. <br />

Output: Renvoie des graphes et un fichier new_screening.xslx qui trie les différents modèles par $R^2_{oos}$. <br />

Utilisation: Poser tous les fichiers mentionnés (voir exemple) dans le répértoire input_graphs, LANCER R2OOS.py, puis lancer le script script_graphs_metrics.py. Le fichier new_screening.xslx est dans le dossier input_graphs. <br />

Exemple de résultats:

![model6_accur](https://github.com/hatimaccuracy/accurstats2/assets/173388521/b7e6622a-18c0-46ad-a07e-22039232a3ab)
