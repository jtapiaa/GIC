# 🏢 GIC — Gestor Inteligente de Clientes

> **Proyecto del Módulo #4 — Alkemy**  
> Empresa solicitante: **SolutionTech**  
> Tecnología: Python 3 · POO · SQLite · Tkinter · APIs externas

---

## 📌 Descripción

El Gestor Inteligente de Clientes es una plataforma integral desarrollada en Python que permite gestionar tres tipos de clientes (`Regular`, `Premium` y `Corporativo`), aplicando los principios de la **Programación Orientada a Objetos**: encapsulación, herencia y polimorfismo.

El sistema incluye validaciones avanzadas, persistencia en SQLite y JSON, una interfaz gráfica en Tkinter, integración con APIs externas y un completo conjunto de pruebas unitarias.

---

## 🗂️ Estructura del Proyecto

```
GIC/
├── models/                    # Clases del dominio (POO)
│   ├── __init__.py
│   ├── cliente.py             # Clase base abstracta
│   ├── cliente_regular.py     # Subclase: puntos de fidelidad
│   ├── cliente_premium.py     # Subclase: niveles Plata/Oro/Platino
│   └── cliente_corporativo.py # Subclase: empresas con crédito
│
├── database/                  # Capa de persistencia SQLite
│   ├── __init__.py
│   └── db_manager.py          # CRUD completo + log de actividad
│
├── utils/                     # Utilidades transversales
│   ├── __init__.py
│   ├── validaciones.py        # Excepciones personalizadas + validadores
│   ├── logger.py              # Sistema de logging (archivo + consola)
│   ├── api_client.py          # Integración con APIs externas
│   └── json_manager.py        # Exportación/importación JSON y CSV
│
├── gui/                       # Interfaz gráfica Tkinter
│   ├── __init__.py
│   └── app.py                 # Ventana principal + formularios
│
├── tests/                     # Pruebas unitarias
│   ├── __init__.py
│   └── test_clientes.py       # +30 tests sobre modelos, BD y validaciones
│
├── data/                      # Archivos generados en ejecución
│   ├── clientes.db            # Base de datos SQLite (auto-generada)
│   ├── clientes.json          # Export JSON (generado al exportar)
│   └── clientes.csv           # Export CSV  (generado al exportar)
│
├── logs/                      # Logs del sistema (auto-generados)
│   └── gic_YYYYMMDD.log
│
├── main.py                    # Punto de entrada principal
├── requirements.txt
└── README.md
```

---

## 🚀 Instalación y Ejecución

### 1. Requisitos previos

- Python **3.8 o superior**
- Tkinter (incluido en la instalación estándar de Python)

### 2. Clonar o descomprimir el proyecto

```bash
cd GestorInteligenteClientes
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

> `requests` y `pytest` son opcionales. El sistema funciona sin ellos.

### 4. Ejecutar la aplicación

```bash
# Lanzar la interfaz gráfica (modo principal)
python main.py

# Ejecutar demo en consola (sin GUI)
python main.py --demo

