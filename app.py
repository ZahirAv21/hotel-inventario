import streamlit as st
from supabase import create_client
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)

def login():

    st.title("Sistema Inventario Hotel")

    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):

        data = supabase.table("usuarios").select("*").eq("username",username).execute()

        if len(data.data) == 0:
            st.error("Usuario no existe")
            return

        user = data.data[0]

        if user["password"] == password:
            st.session_state["login"] = True
            st.success("Acceso permitido")
            st.rerun()

        else:
            st.error("Contraseña incorrecta")


if "login" not in st.session_state:
    st.session_state["login"] = False


if not st.session_state["login"]:
    login()
    st.stop()

st.title("Sistema Inventario Hotel")

menu = st.sidebar.selectbox(
"Menu",
[
"Inventario",
"Registrar venta",
"Rellenar producto",
"Historial",
"Configurar productos"
]
)


def obtener_productos():
    data = supabase.table("productos").select("*").execute()
    return pd.DataFrame(data.data)

if menu == "Inventario":

    st.header("Inventario en vitrina")

    df = obtener_productos()

    for i,row in df.iterrows():

        if row["stock_actual"] <= row["stock_minimo"]:
            st.warning(f"{row['nombre']} STOCK BAJO")

    df = df.drop(columns=["id"])

    st.dataframe(df)

elif menu == "Registrar venta":

    st.header("Registrar venta")

    df = obtener_productos()

    if df.empty:
        st.warning("No hay productos registrados.")
    else:
        producto = st.selectbox("Producto", df["nombre"])

        cantidad = st.number_input("Cantidad", min_value=1)

        turno = st.selectbox(
            "Turno",
            ["8am-8pm", "8pm-8am"]
        )

    if st.button("Registrar venta"):

        stock = int(df[df["nombre"]==producto]["stock_actual"].values[0])

        nuevo_stock = int(stock - cantidad)

        supabase.table("productos").update({
            "stock_actual":nuevo_stock
        }).eq("nombre",producto).execute()

        supabase.table("ventas").insert({
            "producto":producto,
            "cantidad":int(cantidad),
            "turno":turno
        }).execute()

        st.success("Venta registrada")

elif menu == "Rellenar producto":

    st.header("Rellenar inventario")

    df = obtener_productos()

    producto = st.selectbox("Producto",df["nombre"])

    cantidad = st.number_input("Cantidad a agregar",1)

    if st.button("Rellenar"):

        stock = int(df[df["nombre"]==producto]["stock_actual"].values[0])

        nuevo_stock = int(stock - cantidad)

        supabase.table("productos").update({
            "stock_actual":nuevo_stock
        }).eq("nombre",producto).execute()

        supabase.table("reposiciones").insert({
            "producto":producto,
            "cantidad":int(cantidad)
        }).execute()

        st.success("Inventario actualizado")

elif menu == "Historial":

    st.header("Historial de ventas")

    data = supabase.table("ventas").select("*").execute()

    df = pd.DataFrame(data.data)

    if df.empty:
        st.info("No hay ventas registradas aún.")
        st.stop()

    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"]).dt.date


    st.dataframe(df)

    venta_id = st.selectbox("Seleccionar venta a eliminar", df["id"])

    if st.button("Eliminar venta"):

        venta = df[df["id"] == venta_id].iloc[0]

        producto = venta["producto"]
        cantidad = int(venta["cantidad"])

        # Obtener stock actual
        prod_data = supabase.table("productos").select("*").eq("nombre", producto).execute()

        stock_actual = int(prod_data.data[0]["stock_actual"])

        nuevo_stock = stock_actual + cantidad

        # Devolver stock
        supabase.table("productos").update({
            "stock_actual": nuevo_stock
        }).eq("nombre", producto).execute()

        # Eliminar venta
        supabase.table("ventas").delete().eq("id", venta_id).execute()

        st.success("Venta eliminada y stock restaurado")

        st.rerun()

elif menu == "Configurar productos":

    st.header("Configurar productos")

    df = obtener_productos()

    producto = st.selectbox("Producto", df["nombre"])

    stock_actual = st.number_input("Stock actual",1)
    stock_minimo = st.number_input("Stock mínimo",1)

    if st.button("Actualizar producto"):

        supabase.table("productos").update({
            "stock_actual":stock_actual,
            "stock_minimo":stock_minimo
        }).eq("nombre",producto).execute()

        st.success("Producto actualizado")