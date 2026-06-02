
import wx
import socket
import threading
import datetime
from  tcp_by_size import send_with_size ,recv_by_size
from sys import argv
import pygame

APP_SIZE_X = 700
APP_SIZE_Y = 700


class WxChatClient(wx.Dialog):

    def __init__(self, parent, id, title, ip):
        wx.Dialog.__init__(self, parent, id, title, size=(APP_SIZE_X, APP_SIZE_Y))
        self.Bind(wx.EVT_CLOSE, self.onExit)
        self.ip = ip
        self.state = "start"
        self.all_users = []
        self.to_user = ""
        self.username = ""

        self.eye_open = wx.Bitmap('opened.png')
        self.eye_closed = wx.Bitmap('close.png')

        self.BtnClos = wx.Button(self, 2, 'Close connection', (50, 130))
        self.BtmLogin = wx.Button(self, 3, 'Login', (150, 100), (110, -1))
        self.BtnSend = wx.Button(self, 4, 'TcpSend', (150, 130), (110, -1))
        self.showpass = wx.BitmapButton(self,bitmap=self.eye_closed,pos=(275,45))


        self.editname = wx.TextCtrl(self, value=" ! ", pos=(120, 60), size=(140,-1))
        self.data_to_server = wx.TextCtrl(self, value="", pos=(120, 20), size=(140,-1))

        self.data_from_server = wx.ListBox(self, pos=(20,220),  size=(340,200) ,style = wx.LB_SINGLE)
        self.display_users = wx.ListBox(self, pos=(10,10),  size=(60,200) ,style = wx.LB_SINGLE)
        self.show_users()

        self.msg = wx.ListBox(self, pos=(20,430),  size=(240,240) ,style = wx.LB_SINGLE)



        self.BtnSend.Hide()
        self.BtnClos.Hide()
        self.editname.Hide()

        self.EnterUsername = wx.TextCtrl(self, value="", pos=(320, 20), size=(140,-1))
        self.EnterPassword = wx.TextCtrl(self, value="", pos=(320, 50), size=(140,-1),style=wx.TE_PASSWORD)
        self.EnterPasswordShow = wx.TextCtrl(self, value="", pos=(320, 50), size=(140,-1))

        self.EnterPasswordShow.Hide()


        font = wx.Font(12,wx.FONTFAMILY_ROMAN,wx.FONTSTYLE_ITALIC,wx.FONTWEIGHT_BOLD)
        self.EnterUsername.SetFont(font)
        self.EnterUsername.SetForegroundColour(wx.Colour(255,0,0))
        self.EnterUsername.SetBackgroundColour(wx.Colour(0, 0, 255))


        self.data_to_server.Hide()



        self.Bind(wx.EVT_LISTBOX, self.find_user, self.display_users)



        self.listener = None

        self.Bind(wx.EVT_BUTTON, self.CloseConnection, id=2)
        self.Bind(wx.EVT_BUTTON, self.OnTcpConnect, id=3)
        self.Bind(wx.EVT_BUTTON, self.OnTcpSend, id=4)
        #self.Bind(wx.EVT_BUTTON,self.show_pass,id=5)

        self.showpass.Bind(wx.EVT_BUTTON, self.show_pass)


        self.Centre()
        self.ShowModal()
        # self.Destroy()

    def show_pass(self, event):
        if self.EnterPassword.IsShown():
            current_value = self.EnterPassword.GetValue()
            self.EnterPassword.Hide()
            self.EnterPasswordShow.Show()
            self.EnterPasswordShow.SetValue(current_value)
            self.showpass.SetBitmap(self.eye_open)
        else:
            current_value = self.EnterPasswordShow.GetValue()
            self.EnterPasswordShow.Hide()
            self.EnterPassword.Show()
            self.EnterPassword.SetValue(current_value)
            self.showpass.SetBitmap(self.eye_closed)

        self.EnterPassword.Refresh()




    def show_users(self):
        #self.display_users.Clear()
        for n in self.all_users:
            self.display_users.Append(n)

    def find_user(self, evt):
        self.to_user = self.display_users.GetString(self.display_users.GetSelection())

        print ("Got user to send to " + self.to_user)

    def show_hide_after_login(self):
        self.BtnSend.Show()
        self.BtnClos.Show()
        self.editname.Show()
        self.data_to_server.Show()

        self.EnterUsername.Hide()
        self.EnterPassword.Hide()
        self.BtmLogin.Hide()





    def onExit(self, event):
        print ("Bye 2")

        self.Destroy()

    def CloseConnection(self,event):
        self.client_sock.close()
        #self.listener.join()
        self.msg.Append("Connection Closed")




    def OnTcpConnect(self, event):
        if  self.EnterUsername.Value == "" or self.EnterPassword.Value == "":
            self.msg.Append("Please enter username and password")
            return
        try:
            self.client_sock = socket.socket()
            self.client_sock.connect((self.ip, 33445))
            self.listener = threading.Thread(target=self.listen)
            send_with_size(self.client_sock,"LOGIN_|"+ self.EnterUsername.Value +"|" + self.EnterPassword.Value)
            self.state = "login_sent"
            self.listener.start()
        except Exception as err:
            self.msg.Append("Error while try to connect msg=" + str(err.message))

    def listen(self):
        while True:
            try:
                self.client_sock.settimeout(1)
                data = recv_by_size( self.client_sock)
                if data != "":
                    self.data_from_server.Append(str(datetime.datetime.now())[:19] + " | " + data)
                else:
                    self.msg.Append("No Connection")
                    break
                action = data[:6]
                data = data[7:]
                fields = data.split('|')

                if action == "LOGINR":
                    if fields[0] == "Ok":
                        self.state = "user_connected"
                        self.username = self.EnterUsername.Value
                        self.show_hide_after_login()
                        if len(fields) > 1:
                            self.all_users = []
                            for i in xrange(1,len(fields)):
                                self.all_users.append(fields[i])
                        self.show_users()
                        self.SetTitle(self.username + " Connected ")
                    else:
                        self.msg.Append("Error Wrong user or password. Try again")

                elif action =="MESSAG":
                    self.data_from_server.Append(fields[0])
                else:
                    self.msg.Append("Got unknown msg")

            except socket.error as e:
                if e.errno == 10035 or str(e) == "timed out":
                    continue
                self.msg.Append("Listner exit sock exception")
                break
            except:
                self.msg.Append("Listner exit")
                break

    def OnTcpSend(self, event):
        if self.to_user !="":
            to_send = "PRIVAT|"+self.to_user  + "|" + self.data_to_server.Value
            self.to_user = ""
        else:
            to_send = "PUBLIC|" + self.data_to_server.Value


        try:
            send_with_size(self.client_sock,to_send)
        except:
            self.msg.Append("Try Connect")
        self.data_to_server.Value = ""

def main():

    if len(argv) < 2:
        print ("Command line: Missing  IP ")
        exit()
    else:
        ip = argv[1]

    app = wx.App(0)
    WxChatClient(None, -1, 'WX Chat Client',ip)
    app.MainLoop()

if __name__ == '__main__':

    main()