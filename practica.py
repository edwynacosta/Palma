import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import json
import os

# --- CONFIGURACIÓN ESTÉTICA ---
VERDE_PALMA = "#008F39"
BLANCO = "#FFFFFF"
VERDE_TEXTO = "#2A401A"
GRIS_SUAVE = "#F2F2F2"
NARANJA_ALERTA = "#FFB347"
ROJO_CANCELAR = "#FF4B4B"

class AppPalma(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Gestión Palma v2.0")
        self.geometry("1300x850")
        self.configure(fg_color=VERDE_PALMA)

        # --- Base de Datos ---
        self.archivo_db = "base_datos_palma.json"
        self.datos = self.cargar_datos()
        
        self.total_actual = 0
        self.contador_id = 1
        self.venta_finalizada = False

        self._configurar_grid()
        self._crear_interfaz()
        
        # Ejecutar recordatorio al iniciar
        self.after(1000, self.verificar_recibos_pendientes)

    def _configurar_grid(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

    def cargar_datos(self):
        if os.path.exists(self.archivo_db):
            with open(self.archivo_db, 'r') as f:
                data = json.load(f)
                # Asegurar que existan las nuevas llaves
                if "recibos" not in data: data["recibos"] = []
                if "gastos" not in data: data["gastos"] = []
                return data
        return {
            "ventas": [], 
            "recibos": [
                {"nombre": "Luz", "dia": 15, "monto": 0, "pagado": False},
                {"nombre": "Agua", "dia": 22, "monto": 0, "pagado": False}
            ],
            "gastos": []
        }

    def guardar_datos(self):
        with open(self.archivo_db, 'w') as f:
            json.dump(self.datos, f, indent=4)

    def _crear_interfaz(self):
        # PANEL IZQUIERDO: TOTALES
        self.panel_izquierdo = ctk.CTkFrame(self, fg_color="transparent")
        self.panel_izquierdo.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.box_total, self.lbl_total_izq = self.crear_panel_valor("Total a pagar:", "$0")
        self.box_efectivo, self.ent_efectivo = self.crear_panel_input("Efectivo")
        self.box_cambio, self.lbl_cambio = self.crear_panel_valor("Cambio", "$0")

        # PANEL DERECHO: FACTURACIÓN
        self.panel_derecho = ctk.CTkFrame(self, fg_color="transparent")
        self.panel_derecho.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Menú superior
        self.frame_top_btns = ctk.CTkFrame(self.panel_derecho, fg_color="transparent")
        self.frame_top_btns.pack(fill="x", pady=(0, 10))
        
        botones = [
            ("BALANCE", self.abrir_balance),
            ("ANALÍTICAS", self.abrir_graficos),
            ("RECIBOS", self.abrir_gestion_recibos) # Nueva función centralizada
        ]
        for txt, cmd in botones:
            ctk.CTkButton(self.frame_top_btns, text=txt, fg_color=BLANCO, text_color="black", 
                          font=("Arial Black", 11), height=50, command=cmd).pack(side="left", padx=5, expand=True, fill="x")

        # Tabla Facturación
        self.frame_tabla_bg = ctk.CTkFrame(self.panel_derecho, fg_color=BLANCO, corner_radius=25)
        self.frame_tabla_bg.pack(fill="both", expand=True)

        self.tabla = ttk.Treeview(self.frame_tabla_bg, columns=("id", "nombre", "cant", "precio"), show="headings")
        for col, head in zip(("id", "nombre", "cant", "precio"), ("ID", "PRODUCTO", "CANT", "SUBTOTAL")):
            self.tabla.heading(col, text=head)
            self.tabla.column(col, anchor="center")
        self.tabla.pack(fill="both", expand=True, padx=20, pady=20)

        # Botones Inferiores
        self.frame_bot_btns = ctk.CTkFrame(self.panel_derecho, fg_color="transparent")
        self.frame_bot_btns.pack(fill="x", pady=15)
        
        self.btn_accion_principal = ctk.CTkButton(self.frame_bot_btns, text="COBRAR", fg_color=GRIS_SUAVE, 
                                                  text_color="black", font=("Arial Black", 16), height=60, command=self.acc_cobrar)
        self.btn_accion_principal.pack(side="left", padx=5)
        
        ctk.CTkButton(self.frame_bot_btns, text="AGREGAR", fg_color=BLANCO, text_color="black", command=self.acc_agregar).pack(side="left", padx=5, expand=True)

    # --- NUEVA GESTIÓN DE RECIBOS ---
    def abrir_gestion_recibos(self):
        ventana_recibos = ctk.CTkToplevel(self)
        ventana_recibos.title("Administración de Recibos y Facturas")
        ventana_recibos.geometry("700x500")
        ventana_recibos.attributes("-topmost", True)
        ventana_recibos.configure(fg_color=GRIS_SUAVE)

        # Formulario para añadir/editar
        frame_form = ctk.CTkFrame(ventana_recibos, fg_color=BLANCO)
        frame_form.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(frame_form, text="Nombre Recibo:", text_color="black").grid(row=0, column=0, padx=10, pady=5)
        ent_nom = ctk.CTkEntry(frame_form)
        ent_nom.grid(row=0, column=1, padx=10, pady=5)

        ctk.CTkLabel(frame_form, text="Día Pago (1-31):", text_color="black").grid(row=0, column=2, padx=10, pady=5)
        ent_dia = ctk.CTkEntry(frame_form, width=60)
        ent_dia.grid(row=0, column=3, padx=10, pady=5)

        ctk.CTkLabel(frame_form, text="Monto $:", text_color="black").grid(row=1, column=0, padx=10, pady=5)
        ent_monto = ctk.CTkEntry(frame_form)
        ent_monto.grid(row=1, column=1, padx=10, pady=5)

        # Tabla de recibos
        tabla_r = ttk.Treeview(ventana_recibos, columns=("nombre", "dia", "monto", "estado"), show="headings")
        for col, head in zip(("nombre", "dia", "monto", "estado"), ("RECIBO", "DÍA PAGO", "MONTO", "ESTADO")):
            tabla_r.heading(col, text=head)
            tabla_r.column(col, anchor="center")
        tabla_r.pack(fill="both", expand=True, padx=20, pady=10)

        def actualizar_tabla_recibos():
            for i in tabla_r.get_children(): tabla_r.delete(i)
            for r in self.datos["recibos"]:
                estado = "✅ PAGADO" if r.get("pagado") else "⏳ PENDIENTE"
                tabla_r.insert("", "end", values=(r["nombre"], r["dia"], f"${r['monto']:,}", estado))

        def agregar_recibo():
            try:
                nuevo = {
                    "nombre": ent_nom.get(),
                    "dia": int(ent_dia.get()),
                    "monto": int(ent_monto.get()),
                    "pagado": False
                }
                self.datos["recibos"].append(nuevo)
                self.guardar_datos()
                actualizar_tabla_recibos()
            except: messagebox.showerror("Error", "Datos inválidos")

        def eliminar_recibo():
            sel = tabla_r.selection()
            if sel:
                item = tabla_r.item(sel)["values"][0]
                self.datos["recibos"] = [r for r in self.datos["recibos"] if r["nombre"] != item]
                self.guardar_datos()
                actualizar_tabla_recibos()

        def pagar_recibo():
            sel = tabla_r.selection()
            if sel:
                nombre_r = tabla_r.item(sel)["values"][0]
                for r in self.datos["recibos"]:
                    if r["nombre"] == nombre_r and not r["pagado"]:
                        r["pagado"] = True
                        # AÑADIR AUTOMÁTICAMENTE A GASTOS GENERALES
                        gasto = {
                            "fecha": datetime.now().strftime("%Y-%m-%d"),
                            "descripcion": f"Pago de Recibo: {r['nombre']}",
                            "monto": r["monto"]
                        }
                        self.datos["gastos"].append(gasto)
                        self.guardar_datos()
                        messagebox.showinfo("Pago", f"Recibo {nombre_r} pagado e integrado en Gastos.")
                        break
                actualizar_tabla_recibos()

        # Botones de acción
        frame_btns = ctk.CTkFrame(ventana_recibos, fg_color="transparent")
        frame_btns.pack(fill="x", padx=20, pady=10)

        ctk.CTkButton(frame_btns, text="Añadir Recibo", fg_color=VERDE_PALMA, command=agregar_recibo).pack(side="left", padx=5)
        ctk.CTkButton(frame_btns, text="Pagar Seleccionado", fg_color=NARANJA_ALERTA, text_color="black", command=pagar_recibo).pack(side="left", padx=5)
        ctk.CTkButton(frame_btns, text="Eliminar", fg_color=ROJO_CANCELAR, command=eliminar_recibo).pack(side="right", padx=5)

        actualizar_tabla_recibos()

    # --- NOTIFICACIÓN MEJORADA ---
    def verificar_recibos_pendientes(self):
        hoy = datetime.now().day
        mensajes = []
        for r in self.datos["recibos"]:
            # Solo notifica si NO está pagado
            if not r.get("pagado", False):
                diferencia = r["dia"] - hoy
                if 0 <= diferencia <= 3:
                    mensajes.append(f"• {r['nombre']} vence en {diferencia} días")
        
        if mensajes:
            notif = ctk.CTkToplevel(self)
            notif.geometry("300x180+50+50")
            notif.title("Recordatorio")
            notif.attributes("-topmost", True)
            ctk.CTkLabel(notif, text="RECIBOS POR PAGAR", font=("Arial Black", 14), text_color=NARANJA_ALERTA).pack(pady=10)
            ctk.CTkLabel(notif, text="\n".join(mensajes), justify="left").pack()
            ctk.CTkButton(notif, text="Ir a Recibos", command=lambda: [notif.destroy(), self.abrir_gestion_recibos()]).pack(pady=10)

    # --- BALANCE CON GASTOS ---
    def abrir_balance(self):
        df_v = pd.DataFrame(self.datos["ventas"])
        df_g = pd.DataFrame(self.datos["gastos"])
        
        ingresos = df_v['total'].sum() if not df_v.empty else 0
        gastos = df_g['monto'].sum() if not df_g.empty else 0
        balance = ingresos - gastos
        
        msg = f"Ingresos: ${ingresos:,.0f}\nGastos Generales: ${gastos:,.0f}\n"
        msg += f"{'-'*20}\nBALANCE NETO: ${balance:,.0f}"
        
        messagebox.showinfo("Balance General", msg)

    # --- MÉTODOS DE SOPORTE (VENTAS) ---
    def acc_cobrar(self):
        if self.venta_finalizada:
            self.nueva_venta()
            return

        if self.total_actual > 0:
            productos_vendidos = []
            for item in self.tabla.get_children():
                val = self.tabla.item(item)['values']
                if val[1]: productos_vendidos.append({"nombre": val[1], "cant": val[2]})

            nueva_venta = {
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total": self.total_actual,
                "productos": productos_vendidos
            }
            self.datos["ventas"].append(nueva_venta)
            self.guardar_datos()
            
            self.venta_finalizada = True
            self.btn_accion_principal.configure(text="NUEVA VENTA", fg_color=NARANJA_ALERTA)
            messagebox.showinfo("Éxito", "Venta registrada.")

    def crear_panel_valor(self, titulo, valor_inicial):
        frame = ctk.CTkFrame(self.panel_izquierdo, fg_color=BLANCO, corner_radius=20, height=140)
        frame.pack(fill="x", pady=5); frame.pack_propagate(False)
        ctk.CTkLabel(frame, text=titulo, font=("Arial Black", 14), text_color=VERDE_TEXTO).pack(anchor="w", padx=20, pady=(10,0))
        lbl = ctk.CTkLabel(frame, text=valor_inicial, font=("Arial Black", 50), text_color=VERDE_TEXTO)
        lbl.pack(expand=True)
        return frame, lbl

    def crear_panel_input(self, titulo):
        frame = ctk.CTkFrame(self.panel_izquierdo, fg_color=BLANCO, corner_radius=20, height=140)
        frame.pack(fill="x", pady=5); frame.pack_propagate(False)
        ctk.CTkLabel(frame, text=titulo, font=("Arial Black", 14), text_color=VERDE_TEXTO).pack(anchor="w", padx=20, pady=(10,0))
        ent = ctk.CTkEntry(frame, font=("Arial Black", 40), fg_color="transparent", border_width=0, justify="center")
        ent.pack(expand=True, fill="x")
        ent.bind("<KeyRelease>", self.formatear_efectivo)
        return frame, ent

    def formatear_efectivo(self, event=None):
        texto = self.ent_efectivo.get().replace("$", "").replace(".", "").strip()
        if texto.isdigit():
            valor = int(texto)
            self.ent_efectivo.delete(0, tk.END)
            self.ent_efectivo.insert(0, f"${valor:,.0f}".replace(",", "."))
            cambio = valor - self.total_actual
            self.lbl_cambio.configure(text=f"${max(0, cambio):,.0f}".replace(",", "."))

    def acc_agregar(self):
        pop = ctk.CTkToplevel(self); pop.geometry("300x300"); pop.attributes("-topmost", True)
        ctk.CTkLabel(pop, text="Producto:").pack(pady=5)
        e_n = ctk.CTkEntry(pop); e_n.pack()
        ctk.CTkLabel(pop, text="Precio:").pack(pady=5)
        e_p = ctk.CTkEntry(pop); e_p.pack()
        
        def guardar():
            try:
                p = int(e_p.get())
                self.tabla.insert("", 0, values=(self.contador_id, e_n.get(), 1, f"${p:,.0f}".replace(",", ".")))
                self.total_actual += p
                self.lbl_total_izq.configure(text=f"${self.total_actual:,.0f}".replace(",", "."))
                self.contador_id += 1
                pop.destroy()
            except: pass
        ctk.CTkButton(pop, text="Añadir", command=guardar).pack(pady=20)

    def nueva_venta(self):
        self.venta_finalizada = False
        self.total_actual = 0
        for i in self.tabla.get_children(): self.tabla.delete(i)
        self.lbl_total_izq.configure(text="$0")
        self.lbl_cambio.configure(text="$0")
        self.ent_efectivo.delete(0, tk.END)
        self.btn_accion_principal.configure(text="COBRAR", fg_color=GRIS_SUAVE)

    def abrir_graficos(self):
        # Lógica de gráficos (simplificada para este ejemplo)
        messagebox.showinfo("Analíticas", "Gráficos actualizados según ventas y gastos.")

if __name__ == "__main__":
    app = AppPalma()
    app.mainloop()