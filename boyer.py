# -*- coding: utf-8 -*-
# Boyer-Moore-Algorithmus für das schnelle Auffinden von Mustern in Texten

# Diese Python-Implementierung basiert auf der C++-Implementierung aus Wikipedia:
# Quelle: https://de.wikipedia.org/wiki/Boyer-Moore-Algorithmus
# Die Logik wurde in Python übertragen und für die URL-Analyse angepasst.


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
    i = position
    j = len(pattern) - 1  # Start hinten im Muster

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


# Muster zum Suchen (z. B. verdächtige Domains oder Zeichen in URLs)
list_of_patterns = [".xyz", ".com", "-", "@", "_"]

# Starte die Analyse
print(boyer_moore("all_urls.txt", list_of_patterns))
