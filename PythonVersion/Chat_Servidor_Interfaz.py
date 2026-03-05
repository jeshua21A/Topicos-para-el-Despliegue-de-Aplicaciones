import socket
import threading
import tkinter as tk

#Clase del servidor
class Server:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 12345))  #Dirección y puerto del servidor
        self.server_socket.listen(5)  #El servidor solamente puede aceptar 5 clientes a la vez
        self.clientes = []  #Lista para guardar los sockets de los clientes
        self.gui = self.crear_gui()

    def crear_gui(self):
        window = tk.Tk()
        window.title("Servidor")
        window.geometry("400x300")

        self.cliente_listbox = tk.Listbox(window, width=50, height=10)
        self.cliente_listbox.pack(padx=10, pady=10)

        self.texto_display = tk.Text(window, width=50, height=10, wrap="word", state=tk.DISABLED)
        self.texto_display.pack(padx=10, pady=10)
        
        self.texto_display.config(state=tk.NORMAL)
        self.texto_display.insert(tk.END, "Esperando conexiones...\n")
        self.texto_display.config(state=tk.DISABLED)
        
        threading.Thread(target=self.aceptar_clientes, daemon=True).start()
        return window

    def aceptar_clientes(self):
        while True:
            cliente_socket, cliente_address = self.server_socket.accept()
            self.clientes.append(cliente_socket)
            self.gui.after(0, self.cliente_listbox.insert, tk.END, f"{cliente_address}")
            threading.Thread(target=self.handle_cliente, args=(cliente_socket, cliente_address), daemon=True).start()

    def handle_cliente(self, cliente_socket, cliente_address):
        while True:
            try:
                mensaje = cliente_socket.recv(1024).decode('utf-8')
                if not mensaje:
                    break

                if mensaje.upper() == "SALIR":
                    self.eliminar_cliente(cliente_socket, cliente_address)
                    break

                self.gui.after(0, self.broadcast_mensaje, mensaje, cliente_address)
            except:
                break

        self.eliminar_cliente(cliente_socket, cliente_address)

    def broadcast_mensaje(self, mensaje, cliente_address):
        self.texto_display.config(state=tk.NORMAL)
        self.texto_display.insert(tk.END, f"{mensaje}\n")
        self.texto_display.config(state=tk.DISABLED)
        self.texto_display.yview(tk.END)

        for cliente in self.clientes:
            try:
                cliente.send(mensaje.encode('utf-8'))
            except:
                pass

    def eliminar_cliente(self, cliente_socket, cliente_address):
        #Cerrar la conexion para eliminar al cliente de la lista y actualizar la GUI
        if cliente_socket in self.clientes:
            self.clientes.remove(cliente_socket)
        
        cliente_socket.close() #Cierra el socket del cliente
        
        #Eliminar cliente de la Listbox y actualizar la interfaz gráfica
        self.gui.after(0, self.actualizar_lista_clientes, cliente_address)

    def actualizar_lista_clientes(self, cliente_address):
        #Eliminar al cliente de la Listbox

        for i in range(self.cliente_listbox.size()):
            if self.cliente_listbox.get(i) == str(cliente_address):
                self.texto_display.config(state=tk.NORMAL)
                self.texto_display.insert(tk.END, f"{cliente_address} se ha desconectado.\n")
                self.texto_display.config(state=tk.DISABLED)
                self.cliente_listbox.delete(i)
                break

    def run(self):
        self.gui.mainloop()

#Ejecución del servidor
if __name__ == "__main__":
    server = Server()
    server.run()
