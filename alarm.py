import webbrowser, datetime, os, tkinter.filedialog
from time import sleep
from tkinter import *
from tkinter import messagebox
from threading import Thread

"""TODO LIST:
optimalize  
notifications
sort by other things than time (optionmenu      ) - page name (parse), file name
"""

class App:
    def __init__(self, master):  # creates the main UI - labels, entries, buttons and basic frame
        self.filename=""
        self.labels=[]
        self.list_of_alarms=[]
        self.Finished=False  # used to stop the code
        root.protocol("WM_DELETE_WINDOW", self.on_closing)  # in case cross is used to close it will ask if client wants to close
        self.frame = Frame(master)
        self.frame.pack()
        self.choose=StringVar(self.frame)
        self.choose.set("Time")
        self.chosen="Time"
        keywords=["Time","Link","File name"]
        for index, name in enumerate(keywords):
            Label(self.frame,text=name).grid(row=index,column=0)
        self.e1 = Entry(self.frame)
        self.e2 = Entry(self.frame)
        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        Button(self.frame, text="CHOOSE", command=self.askopenfile).grid(row=2, column=1)  # buttons targetting functions
        Button(self.frame, text="CLOSE", fg="red", command=self.on_closing).grid(row=5, column=0)
        Button(self.frame, text="START", fg="green", command=self.show_entry_fields).grid(row=5, column=1)
        Label(self.frame, text="Sort by").grid(row=7, column= 0)
        option=OptionMenu(self.frame, self.choose, "Time", "Link", "Name", command=self.options)
        option.grid(row=7, column=1)
        keywords=["Time","Link","Name"]
        for index, name in enumerate(keywords):
            Label(self.frame, text=name).grid(row=8, column=index)

    def options(self, value):
        self.chosen = self.choose.get()
        self.list()

    def askopenfile(self):  # entry of a file
        self.filename=tkinter.filedialog.askopenfilename()

    def show_entry_fields(self):
        first, second, third= self.e1.get(), self.e2.get(), self.filename  # when button "Start" is pressed, gets the values from entries and clears them
        self.filename = ""
        if first == "":
            pass
        elif first == '' and second == '' and third == "":
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
        self.labels=[]

    def list(self):  # makes new visual list of active alarms
        self.delete_labels()
        self.sort_alarms()
        for index, alarm in enumerate(self.list_of_alarms):
            current = []  # row
            for i, words in enumerate(self.list_of_alarms[index]):
                l=Label(self.frame, text=words)
                l.grid(row=9+index, column=i)
                current.append(l)
            button = Button(self.frame, text=X, fg="red", command=lambda variable=alarm:self.delete_alarm(variable))  # bind info of alarm to a button on the same line
            button.grid(row=9+index,column=5)
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
                        os.startfile(name)  # starts the file
                    else:
                        os.startfile(name)
                        webbrowser.open(url)
                    del self.list_of_alarms[index]
                    self.list()
            sleep(1)

    def get_time(self):  # gets current time and parses it to hh:mm format
        localtime = datetime.datetime.now()
        self.hoursmins = str(localtime)[11:16]

    def analyze(self, link, name):  # analyzes whether client wants to open link or file
        if link == "":
            return "file"
        elif name=="":
            return "link"
        else:
            return"both"

    def sort_alarms(self):  # sorts alarms according to time on base of bubblesort
        if self.chosen == "Time":
            for i in range(len(self.list_of_alarms)):
                bool_swapped=False  # kills the function if nothing changed
                for a in range(len(self.list_of_alarms)-i-1):
                    current_time=str(self.list_of_alarms[a][0])[0:2]+str(self.list_of_alarms[a][0])[3:5]  # parses time from list of alarms
                    next_time=str(self.list_of_alarms[a+1][0])[0:2]+str(self.list_of_alarms[a+1][0])[3:5]  # parses next time from list of alarms
                    if int(current_time)>int(next_time):
                        self.list_of_alarms[a],self.list_of_alarms[a+1]=self.list_of_alarms[a+1],self.list_of_alarms[a]  # switches them
                        bool_swapped=True
                if not bool_swapped:
                    break


if __name__ == "__main__":
    root = Tk()
    root.resizable(0, 0)
    root.iconbitmap(r"alarm.ico")
    app = App(root)  # initializes the class and its functions
    Thread(target=app.alarm).start()  # starts the main algorithm
    root.wm_title("Alarmclock")  # set title of the app
    mainloop()
    if app.Finished:  # when the UI is closed, the Thread is terminated
        Thread(target=app.alarm)._stop()