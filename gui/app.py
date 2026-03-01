# gui/app.py
"""
Interfaz gráfica principal del sistema GIC usando Tkinter.
Permite crear, visualizar, buscar y eliminar clientes.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from models.cliente_regular import ClienteRegular
from models.cliente_premium import ClientePremium
from models.cliente_corporativo import ClienteCorporativo
from database.db_manager import DatabaseManager
from utils.json_manager import JsonManager, CsvManager
from utils.api_client import enviar_email_bienvenida
from utils.validaciones import (
    EmailDuplicadoError, DatosInvalidosError, ClienteNoEncontradoError
)
from utils.logger import logger

# ── Paleta de colores ──────────────────────────────────────
COLOR_PRIMARIO   = "#1A73E8"
COLOR_SECUNDARIO = "#F1F3F4"
COLOR_EXITO      = "#34A853"
COLOR_PELIGRO    = "#EA4335"
COLOR_TEXTO      = "#202124"
COLOR_BLANCO     = "#FFFFFF"
FUENTE_TITULO    = ("Arial", 14, "bold")
FUENTE_NORMAL    = ("Arial", 10)
FUENTE_PEQUEÑA   = ("Arial", 9)


class App(tk.Tk):
    """Ventana principal del sistema GIC."""

    def __init__(self):
        super().__init__()
        self.title("🏢 Gestor Inteligente de Clientes (GIC) — SolutionTech")
        self.geometry("1000x650")
        self.resizable(True, True)
        self.configure(bg=COLOR_SECUNDARIO)

        self.db  = DatabaseManager()
        self.json_mgr = JsonManager()
        self.csv_mgr  = CsvManager()

        self._construir_encabezado()
        self._construir_panel_formulario()
        self._construir_panel_tabla()
        self._construir_barra_estado()
        self._cargar_tabla()

    # ──────────────────────────────────────────────
    # CONSTRUCCIÓN DE UI
    # ──────────────────────────────────────────────

    def _construir_encabezado(self):
        """Barra superior con título y estadísticas."""
        frame = tk.Frame(self, bg=COLOR_PRIMARIO, pady=10)
        frame.pack(fill="x")

        tk.Label(frame,
                 text="🏢  Gestor Inteligente de Clientes",
                 font=("Arial", 16, "bold"),
                 bg=COLOR_PRIMARIO, fg=COLOR_BLANCO
                 ).pack(side="left", padx=20)

        self.lbl_stats = tk.Label(frame, text="", font=FUENTE_PEQUEÑA,
                                   bg=COLOR_PRIMARIO, fg=COLOR_BLANCO)
        self.lbl_stats.pack(side="right", padx=20)

    def _construir_panel_formulario(self):
        """Panel izquierdo: formulario de nuevo cliente."""
        frame_outer = tk.Frame(self, bg=COLOR_SECUNDARIO)
        frame_outer.pack(side="left", fill="y", padx=10, pady=10)

        frame = tk.LabelFrame(frame_outer, text=" ➕ Nuevo Cliente ",
                               font=FUENTE_TITULO, bg=COLOR_BLANCO,
                               fg=COLOR_PRIMARIO, padx=15, pady=15)
        frame.pack(fill="both", expand=True)

        # ── Campos ──
        self.entries = {}
        campos = [
            ("Nombre *",    "nombre"),
            ("Email *",     "email"),
            ("Teléfono *",  "telefono"),
            ("Dirección",   "direccion"),
        ]
        for i, (label, key) in enumerate(campos):
            tk.Label(frame, text=label, font=FUENTE_NORMAL,
                     bg=COLOR_BLANCO, fg=COLOR_TEXTO, anchor="w"
                     ).grid(row=i, column=0, sticky="w", pady=4)
            entry = tk.Entry(frame, width=28, font=FUENTE_NORMAL,
                             relief="solid", bd=1)
            entry.grid(row=i, column=1, pady=4, padx=(8, 0))
            self.entries[key] = entry

        # ── Tipo de cliente ──
        tk.Label(frame, text="Tipo *", font=FUENTE_NORMAL,
                 bg=COLOR_BLANCO, fg=COLOR_TEXTO, anchor="w"
                 ).grid(row=4, column=0, sticky="w", pady=4)
        self.tipo_var = tk.StringVar(value="Regular")
        combo = ttk.Combobox(frame, textvariable=self.tipo_var, width=26,
                             values=["Regular", "Premium", "Corporativo"],
                             state="readonly", font=FUENTE_NORMAL)
        combo.grid(row=4, column=1, pady=4, padx=(8, 0))
        combo.bind("<<ComboboxSelected>>", self._toggle_campo_empresa)

        # ── Campo empresa (solo para Corporativo) ──
        self.frame_empresa = tk.Frame(frame, bg=COLOR_BLANCO)
        self.frame_empresa.grid(row=5, column=0, columnspan=2, sticky="ew")
        tk.Label(self.frame_empresa, text="Empresa", font=FUENTE_NORMAL,
                 bg=COLOR_BLANCO, fg=COLOR_TEXTO
                 ).grid(row=0, column=0, sticky="w", pady=4)
        self.entry_empresa = tk.Entry(self.frame_empresa, width=28,
                                      font=FUENTE_NORMAL, relief="solid", bd=1)
        self.entry_empresa.grid(row=0, column=1, padx=(8, 0))
        self.frame_empresa.grid_remove()  # Oculto por defecto

        # ── Botones ──
        btn_frame = tk.Frame(frame, bg=COLOR_BLANCO)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=(15, 0))

        tk.Button(btn_frame, text="💾 Guardar Cliente",
                  font=("Arial", 10, "bold"),
                  bg=COLOR_EXITO, fg=COLOR_BLANCO,
                  relief="flat", padx=12, pady=6, cursor="hand2",
                  command=self._agregar_cliente
                  ).pack(side="left", padx=5)

        tk.Button(btn_frame, text="🔄 Limpiar",
                  font=FUENTE_NORMAL,
                  bg="#9E9E9E", fg=COLOR_BLANCO,
                  relief="flat", padx=12, pady=6, cursor="hand2",
                  command=self._limpiar_formulario
                  ).pack(side="left", padx=5)

        # ── Separador ──
        ttk.Separator(frame_outer, orient="horizontal").pack(fill="x", pady=8)

        # ── Botones de exportación ──
        frame_exp = tk.LabelFrame(frame_outer, text=" 📁 Exportar ",
                                   font=("Arial", 10, "bold"),
                                   bg=COLOR_BLANCO, fg=COLOR_PRIMARIO,
                                   padx=10, pady=10)
        frame_exp.pack(fill="x")

        tk.Button(frame_exp, text="📄 Exportar JSON",
                  font=FUENTE_PEQUEÑA, bg=COLOR_PRIMARIO, fg=COLOR_BLANCO,
                  relief="flat", padx=8, pady=4, cursor="hand2",
                  command=self._exportar_json
                  ).pack(fill="x", pady=2)

        tk.Button(frame_exp, text="📊 Exportar CSV",
                  font=FUENTE_PEQUEÑA, bg="#0F9D58", fg=COLOR_BLANCO,
                  relief="flat", padx=8, pady=4, cursor="hand2",
                  command=self._exportar_csv
                  ).pack(fill="x", pady=2)

    def _construir_panel_tabla(self):
        """Panel derecho: tabla de clientes con búsqueda y acciones."""
        frame_outer = tk.Frame(self, bg=COLOR_SECUNDARIO)
        frame_outer.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # ── Búsqueda ──
        frame_busq = tk.Frame(frame_outer, bg=COLOR_SECUNDARIO)
        frame_busq.pack(fill="x", pady=(0, 5))

        tk.Label(frame_busq, text="🔍 Buscar:", font=FUENTE_NORMAL,
                 bg=COLOR_SECUNDARIO).pack(side="left")
        self.entry_buscar = tk.Entry(frame_busq, width=30, font=FUENTE_NORMAL,
                                      relief="solid", bd=1)
        self.entry_buscar.pack(side="left", padx=8)
        self.entry_buscar.bind("<KeyRelease>", self._buscar_cliente)

        tk.Button(frame_busq, text="Mostrar todos",
                  font=FUENTE_PEQUEÑA, bg=COLOR_PRIMARIO, fg=COLOR_BLANCO,
                  relief="flat", padx=6, pady=3, cursor="hand2",
                  command=self._cargar_tabla
                  ).pack(side="left")

        # ── Tabla ──
        frame_tabla = tk.LabelFrame(frame_outer, text=" 📋 Clientes Registrados ",
                                     font=("Arial", 11, "bold"),
                                     bg=COLOR_BLANCO, fg=COLOR_PRIMARIO,
                                     padx=5, pady=5)
        frame_tabla.pack(fill="both", expand=True)

        cols = ("ID", "Tipo", "Nombre", "Email", "Teléfono", "Descuento", "Registrado")
        self.tabla = ttk.Treeview(frame_tabla, columns=cols,
                                   show="headings", selectmode="browse")

        anchos = {"ID": 40, "Tipo": 100, "Nombre": 150, "Email": 180,
                  "Teléfono": 100, "Descuento": 70, "Registrado": 130}
        for col in cols:
            self.tabla.heading(col, text=col,
                               command=lambda c=col: self._ordenar_tabla(c))
            self.tabla.column(col, width=anchos[col], anchor="center")

        # Scrollbars
        sb_y = ttk.Scrollbar(frame_tabla, orient="vertical",
                              command=self.tabla.yview)
        sb_x = ttk.Scrollbar(frame_tabla, orient="horizontal",
                              command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)

        sb_y.pack(side="right", fill="y")
        sb_x.pack(side="bottom", fill="x")
        self.tabla.pack(fill="both", expand=True)

        # Tags de color por tipo
        self.tabla.tag_configure("Regular",     background="#E8F5E9")
        self.tabla.tag_configure("Premium",     background="#FFF3E0")
        self.tabla.tag_configure("Corporativo", background="#E3F2FD")

        # ── Botones de acción ──
        frame_acc = tk.Frame(frame_outer, bg=COLOR_SECUNDARIO)
        frame_acc.pack(fill="x", pady=5)

        tk.Button(frame_acc, text="👁 Ver Detalle",
                  font=FUENTE_NORMAL, bg=COLOR_PRIMARIO, fg=COLOR_BLANCO,
                  relief="flat", padx=10, pady=5, cursor="hand2",
                  command=self._ver_detalle
                  ).pack(side="left", padx=3)

        tk.Button(frame_acc, text="🗑 Eliminar",
                  font=FUENTE_NORMAL, bg=COLOR_PELIGRO, fg=COLOR_BLANCO,
                  relief="flat", padx=10, pady=5, cursor="hand2",
                  command=self._eliminar_cliente
                  ).pack(side="left", padx=3)

        tk.Button(frame_acc, text="📊 Estadísticas",
                  font=FUENTE_NORMAL, bg="#7B1FA2", fg=COLOR_BLANCO,
                  relief="flat", padx=10, pady=5, cursor="hand2",
                  command=self._mostrar_estadisticas
                  ).pack(side="right", padx=3)

    def _construir_barra_estado(self):
        """Barra inferior de estado."""
        self.barra_estado = tk.Label(self, text="Sistema listo.",
                                      font=FUENTE_PEQUEÑA,
                                      bg="#DADCE0", fg=COLOR_TEXTO,
                                      anchor="w", padx=10)
        self.barra_estado.pack(side="bottom", fill="x")

    # ──────────────────────────────────────────────
    # LÓGICA DE NEGOCIO / ACCIONES
    # ──────────────────────────────────────────────

    def _agregar_cliente(self):
        """Valida el formulario y guarda el nuevo cliente."""
        try:
            nombre   = self.entries["nombre"].get().strip()
            email    = self.entries["email"].get().strip()
            telefono = self.entries["telefono"].get().strip()
            direccion = self.entries["direccion"].get().strip()
            tipo     = self.tipo_var.get()

            if not all([nombre, email, telefono]):
                messagebox.showwarning("Campos requeridos",
                    "Los campos Nombre, Email y Teléfono son obligatorios.")
                return

            nuevo_id = self.db.obtener_siguiente_id()

            if tipo == "Regular":
                cliente = ClienteRegular(nuevo_id, nombre, email, telefono, direccion)
            elif tipo == "Premium":
                cliente = ClientePremium(nuevo_id, nombre, email, telefono, direccion)
            else:
                empresa = self.entry_empresa.get().strip() or "Sin especificar"
                cliente = ClienteCorporativo(nuevo_id, nombre, email, telefono,
                                             direccion, empresa, "00000000-0")

            self.db.insertar_cliente(cliente.to_dict())
            enviar_email_bienvenida(email, nombre, tipo)

            self._cargar_tabla()
            self._limpiar_formulario()
            self._actualizar_estado(f"✓ Cliente '{nombre}' agregado correctamente.")
            messagebox.showinfo("Éxito", f"Cliente '{nombre}' registrado exitosamente.")

        except ValueError as e:
            messagebox.showerror("Error de validación", str(e))
        except EmailDuplicadoError as e:
            messagebox.showerror("Email duplicado", str(e))
        except Exception as e:
            logger.error(f"Error al agregar cliente: {e}")
            messagebox.showerror("Error inesperado", str(e))

    def _eliminar_cliente(self):
        """Elimina (baja lógica) el cliente seleccionado."""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Selecciona un cliente de la tabla.")
            return

        valores = self.tabla.item(seleccion[0])["values"]
        id_cliente = valores[0]
        nombre = valores[2]

        if not messagebox.askyesno("Confirmar",
                f"¿Eliminar al cliente '{nombre}' (ID: {id_cliente})?"):
            return

        try:
            self.db.eliminar_cliente(id_cliente)
            self._cargar_tabla()
            self._actualizar_estado(f"✓ Cliente '{nombre}' eliminado.")
        except ClienteNoEncontradoError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _ver_detalle(self):
        """Muestra una ventana emergente con el detalle del cliente seleccionado."""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Selecciona un cliente.")
            return

        id_cliente = self.tabla.item(seleccion[0])["values"][0]
        try:
            datos = self.db.obtener_por_id(id_cliente)
            extra = json_seguro(datos.get("datos_extra", "{}"))

            ventana = tk.Toplevel(self)
            ventana.title(f"Detalle — Cliente ID {id_cliente}")
            ventana.geometry("420x350")
            ventana.configure(bg=COLOR_BLANCO)
            ventana.resizable(False, False)

            tk.Label(ventana, text=f"Cliente #{id_cliente} — {datos['tipo']}",
                     font=FUENTE_TITULO, bg=COLOR_PRIMARIO, fg=COLOR_BLANCO
                     ).pack(fill="x", pady=(0, 10))

            campos = [
                ("Nombre",      datos["nombre"]),
                ("Email",       datos["email"]),
                ("Teléfono",    datos["telefono"]),
                ("Dirección",   datos.get("direccion", "—")),
                ("Registrado",  datos.get("fecha_registro", "—")),
                ("Estado",      "Activo" if datos["activo"] else "Inactivo"),
            ]
            for k, v in campos:
                f = tk.Frame(ventana, bg=COLOR_BLANCO)
                f.pack(fill="x", padx=20, pady=2)
                tk.Label(f, text=f"{k}:", font=("Arial", 10, "bold"),
                         bg=COLOR_BLANCO, width=12, anchor="w").pack(side="left")
                tk.Label(f, text=str(v), font=FUENTE_NORMAL,
                         bg=COLOR_BLANCO, anchor="w").pack(side="left")

            # Datos extra (puntos, nivel, empresa, etc.)
            if extra:
                tk.Label(ventana, text="Datos adicionales:",
                         font=("Arial", 10, "bold"), bg=COLOR_BLANCO
                         ).pack(anchor="w", padx=20, pady=(8, 2))
                for k, v in extra.items():
                    f = tk.Frame(ventana, bg=COLOR_BLANCO)
                    f.pack(fill="x", padx=30, pady=1)
                    tk.Label(f, text=f"• {k}: {v}", font=FUENTE_PEQUEÑA,
                             bg=COLOR_BLANCO).pack(anchor="w")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _buscar_cliente(self, event=None):
        """Filtra la tabla según el texto de búsqueda."""
        termino = self.entry_buscar.get().strip()
        if len(termino) < 2:
            self._cargar_tabla()
            return
        resultados = self.db.buscar_clientes(termino)
        self._poblar_tabla(resultados)

    def _mostrar_estadisticas(self):
        """Muestra ventana con estadísticas del sistema."""
        stats = self.db.obtener_estadisticas()
        ventana = tk.Toplevel(self)
        ventana.title("📊 Estadísticas")
        ventana.geometry("300x250")
        ventana.configure(bg=COLOR_BLANCO)
        ventana.resizable(False, False)

        tk.Label(ventana, text="📊 Estadísticas del Sistema",
                 font=FUENTE_TITULO, bg=COLOR_PRIMARIO, fg=COLOR_BLANCO
                 ).pack(fill="x", pady=(0, 15))

        tk.Label(ventana, text=f"Total clientes activos: {stats['total_activos']}",
                 font=("Arial", 12), bg=COLOR_BLANCO).pack(pady=5)

        tk.Label(ventana, text="Distribución por tipo:",
                 font=("Arial", 11, "bold"), bg=COLOR_BLANCO).pack(pady=(10, 3))

        for tipo, cantidad in stats["por_tipo"].items():
            tk.Label(ventana, text=f"  • {tipo}: {cantidad}",
                     font=FUENTE_NORMAL, bg=COLOR_BLANCO).pack(anchor="w", padx=40)

    # ──────────────────────────────────────────────
    # HELPERS
    # ──────────────────────────────────────────────

    def _cargar_tabla(self):
        """Carga todos los clientes activos en la tabla."""
        clientes = self.db.obtener_todos()
        self._poblar_tabla(clientes)
        self._actualizar_estadisticas()

    def _poblar_tabla(self, clientes: list):
        """Rellena la tabla con la lista de clientes dada."""
        for row in self.tabla.get_children():
            self.tabla.delete(row)

        descuentos = {"ClienteRegular": "5%", "ClientePremium": "10-20%",
                      "ClienteCorporativo": "25%"}
        tipos_cortos = {"ClienteRegular": "Regular",
                        "ClientePremium": "Premium",
                        "ClienteCorporativo": "Corporativo"}

        for c in clientes:
            tipo_corto = tipos_cortos.get(c["tipo"], c["tipo"])
            self.tabla.insert("", "end", tags=(tipo_corto,), values=(
                c["id"],
                tipo_corto,
                c["nombre"],
                c["email"],
                c["telefono"],
                descuentos.get(c["tipo"], "—"),
                (c.get("fecha_registro") or "")[:10]
            ))

    def _limpiar_formulario(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.entry_empresa.delete(0, tk.END)
        self.tipo_var.set("Regular")
        self.frame_empresa.grid_remove()

    def _toggle_campo_empresa(self, event=None):
        if self.tipo_var.get() == "Corporativo":
            self.frame_empresa.grid()
        else:
            self.frame_empresa.grid_remove()

    def _actualizar_estadisticas(self):
        try:
            stats = self.db.obtener_estadisticas()
            self.lbl_stats.config(
                text=f"Total clientes: {stats['total_activos']}"
            )
        except Exception:
            pass

    def _actualizar_estado(self, mensaje: str):
        self.barra_estado.config(text=mensaje)

    def _ordenar_tabla(self, columna: str):
        """Ordena la tabla por la columna clickeada (toggle asc/desc)."""
        pass  # Implementación opcional

    def _exportar_json(self):
        clientes = self.db.obtener_todos()
        if self.json_mgr.exportar(clientes):
            messagebox.showinfo("Éxito", f"Exportado a data/clientes.json\n({len(clientes)} registros)")

    def _exportar_csv(self):
        clientes = self.db.obtener_todos()
        if self.csv_mgr.exportar(clientes):
            messagebox.showinfo("Éxito", f"Exportado a data/clientes.csv\n({len(clientes)} registros)")


# ──────────────────────────────────────────────────────────────
# UTILIDADES
# ──────────────────────────────────────────────────────────────

def json_seguro(valor) -> dict:
    """Parsea un string JSON de forma segura."""
    import json
    if isinstance(valor, dict):
        return valor
    try:
        return json.loads(valor or "{}")
    except Exception:
        return {}


# ──────────────────────────────────────────────────────────────
# PUNTO DE ENTRADA
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = App()
    app.mainloop()
