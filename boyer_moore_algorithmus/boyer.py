# -*- coding: utf-8 -*-
# Boyer-Moore-Algorithmus für das schnelle Auffinden von Mustern in Texten

# Diese Python-Implementierung basiert auf der C++-Implementierung aus Wikipedia:
# Quelle: https://de.wikipedia.org/wiki/Boyer-Moore-Algorithmus
# Die Logik wurde in Python übertragen und für die URL-Analyse angepasst.
# Bitte beachten: Diese Implementierung ist ausgelegt für "bereinigte" Datensätze also nur Phishing URLs oder legitime!


#---------------------------- Imports ---------------------------------#

from datetime import datetime
import time
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, f1_score, ConfusionMatrixDisplay
from matplotlib.colors import ListedColormap

#---------------------------- Boyer-Moore-Algorithmus ---------------------------------#


def is_prefix_of_pattern(pattern: str, position: int) -> bool:
    """
    Überprüft, ob ein Teil des Musters ab einer bestimmten Position ein Präfix des Musters ist.
    Wird in der "Good-Suffix-Heuristic" verwendet, um die Sprünge zu optimieren.
    """
    for i in range(position, len(pattern)):
        j = i - position  # Vergleich mit dem Präfix
        if pattern[i] != pattern[j]:  # Sobald es nicht passt -> kein Präfix
            return False
    return True


def suffix_length_matching_prefix(pattern: str, position: int) -> int:
    """
    Berechnet die Länge des Suffixes eines Musters, das mit einem Präfix übereinstimmt.
    Diese Funktion ist Teil der "Good-Suffix-Heuristic", um die Sprünge zu optimieren.
    """
    size = 0  # Wie viele Zeichen passen von hinten zusammen?
    i, j = position, len(pattern) - 1  # Start hinten im Muster

    while i >= 0 and pattern[i] == pattern[j]:
        i -= 1  # Rückwärts laufen
        j -= 1
        size += 1

    return size  # Länge des Suffixes zurückgeben


def build_bad_character_table(pattern: str) -> list[int]:
    """
    Erstellt die "Bad-Character-Heuristic"-Tabelle für den Boyer-Moore-Algorithmus.
    Sie beschreibt, wie viele Zeichen übersprungen werden können, wenn ein Zeichen nicht passt.
    """
    table = [len(pattern)] * 256  # Für alle ASCII-Zeichen (256 Zeichen)

    for i in range(len(pattern) - 1):  # Für jedes Zeichen im Muster (außer dem letzten)
        table[ord(pattern[i])] = len(pattern) - 1 - i  # Speichere die Sprungweite für dieses Zeichen

    return table


def build_good_suffix_table(pattern: str) -> list[int]:
    """
    Erstellt die "Good-Suffix-Heuristic"-Tabelle für den Boyer-Moore-Algorithmus.
    Sie hilft zu bestimmen, wie viel weiter das Muster verschoben werden kann, wenn ein Teil des Musters übereinstimmt.
    """
    table = [0] * len(pattern)
    last_prefix_position = len(pattern)

    for i in range(len(pattern), 0, -1):  # Rückwärts durchs Muster
        if is_prefix_of_pattern(pattern, i):  # Prüft, ob ein Präfix gefunden wurde
            last_prefix_position = i
        table[len(pattern) - i] = last_prefix_position - i + len(pattern)

    for i in range(len(pattern) - 1):  # Suche nach passenden Suffixen
        size = suffix_length_matching_prefix(pattern, i)
        table[size] = len(pattern) - 1 - i + size  # Berücksichtige Suffix übereinstimmende Teile

    return table


def find_pattern_in_string(string_to_search: str, pattern: str, bad_char_table: list[int], good_suffix_table: list[int]) -> int:
    """
    Sucht nach einem Muster in einem String und gibt zurück, wie oft es vorkommt.
    Verwendet die "Bad-Character-Heuristic" und "Good-Suffix-Heuristic" zur Optimierung.
    """
    if not pattern:
        return 0  # Leeres Muster = nichts zu tun

    count = 0  # Zähler für Treffer
    i = len(pattern) - 1  # Start am Ende des Musters

    while i < len(string_to_search):
        j = len(pattern) - 1  # Vergleich von hinten nach vorne

        # Prüfe, ob Muster mit einem Teilstring übereinstimmt
        while j >= 0 and i < len(string_to_search) and pattern[j] == string_to_search[i]:
            if j == 0:  # Komplettes Muster gefunden
                count += 1
                break
            i -= 1
            j -= 1

        if i < len(string_to_search):
            # Berechne, wie viel wir springen können, wenn das Muster nicht passt
            skip_char = ord(string_to_search[i]) if 0 <= ord(string_to_search[i]) < 256 else 0
            skip_value = max(good_suffix_table[len(pattern) - 1 - j], bad_char_table[skip_char])
            i += skip_value  # Spring weiter!

        if i >= len(string_to_search):
            break

    return count


