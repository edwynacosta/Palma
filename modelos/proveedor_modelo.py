class ProveedorModelo:
    def __init__(self, conexion):
        self.conexion = conexion

    def _ping(self):
        if hasattr(self.conexion, "ping"):
            self.conexion.ping(reconnect=True)

    def listar_proveedores(self, texto=""):
        self._ping()
        condiciones = []
        parametros = []

        texto = (texto or "").strip()
        if texto:
            condiciones.append(
                """
                (pr.nombre_empresa LIKE %s OR pr.nit LIKE %s OR pr.telefono_principal LIKE %s
                 OR pr.email LIKE %s OR pr.ciudad LIKE %s)
                """
            )
            busqueda = f"%{texto}%"
            parametros.extend([busqueda, busqueda, busqueda, busqueda, busqueda])

        where_sql = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""
        sql = f"""
            SELECT
                pr.id_proveedor,
                pr.nombre_empresa,
                pr.nit,
                pr.telefono_principal,
                pr.email,
                pr.direccion,
                pr.ciudad,
                COUNT(p.id_producto) AS total_productos
            FROM proveedores pr
            LEFT JOIN productos p ON p.id_proveedor = pr.id_proveedor
            {where_sql}
            GROUP BY
                pr.id_proveedor,
                pr.nombre_empresa,
                pr.nit,
                pr.telefono_principal,
                pr.email,
                pr.direccion,
                pr.ciudad
            ORDER BY pr.nombre_empresa ASC
        """

        with self.conexion.cursor() as cursor:
            cursor.execute(sql, parametros)
            return cursor.fetchall()

    def listar_productos_proveedor(self, id_proveedor):
        self._ping()
        sql = """
            SELECT
                p.id_producto,
                p.nombre_producto,
                p.marca_producto,
                c.nombre_categoria,
                e.nombre_estado,
                p.precio_venta_prod,
                COALESCE(i.stock_actual, 0) AS stock_actual
            FROM productos p
            LEFT JOIN categoria c ON c.id_categoria = p.id_categoria
            LEFT JOIN estado_producto e ON e.id_estado = p.id_estado
            LEFT JOIN (
                SELECT inv.*
                FROM inventarios inv
                INNER JOIN (
                    SELECT id_producto, MAX(id_inventario) AS id_inventario
                    FROM inventarios
                    GROUP BY id_producto
                ) ult ON ult.id_inventario = inv.id_inventario
            ) i ON i.id_producto = p.id_producto
            WHERE p.id_proveedor = %s
            ORDER BY p.nombre_producto ASC
        """
        with self.conexion.cursor() as cursor:
            cursor.execute(sql, (id_proveedor,))
            return cursor.fetchall()