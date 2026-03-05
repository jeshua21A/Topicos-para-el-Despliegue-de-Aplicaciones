import socket
import threading
import tkinter as tk
from tkinter import simpledialog

#Clase del cliente
class Cliente:
    def __init__(self):
        self.cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cliente_socket.connect(('localhost', 12345)) #Socket de conexión para el cliente
        
        self.gui = tk.Tk()
        self.gui.withdraw()

        self.nombre_usuario = self.pedir_nombre()
        self.gui.deiconify()

        self.enviar_mensaje(f"{self.nombre_usuario} se ha unido al chat")
        self.crear_gui()

        self.recibir_hilo = threading.Thread(target=self.recibir_mensaje, daemon=True)
        self.recibir_hilo.start()

    def pedir_nombre(self):
        nombre = simpledialog.askstring("Nombre", "Ingrese su nombre: ", parent=self.gui)
        return nombre if nombre else "Usuario anonimo"

    def crear_gui(self):
        self.gui.title(f"Chat de {self.nombre_usuario}")
        self.gui.geometry("400x350")

        etiqueta_usuario = tk.Label(self.gui, text=f"Bienvenido, {self.nombre_usuario}", font=("Arial", 12, "bold"))
        etiqueta_usuario.pack(pady=5)

        self.texto_display = tk.Text(self.gui, width=50, height=10, wrap="word", state=tk.DISABLED)
        self.texto_display.pack(padx=10, pady=10)

        self.mensaje_entrada = tk.Entry(self.gui, width=40)
        self.mensaje_entrada.pack(padx=10, pady=10)
        self.mensaje_entrada.bind("<Return>", lambda event: self.enviar_mensaje_entrada)

        enviar_boton = tk.Button(self.gui, text="Enviar", command=self.enviar_mensaje_entrada)
        enviar_boton.pack(padx=10, pady=10)

        salir_boton = tk.Button(self.gui, text="Salir", command=self.salir_chat)
        salir_boton.pack(padx=10, pady=10)

        self.gui.protocol("WM_DELETE_WINDOW", self.salir_chat)

    def enviar_mensaje(self, mensaje):
        if mensaje:
            try:
                self.cliente_socket.send(mensaje.encode('utf-8'))
            except:
                print("Error al enviar mensaje.")
    
    def enviar_mensaje_entrada(self):
        mensaje = self.mensaje_entrada.get().strip()
        if mensaje:
            if mensaje.upper() == "S":
                self.enviar_mensaje(f"{self.nombre_usuario} ha salido del chat.")
                self.salir_chat()
                return
            elif mensaje.upper() == "E":
                self.enviar_mensaje(f"{self.nombre_usuario} ha vuelto a entrar al chat.")
            else:
                self.enviar_mensaje(f"{self.nombre_usuario}: {mensaje}")
            self.mensaje_entrada.delete(0, tk.END)

    def recibir_mensaje(self):
        while True:
            try:
                mensaje = self.cliente_socket.recv(1024).decode('utf-8')
                if mensaje:
                    self.texto_display.config(state=tk.NORMAL)
                    self.texto_display.insert(tk.END, f"{mensaje}\n")
                    self.texto_display.config(state=tk.DISABLED)
                    self.texto_display.yview(tk.END)
            except:
                print("Error al recibir mensajes.")
                break
    
    def salir_chat(self):
        try:
            self.cliente_socket.send("SALIR".encode('utf-8'))
        except:
            pass
        self.cliente_socket.close()
        self.gui.quit()
    
    def run(self):
        self.gui.mainloop()

#Ejecución del cliente
if __name__ == "__main__":
    cliente = Cliente()
    cliente.run()
