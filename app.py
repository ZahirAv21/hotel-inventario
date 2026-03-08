import streamlit as st
from supabase import create_client
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)

st.title("Sistema Inventario Hotel")

menu = st.sidebar.selectbox(
"Menu",
["Inventario","Registrar venta","Rellenar producto","Historial"]
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

    st.dataframe(df)

elif menu == "Registrar venta":

    st.header("Registrar venta")

    df = obtener_productos()

    producto = st.selectbox("Producto",df["nombre"])

    cantidad = st.number_input("Cantidad",1)

    turno = st.selectbox(
        "Turno",
        ["8am-8pm","8pm-8am"]
    )

    if st.button("Registrar venta"):

        stock = df[df["nombre"]==producto]["stock_actual"].values[0]

        nuevo_stock = stock - cantidad

        supabase.table("productos").update({
            "stock_actual":nuevo_stock
        }).eq("nombre",producto).execute()

        supabase.table("ventas").insert({
            "producto":producto,
            "cantidad":cantidad,
            "turno":turno
        }).execute()

        st.success("Venta registrada")

elif menu == "Rellenar producto":

    st.header("Rellenar inventario")

    df = obtener_productos()

    producto = st.selectbox("Producto",df["nombre"])

    cantidad = st.number_input("Cantidad a agregar",1)

    if st.button("Rellenar"):

        stock = df[df["nombre"]==producto]["stock_actual"].values[0]

        nuevo_stock = stock + cantidad

        supabase.table("productos").update({
            "stock_actual":nuevo_stock
        }).eq("nombre",producto).execute()

        supabase.table("reposiciones").insert({
            "producto":producto,
            "cantidad":cantidad
        }).execute()

        st.success("Inventario actualizado")

elif menu == "Historial":

    st.header("Historial de ventas")

    data = supabase.table("ventas").select("*").execute()

    df = pd.DataFrame(data.data)

    st.dataframe(df)