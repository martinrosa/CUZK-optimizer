import streamlit as st
import random
import io

st.set_page_config(page_title="XYZ Reducer", layout="centered")

st.title("XYZ Reducer")

uploaded_file = st.file_uploader("Vyberte soubor XYZ", type="xyz")
mode = st.radio(
    "Režim redukce",
    (
        "Jednotné náhodné",
        "Podle vzdálenosti od středu",
        "Podle vzdálenosti od vlastního bodu",
    ),
)

if uploaded_file:
    # načti a vypočti základní údaje
    raw = uploaded_file.read().splitlines()
    lines = [ln.decode("utf-8") for ln in raw if ln.strip()]
    total = len(lines)
    coords = [list(map(float, ln.split())) for ln in lines]
    xs, ys, zs = zip(*coords)
    center = (sum(xs) / total, sum(ys) / total, sum(zs) / total)
    distances_center = [
        ((x - center[0]) ** 2 + (y - center[1]) ** 2 + (z - center[2]) ** 2) ** 0.5
        for x, y, z in coords
    ]
    max_d_center = max(distances_center)

    st.write(f"Celkový počet bodů: **{total}**")

    if mode == "Jednotné náhodné":
        pct = st.slider("Procento bodů k zachování", 0, 100, 50, 5)
        est = int(total * pct / 100)
        st.write(f"Odhad zachovaných bodů: **{est}**")
        if st.button("Redukovat"):
            keep = int(total * pct / 100)
            if keep < 1:
                st.error("Procento příliš nízké – žádné body nezůstanou.")
            else:
                reduced = random.sample(lines, keep)
                out = io.StringIO("\n".join(reduced))
                st.download_button(
                    "Stáhnout redukovaný soubor",
                    data=out.getvalue(),
                    file_name=uploaded_file.name.replace(".xyz", "_reduced.xyz"),
                    mime="text/plain",
                )

    elif mode == "Podle vzdálenosti od středu":
        p1 = st.slider("Procento pro blízké body", 0, 100, 80, 5)
        p2 = st.slider("Procento pro vzdálené body", 0, 100, 30, 5)
        est = int(total * ((p1 + p2) / 2) / 100)
        st.write(f"Odhad zachovaných bodů: **{est}**")
        if st.button("Redukovat"):
            reduced = []
            for ln, d in zip(lines, distances_center):
                local_pct = p1 + (p2 - p1) * (d / max_d_center)
                if random.random() < local_pct / 100:
                    reduced.append(ln)
            keep = len(reduced)
            if keep < 1:
                st.error("Žádné body nezůstaly – změňte procenta.")
            else:
                out = io.StringIO("\n".join(reduced))
                st.download_button(
                    "Stáhnout redukovaný soubor",
                    data=out.getvalue(),
                    file_name=uploaded_file.name.replace(".xyz", "_reduced.xyz"),
                    mime="text/plain",
                )

    else:  # vlastní bod
        x0 = st.number_input("Souřadnice X", value=center[0], format="%.3f")
        y0 = st.number_input("Souřadnice Y", value=center[1], format="%.3f")
        if not (min(xs) <= x0 <= max(xs) and min(ys) <= y0 <= max(ys)):
            st.error("Souřadnice mimo rozsah. Zadejte jiné.")
        else:
            distances_custom = [
                ((x - x0) ** 2 + (y - y0) ** 2) ** 0.5 for x, y, z in coords
            ]
            max_d_custom = max(distances_custom)
            p1c = st.slider("Procento pro blízké body", 0, 100, 80, 5, key="c1")
            p2c = st.slider("Procento pro vzdálené body", 0, 100, 30, 5, key="c2")
            est = int(total * ((p1c + p2c) / 2) / 100)
            st.write(f"Odhad zachovaných bodů: **{est}**")
            if st.button("Redukovat"):
                reduced = []
                for ln, d in zip(lines, distances_custom):
                    local_pct = p1c + (p2c - p1c) * (d / max_d_custom)
                    if random.random() < local_pct / 100:
                        reduced.append(ln)
                keep = len(reduced)
                if keep < 1:
                    st.error("Žádné body nezůstaly – změňte procenta nebo bod.")
                else:
                    out = io.StringIO("\n".join(reduced))
                    st.download_button(
                        "Stáhnout redukovaný soubor",
                        data=out.getvalue(),
                        file_name=uploaded_file.name.replace(".xyz", "_reduced.xyz"),
                        mime="text/plain",
                    )