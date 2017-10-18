#!/usr/bin/env python
import webbrowser
import datetime
import tkinter.filedialog
import subprocess
import sys
import os
import requests
import json
from time import sleep
from tkinter import *
from tkinter import messagebox
from threading import Thread

"""TODO LIST:
optimalize  
notifications
sort by other things than time (optionmenu) - page name (parse), file name
"""


class App:
    def __init__(self, master):  # creates the main UI - labels, entries, buttons and basic frame
        self.filename = ""
        self.labels = []
        self.list_of_alarms = []
        self.Finished = False  # used to stop the code
        root.protocol("WM_DELETE_WINDOW", self.on_closing)  # in case cross is used to close it will ask if client wants to close
        self.frame = Frame(master)
        self.frame.pack()
        self.choose = StringVar(self.frame)
        self.choose.set("Time")
        self.chosen = "Time"
        self.hoursmins = None
        keywords = ["Time", "Link", "Filename"]
        for index, name in enumerate(keywords):
            Label(self.frame,text=name).grid(row=index,column=0)
        self.e1 = Entry(self.frame)
        self.e2 = Entry(self.frame)
        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        Button(self.frame, text="CHOOSE", command=self.askopenfile).grid(row=2, column=1)  # buttons targetting functions
        Button(self.frame, text="CLOSE", fg="#FF4949", command=self.on_closing).grid(row=5, column=0)
        Button(self.frame, text="START", fg="#13CE66", command=self.show_entry_fields).grid(row=5, column=1)
        Label(self.frame, text="Sort by").grid(row=7, column=0)
        option = OptionMenu(self.frame, self.choose, "Time", "Link", "Filename", command=self.options)
        option.grid(row=7, column=1)
        keywords = ["Time", "Link", "Filename"]
        for index, name in enumerate(keywords):
            Label(self.frame, text=name).grid(row=8, column=index)

    def options(self):
        self.chosen = self.choose.get()
        self.list()

    def askopenfile(self):  # entry of a file
        self.filename = tkinter.filedialog.askopenfilename()

    def show_entry_fields(self):
        first, second, third = self.e1.get(), self.e2.get(), self.filename  # when button "Start" is pressed, gets the values from entries and clears them
        self.filename = ""
        if first == "":
            pass
        elif int(first[3:5]) >= 60:  # checks if time is in an OK format
            pass
        elif int(first[0:2]) >= 24:
            pass
        elif second == '' and third == "":
            pass
        else:
            self.list_of_alarms.append([first, second, third])
            self.e1.delete(0, END)
            self.e2.delete(0, END)
            self.list()

    def delete_labels(self):  # deletes all labels showing alarms
        for index, label in enumerate(self.labels):  # deletes rows
            for i in range(len(self.labels[index])):  # deletes individual labels
                self.labels[index][i].destroy()
        self.labels = []

    @staticmethod
    def find_equals_index(phrase):  # finds index of sign "="
        for index, letter in enumerate(phrase):
            if letter == "=":
                return index

    def list(self):  # makes new visual list of active alarms
        self.delete_labels()
        self.sort_alarms()
        for index, alarm in enumerate(self.list_of_alarms):
            current = []  # row
            for i, words in enumerate(self.list_of_alarms[index]):
                if i == 1 and "youtube.com/watch?v" in words:
                    _id = words[self.find_equals_index(words)+1:len(words)]  # gets video ID tag
                    url = "https://www.googleapis.com/youtube/v3/videos?part=snippet&id={id}&key={api_key}" # using google API to get video title
                    r = requests.get(url.format(id=_id, api_key="AIzaSyBqYx6Qoose6vt-7e8evYXOT4ztJOxMXws"))
                    js = r.json()
                    items = js["items"][0]
                    title = items["snippet"]["title"]
                    author = items["snippet"]["channelTitle"]
                    text_to_show = "{author}: {title}".format(author=author, title=title)
                    l = Label(self.frame, text=text_to_show)
                elif i == 2 and words != "":
                    for j in range(len(words)):
                        if words[len(words) - 1 - j] == "/":
                            slash_index = j
                            break
                    l = Label(self.frame, text=words[-slash_index:])
                else:
                    l = Label(self.frame, text=words)
                l.grid(row=9+index, column=i)
                current.append(l)
            button = Button(self.frame, text=X, fg="red", command=lambda variable=alarm: self.delete_alarm(variable))  # bind info of alarm to a button on the same line
            button.grid(row=9+index, column=5)
            current.append(button)
            self.labels.append(current)  # creates list of labels

    def delete_alarm(self, alarm):
        self.list_of_alarms.remove(alarm)
        self.list()

    def on_closing(self):
        if messagebox.askokcancel("Closing", "Do you really want to quit?"):
            root.destroy()
            self.Finished = True

    def alarm(self):  # the main algorithm
        while not self.Finished:
            for index, alarm in enumerate(self.list_of_alarms):
                target_time, url, name = alarm[0], alarm[1], alarm[2]
                self.get_time()
                analyzed = self.analyze(url, name)
                if self.hoursmins == target_time:
                    if analyzed == "link":
                        webbrowser.open(url)
                    elif analyzed == "file":
                        if os.name == "nt":  # Windows use a different function to start a file
                            os.startfile(name)
                        else:
                            opener = "open" if sys.platform == "darwin" else "xdg-open"
                            subprocess.call([opener, name])  # starts the file on Linux
                    else:
                        if os.name == "nt":
                            os.startfile(name)
                        else:
                            opener = "open" if sys.platform == "darwin" else "xdg-open"
                            subprocess.call([opener, name])
                        webbrowser.open(url)
                    del self.list_of_alarms[index]
                    self.list()
            sleep(1)

    def get_time(self):  # gets current time and parses it to hh:mm format
        localtime = datetime.datetime.now()
        self.hoursmins = str(localtime)[11:16]

    @staticmethod
    def analyze(link, name):  # analyzes whether client wants to open link or file
        if link == "":
            return "file"
        elif name == "":
            return "link"
        else:
            return "both"

    def sort_alarms(self):  # sorts alarms according to time on base of bubblesort
        if self.chosen == "Time":
            for i in range(len(self.list_of_alarms)):
                bool_swapped = False  # kills the function if nothing changed
                for a in range(len(self.list_of_alarms)-i-1):
                    current_time = str(self.list_of_alarms[a][0])[0:2]+str(self.list_of_alarms[a][0])[3:5]  # parses time from list of alarms
                    next_time = str(self.list_of_alarms[a+1][0])[0:2]+str(self.list_of_alarms[a+1][0])[3:5]  # parses next time from list of alarms
                    if int(current_time) > int(next_time):
                        self.list_of_alarms[a], self.list_of_alarms[a+1] = self.list_of_alarms[a+1], self.list_of_alarms[a]  # switches them
                        bool_swapped = True
                if not bool_swapped:
                    break
        elif self.chosen == "Link":
            pass
        elif self.chosen == "Filename":
            pass


if __name__ == "__main__":
    root = Tk()
    root.resizable(0, 0)
    if os.name == "nt":
        root.iconbitmap(r"data/alarm.ico")
    else:
        img = PhotoImage(file='data/alarm.gif')
        root.tk.call('wm', 'iconphoto', root._w, img)
    app = App(root)  # initializes the class and its functions
    Thread(target=app.alarm).start()  # starts the main algorithm
    root.wm_title("Alarmclock")  # set title of the app
    mainloop()
    if app.Finished:  # when the UI is closed, the Thread is terminated
        Thread(target=app.alarm)._stop()