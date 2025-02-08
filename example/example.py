import boyer_moore_algorithmus as boyer

list_of_patterns = [
    "http://","@","?","=","_","confirm","account",
    "banking","secure","webscr","login","signin","top","xyz",
    "cn","info","shop","online","sbs","ru","lol","site","cfd"
    "club","bond","live","cc","life","click","paypal"
]

print("----------Normale Version----------")
list_of_patterns, occurrences_of_pattern, total_hits = boyer.boyer_moore("example\dataset_phishing.txt",list_of_patterns)
print(f"Anzahl von jedem Muster: {occurrences_of_pattern} Gefunde Phishing URLs: {total_hits}")


print("----------Zeitmessung----------")
list_of_patterns, occurrences_of_pattern, total_hits, timer = boyer.boyer_moore_timed("example\dataset_timed.txt",list_of_patterns)
print(f"Anzahl von jedem Muster: {occurrences_of_pattern} Legitime URLs als Phishing makiert: {total_hits} ")
print(f"Die durchschnittliche Zeit für die Suche nach allen Musters innerhalb einer URL bzw. 50 URLs:{timer} " )


print("----------Visualisierung----------")
boyer.boyer_moore_visualised("example\dataset_phishing.txt","example\dataset_legitim.txt",list_of_patterns)

