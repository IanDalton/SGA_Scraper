import pandas as pd
import csv
from datetime import datetime

def clean_db(df:pd.DataFrame):

    if type(df) != pd.DataFrame:
        df = pd.DataFrame(df)

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
            else:
                lista_horarios = horario[0].split(" ")
                dia = lista_horarios[0]
                inicio = lista_horarios[1]
                fin = lista_horarios[3]
                del lista_horarios
                horario[0] = (dia,inicio,fin)



            horarios[i] = horario
        
        return horarios

    df["Horario"]= df["Horario"].apply(clean_horario)

    #check the size of the dataframe in bytes
    #print(df.memory_usage(deep=True).sum()) #7832688 - 6539160 = 1293528 bytes of difference between tuple and list. that is 1.2 MB


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

    def get_inscriptos(inscriptos):
        inscriptos = inscriptos.split(" / ")
        return int(inscriptos[0])
    def get_available_spaces(inscriptos):
        inscriptos = inscriptos.split(" / ")
        return inscriptos[1]

    def get_creditos(horarios):
        creditos = 0

        for horario in horarios:
            if horario[0] == None:
                continue
            inicio = horario[1]
            fin = horario[2]
            inicio = datetime.strptime(inicio, '%H:%M')
            fin = datetime.strptime(fin, '%H:%M')
            horario = (fin - inicio).seconds / 3600
            creditos += horario
        
        return round(creditos)
    df["Capacidad"] = df["Inscriptos"].apply(get_available_spaces)
    df["Inscriptos"] = df["Inscriptos"].apply(get_inscriptos)
    df["Codigo"] = df["Materia"].apply(lambda x: x.split(" - ")[0])
    df["Materia"] = df["Materia"].apply(lambda x: x.split(" - ")[1])
    #df["Horario"] = df["Horario"].apply(format_horario)
    #df["Creditos"] = df["Horario"].apply(get_creditos)
    
    
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

def get_credits_done_in_year(db:pd.DataFrame,year:int):
    #It excludes the classes that are not the standard 1,3,6,9 credits
    #get the total inscriptos in that year
    db = db[db["Creditos"].isin([1,3,6,9])]
  
    # Get the total number of studens and credits per year
    year_totals = db[db["Año"]==str(year)].groupby("Creditos")[["Inscriptos"]].sum()

    # Plot the total number of credits
    year_totals.plot.bar(rot=0)
    #plt.show()
    # multiply the credits by the number of students
    year_totals["Creditos"] = year_totals.index

    tt = year_totals["Creditos"].apply(lambda x: year_totals[year_totals["Creditos"]==x]["Inscriptos"].sum()*x )
 
    return tt.sum()




if __name__ == "__main__":
    with open("./data/dataset.csv","r",encoding="utf-8") as f:
        reader = csv.DictReader(f)
        data = list(reader)
    db = clean_db(data)

    #print(db["Materia"])

    """ res = get_credits_done_in_year(db,2022)
    print(res) """
    #analize_db(db)
