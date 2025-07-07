import streamlit as st
import pandas as pd
import re
import statistics

st.set_page_config(page_title="📊 Prédicteur FIFA 25", layout="centered")
st.title("📊 Prédicteur FIFA FC 25 – Championnat du monde")

# Extraction d'un fichier texte
def parse_scores_from_text(text):
    pattern = r"([A-Za-zÀ-ÿ\s\-']+)\s+et\s+([A-Za-zÀ-ÿ\s\-']+)\s+(\d)[-–](\d)"
    matches = re.findall(pattern, text, re.IGNORECASE)
    data = []
    for eq1, eq2, s1, s2 in matches:
        data.append((eq1.strip().lower(), eq2.strip().lower(), int(s1), int(s2)))
    return data

# Calcul des moyennes
def build_stats(matches):
    stats = {}
    for eq1, eq2, s1, s2 in matches:
        for team, scored, conceded in [(eq1, s1, s2), (eq2, s2, s1)]:
            if team not in stats:
                stats[team] = {'scored': [], 'conceded': []}
            stats[team]['scored'].append(scored)
            stats[team]['conceded'].append(conceded)
    return stats
# Fonction pour afficher les statistiques moyennes d'une équipe
def show_team_stats(team, stats):
    st.subheader(f"📈 Statistiques pour {team.title()}")
    scored = stats[team]['scored']
    conceded = stats[team]['conceded']
    st.markdown(f"""
    - ⚽ **Buts marqués (moyenne)** : {round(statistics.mean(scored), 2)}
    - 🛡️ **Buts encaissés (moyenne)** : {round(statistics.mean(conceded), 2)}
    - 🧾 **Matchs analysés** : {len(scored)}
    """)
# Fonction pour récupérer le top 5 des équipes avec la meilleure attaque
def get_top_teams(stats, top_n=5):
    moyennes = []
    for team, data in stats.items():
        moyenne = statistics.mean(data['scored'])  # moyenne de buts marqués
        moyennes.append((team.title(), round(moyenne, 2)))

    # On trie du plus grand au plus petit
    top = sorted(moyennes, key=lambda x: x[1], reverse=True)[:top_n]
    return top

def predict_score(team1, team2, stats):
    if team1 not in stats or team2 not in stats:
        return None, None
    avg1 = statistics.mean(stats[team1]['scored'])
    avg2 = statistics.mean(stats[team2]['scored'])
    score1 = round(avg1)
    score2 = round(avg2)
    if score1 > score2:
        winner = team1.title()
    elif score2 > score1:
        winner = team2.title()
    else:
        winner = "Match nul"
    return (score1, score2), winner

# Interface
uploaded_file = st.file_uploader("📄 Téléverse ton fichier de scores (format texte)", type="txt")

if uploaded_file is not None:
    raw_text = uploaded_file.read().decode("utf-8")
    matches = parse_scores_from_text(raw_text)

    if matches:
        st.success(f"{len(matches)} matchs détectés.")
        stats = build_stats(matches)

        teams = sorted(set([m[0] for m in matches] + [m[1] for m in matches]))
        team1 = st.selectbox("Équipe 1", teams)
        team2 = st.selectbox("Équipe 2", teams)
st.markdown("---")
show_team_stats(team1, stats)
show_team_stats(team2, stats)
st.markdown("---")

if team1 != team2 and st.button("⚽ Prédire le match"):
    score, winner = predict_score(team1, team2, stats)

    if score:
        st.markdown("---")

        with st.container():
            st.markdown(f"""
            <div style='background-color:#f0f2f6;padding:20px;border-radius:10px;'>
                <h3 style='color:#2c3e50;text-align:center;'>
                    {team1.title()} <span style='color:#72ae60'>{score[0]}</span> -
                    <span style='color:#e74c3c'>{score[1]}</span> {team2.title()}
                </h3>
                <h4 style='text-align:center;color:#2980b9;'>🏆 Gagnant probable : {winner}</h4>
            </div>
            """, unsafe_allow_html=True)


    # Génération du contenu texte à télécharger
    resume = f"""
    📝 Prédiction de match :
    {team1.title()} {score[0]} - {score[1]} {team2.title()}
    Gagnant probable : {winner}
    """

    st.download_button(
        label="📥 Télécharger la prédiction (.txt)",
        data=resume,
        file_name=f"prediction_{team1}_{team2}.txt",
        mime="text/plain"
        else:
            st.warning("Pas assez de données pour prédire ce match.")
    else:
        st.error("Aucun score détecté dans le texte.")

