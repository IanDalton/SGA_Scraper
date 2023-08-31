import pandas as pd
import numpy as np
import os,csv
def generate_db(cursos:pd.DataFrame = None,carreras:pd.DataFrame = None):

    def clean_carreras(carreras):
        #group by plan and show the carrera and desde y hasta
        carreras = carreras.groupby(["Plan","Carrera"],as_index=False).agg({"Desde":"min","Hasta":"max"})
        print(carreras)
    def filtro(df,df2,output):
        codigo = df["Codigo"]

    #filter carreras
    

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
    print(cursos)
    print(carreras)
    #print the carreras that has the materia 11.32 
    print(carreras[carreras["Codigo"].str.contains("12.67")]["Plan"])

    # for each curso, add it to a new db and add the plan to the db
    """ cursos["Planes"] = cursos.apply(lambda x: list(carreras[carreras["Codigo"].str.contains(x)]["Plan"]))
    cursos["Carreras"] = cursos["Codigo"].apply(lambda x: list(carreras[carreras["Codigo"].str.contains(x)]["Carrera"]))
    cursos["Correlativas"] = cursos["Codigo"].apply(lambda x: list(carreras[carreras["Codigo"].str.contains(x)]["Correlativas"]))
    cursos["Creditos"] = cursos["Codigo"].apply(lambda x: list(carreras[carreras["Codigo"].str.contains(x)]["Creditos"]))
    cursos["Creditos Requeridos"] = cursos["Codigo"].apply(lambda x: list(carreras[carreras["Codigo"].str.contains(x)]["Creditos Requeridos"])) """
    

    print(cursos)

if __name__ == "__main__":
    generate_db()
    