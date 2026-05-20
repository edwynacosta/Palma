import datetime
import os  # Necesario para limpiar la pantalla

def calcular_total(cantidad, precio):
    return cantidad * precio

carrito = [] 

while True:
    # --- LIMPIAR PANTALLA ---
    # Esto borra lo anterior para que la lista parezca actualizarse en el mismo lugar
    os.system('cls' if os.name == 'nt' else 'clear')

    print("\n---          CAJA PALMA          ---")
    
    # --- MOSTRAR LISTA ACTUAL (Lo que ya se ha registrado) ---
    if carrito:
        print("\nPRODUCTOS EN EL CARRITO:")
        print(f"{'CANT':<5} | {'PRODUCTO':<15} | {'UNIT.':<8} | {'TOTAL':<8}")
        print("-" * 50)
        for c, n, u, t in carrito:
            print(f"{c:<5} | {n:<15} | ${u:<7.2f} | ${t:<7.2f}")
        print("-" * 50)
    else:
        print("\n--- CARRITO VACÍO ---")

    # --- REGISTRA TUS PRODUCTOS ABAJO ---
    print("\nREGISTRA UN NUEVO PRODUCTO:")
    nombre = input("Nombre: ")
    cantidad = int(input(f"Cantidad de {nombre}: "))
    precio_unitario = float(input(f"Precio unitario: "))
    
    precio_total_producto = calcular_total(cantidad, precio_unitario)
    
    item = (cantidad, nombre, precio_unitario, precio_total_producto)
    carrito.append(item) 

    # Preguntar si desea continuar
    print("\n¿Deseas agregar algo más?")
    print("1. Finalizar y Generar Factura")
    print("2. Seguir registrando productos")
    opcion = input("Selecciona (1 o 2): ")

    if opcion == "1":
        break

# --- GENERACIÓN DE FACTURA FINAL ---
os.system('cls' if os.name == 'nt' else 'clear')
ahora = datetime.datetime.now()
fecha_formateada = ahora.strftime("%d/%m/%Y %H:%M:%S")

print("\n" + "X" * 50)
print("             FACTURA DE VENTA")
print(f"  Fecha: {fecha_formateada}")
print("X" * 50)
print(f"{'CANT':<5} | {'PRODUCTO':<15} | {'UNIT.':<8} | {'TOTAL':<8}")
print("-" * 50)

total_general = 0
for cant, nom, p_unit, p_total in carrito:
    print(f"{cant:<5} | {nom:<15} | ${p_unit:<7.2f} | ${p_total:<7.2f}")
    total_general += p_total

print("-" * 50)
print(f"{'TOTAL A PAGAR:':>32} ${total_general:>9.2f}")
print("X" * 50)
print("        ¡Gracias por su compra!")