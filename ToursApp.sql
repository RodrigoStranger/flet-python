CREATE DATABASE IF NOT EXISTS ToursApp;
USE ToursApp;

-- Tabla de usuarios
CREATE TABLE usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  correo VARCHAR(100) NOT NULL UNIQUE,
  clave VARCHAR(255) NOT NULL
);

-- Tabla de rutas
CREATE TABLE rutas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id INT NOT NULL,
  nombre VARCHAR(100) NOT NULL,
  descripcion TEXT,
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Tabla de paradas
CREATE TABLE paradas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  ruta_id INT NOT NULL,
  nombre VARCHAR(100) NOT NULL,
  descripcion TEXT,
  FOREIGN KEY (ruta_id) REFERENCES rutas(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Tabla de vecinos (relación entre paradas)
CREATE TABLE vecinos (
  parada_origen_id INT NOT NULL,
  parada_destino_id INT NOT NULL,
  distancia DECIMAL(10, 2) NOT NULL,
  PRIMARY KEY (parada_origen_id, parada_destino_id),
  FOREIGN KEY (parada_origen_id) REFERENCES paradas(id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (parada_destino_id) REFERENCES paradas(id) ON DELETE CASCADE ON UPDATE CASCADE
);
