import streamlit as st
import sqlite3
from datetime import date
import unicodedata
import difflib
import streamlit.components.v1 as components

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="Bloom - Présence", layout="wide")

if "show_app" not in st.session_state:
    st.session_state.show_app = False
if "noms_input" not in st.session_state:
    st.session_state.noms_input = ""

# ======================
# STYLE
# ======================
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #006D66;
    color: #fff;
}
h1, h2, h3 { color: #FFD700 !important; }
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
textarea {
    background-color: #f5f5f5 !important;
    color: #000 !important;
}
button {
    background-color: #FFD700;
    color: #000;
    border: none;
    padding: 8px 16px;
    font-size: 16px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ======================
# ACCUEIL
# ======================
if not st.session_state.show_app:
    st.markdown("<div class='welcome'>Bienvenue sur l’app Bloom</div>", unsafe_allow_html=True)
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
    return base_norm[proche[0]] if proche else None

# ======================
# BASE DE DONNÉES
# ======================
conn = sqlite3.connect("presence.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS filles (id INTEGER PRIMARY KEY, nom TEXT UNIQUE)")
cursor.execute("CREATE TABLE IF NOT EXISTS garcons (id INTEGER PRIMARY KEY, nom TEXT UNIQUE)")
cursor.execute("CREATE TABLE IF NOT EXISTS coachs (id INTEGER PRIMARY KEY, nom TEXT UNIQUE)")
conn.commit()

filles = [
    "danielle","camille","charis","chrismaëlla","sarah","helena",
    "joëlle","kenza","leila","maïva","mariska","sainte","angèle",
    "méléa","ketlyn","romaine","daliah","holy","ana","josé"
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
# TITRE
# ======================
jours = {
    3: "Mercredi – Liste de présence MDP",
    5: "Samedi – Liste de présence Réunion des jeunes",
    6: "Dimanche – Liste de présence Culte du dimanche"
}
titre_jour = jours.get(date.today().weekday(), "Liste de présence")

st.title(titre_jour)
st.write("Date :", date.today().strftime("%d/%m/%Y"))

# ======================
# SAISIE
# ======================
st.markdown("### Écrivez ici le nom des présents aujourd’hui")
st.text_area("", height=180, key="noms_input")

valider = st.button("Valider")
reset = st.button("Réinitialiser")

if reset:
    st.session_state.noms_input = ""
    st.rerun()

# ======================
# TRAITEMENT
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

    for e in entrees:
        if r := trouver_nom(e, toutes_filles):
            filles_p.add(capitaliser(r))
        elif r := trouver_nom(e, tous_garcons):
            garcons_p.add(capitaliser(r))
        elif r := trouver_nom(e, tous_coachs):
            coachs_p.add(capitaliser(r))

    filles_a = {capitaliser(n) for n in toutes_filles if capitaliser(n) not in filles_p}
    garcons_a = {capitaliser(n) for n in tous_garcons if capitaliser(n) not in garcons_p}
    coachs_a = {capitaliser(n) for n in tous_coachs if capitaliser(n) not in coachs_p}

    presents = sorted(filles_p | garcons_p | coachs_p)
    absents = sorted(filles_a | garcons_a | coachs_a)

    texte_final = "\n".join(
        [titre_jour, f"Date : {date.today().strftime('%d/%m/%Y')}", "",
         "Présents:"] +
        [f"✓ {n}" for n in presents] + ["", "Absents:"] +
        [f"✗ {n}" for n in absents]
    )

    st.markdown("## Liste complète copiable")
    components.html(f"""
    <textarea style="width:100%;height:400px;">{texte_final}</textarea>
    <br>
    <button onclick="navigator.clipboard.writeText(this.previousElementSibling.value)">
        Copier la liste
    </button>
    """, height=450)
