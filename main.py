import os,csv
from analisis import clean_db
if not os.path.isfile("./data/dataset1.csv"):
    import extract

    extract.extract_sga_classes(year_min=2023)
    extract.turn_sga_into_csv()

with open("./data/dataset.csv","r",encoding="utf-8") as f:
    reader = csv.DictReader(f)
    data = list(reader)

clean_db(data)




