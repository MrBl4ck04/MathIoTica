-- Created by Vertabelo (http://vertabelo.com)
-- Last modification date: 2024-10-02 03:52:48.082

-- tables
-- Table: ejercicios
CREATE TABLE ejercicios
(
    id_ejercicio int NOT NULL
    AUTO_INCREMENT,
    operacion varchar
    (50)  NOT NULL,
    valor1 int  NOT NULL,
    valor2 int  NOT NULL,
    respuesta int  NOT NULL,
    CONSTRAINT ejercicios_pk PRIMARY KEY
    (id_ejercicio)
);

    -- Table: juegos
    CREATE TABLE juegos
    (
        id int NOT NULL
        AUTO_INCREMENT,
    curso varchar
        (50)  NOT NULL,
    nombre varchar
        (50)  NOT NULL,
    tiempo time  NOT NULL,
    fecha date  NOT NULL,
    puntuacion float
        (20,2)  NOT NULL,
    operacion varchar
        (100)  NOT NULL,
    digitos int  NOT NULL,
    logrado bool  NOT NULL,
    CONSTRAINT juegos_pk PRIMARY KEY
        (id)
);

-- End of file.

