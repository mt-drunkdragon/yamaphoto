#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Updated for Yamareco 2024 renewal by drunkdragon 2024
# Backup photos and gpx files from yamareco by drunkdragon 2020
#
# Note: Logging-in to Yamareco is OAuth based, so it is not possible to login with
#  just POST method. However, currently Yamareco does not accept registration of 
#  applications with personal use.  What a shame...
#    https://sites.google.com/site/apiforyamareco/api/oauth
#  Maybe you can access protected contents using Selenium.
#
# The copyright holder of this work allows anyone to use it
# for any purpose including unrestricted redistribution,
# commercial use, and modification.

import os, sys, logging
import argparse
import requests
import re
from bs4 import BeautifulSoup
import tkinter
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog

TITLE = u"yamareco photo backup"
PROXIES = {}
GUI = False
logging.basicConfig(level=logging.DEBUG)


def dirButton_clicked():
    path = filedialog.askdirectory()
    dirVar.set(path)

def getPhotosGUI():
    getPhotos(urlEntry.get(), dirEntry.get(), localVar.get())
    root.destroy()

def getPhotos(url, dir, local):
    try:
        os.chdir(dir)

        r = requests.get(url, proxies=PROXIES)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        r.close()

        ### first, check if the article is accessed 
        owner_name = soup.find("div", class_="sidebar-right-owner-name")
        if owner_name is None:
            raise ValueError("The record cannot be get as it may be draft or private.")

        m = re.search(r"detail-(\d+).html", url)
        infofile = "info-" + m.group(1) + ".txt"
        photodir = "photo-" + m.group(1)
        indexfile = m.group()
        if local:
            os.makedirs(photodir, exist_ok=True)
        info = open(infofile, "w", encoding="utf-8")

        ### Retrieve various info
        owner_id = soup.find("div", class_="sidebar-right-owner-id")
        print("Owner: %s %s" % (owner_name.text, owner_id.text), file=info)
        
        title = soup.find("h2").text.strip()
        print("Title: %s" % title, file=info)
        date = soup.find("div", class_="date")
        date = re.sub(r"\s+", "", date.text.strip())
        print("Date: %s" % date, file=info)
        members = soup.find("div", class_="record-detail-content-member")
        for member in members.find_all("a", class_="item"):
            print("Member: %s" % member.text.strip(), file=info)
        for time_comment in soup.find_all("div", class_="record-detail-content-time-text"):
            print("Time Comment: %s" % time_comment.text.strip(), file=info)

        # parse items in a table
        th = soup.find("th", string="天候")
        climate = re.sub("</?(br|td)/?>", "\n", str(th.find_next("td"))).strip()
        print("Climate: %s" % climate, file=info)
        th = soup.find("th", string="アクセス")
        access = th.find_next("td")
        for i in access.select("div"):
            i.replace_with("")
        access = re.sub("</?(br|td)/?>", "\n", str(access)).strip()
        print("Access: %s" % access, file=info)
        th = th.find_next("th")
        condition = re.sub("</?(br|td)/?>", "\n", str(th.find_next("td"))).strip()
        print("Condition: %s" % condition, file=info)
        th = th.find_next("th", string="その他周辺情報")
        other = re.sub("</?(br|td)/?>", "\n", str(th.find_next("td"))).strip()
        print("Other: %s" % other, file=info)
        th = soup.find("th", string="個人装備")
        if th is not None:
            gears = []
            td = th.find_next("td")
            for gear in td.find_all("span"):
                gears.append(gear.text)
                print("Gear: %s" % gear.text, file=info)
        impressions = soup.find("div", class_="record-detail-content-impression-wrap")
        for impression_head in impressions.find_all("div", class_="impression-head"):
            author = impression_head.text.strip()
            impression = impression_head.find_next("p")
            print("Impression: [%s]\n%s" % (author, re.sub("</?(br|p)/?>", "\n", str(impression)).strip()), file=info)

        info.close()

        ### Retrieve photos and save them
        photo_section = soup.find("section", class_="photo-list")
        if photo_section is None:
            if GUI:
                messagebox.showerror(title=TITLE, message=u"写真データが取得できません")
            else:
                print("Error: no photo data", file=sys.stderr)
        else:
            photos = []
            i = 0
            for item in photo_section.find_all("div", class_="photo-list-wrap-item"):
                i += 1
                # get original photo
                d = item.find("span", class_="highslide-caption")
                photo = d.find("a", string=re.compile("元サイズ")).get("href")
                # get image
                if local:
                    r = requests.get(photo, proxies=PROXIES)
                    photo = photodir + "/" + "%03d.jpg" % i
                    with open(photo, "wb") as f:
                        f.write(r.content)
                    r.close()
                # get photo caption
                caption = item.find("div", class_="photo-list-wrap-item-caption")
                for br in caption.select("br"):
                    br.replace_with("\n")
                photos.append((photo, caption.text.strip()))

        ### Retrieving GPX tracking data
        gpxurl = re.sub("detail", "track", url)
        gpxurl = re.sub("html", "gpx", gpxurl)
        gpxfile = re.search(r"track-\d+.gpx", gpxurl).group()
        r = requests.get(gpxurl, proxies=PROXIES)
        if r is None:
            if GUI:
                messagebox.showerror(title=TITLE, message=u"軌跡データが取得できません")
            else:
                print("Error: no GPX data", file=sys.stderr)
        else:
            with open(gpxfile, mode="wb") as f:
                f.write(r.content)
                r.close()

        ### Create index file to browse photos
        with open(indexfile, "w", encoding="utf-8") as file:
            i = 0
            print("<html><head><title>%s</title></head><body>" % title, file=file)
            for photo in photos:
                i += 1
                print('<figure id="%03d"><img src="%s" width="100%%" alt="%s" title="%s" /><figcaption>%s</figcaption></figure>' % (i, photo[0], photo[0], photo[1], photo[1].replace('\n', '<br />')), file=file)
            print("</body></html>", file=file)


    except Exception as e:
        if GUI:
            messagebox.showerror(title=TITLE, message=str(e))
        else:
            print(str(e), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":

    p = argparse.ArgumentParser()
    p.add_argument("-u", "--url", help=u"ヤマレコ山行記録URL")
    p.add_argument("-d", "--dir", help=u"destination directory")
    p.add_argument("-l", "--local", action="store_true", help=u"save images locally")
    p.add_argument("-p", "--proxy", help=u"proxy server")
    args = p.parse_args()

    if args.proxy is None:
        proxy = os.getenv("HTTP_PROXY")
        if proxy is not None:
            PROXIES["http"] = proxy
        proxy = os.getenv("HTTPS_PROXY")
        if proxy is not None:
            PROXIES["https"] = proxy
        proxy = os.getenv("FTP_PROXY")
        if proxy is not None:
            PROXIES["ftp"] = proxy
    else:
        PROXIES["http"] = args.proxy
        PROXIES["https"] = args.proxy
        PROXIES["ftp"] = args.proxy

    if args.url is None or args.dir is None:
        GUI = True
        root = tkinter.Tk()
        urlVar = tkinter.StringVar()
        dirVar = tkinter.StringVar()
        localVar = tkinter.BooleanVar()
        if args.url is not None:
            urlVar.set(args.url)
        if args.dir is not None:
            dirVar.set(args.dir)
        if args.local is not None:
            localVar.set(args.local)
        root.title(TITLE)
        root.geometry("500x120")
        frame = ttk.Frame(root)
        frame.grid(column=0, row=0, sticky=tkinter.NSEW, padx=5, pady=10)

        urlLabel = ttk.Label(frame, text="URL")
        urlEntry = ttk.Entry(frame, textvariable=urlVar)
        localCheckbutton = ttk.Checkbutton(frame, text=u"save images locally", variable=localVar)
        dirLabel = ttk.Label(frame, text="DIR")
        dirEntry = ttk.Entry(frame, textvariable=dirVar)
        dirButton = ttk.Button(frame, text=">>", command=dirButton_clicked)
        execButton = ttk.Button(frame, text="Go", command=getPhotosGUI)

        urlLabel.grid(column=0, row=0, pady=5)
        urlEntry.grid(column=1, row=0, sticky=tkinter.EW, padx=5)
        localCheckbutton.grid(column=2, row=0, sticky=tkinter.W)
        dirLabel.grid(column=0, row=1, pady=5)
        dirEntry.grid(column=1, row=1, sticky=tkinter.EW, padx=5)
        dirButton.grid(column=2, row=1, sticky=tkinter.W)
        execButton.grid(column=1, row=2, pady=5)

        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        root.mainloop()
    else:
        getPhotos(args.url, args.dir, args.local)
