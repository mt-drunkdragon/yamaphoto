#!/usr/bin/env python
# -*- coding: utf-8 -*-
# backup photos and gpx files from yamareco by drunkdragon 2020
# The copyright holder of this work allows anyone to use it
# for any purpose including unrestricted redistribution,
# commercial use, and modification.

import os
import argparse
import requests
import re
from bs4 import BeautifulSoup
import tkinter
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog
TITLE = u"yamareco photo backup"

# プロキシーを通す場合は以下を設定
PROXIES = {
#    'http': 'http://proxy.yourdomain.com:8080',
#    'https': 'https://proxy.yourdomain.com:8080',
#    'ftp': 'ftp://proxy.yourdomain.com:8080'
}

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

        m = re.search('detail-(\d+).html', url)
        photodir = 'photo-' + m.group(1)
        indexfile = m.group()
        if local:
            os.makedirs(photodir, exist_ok=True)

        title = soup.find('title').text

        photo_area = soup.find('div', class_='photo_area')
        if photo_area is None:
            raise ValueError(u"写真データが取得できません\n認証が必要なのかもしれません(未サポート)")
        photos = []
        i = 0
        for item in photo_area.find_all('div', class_='item'):
            i += 1
            # get original photo
            d = item.find('span', class_='highslide-caption')
            d.find('div').decompose()
            d.find('span').decompose()
            photo = d.find_all('a')[1].get('href')
            # get image
            if local:
                r = requests.get(photo, proxies=PROXIES)
                photo = photodir + '/' + '%03d.jpg' % i
                with open(photo, "wb") as f:
                    f.write(r.content)
                r.close()
            # get photo caption
            c = item
            c.find('div').decompose()
            c.find('span').decompose()
            caption = c.text
            photos.append((photo, caption))

        with open(indexfile, 'w') as file:
            i = 0
            print("<html><head><title>%s</title></head><body>" % title, file=file)
            for photo in photos:
                i += 1
                print("<figure id=\"%03d\"><img src=\"%s\" width=\"100%%\" alt=\"%s\" title=\"%s\" /><figcaption>%s</figcaption></figure>" % (i, photo[0], photo[0], photo[1], photo[1]), file=file)
            print("</body></html>", file=file)

        gpxurl = re.sub('detail', 'track', url)
        gpxurl = re.sub('html', 'gpx', gpxurl)
        gpxfile = re.search('track-\d+.gpx', gpxurl).group()
        r = requests.get(gpxurl, proxies=PROXIES)
        with open(gpxfile, mode='wb') as f:
             f.write(r.content)
        r.close()

    except Exception as e:
        messagebox.showerror(title=TITLE, message=str(e))


if __name__ == "__main__":

    p = argparse.ArgumentParser()
    p.add_argument("-u", "--url", help=u"ヤマレコ山行記録URL")
    p.add_argument("-d", "--dir", help=u"destination directory")
    p.add_argument("-l", "--local", action='store_true', help=u"save images locally")
    args = p.parse_args()

    if args.url is None or args.dir is None:
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
