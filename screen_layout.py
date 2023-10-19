#! /usr/bin/env python3.11

# screen framework came from:
#  https://stackoverflow.com/questions/62484655/how-to-update-refresh-widgets-when-switching-frames-in-tkinter
# could be useful for threading so screen updates dont freeze
#  https://github.com/pratikguru/Instructables/blob/master/uart_visualizer.py

from tkinter import *
from tkinter import font as tkFont  # for convenience

class screen(Frame):
    def __init__(self,master,name):
        Frame.__init__(self,master)
        self.master=master
        self.name=name
        # Initalise with master
        self.master.addScreen(self)

    # the one line function that could be replaced by one line
    def show(self):
        self.master.showScreen(self.name)

    def screen1_layout(s):
        Label(s,text="This is screen 1").grid(row=0,column=0) 
        s.config()

    def screen2_layout(s):
        Label(s,text="This is screen 2").grid(row=0,column=0) 
        s.config()

    def screen4_layout(s):
        Label(s,text="This is screen 4").grid(row=0,column=0) 
        s.config()

class keyboard(Frame):
    def __init__(self,parent,screen):
        Frame.__init__(self,parent)
        self.font = tkFont.Font(family='Helvetica', size=14)
        self.screen = screen
        self.exp = ''

        self.entry_str = StringVar()
        self.enty_bar = Entry(self.screen, state='readonly', textvariable=self.entry_str)
        self.enty_bar.grid(rowspan=1, columnspan=80)

        self.keylist = [
            {'lc':'`',   'uc':'~',   'row':1, 'col':0, 'span':1},
            {'lc':'1',   'uc':'!',   'row':1, 'col':1, 'span':1},
            {'lc':'2',   'uc':'@',   'row':1, 'col':2, 'span':1},
            {'lc':'3',   'uc':'#',   'row':1, 'col':3, 'span':1},
            {'lc':'4',   'uc':'$',   'row':1, 'col':4, 'span':1},
            {'lc':'5',   'uc':'%',   'row':1, 'col':5, 'span':1},
            {'lc':'6',   'uc':'^',   'row':1, 'col':6, 'span':1},
            {'lc':'7',   'uc':'&',   'row':1, 'col':7, 'span':1},
            {'lc':'8',   'uc':'*',   'row':1, 'col':8, 'span':1},
            {'lc':'9',   'uc':'(',   'row':1, 'col':9, 'span':1},
            {'lc':'0',   'uc':')',   'row':1, 'col':10, 'span':1},
            {'lc':'-',   'uc':'_',   'row':1, 'col':11, 'span':1},
            {'lc':'=',   'uc':'+',   'row':1, 'col':12, 'span':1},
            {'lc':'⌫',  'uc':'⌫',   'row':1, 'col':13, 'span':1},
            {'lc':'Tab', 'uc':'Tab', 'row':2, 'col':0, 'span':2},
            {'lc':'q',   'uc':'Q',   'row':2, 'col':2, 'span':1},
            {'lc':'w',   'uc':'W',   'row':2, 'col':3, 'span':1},
            {'lc':'e',   'uc':'E',   'row':2, 'col':4, 'span':1},
            {'lc':'r',   'uc':'R',   'row':2, 'col':5, 'span':1},
            {'lc':'t',   'uc':'T',   'row':2, 'col':6, 'span':1},
            {'lc':'y',   'uc':'Y',   'row':2, 'col':7, 'span':1},
            {'lc':'u',   'uc':'U',   'row':2, 'col':8, 'span':1},
            {'lc':'i',   'uc':'I',   'row':2, 'col':9, 'span':1},
            {'lc':'o',   'uc':'O',   'row':2, 'col':10, 'span':1},
            {'lc':'p',   'uc':'P',   'row':2, 'col':11, 'span':1},
            {'lc':'[',   'uc':'{',   'row':2, 'col':12, 'span':1},
            {'lc':']',   'uc':'}',   'row':2, 'col':13, 'span':1},
            {'lc':'a',   'uc':'A',   'row':3, 'col':0, 'span':1},
            {'lc':'s',   'uc':'S',   'row':3, 'col':1, 'span':1},
            {'lc':'d',   'uc':'D',   'row':3, 'col':2, 'span':1},
            {'lc':'f',   'uc':'F',   'row':3, 'col':3, 'span':1},
            {'lc':'g',   'uc':'G',   'row':3, 'col':4, 'span':1},
            {'lc':'h',   'uc':'H',   'row':3, 'col':5, 'span':1},
            {'lc':'j',   'uc':'J',   'row':3, 'col':6, 'span':1},
            {'lc':'k',   'uc':'K',   'row':3, 'col':7, 'span':1},
            {'lc':'l',   'uc':'L',   'row':3, 'col':8, 'span':1},
            {'lc':';',   'uc':':',   'row':3, 'col':9, 'span':1},
            {'lc':"'",   'uc':'"',   'row':3, 'col':10, 'span':1},
            {'lc':'\\',  'uc':'|',   'row':3, 'col':11, 'span':1},
            {'lc':'⏎', 'uc':'⏎', 'row':3, 'col':12, 'span':2},
            {'lc':'⇧',  'uc':'⇧',  'row':4, 'col':0, 'span':2},
            {'lc':'z',   'uc':'Z',   'row':4, 'col':2, 'span':1},
            {'lc':'x',   'uc':'X',   'row':4, 'col':3, 'span':1},
            {'lc':'c',   'uc':'C',   'row':4, 'col':4, 'span':1},
            {'lc':'v',   'uc':'V',   'row':4, 'col':5, 'span':1},
            {'lc':'b',   'uc':'B',   'row':4, 'col':6, 'span':1},
            {'lc':'n',   'uc':'N',   'row':4, 'col':7, 'span':1},
            {'lc':'m',   'uc':'M',   'row':4, 'col':8, 'span':1},
            {'lc':',',   'uc':'<',   'row':4, 'col':9, 'span':1},
            {'lc':'.',   'uc':'>',   'row':4, 'col':10, 'span':1},
            {'lc':'/',   'uc':'?',   'row':4, 'col':11, 'span':1},
            {'lc':'Clr', 'uc':'Clr', 'row':4, 'col':12, 'span':2},
            {'lc':'get', 'uc':'get', 'row':5, 'col':1, 'span':2},
            {'lc':'SPC', 'uc':'SPC', 'row':5, 'col':4, 'span':5},
            {'lc':'set', 'uc':'set', 'row':5, 'col':10, 'span':2}
        ]
        self.isShift = True
        self.keyboard_layout()
        self.isShift = False
        self.keyboard_layout()

    def keyboard_layout(self):
        char = 'lc'
        if self.isShift:
            char = 'uc'

        # Label(self.screen,text="keyboard").grid(row=0,column=0) 
        for row in self.keylist:
            btn = Label(self.screen, font = self.font, text=row[char], padx = 4, borderwidth=1, relief="solid")
            btn.grid(column=row['col'], row=row['row'], columnspan = row['span'], sticky="news", padx = 2, pady = 2)
            if row[char] == '⇧':
                btn.bind("<Button-1>", lambda event, btn=btn: self.shift())
            elif row[char] == 'Clr':
                btn.bind("<Button-1>", lambda event, btn=btn: self.clear())
            elif row[char] == '⏎':
                btn.bind("<Button-1>", lambda event, btn=btn: self.enter())
            elif row[char] == '⌫':
                btn.bind("<Button-1>", lambda event, btn=btn: self.backspace())
            elif row[char] == 'SPC':
                btn.bind("<Button-1>", lambda event, btn=btn: self.add_space())
            elif row[char] == 'set':
                btn.bind("<Button-1>", lambda event, btn=btn: self.add_set(btn))
            elif row[char] == 'get':
                btn.bind("<Button-1>", lambda event, btn=btn: self.add_get(btn))
            else:
                btn.bind("<Button-1>", lambda event, btn=btn: self.press(btn))

        self.screen.config()

    def enter(self):
        self.exp = " "
        self.entry_str.set(self.exp)

    def add_space(self):
        self.exp = self.exp + str(' ')

    def add_get(self, item):
        self.exp = self.exp + str('get ')
        self.entry_str.set(self.exp)

    def add_set(self, item):
        self.exp = self.exp + str('set ')
        self.entry_str.set(self.exp)

    def press(self, item):
        self.exp = self.exp + str(item["text"])
        self.entry_str.set(self.exp)

    def backspace(self):
        self.exp = self.exp[:-1]
        self.entry_str.set(self.exp)

    def shift(self):
        self.isShift = not self.isShift
        self.keyboard_layout()

    def clear(self):
        self.exp = " "
        self.entry_str.set(self.exp)


