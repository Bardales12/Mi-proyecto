from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

# 📂 Definir rutas relativas (Render no usa rutas absolutas como "D:/...")
UPLOADS_DIR = os.path.join(os.getcwd(), "uploads")
EXCEL_FILE = os.path.join(UPLOADS_DIR, "LISTA_ORIGINAL_DEUDA.xlsx")
BACKUP_FILE = os.path.join(UPLOADS_DIR, "LISTA_ORIGINAL_DEUDA_BACKUP.xlsx")

# 🛠 Función para verificar si el archivo existe
def verificar_archivo(ruta):
    if not os.path.exists(ruta):
        print(f"❌ Archivo no encontrado: {ruta}")
        return False
    print(f"✅ Archivo encontrado: {ruta}")
    return True

# 📖 Leer datos del archivo Excel
def leer_datos(ruta=BACKUP_FILE):
    if verificar_archivo(ruta):
        return pd.read_excel(ruta, header=3, engine='openpyxl')
    return pd.DataFrame()  # Retorna un DataFrame vacío si no encuentra el archivo

# 💾 Guardar datos en el archivo Excel
def guardar_datos(df, ruta=BACKUP_FILE):
    try:
        with pd.ExcelWriter(ruta, engine='openpyxl', mode='w') as writer:
            df.to_excel(writer, index=False)
        print(f"💾 Datos guardados en: {ruta}")
    except PermissionError:
        print(f"❌ Error: No se puede guardar '{ruta}'. Verifica que el archivo no esté abierto.")
    except Exception as e:
        print(f"⚠️ Error inesperado al guardar '{ruta}': {e}")

# 🔍 Buscar estudiantes en el archivo Excel
def buscar_estudiantes_por_nombre(nombre):
    df = leer_datos()
    if df.empty:
        return []
    resultados = df[df['APELLIDOS Y NOMBRES'].astype(str).str.contains(nombre, case=False, na=False)]
    return resultados.to_dict(orient='records') if not resultados.empty else []

# ✅ Actualizar la deuda del estudiante a 0
def actualizar_deuda(nombre):
    df = leer_datos()
    if df.empty:
        return
    mask = df['APELLIDOS Y NOMBRES'].astype(str).str.contains(nombre, case=False, na=False)
    if mask.any():
        df.loc[mask, ['I', 'II', 'III', 'IV', 'DEUDA TOT']] = 0
        guardar_datos(df)
        print(f"✅ Deuda de '{nombre}' actualizada a 0.")
    else:
        print(f"⚠️ No se encontró a '{nombre}' para actualizar.")

# 🔄 Restaurar la deuda original desde el archivo de respaldo
def restaurar_deuda(nombre):
    df_backup = leer_datos()
    df_original = leer_datos(EXCEL_FILE)
    if df_backup.empty or df_original.empty:
        return
    mask = df_backup['APELLIDOS Y NOMBRES'].astype(str).str.contains(nombre, case=False, na=False)
    if mask.any():
        columnas_deuda = ['I', 'II', 'III', 'IV', 'DEUDA TOT']
        for columna in columnas_deuda:
            df_backup.loc[mask, columna] = df_original.loc[df_original['APELLIDOS Y NOMBRES'] == nombre, columna].values[0]
        guardar_datos(df_backup)
        print(f"🔄 Deuda de '{nombre}' restaurada.")
    else:
        print(f"⚠️ No se encontró deuda original para '{nombre}'.")

# 🌍 Ruta principal del servidor Flask
@app.route('/', methods=['GET', 'POST'])
def index():
    verificar_archivo(BACKUP_FILE)  # Verifica si el backup existe
    estudiantes = []
    if request.method == 'POST':
        nombre = request.form['busqueda'].strip()
        accion = request.form.get('accion')
        if accion == 'pago_si':
            actualizar_deuda(nombre)
        elif accion == 'pago_no':
            restaurar_deuda(nombre)
        estudiantes = buscar_estudiantes_por_nombre(nombre)
    return render_template('index.html', estudiantes=estudiantes)

# 🚀 Iniciar el servidor en el puerto 10000
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Permite configurar el puerto en Render
    app.run(host="0.0.0.0", port=port, debug=True)


