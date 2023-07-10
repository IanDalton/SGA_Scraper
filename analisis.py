import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv,sqlite3
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

    return df


def analize_db(df:pd.DataFrame):
    #check the number of classes per day with a bar chart
       
    # Transform the 'Profesores' column into a long format
    instructors = df[df["Año"]=="2022"].explode('Profesores')['Profesores']
    print(instructors)
    # Count the occurrences of each unique instructor
    instructor_counts = instructors.value_counts()

    # Create a bar chart
    instructor_counts.plot.bar(rot=0)

    # Show the plot
    #plt.show()
    # Transform the 'Horario' column into a long format
    schedules = df.explode('Horario')['Horario']

    # Extract the day of the week from each tuple
    days = schedules.apply(lambda x: x[0])
    print(days)

    # Count the occurrences of each unique day
    day_counts = days.value_counts()

    # Create a bar chart
    #day_counts.plot.bar(rot=0)

    # Show the plot
    #plt.show()
    # Transform the 'Horario' column into a long format
    # Transform the 'Horario' column into a long format
    schedules = df.explode('Horario')

    # Extract the day of the week from each tuple
    schedules['day'] = schedules['Horario'].apply(lambda x: x[0])
    print(schedules)
    # Group the rows by year and day of the week and compute the size of each group
    year_day_counts = schedules.groupby(['Año', 'day']).size()

    # Reshape the resulting Series into a DataFrame
    year_day_counts = year_day_counts.unstack(level='day')

    # Sort the columns of the DataFrame by decreasing quantity for each year
    year_day_counts = year_day_counts.apply(lambda x: x.sort_values(ascending=True), axis=1)

    # Create a stacked bar chart
    year_day_counts.plot.bar(stacked=False, rot=0)
    print(year_day_counts)

    # Show the plot
    #plt.show()

    #check the number of classes per hour
    #check the number of classes per aula
    #check the number of classes per profesor
    #check the number of classes per materia

    pass



if __name__ == "__main__":
    with open("dataset.csv","r",encoding="utf-8") as f:
        reader = csv.DictReader(f)
        data = list(reader)
        db = clean_db(data)
    print(db)
    
    analize_db(db)