# manage screens
class screenController(Frame):
    def __init__(self,parent):
        Frame.__init__(self,parent)
        #Configure
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        #Attributes
        self.allScreens={}
        self.currentScreen=None

    def addScreen(self,screenObject):
        #Place the screen
        screenObject.grid(row=0, column=0, sticky="nsew")
        #Add to dictionary
        self.allScreens[screenObject.name]=screenObject

    def showScreen(self,screenName):
        if screenName in self.allScreens:
            self.allScreens[screenName].tkraise() # display
            self.currentScreen=screenName # update variable
            

if __name__ == "__main__":
    #Create a Tkinter Window
    
    gui=Tk()
    gui.title("MESC display")
    gui.geometry("400x300")
    gui.columnconfigure(0,weight=1)
    gui.rowconfigure(1,weight=1)

    screenMaster=screenController(gui)
    screenMaster.grid(row=1,column=0,sticky="NSEW")
    
    # Create screens
    screen1 = screen(screenMaster, "S1")
    screen.screen1_layout(screen1)

    screen2 = screen(screenMaster, "S2")
    screen.screen2_layout(screen2)

    screen3 = screen(screenMaster, "S3")
    keyboard = keyboard(gui, screen3)
    keyboard.keyboard_layout()

    screen4 = screen(screenMaster, "S4")
    screen.screen4_layout(screen4)

    # put a navbar on the top
    navBar=Frame(gui)
    navBar.grid(row=0,column=0,sticky="EW")
    navBar.config(bg="#F1F0F2")
    
    keyboard = PhotoImage(file='icons/keyboard.png')
    connect = PhotoImage(file='icons/connect.png')
    settings = PhotoImage(file='icons/settings.png')
    data = PhotoImage(file='icons/view_data.png')

    b1=Button(navBar, image = connect, command=lambda: screen1.show())
    b1.grid(row=0,column=0)
    
    b2=Button(navBar, image = data,command=lambda: screen2.show())
    b2.grid(row=0,column=1)
    
    b3=Button(navBar, image = keyboard, command=lambda: screen3.show())
    b3.grid(row=0,column=3)
    
    b4=Button(navBar, image = settings,command=lambda: screen4.show())
    b4.grid(row=0,column=4)
    
    # let's start with screen1
    screen1.show()
    
    gui.mainloop()
