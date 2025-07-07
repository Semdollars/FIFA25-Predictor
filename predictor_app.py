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

        if team1 != team2 and st.button("🔮 Prédire le match"):
            score, winner = predict_score(team1, team2, stats)
            if score:
                st.info(f"Score estimé : {team1.title()} {score[0]} - {score[1]} {team2.title()}")
                st.success(f"🏆 Vainqueur probable : {winner}")
            else:
                st.warning("Pas assez de données pour prédire ce match.")
    else:
        st.error("Aucun score détecté dans le texte.")
