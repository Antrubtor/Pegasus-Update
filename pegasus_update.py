import os
import sys
import json
import requests
from bs4 import BeautifulSoup

def get_html(ESTSAUTHPERSISTENT, discord_webhook):
    try:
        session = requests.Session()
        response = session.get("https://prepa-epita.helvetius.net/pegasus/index.php")
        cookies = response.cookies.get_dict()
        phpsessid = cookies.get('PHPSESSID')
        response = session.get('https://prepa-epita.helvetius.net/pegasus/o365Auth.php', allow_redirects=False)
        response = session.get(response.headers.get("Location"), allow_redirects=False)
        cookies = {
            'ESTSAUTHPERSISTENT': ESTSAUTHPERSISTENT
        }
        response = session.get(response.headers.get("Location"), cookies=cookies, allow_redirects=False)
        response = session.get(response.headers.get("Location"), allow_redirects=False)
        location = response.headers.get("Location")
        response = session.get(f"https://prepa-epita.helvetius.net/pegasus/{location}")
        response = session.get('https://prepa-epita.helvetius.net/pegasus/index.php?com=extract&job=extract-notes')
        print("Page loaded")
        return response.text
    except:
        send_webhook_custom(discord_webhook, "Unable to retrieve Pegasus web page, cookie may have expired.", 15548997)
        sys.exit(0)


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
    print(diff)
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
        "content": "@oui", ##TODO: remettre @everyone
        "embeds": embeds[:9],
        "avatar_url": "https://prepa-epita.helvetius.net/pegasus/assets/images/pegasus/medium-logo-pegasus-entete.png",
    }
    send(data, WEBHOOK_URL)

def send_webhook_custom(WEBHOOK_URL, text, color):
    print(text)
    embed = {
        "title": text,
        "color": color,
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
    if os.path.isfile("tokens.json") and os.path.isfile("pegasus.html"):
        with open('tokens.json', 'r') as json_file:
            tokens_data = json.load(json_file)

        discord_webhook = tokens_data['discord_webhook']
        ESTSAUTHPERSISTENT_cookie = tokens_data['ESTSAUTHPERSISTENT_cookie']

        with open("pegasus.html", 'r', encoding='utf-8') as file:
            file1_html = file.read()
        print("Getting HTML...")
        file2_html = get_html(ESTSAUTHPERSISTENT_cookie, discord_webhook)

        if file1_html == file2_html:  # If nothing has changed
            send_webhook_custom(discord_webhook, "No new grade", 0)
        else:
            dict_1 = parse_to_dict(file1_html)  # old
            dict_2 = parse_to_dict(file2_html)  # new
            embed_field_list = differences(dict_1, dict_2)
            send_webhook(embed_field_list, discord_webhook)
            with open("pegasus.html", 'w', encoding='utf-8') as file:
                file.write(file2_html)
            print("HTML saved")
            print("exit...")

    else:   # first opening
        print("Start \"setup.py\" before launching this file.")

if __name__ == "__main__":
    main()