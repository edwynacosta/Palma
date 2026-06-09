class InventarioModelo:
    def __init__(self, conexion):
        self.conexion = conexion

    def _ping(self):
        if hasattr(self.conexion, "ping"):
            self.conexion.ping(reconnect=True)

    def obtener_catalogos(self):
        self._ping()
        with self.conexion.cursor() as cursor:
            cursor.execute("SELECT id_categoria, nombre_categoria FROM categoria ORDER BY nombre_categoria")
            categorias = cursor.fetchall()

            cursor.execute("SELECT id_estado, nombre_estado FROM estado_producto ORDER BY nombre_estado")
            estados = cursor.fetchall()

            cursor.execute("SELECT id_proveedor, nombre_empresa FROM proveedores ORDER BY nombre_empresa")
            proveedores = cursor.fetchall()

        return {
            "categorias": categorias,
            "estados": estados,
            "proveedores": proveedores,
        }

    def listar_productos(self, texto="", id_categoria=None, id_estado=None):
        self._ping()
        condiciones = []
        parametros = []

        texto = (texto or "").strip()
        if texto:
            condiciones.append(
                "(p.nombre_producto LIKE %s OR p.marca_producto LIKE %s OR pr.nombre_empresa LIKE %s)"
            )
            busqueda = f"%{texto}%"
            parametros.extend([busqueda, busqueda, busqueda])

        if id_categoria:
            condiciones.append("p.id_categoria = %s")
            parametros.append(id_categoria)

        if id_estado:
            condiciones.append("p.id_estado = %s")
            parametros.append(id_estado)

        where_sql = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""
        sql = f"""
            SELECT
                p.id_producto,
                p.nombre_producto,
                p.marca_producto,
                p.id_categoria,
                c.nombre_categoria,
                p.id_estado,
                e.nombre_estado,
                p.precio_venta_prod,
                p.id_proveedor,
                pr.nombre_empresa,
                i.id_inventario,
                COALESCE(i.stock_actual, 0) AS stock_actual,
                COALESCE(i.condicion, 'Sin revisar') AS condicion,
                i.timestamp_ultima_actualizacion
            FROM productos p
            LEFT JOIN categoria c ON c.id_categoria = p.id_categoria
            LEFT JOIN estado_producto e ON e.id_estado = p.id_estado
            LEFT JOIN proveedores pr ON pr.id_proveedor = p.id_proveedor
            LEFT JOIN (
                SELECT inv.*
                FROM inventarios inv
                INNER JOIN (
                    SELECT id_producto, MAX(id_inventario) AS id_inventario
                    FROM inventarios
                    GROUP BY id_producto
                ) ult ON ult.id_inventario = inv.id_inventario
            ) i ON i.id_producto = p.id_producto
            {where_sql}
            ORDER BY p.nombre_producto ASC
        """

        with self.conexion.cursor() as cursor:
            cursor.execute(sql, parametros)
            return cursor.fetchall()

    def obtener_sugerencias_busqueda(self):
        self._ping()
        sql = """
            SELECT DISTINCT sugerencia
            FROM (
                SELECT nombre_producto AS sugerencia FROM productos
                UNION ALL
                SELECT marca_producto AS sugerencia FROM productos WHERE marca_producto IS NOT NULL
                UNION ALL
                SELECT nombre_empresa AS sugerencia FROM proveedores
            ) base
            WHERE sugerencia IS NOT NULL AND sugerencia <> ''
            ORDER BY sugerencia ASC
        """
        with self.conexion.cursor() as cursor:
            cursor.execute(sql)
            return [fila["sugerencia"] for fila in cursor.fetchall()]

    def guardar_producto(self, datos):
        self._ping()
        id_producto = datos.get("id_producto")

        with self.conexion.cursor() as cursor:
            if id_producto:
                cursor.execute(
                    """
                    UPDATE productos
                    SET nombre_producto = %s,
                        marca_producto = %s,
                        id_categoria = %s,
                        id_estado = %s,
                        precio_venta_prod = %s,
                        id_proveedor = %s
                    WHERE id_producto = %s
                    """,
                    (
                        datos["nombre_producto"],
                        datos["marca_producto"],
                        datos["id_categoria"],
                        datos["id_estado"],
                        datos["precio_venta_prod"],
                        datos["id_proveedor"],
                        id_producto,
                    ),
                )

                if datos.get("id_inventario"):
                    cursor.execute(
                        """
                        UPDATE inventarios
                        SET stock_actual = %s,
                            condicion = %s
                        WHERE id_inventario = %s
                        """,
                        (
                            datos["stock_actual"],
                            datos["condicion"],
                            datos["id_inventario"],
                        ),
                    )
                else:
                    cursor.execute(
                        """
                        INSERT INTO inventarios (id_producto, stock_actual, condicion)
                        VALUES (%s, %s, %s)
                        """,
                        (id_producto, datos["stock_actual"], datos["condicion"]),
                    )
            else:
                cursor.execute(
                    """
                    INSERT INTO productos (
                        nombre_producto,
                        marca_producto,
                        id_categoria,
                        id_estado,
                        precio_venta_prod,
                        id_proveedor
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        datos["nombre_producto"],
                        datos["marca_producto"],
                        datos["id_categoria"],
                        datos["id_estado"],
                        datos["precio_venta_prod"],
                        datos["id_proveedor"],
                    ),
                )
                id_producto = cursor.lastrowid
                cursor.execute(
                    """
                    INSERT INTO inventarios (id_producto, stock_actual, condicion)
                    VALUES (%s, %s, %s)
                    """,
                    (id_producto, datos["stock_actual"], datos["condicion"]),
                )

        self.conexion.commit()
        return id_producto
