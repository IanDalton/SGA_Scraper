from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import os,csv,json,time,datetime,sys
from analisis import clean_db
from dotenv import load_dotenv
import pandas as pd

def login():
    load_dotenv()

    # CONFIGURATIONS
    url = 'https://sga.itba.edu.ar'
    username = os.getenv("ITBA_USERNAME")
    password = os.getenv("ITBA_PASSWORD")

    username_selector = 'user'
    password_selector = 'password'
    submit_selector = 'login'

    # Create a new instance of the Chrome driver
    driver = webdriver.Edge()

    # Navigate to the login page
    driver.get(url)

    # Find the username, password, and submit elements
    username_element = driver.find_element(By.NAME, username_selector)
    password_element = driver.find_element(By.NAME, password_selector)
    submit_element = driver.find_element(By.NAME, submit_selector)

    # Enter the username and password
    username_element.send_keys(username)
    password_element.send_keys(password)

    # Click the submit button to log in
    submit_element.click()

    # Wait for the page to load
    driver.implicitly_wait(5)

    return driver

def extract_sga_classes(year_min=2010,year_max=datetime.datetime.now().year,save=True):
    
    driver = login()

    dataset = {}
    def get_info_on_page(links,year):
        # create a dictionary for the year
        if dataset.get(year) == None:
            dataset[year] = {}
        for url in links:
            #Get the name of the materia and the cuatrimestre
            datos = {}
            driver.get(url)
            materia = driver.find_element(By.XPATH,"//*[@id='content']/div[3]/div/div[1]/label").text
            cuatrimestre = driver.find_element(By.XPATH,"//*[@id='content']/div[3]/div/div[3]/div[2]/span[1]").text
            departamento = driver.find_element(By.XPATH,"//*[@id='content']/div[3]/div/div[2]/label").text

            # create a dictionary for the cuatrimestre
            if dataset[year].get(cuatrimestre) == None:
                dataset[year][cuatrimestre] = {}
            #Click on the link that has the span inside that has the text "Comisiones"
            driver.find_element(By.CLASS_NAME,"tab1").click()

            #from the table extract all elements and save it in a dictionary
            tabla = driver.find_element(By.TAG_NAME,"tbody")

            # extract the data from the table into a dictionary
            for clases in tabla.find_elements(By.TAG_NAME,"tr"):
                cells = clases.find_elements(By.TAG_NAME,"td")
                datos[cells[0].text] = {
                    "horario":cells[1].text,
                    "profesores":cells[2].text.split(','),
                    "inscriptos":cells[3].text,
                    "departamento":departamento
                }
            # add the dictionary to the dataset
            dataset[year][cuatrimestre][materia] = datos

    
    for year in range(year_min,year_max+1):
        #Click into cursos
        next_link = 1
        driver.find_element(By.XPATH,"//*[@id='content']/div[1]/div/div/div/ul/li[3]/a").click()
        driver.find_element(By.XPATH,"//*[@id='content']/div[1]/div/div/div/ul/li[3]/ul/li[3]/a").click()
        print(year)
        options = driver.find_elements(By.CLASS_NAME,"filter-td")

        # Set the cuatrimestre into all
        period = options[4]
        period.click()
        period.find_elements(By.TAG_NAME,"option")[0].click()
        #set current year as the year to search by typing it in the input
        search_year = options[5].find_element(By.TAG_NAME,"input")
        search_year.clear()
        search_year.click()
        search_year.send_keys(str(year))

        # Update the filter
        options[11].find_elements(By.TAG_NAME,"a")[0].click()

        # wait for the page to load
        time.sleep(0.5)

        # Do until the next button is disabled
        while next_link:
            try:
                next_link = driver.find_element(By.CLASS_NAME,"next").get_attribute("href")
            except:
                next_link = None
            table = driver.find_element(By.TAG_NAME,"tbody")
            rows = table.find_elements(By.TAG_NAME,"tr")



            urls = []
            # Get all the urls from the table
            for row in rows:
                cells = row.find_elements(By.TAG_NAME,"td")
                urls.append(cells[len(cells)-1].find_element(By.TAG_NAME,"a").get_attribute("href"))
            # Extract the info from the urls
            get_info_on_page(urls, year)

            # Go to the next page
            if next_link:
                driver.get(next_link)

    driver.quit()

    if save:
        #save the data in a json file
        with open("./data/dataset.json","w",encoding="utf-8") as f:
            json.dump(dataset,f)
    else: 
        return dataset

    # Quit the driver when you are done
    
