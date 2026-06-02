# Encrypted Hybrid Chat – Secure Client-Server Messaging

A Python-based secure instant messaging application with a modern GUI,
built with wxPython.

## Features
- Live list of all connected users
- Broadcast messages to all users simultaneously
- Private 1-on-1 messaging
- Messages are ephemeral – deleted on disconnect (no server-side storage)

## Security
- User choice of key exchange protocol per session: RSA or Diffie-Hellman (DH)
- AES-256 encryption for all message payloads
- Hybrid encryption ensures no plaintext data is transmitted

## Tech Stack
- Language: Python
- GUI: wxPython
- Encryption: RSA / DH + AES-256
- Networking: TCP Sockets
