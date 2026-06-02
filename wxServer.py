from random import randbytes

from AsyncMessages import AsyncMessages
import socket
import threading

from RSA import RSA_CLASS
from tcp_by_size import send_with_size, recv_by_size
import pickle
import os
import hashlib
import secrets
from TCP_AES import send_with_AES, recv_with_AES
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


As = None
Users = None
IV = 'hefuhrgjhsdfirps'
online_users = {}

PEPPER = 'HelloPepperebhsdj'

def hashing_for_sign_up(data):
    global PEPPER
    salt = os.urandom(16)
    salted_pass = data.encode() + salt + PEPPER.encode()
    sha = hashlib.sha256()
    sha.update(salted_pass)
    return sha.hexdigest(), salt

def hash(password,salt):
    global PEPPER
    salted_pass = password.encode() + salt + PEPPER.encode()
    sha = hashlib.sha256()
    sha.update(salted_pass)
    return sha.hexdigest()

def generate_large_prime():
    p_hex = """
        FFFFFFFF FFFFFFFF C90FDAA2 2168C234 C4C6628B 80DC1CD1
        29024E08 8A67CC74 020BBEA6 3B139B22 514A0879 8E3404DD
        EF9519B3 CD3A431B 302B0A6D F25F1437 4FE1356D 6D51C245
        E485B576 625E7EC6 F44C42E9 A637ED6B 0BFF5CB6 F406B7ED
        EE386BFB 5A899FA5 AE9F2411 7C4B1FE6 49286651 ECE65381
        FFFFFFFF FFFFFFFF
    """.replace('\n', '').replace(' ', '')
    return int(p_hex, 16)