def extract_sga_carreras(save = True,debug = False):

    # Logs into the sga
    driver = login()


    #Click into cursos
    driver.find_element(By.XPATH,"//*[@id='content']/div[1]/div/div/div/ul/li[3]/a").click()
    driver.find_element(By.XPATH,"//*[@id='content']/div[1]/div/div/div/ul/li[3]/ul/li[2]/a").click()
    
    #get all carreras in from the table and saves the link
    carreras = dict()
    table = driver.find_element(By.TAG_NAME,"tbody")
    for row in table.find_elements(By.TAG_NAME,"tr"):
        cells = row.find_elements(By.TAG_NAME,"td")
        carreras[cells[0].text] = {"Nombre":cells[1].text,
                                   "Escuela":cells[2].text,
                                   "Nivel":cells[3].text,
                                   "URL":cells[5].find_element(By.TAG_NAME,"a").get_attribute("href")}
        

    #For each carrera I access the URL and delete it as the URL changes every time
    for carrera in carreras.values():
        
        driver.get(carrera["URL"])
        carrera["URL"] = None
        carrera["Planes"] = dict()
        #Get all study plans
        table = driver.find_element(By.TAG_NAME,"tbody")
        for row in table.find_elements(By.TAG_NAME,"tr"):
            cells = row.find_elements(By.TAG_NAME,"td")
            carrera["Planes"][cells[0].text] = {"Desde":cells[2].text,
                                                    "Hasta":cells[3].text,
                                                    "URL":cells[4].find_element(By.TAG_NAME,"a").get_attribute("href")}
            
        #For each study plan
        for plan in carrera["Planes"].values():
            driver.get(plan["URL"])
            plan["Materias"] = dict()
            # get all the tables from the page
            # The tables may or may not have a sub table
            driver.implicitly_wait(0)
            tables = driver.find_elements(By.TAG_NAME,"table")
            print(len(tables))
            registered_tables = set()
            for table in tables[:-1]: #Las table is for certifications
                
                # Check if I have alredy seen the table as find elements gets me all the tables on the page
                # This differ between pages so I cant create a standard solution
                # Plus this works... Feel free to change it.


                if table.id not in registered_tables:
                    registered_tables.add(table.id)
                    #highlight the table if debug is enabled
                    driver.execute_script("arguments[0].style.border='3px solid red'", table) if debug else None
                    titulos = table.find_element(By.TAG_NAME,"Thead").find_elements(By.TAG_NAME,"span")
                    titulos = [titulo.text for titulo in titulos[1:]]
                    
                    titulo_plan = titulos[0]

                    plan["Materias"][titulo_plan] = {"Subtitulos":titulos[1:],"Datos":dict()}
                    table = table.find_element(By.TAG_NAME,"tbody")
                    for sub_table in table.find_elements(By.TAG_NAME,"table"):
                        registered_tables.add(sub_table.id)
                        
                        driver.execute_script("arguments[0].style.border='3px solid blue'", sub_table) if debug else None
                        sub_table = sub_table.find_element(By.TAG_NAME,"tbody")
                        
                        for row in sub_table.find_elements(By.TAG_NAME,"tr"):
                            cells = row.find_elements(By.TAG_NAME,"td")
                            id_materia = cells[0].text.split(" - ")[0]

                            materia = dict()
                            plan["Materias"][titulo_plan]["Datos"][id_materia] = materia
                            
                            materia["Nombre"] = cells[0].text.split(" - ")[1] if len(cells[0].text.split(" - ")) != 1 else None
                            materia["Creditos"] = cells[1].text

                            #Check if is a required in order to move foward table or a materia table.
                            # It filters out the blank spaces that the SGA adds needlessly 
                            if len(cells) == 4:
                                materia["Creditos requeridos"] = cells[2].text
                                materia["Correlativas"] = list(filter(lambda text: text != "",cells[3].text.split(" ")))
                            else:
                                materia["Correlativas"] = list(filter(lambda text: text != "",cells[2].text.split(" ")))

                    


            #get 

    if save:
        #save the data in a json file
        with open("./data/carreras.json","w",encoding="utf-8") as f:
            json.dump(carreras,f)
    else: 
        return carreras




    pass

