import streamlit as st
import simpy
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# ============================================
#   DASHBOARD HEADER
# ============================================
st.set_page_config(page_title="Simulasi Kantin IT Del", layout="wide")

st.title("🍽️ Simulasi Kantin IT Del – Versi Visual")
st.write("Simulasi alur: pemberian lauk → pengangkatan ompreng → penambahan nasi.")

# ============================================
#   SIDEBAR PARAMETER
# ============================================
st.sidebar.header("⚙️ Pengaturan Simulasi")

jumlah_meja = st.sidebar.slider("Jumlah Meja", 10, 100, 60)
orang_per_meja = st.sidebar.slider("Orang per Meja", 1, 5, 3)
jumlah_petugas = st.sidebar.slider("Jumlah Petugas", 1, 10, 7)

TOTAL_OMPRENG = jumlah_meja * orang_per_meja

st.sidebar.write(f"Total Ompreng: **{TOTAL_OMPRENG}**")
st.sidebar.write("---")

# waktu proses (detik)
WAKTU_LAUK = (30, 60)
WAKTU_ANGKAT = (20, 60)
WAKTU_NASI = (30, 60)

# ============================================
#   EVENT LOGGER
# ============================================
event_log = []

def log_event(stage, time, item):
    event_log.append([stage, time, item])

# ============================================
#   PROSES KANTIN (3 tahap)
# ============================================
def proses_kantin(env, nama, petugas):
    log_event("Mulai", env.now, nama)

    # Tahap 1: Lauk
    with petugas.request() as req:
        yield req
        yield env.timeout(np.random.uniform(*WAKTU_LAUK))
        log_event("Lauk Selesai", env.now, nama)

    # Tahap 2: Angkat
    with petugas.request() as req:
        yield req
        yield env.timeout(np.random.uniform(*WAKTU_ANGKAT))
        log_event("Angkat Selesai", env.now, nama)

    # Tahap 3: Nasi
    with petugas.request() as req:
        yield req
        yield env.timeout(np.random.uniform(*WAKTU_NASI))
        log_event("Nasi Selesai", env.now, nama)

    log_event("Selesai Semua", env.now, nama)

# ============================================
#   GENERATOR OMPRING
# ============================================
def jalankan_simulasi(total, petugas_count):
    env = simpy.Environment()
    petugas = simpy.Resource(env, capacity=petugas_count)

    for i in range(total):
        env.process(proses_kantin(env, f"Ompreng-{i+1}", petugas))

    env.run()
    return pd.DataFrame(event_log, columns=["Tahap","Waktu","Ompreng"])

# ============================================
#   TOMBOL SIMULASI
# ============================================
if st.button("🚀 Jalankan Simulasi", use_container_width=True):

    df = jalankan_simulasi(TOTAL_OMPRENG, jumlah_petugas)

    st.success("Simulasi kantin selesai dijalankan!")
    st.write("---")

    # =============================
    #        DATAFRAME
    # =============================
    st.subheader("📄 Data Event")
    st.dataframe(df, use_container_width=True)

    # =============================
    #     ANALISIS DURASI
    # =============================
    pivot = df.pivot_table(values="Waktu", index="Ompreng", columns="Tahap")
    durasi = pivot["Selesai Semua"] - pivot["Mulai"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Rata-rata Durasi", f"{durasi.mean():.2f} detik")
    col2.metric("Durasi Tercepat", f"{durasi.min():.2f} detik")
    col3.metric("Durasi Terlama", f"{durasi.max():.2f} detik")

    st.write("---")

    # ============================================
    #   TAB LAYOUT VISUALISASI
    # ============================================
    tab1, tab2, tab3 = st.tabs([
        "📊 Heatmap Tahapan",
        "📈 Distribusi Durasi",
        "🧱 Jumlah Event"
    ])

    # =============================
    #   TAB 1 — HEATMAP
    # =============================
    with tab1:
        st.subheader("Heatmap Tahapan Ompreng")

        plt.figure(figsize=(14, 6))
        sns.heatmap(pivot, cmap="crest")
        st.pyplot(plt)

    # =============================
    #   TAB 2 — KDE PLOT
    # =============================
    with tab2:
        st.subheader("Distribusi Durasi (KDE)")

        plt.figure(figsize=(12, 5))
        sns.kdeplot(durasi, fill=True, linewidth=2)
        sns.rugplot(durasi, color="black")
        st.pyplot(plt)

    # =============================
    #   TAB 3 — EVENT COUNT
    # =============================
    with tab3:
        st.subheader("Jumlah Event per Tahap")

        plt.figure(figsize=(10, 5))
        sns.countplot(x="Tahap", data=df)
        plt.xticks(rotation=25)
        st.pyplot(plt)

else:
    st.info("Klik tombol di atas untuk menjalankan simulasi kantin.")
