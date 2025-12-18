import streamlit as st
from datetime import date

# ======================
# CONFIG PAGE
# ======================
st.set_page_config(page_title="Bloom", layout="wide")

# ======================
# STYLE GLOBAL
# ======================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
}

textarea {
    color: black !important;
    font-size: 15px;
}

button {
    background-color: orange !important;
    color: white !important;
    font-weight: bold !important;
    border: none !important;
}
</style>
""", unsafe_allow_html=True)

# ======================
# ÉTAT INITIAL
# ======================
if "go" not in st.session_state:
    st.session_state.go = False

if "saisie" not in st.session_state:
    st.session_state.saisie = ""

# ======================
# MESSAGE BIENVENUE
# ======================
if not st.session_state.go:
    st.markdown(
        "<h1 style='text-align:center;color:white;'>Bienvenue sur l'app Bloom</h1>",
        unsafe_allow_html=True
    )
    if st.button("Entrer"):
        st.session_state.go = True
    # on AFFICHERA l'app au prochain rerun
else:

    # ======================
    # BASE DES NOMS (FIXE)
    # ======================
    filles = {
        "Angèle","Camille","Helena","Joëlle","Josée","Julyahana","Ketlyn","Maïva",
        "Mariska","Romaine","Méléa","Kenza","Ketsia","Chrismaëlla","Jade","Daliah"
    }

    garcons = {
        "Arthur","Alain Emmanuel","Jhosue","Stephen","Darlick","Jéremie",
        "Iknan","Ighal","Yvan","Evans","André","Karl Emmanuel"
    }

    coachs = {
        "Noelvine","Jean Junior","Valérie","Aurel"
    }

    # ======================
    # TITRE SELON LE JOUR
    # ======================
    jour = date.today().weekday()
    titres = {
        2: "Liste de présence – MDP",
        4: "Liste de présence – Réunion en ligne",
        5: "Liste de présence – Réunion des jeunes",
        6: "Liste de présence – Culte du dimanche"
    }
    titre = titres.get(jour, "Liste de présence de Bloom")

    # ======================
    # AFFICHAGE PRINCIPAL
    # ======================
    st.markdown(f"<h1 style='color:orange'>{titre}</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color:white'>Date : {date.today().strftime('%d/%m/%Y')}</p>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='color:orange;font-weight:bold'>"
        "Écrivez ici le nom des présents aujourd’hui (un par ligne)"
        "</p>",
        unsafe_allow_html=True
    )

    st.text_area("", height=180, key="saisie")

    c1, c2 = st.columns(2)
    valider = c1.button("Valider")
    reset = c2.button("Réinitialiser")

    if reset:
        st.session_state.saisie = ""

    # ======================
    # TRAITEMENT
    # ======================
    if valider:

        def clean(n):
            return n.strip().capitalize()

        presents = {
            clean(n)
            for n in st.session_state.saisie.split("\n")
            if n.strip()
        }

        # PRÉSENTS PAR GROUPE
        filles_p = filles & presents
        garcons_p = garcons & presents
        coachs_p = coachs & presents

        # ABSENTS (LOGIQUE CORRECTE)
        filles_abs = filles - filles_p
        garcons_abs = garcons - garcons_p
        coachs_abs = coachs - coachs_p

        # ======================
        # LISTE COPIABLE
        # ======================
        texte = (
            f"{titre}\n"
            f"Date : {date.today().strftime('%d/%m/%Y')}\n\n"
            "PRÉSENTS\n"
        )

        texte += "\n".join(f"🟢 {n}" for n in sorted(presents)) if presents else "Aucun"

        texte += "\n\nABSENTS\n"
        texte += "\n".join(
            f"🔴 {n}" for n in sorted(filles_abs | garcons_abs)
        ) if (filles_abs or garcons_abs) else "Aucun"

        texte += "\n\nABSENTS COACHS\n"
        texte += "\n".join(f"🔴 {n}" for n in sorted(coachs_abs)) if coachs_abs else "Aucun"

        texte += (
            "\n\nTOTAUX PRÉSENTS\n"
            f"Filles : {len(filles_p)}\n"
            f"Garçons : {len(garcons_p)}"
        )

        st.text_area("Liste finale (copiable)", texte, height=450)

