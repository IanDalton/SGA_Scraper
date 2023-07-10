import json,csv

with open("dataset.json","r") as f:
    dataset = json.load(f)

with open("dataset.csv","w",encoding="utf-8",newline="") as f:
    writer = csv.writer(f)
    headers = ["Año","Cuatrimestre","Materia","Comision","Horario","Profesores","Inscriptos"]
    writer.writerow(headers)
    todos:dict
    for ano,todos in dataset.items():
        for cuatrimestre,materias in todos.items():
            for materia,comisiones in materias.items():
                for comision, datos in comisiones.items():
                    writer.writerow([ano,cuatrimestre,materia,comision,datos["horario"],datos["profesores"],datos["inscriptos"]])
