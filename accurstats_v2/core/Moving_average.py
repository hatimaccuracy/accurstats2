import pandas as pd
import numpy as np

class Moving_average:
    def __init__(self , ordre_sup, ordre_inf , coeff):
        self.ordre_sup = ordre_sup
        self.ordre_inf = ordre_inf
        self.coeff = coeff

    def __str__(self):
        phrase = "Cette moyenne mobile est d'ordre " + str(self.ordre_sup - self.ordre_inf +1) + " , et de coefficient " + str(self.coeff)
        return phrase

    # Fonction multipliant deux moyenne mobile
    def difference(self , other):
        return


