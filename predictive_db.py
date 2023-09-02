import pandas as pd
import numpy as np
import os,csv
def clean_carreras(carreras):
    #group by plan and show the carrera and desde y hasta
    carreras_agrupadas = carreras.groupby(["Plan","Carrera"],as_index=False).agg({"Desde_Ano":"min","Desde_Cuatri":"min","Hasta_Ano":"max","Hasta_Cuatri":"max"})

    #sort by plan and desde index 1
    carreras_agrupadas = carreras_agrupadas.sort_values(by = ["Plan","Desde_Ano","Desde_Cuatri"],ascending = True).reset_index(drop=True)
    #if they have the same desde and hasta, decrease desde by one year

    for i in range(1,len(carreras_agrupadas)):
        if carreras_agrupadas.loc[i,"Desde_Ano"] == carreras_agrupadas.loc[i-1,"Desde_Ano"] and carreras_agrupadas.loc[i,"Desde_Cuatri"] == carreras_agrupadas.loc[i-1,"Desde_Cuatri"]:
            carreras_agrupadas.loc[i,"Desde_Ano"] = str(int(carreras_agrupadas.loc[i,"Desde_Ano"]) - 1)

    # if they have the same carrera check if there is a newer plan and make the end of the previus plan the start of the new one
    for i in range(1,len(carreras_agrupadas)):
        if carreras_agrupadas.loc[i,"Carrera"] == carreras_agrupadas.loc[i-1,"Carrera"] and carreras_agrupadas.loc[i,"Plan"] != carreras_agrupadas.loc[i-1,"Plan"]:
            
            carreras_agrupadas.loc[i-1,"Hasta_Ano"] = carreras_agrupadas.loc[i,"Desde_Ano"]
            carreras_agrupadas.loc[i-1,"Hasta_Cuatri"] = carreras_agrupadas.loc[i,"Desde_Cuatri"]
    
    #change if Primer Cuatrimestre is 0, Segundo Cuatrimestre is 1, else is 2
    carreras_agrupadas["Desde_Cuatri"] = carreras_agrupadas["Desde_Cuatri"].apply(lambda x: 0 if x == "Primer Cuat." else 1 if x == "Segundo Cuat." else 2)
    carreras_agrupadas["Hasta_Cuatri"] = carreras_agrupadas["Hasta_Cuatri"].apply(lambda x: 0 if x == "Primer Cuat." else 1 if x == "Segundo Cuat." else 2)
    

    #Change all desdes and hastas in the original db
    for i in range(len(carreras)):
        plan = carreras.loc[i,"Plan"]
        desde_ano = carreras_agrupadas[(carreras_agrupadas["Plan"] == plan)]["Desde_Ano"].values[0]
        desde_cuatri = carreras_agrupadas[(carreras_agrupadas["Plan"] == plan)]["Desde_Cuatri"].values[0]
        hasta_ano = carreras_agrupadas[(carreras_agrupadas["Plan"] == plan)]["Hasta_Ano"].values[0]
        hasta_cuatri = carreras_agrupadas[(carreras_agrupadas["Plan"] == plan)]["Hasta_Cuatri"].values[0]
        carreras.loc[i,"Desde_Ano"] = int(desde_ano)
        carreras.loc[i,"Desde_Cuatri"] = int(desde_cuatri)
        carreras.loc[i,"Hasta_Ano"] = int(hasta_ano) if hasta_ano else 9999
        carreras.loc[i,"Hasta_Cuatri"] = int(hasta_cuatri) if hasta_cuatri else 9999           

def generate_db(cursos:pd.DataFrame = None,carreras:pd.DataFrame = None):

   
    # Get the data
    if not cursos:
        with open("./data/cursos.csv","r",encoding="utf-8") as f:
            reader = csv.DictReader(f)
            cursos = list(reader)
        cursos = pd.DataFrame(cursos)
    if not carreras:
        with open("./data/carreras.csv","r",encoding="utf-8") as f:
            reader = csv.DictReader(f)
            carreras = list(reader)
        carreras = pd.DataFrame(carreras)
    
    clean_carreras(carreras)
    
    cursos["Planes"] = cursos.apply(get_cursos,args=(carreras,))

    

    # for each curso, add it to a new db and add the plan to the db
    """ cursos["Planes"] = cursos.apply(lambda x: list(carreras[carreras["Codigo"].str.contains(x)]["Plan"]))
    cursos["Carreras"] = cursos["Codigo"].apply(lambda x: list(carreras[carreras["Codigo"].str.contains(x)]["Carrera"]))
    cursos["Correlativas"] = cursos["Codigo"].apply(lambda x: list(carreras[carreras["Codigo"].str.contains(x)]["Correlativas"]))
    cursos["Creditos"] = cursos["Codigo"].apply(lambda x: list(carreras[carreras["Codigo"].str.contains(x)]["Creditos"]))
    cursos["Creditos Requeridos"] = cursos["Codigo"].apply(lambda x: list(carreras[carreras["Codigo"].str.contains(x)]["Creditos Requeridos"])) """
    

    print(cursos)

if __name__ == "__main__":
    generate_db()
    