def preprocess_patterns(list_patterns: list[str]) -> tuple:
    """
    Bereitet alle Muster vor, indem die "Bad-Character-Heuristic"- und "Good-Suffix-Heuristic"-Tabellen erstellt werden.
    """
    all_bad_char_table = []  # Hier speichern wir die Bad-Character-Heuristic-Tabellen
    all_good_suffix_table = []  # Hier die Good-Suffix-Heuristic-Tabellen
    occurrences_of_pattern_in_string = []  # Zähler für jedes Muster

    for pattern in list_patterns:
        all_bad_char_table.append(build_bad_character_table(pattern))  # Erstelle Bad-Character-Heuristic-Tabelle
        all_good_suffix_table.append(build_good_suffix_table(pattern))  # Erstelle Good-Suffix-Heuristic-Tabelle
        occurrences_of_pattern_in_string.append(0)  # Initialisiere Treffer-Zähler

    return all_bad_char_table, all_good_suffix_table, occurrences_of_pattern_in_string


def preprocess_txt_file(txtfile) -> list[str]:
    """
    Liest eine Datei ein und gibt die Zeilen als Liste zurück (z. B. URLs).
    """
    return [line.rstrip() for line in open(txtfile, encoding="utf-8")]


def boyer_moore(txtfile, list_of_patterns: list[str]) -> tuple:
    """
    Sucht mit dem Boyer-Moore-Algorithmus nach Mustern in einer Datei.
    Gibt zurück:
    - Die Liste der Muster
    - Wie oft jedes Muster gefunden wurde
    - Die Anzahl eindeutiger URLs mit Treffern
    Dabei ist zu beachten die Implementation ist auf Datensätze ausgelegt die Phishing und Legitime URLs in unterschiedlichen Dateien haben.
    """
    url_seen = set()  # Set für eindeutige URLs
    all_bad_char_table, all_good_suffix_table, occurrences_of_pattern = preprocess_patterns(list_of_patterns)
    text_strings = preprocess_txt_file(txtfile)

    for eintrag in text_strings:
        for index_pattern in range(len(list_of_patterns)):
            if find_pattern_in_string(eintrag, list_of_patterns[index_pattern], all_bad_char_table[index_pattern], all_good_suffix_table[index_pattern]) > 0:
                url_seen.add(eintrag)  # URL als gesehen markieren
                occurrences_of_pattern[index_pattern] += 1  # Treffer für das Muster erhöhen

    return list_of_patterns, occurrences_of_pattern, len(url_seen)

#---------------------------- Zeitmessung ---------------------------------#

def average_time(timer: list) -> list:
    """
    Berechnet den Durchschnitt der Zeiten für 1 URLs und darauf basiert von 50 URLs.
    """
    avg = timer[0]
    for k in range(1,len(timer)):
            avg += timer[k]
                
    return avg / len(timer), avg / len(timer) * 50

    


def boyer_moore_timed(txtfile, list_of_patterns: list[str]) -> tuple:
    """
    Sucht mit dem Boyer-Moore-Algorithmus nach Mustern in einer Datei.
    Gibt zurück:
    - Die Liste der Muster
    - Wie oft jedes Muster gefunden wurde
    - Die Anzahl eindeutiger URLs mit Treffern
    - Die durchschnittliche Zeit für die Suche nach allen Musters in einer URL bzw. 50 URLs
    Dabei ist zu beachten die Implementation ist auf Datensätze ausgelegt die Phishing und Legitime URLs in unterschiedlichen Dateien haben.
    """
    url_seen = set()  # Set für eindeutige URLs
    all_bad_char_table, all_good_suffix_table, occurrences_of_pattern = preprocess_patterns(list_of_patterns)
    text_strings = preprocess_txt_file(txtfile)

    timer = []
    for eintrag in text_strings:
        start = datetime.now()
        for index_pattern in range(len(list_of_patterns)):
            find_pattern_in_string(eintrag, list_of_patterns[index_pattern], all_bad_char_table[index_pattern], all_good_suffix_table[index_pattern])
        end = datetime.now()
        timer.append(end-start)
        time.sleep(1)

    return list_of_patterns, occurrences_of_pattern, len(url_seen), average_time(timer)


