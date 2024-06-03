import json
import pegasus_update
try:
    import browser_cookie3
except:
    print("You will have to do the manual steps to recover the cookie.")

def get_cookie():
    browsers = ['chrome', 'chromium', 'opera', 'opera_gx', 'brave', 'edge', 'vivaldi', 'firefox', 'librewolf', 'safari']
    for browser in browsers:
        try:
            br = getattr(browser_cookie3, browser)(domain_name='.login.microsoftonline.com')    # get the microsoft cookie of every browsers
            ESTSAUTHPERSISTENT_cookie = br._cookies['.login.microsoftonline.com']['/']['ESTSAUTHPERSISTENT'].value
            return ESTSAUTHPERSISTENT_cookie
        except:
            pass
    print("The ESTSAUTHPERSISTENT cookie was not found")
    print("1) Open a new tab on your browser, and open the inspection page on the Network tab.")
    print("2) Go on \"https://login.microsoftonline.com/common/oauth2/authorize?\"")
    print("3) Click on the authorize request, in the Headers in the Cookie subcategory you find “ESTSAUTHPERSISTENT”. Copy it (without the = and the ending ;).")
    ESTSAUTHPERSISTENT_cookie = str(input("4) Paste it here: "))
    return ESTSAUTHPERSISTENT_cookie

def main():
    webhook_url = str(input("Give your discord webhook url: "))
    print("Now close the browser on which you are connected to pegasus to be able to retrieve the authentication token. (Only if you have browser_cookie3 installed)")
    input("Press enter when you're ready...")

    ESTSAUTHPERSISTENT = get_cookie()
    if ESTSAUTHPERSISTENT is not None:
        print("The cookie was successfully retrieved")

    data = {
        "discord_webhook": webhook_url,
        "ESTSAUTHPERSISTENT_cookie": ESTSAUTHPERSISTENT
    }
    with open('tokens.json', 'w') as json_file:  # fill json file with tokens
        json.dump(data, json_file)
    print("The tokens.json file has been successfully completed")

    pegasus_html = pegasus_update.get_html(ESTSAUTHPERSISTENT, webhook_url)  # create the pegasus html file
    with open("pegasus.html", 'w', encoding='utf-8') as file:
        file.write(pegasus_html)
    print("The pegasus.html file has been successfully completed")
    print("Done, you can now start \"pegasus_update.py\"...")

if __name__ == "__main__":
    main()