# Ejecutar las pruebas unitarias
python main.py --test
```

---

## 🧱 Arquitectura y Principios de POO

### Jerarquía de Clases

```
Cliente (clase base)
├── ClienteRegular      → +puntos, +agregar_puntos(), descuento 5%
├── ClientePremium      → +nivel (Plata/Oro/Platino), descuento 10-20%
└── ClienteCorporativo  → +empresa, +rut, +crédito, descuento 25%
```

## Diagrama UML 

- diagramaClase.pdf

### Encapsulación

Todos los atributos son **privados** (`_atributo`) y accesibles mediante **properties** con validación integrada

### Herencia

Las subclases extienden `Cliente` usando `super()` para reutilizar la inicialización y agregan sus propios atributos:

### Polimorfismo

Cada tipo de cliente sobrescribe `obtener_descuento()` y `mostrar_info()`:

```python
# Mismo método, distintos comportamientos
cliente_regular.obtener_descuento()     # → 0.05 (5%)
cliente_premium.obtener_descuento()     # → 0.15 (15%)
cliente_corporativo.obtener_descuento() # → 0.25 (25%)
```

---

## 🗄️ Base de Datos (SQLite)

El sistema crea automáticamente dos tablas:

| Tabla           | Descripción                              |
|-----------------|------------------------------------------|
| `clientes`      | Datos de todos los clientes registrados  |
| `actividad_log` | Registro de cada operación realizada     |

La columna `datos_extra` almacena en JSON los atributos específicos de cada tipo (puntos, nivel_premium, empresa, etc.), permitiendo una estructura flexible sin necesidad de tablas separadas.

---

## ❗ Manejo de Errores

El sistema define una jerarquía de excepciones personalizadas:

| Excepción                  | Cuándo se lanza                               | Código |
|----------------------------|-----------------------------------------------|--------|
| `GICError`                 | Excepción base del sistema                    | —      |
| `ClienteNoEncontradoError` | ID o email no existe en la BD                 | 404    |
| `EmailDuplicadoError`      | Email ya registrado                           | 409    |
| `DatosInvalidosError`      | Campo con formato incorrecto                  | 400    |
| `BaseDatosError`           | Fallo en SQLite                               | 500    |
| `OperacionNoPermitidaError`| Acción no permitida en el contexto actual     | 403    |

---

## 🌐 Integración con APIs Externas

El módulo `utils/api_client.py` incluye:

- **Validación de email** vía [Abstract API](https://www.abstractapi.com/) (gratuita)
- **Email de bienvenida** simulado (log en consola/archivo)
- **Verificación de identidad** corporativa (simulada)

Para activar la validación real, reemplaza `TU_API_KEY_AQUI` en `api_client.py` con tu clave de Abstract API.

---

## 🧪 Pruebas Unitarias

El archivo `tests/test_clientes.py` contiene más de **30 tests** organizados en 6 suites:

| Suite                   | Qué prueba                                |
|-------------------------|-------------------------------------------|
| `TestClienteBase`       | Atributos, setters, validaciones, `__eq__`|
| `TestClienteRegular`    | Puntos, canje, descuento 5%               |
| `TestClientePremium`    | Niveles, descuentos progresivos           |
| `TestClienteCorporativo`| Empresa, crédito, contactos               |
| `TestValidaciones`      | Email, teléfono, RUT                      |
| `TestDatabaseManager`   | CRUD, duplicados, búsqueda, estadísticas  |
| `TestPolimorfismo`      | Descuentos, isinstance, to_dict           |

### Ejecutar tests

```bash
# Con unittest (sin dependencias externas)
python -m unittest discover tests/ -v

# Con pytest (si está instalado)
pytest tests/ -v

# Desde main.py
python main.py --test
```

---

## 📁 Exportación de Datos

Desde la GUI, los botones de exportación generan:

- `data/clientes.json` → Formato JSON con todos los campos
- `data/clientes.csv` → Formato CSV compatible con Excel

---

## 📋 Funcionalidades Implementadas

| Funcionalidad                      | Estado |
|------------------------------------|--------|
| Clase base `Cliente` con encapsulación | ✅ |
| Subclases con herencia y polimorfismo  | ✅ |
| Validaciones de email, teléfono, nombre | ✅ |
| Excepciones personalizadas            | ✅ |
| Sistema de logging (archivo + consola)| ✅ |
| Persistencia SQLite (CRUD completo)   | ✅ |
| Log de actividad en BD                | ✅ |
| Exportación JSON y CSV                | ✅ |
| GUI en Tkinter                        | ✅ |
| Búsqueda de clientes                  | ✅ |
| Integración con API externa           | ✅ |
| Email de bienvenida automatizado      | ✅ |
| Pruebas unitarias (+30 tests)         | ✅ |
| Estadísticas del sistema              | ✅ |

---

## 👩‍💻 Tecnologías Utilizadas

- **Python 3.8+**
- **sqlite3** — Base de datos relacional local
- **tkinter** — Interfaz gráfica nativa
- **json / csv** — Persistencia de archivos
- **logging** — Sistema de registros
- **unittest** — Pruebas unitarias
- **requests** — Llamadas HTTP a APIs externas (opcional)

---

## 📝 Notas de Desarrollo

- La base de datos se crea automáticamente en `data/clientes.db` al primer inicio.
- Los logs se generan diariamente en `logs/gic_YYYYMMDD.log`.
- La eliminación de clientes es **lógica** por defecto (campo `activo = 0`), preservando el historial.
- El campo `datos_extra` en SQLite almacena como JSON los atributos específicos de cada tipo de cliente.

---
