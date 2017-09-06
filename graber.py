from html.parser import HTMLParser
from urllib.request import urlopen
from json import load, dumps
from datetime import datetime
import argparse

just_updated = {}

with open("config.json") as config:
    config = load(config)

class ContentParser(HTMLParser):
    """ Extracts the Content from the entire page. """

    def __init__(self, html):
        super().__init__()
        self.opened = False # parsing content?
        self.openDivs = 1 # divs until content ends
        self.content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>mOffwiki</title>
    <link href="style.css" rel="stylesheet">
</head>
<body style="padding: 1em;">""" # content
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if self.opened:
            if tag == "div":
                self.openDivs += 1
            attrs = attrs = self.attrsToString(attrs)
            tag = self.get_starttag_text()
            self.content += tag
            # print("Start tag:", tag)
            # print(self.openDivs)
            if self.openDivs <= 0:
                self.content += "</body></html>"
                self.opened = False
                # self.close()
        else:
            # check this tag contains the content
            for attr in attrs:
                if attr == ("id", "mw-content-text"):
                    self.opened = True # -> we can start parsing it

    def handle_endtag(self, tag):
        if self.opened:
            if tag == "div":
                self.openDivs -= 1
            tag = "</{}>".format(tag)
            self.content += tag
            # print("End tag  :", tag)

    def handle_data(self, data):
        if self.opened:
            # print("Data     :", data)
            self.content += data
            if self.openDivs <= 0:
                self.content += "</body></html>"
                self.opened = False
                # self.close()

    def handle_startendtag(self, tag, attrs):
        if self.opened:
            attrs = self.attrsToString(attrs)
            string = ""
            for attr in attrs:
                # converts its name and value to string and adds this to string
                string += " {}=\"{}\"".format(attr[0], attr[1])
                # no exception!
                print("Das Attribut ist zu lang!") if len(attr) > 2 else None
            attrs = string
            tag = "<{}{}>".format(tag, attrs)
            self.content += tag
            # print("Startendtag:", tag)

    def attrsToString(self, attrs):
        """Converts HTMLtag attributs given by HTMLParser to handler functions
         to string."""
        string = ""
        # for every attribut
        for attr in attrs:
            # converts its name and value to string and adds this to string
            string += " {}=\"{}\"".format(attr[0], attr[1])
            # no exception!
            print("Das Attribut ist zu lang!") if len(attr) > 2 else None
        return string

def update(url, title):
    path = "wiki/"
    site = getPage(url)
    global just_updated
    # if it is not updated
    if not title in just_updated:
        # save its content
        open(config["path"] + title + ".html", "w").writelines(ContentParser(site).content)
        # remember this page was just updated
        just_updated[title] = True

class updater(HTMLParser):
    """ Searches for updatable sites and update them."""
    def __init__(self):
        super().__init__()
        self.last_href = ""
        global just_updated
        just_updated = {}

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            updatable = False
            site = None
            for attr in attrs:
                if attr[0] == "href":
                    self.last_href = attr[1]

    def handle_data(self, data):
        if data.lower() in [ (i).lower() for i in config["pages"] ]:
            print(self.last_href)
            update(config["domain"] + "/" + self.last_href, data)

def getPage(url):
    try:
        page = urlopen(url)
    except:
        print("""Keine Aktulisierungen gefunden.

Deine mOffwiki sollte schon aktuell sein, falls nicht:
Bitte überprüfe deine Internetverbindung und 
stelle sicher das du die aktuelle Version besitzt.
Falls es trotz allem nicht funktioniert, informiere mich im Forum.""")
        raise SystemExit
    page = page.read().decode()
    return page

if __name__ == "__main__":
    # handel command-line parsing
    args = argparse.ArgumentParser(description='Download wiki pages.')
    args.add_argument('sites', metavar='sites', nargs='*',
                        help='Sites to download.')
    args.add_argument('-add', dest='add',
                        help='add site to update list')
    args = args.parse_args()

    print(args)
    i = 0
    for page in args.sites:
        update(page, "pageNr.{}.html".format(i))
        ++i

    updater = updater()
    # bring pages, that had changed since the last update, up to date
    upsite = "{0[domain]}{0[changes_src]}&from={0[last_update]}&days=30&limit=500".format(config)
    x = getPage(upsite)
    updater.feed(x)
    config["last_update"] = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    with open("config.json", "w") as file:
        file.write(dumps(config, indent=4))