def DiffieHellman(s:socket.socket):
    p = generate_large_prime()
    g = 5
    send_with_size(s,f'DIFHEL|{str(p)}|{str(g)}')
    a = secrets.randbelow(p-2)+1
    A = pow(g,a,p)
    send_with_size(s,f'DIFHEL|{str(A)}')
    data = recv_by_size(s).decode('utf-8')
    splited_data = data.split('|')
    B = int(splited_data[1])
    key = pow(B, a, p)
    shared_secret_bytes = key.to_bytes((key.bit_length() + 7) // 8, 'big')
    return hashlib.sha256(shared_secret_bytes).digest()


def handle_client(cli_socket, ip):
    global AM
    global Users
    global IV
    global online_users
    username = ''
    mode = ''
    data = recv_by_size(cli_socket).decode('utf-8')
    code = data[:6]
    print(code)
    mode = data
    DiffieHellmanKey = DiffieHellman(cli_socket)
    r = RSA_CLASS()
    RSAkey = randbytes(16)
    data = recv_by_size(cli_socket).decode('utf-8')
    r.set_other_public(data)
    send_with_size(cli_socket, r.encrypt_RSA(RSAkey))
    print(RSAkey)
    print(999999999999999999999999)
    while True:
        try:
            cli_socket.settimeout(1)
            if mode == 'DH':
                data = recv_with_AES(cli_socket, DiffieHellmanKey, IV).decode('utf-8')
            else:
                data = recv_with_AES(cli_socket, RSAkey, IV).decode('utf-8')
                print(f'{data}555')
            code = data[:6]
            data = data[7:]
            data = data.split('|')
            if code == 'SIGNUP':
                if data[0] in Users.keys():
                    if mode == 'DH':
                        send_with_AES(cli_socket,'SIGNNO|', DiffieHellmanKey, IV)
                        return
                    else:
                        send_with_AES(cli_socket,'SIGNNO|', RSAkey, IV)
                        return
                else:
                    hashed, salt = hashing_for_sign_up(data[1])
                    Users[data[0]] = (data[0],data[1],hashed,salt)
                    if mode == 'DH':
                        send_with_AES(cli_socket,'SIGNOK|', DiffieHellmanKey, IV)
                    else:
                        send_with_AES(cli_socket, 'SIGNOK|', RSAkey, IV)
                    with open('users.pkl', 'wb') as file:
                        pickle.dump(Users, file)
                    return
            elif code == 'LOGIN_':
                try:
                    username = data[0]
                    val = Users[username]
                    if username in As.sock_by_user.keys():
                        if mode == 'DH':
                            send_with_AES(cli_socket, 'LOGINR|ARC', DiffieHellmanKey, IV)
                            return
                        else:
                            send_with_AES(cli_socket, 'LOGINR|ARC', RSAkey, IV)
                            return
                    elif val[2] == hash(data[1],val[3]):
                        if mode == 'DH':
                            send_with_AES(cli_socket, 'LOGINR|Ok', DiffieHellmanKey, IV)
                        else:
                            send_with_AES(cli_socket, 'LOGINR|Ok', RSAkey, IV)
                        As.add_new_socket(cli_socket)
                        As.sock_by_user[username] = cli_socket
                        online_users[cli_socket] = [mode, DiffieHellmanKey, RSAkey]
                        users = ''
                        for g in As.sock_by_user.keys():
                            users += f'{g}|'
                        for i in As.async_msgs.keys():
                            if online_users[i][0] == 'DH':
                                send_with_AES(i, f'NEWLOG|{username}|{users}'[:-1], online_users[i][1], IV)
                            else:
                                send_with_AES(i, f'NEWLOG|{username}|{users}'[:-1], online_users[i][2], IV)
                        users = ''
                    else:
                        if mode == 'DH':
                            send_with_AES(cli_socket, 'LOGINR|', DiffieHellmanKey, IV)
                            return
                        else:
                            send_with_AES(cli_socket, 'LOGINR|', RSAkey, IV)
                            return
                except BaseException as e:
                    print(e)
                    if mode == 'DH':
                        send_with_AES(cli_socket, 'LOGINR|', DiffieHellmanKey, IV)
                    else:
                        send_with_AES(cli_socket, 'LOGINR|', RSAkey, IV)
            elif code == 'PRIVAT':
                As.put_msg_by_user(f'PR|{username}|{data[1]}', data[0])
                if mode == 'DH':
                    send_with_AES(cli_socket, 'MSGRCV|', DiffieHellmanKey, IV)
                else:
                    send_with_AES(cli_socket, 'MSGRCV|', RSAkey, IV)
            elif code == 'PUBLIC':
                As.put_msg_to_all(f'PU|{username}|{data[0]}')
                if mode == 'DH':
                    send_with_AES(cli_socket, 'MSGRCV|', DiffieHellmanKey, IV)
                else:
                    send_with_AES(cli_socket, 'MSGRCV|', RSAkey, IV)
                print(mode)
            elif code == 'DISCON':
                As.delete_socket(cli_socket)
                del As.sock_by_user[username]
                del online_users[cli_socket]
                for i in As.async_msgs.keys():
                    for g in As.sock_by_user.keys():
                        users += f'{g}|'
                    if online_users[i][0] == 'DH':
                        send_with_AES(i, f'NEWDIS|{username}|{users}'[:-1], online_users[i][1], IV)
                    else:
                        send_with_AES(i, f'NEWDIS|{username}|{users}'[:-1], online_users[i][2], IV)
                    users = ''
                cli_socket.close()
                return
            elif code == 'CTORSA':
                mode = 'RSA'
                online_users[cli_socket] = [mode,DiffieHellmanKey,RSAkey]
            elif code == 'CHTODH':
                mode = 'DH'
                online_users[cli_socket] = [mode,DiffieHellmanKey,RSAkey]
        except socket.timeout:
            if cli_socket in As.async_msgs.keys():
                msgs = As.get_async_messages_to_send(cli_socket)
                for i in msgs:
                    if online_users[cli_socket][0] == 'DH':
                        send_with_AES(cli_socket, f'MESSAG|{i}', online_users[cli_socket][1], IV)
                    else:
                        send_with_AES(cli_socket, f'MESSAG|{i}', online_users[cli_socket][2], IV)
        except ConnectionResetError as e:
            print("Error, socket closed unexpectedly, leaving")
            As.delete_socket(cli_socket)
            del As.sock_by_user[username]
            del online_users[cli_socket]
            for i in As.async_msgs.keys():
                for g in As.sock_by_user.keys():
                    users += f'{g}|'
                if online_users[i][0] == 'DH':
                    send_with_AES(i, f'NEWDIS|{username}|{users}'[:-1], online_users[i][1], IV)
                else:
                    send_with_AES(i, f'NEWDIS|{username}|{users}'[:-1], online_users[i][2], IV)
                users = ''
            cli_socket.close()
            return
        except KeyError as e:
            if mode == 'DH':
                send_with_AES(cli_socket, 'ERRORR|The user you chose disconnected', DiffieHellmanKey,IV)
            else:
                send_with_AES(cli_socket, 'ERRORR|The user you chose disconnected', RSAkey, IV)




def main():
    global As
    global Users
    As = AsyncMessages()
    threads = []
    if os.path.isfile('users.pkl'):
        with open('users.pkl', 'rb') as file:
            Users = pickle.load(file)
    else:
        Users = {}

    srv_sock = socket.socket()

    srv_sock.bind(('127.0.0.1', 33445))

    srv_sock.listen(20)

    # next line release the port
    srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    i = 1
    while True:
        print('\nMain thread: before accepting ...')
        cli_sock, addr = srv_sock.accept()
        t = threading.Thread(target=handle_client, args=(cli_sock, addr))
        t.start()
        i += 1
        threads.append(t)
        if i > 100000000:  # for tests change it to 4
            print('\nMain thread: going down for maintenance')
            break

    all_to_die = True
    print('Main thread: waiting to all clints to die')
    for t in threads:
        t.join()
    srv_sock.close()
    print('Bye ..')


if __name__ == '__main__':
    main()