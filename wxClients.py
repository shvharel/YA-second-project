import secrets
from random import randbytes
from tarfile import DIRTYPE

import wx
import socket
import threading
import datetime

from pygame.examples.cursors import bitmap_cursor1

from RSA import RSA_CLASS
from TCP_AES import send_with_AES, recv_with_AES
from  tcp_by_size import send_with_size ,recv_by_size
from sys import argv
import pygame
import secrets
import hashlib
from PIL import Image

APP_SIZE_X = 1400
APP_SIZE_Y = 700


class WxChatClient(wx.Dialog):

    def __init__(self, parent, id, title, ip):
        wx.Dialog.__init__(self, parent, id, title, size=(APP_SIZE_X, APP_SIZE_Y))
        self.Bind(wx.EVT_CLOSE, self.CloseConnection)
        self.ip = ip
        self.state = "start"
        self.all_users = ['PUBLIC']
        self.to_user = ""
        self.username = ""
        self.SetBackgroundColour(wx.Colour(255,255,255))
        self.DiffieHellmankey = ''
        self.KeyRSA = ''
        self.IV = 'hefuhrgjhsdfirps'
        self.mode = ''
        self.GeneratedDH = False
        self.GeneratedRSA = False

        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load('Sneaky Snitch (Kevin MacLeod) - Gaming Background Music (HD).mp3')
        pygame.mixer.music.play(-1)


        self.eye_open = wx.Bitmap('opened.png')
        self.eye_closed = wx.Bitmap('close.png')
        self.StartingPicture = wx.Bitmap('Hybrid.png')
        self.Login = wx.Bitmap('Login.png')
        self.Signup = wx.Bitmap('Signup.png')
        self.sound_on = wx.Bitmap('SoundOn.png')
        self.Sound_off = wx.Bitmap('SoundOff.png')
        self.Send = wx.Bitmap('Send.png')
        self.rsa = wx.Bitmap('RSA.png')
        self.diffhell = wx.Bitmap('DH.png')

        self.BtnClos = wx.Button(self, 2, 'Close connection', (530, 300))
        self.BtmLogin1 = wx.BitmapButton(self, bitmap=self.Login, pos=(433, 345))
        self.BtmLogin2 = wx.BitmapButton(self, bitmap=self.Login, pos=(570, 355))
        self.BtmSignup1 = wx.BitmapButton(self, bitmap=self.Signup,pos=(713, 345))
        self.BtmSignup2 = wx.BitmapButton(self, bitmap=self.Signup, pos=(570, 355))
        self.BtnSend = wx.BitmapButton(self, bitmap=self.Send, pos=(530,355))
        self.rsa = wx.BitmapButton(self, bitmap=self.rsa,pos=(120,570))
        self.dh = wx.BitmapButton(self, bitmap=self.diffhell, pos=(1000,570))
        self.showpass = wx.BitmapButton(self,bitmap=self.eye_closed,pos=(535,297))
        self.showsound = wx.BitmapButton(self,bitmap=self.sound_on,pos=(15,15),style=wx.NO_BORDER)


        self.editname = wx.TextCtrl(self, value="Currently sending a public message", pos=(120, 60), size=(200,-1))
        self.data_to_server = wx.TextCtrl(self, value="", pos=(530, 328), size=(225,-1))


        self.data_from_server = wx.ListBox(self, pos=(7,250),  size=(520,310) ,style = wx.LB_SINGLE)
        self.display_users = wx.ListBox(self, pos=(760,250),  size=(60,200) ,style = wx.LB_SINGLE)
        self.show_users()

        self.msg = wx.ListBox(self, pos=(825,250),  size=(540,310) ,style = wx.LB_SINGLE)

        self.StartingPictureShow = wx.StaticBitmap(self, -1, self.StartingPicture,pos=(462,140))

        self.EnterUsername = wx.TextCtrl(self, value="", pos=(574, 230), size=(220,50))
        self.EnterPassword = wx.TextCtrl(self, value="", pos=(574, 290), size=(220,50),style=wx.TE_PASSWORD)
        self.EnterPasswordShow = wx.TextCtrl(self, value="", pos=(574, 290), size=(220,50))

        self.EnterPasswordShow.Hide()


        font = wx.Font(24,wx.FONTFAMILY_ROMAN,wx.FONTSTYLE_ITALIC,wx.FONTWEIGHT_BOLD)
        password_font = wx.Font(24,wx.FONTFAMILY_DEFAULT, wx.TE_CENTER, wx.FONTWEIGHT_BOLD)
        self.EnterUsername.SetFont(font)
        self.EnterUsername.SetForegroundColour(wx.Colour(0,0,0))
        self.EnterUsername.SetBackgroundColour(wx.Colour(135, 206, 235))
        self.EnterPasswordShow.SetFont(password_font)
        self.EnterPassword.SetFont(password_font)


        self.data_to_server.Hide()
        self.msg.Hide()
        self.BtnSend.Hide()
        self.BtnClos.Hide()
        self.editname.Hide()
        self.display_users.Hide()
        self.data_from_server.Hide()
        self.showpass.Hide()
        self.EnterPassword.Hide()
        self.EnterUsername.Hide()
        self.BtmLogin2.Hide()
        self.BtmSignup2.Hide()
        self.rsa.Hide()
        self.dh.Hide()


        self.Sound_Enabled = True
        self.is_closed = True

        self.Bind(wx.EVT_LISTBOX, self.find_user, self.display_users)


        self.listener = None

        self.Bind(wx.EVT_BUTTON, self.CloseConnection, id=2)
        self.Bind(wx.EVT_BUTTON, self.OnTcpConnect, id=3)
        self.Bind(wx.EVT_BUTTON, self.OnTcpSend, id=4)



        self.showpass.Bind(wx.EVT_BUTTON, self.show_pass)

        self.showsound.Bind(wx.EVT_BUTTON,self.sound)

        self.BtmLogin1.Bind(wx.EVT_BUTTON, self.Login_page)
        self.BtmLogin2.Bind(wx.EVT_BUTTON,self.rsa_or_dh_login)
        self.BtmSignup1.Bind(wx.EVT_BUTTON,self.Signup_page)
        self.BtmSignup2.Bind(wx.EVT_BUTTON, self.rsa_or_dh_signup)
        self.BtnSend.Bind(wx.EVT_BUTTON, self.OnTcpSend)
        self.dh.Bind(wx.EVT_BUTTON, self.ChangeToDH)
        self.rsa.Bind(wx.EVT_BUTTON, self.ChangeToRSA)
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
            self.is_closed = False
        else:
            current_value = self.EnterPasswordShow.GetValue()
            self.EnterPasswordShow.Hide()
            self.EnterPassword.Show()
            self.EnterPassword.SetValue(current_value)
            self.showpass.SetBitmap(self.eye_closed)
            self.is_closed = True

    def sound(self,event):
        if self.Sound_Enabled:
            self.showsound.SetBitmap(self.Sound_off)
            self.Sound_Enabled = False
            pygame.mixer.music.stop()
        else:
            self.showsound.SetBitmap(self.sound_on)
            self.Sound_Enabled = True
            pygame.mixer.music.load('Sneaky Snitch (Kevin MacLeod) - Gaming Background Music (HD).mp3')
            pygame.mixer.music.play(-1)

        self.showsound.Refresh()

    def rsa_or_dh_signup(self, event):
        if not self.mode:
            self.msg.Append('You need to pick a method of key exchange first')
            return
        self.OnTcpConnectSignup()

    def rsa_or_dh_login(self, event):
        if not self.mode:
            self.msg.Append('You need to pick a method of key exchange first')
            return
        self.OnTcpConnect()

    def Login_page(self, event):
        self.StartingPictureShow.SetPosition(wx.Point(462,25))
        self.BtmLogin1.Hide()
        self.BtmSignup1.SetPosition(wx.Point(570, 450))
        self.BtmSignup1.Show()
        self.BtmLogin2.Show()
        self.BtmSignup2.Hide()
        self.EnterUsername.Show()
        self.EnterPassword.Show()
        self.EnterUsername.SetValue('')
        self.EnterPassword.SetValue('')
        self.EnterPasswordShow.SetValue('')
        self.showpass.SetBitmap(self.eye_closed)
        self.showpass.Show()
        self.msg.Show()
        self.data_from_server.Show()
        self.rsa.Show()
        self.dh.Show()

    def Signup_page(self,event):
        self.StartingPictureShow.SetPosition(wx.Point(462,25))
        self.BtmSignup1.Hide()
        self.BtmLogin1.SetPosition(wx.Point(570, 450))
        self.BtmLogin1.Show()
        self.BtmSignup2.Show()
        self.BtmLogin2.Hide()
        self.EnterUsername.Show()
        self.EnterPassword.Show()
        self.EnterUsername.SetValue('')
        self.EnterPassword.SetValue('')
        self.EnterPasswordShow.SetValue('')
        self.showpass.SetBitmap(self.eye_closed)
        self.showpass.Show()
        self.msg.Show()
        self.data_from_server.Show()
        self.rsa.Show()
        self.dh.Show()

    def show_users(self):
        self.display_users.Clear()
        for n in self.all_users:
            self.display_users.Append(n)

    def find_user(self, evt):
        self.to_user = self.display_users.GetString(self.display_users.GetSelection())

        if self.to_user != 'PUBLIC':
            self.msg.Append("Got user to send to " + self.to_user)
        else:
            self.msg.Append("will send a public message if send button is pressed")
    def show_hide_after_login(self):
        self.BtnSend.Show()
        self.BtnClos.Show()
        self.data_to_server.Show()
        self.EnterUsername.Hide()
        self.EnterPassword.Hide()
        self.EnterPasswordShow.Hide()
        self.BtmLogin1.Hide()
        self.BtmLogin2.Hide()
        self.BtmSignup2.Hide()
        self.BtmSignup1.Hide()
        self.showpass.Hide()
        self.display_users.Show()






    def onExit(self, event):
        self.Destroy()

    def CloseConnection(self,event):
        if self.state != 'start':
            if self.mode == 'DH':
                send_with_AES(self.client_sock, 'DISCON|', self.DiffieHellmankey, self.IV)
            else:
                send_with_AES(self.client_sock, 'DISCON|', self.KeyRSA, self.IV)
            self.client_sock.close()
            #self.listener.join()
            self.msg.Append("Connection Closed")
        print ("Bye 2")

        self.Destroy()


    def OnTcpConnectSignup(self):
        if  self.EnterUsername.Value == "" or self.EnterPassword.Value == "":
            self.msg.Append("Please enter username and password")
            return
        try:
            self.client_sock = socket.socket()
            self.client_sock.connect((self.ip, 33445))
            self.listener = threading.Thread(target=self.listen)
            if self.mode:
                send_with_size(self.client_sock, self.mode)
            self.DiffieHellman(self.client_sock)
            self.RSAKey(self.client_sock)
            if self.is_closed:
                if self.mode == 'DH':
                    send_with_AES(self.client_sock,"SIGNUP|"+ self.EnterUsername.Value +"|" + self.EnterPassword.Value, self.DiffieHellmankey, self.IV)
                else:
                    send_with_AES(self.client_sock,"SIGNUP|"+ self.EnterUsername.Value +"|" + self.EnterPassword.Value, self.KeyRSA, self.IV)
            else:
                if self.mode == 'DH':
                    send_with_AES(self.client_sock, "SIGNUP|" + self.EnterUsername.Value + "|" + self.EnterPasswordShow.Value, self.DiffieHellmankey, self.IV)
                else:
                    send_with_AES(self.client_sock, "SIGNUP|" + self.EnterUsername.Value + "|" + self.EnterPasswordShow.Value, self.KeyRSA, self.IV)
            self.state = "signup_sent"
            self.listener.start()
        except Exception as err:
            self.msg.Append("Error while try to connect msg=" + str(err))

    def OnTcpConnect(self):
        if  self.EnterUsername.Value == "" or self.EnterPassword.Value == "":
            self.msg.Append("Please enter username and password")
            return
        try:
            self.client_sock = socket.socket()
            self.client_sock.connect((self.ip, 33445))
            self.listener = threading.Thread(target=self.listen)
            if self.mode:
                send_with_size(self.client_sock, self.mode)
            if not self.GeneratedDH and not self.GeneratedRSA:
                self.DiffieHellman(self.client_sock)
                self.RSAKey(self.client_sock)
            if self.is_closed:
                if self.mode == 'DH':
                    send_with_AES(self.client_sock,"LOGIN_|"+ self.EnterUsername.Value +"|" + self.EnterPassword.Value, self.DiffieHellmankey, self.IV)
                else:
                    send_with_AES(self.client_sock,"LOGIN_|"+ self.EnterUsername.Value +"|" + self.EnterPassword.Value, self.KeyRSA, self.IV)
            else:
                if self.mode == 'DH':
                    send_with_AES(self.client_sock, "LOGIN_|" + self.EnterUsername.Value + "|" + self.EnterPasswordShow.Value, self.DiffieHellmankey, self.IV)
                else:
                    send_with_AES(self.client_sock,"LOGIN_|" + self.EnterUsername.Value + "|" + self.EnterPasswordShow.Value,self.KeyRSA, self.IV)
                self.state = "login_sent"
            self.listener.start()
        except Exception as err:
            self.msg.Append("Error while try to connect msg=" + str(err))

    def listen(self):
        while True:
            try:
                self.client_sock.settimeout(1)
                if self.mode != 'DH':
                    data = recv_with_AES(self.client_sock,self.KeyRSA, self.IV).decode('utf-8')
                else:
                    data = recv_with_AES(self.client_sock,self.DiffieHellmankey, self.IV).decode('utf-8')
                if data == "":
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
                        self.SetTitle(self.username + " Connected ")
                        self.msg.Append("You've connected successfully and you're now online")
                    elif fields[0] == 'ARC':
                        self.msg.Append('User already connected')
                        self.GeneratedDH = False
                        self.GeneratedRSA = False
                        return
                    else:
                        self.msg.Append("Error Wrong user or password. Try again")
                        self.GeneratedDH = False
                        self.GeneratedRSA = False
                        return
                elif action == "SIGNOK":
                    self.BtmLogin1.Hide()
                    self.BtmSignup1.SetPosition(wx.Point(570, 450))
                    self.BtmSignup1.Show()
                    self.BtmLogin2.Show()
                    self.BtmSignup2.Hide()
                    self.EnterUsername.Show()
                    self.EnterPassword.Show()
                    self.EnterUsername.SetValue('')
                    self.EnterPassword.SetValue('')
                    self.EnterPasswordShow.SetValue('')
                    self.showpass.SetBitmap(self.eye_closed)
                    self.showpass.Show()
                    self.msg.Show()
                    self.msg.Append('SignUp Success')
                    self.GeneratedDH = False
                    self.GeneratedRSA = False
                    return
                elif action == 'SIGNNO':
                    self.msg.Append('Username already taken, pick another one')
                    self.GeneratedDH = False
                    self.GeneratedRSA = False
                    return
                elif action == 'NEWLOG':
                    if fields[0] != self.username:
                        self.data_from_server.Append(f"{fields[0]} connected")
                    self.all_users = ['PUBLIC']
                    if len(fields) > 2:
                        for i in range(1, len(fields)):
                            if fields[i] != self.username:
                                self.all_users.append(fields[i])
                        self.show_users()
                elif action == 'NEWDIS':
                    self.data_from_server.Append(f"{fields[0]} disconnected")
                    if fields[0] == self.to_user:
                        self.to_user = ''
                        self.msg.Append(f'Returned to public sending because the person you chose disconnected')
                    self.all_users = ['PUBLIC']
                    for i in range(1, len(fields)):
                        if fields[i] != self.username:
                            self.all_users.append(fields[i])
                    self.show_users()
                elif action =="MESSAG":
                    if fields[0] == 'PR':
                        if fields[1] != self.username:
                            self.data_from_server.Append(f'Recived a private message from: {fields[1]}, {fields[2]}')
                    else:
                        if fields[1] != self.username:
                            self.data_from_server.Append(f'Recived a message from: {fields[1]}, {fields[2]}')
                elif action == 'MSGRCV':
                    self.msg.Append(f'Message sent')
                elif action == 'ERRORR':
                    self.msg.Append(fields[0])
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
        if self.to_user != "" and self.to_user != 'PUBLIC':
            to_send = "PRIVAT|"+self.to_user + "|" + self.data_to_server.Value
            self.data_from_server.Append(f"Sent a private message to: {self.to_user}, {self.data_to_server.Value}")
        else:
            to_send = "PUBLIC|" + self.data_to_server.Value
            self.data_from_server.Append(f"Sent a public message, {self.data_to_server.Value}")


        try:
            if self.mode == 'DH':
                send_with_AES(self.client_sock,to_send, self.DiffieHellmankey, self.IV)
            else:
                send_with_AES(self.client_sock, to_send, self.KeyRSA, self.IV)
        except:
            self.msg.Append("Try Connect")
        self.data_to_server.Value = ""

    def ChangeToRSA(self, event):
        if self.state != 'start':
            if self.mode == 'DH':
                send_with_AES(self.client_sock, 'CTORSA|', self.DiffieHellmankey, self.IV)
                self.mode = 'RSA'
                self.msg.Append('Now using RSA key exchange!')
            elif self.mode == '':
                self.mode = 'RSA'
                self.msg.Append('Now using RSA key exchange!')
            else:
                self.msg.Append('Already using RSA key exchange!')
        else:
            if self.mode == 'DH':
                self.mode = 'RSA'
                self.msg.Append('Now using RSA key exchange!')
            elif self.mode == '':
                self.mode = 'RSA'
                self.msg.Append('Now using RSA key exchange!')
            else:
                self.msg.Append('Already using RSA key exchange!')

    def ChangeToDH(self, event):
        if self.state != 'start':
            if self.mode == 'RSA':
                send_with_AES(self.client_sock, 'CHTODH|', self.KeyRSA, self.IV)
                self.mode = 'DH'
                self.msg.Append('Now using Diffie-Hellman key exchange!')
            elif self.mode == '':
                self.mode = 'DH'
                self.msg.Append('Now using Diffie-Hellman key exchange!')
            else:
                self.msg.Append('Already using Diffie-Hellman key exchange!')
        else:
            if self.mode == 'RSA':
                self.mode = 'DH'
                self.msg.Append('Now using Diffie-Hellman key exchange!')
            elif self.mode == '':
                self.mode = 'DH'
                self.msg.Append('Now using Diffie-Hellman key exchange!')
            else:
                self.msg.Append('Already using Diffie-Hellman key exchange!')


    def DiffieHellman(self, s:socket.socket):
        data = recv_by_size(s).decode('utf-8')
        splited_data = data.split('|')
        p = int(splited_data[1])
        g = int(splited_data[2])
        a = secrets.randbelow(p-2)+1
        A = pow(g,a,p)
        send_with_size(s,f'DIFHEL|{str(A)}')
        data = recv_by_size(s).decode('utf-8')
        splited_data = data.split('|')
        B = int(splited_data[1])
        key = pow(B, a, p)
        shared_secret_bytes = key.to_bytes((key.bit_length() + 7) // 8, 'big')

        self.GeneratedDH = True
        self.DiffieHellmankey = hashlib.sha256(shared_secret_bytes).digest()

    def RSAKey(self, s:socket.socket):
        r = RSA_CLASS()
        send_with_size(s, r.public_key)
        data = recv_by_size(s)
        self.KeyRSA = r.decrypt_RSA(data)
        self.GeneratedRSA = True



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