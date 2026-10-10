"""
TransitPulse AI - Port 8501 to 8502 Transparent TCP Proxy
Ensures that users navigating to either http://localhost:8501 or http://localhost:8502
reach the active Streamlit operational intelligence platform seamlessly.
"""
import socket
import threading
import sys

def forward(source, destination):
    try:
        while True:
            data = source.recv(8192)
            if not data:
                break
            destination.sendall(data)
    except Exception:
        pass
    finally:
        try:
            source.close()
        except Exception:
            pass
        try:
            destination.close()
        except Exception:
            pass

def handle_client(client_socket):
    try:
        backend_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        backend_socket.connect(("127.0.0.1", 8502))
        
        t1 = threading.Thread(target=forward, args=(client_socket, backend_socket), daemon=True)
        t2 = threading.Thread(target=forward, args=(backend_socket, client_socket), daemon=True)
        t1.start()
        t2.start()
    except Exception as e:
        try:
            client_socket.close()
        except Exception:
            pass

def run_proxy(listen_port=8501, target_port=8502):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind(("0.0.0.0", listen_port))
    except Exception as e:
        print(f"Could not bind to port {listen_port}: {e}")
        sys.exit(1)
        
    server.listen(30)
    print(f"TransitPulse Port Forwarder: http://localhost:{listen_port} -> http://localhost:{target_port}")
    
    while True:
        try:
            client, addr = server.accept()
            threading.Thread(target=handle_client, args=(client,), daemon=True).start()
        except KeyboardInterrupt:
            break
        except Exception:
            pass

if __name__ == "__main__":
    run_proxy()
