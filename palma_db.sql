-- ============================================================
-- BASE DE DATOS: PALMA (CON FACTURACIÓN ELECTRÓNICA Y DEVOLUCIONES)
-- VERSIÓN COMPLETA PARA INSTALACIÓN LIMPIA
-- ============================================================

SET FOREIGN_KEY_CHECKS = 0;
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";
START TRANSACTION;

-- ------------------------------------------------------------
-- 1. TABLA: rol
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `rol`;
CREATE TABLE `rol` (
  `id_rol` INT(11) NOT NULL AUTO_INCREMENT,
  `descripcion_rol` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`id_rol`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `rol` (`id_rol`, `descripcion_rol`) VALUES
(1, 'Administrador'),
(2, 'Cajero');

-- ------------------------------------------------------------
-- 2. TABLA: categoria
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `categoria`;
CREATE TABLE `categoria` (
  `id_categoria` INT(11) NOT NULL AUTO_INCREMENT,
  `nombre_categoria` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`id_categoria`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `categoria` (`id_categoria`, `nombre_categoria`) VALUES
(1, 'Frutas'),
(2, 'Verduras'),
(3, 'Granos'),
(4, 'Lácteos'),
(5, 'Bebidas'),
(6, 'Aseo y limpieza personal');

-- ------------------------------------------------------------
-- 3. TABLA: estado_producto
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `estado_producto`;
CREATE TABLE `estado_producto` (
  `id_estado` INT(11) NOT NULL AUTO_INCREMENT,
  `nombre_estado` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`id_estado`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `estado_producto` (`id_estado`, `nombre_estado`) VALUES
(1, 'Disponible'),
(2, 'Vencido'),
(3, 'Descontinuado'),
(4, 'Dañado');

-- ------------------------------------------------------------
-- 4. TABLA: tipo_movimiento
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `tipo_movimiento`;
CREATE TABLE `tipo_movimiento` (
  `id_tipo_mov` INT(11) NOT NULL AUTO_INCREMENT,
  `nombre_tipo_movimiento` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`id_tipo_mov`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `tipo_movimiento` (`id_tipo_mov`, `nombre_tipo_movimiento`) VALUES
(1, 'Entrada'),
(2, 'Salida'),
(3, 'Devolución');

-- ------------------------------------------------------------
-- 5. TABLA: clientes (MODIFICADA PARA FACTURACIÓN ELECTRÓNICA)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `clientes`;
CREATE TABLE `clientes` (
  `id_cliente` INT(11) NOT NULL AUTO_INCREMENT,
  `nombre_cliente` VARCHAR(150) NOT NULL,
  `documento_identidad` VARCHAR(20) DEFAULT NULL,
  `tipo_identificacion` VARCHAR(20) DEFAULT NULL COMMENT 'Tipo de identificación (ej. NIT, CC, CE)',
  `responsabilidad_fiscal` VARCHAR(100) DEFAULT NULL COMMENT 'Responsabilidad fiscal (ej. Régimen común, simplificado)',
  `telefono` VARCHAR(20) DEFAULT NULL,
  `email` VARCHAR(150) DEFAULT NULL,
  `direccion` VARCHAR(200) DEFAULT NULL,
  `ciudad` VARCHAR(100) DEFAULT 'Bogotá',
  `departamento` VARCHAR(100) DEFAULT 'Cundinamarca',
  PRIMARY KEY (`id_cliente`),
  UNIQUE KEY `documento_identidad` (`documento_identidad`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `clientes` (`id_cliente`, `nombre_cliente`, `documento_identidad`, `tipo_identificacion`, `responsabilidad_fiscal`, `telefono`, `email`, `direccion`, `ciudad`, `departamento`) VALUES
(1, 'Carlos Andrés Gómez', '1020304050', 'CC', 'Régimen común', '3101234567', 'carlos.gomez@email.com', 'Calle 12 # 5-30', 'Bogotá', 'Cundinamarca'),
(2, 'María Fernanda López', '1030405060', 'CC', 'Régimen simplificado', '3209876543', 'mfernanda.lopez@email.com', 'Carrera 7 # 45-10', 'Medellín', 'Antioquia'),
(3, 'Juan Pablo Martínez', '1040506070', 'CC', 'Régimen común', '3155557788', 'jp.martinez@email.com', 'Av. 30 # 20-15', 'Cali', 'Valle del Cauca'),
(4, 'Luisa Valentina Torres', '1050607080', 'CC', 'Régimen simplificado', '3187776655', 'luisa.torres@email.com', 'Calle 80 # 10-05', 'Barranquilla', 'Atlántico'),
(5, 'Pedro Antonio Vargas', '1060708090', 'CC', 'Régimen común', '3004445566', 'pedro.vargas@email.com', 'Diagonal 15 # 8-22', 'Bucaramanga', 'Santander'),
(6, 'Camila Andrea Ospina', '1070809100', 'CC', 'Régimen simplificado', '3112223344', 'camila.ospina@email.com', 'Calle 45 # 12-08', 'Manizales', 'Caldas'),
(7, 'Ricardo Esteban Pinto', '1080910200', 'CC', 'Régimen común', '3223334455', 'ricardo.pinto@email.com', 'Carrera 20 # 33-17', 'Pereira', 'Risaralda'),
(8, 'Natalia Marcela Herrera', '1091011300', 'CC', 'Régimen simplificado', '3334445566', 'natalia.herrera@email.com', 'Av. Las Palmas # 5-9', 'Cartagena', 'Bolívar');

-- ------------------------------------------------------------
-- 6. TABLA: proveedores
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `proveedores`;
CREATE TABLE `proveedores` (
  `id_proveedor` INT(11) NOT NULL AUTO_INCREMENT,
  `nombre_empresa` VARCHAR(150) NOT NULL,
  `nit` VARCHAR(20) DEFAULT NULL,
  `telefono_principal` VARCHAR(20) DEFAULT NULL,
  `email` VARCHAR(150) DEFAULT NULL,
  `direccion` VARCHAR(200) DEFAULT NULL,
  `ciudad` VARCHAR(100) DEFAULT NULL,
  PRIMARY KEY (`id_proveedor`),
  UNIQUE KEY `nit` (`nit`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `proveedores` (`id_proveedor`, `nombre_empresa`, `nit`, `telefono_principal`, `email`, `direccion`, `ciudad`) VALUES
(1, 'Distribuidora El Campo SAS', '900111222-1', '6011234567', 'ventas@elcampo.com', 'Bodega 5, Zona Industrial Norte', 'Bogotá'),
(2, 'Lácteos del Valle Ltda', '800333444-2', '6024569870', 'pedidos@lacteosvalle.com', 'Km 3 Vía Cali-Palmira', 'Cali'),
(3, 'Proviser Higiene y Aseo SAS', '901555666-3', '6055558877', 'comercial@proviser.com', 'Carrera 50 # 30-40', 'Medellín');

-- ------------------------------------------------------------
-- 7. TABLA: empleados
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `empleados`;
CREATE TABLE `empleados` (
  `id_empleado` INT(10) NOT NULL AUTO_INCREMENT,
  `nombre_empleado` VARCHAR(150) NOT NULL,
  `id_rol` INT(11) DEFAULT NULL,
  `fecha_ingreso` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `monto_pago` DECIMAL(10,2) DEFAULT NULL,
  PRIMARY KEY (`id_empleado`),
  KEY `id_rol` (`id_rol`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `empleados` (`id_empleado`, `nombre_empleado`, `id_rol`, `fecha_ingreso`, `monto_pago`) VALUES
(1, 'nicolas eduardo herran daza', 1, '2023-01-15 08:00:00', 3500000.00),
(2, 'edwin armando acosta soriano', 1, '2023-03-01 08:00:00', 3200000.00),
(3, 'Joseph Alejandro Hernández', 2, '2023-06-10 08:00:00', 2000000.00),
(4, 'Mariana Zarate Pachote', 2, '2022-11-20 08:00:00', 2000000.00);

-- ------------------------------------------------------------
-- 8. TABLA: usuarios
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `usuarios`;
CREATE TABLE `usuarios` (
  `id_usuario` INT(11) NOT NULL AUTO_INCREMENT,
  `id_rol` INT(11) DEFAULT NULL,
  `id_empleado` INT(10) DEFAULT NULL,
  `username_log` VARCHAR(50) DEFAULT NULL,
  `contrasena_log` VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `username_log` (`username_log`),
  KEY `id_empleado` (`id_empleado`),
  KEY `id_rol` (`id_rol`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `usuarios` (`id_usuario`, `id_rol`, `id_empleado`, `username_log`, `contrasena_log`) VALUES
(1, 1, 1, 'nicolasherran', '113355'),
(2, 1, 2, 'edwinacosta', '224466'),
(3, 2, 3, 'alejandrohernandez', '335577'),
(4, 2, 4, 'marianazarate', '446688');

-- ------------------------------------------------------------
-- 9. TABLA: productos (con todos los 91 productos)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `productos`;
CREATE TABLE `productos` (
  `id_producto` INT(11) NOT NULL AUTO_INCREMENT,
  `nombre_producto` VARCHAR(150) NOT NULL,
  `marca_producto` VARCHAR(100) DEFAULT NULL,
  `id_categoria` INT(11) DEFAULT NULL,
  `id_estado` INT(11) DEFAULT NULL,
  `precio_venta_prod` DECIMAL(10,2) DEFAULT NULL,
  `id_proveedor` INT(11) DEFAULT NULL,
  PRIMARY KEY (`id_producto`),
  KEY `id_categoria` (`id_categoria`),
  KEY `id_estado` (`id_estado`),
  KEY `id_proveedor` (`id_proveedor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `productos` (`id_producto`, `nombre_producto`, `marca_producto`, `id_categoria`, `id_estado`, `precio_venta_prod`, `id_proveedor`) VALUES
(1, 'Manzana Roja x kg', 'Frutas Frescas', 1, 1, 4500.00, 1),
(2, 'Leche Entera x Lt', 'Alquería', 4, 1, 3200.00, 2),
(3, 'Arroz Blanco x 5kg', 'Roa', 3, 1, 18500.00, 1),
(4, 'Agua Mineral x 600ml', 'Cristal', 5, 1, 2000.00, 2),
(5, 'Jabón de Baño', 'Dove', 6, 1, 3800.00, 3),
(6, 'Zanahoria x kg', 'La Huerta', 2, 1, 2800.00, 1),
(7, 'Yogur Fresa x 200g', 'Alpina', 4, 2, 2500.00, 2),
(8, 'Shampoo Anticaspa x 400ml', 'Head & Shoulders', 6, 1, 18900.00, 3),
(9, 'Banano x kg', 'Frutas Frescas', 1, 1, 2200.00, 1),
(10, 'Detergente Líquido x 1Lt', 'Ariel', 6, 1, 12500.00, 3),
(11, 'Jugo de Naranja x 1Lt', 'Del Valle', 5, 1, 5800.00, 2),
(12, 'Aguacate Has x kg', 'Fruver Local', 1, 1, 8500.00, 1),
(13, 'Mango Tomy x kg', 'Fruver Local', 1, 1, 4200.00, 1),
(14, 'Piña Oro Miel unidad', 'Fruver Local', 1, 1, 3500.00, 1),
(15, 'Papaya Maradol x kg', 'Fruver Local', 1, 1, 3800.00, 1),
(16, 'Fresas seleccionadas x 500g', 'Fruver Premium', 1, 1, 5500.00, 1),
(17, 'Mora de Castilla x kg', 'Fruver Local', 1, 1, 4600.00, 1),
(18, 'Lulo de la Región x kg', 'Fruver Local', 1, 1, 5800.00, 1),
(19, 'Maracuyá Premium x kg', 'Fruver Local', 1, 1, 4900.00, 1),
(20, 'Guanábana entera x kg', 'Fruver Local', 1, 1, 6500.00, 1),
(21, 'Guayaba Manzana x kg', 'Fruver Local', 1, 1, 3400.00, 1),
(22, 'Naranja Tangelo x kg', 'Fruver Local', 1, 1, 2900.00, 1),
(23, 'Mandarina Arrayana x kg', 'Fruver Local', 1, 1, 3200.00, 1),
(24, 'Limón Tahití x kg', 'Fruver Local', 1, 1, 4000.00, 1),
(25, 'Melón Cantaloupe unidad', 'Fruver Local', 1, 1, 4500.00, 1),
(26, 'Sandía entera x kg', 'Fruver Local', 1, 1, 1800.00, 1),
(27, 'Uva Isabela x 500g', 'Fruver Local', 1, 1, 3900.00, 1),
(28, 'Uva Verde sin semilla x 500g', 'Importado', 1, 1, 8900.00, 1),
(29, 'Manzana Verde x kg', 'Importado', 1, 1, 7800.00, 1),
(30, 'Pera Williams x kg', 'Importado', 1, 1, 7200.00, 1),
(31, 'Durazno Nacional x kg', 'Fruver Local', 1, 1, 6800.00, 1),
(32, 'Ciruela Roja x kg', 'Fruver Local', 1, 1, 5900.00, 1),
(33, 'Kiwi importado unidad', 'Importado', 1, 1, 2500.00, 1),
(34, 'Pitahaya Amarilla unidad', 'Fruver Premium', 1, 1, 4800.00, 1),
(35, 'Granadilla seleccionada x kg', 'Fruver Local', 1, 1, 6200.00, 1),
(36, 'Curuba larga x kg', 'Fruver Local', 1, 1, 3100.00, 1),
(37, 'Feijoa criolla x kg', 'Fruver Local', 1, 1, 4300.00, 1),
(38, 'Tomate de Árbol x kg', 'Fruver Local', 1, 1, 3700.00, 1),
(39, 'Chirimoya dulce x kg', 'Fruver Local', 1, 1, 7500.00, 1),
(40, 'Borojó de la Costa unidad', 'Fruver Local', 1, 1, 3500.00, 1),
(41, 'Mangostino exótico x kg', 'Fruver Premium', 1, 1, 14000.00, 1),
(42, 'Arándanos bandeja x 125g', 'Fruver Premium', 1, 1, 4500.00, 1),
(43, 'Frambuesas bandeja x 125g', 'Fruver Premium', 1, 1, 6900.00, 1),
(44, 'Plátano Hartón Verde x kg', 'Fruver Local', 1, 1, 3300.00, 1),
(45, 'Plátano Madurito x kg', 'Fruver Local', 1, 1, 3500.00, 1),
(46, 'Tomate Chonto x kg', 'La Huerta', 2, 1, 3400.00, 1),
(47, 'Tomate Milano x kg', 'La Huerta', 2, 1, 4200.00, 1),
(48, 'Cebolla Cabezona Blanca x kg', 'La Huerta', 2, 1, 2800.00, 1),
(49, 'Cebolla Cabezona Roja x kg', 'La Huerta', 2, 1, 3200.00, 1),
(50, 'Cebolla Larga Junca x atado', 'La Huerta', 2, 1, 1800.00, 1),
(51, 'Pimentón Rojo x kg', 'La Huerta', 2, 1, 4500.00, 1),
(52, 'Papa Pastusa x kg', 'La Huerta', 2, 1, 2400.00, 1),
(53, 'Papa Sabanera x kg', 'La Huerta', 2, 1, 3100.00, 1),
(54, 'Papa Criolla limpia x kg', 'La Huerta', 2, 1, 3800.00, 1),
(55, 'Yuca ICA congelada x kg', 'La Huerta', 2, 1, 4000.00, 1),
(56, 'Arracacha Tolimense x kg', 'La Huerta', 2, 1, 4800.00, 1),
(57, 'Auyama porción x kg', 'La Huerta', 2, 1, 1800.00, 1),
(58, 'Ahuyama Baby unidad', 'La Huerta', 2, 1, 2200.00, 1),
(59, 'Pepino Cohombro x kg', 'La Huerta', 2, 1, 1900.00, 1),
(60, 'Calabacín Zucchini Verde x kg', 'La Huerta', 2, 1, 3300.00, 1),
(61, 'Habichuela larga x kg', 'La Huerta', 2, 1, 2600.00, 1),
(62, 'Arveja Verde en vaina x kg', 'La Huerta', 2, 1, 6500.00, 1),
(63, 'Fríjol Verde en vaina x kg', 'La Huerta', 2, 1, 5800.00, 1),
(64, 'Espinaca Bogotá atado', 'La Huerta', 2, 1, 1500.00, 1),
(65, 'Lechuga Crespa Verde unidad', 'La Huerta', 2, 1, 2000.00, 1),
(66, 'Lechuga Romana unidad', 'La Huerta', 2, 1, 2500.00, 1),
(67, 'Brócoli seleccionado x kg', 'La Huerta', 2, 1, 4900.00, 1),
(68, 'Coliflor limpia unidad', 'La Huerta', 2, 1, 4300.00, 1),
(69, 'Repollo Blanco unidad', 'La Huerta', 2, 1, 2600.00, 1),
(70, 'Repollo Morado unidad', 'La Huerta', 2, 1, 3100.00, 1),
(71, 'Apio España atado', 'La Huerta', 2, 1, 1700.00, 1),
(72, 'Cilantro fresco atado', 'La Huerta', 2, 1, 1200.00, 1),
(73, 'Perejil Crespo atado', 'La Huerta', 2, 1, 1400.00, 1),
(74, 'Ajo trenza x 3 unidades', 'La Huerta', 2, 1, 3000.00, 1),
(75, 'Remolacha limpia x kg', 'La Huerta', 2, 1, 2300.00, 1),
(76, 'Lenteja Nacional x 500g', 'Aburrá', 3, 1, 3500.00, 1),
(77, 'Fríjol Bola Roja x 500g', 'Aburrá', 3, 1, 6200.00, 1),
(78, 'Garbanzo Importado x 500g', 'Aburrá', 3, 1, 4100.00, 1),
(79, 'Maíz Pira Bolsa x 500g', 'Aburrá', 3, 1, 2800.00, 1),
(80, 'Queso Campesino x 500g', 'Alpina', 4, 1, 11500.00, 2),
(81, 'Mantequilla con sal x 250g', 'Colanta', 4, 1, 6800.00, 2),
(82, 'Crema de Leche x 200g', 'Alquería', 4, 1, 4100.00, 2),
(83, 'Kumis Vaso x 150g', 'San Fernando', 4, 1, 1800.00, 2),
(84, 'Gaseosa Coca-Cola 1.5Lt', 'Coca-Cola', 5, 1, 4800.00, 2),
(85, 'Té Verde Hatsu 400ml', 'Hatsu', 5, 1, 3900.00, 2),
(86, 'Jugo Hit Mora 1Lt', 'Postobón', 5, 1, 3200.00, 2),
(87, 'Soda Bretaña Botella 300ml', 'Postobón', 5, 1, 1700.00, 2),
(88, 'Crema Dental Triple Acción', 'Colgate', 6, 1, 5400.00, 3),
(89, 'Papel Higiénico x 4 rollos', 'Familia', 6, 1, 6500.00, 3),
(90, 'Jabón Líquido Manos 500ml', 'Protex', 6, 1, 8900.00, 3),
(91, 'Desodorante Original Barra', 'Rexona', 6, 1, 11200.00, 3);

-- ------------------------------------------------------------
-- 10. TABLA: inventarios
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `inventarios`;
CREATE TABLE `inventarios` (
  `id_inventario` INT(11) NOT NULL AUTO_INCREMENT,
  `id_producto` INT(11) DEFAULT NULL,
  `stock_actual` INT(11) DEFAULT NULL,
  `condicion` VARCHAR(100) DEFAULT NULL,
  `timestamp_ultima_actualizacion` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_inventario`),
  KEY `id_producto` (`id_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `inventarios` (`id_inventario`, `id_producto`, `stock_actual`, `condicion`, `timestamp_ultima_actualizacion`) VALUES
(1, 1, 150, 'Buena', '2026-04-06 14:46:59'),
(2, 2, 200, 'Buena', '2026-04-06 14:46:59'),
(3, 3, 80, 'Buena', '2026-04-06 14:46:59'),
(4, 4, 300, 'Buena', '2026-04-06 14:46:59'),
(5, 5, 120, 'Buena', '2026-04-06 14:46:59'),
(6, 6, 100, 'Buena', '2026-04-06 14:46:59'),
(7, 7, 10, 'Vencida', '2026-04-06 14:46:59'),
(8, 8, 60, 'Buena', '2026-04-06 14:46:59'),
(9, 9, 180, 'Buena', '2026-04-06 14:51:06'),
(10, 10, 90, 'Buena', '2026-04-06 14:51:06'),
(11, 11, 130, 'Buena', '2026-04-06 14:51:06'),
(12, 12, 85, 'Buena', CURRENT_TIMESTAMP),
(13, 13, 120, 'Buena', CURRENT_TIMESTAMP),
(14, 14, 60, 'Buena', CURRENT_TIMESTAMP),
(15, 15, 75, 'Buena', CURRENT_TIMESTAMP),
(16, 16, 40, 'Buena', CURRENT_TIMESTAMP),
(17, 17, 95, 'Buena', CURRENT_TIMESTAMP),
(18, 18, 110, 'Buena', CURRENT_TIMESTAMP),
(19, 19, 80, 'Buena', CURRENT_TIMESTAMP),
(20, 20, 35, 'Buena', CURRENT_TIMESTAMP),
(21, 21, 90, 'Buena', CURRENT_TIMESTAMP),
(22, 22, 250, 'Buena', CURRENT_TIMESTAMP),
(23, 23, 180, 'Buena', CURRENT_TIMESTAMP),
(24, 24, 300, 'Buena', CURRENT_TIMESTAMP),
(25, 25, 45, 'Buena', CURRENT_TIMESTAMP),
(26, 26, 70, 'Buena', CURRENT_TIMESTAMP),
(27, 27, 65, 'Buena', CURRENT_TIMESTAMP),
(28, 28, 50, 'Buena', CURRENT_TIMESTAMP),
(29, 29, 105, 'Buena', CURRENT_TIMESTAMP),
(30, 30, 90, 'Buena', CURRENT_TIMESTAMP),
(31, 31, 55, 'Buena', CURRENT_TIMESTAMP),
(32, 32, 60, 'Buena', CURRENT_TIMESTAMP),
(33, 33, 140, 'Buena', CURRENT_TIMESTAMP),
(34, 34, 30, 'Buena', CURRENT_TIMESTAMP),
(35, 35, 85, 'Buena', CURRENT_TIMESTAMP),
(36, 36, 40, 'Buena', CURRENT_TIMESTAMP),
(37, 37, 50, 'Buena', CURRENT_TIMESTAMP),
(38, 38, 115, 'Buena', CURRENT_TIMESTAMP),
(39, 39, 25, 'Buena', CURRENT_TIMESTAMP),
(40, 40, 40, 'Buena', CURRENT_TIMESTAMP),
(41, 41, 15, 'Buena', CURRENT_TIMESTAMP),
(42, 42, 60, 'Buena', CURRENT_TIMESTAMP),
(43, 43, 40, 'Buena', CURRENT_TIMESTAMP),
(44, 44, 130, 'Buena', CURRENT_TIMESTAMP),
(45, 45, 140, 'Buena', CURRENT_TIMESTAMP),
(46, 46, 200, 'Buena', CURRENT_TIMESTAMP),
(47, 47, 180, 'Buena', CURRENT_TIMESTAMP),
(48, 48, 220, 'Buena', CURRENT_TIMESTAMP),
(49, 49, 190, 'Buena', CURRENT_TIMESTAMP),
(50, 50, 150, 'Buena', CURRENT_TIMESTAMP),
(51, 51, 95, 'Buena', CURRENT_TIMESTAMP),
(52, 52, 400, 'Buena', CURRENT_TIMESTAMP),
(53, 53, 350, 'Buena', CURRENT_TIMESTAMP),
(54, 54, 280, 'Buena', CURRENT_TIMESTAMP),
(55, 55, 100, 'Buena', CURRENT_TIMESTAMP),
(56, 56, 85, 'Buena', CURRENT_TIMESTAMP),
(57, 57, 60, 'Buena', CURRENT_TIMESTAMP),
(58, 58, 45, 'Buena', CURRENT_TIMESTAMP),
(59, 59, 130, 'Buena', CURRENT_TIMESTAMP),
(60, 60, 70, 'Buena', CURRENT_TIMESTAMP),
(61, 61, 110, 'Buena', CURRENT_TIMESTAMP),
(62, 62, 90, 'Buena', CURRENT_TIMESTAMP),
(63, 63, 85, 'Buena', CURRENT_TIMESTAMP),
(64, 64, 120, 'Buena', CURRENT_TIMESTAMP),
(65, 65, 80, 'Buena', CURRENT_TIMESTAMP),
(66, 66, 75, 'Buena', CURRENT_TIMESTAMP),
(67, 67, 65, 'Buena', CURRENT_TIMESTAMP),
(68, 68, 55, 'Buena', CURRENT_TIMESTAMP),
(69, 69, 90, 'Buena', CURRENT_TIMESTAMP),
(70, 70, 50, 'Buena', CURRENT_TIMESTAMP),
(71, 71, 70, 'Buena', CURRENT_TIMESTAMP),
(72, 72, 160, 'Buena', CURRENT_TIMESTAMP),
(73, 73, 80, 'Buena', CURRENT_TIMESTAMP),
(74, 74, 100, 'Buena', CURRENT_TIMESTAMP),
(75, 75, 110, 'Buena', CURRENT_TIMESTAMP),
(76, 76, 150, 'Buena', CURRENT_TIMESTAMP),
(77, 77, 120, 'Buena', CURRENT_TIMESTAMP),
(78, 78, 95, 'Buena', CURRENT_TIMESTAMP),
(79, 79, 140, 'Buena', CURRENT_TIMESTAMP),
(80, 80, 45, 'Buena', CURRENT_TIMESTAMP),
(81, 81, 70, 'Buena', CURRENT_TIMESTAMP),
(82, 82, 85, 'Buena', CURRENT_TIMESTAMP),
(83, 83, 120, 'Buena', CURRENT_TIMESTAMP),
(84, 84, 100, 'Buena', CURRENT_TIMESTAMP),
(85, 85, 60, 'Buena', CURRENT_TIMESTAMP),
(86, 86, 80, 'Buena', CURRENT_TIMESTAMP),
(87, 87, 150, 'Buena', CURRENT_TIMESTAMP),
(88, 88, 90, 'Buena', CURRENT_TIMESTAMP),
(89, 89, 110, 'Buena', CURRENT_TIMESTAMP),
(90, 90, 65, 'Buena', CURRENT_TIMESTAMP),
(91, 91, 75, 'Buena', CURRENT_TIMESTAMP);

-- ------------------------------------------------------------
-- 11. TABLA: factura_compra
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `factura_compra`;
CREATE TABLE `factura_compra` (
  `id_fac_compra` INT(11) NOT NULL AUTO_INCREMENT,
  `numero_fac_compra` VARCHAR(50) DEFAULT NULL,
  `id_proveedor` INT(11) DEFAULT NULL,
  `id_empleado` INT(11) DEFAULT NULL,
  `fecha_fac_compra` DATETIME DEFAULT NULL,
  `valor_fac_compra` DECIMAL(10,2) DEFAULT NULL,
  PRIMARY KEY (`id_fac_compra`),
  KEY `id_proveedor` (`id_proveedor`),
  KEY `id_empleado` (`id_empleado`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `factura_compra` (`id_fac_compra`, `numero_fac_compra`, `id_proveedor`, `id_empleado`, `fecha_fac_compra`, `valor_fac_compra`) VALUES
(1, 'FC-2024-001', 1, 4, '2024-01-10 09:00:00', 850000.00),
(2, 'FC-2024-002', 2, 4, '2024-02-05 10:30:00', 640000.00),
(3, 'FC-2024-003', 3, 1, '2024-03-12 11:00:00', 1150000.00);

-- ------------------------------------------------------------
-- 12. TABLA: facturas (ventas normales)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `facturas`;
CREATE TABLE `facturas` (
  `id_factura` INT(11) NOT NULL AUTO_INCREMENT,
  `id_empleado` INT(11) DEFAULT NULL,
  `id_cliente` INT(11) DEFAULT NULL,
  `fecha_fac` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `total_fac` DECIMAL(10,2) DEFAULT NULL,
  PRIMARY KEY (`id_factura`),
  KEY `id_empleado` (`id_empleado`),
  KEY `id_cliente` (`id_cliente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `facturas` (`id_factura`, `id_empleado`, `id_cliente`, `fecha_fac`, `total_fac`) VALUES
(1, 2, 1, '2024-03-15 10:15:00', 26200.00),
(2, 3, 2, '2024-03-16 14:30:00', 18500.00),
(3, 2, 3, '2024-03-18 09:45:00', 41700.00),
(4, 3, 4, '2024-03-20 16:00:00', 22700.00),
(5, 2, 5, '2024-04-02 11:20:00', 34500.00),
(6, 3, 6, '2024-04-05 15:00:00', 27400.00),
(7, 2, 7, '2024-04-08 10:10:00', 19800.00);

-- ------------------------------------------------------------
-- 13. TABLA: detalle_factura
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `detalle_factura`;
CREATE TABLE `detalle_factura` (
  `id_detalle` INT(11) NOT NULL AUTO_INCREMENT,
  `id_factura` INT(11) DEFAULT NULL,
  `id_producto` INT(11) DEFAULT NULL,
  `cantidad_detfac` INT(11) DEFAULT NULL,
  `precio_unitario_detfac` DECIMAL(10,2) DEFAULT NULL,
  `subtotal_detfac` DECIMAL(10,2) DEFAULT NULL,
  PRIMARY KEY (`id_detalle`),
  KEY `id_factura` (`id_factura`),
  KEY `id_producto` (`id_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `detalle_factura` (`id_detalle`, `id_factura`, `id_producto`, `cantidad_detfac`, `precio_unitario_detfac`, `subtotal_detfac`) VALUES
(1, 1, 1, 2, 4500.00, 9000.00),
(2, 1, 4, 3, 2000.00, 6000.00),
(3, 1, 6, 4, 2800.00, 11200.00),
(4, 2, 3, 1, 18500.00, 18500.00),
(5, 3, 2, 3, 3200.00, 9600.00),
(6, 3, 5, 2, 3800.00, 7600.00),
(7, 3, 8, 1, 18900.00, 18900.00),
(8, 4, 4, 5, 2000.00, 10000.00),
(9, 4, 5, 3, 3800.00, 11400.00),
(10, 5, 9, 3, 2200.00, 6600.00),
(11, 5, 11, 2, 5800.00, 11600.00),
(12, 5, 5, 4, 3800.00, 15200.00),
(13, 6, 2, 4, 3200.00, 12800.00),
(14, 6, 10, 1, 12500.00, 12500.00),
(15, 7, 4, 3, 2000.00, 6000.00),
(16, 7, 9, 6, 2200.00, 13200.00);

-- ------------------------------------------------------------
-- 14. TABLA: devoluciones (Cabecera)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `devoluciones`;
CREATE TABLE `devoluciones` (
  `id_devolucion` INT(11) NOT NULL AUTO_INCREMENT,
  `tipo_devolucion` ENUM('venta', 'compra') NOT NULL COMMENT 'Indica si es venta o compra',
  `id_factura` INT(11) DEFAULT NULL COMMENT 'FK a facturas',
  `id_fac_compra` INT(11) DEFAULT NULL COMMENT 'FK a factura_compra',
  `id_empleado` INT(11) NOT NULL COMMENT 'Empleado que registra',
  `fecha_devolucion` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `motivo` TEXT,
  `estado` ENUM('Pendiente', 'Aprobada', 'Rechazada', 'Completada') DEFAULT 'Pendiente',
  `monto_total` DECIMAL(10,2) DEFAULT NULL,
  PRIMARY KEY (`id_devolucion`),
  KEY `id_factura` (`id_factura`),
  KEY `id_fac_compra` (`id_fac_compra`),
  KEY `id_empleado` (`id_empleado`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `devoluciones` (`id_devolucion`, `tipo_devolucion`, `id_factura`, `id_fac_compra`, `id_empleado`, `fecha_devolucion`, `motivo`, `estado`, `monto_total`) VALUES
(1, 'venta', 1, NULL, 2, '2024-03-16 09:00:00', 'Producto en mal estado', 'Completada', 9000.00),
(2, 'compra', NULL, 2, 4, '2024-02-10 14:30:00', 'Producto vencido al recibir', 'Aprobada', 3200.00);

-- ------------------------------------------------------------
-- 15. TABLA: detalle_devolucion
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `detalle_devolucion`;
CREATE TABLE `detalle_devolucion` (
  `id_detalle_devolucion` INT(11) NOT NULL AUTO_INCREMENT,
  `id_devolucion` INT(11) NOT NULL,
  `id_producto` INT(11) NOT NULL,
  `cantidad` INT(11) NOT NULL,
  `precio_unitario` DECIMAL(10,2) NOT NULL,
  `subtotal` DECIMAL(10,2) GENERATED ALWAYS AS (cantidad * precio_unitario) STORED,
  PRIMARY KEY (`id_detalle_devolucion`),
  KEY `id_devolucion` (`id_devolucion`),
  KEY `id_producto` (`id_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `detalle_devolucion` (`id_detalle_devolucion`, `id_devolucion`, `id_producto`, `cantidad`, `precio_unitario`) VALUES
(1, 1, 1, 1, 4500.00),
(2, 1, 4, 2, 2000.00),
(3, 2, 2, 1, 3200.00);

-- ------------------------------------------------------------
-- 16. TABLA: movimientos
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `movimientos`;
CREATE TABLE `movimientos` (
  `id_movimiento` INT(11) NOT NULL AUTO_INCREMENT,
  `id_inventario` INT(11) DEFAULT NULL,
  `id_tipo_mov` INT(11) DEFAULT NULL,
  `id_empleado` INT(11) DEFAULT NULL,
  `id_factura` INT(11) DEFAULT NULL,
  `id_fac_compra` INT(11) DEFAULT NULL,
  `id_devolucion` INT(11) DEFAULT NULL,
  `cantidad_movimiento` INT(11) DEFAULT NULL,
  `fecha_movimiento` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_movimiento`),
  KEY `id_inventario` (`id_inventario`),
  KEY `id_tipo_mov` (`id_tipo_mov`),
  KEY `id_empleado` (`id_empleado`),
  KEY `id_factura` (`id_factura`),
  KEY `id_fac_compra` (`id_fac_compra`),
  KEY `id_devolucion` (`id_devolucion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `movimientos` (`id_inventario`, `id_tipo_mov`, `id_empleado`, `id_factura`, `id_fac_compra`, `id_devolucion`, `cantidad_movimiento`, `fecha_movimiento`) VALUES
(1, 1, 4, NULL, 1, NULL, 200, '2024-01-10 09:30:00'),
(6, 1, 4, NULL, 1, NULL, 150, '2024-01-10 09:35:00'),
(2, 1, 4, NULL, 2, NULL, 300, '2024-02-05 11:00:00'),
(7, 1, 4, NULL, 2, NULL, 100, '2024-02-05 11:10:00'),
(5, 1, 1, NULL, 3, NULL, 200, '2024-03-12 11:30:00'),
(8, 1, 1, NULL, 3, NULL, 100, '2024-03-12 11:35:00'),
(1, 2, 2, 1, NULL, NULL, 2, '2024-03-15 10:15:00'),
(3, 2, 3, 2, NULL, NULL, 1, '2024-03-16 14:30:00'),
(9, 1, 4, NULL, 1, NULL, 250, '2024-04-01 08:30:00'),
(10, 1, 1, NULL, 3, NULL, 120, '2024-04-01 08:45:00'),
(11, 1, 4, NULL, 2, NULL, 200, '2024-04-01 09:00:00'),
(9, 2, 2, 5, NULL, NULL, 3, '2024-04-02 11:20:00'),
(2, 2, 3, 6, NULL, NULL, 4, '2024-04-05 15:00:00'),
(4, 2, 2, 7, NULL, NULL, 3, '2024-04-08 10:10:00'),
(1, 3, 2, 1, NULL, 1, 1, '2024-03-16 09:05:00'),
(4, 3, 2, 1, NULL, 1, 2, '2024-03-16 09:05:00'),
(2, 3, 4, NULL, 2, 2, -1, '2024-02-10 14:35:00');

-- ============================================================
-- NUEVAS TABLAS PARA FACTURACIÓN ELECTRÓNICA
-- ============================================================

-- ------------------------------------------------------------
-- 17. TABLA: empresa (emisor de factura electrónica)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `empresa`;
CREATE TABLE `empresa` (
  `id_empresa` INT(11) NOT NULL AUTO_INCREMENT,
  `razon_social` VARCHAR(200) NOT NULL,
  `nit` VARCHAR(20) NOT NULL UNIQUE,
  `regimen_contable` VARCHAR(100) DEFAULT NULL,
  `direccion` VARCHAR(200) DEFAULT NULL,
  `ciudad` VARCHAR(100) DEFAULT NULL,
  `departamento` VARCHAR(100) DEFAULT NULL,
  `telefono` VARCHAR(20) DEFAULT NULL,
  `email` VARCHAR(150) DEFAULT NULL,
  `resolucion_facturacion` VARCHAR(100) DEFAULT NULL COMMENT 'Número de resolución de facturación',
  `fecha_resolucion` DATE DEFAULT NULL,
  PRIMARY KEY (`id_empresa`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `empresa` (`razon_social`, `nit`, `regimen_contable`, `direccion`, `ciudad`, `departamento`, `telefono`, `email`, `resolucion_facturacion`, `fecha_resolucion`) VALUES
('Palma Distribuciones SAS', '123456789-0', 'Régimen común', 'Calle 123 # 45-67, Centro', 'Bogotá', 'Cundinamarca', '6011234567', 'facturacion@palma.com', 'RES-2024-001', '2024-01-01');

-- ------------------------------------------------------------
-- 18. TABLA: factura_electronica (cabecera)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `factura_electronica`;
CREATE TABLE `factura_electronica` (
  `id_factura_electronica` INT(11) NOT NULL AUTO_INCREMENT,
  `id_cliente` INT(11) NOT NULL,
  `id_empleado` INT(11) NOT NULL,
  `id_factura_base` INT(11) DEFAULT NULL COMMENT 'Opcional: referencia a factura normal de caja',
  `prefijo` VARCHAR(5) DEFAULT NULL COMMENT 'Prefijo de facturación (ej. FAC)',
  `consecutivo` INT(11) NOT NULL,
  `numero_resolucion` VARCHAR(50) DEFAULT NULL,
  `fecha_emision` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `fecha_vencimiento` DATETIME DEFAULT NULL,
  `total` DECIMAL(10,2) NOT NULL,
  `subtotal` DECIMAL(10,2) DEFAULT NULL,
  `iva` DECIMAL(10,2) DEFAULT NULL,
  `cufe` VARCHAR(255) UNIQUE DEFAULT NULL COMMENT 'Código único de factura electrónica',
  `estado` ENUM('Generada', 'Enviada', 'Aceptada', 'Rechazada', 'Anulada') DEFAULT 'Generada',
  `xml_enviado` TEXT DEFAULT NULL,
  `respuesta_dian` TEXT DEFAULT NULL,
  `observaciones` TEXT DEFAULT NULL,
  PRIMARY KEY (`id_factura_electronica`),
  KEY `id_cliente` (`id_cliente`),
  KEY `id_empleado` (`id_empleado`),
  KEY `id_factura_base` (`id_factura_base`),
  CONSTRAINT `factura_electronica_ibfk_1` FOREIGN KEY (`id_cliente`) REFERENCES `clientes` (`id_cliente`),
  CONSTRAINT `factura_electronica_ibfk_2` FOREIGN KEY (`id_empleado`) REFERENCES `empleados` (`id_empleado`),
  CONSTRAINT `factura_electronica_ibfk_3` FOREIGN KEY (`id_factura_base`) REFERENCES `facturas` (`id_factura`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ------------------------------------------------------------
-- 19. TABLA: detalle_factura_electronica
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `detalle_factura_electronica`;
CREATE TABLE `detalle_factura_electronica` (
  `id_detalle_fe` INT(11) NOT NULL AUTO_INCREMENT,
  `id_factura_electronica` INT(11) NOT NULL,
  `id_producto` INT(11) NOT NULL,
  `cantidad` INT(11) NOT NULL,
  `precio_unitario` DECIMAL(10,2) NOT NULL,
  `subtotal` DECIMAL(10,2) NOT NULL,
  PRIMARY KEY (`id_detalle_fe`),
  KEY `id_factura_electronica` (`id_factura_electronica`),
  KEY `id_producto` (`id_producto`),
  CONSTRAINT `detalle_factura_electronica_ibfk_1` FOREIGN KEY (`id_factura_electronica`) REFERENCES `factura_electronica` (`id_factura_electronica`) ON DELETE CASCADE,
  CONSTRAINT `detalle_factura_electronica_ibfk_2` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ============================================================
-- DECLARACIÓN FINAL DE RESTRICCIONES (CONSTRAINTS) EXISTENTES
-- ============================================================

ALTER TABLE `empleados` 
  ADD CONSTRAINT `empleados_ibfk_1` FOREIGN KEY (`id_rol`) REFERENCES `rol` (`id_rol`);

ALTER TABLE `usuarios` 
  ADD CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`id_empleado`) REFERENCES `empleados` (`id_empleado`),
  ADD CONSTRAINT `usuarios_ibfk_2` FOREIGN KEY (`id_rol`) REFERENCES `rol` (`id_rol`);

ALTER TABLE `productos` 
  ADD CONSTRAINT `productos_ibfk_1` FOREIGN KEY (`id_categoria`) REFERENCES `categoria` (`id_categoria`),
  ADD CONSTRAINT `productos_ibfk_2` FOREIGN KEY (`id_estado`) REFERENCES `estado_producto` (`id_estado`),
  ADD CONSTRAINT `productos_ibfk_3` FOREIGN KEY (`id_proveedor`) REFERENCES `proveedores` (`id_proveedor`);

ALTER TABLE `inventarios` 
  ADD CONSTRAINT `inventarios_ibfk_1` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`);

ALTER TABLE `factura_compra` 
  ADD CONSTRAINT `factura_compra_ibfk_1` FOREIGN KEY (`id_proveedor`) REFERENCES `proveedores` (`id_proveedor`),
  ADD CONSTRAINT `factura_compra_ibfk_2` FOREIGN KEY (`id_empleado`) REFERENCES `empleados` (`id_empleado`);

ALTER TABLE `facturas` 
  ADD CONSTRAINT `facturas_ibfk_1` FOREIGN KEY (`id_empleado`) REFERENCES `empleados` (`id_empleado`),
  ADD CONSTRAINT `facturas_ibfk_2` FOREIGN KEY (`id_cliente`) REFERENCES `clientes` (`id_cliente`);

ALTER TABLE `detalle_factura` 
  ADD CONSTRAINT `detalle_factura_ibfk_1` FOREIGN KEY (`id_factura`) REFERENCES `facturas` (`id_factura`),
  ADD CONSTRAINT `detalle_factura_ibfk_2` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`);

ALTER TABLE `devoluciones` 
  ADD CONSTRAINT `devoluciones_ibfk_1` FOREIGN KEY (`id_factura`) REFERENCES `facturas` (`id_factura`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `devoluciones_ibfk_2` FOREIGN KEY (`id_fac_compra`) REFERENCES `factura_compra` (`id_fac_compra`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `devoluciones_ibfk_3` FOREIGN KEY (`id_empleado`) REFERENCES `empleados` (`id_empleado`);

ALTER TABLE `detalle_devolucion` 
  ADD CONSTRAINT `detalle_devolucion_ibfk_1` FOREIGN KEY (`id_devolucion`) REFERENCES `devoluciones` (`id_devolucion`) ON DELETE CASCADE,
  ADD CONSTRAINT `detalle_devolucion_ibfk_2` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`);

ALTER TABLE `movimientos` 
  ADD CONSTRAINT `movimientos_ibfk_1` FOREIGN KEY (`id_inventario`) REFERENCES `inventarios` (`id_inventario`),
  ADD CONSTRAINT `movimientos_ibfk_2` FOREIGN KEY (`id_tipo_mov`) REFERENCES `tipo_movimiento` (`id_tipo_mov`),
  ADD CONSTRAINT `movimientos_ibfk_3` FOREIGN KEY (`id_empleado`) REFERENCES `empleados` (`id_empleado`),
  ADD CONSTRAINT `movimientos_ibfk_4` FOREIGN KEY (`id_factura`) REFERENCES `facturas` (`id_factura`),
  ADD CONSTRAINT `movimientos_ibfk_5` FOREIGN KEY (`id_fac_compra`) REFERENCES `factura_compra` (`id_fac_compra`),
  ADD CONSTRAINT `movimientos_ibfk_6` FOREIGN KEY (`id_devolucion`) REFERENCES `devoluciones` (`id_devolucion`) ON DELETE SET NULL;

SET FOREIGN_KEY_CHECKS = 1;
COMMIT;