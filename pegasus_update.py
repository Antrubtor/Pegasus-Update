import os
import json
import requests
from bs4 import BeautifulSoup

def get_html(auth_url):
    session = requests.Session()
    response = session.get(auth_url)
    response_new = session.get('https://prepa-epita.helvetius.net/pegasus/index.php?com=extract&job=extract-notes')
    return response_new.text


def parse_to_dict(file_html):
    dictionary = {}

    soup = BeautifulSoup(file_html, 'html.parser')
    td_elements = soup.find_all('td', {'colspan': '27', 'class': 'dsp_data_td_fils'})

    for td in td_elements:
        page_cells = td.find_all('td', class_='dsp_data_td_data', title='Libellé du produit')
        for cell in page_cells: # get the name of the subject
            div_content = cell.find('div')
            if div_content and div_content.text.strip():
                dict_name = div_content.text.strip()
                break

        cc_qcm_elements = td.find_all('td', class_='dsp_data_td_data', title='Type de note')
        note_elements = td.find_all('td', class_='dsp_data_td_data', title=lambda value: value and 'Note' in value)

        association_list = []
        for i in range(len(cc_qcm_elements)):
            cc_qcm_text = cc_qcm_elements[i].find('div').text if cc_qcm_elements[i].find('div') else None
            note_text = note_elements[i].find('div').text if note_elements[i].find('div') else None
            if cc_qcm_text and note_text:
                association_list.append((cc_qcm_text, note_text))
        dictionary[dict_name] = association_list
    return dictionary

def differences(dict1, dict2):  # dict2 is new dict
    print("\n\n\n")
    embed_field_list = []

    diff = "/".join(set(list(dict1)).symmetric_difference(set(list(dict2.keys()))))[0:1023]
    if diff != "":
        embed_field_list.append({
            "name": "Added Categories",
            "value": diff,
            "inline": False
        })
        print(f"Added Categories\n{diff}\n--------------------------------------")
    for inter in set(list(dict1)).intersection(set(list(dict2.keys()))):
        grade1 = dict1[inter]
        grade2 = dict2[inter]

        if len(grade1) != len(grade2):
            for i in range(min(len(grade1), len(grade2)), max(len(grade1), len(grade2))):
                gr = ""
                try:
                    gr = grade2[i]
                except:
                    gr = grade1[i]
                name = f"Added grade field in {inter}"
                embed_field_list.append({
                    "name": name[:255],
                    "value": f"{gr[0]} : {gr[1]}",
                    "inline": False
                })
                print(f"Added grade field in {inter}\n{gr[0]} : {gr[1]}\n--------------------------------------")
        else:
            for i in range(len(grade1)):
                if grade1[i] != grade2[i]:
                    name = f"New grade in {inter}"
                    embed_field_list.append({
                        "name": name[:255],
                        "value": f"{grade2[i][0]} : {grade2[i][1]}",
                        "inline": False
                    })
                    print(f"New grade in {inter}\n{grade2[i][0]} : {grade2[i][1]}\n--------------------------------------")
    print("\n\n\n")
    return embed_field_list


def send_webhook(embed_field_list, WEBHOOK_URL):
    color = 0

    length = len(embed_field_list)
    if 0 < length < 3:  # difference number change color
        color = 15871
    elif 3 <= length < 5:
        color = 65535
    elif 5 <= length < 9:
        color = 2752256
    elif 9 <= length < 12:
        color = 16121600
    else:
        color = 16711680

    embeds_list = [embed_field_list[i:i + 24] for i in range(0, len(embed_field_list), 24)]     # max embed field

    embeds = []
    for emb in embeds_list: # make embeds bloc
        embeds.append({
                "color": color,
                "fields": emb,
                "author": {
                        "name": "Pegasus update",
                        "icon_url": "https://epita-etu.helvetius.net/pegasus/assets/images/pegasus/medium-logo-pegasus.png"
                        }
        })
    data = {
        "content": "@everyone",
        "embeds": embeds[:9],
        "avatar_url": "https://prepa-epita.helvetius.net/pegasus/assets/images/pegasus/medium-logo-pegasus-entete.png",
    }
    send(data, WEBHOOK_URL)

def send_webhook_empty(WEBHOOK_URL):
    print("No new notes")
    embed = {
        "title": "No new notes",
        "color": 0,
        "author": {
            "name": "Pegasus update",
            "icon_url": "https://epita-etu.helvetius.net/pegasus/assets/images/pegasus/medium-logo-pegasus.png"
        }
    }

    data = {
        "embeds": [
            embed
        ],
    }
    send(data, WEBHOOK_URL)

def send(data, WEBHOOK_URL):
    headers = {
        "Content-Type": "application/json"
    }
    result = requests.post(WEBHOOK_URL, json=data, headers=headers)
    if 200 <= result.status_code < 300:
        print(f"Webhook sent {result.status_code}")
    else:
        print(f"Not sent with {result.status_code}, response:\n{result.json()}")

def main():
    if os.path.isfile("tokens.json") and os.path.isfile("pegasus.txt"):
        with open('tokens.json', 'r') as json_file:
            tokens_data = json.load(json_file)

        discord_webhook = tokens_data['discord_webhook']
        pegasus_url = tokens_data['pegasus_url']

        with open("pegasus.txt", 'r', encoding='utf-8') as file:
            file1_html = file.read()
        print("Getting HTML...")
        file2_html = get_html(pegasus_url)

        if file1_html == file2_html:    # If nothing has changed
            send_webhook_empty(discord_webhook)
        else:
            dict_1 = parse_to_dict(file1_html)  # old
            dict_2 = parse_to_dict(file2_html)  # new
            embed_field_list = differences(dict_1, dict_2)
            send_webhook(embed_field_list, discord_webhook)
            with open("pegasus.txt", 'w', encoding='utf-8') as file:
                file.write(file2_html)
            print("HTML saved")
            print("exit...")

    else:   # first opening
        pegasus_url = ""
        while "https://prepa-epita.helvetius.net/pegasus/gfront-controller.php?com=" not in pegasus_url:
            pegasus_url = str(input("Give your Pegasus url: "))

        webhook_url = ""
        while "https://discord.com/api/webhooks/" not in webhook_url:
            webhook_url = str(input("Give your webhook url: "))

        data = {
            "discord_webhook": webhook_url,
            "pegasus_url": pegasus_url
        }
        with open('tokens.json', 'w') as json_file: # fill json file with tokens
            json.dump(data, json_file)
        print("The tokens have been saved successfully")

        with open("pegasus.txt", 'w', encoding='utf-8') as file:    # fill pegasus.txt for the first time
            file.write(get_html(pegasus_url))
        print("The pegasus HTML page has been saved successfully")

        print("Please restart the program...")

if __name__ == "__main__":
    main()