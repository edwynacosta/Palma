-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 08-04-2026 a las 14:03:37
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `palma_web`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `categoria`
--

CREATE TABLE `categoria` (
  `id_categoria` int(11) NOT NULL,
  `nombre_categoria` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `categoria`
--

INSERT INTO `categoria` (`id_categoria`, `nombre_categoria`) VALUES
(1, 'Frutas'),
(2, 'Verduras'),
(3, 'Granos'),
(4, 'Lácteos'),
(5, 'Bebidas'),
(6, 'Aseo y limpieza personal');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `clientes`
--

CREATE TABLE `clientes` (
  `id_cliente` int(11) NOT NULL,
  `nombre_cliente` varchar(150) NOT NULL,
  `documento_identidad` varchar(20) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `email` varchar(150) DEFAULT NULL,
  `direccion` varchar(200) DEFAULT NULL,
  `ciudad` varchar(100) DEFAULT NULL,
  `departamento` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `clientes`
--

INSERT INTO `clientes` (`id_cliente`, `nombre_cliente`, `documento_identidad`, `telefono`, `email`, `direccion`, `ciudad`, `departamento`) VALUES
(1, 'Carlos Andrés Gómez', '1020304050', '3101234567', 'carlos.gomez@email.com', 'Calle 12 # 5-30', 'Bogotá', 'Cundinamarca'),
(2, 'María Fernanda López', '1030405060', '3209876543', 'mfernanda.lopez@email.com', 'Carrera 7 # 45-10', 'Medellín', 'Antioquia'),
(3, 'Juan Pablo Martínez', '1040506070', '3155557788', 'jp.martinez@email.com', 'Av. 30 # 20-15', 'Cali', 'Valle del Cauca'),
(4, 'Luisa Valentina Torres', '1050607080', '3187776655', 'luisa.torres@email.com', 'Calle 80 # 10-05', 'Barranquilla', 'Atlántico'),
(5, 'Pedro Antonio Vargas', '1060708090', '3004445566', 'pedro.vargas@email.com', 'Diagonal 15 # 8-22', 'Bucaramanga', 'Santander'),
(6, 'Camila Andrea Ospina', '1070809100', '3112223344', 'camila.ospina@email.com', 'Calle 45 # 12-08', 'Manizales', 'Caldas'),
(7, 'Ricardo Esteban Pinto', '1080910200', '3223334455', 'ricardo.pinto@email.com', 'Carrera 20 # 33-17', 'Pereira', 'Risaralda'),
(8, 'Natalia Marcela Herrera', '1091011300', '3334445566', 'natalia.herrera@email.com', 'Av. Las Palmas # 5-9', 'Cartagena', 'Bolívar');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalle_factura`
--

CREATE TABLE `detalle_factura` (
  `id_detalle` int(11) NOT NULL,
  `id_factura` int(11) DEFAULT NULL,
  `id_producto` int(11) DEFAULT NULL,
  `cantidad_detfac` int(11) DEFAULT NULL,
  `precio_unitario_detfac` float DEFAULT NULL,
  `subtotal_detfac` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `detalle_factura`
--

INSERT INTO `detalle_factura` (`id_detalle`, `id_factura`, `id_producto`, `cantidad_detfac`, `precio_unitario_detfac`, `subtotal_detfac`) VALUES
(1, 1, 1, 2, 4500, 9000),
(2, 1, 4, 3, 2000, 6000),
(3, 1, 6, 4, 2800, 11200),
(4, 2, 3, 1, 18500, 18500),
(5, 3, 2, 3, 3200, 9600),
(6, 3, 5, 2, 3800, 7600),
(7, 3, 8, 1, 18900, 18900),
(8, 4, 4, 5, 2000, 10000),
(9, 4, 5, 3, 3800, 11400),
(10, 5, 9, 3, 2200, 6600),
(11, 5, 11, 2, 5800, 11600),
(12, 5, 5, 4, 3800, 15200),
(13, 6, 2, 4, 3200, 12800),
(14, 6, 10, 1, 12500, 12500),
(15, 7, 4, 3, 2000, 6000),
(16, 7, 9, 6, 2200, 13200);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `empleados`
--

CREATE TABLE `empleados` (
  `id_empleado` int(11) NOT NULL,
  `nombre_empleado` varchar(150) NOT NULL,
  `id_rol` int(11) DEFAULT NULL,
  `fecha_ingreso` datetime DEFAULT current_timestamp(),
  `monto_pago` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `empleados`
--

INSERT INTO `empleados` (`id_empleado`, `nombre_empleado`, `id_rol`, `fecha_ingreso`, `monto_pago`) VALUES
(1, 'Sofía Ramírez Castillo', 1, '2023-01-15 08:00:00', 3500000),
(2, 'Diego Hernández Mora', 2, '2023-03-01 08:00:00', 1800000),
(3, 'Valentina Suárez Ríos', 2, '2023-06-10 08:00:00', 1800000),
(4, 'Andrés Felipe Rojas', 1, '2022-11-20 08:00:00', 3500000);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `estado_producto`
--

CREATE TABLE `estado_producto` (
  `id_estado` int(11) NOT NULL,
  `nombre_estado` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `estado_producto`
--

INSERT INTO `estado_producto` (`id_estado`, `nombre_estado`) VALUES
(1, 'Disponible'),
(2, 'Vencido'),
(3, 'Descontinuado'),
(4, 'Dañado');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `facturas`
--

CREATE TABLE `facturas` (
  `id_factura` int(11) NOT NULL,
  `id_empleado` int(11) DEFAULT NULL,
  `id_cliente` int(11) DEFAULT NULL,
  `fecha_fac` datetime DEFAULT current_timestamp(),
  `total_fac` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `facturas`
--

INSERT INTO `facturas` (`id_factura`, `id_empleado`, `id_cliente`, `fecha_fac`, `total_fac`) VALUES
(1, 2, 1, '2024-03-15 10:15:00', 26200),
(2, 3, 2, '2024-03-16 14:30:00', 18500),
(3, 2, 3, '2024-03-18 09:45:00', 41700),
(4, 3, 4, '2024-03-20 16:00:00', 22700),
(5, 2, 5, '2024-04-02 11:20:00', 34500),
(6, 3, 6, '2024-04-05 15:00:00', 27400),
(7, 2, 7, '2024-04-08 10:10:00', 19800);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `factura_compra`
--

CREATE TABLE `factura_compra` (
  `id_fac_compra` int(11) NOT NULL,
  `numero_fac_compra` varchar(50) DEFAULT NULL,
  `id_proveedor` int(11) DEFAULT NULL,
  `id_empleado` int(11) DEFAULT NULL,
  `fecha_fac_compra` datetime DEFAULT NULL,
  `valor_fac_compra` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `factura_compra`
--

INSERT INTO `factura_compra` (`id_fac_compra`, `numero_fac_compra`, `id_proveedor`, `id_empleado`, `fecha_fac_compra`, `valor_fac_compra`) VALUES
(1, 'FC-2024-001', 1, 4, '2024-01-10 09:00:00', 850000),
(2, 'FC-2024-002', 2, 4, '2024-02-05 10:30:00', 640000),
(3, 'FC-2024-003', 3, 1, '2024-03-12 11:00:00', 1150000);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `inventarios`
--

CREATE TABLE `inventarios` (
  `id_inventario` int(11) NOT NULL,
  `id_producto` int(11) DEFAULT NULL,
  `stock_actual` int(11) DEFAULT NULL,
  `condicion` varchar(100) DEFAULT NULL,
  `timestamp_ultima_actualizacion` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `inventarios`
--

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
(11, 11, 130, 'Buena', '2026-04-06 14:51:06');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `login`
--

CREATE TABLE `usuarios` (
  `id_usuarios` int(11) NOT NULL,
  `id_empleado` int(11) DEFAULT NULL,
  `username_log` varchar(50) DEFAULT NULL,
  `contrasena_log` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `login`
--

INSERT INTO `usuarios` (`id_usuarios`, `id_rol`, `username_log`, `contrasena_log`) VALUES
(1, 1, 'edwin.acosta', '123'),
(2, 1, 'nicolas.herran', '456'),
(3, 2, 'joshep,hernandez', '246'),
(4, 2, 'mariana.zarate', '135');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `movimientos`
--

CREATE TABLE `movimientos` (
  `id_movimiento` int(11) NOT NULL,
  `id_inventario` int(11) DEFAULT NULL,
  `id_tipo_mov` int(11) DEFAULT NULL,
  `id_empleado` int(11) DEFAULT NULL,
  `id_factura` int(11) DEFAULT NULL,
  `id_fac_compra` int(11) DEFAULT NULL,
  `cantidad_movimiento` int(11) DEFAULT NULL,
  `fecha_movimiento` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `movimientos`
--

INSERT INTO `movimientos` (`id_movimiento`, `id_inventario`, `id_tipo_mov`, `id_empleado`, `id_factura`, `id_fac_compra`, `cantidad_movimiento`, `fecha_movimiento`) VALUES
(1, 1, 1, 4, NULL, 1, 200, '2024-01-10 09:30:00'),
(2, 6, 1, 4, NULL, 1, 150, '2024-01-10 09:35:00'),
(3, 2, 1, 4, NULL, 2, 300, '2024-02-05 11:00:00'),
(4, 7, 1, 4, NULL, 2, 100, '2024-02-05 11:10:00'),
(5, 5, 1, 1, NULL, 3, 200, '2024-03-12 11:30:00'),
(6, 8, 1, 1, NULL, 3, 100, '2024-03-12 11:35:00'),
(7, 1, 2, 2, 1, NULL, 2, '2024-03-15 10:15:00'),
(8, 3, 2, 3, 2, NULL, 1, '2024-03-16 14:30:00'),
(9, 9, 1, 4, NULL, 1, 250, '2024-04-01 08:30:00'),
(10, 10, 1, 1, NULL, 3, 120, '2024-04-01 08:45:00'),
(11, 11, 1, 4, NULL, 2, 200, '2024-04-01 09:00:00'),
(12, 9, 2, 2, 5, NULL, 3, '2024-04-02 11:20:00'),
(13, 2, 2, 3, 6, NULL, 4, '2024-04-05 15:00:00'),
(14, 4, 2, 2, 7, NULL, 3, '2024-04-08 10:10:00');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `productos`
--

CREATE TABLE `productos` (
  `id_producto` int(11) NOT NULL,
  `nombre_producto` varchar(150) NOT NULL,
  `marca_producto` varchar(100) DEFAULT NULL,
  `id_categoria` int(11) DEFAULT NULL,
  `id_estado` int(11) DEFAULT NULL,
  `id_proveedor` int(11) NOT NULL,
  `precio_venta_prod` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `productos`
--

INSERT INTO `productos` (`id_producto`, `nombre_producto`, `marca_producto`, `id_categoria`, `id_estado`,`id_proveedor`, `precio_venta_prod`) VALUES
(1, 'Manzana Roja x kg', 'Frutas Frescas', 1, 1,1, 4500),
(2, 'Leche Entera x Lt', 'Alquería', 4, 1, 2, 3200),
(3, 'Arroz Blanco x 5kg', 'Roa', 3, 1, 1, 18500),
(4, 'Agua Mineral x 600ml', 'Cristal', 5, 1, 2, 2000),
(5, 'Jabón de Baño', 'Dove', 6, 1, 3, 3800),
(6, 'Zanahoria x kg', 'La Huerta', 2, 1, 1, 2800),
(7, 'Yogur Fresa x 200g', 'Alpina', 4, 2, 2, 2500),
(8, 'Shampoo Anticaspa x 400ml', 'Head & Shoulders', 6, 1, 3, 18900),
(9, 'Banano x kg', 'Frutas Frescas', 1, 1, 1, 2200),
(10, 'Detergente Líquido x 1Lt', 'Ariel', 6, 1, 3, 12500),
(11, 'Jugo de Naranja x 1Lt', 'Del Valle', 5, 1, 2, 5800);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `proveedores`
--

CREATE TABLE `proveedores` (
  `id_proveedor` int(11) NOT NULL,
  `nombre_empresa` varchar(150) NOT NULL,
  `nit` varchar(20) DEFAULT NULL,
  `telefono_principal` varchar(20) DEFAULT NULL,
  `email` varchar(150) DEFAULT NULL,
  `direccion` varchar(200) DEFAULT NULL,
  `ciudad` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `proveedores`
--

INSERT INTO `proveedores` (`id_proveedor`, `nombre_empresa`, `nit`, `telefono_principal`, `email`, `direccion`, `ciudad`) VALUES
(1, 'Distribuidora El Campo SAS', '900111222-1', '6011234567', 'ventas@elcampo.com', 'Bodega 5, Zona Industrial Norte', 'Bogotá'),
(2, 'Lácteos del Valle Ltda', '800333444-2', '6024569870', 'pedidos@lacteosvalle.com', 'Km 3 Vía Cali-Palmira', 'Cali'),
(3, 'Proviser Higiene y Aseo SAS', '901555666-3', '6055558877', 'comercial@proviser.com', 'Carrera 50 # 30-40', 'Medellín');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `rol`
--

CREATE TABLE `rol` (
  `id_rol` int(11) NOT NULL,
  `descripcion_rol` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `rol`
--

INSERT INTO `rol` (`id_rol`, `descripcion_rol`) VALUES
(1, 'Administrador'),
(2, 'Cajero');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tipo_movimiento`
--

CREATE TABLE `tipo_movimiento` (
  `id_tipo_mov` int(11) NOT NULL,
  `nombre_tipo_movimiento` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `tipo_movimiento`
--

INSERT INTO `tipo_movimiento` (`id_tipo_mov`, `nombre_tipo_movimiento`) VALUES
(1, 'Entrada'),
(2, 'Salida'),
(3, 'Devolución');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `categoria`
--
ALTER TABLE `categoria`
  ADD PRIMARY KEY (`id_categoria`);

--
-- Indices de la tabla `clientes`
--
ALTER TABLE `clientes`
  ADD PRIMARY KEY (`id_cliente`),
  ADD UNIQUE KEY `documento_identidad` (`documento_identidad`);

--
-- Indices de la tabla `detalle_factura`
--
ALTER TABLE `detalle_factura`
  ADD PRIMARY KEY (`id_detalle`),
  ADD KEY `id_factura` (`id_factura`),
  ADD KEY `id_producto` (`id_producto`);

--
-- Indices de la tabla `empleados`
--
ALTER TABLE `empleados`
  ADD PRIMARY KEY (`id_empleado`),
  ADD KEY `id_rol` (`id_rol`);

--
-- Indices de la tabla `estado_producto`
--
ALTER TABLE `estado_producto`
  ADD PRIMARY KEY (`id_estado`);

--
-- Indices de la tabla `facturas`
--
ALTER TABLE `facturas`
  ADD PRIMARY KEY (`id_factura`),
  ADD KEY `id_empleado` (`id_empleado`),
  ADD KEY `id_cliente` (`id_cliente`);

--
-- Indices de la tabla `factura_compra`
--
ALTER TABLE `factura_compra`
  ADD PRIMARY KEY (`id_fac_compra`),
  ADD KEY `id_proveedor` (`id_proveedor`),
  ADD KEY `id_empleado` (`id_empleado`);

--
-- Indices de la tabla `inventarios`
--
ALTER TABLE `inventarios`
  ADD PRIMARY KEY (`id_inventario`),
  ADD KEY `id_producto` (`id_producto`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id_usuarios`),
  ADD UNIQUE KEY `username_log` (`username_log`),
  ADD KEY `id_rol` (`id_rol`);

--
-- Indices de la tabla `movimientos`
--
ALTER TABLE `movimientos`
  ADD PRIMARY KEY (`id_movimiento`),
  ADD KEY `id_inventario` (`id_inventario`),
  ADD KEY `id_tipo_mov` (`id_tipo_mov`),
  ADD KEY `id_empleado` (`id_empleado`),
  ADD KEY `id_factura` (`id_factura`),
  ADD KEY `id_fac_compra` (`id_fac_compra`);

--
-- Indices de la tabla `productos`
--
ALTER TABLE `productos`
  ADD PRIMARY KEY (`id_producto`),
  ADD KEY `id_categoria` (`id_categoria`),
  ADD KEY `id_proveedor` (`id_proveedor`),
  ADD KEY `id_estado` (`id_estado`);

--
-- Indices de la tabla `proveedores`
--
ALTER TABLE `proveedores`
  ADD PRIMARY KEY (`id_proveedor`),
  ADD UNIQUE KEY `nit` (`nit`);

--
-- Indices de la tabla `rol`
--
ALTER TABLE `rol`
  ADD PRIMARY KEY (`id_rol`);

--
-- Indices de la tabla `tipo_movimiento`
--
ALTER TABLE `tipo_movimiento`
  ADD PRIMARY KEY (`id_tipo_mov`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `categoria`
--
ALTER TABLE `categoria`
  MODIFY `id_categoria` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de la tabla `clientes`
--
ALTER TABLE `clientes`
  MODIFY `id_cliente` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT de la tabla `detalle_factura`
--
ALTER TABLE `detalle_factura`
  MODIFY `id_detalle` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT de la tabla `empleados`
--
ALTER TABLE `empleados`
  MODIFY `id_empleado` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `estado_producto`
--
ALTER TABLE `estado_producto`
  MODIFY `id_estado` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `facturas`
--
ALTER TABLE `facturas`
  MODIFY `id_factura` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT de la tabla `factura_compra`
--
ALTER TABLE `factura_compra`
  MODIFY `id_fac_compra` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `inventarios`
--
ALTER TABLE `inventarios`
  MODIFY `id_inventario` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT de la tabla `login`
--
ALTER TABLE `login`
  MODIFY `id_login` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `movimientos`
--
ALTER TABLE `movimientos`
  MODIFY `id_movimiento` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT de la tabla `productos`
--
ALTER TABLE `productos`
  MODIFY `id_producto` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT de la tabla `proveedores`
--
ALTER TABLE `proveedores`
  MODIFY `id_proveedor` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `rol`
--
ALTER TABLE `rol`
  MODIFY `id_rol` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `tipo_movimiento`
--
ALTER TABLE `tipo_movimiento`
  MODIFY `id_tipo_mov` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `detalle_factura`
--
ALTER TABLE `detalle_factura`
  ADD CONSTRAINT `detalle_factura_ibfk_1` FOREIGN KEY (`id_factura`) REFERENCES `facturas` (`id_factura`),
  ADD CONSTRAINT `detalle_factura_ibfk_2` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`);

--
-- Filtros para la tabla `empleados`
--
ALTER TABLE `empleados`
  ADD CONSTRAINT `empleados_ibfk_1` FOREIGN KEY (`id_rol`) REFERENCES `rol` (`id_rol`);

--
-- Filtros para la tabla `facturas`
--
ALTER TABLE `facturas`
  ADD CONSTRAINT `facturas_ibfk_1` FOREIGN KEY (`id_empleado`) REFERENCES `empleados` (`id_empleado`),
  ADD CONSTRAINT `facturas_ibfk_2` FOREIGN KEY (`id_cliente`) REFERENCES `clientes` (`id_cliente`);

--
-- Filtros para la tabla `factura_compra`
--
ALTER TABLE `factura_compra`
  ADD CONSTRAINT `factura_compra_ibfk_1` FOREIGN KEY (`id_proveedor`) REFERENCES `proveedores` (`id_proveedor`),
  ADD CONSTRAINT `factura_compra_ibfk_2` FOREIGN KEY (`id_empleado`) REFERENCES `empleados` (`id_empleado`);

--
-- Filtros para la tabla `inventarios`
--
ALTER TABLE `inventarios`
  ADD CONSTRAINT `inventarios_ibfk_1` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`);

--
-- Filtros para la tabla `login`
--
ALTER TABLE `usuarios`
  ADD CONSTRAINT `login_ibfk_1` FOREIGN KEY (`id_rol`) REFERENCES `rol` (`id_rol`);

--
-- Filtros para la tabla `movimientos`
--
ALTER TABLE `movimientos`
  ADD CONSTRAINT `movimientos_ibfk_1` FOREIGN KEY (`id_inventario`) REFERENCES `inventarios` (`id_inventario`),
  ADD CONSTRAINT `movimientos_ibfk_2` FOREIGN KEY (`id_tipo_mov`) REFERENCES `tipo_movimiento` (`id_tipo_mov`),
  ADD CONSTRAINT `movimientos_ibfk_3` FOREIGN KEY (`id_empleado`) REFERENCES `empleados` (`id_empleado`),
  ADD CONSTRAINT `movimientos_ibfk_4` FOREIGN KEY (`id_factura`) REFERENCES `facturas` (`id_factura`),
  ADD CONSTRAINT `movimientos_ibfk_5` FOREIGN KEY (`id_fac_compra`) REFERENCES `factura_compra` (`id_fac_compra`);

--
-- Filtros para la tabla `productos`
--
ALTER TABLE `productos`
  ADD CONSTRAINT `productos_ibfk_1` FOREIGN KEY (`id_categoria`) REFERENCES `categoria` (`id_categoria`),
  ADD CONSTRAINT `productos_ibfk_3` FOREIGN KEY (`id_estado`) REFERENCES `estado_producto` (`id_estado`),
  ADD CONSTRAINT `productos_ibfk_2` FOREIGN KEY (`id_proveedor`) REFERENCES `proveedores` (`id_proveedor`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