#---------------------------- Visualisierung ---------------------------------#

def boyer_moore_visualised(txtfile_phishing,txtfile_legit, list_of_patterns: list[str]):
    """
    Sucht mit dem Boyer-Moore-Algorithmus nach Mustern in 2 Datensätzen(Phishing und legitime URLs)
    """

    patterns, occurrences_of_pattern_in_phishing, total_hits_in_txtfile_phishing = boyer_moore(txtfile_phishing, list_of_patterns) # Boyer-Moore-Algo ausführen für phishing URL Datensatz
    patterns, occurrences_of_pattern_in_legit, total_hits_in_txtfile_legit = boyer_moore(txtfile_legit, list_of_patterns) # Boyer-Moore-Algo ausführen für legit URL Datensatz


    calculate_and_plot_confusion_matrix(total_hits_in_txtfile_phishing,
                                        count_lines_readlines(txtfile_phishing) - total_hits_in_txtfile_phishing, 
                                        total_hits_in_txtfile_legit, 
                                        count_lines_readlines(txtfile_legit) - total_hits_in_txtfile_legit)

    top_10_hits(occurrences_of_pattern_in_phishing,patterns,txtfile_phishing)
    top_10_hits(occurrences_of_pattern_in_legit,patterns,txtfile_legit)


def top_10_hits(count_in,patterns,txtfile="test.txt"):
    """
    Visualisiert die 10 häufigsten Muster in einer Liste.
    """
    count, pattern = zip(*(list(sorted(zip(count_in,patterns),reverse = True)[:10])))

    fig, ax = plt.subplots()
    ax.bar(pattern, count, width=0.6)

    ax.set_ylabel('Auftreten')
    ax.set_title(f"10 Häufigste Muster in {txtfile}")


def calculate_and_plot_confusion_matrix(true_positive, false_positive, false_negative, true_negative):
    """
    Berechnet die Confusion Matrix und den F1-Score und plottet die Confusion Matrix.
    """
    # Berechnung der Confusion Matrix
    y_true = np.array([1] * true_positive + [0] * false_negative + [1] * false_positive + [0] * true_negative)
    y_pred = np.array([1] * true_positive + [1] * false_negative + [0] * false_positive + [0] * true_negative)
    
    cm = confusion_matrix(y_true, y_pred)
    cm_sum = np.sum(cm)
    cm_perc = cm / cm_sum * 100

    # Berechnung des F1-Scores
    f1 = f1_score(y_true, y_pred)

    # Erstellen einer helleren Farbkarte
    cmap = ListedColormap(plt.cm.Blues(np.linspace(0.27, 0.86, 256)))
    
    # Plotten der Confusion Matrix
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['Negative', 'Positive'])
    disp.plot(cmap=cmap)
    
    # Hinzufügen von personalisiertem Text in jedes Feld
    personalized_texts = [
        ["Echte Url als\n Echte Url", "Echte Url als\n Phishing Url"],
        ["Phishing Url als\n Echte Url", "Phishing Url als\n Phishing Url"]
    ]
    
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            plt.text(j, i+0.2, f'{cm_perc[i, j]:.2f}%\n({personalized_texts[i][j]})', ha='center', va='center', color='black')
    
    plt.title(f'Confusion Matrix\nF1 Score: {f1:.2f}')
    plt.show()
    
    return f1



#---------------------------- Zusätzliche Hilfsfunktionen for ease of use -----------------------#

def convert_file_to_lowercase(file_path):
    """
    Wandelt den Inhalt einer Datei in Kleinbuchstaben um und speichert die Änderungen zurück in die Datei.
    """
    # Datei öffnen und Inhalt lesen
    with open(file_path, 'r', encoding="utf-8") as file:
        content = file.read()
    
    # Inhalt in Kleinbuchstaben umwandeln
    lower_content = content.lower()
    
    # Geänderten Inhalt zurück in die Datei schreiben
    with open(file_path, 'w', encoding="utf-8") as file:
        file.write(lower_content)

def count_lines_readlines(filename):
    """
    Zählt die Anzahl der Zeilen in einer Datei.
    """
    with open(filename, encoding="utf-8") as f:
        return len(f.readlines())
    

#----------------------------DACS 24/04 ---------------------------------------------------------#