def turn_carreras_into_csv(dataset:dict = None):
    if not dataset:
        with open("./data/carreras.json","r",encoding="utf-8") as f:
            dataset = json.load(f)

    with open("./data/carreras.csv","w",encoding="utf-8",newline="") as f:
        writer = csv.writer(f)
        headers = ["Carrera","Plan","Desde_Cuatri","Desde_Ano","Hasta_Cuatri","Hasta_Ano","Tipo","Codigo","Materia","Creditos","Creditos Requeridos","Correlativas"]
        writer.writerow(headers)
        planes:dict
        materia:dict
        for carrera,planes in dataset.items():
            for plan,tipos in planes.get("Planes").items():
                for tipo,materias in tipos.get("Materias").items():
                    for codigo, materia in materias.get("Datos").items():
                        desde = tipos.get("Desde")
                        if desde:
                            desde = desde.split(" ")
                            if len(desde) == 3:
                                desde = [f"{desde[0]} {desde[1]}",desde[2]]
                        else:
                            desde = [None,None]

                        hasta = tipos.get("Hasta")
                        if hasta:
                            hasta = hasta.split(" ")
                            if len(hasta) == 3:
                                hasta = [f"{hasta[0]} {hasta[1]}",hasta[2]]
                        else:
                            hasta = [None,None]

                        writer.writerow([carrera,plan,desde[0],desde[1],hasta[0],hasta[1],tipo,codigo,materia.get("Nombre"),materia.get("Creditos"),materia.get("Creditos requeridos"),materia.get("Correlativas")])
                        

def turn_sga_into_csv(dataset=None):
    if not dataset:
        with open("./data/dataset.json","r",encoding="utf-8") as f:
            dataset = json.load(f)

    with open("./data/dataset.csv","w",encoding="utf-8",newline="") as f:
        writer = csv.writer(f)
        headers = ["Año","Cuatrimestre","Materia","Departamento","Comision","Horario","Profesores","Inscriptos"]
        writer.writerow(headers)
        todos:dict
        materias:dict
        comisiones:dict
        for ano,todos in dataset.items():
            for cuatrimestre,materias in todos.items():
                for materia,comisiones in materias.items():
                    for plan,datos  in comisiones.items():
                        #print([ano,cuatrimestre,materia,datos["departamento"],plan,datos["horario"],datos["profesores"],datos["inscriptos"]])
                        writer.writerow([ano,cuatrimestre,materia,datos["departamento"],plan,datos["horario"],datos["profesores"],datos["inscriptos"]])

    with open("./data/dataset.csv","r",encoding="utf-8") as f:
        reader = csv.DictReader(f)
        data = list(reader)
    db:pd.DataFrame = clean_db(data)
    del data

    with open("./data/cursos.csv","w",encoding="utf-8",newline="") as f:
        writer = csv.writer(f)
        headers = ['Año', 'Cuatrimestre', 'Materia', 'Departamento', 'Comision', 'Horario',
       'Profesores', 'Inscriptos', 'Capacidad', 'Codigo']
        writer.writerow(headers)
        for row in db.iterrows():
            
            writer.writerow(row[1])
            




if __name__ == "__main__":
    #extract_sga_classes()

    #extract_sga_carreras(debug=getattr(sys, 'gettrace', None)())
    #turn_sga_into_csv()
    turn_carreras_into_csv()
    pass
    