import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv
from datetime import datetime

def clean_db(data:list):

    df = pd.DataFrame(data)

    #turn profesores from str to list
    df["Profesores"] = df["Profesores"].apply(lambda x: x[1:-1].split(","))

    def clean_profesores(profesores):
        profs = []
        nombre = ""
        texto:str
        for texto in profesores:
            # Remove the first and last character, excluding spaces
            texto = texto.strip()
            texto = texto[1:-1]
            #check if the string has \n
            cadena = texto.split("\\n")
            #if it doesnt it is probably a surname
            if len(cadena) == 1:
                nombre += cadena[0]
            else:
                #if it does, it is probably a name + a surname with another person
                nombre += cadena[0]
                profs.append(nombre)
                #reset the name to the surname of the other person
                nombre = cadena[1]

        return profs

    df["Profesores"] = df["Profesores"].apply(clean_profesores)

    def clean_horario(horario):
        #split before the text "Aula"
        horarios = horario.split("\n")
        for i,horario in enumerate(horarios):
            #split on the first "Aula" or "Sin"

            horario = horario.split("Aula",1)

            if len(horario) == 1:
                horario = horario[0].split("Sin",1)
                if len(horario) != 1:
                    horario[1] = None
            horarios[i] = horario
        return horarios

    df["Horario"]= df["Horario"].apply(clean_horario)

    #check the size of the dataframe in bytes
    print(df.memory_usage(deep=True).sum()) #7832688 - 6539160 = 1293528 bytes of difference between tuple and list. that is 1.2 MB


    def format_horario(horarios):
        #the first element in the list is a string with the day and the time to end. The format is %D %H:%M - %H:%M
        #the second element is the aula


        for i,horario in enumerate(horarios):
            if len(horario) != 1:
                horario, aula = horario
                horario = horario.split("-")
                horario[0] = horario[0].strip()
                horario_end = horario[1].strip()
                dia, horario_start = horario[0].split(" ")
                
                horarios[i] = (dia,horario_start,horario_end,aula)
            else:
                horarios[i] = (None,None,None,None)
        return horarios

                
    df["Horario"] = df["Horario"].apply(format_horario)

    print(df["Horario"])



    # Disclaimer! if the cuatrimestre is unknown the date witll be on december
    print(df)

if __name__ == "__main__":
    with open("dataset.csv","r",encoding="utf-8") as f:
        reader = csv.DictReader(f)
        data = list(reader)
        clean_db(data)