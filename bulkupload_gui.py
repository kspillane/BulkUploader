import sys, os, tkFileDialog, sets, tkMessageBox, hashlib
import Tkinter as tk
import cPickle as p
from ftplib import FTP, error_perm

class select_server_chkbx:

    def __init__(self, w, row, col, name, ip):
        global srvListUp
        global srvListAll
        self.var = tk.IntVar(value=1)
        self.name = name
        self.ip = ip
        srvListAll.add(self)
        srvListUp.add(self.ip)
        tk.Checkbutton(w, text=name, state="active", variable=self.var,
                command=self.toggled).grid(row=row, column=col, sticky='W', padx=5, pady=2)
        return

    def toggled(self):
        global srvListUp
    
        if not self.var.get():
            srvListUp.remove(self.ip)
        else:
            srvListUp.add(self.ip)
        return

class toggle_all_chkbx:

    def __init__(self, w):
        self.var = tk.IntVar(value=1)
        self.state = tk.StringVar(w,"Uncheck all")
        tk.Checkbutton(w, textvariable=self.state, state="active", variable=self.var,
                command=self.toggled).grid(row=5, column=2, columnspan=2, padx=5, pady=2, sticky='W')
        return
    
    def toggled(self):
        global srvListUp
        global srvListAll
    
        if not self.var.get():
            srvListUp.clear()
            for i in srvListAll:
                i.var.set(value=0)
            self.state.set("Check All")
        else:
            srvListUp = srvListAll.copy()
            for i in srvListAll:
                i.var.set(value=1)
            self.state.set("Uncheck All")
        return

def export_log_file():
    global loglist
    file = tkFileDialog.asksaveasfile(parent=w,mode='w+',title='Choose a file')
    if file != None:
        for line in loglist:
            file.write(loglist)
            file.write("\n")

        file.close()
        exportmsg = "Wrote "+str(len(loglist))+" to file "+str(file.name)
        tkMessageBox.showinfo(title="Log file saved", message=exportmsg)

    return

def clear_log():
    global loglist
    global listbox
    listbox.delete(0, tk.END)
    del loglist[:]

    return

def open_log():
    global w
    global loglist
    global listbox
    logwin = tk.Toplevel(w)
    logwin.title("Log viewer")
    tk.Grid.rowconfigure(logwin, 0, weight=0)
    exportBtn = tk.Button(logwin, text="Export to file", command=export_log_file)
    exportBtn.grid(row=0, column=0, padx=5, pady=2)
    clrBtn = tk.Button(logwin, text="Clear log", command=clear_log)
    clrBtn.grid(row=0, column=1, padx=5, pady=2)


    tk.Grid.rowconfigure(logwin, 1, weight=1)
    tk.Grid.columnconfigure(logwin, 0, weight=1)
    scrollbar = tk.Scrollbar(logwin)
    listbox = tk.Listbox(logwin, yscrollcommand=scrollbar.set, width=55)
    for i in loglist:
        listbox.insert(tk.END, str(i))
    scrollbar.config(command=listbox.yview)
    listbox.grid(rowspan=15, columnspan=5, row=1, column=0, pady=5, sticky='NESW')
    scrollbar.grid(rowspan=15, row=1, column=6, pady=5, sticky='WESN')

    return


def func_read_servers():
    global w
    
    file = tkFileDialog.askopenfile(parent=w,mode='rb',title='Choose a file')
    if file != None:
        data = file.readlines()
        file.close()
        srvlist = [line.rstrip('\n') for line in data]
        srvlist = [line.rstrip('\t') for line in srvlist]
        srvlist = [line.rstrip('\r') for line in srvlist]
        #name, ip = [line.split() for line in srvlist]
        import_srvs(srvlist)
    return 
        
def import_srvs(srvlist):
        global w
        global row
        
        tk.Label(w, text="Selected Servers to Upload to:").grid(row=5, column=0, columnspan=2, padx=5, pady=2, sticky='W')
        col=-1
        row = 6
        for servers in srvlist:
            try:
                name, ip = servers.split()
            except ValueError as e:
                tkMessageBox.showerror(title="Error importing server list",\
                    message="There was an error importing the server list from your file.\nFormat needs to be server_name server_ip\non seperate lines with a single whitespace")
                return 1
        
            if col == 3:
                col=0
                row+= 1
            else:
                col+= 1
            select_server_chkbx(w, row, col, name, ip)
        toggle_all_chkbx(w)
        save_srv_list(srvlist)
        return

def get_hash(l):
    h = hashlib.new('sha256')
    salt="One does not simply walk into Mordor"
    for i in l:
        h.update(i + salt)
    return h.hexdigest()

def save_srv_list(lst):
    try:
        fp = open('srvlst.dat', 'wb')
        hash = get_hash(lst)
        srvDct = {'servers': lst, 'hash': hash}
        p.dump(srvDct, fp)
        fp.close
    except:
        tkMessageBox.showwarning(title="Error saving server list", message="There was an error saving the server list.\nAre you running from a read-only directory?")
    return

def load_srv_lst():
    try:
        fp = open("srvlst.dat", "rb")
        srvDct = p.load(fp)
        srvlst = srvDct['servers']
        hash = get_hash(srvlst)
        if not hash == srvDct['hash']:
            tkMessageBox.showerror(message="The stored server list has become corrupted!\nPlease reimport the list of servers.")
            return
        fp.close
        import_srvs(srvlst)
    except:
        tkMessageBox.showerror(message="There was an error reading the stored server list\n\n\Please import a server list")
    return
    

