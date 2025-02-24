from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

# Rutas de los archivos Excel
excel_file = r'D:/MI PROYECTO/uploads/LISTA_ORIGINAL_DEUDA.xlsx'
backup_file = r'D:/MI PROYECTO/uploads/LISTA_ORIGINAL_DEUDA_BACKUP.xlsx'

def crear_backup():
    """Verificar si el archivo de respaldo existe."""
    if not os.path.exists(backup_file):
        print("❌ El archivo de respaldo no se encontró.")
    else:
        print("✅ Archivo de respaldo encontrado y listo para usarse.")

def leer_datos(ruta=backup_file):
    df = pd.read_excel(ruta, header=3, engine='openpyxl')
    df.columns = df.columns.str.strip()
    return df

def guardar_datos(df, ruta=backup_file):
    try:
        with pd.ExcelWriter(ruta, engine='openpyxl', mode='w') as writer:
            df.to_excel(writer, index=False)
        print(f"💾 Cambios guardados en: {ruta}")
    except PermissionError:
        print(f"❌ Error: No se pudo guardar '{ruta}'. Verifica que el archivo no esté abierto.")
    except Exception as e:
        print(f"⚠️ Error inesperado al guardar '{ruta}': {e}")

def buscar_estudiantes_por_nombre(nombre):
    df = leer_datos()
    resultados = df[df['APELLIDOS Y NOMBRES'].astype(str).str.contains(nombre, case=False, na=False)]
    return resultados.to_dict(orient='records') if not resultados.empty else []

def actualizar_deuda(nombre):
    """Actualizar la deuda del estudiante a 0 y guardar en el Excel."""
    df = leer_datos()
    mask = df['APELLIDOS Y NOMBRES'].astype(str).str.contains(nombre, case=False, na=False)
    if mask.any():
        df.loc[mask, ['I', 'II', 'III', 'IV', 'DEUDA TOT']] = 0
        guardar_datos(df)
        print(f"✅ Deuda de '{nombre}' actualizada a 0 y guardada en el Excel.")
    else:
        print(f"⚠️ No se encontró a '{nombre}' para actualizar.")

def restaurar_deuda(nombre):
    """Restaurar la deuda original del estudiante desde el respaldo."""
    df_backup = leer_datos()
    df_original = pd.read_excel(excel_file, header=3, engine='openpyxl')
    df_original.columns = df_original.columns.str.strip()
    mask = df_backup['APELLIDOS Y NOMBRES'].astype(str).str.contains(nombre, case=False, na=False)
    if mask.any():
        datos_originales = df_original[df_original['APELLIDOS Y NOMBRES'].astype(str).str.contains(nombre, case=False, na=False)]
        if not datos_originales.empty:
            columnas_deuda = ['I', 'II', 'III', 'IV', 'DEUDA TOT']
            for columna in columnas_deuda:
                df_backup.loc[mask, columna] = datos_originales.iloc[0][columna]
            guardar_datos(df_backup)
            print(f"🔄 Deuda original de '{nombre}' restaurada en el Excel.")
        else:
            print(f"⚠️ No se encontró deuda original para '{nombre}'.")

@app.route('/', methods=['GET', 'POST'])
def index():
    crear_backup()
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

if __name__ == '__main__':
    app.run(debug=True)

