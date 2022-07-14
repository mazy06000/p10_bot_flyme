import json

with open('performances.json') as json_file:
    performances = json.load(json_file)

nb_successful = len(performances["successfull"])
nb_unsuccessful = len(performances["unsuccessfull"])
nb_total = nb_successful + nb_unsuccessful

success_percent = round((nb_successful/nb_total)*100, 2)
print(f"Taux de réussite du bot: {success_percent}%")