def func_select_file():
    global w
    file = tkFileDialog.askopenfile(parent=w,mode='rb',title='Choose a file')
    global datFileName
    global uploadBtn
    datFileName = file.name
    print datFileName
    uploadBtn = tk.Button(w, text="Upload File", command=do_upload)
    uploadBtn.grid(row=4, column=3, sticky='W', padx=5, pady=2)
    datFileEnt = tk.Label(w, text=datFileName).grid(row=2, column=1, columnspan=3, sticky='W', padx=5, pady=2)

    return

def do_stop():
    global stop_loop
    stop_loop = 1
    return

def check_for_stop():
    global stop_loop

    if stop_loop == 1:
        stop_loop = 0
        return 1
    else:
        return 0

def do_upload():
    global datFileName
    global srvListUp
    global userEnt
    global passEnt
    global w
    global row
    global loglist
    global uploadBtn
    username = userEnt.get()
    password = passEnt.get()
    datfile = datFileName
    if len(username) < 1:
        tkMessageBox.showerror(message="You need to specify a username.")
        return
    if len(password) < 1:
        tkMessageBox.showerror(message="You need to specify a password.")
        return
    if len(datFileName) < 1:
        tkMessageBox.showerror(message="You need to input a file to send!")
        return
    if len(srvListUp) < 1:
        tkMessageBox.showerror(message="You need to import a server and select at least one server!")
    basepath, datfilename = os.path.split(datfile)
    count = 0
    row+=1
    percentDone = tk.StringVar(w, "Uploaded 0 of ")
    percentDoneLbl = tk.Label(w, textvariable=percentDone, font="Helvetica, 14")
    percentDoneLbl.grid(row=0, column=2, columnspan=3, rowspan=2)
    uploadBtn.grid_remove()
    stopBtn = tk.Button(w, text="   Stop   ", command=do_stop)
    stopBtn.grid(row=4, column=3, padx=5, pady=2, sticky='W')

    loglist.append("Selected file: "+str(datFileName))
    loglist.append("Uploading to "+str(len(srvListUp))+" servers.")
    for server in srvListUp:
        if check_for_stop() == 1:
            stopBtn.destroy()
            percentDone.set("Stopping...")
            loglist.append("Stop Button pressed! - Done")
            percentDoneLbl.destroy()
            uploadBtn.grid(row=4, column=3, sticky='W', padx=5, pady=2)
            return
        loglist.append("========== Starting new server connection ==========")
        loglist.append("Connecting to server "+server)
        try:
            ftp = FTP(server)
        except socket.error, e:
            storemsg = "There was an error connecting to server "+server
            loglist.append(storemsg)
            tkMessageBox.showwarning(message=storemsg)
            break
        else:
                try:
                    ftp.login(username, password)
                except:
                    tkMessageBox.showerror(message="There was a error logging into "+server+".\n Check the username and password")
                    loglist.append("There was an error logging into server "+server+".")
                else:
                    loglist.append("Connected. Sending file.")
                    try:
                        #Comment out the next two lines to enable dry-run mode. Connect only, no upload.
                        fp = open(datfile, "rb")
                        ftp.storbinary("STOR " + datfilename, fp)
                        ftp.quit()
                    except IOError as e:
                        storemsg = "There was an error storing the file on server "+server
                        loglist.append(storemsg)
                        tkMessageBox.showwarning(message=storemsg)
                    except errpr_perm:
                        storemsg = "There was an error storing the file on server "+server+".\nProbably a permissions error."
                        loglist.append(storemsg)
                        tkMessageBox.showwarning(message=storemsg)
                    else:
                        count += 1
                        loglist.append("File uploaded. Closing connection to "+server)
                        percentDone.set("Uploaded "+str(count)+" of "+str(len(srvListUp)))
                        w.update()
    stopBtn.destroy()
    percentDoneLbl.destroy()
    uploadBtn.grid(row=4, column=3, sticky='W', padx=5, pady=2)
    return
       
def build_gui():
    w = tk.Tk()
    w.title("Bulk FTP Uploader")
    defuser = tk.StringVar(w, '')
    defpass = tk.StringVar(w, '')
    userLbl = tk.Label(w, text="Username: ")
    passLbl = tk.Label(w, text="Password: ")
    global userEnt
    userEnt = tk.Entry(w, textvariable=defuser)
    global passEnt
    passEnt = tk.Entry(w, textvariable=defpass, show='*')
    srvfileBtn = tk.Button(w, text="Import Server List", command=func_read_servers)
    datfileBtn = tk.Button(w,text="Select Upload File", command=func_select_file)
    tk.Label(w, text="File to Upload:").grid(row=2, column=0, sticky='E', padx=5, pady=2
    )
    dspLogBtn = tk.Button(w, text="Display log", command=open_log)
      
    tk.Grid.rowconfigure(w, 0, weight=1)
    tk.Grid.columnconfigure(w, 0, weight=1)

    dspLogBtn.grid(row=4, column=2, padx=5, pady=2, sticky='W')
    userLbl.grid(row=0, column=0, sticky="E", padx=5, pady=2)
    userEnt.grid(row=0, column=1, sticky='W', columnspan=2, padx=5, pady=2)
    passLbl.grid(row=1, column=0, sticky='E', padx=5, pady=2)
    passEnt.grid(row=1, column=1, sticky='W', columnspan=2, padx=5, pady=2)
    srvfileBtn.grid(row=4, column=0, padx=5, pady=2)
    datfileBtn.grid(row=4, column=1, padx=5, pady=2)
    
    
    return w

loglist = []
stop_loop = 0
srvListUp = set()
srvListAll = set()
w = build_gui()
load_srv_lst()
w.mainloop()
