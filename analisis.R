db <- read.csv("S:\\Github\\SGA_Scrapper\\data\\dataset_completo.csv")

# Path: analisis.R

# Creating a graph that shows the creditos over the years
library(ggplot2)    
library(dplyr)

get_horarios <- function(x) {
  # Remove the brackets and split the string by comma
  split_string <- strsplit(gsub("\\[|\\]|\\(|\\)|'", "", x), ", ")[[1]]
  
  # Create a list with the day, start time, end time, and room number
  list_data <- split(split_string, ceiling(seq_along(split_string)/4))
  
  # Convert each group of four elements into a list
  list_of_lists <- lapply(list_data, function(group) {
    list(day = group[1], start_time = group[2], end_time = group[3], room = group[4])
  })
  
  return(list_of_lists)
}

db$Horario <- lapply(db$Horario, get_horarios)

#shows the creditos over the years
# the dots show the ammount of creditos per year
db %>% 
  filter(!is.na(Creditos))%>%
  group_by(Año) %>% 
  summarise(Creditos = sum(Creditos)) %>% 
    ggplot(aes(x = Año, y = Creditos)) +
    geom_line() +
    geom_point() +
    geom_label(aes(label = Creditos), nudge_y = 100) +
    labs(title = "Creditos por año",
         x = "Año",
         y = "Creditos") +
    theme(plot.title = element_text(hjust = 0.5))

# show the creditos per year but multiplying the creditos by the ammount of alumnos

db %>% 
  filter(!is.na(Creditos))%>%
  group_by(Año) %>% 
  summarise(Creditos = sum(Creditos*Inscriptos)) %>% 
    ggplot(aes(x = Año, y = Creditos)) +
    geom_line() +
    geom_point() +
    geom_label(aes(label = Creditos), nudge_y = 2500) +
    labs(title = "Creditos cursados por año",
         x = "Año",
         y = "Creditos") +
    theme(plot.title = element_text(hjust = 0.5))


# Suppose your column of strings looks like this:
string_column <- c("[[('Lunes', '18:00', '21:00'), ' externa: 4003']]")

# You can use lapply() to apply a function to each element of the column:
vector_of_vectors <- lapply(string_column, get_horarios)
#apply that function to all the elements of the column

#Making a bar graph showing the ammount of materias per year. It start from Y=500 because the first year has 500 materias
db %>% 
  group_by(Año) %>% 
  summarise(Materias = n()) %>% 
    ggplot(aes(x = Año, y = Materias)) +
    geom_bar(stat = "identity") +
    geom_label(aes(label = Materias), nudge_y = 10) +
    labs(title = "Materias por año",
         x = "Año",
         y = "Materias") +
    theme(plot.title = element_text(hjust = 0.5))+
    coord_cartesian(ylim = c(700, 1200))

########################################################################################################################################

# Análisis exploratorio de datos

# Vamos a hacer EDA en los datos del sistema de gestión académica del ITBA (SGA).  

# Nuestro objetivo es predecir la cantidad de alumnos que se va a inscribir en una materia al inicio del cuatrimestre. 
# Esto permitiría que la facultad planificara la distribución de los alumnos en las sedes, 
# y prevenir una falta de espacio para las clases. 

library(tidyverse)

# Inspección inicial

dim(datos)
head(datos)
names(datos)
str(datos)

# Digrama de dispersión de inscriptos y capacidad

ggplot(datos, aes(x=Inscriptos, y=Capacidad)) +
  geom_point() 

# boxplot e histograma de inscriptos

boxplot(datos$Inscriptos, main = "Boxplot de inscriptos", ylab = "Valores")
hist(datos$Inscriptos, main = "Histograma de inscriptos", xlab = "Valores")

