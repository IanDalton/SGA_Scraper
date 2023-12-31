db <- read.csv("S:\\Github\\SGA_Scrapper\\data\\dataset_completo.csv")

########################################################################################################################################

# Análisis exploratorio de datos

# Vamos a hacer EDA en los datos del sistema de gestión académica del ITBA (SGA).  

# Nuestro objetivo es predecir la cantidad de alumnos que se va a inscribir en una materia al inicio del cuatrimestre. 
# Esto permitiría que la facultad planificara la distribución de los alumnos en las sedes, 
# y prevenir una falta de espacio para las clases. 

library(tidyverse)

# Inspección inicial

dim(db)
head(db)
names(db)
str(db)

# Digrama de dispersión de inscriptos y capacidad

ggplot(db, aes(x=Inscriptos, y=Capacidad)) +
  geom_point() 



# boxplot e histograma de inscriptos

boxplot(db$Inscriptos, main = "Boxplot de inscriptos", ylab = "Valores")
hist(db$Inscriptos, main = "Histograma de inscriptos", xlab = "Valores")



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

db$Planes <- lapply(db$Planes, function(x) {
  # Divide la cadena por coma
  vector <- strsplit(x, ", ")[[1]]
  # Elimina los corchetes
  gsub("\\[|\\]|'", "", vector)
})


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
    labs(title = "Créditos ofrecidos por año",
         x = "Año",
         y = "Créditos") +
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
    labs(title = "Créditos cursados por año",
         x = "Año",
         y = "Créditos") +
    theme(plot.title = element_text(hjust = 0.5))



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


#Testing if there is a correlation between creditos ofrecidos and creditos cursados per year

db %>% 
  filter(!is.na(Creditos))%>%
  group_by(Año) %>% 
  summarise(Creditos = sum(Creditos)) %>% 
  left_join(db %>% 
              filter(!is.na(Creditos))%>%
              group_by(Año) %>% 
              summarise(Creditos = sum(Creditos*Inscriptos)), by = "Año") %>% 
  ggplot(aes(x = Creditos.x, y = Creditos.y)) +
  geom_point() +
  geom_smooth(method = "lm") +
  labs(title = "Créditos ofrecidos vs cursados",
       x = "Créditos ofrecidos",
       y = "Créditos cursados") +
  theme(plot.title = element_text(hjust = 0.5))


#graph bar showing the top 5 inscriptos in a year on materias that have creditos

db %>% 
  filter(!is.na(Creditos))%>%
  group_by(Año, Codigo,Materia) %>% 
  summarise(Inscriptos = sum(Inscriptos)) %>% 
  arrange(desc(Inscriptos)) %>% 
  head(8)%>%
  ggplot(aes(x = reorder(Materia, Inscriptos), y = Inscriptos,fill = Materia)) +
  geom_bar(stat = "identity", position = "dodge") +
  geom_label(aes(label = Inscriptos), nudge_y = -100) +
  labs(title = "Top 8 materias con más inscriptos por año",
       x = "Materia",
       y = "Inscriptos") +
  theme(plot.title = element_text(hjust = 0.5))+
  coord_flip()+
  facet_wrap(~Año)

db %>% 
  filter(!is.na(Creditos))%>%
  group_by(Año, Codigo,Materia,Inscriptos,Capacidad,Comision) %>% 
  arrange(desc(Inscriptos)) %>% 
  View()

# Creating a graph showing the size of the comisions year over year in Fisica I

db %>% 
  filter(Materia == "Física I")%>%
  group_by(Año,Comision) %>% 
  summarise(Inscriptos = sum(Inscriptos)) %>% 
  ggplot(aes(x = Año, y = Inscriptos,fill = Comision)) +
  geom_bar(stat = "identity", position = "dodge") +
  geom_label(aes(label = Inscriptos), nudge_y = -100) +
  labs(title = "Inscriptos en Física I por año",
       x = "Año",
       y = "Inscriptos") +
  theme(plot.title = element_text(hjust = 0.5))+
  coord_flip()+
  facet_wrap(~Comision)

#Creating a graph showing the average year over year in Fisica I on a line graph


db %>% 
  filter(Materia == "Física I")%>%
  group_by(Año,Comision) %>% 
  summarise(Inscriptos = mean(Inscriptos)) %>% 
  group_by(Año) %>%
  summarise(Inscriptos = mean(Inscriptos)) %>%
  ggplot(aes(x = Año, y = Inscriptos)) +
  geom_line() +
  geom_point() +
  geom_label(aes(label = Inscriptos)) +
  labs(title = "Inscriptos promedio en Estructura de datos y programacion por año",
       x = "Año",
       y = "Inscriptos") +
  theme(plot.title = element_text(hjust = 0.5))

db %>% 
  filter(Codigo == "71.45")%>%
  group_by(Año,Comision, Cuatrimestre) %>% 
  summarise(Inscriptos = mean(Inscriptos)) %>% 
  group_by(Año, Cuatrimestre) %>%
  summarise(Inscriptos = mean(Inscriptos)) %>%
  ggplot(aes(x = Año, y = Inscriptos, color = Cuatrimestre)) +
  geom_line() +
  geom_point() +
  geom_label(aes(label = Inscriptos)) +
  labs(title = "Inscriptos promedio en Estructura de datos y programacion por año",
       x = "Año",
       y = "Inscriptos") +
  theme(plot.title = element_text(hjust = 0.5))

#spearman correlation matrix

library(corrplot)

db %>% 
  select_if(is.numeric) %>% 
  cor(method = "spearman") %>% 
  corrplot( method = "square", tl.col = "black", tl.srt = 45)

