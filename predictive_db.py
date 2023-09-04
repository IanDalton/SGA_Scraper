import pandas as pd
import numpy as np
import os,csv
def add_creditos(carreras,cursos):
    cursos["Creditos"] = 0
    lista = []
    for i in range(len(cursos)):
        ano = int(cursos["Año"][i])
        codigo = cursos["Codigo"][i]
        creditos = carreras.loc[(codigo==carreras["Codigo"])&(ano>=carreras["Desde_Ano"])]["Creditos"]
        if len(creditos)>0:
            creditos = creditos.iloc[0]
        else:
            creditos = None
        cursos["Creditos"][i] = creditos
    
    pass


def get_planes_from_curso(cursos, carreras):
    planes_list = []
    cursos["Planes"] = None
    
    cuatrimestre_map = {"Primer Cuat.": 0, "Segundo Cuat.": 1}
    print(len(cursos))
    for i, row in cursos.iterrows():
        materia = row["Codigo"]
        ano = int(row["Año"])
        cuatrimestre = cuatrimestre_map.get(row["Cuatrimestre"], 2)
        
        # locate all the plans that have that materia and the date is between the start and end date
        planes = carreras[(carreras['Codigo'] == materia) & (carreras['Desde_Ano'] <= ano) & (carreras['Hasta_Ano'] >= ano)]

        planes = list(planes["Plan"].unique())
        planes_list.append(planes)

        
    
    cursos["Planes"] = planes_list

def get_inscriptos_from_previous_years(cursos:pd.DataFrame):
    cuatrimestre_map = {"Primer Cuat.": 0, "Segundo Cuat.": 1}
    def get_previous_year(year:int, cuatrimestre:int):
        if cuatrimestre == 1:
            return year 
        else:
            return year - 1
    def get_previous_cuat(cuatrimestre):
        if cuatrimestre == 0:
            return "Segundo Cuat."
        elif cuatrimestre == 1:
            cuatrimestre = "Primer Cuat."
        return cuatrimestre


    lista_inscriptos_menos_1 = []
    lista_inscriptos_menos_2 = []
    lista_inscriptos_menos_3 = []	
    for i,row in cursos.iterrows():
        year = int(row["Año"])
        cuatrimestre = cuatrimestre_map.get(row["Cuatrimestre"], row["Cuatrimestre"])
        comision = row["Comision"]
        
        year = str(get_previous_year(year,cuatrimestre))
        cuatrimestre = get_previous_cuat(cuatrimestre)

        inscriptos = cursos[(cursos["Codigo"] == row["Codigo"]) & (cursos["Año"] == year) & (cursos["Cuatrimestre"] == cuatrimestre) & (cursos["Comision"] == comision)]["Inscriptos"].values
        lista_inscriptos_menos_1.append(inscriptos[0] if len(inscriptos) > 0 else 0)

        year = str(get_previous_year(int(year),cuatrimestre_map.get(cuatrimestre)))
        cuatrimestre = cuatrimestre_map.get(cuatrimestre, cuatrimestre)
        cuatrimestre = get_previous_cuat(cuatrimestre)

        inscriptos = cursos[(cursos["Codigo"] == row["Codigo"]) & (cursos["Año"] == year) & (cursos["Cuatrimestre"] == cuatrimestre) & (cursos["Comision"] == comision)]["Inscriptos"].values
        lista_inscriptos_menos_2.append(inscriptos[0] if len(inscriptos) > 0 else 0)

        year = str(get_previous_year(int(year),cuatrimestre_map.get(cuatrimestre)))
        cuatrimestre = cuatrimestre_map.get(cuatrimestre, cuatrimestre)
        cuatrimestre = get_previous_cuat(cuatrimestre)

        inscriptos = cursos[(cursos["Codigo"] == row["Codigo"]) & (cursos["Año"] == year) & (cursos["Cuatrimestre"] == cuatrimestre) & (cursos["Comision"] == comision)]["Inscriptos"].values
        lista_inscriptos_menos_3.append(inscriptos[0] if len(inscriptos) > 0 else 0)
    
    cursos["Inscriptos_menos_1"] = lista_inscriptos_menos_1
    cursos["Inscriptos_menos_2"] = lista_inscriptos_menos_2
    cursos["Inscriptos_menos_3"] = lista_inscriptos_menos_3

def get_capacidad_from_previous_years(cursos):
    cuatrimestre_map = {"Primer Cuat.": 0, "Segundo Cuat.": 1}
    def get_previous_year(year:int, cuatrimestre:int):
        if cuatrimestre == 1:
            return year 
        else:
            return year - 1
    def get_previous_cuat(cuatrimestre):
        if cuatrimestre == 0:
            return "Segundo Cuat."
        elif cuatrimestre == 1:
            cuatrimestre = "Primer Cuat."
        return cuatrimestre


    lista_capacidad_menos_1 = []
    lista_capacidad_menos_2 = []
    lista_capacidad_menos_3 = []	
    for i,row in cursos.iterrows():
        year = int(row["Año"])
        cuatrimestre = cuatrimestre_map.get(row["Cuatrimestre"], row["Cuatrimestre"])
        comision = row["Comision"]
        
        year = str(get_previous_year(year,cuatrimestre))
        cuatrimestre = get_previous_cuat(cuatrimestre)

        capacidad = cursos[(cursos["Codigo"] == row["Codigo"]) & (cursos["Año"] == year) & (cursos["Cuatrimestre"] == cuatrimestre) & (cursos["Comision"] == comision)]["Capacidad"].values
        if len(capacidad) > 0:
            capacidad = capacidad[0]
            if capacidad == "Ilimitado":
                capacidad = 9999
        else:
            capacidad = 0
        
        lista_capacidad_menos_1.append(capacidad)

        year = str(get_previous_year(int(year),cuatrimestre_map.get(cuatrimestre)))
        cuatrimestre = cuatrimestre_map.get(cuatrimestre, cuatrimestre)
        cuatrimestre = get_previous_cuat(cuatrimestre)

        capacidad = cursos[(cursos["Codigo"] == row["Codigo"]) & (cursos["Año"] == year) & (cursos["Cuatrimestre"] == cuatrimestre) & (cursos["Comision"] == comision)]["Capacidad"].values
        if len(capacidad) > 0:
            capacidad = capacidad[0]
            if capacidad == "Ilimitado":
                capacidad = 9999
        else:
            capacidad = 0
        
        lista_capacidad_menos_2.append(capacidad)

        year = str(get_previous_year(int(year),cuatrimestre_map.get(cuatrimestre)))
        cuatrimestre = cuatrimestre_map.get(cuatrimestre, cuatrimestre)
        cuatrimestre = get_previous_cuat(cuatrimestre)

        capacidad = cursos[(cursos["Codigo"] == row["Codigo"]) & (cursos["Año"] == year) & (cursos["Cuatrimestre"] == cuatrimestre) & (cursos["Comision"] == comision)]["Capacidad"].values
        if len(capacidad) > 0:
            capacidad = capacidad[0]
            if capacidad == "Ilimitado":
                capacidad = 9999
        else:
            capacidad = 0
        
        lista_capacidad_menos_3.append(capacidad)
    
    cursos["Capacidad_menos_1"] = lista_capacidad_menos_1
    cursos["Capacidad_menos_2"] = lista_capacidad_menos_2
    cursos["Capacidad_menos_3"] = lista_capacidad_menos_3

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



if __name__ == "__main__":
    pass
    