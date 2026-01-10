import streamlit as st
import sqlite3
from datetime import date
import unicodedata
import difflib

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="Bloom - Présence", layout="wide")

# ======================
# SESSION
# ======================
if "show_app" not in st.session_state:
    st.session_state.show_app = False
if "noms_input" not in st.session_state:
    st.session_state.noms_input = ""

# ======================
# STYLE
# ======================
st.markdown("""
<style>
.welcome {
    background-color: black;
    color: white;
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 38px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ======================
# BIENVENUE
# ======================
if not st.session_state.show_app:
    st.markdown("<div class='welcome'>🌸 Bienvenue sur l’app Bloom</div>", unsafe_allow_html=True)
    if st.button("Entrer"):
        st.session_state.show_app = True
        st.rerun()
    st.stop()

# ======================
# FONCTIONS
# ======================
def normaliser(txt):
    txt = txt.lower()
    txt = unicodedata.normalize("NFD", txt)
    return "".join(c for c in txt if unicodedata.category(c) != "Mn").strip()

def capitaliser(nom):
    return " ".join(p.capitalize() for p in nom.split())

def trouver_nom(entree, base):
    base_norm = {normaliser(n): n for n in base}
    e = normaliser(entree)
    if e in base_norm:
        return base_norm[e]
    proche = difflib.get_close_matches(e, base_norm.keys(), n=1, cutoff=0.7)
    if proche:
        return base_norm[proche[0]]
    return None

def afficher_liste(titre, noms, symbole):
    st.subheader(titre)
    texte = "\n".join(f"{symbole} {n}" for n in sorted(noms)) if noms else "Aucun"
    st.text_area("", texte, height=180, key=titre)

# ======================
# BASE DE DONNÉES
# ======================
conn = sqlite3.connect("presence.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS filles (id INTEGER PRIMARY KEY, nom TEXT UNIQUE)")
cursor.execute("CREATE TABLE IF NOT EXISTS garcons (id INTEGER PRIMARY KEY, nom TEXT UNIQUE)")
cursor.execute("CREATE TABLE IF NOT EXISTS coachs (id INTEGER PRIMARY KEY, nom TEXT UNIQUE)")
conn.commit()

# ======================
# DONNÉES
# ======================
filles = [
    "danielle","camille","charis","chrismaëlla","sarah","helena",
    "joëlle","kenza","leila","maïva","mariska","sainte","angèle",
    "melea","ketlyn","romaine","dalhia","holy","ana","josé"
]

garcons = [
    "jhosue","iknan","ighal","patrick","jeremie darlick","jeremie",
    "alain emmanuel","arthur","nathan","stephen","yvan"
]

coachs = ["noelvine","jean junior","valérie","aurel"]

for n in filles:
    cursor.execute("INSERT OR IGNORE INTO filles (nom) VALUES (?)", (n,))
for n in garcons:
    cursor.execute("INSERT OR IGNORE INTO garcons (nom) VALUES (?)", (n,))
for n in coachs:
    cursor.execute("INSERT OR IGNORE INTO coachs (nom) VALUES (?)", (n,))
conn.commit()

# ======================
# APPLICATION
# ======================
st.title("Liste de présence de Bloom")
st.write("Date :", date.today().strftime("%d/%m/%Y"))

st.markdown("### Écrivez ici le nom des présents aujourd’hui")
st.text_area("", height=180, key="noms_input")

valider = st.button("Valider")
reset = st.button("Réinitialiser")

if reset:
    st.session_state.noms_input = ""
    st.rerun()

# ======================
# TRAITEMENT AVANCÉ
# ======================
if valider:
    entrees = [n.strip() for n in st.session_state.noms_input.splitlines() if n.strip()]

    cursor.execute("SELECT nom FROM filles")
    toutes_filles = [r[0] for r in cursor.fetchall()]
    cursor.execute("SELECT nom FROM garcons")
    tous_garcons = [r[0] for r in cursor.fetchall()]
    cursor.execute("SELECT nom FROM coachs")
    tous_coachs = [r[0] for r in cursor.fetchall()]

    filles_p, garcons_p, coachs_p = set(), set(), set()

    # ---- RECONNAISSANCE ROBUSTE ----
    for e in entrees:
        if (r := trouver_nom(e, toutes_filles)):
            filles_p.add(capitaliser(r))
        elif (r := trouver_nom(e, tous_garcons)):
            garcons_p.add(capitaliser(r))
        elif (r := trouver_nom(e, tous_coachs)):
            coachs_p.add(capitaliser(r))

    # ---- CALCUL DES ABSENTS ----
    filles_p_norm = {normaliser(n) for n in filles_p}
    garcons_p_norm = {normaliser(n) for n in garcons_p}
    coachs_p_norm = {normaliser(n) for n in coachs_p}

    filles_a = {capitaliser(n) for n in toutes_filles if normaliser(n) not in filles_p_norm}
    garcons_a = {capitaliser(n) for n in tous_garcons if normaliser(n) not in garcons_p_norm}
    coachs_a = {capitaliser(n) for n in tous_coachs if normaliser(n) not in coachs_p_norm}

    # ---- AFFICHAGE DES LISTES ----
    st.markdown("## Résultats")

    afficher_liste("Filles présentes", filles_p, "✓")
    afficher_liste("Filles absentes", filles_a, "✗")

    afficher_liste("Garçons présents", garcons_p, "✓")
    afficher_liste("Garçons absents", garcons_a, "✗")

    afficher_liste("Coachs présents", coachs_p, "✓")
    afficher_liste("Coachs absents", coachs_a, "✗")
