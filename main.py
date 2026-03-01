#!/usr/bin/env python3
# main.py
"""
Punto de entrada del sistema GIC (Gestor Inteligente de Clientes).
Empresa: Empatic Spa | Módulo 4 — Alkermy

USABILIDAD:
    python main.py          → Lanza la GUI (Tkinter)
    python main.py --demo   → Ejecuta demo en consola
    python main.py --test   → Ejecuta las pruebas unitarias
"""
import sys
import os


def lanzar_gui():
    """Inicia la interfaz gráfica Tkinter."""
    try:
        from gui.app import App
        app = App()
        app.mainloop()
    except ImportError as e:
        print(f"[ERROR] No se pudo cargar la GUI: {e}")
        print("Asegúrate de tener Tkinter instalado.")
        sys.exit(1)


def demo_consola():
    """Demuestra el sistema en modo consola sin GUI."""
    from models.cliente_regular import ClienteRegular
    from models.cliente_premium import ClientePremium
    from models.cliente_corporativo import ClienteCorporativo
    from database.db_manager import DatabaseManager
    from utils.api_client import enviar_email_bienvenida
    from utils.json_manager import JsonManager

    print("\n" + "="*60)
    print("   DEMO — Gestor Inteligente de Clientes (GIC)")
    print("="*60)

    db = DatabaseManager()

    # Crear clientes de prueba
    clientes = [
        ClienteRegular(1, "Ana García",    "ana@test.com",    "+56911111111", "Av. Libertad 100"),
        ClientePremium(2, "Carlos Rojas",  "carlos@test.com", "+56922222222", "Calle 5 #200", nivel_premium=2),
        ClienteCorporativo(3, "Juan Pérez", "juan@corp.com",  "+56933333333", "Parque Industrial 55",
                          empresa="TechCorp SA", rut_empresa="12345678-9", limite_credito=1000000),
    ]

    print("\n📝 Creando clientes...")
    for c in clientes:
        try:
            db.insertar_cliente(c.to_dict())
            print(f"  ✓ {c}")
        except Exception as e:
            print(f"  ⚠ {e}")

    print("\n📋 Listado de clientes:")
    for c in clientes:
        print(c.mostrar_info())

    print("\n📊 Polimorfismo — Descuentos:")
    for c in clientes:
        print(f"  {c.obtener_tipo():20s} → {c.obtener_descuento()*100:.0f}% descuento")

    print("\n🗄  Estadísticas de la BD:")
    stats = db.obtener_estadisticas()
    print(f"  Total activos : {stats['total_activos']}")
    for tipo, cant in stats["por_tipo"].items():
        print(f"  {tipo:25s}: {cant}")

    print("\n💾 Exportando a JSON...")
    jm = JsonManager()
    todos = db.obtener_todos()
    jm.exportar(todos)
    print("  ✓ data/clientes.json generado.")

    print("\n" + "="*60)
    print("   Demo completado exitosamente.")
    print("="*60 + "\n")


def ejecutar_tests():
    """Ejecuta las pruebas unitarias."""
    import unittest
    loader = unittest.TestLoader()
    suite  = loader.discover("tests")
    runner = unittest.TextTestRunner(verbosity=2)
    resultado = runner.run(suite)
    sys.exit(0 if resultado.wasSuccessful() else 1)


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    if "--demo" in sys.argv:
        demo_consola()
    elif "--test" in sys.argv:
        ejecutar_tests()
    else:
        lanzar_gui()
