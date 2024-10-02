CREATE TABLE ejercicios (
    id INT NOT NULL AUTO_INCREMENT,
    id_juego INT NOT NULL,
    curso VARCHAR(50) NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    tiempo TIME NOT NULL,
    fecha DATE NOT NULL,
    puntuacion FLOAT(20,2) NOT NULL,
    operacion VARCHAR(100) NOT NULL,
    digitos INT NOT NULL,
    logrado BOOL NOT NULL,
    CONSTRAINT ejercicios_pk PRIMARY KEY (id)
);
