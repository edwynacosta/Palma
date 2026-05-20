def calcular_total(cantidad, precio):
    return cantidad * precio

carrito = [] 
total_factura = 0 

print("\n---      FACTURACIÓN       ---")
print("--- REGISTRA LOS PRODUCTOS ---")

while True:
    nombre = input("Ingresa el nombre del producto: ")
    cantidad = int(input(f"¿Cuántos {nombre} llevas?: "))
    precio = float(input(f"Precio de cada {nombre}: "))
    
    item = (nombre, cantidad, precio) # ITEMS: GUARDAMOS EL PRODUCTO
    carrito.append(item) 

    subtotal = calcular_total(cantidad, precio)
    print(f"Subtotal por {nombre}: ${subtotal}")

    print("\n1. Finalizar compra")
    print("2. Continuar comprando")
    opcion = input("Selecciona (1 o 2): ")

    if opcion == "1":
        break

# RESUMEN DE FACTURA
print("\n" + "="*35)
print("       RESUMEN DE COMPRA")
print("="*35)

total_general = 0

for item in carrito:
    sub_item = item[1] * item[2] # CALCULAMOS EL SUBTOTAL DE CADA ITEM GUARDADO
    print(f"{item[1]}x {item[0]} .......... ${sub_item:.2f}")
    
    total_general += sub_item # SUMAR EL SUBTOTAL, NO SOLO AL PRECIO

print("-" * 35)
print(f"TOTAL A PAGAR:       ${total_general:.2f}")
print("="*35)