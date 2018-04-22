import tkinter as tk
from tkinter import StringVar, IntVar, ttk, filedialog as FileDialog, messagebox as MessageBox
from tkFontChooser import askfont
import datetime
import win32clipboard
import win32api
import win32print
import tempfile
import sys

__version__ = "1.0"
__author__ = "Nilso Viani"

FUENTE_POR_DEFECTO = ("Consolas",10)
FONDO_POR_DEFECTO = "#ffffff"

class InterfazDeUsuario(tk.Tk):
	
	def __init__(self, parent=None):	
		tk.Frame.__init__(self, parent)
		self.parent = parent
		self.crear_widgets()

	def crear_widgets(self):
		self.parent.title("vtext")
		self.toplevel = None

		#Barra de Menú (Menu)
		menubar = tk.Menu(self.parent)
		
		#Archivo (File)
		filemenu = tk.Menu(menubar, tearoff = 0)
		filemenu.add_command(label="Nuevo", accelerator="Ctrl+N", command=self.nuevo)
		filemenu.add_command(label="Abrir", accelerator="Ctrl+T", command=self.abrir)
		filemenu.add_command(label="Guardar", underline=0, accelerator="Ctrl+G", command=self.guardar)
		filemenu.add_command(label="Guardar como...", command=self.guardar_como)
		filemenu.add_separator()
		filemenu.add_command(label="Imprimir", accelerator="Ctrl+P", command=self.imprimir)
		filemenu.add_command(label="Salir", accelerator="Ctrl+Q", command=self.salir)
		menubar.add_cascade(menu=filemenu, label="Archivo")

		#Editar (Edit)
		self.editmenu = tk.Menu(menubar, tearoff = 0)    
		self.editmenu.add_command(label="Deshacer", accelerator="Ctrl+Z", command=self.deshacer)
		self.editmenu.add_command(label="Rehacer", accelerator="Ctrl+Y", command=lambda: self.texto.focus_get().event_generate('<<Redo>>'))
		self.editmenu.add_separator()
		self.editmenu.add_command(label="Cortar", accelerator="Ctrl+X", command=lambda: self.texto.focus_get().event_generate('<<Cut>>'))
		self.editmenu.add_command(label="Copiar", accelerator="Ctrl+C", command=lambda: self.texto.focus_get().event_generate('<<Copy>>'))
		self.editmenu.add_command(label="Pegar", accelerator="Ctrl+V", command=lambda: self.texto.focus_get().event_generate('<<Paste>>'))
		self.editmenu.add_command(label="Eliminar", accelerator="Supr", command=lambda:self.texto.focus_get().event_generate('<<Clear>>'))
		self.editmenu.add_separator()
		self.editmenu.add_command(label="Buscar...", command=self.buscar, accelerator="Ctrl+B")
		self.editmenu.add_command(label="Buscar patrones", command=lambda: MessageBox.showinfo("En construcción","Esta opción se encuentra en construcción"))
		self.editmenu.add_command(label="Reemplazar", command=self.reemplazar, accelerator="Ctrl+B")
		self.editmenu.add_command(label="Ir a...", command=self.ir_a, accelerator="Ctrl+F")
		self.editmenu.add_separator()
		self.editmenu.add_command(label="Contar Palabras", command=self.contar_palabras, accelerator="Ctrl+K")
		self.editmenu.add_command(label="Seleccionar todo", accelerator="Ctrl+A", command=self.seleccionar_todo)
		self.editmenu.add_command(label="Eliminar todo", command=lambda: self.texto.delete(1.0,"end-1c"))
		self.editmenu.add_command(label="Insertar fecha y hora", command=self.fecha_y_hora, accelerator="F3")
		menubar.add_cascade(menu=self.editmenu, label="Editar")

		#Preferencias (Preferences)
		prefmenu = tk.Menu(menubar, tearoff = 0)
		prefmenu.add_command(label="Fuente", command=self.fuente)
		prefmenu.add_command(label="Color de fondo", command=self.seleccionar_color)
		prefmenu.add_command(label="Reiniciar color y fuente", command=lambda:self.texto.config(background=FONDO_POR_DEFECTO, font=FUENTE_POR_DEFECTO))
		menubar.add_cascade(menu=prefmenu, label="Preferencias")

		#Acerca de (About)
		aboutmenu = tk.Menu(menubar, tearoff = 0)
		aboutmenu.add_command(label="Acerca de vtext", command=self.acerca_de)
		menubar.add_cascade(menu=aboutmenu, label="Acerca de")

		#Caja de texto central
		self.texto = tk.Text(self.parent)
		scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=self.texto.yview)
		scrollbar.pack(fill="y", side="right")
		self.texto.pack(fill="both", expand=True)
		self.texto.bind("<KeyRelease>",self.contar_todo_el_texto)
		self.texto.bind("<Leave>",self.habilitar_deshabilitar)

		#--------- ATAJOS DEL TECLADO (KEYBOARD SHORTCUTS)	----------
		self.texto.bind('<Control-t>', self.abrir)
		self.texto.bind('<Control-g>', self.guardar)
		self.texto.bind('<Control-n>', self.nuevo)
		self.texto.bind('<Control-q>', self.salir)
		self.texto.bind('<Control-b>', self.buscar)
		self.texto.bind('<Control-r>', self.reemplazar)
		self.texto.bind('<Control-f>', self.ir_a)
		self.texto.bind('<Control-k>', self.contar_palabras)
		self.texto.bind('<Control-p>', self.imprimir)
		self.texto.bind('<F3>', self.fecha_y_hora)

		self.texto.config(bd=0, padx=5, pady=0, background="white", yscrollcommand=scrollbar.set, font=FUENTE_POR_DEFECTO)

		#Barra informativa inferior
		self.mensaje = StringVar()
		self.contador_de_palabras = StringVar()

		self.ruta = StringVar()
		self.ruta = ""

		self.mensaje.set("Editor de Texto vtext v.1.0")
		self.barra_informativa = ttk.Label(self.parent, textvariable=self.mensaje, justify="left")
		self.barra_informativa.pack(side="left", fill="x")
		self.barra_de_palabras = ttk.Label(self.parent, textvar=self.contador_de_palabras)
		self.barra_de_palabras.pack(side="right", fill="x", padx=3)

		self.parent.config(menu=menubar)
		self.texto.focus_set()
		self.parent.protocol("WM_DELETE_WINDOW", self.salir)

	#================================================ FUNCIONES (FUNCTIONS) =================================================

	#========= NUEVO (NEW FILE)	==========
	def nuevo(self, event=None):
		self.mensaje.set("Nuevo Fichero")
		self.ruta = ""
		self.texto.delete(1.0, "end")
		self.parent.title("Nuevo Fichero")

	#========= OPEN (OPEN FILE)	==========
	def abrir(self, event=None):
		self.mensaje.set("Abrir Fichero...")
		self.ruta = FileDialog.askopenfilename(initialdir=".", filetype = (("Ficheros de texto", "*.txt"),), title="Abrir un fichero de texto")

		if self.ruta != "":
			fichero = open(self.ruta, "r")
			contenido = fichero.read()
			self.texto.delete(1.0,"end")
			self.texto.insert("insert", contenido)
			fichero.close()
			self.parent.title(self.ruta + " - vtext")
			self.contar_todo_el_texto()

		self.barra_informativa.after(1000, lambda: self.mensaje.set("Listo"))

		#========= GUARDAR (SAVE) ==========
	def guardar(self, event=None):
		self.mensaje.set("Guardar Fichero") 
		if self.ruta != "":
			contenido = self.texto.get(1.0,"end-1c")
			fichero = open(self.ruta, "w+")
			fichero.write(contenido)
			fichero.close()
			self.mensaje.set("Fichero guardado correctamente")
			MessageBox.showinfo("Guardado correcto","Fichero guardado correctamente")
			self.barra_informativa.after(1000, lambda: self.mensaje.set("Listo"))
		else:
			self.guardar_como()

	#========= GUARDAR COMO (SAVE AS) ==========
	def guardar_como(self):
		self.mensaje.set("Guardar Fichero Como...")
		fichero = FileDialog.asksaveasfile(title="Guardar Fichero", mode="w", defaultextension=".txt")

		if fichero is not None:
			self.ruta = fichero.name
			contenido = self.texto.get(1.0,"end-1c")
			fichero = open(self.ruta, "w+")
			fichero.write(contenido)
			fichero.close()
			self.mensaje.set("Fichero guardado correctamente")
			self.barra_informativa.after(1000, lambda: self.mensaje.set("Listo"))
			self.parent.title(self.ruta + " - vtext")
		else:
			self.ruta=""
			self.mensaje.set("Guardado cancelado")
			self.barra_informativa.after(1000, lambda: self.mensaje.set("Listo"))

	#========= CONTAR PALABRAS (COUNT WORDS) ==========
	def contar_palabras(self, event=None):
		try:
			contenido = self.texto.selection_get().replace("\n"," ").replace("\t"," ").split(" ")
			palabras = len(contenido)	
			for a in contenido:
				if a == None or a == "" or a == "\u2003" or a == "\n":
					palabras -= 1 
			if palabras == 1:
				MessageBox.showinfo("Contador de palabras","La selección contiene {:,} palabra".format(palabras))
			else:
				MessageBox.showinfo("Contador de palabras","La selección contiene {:,} palabras".format(palabras))
		except:
			MessageBox.showinfo("Contador de palabras","No ha seleccionado algún contenido")

	#========= IMPRIMIR (PRINT) ==========
	def imprimir(self, event=None):
		if self.toplevel is None:
			printerdef = ""

			self.toplevel = tk.Toplevel(self)
			imprimir = self.toplevel
			imprimir.geometry("225x230")
			imprimir.title("Seleccione una impresora")
			imprimir.protocol('WM_DELETE_WINDOW', self.removewindow)
			imprimir.resizable(0,0)
			imprimir.transient(self.parent)
			var1 = StringVar()
			
			lbl_seleccionar_impr = ttk.Label(imprimir, text="Seleccione una impresora de la lista")
			lbl_seleccionar_impr.grid(row=0, column=0, sticky="w", padx=5, columnspan=2, pady=5)
			
			combo_lista_impr = tk.Listbox(imprimir, width=35,listvariable=var1, activestyle=tk.NONE)
			combo_lista_impr.grid(row=1, column=0, columnspan=2, rowspan=4, sticky=tk.W+tk.E+tk.N+tk.S, padx=5)

			impresoras = list(win32print.EnumPrinters(2))

			for impresora in impresoras:
				combo_lista_impr.insert("end", impresora[2])
			
			def inciar_impresion():
				contenido = len(self.texto.get(1.0,"end-1c").replace("\n","").replace("\t",""))
				try:
					if contenido == 0:
						MessageBox.showinfo("Impresión vacía","No hay contenido para imprimir")
					elif combo_lista_impr.selection_get():
						global printerdef
						printerdef = combo_lista_impr.selection_get()
						info()
						self.mensaje.set("Imprimiendo...")
						imprimir.destroy()
						self.barra_informativa.after(2000, lambda: self.mensaje.set("Listo"))
				except:
					MessageBox.showinfo("Seleccione una impresora","Debe seleccionar una impresora de la lista")

			def info():
				texto_a_imprimir = self.texto.get("1.0", "end")
				if self.ruta != "":
					direccion = self.ruta.split("/")[-1]
					nombre_archivo = tempfile.mktemp("_{}".format(direccion))
				else:
					nombre_archivo = tempfile.mktemp(".txt")

				fichero = open(nombre_archivo, "w")
				fichero.write(texto_a_imprimir)		
				
				if sys.version_info >= (3,):
					raw_data = bytes(nombre_archivo, "utf-8")
				else:
					raw_data = nombre_archivo

				hPrinter = win32print.OpenPrinter (combo_lista_impr.selection_get())
				try:
					hJob = win32print.StartDocPrinter (hPrinter, 1, (nombre_archivo, None, "RAW"))
					try:
						win32api.ShellExecute(0, "print", nombre_archivo, None,  ".",  0)
						win32print.StartPagePrinter (hPrinter)
						win32print.WritePrinter (hPrinter, raw_data)
						win32print.EndPagePrinter (hPrinter)
					finally:
						win32print.EndDocPrinter (hPrinter)
				finally:
					win32print.ClosePrinter (hPrinter)

				fichero.close()

			boton_aceptar = ttk.Button(imprimir, text="Aceptar",command=inciar_impresion, width=15)
			boton_aceptar.grid(row=6, column=0, sticky="w", padx=5, pady=5)
			boton_cancelar = ttk.Button(imprimir, text="Cancelar",command=self.removewindow, width=15)
			boton_cancelar.grid(row=6, column=1, sticky="w", padx=5, pady=5)

			imprimir.mainloop()

	#========= SALIR (EXIT) ==========
	def salir(self, event=None):
		contenido = self.texto.get(1.0,"end-1c")

		if self.ruta == "" and contenido == "":
			self.parent.destroy()
		elif self.ruta != "": 
			fichero = open(self.ruta,"r")
			lineas = fichero.read()
			fichero.close()
			if lineas == contenido:
				self.parent.destroy()
			else:
				self.preguntar_salir()
		elif contenido != "" and self.ruta == "":
			self.preguntar_salir()
		else:
			self.parent.destroy()

	def preguntar_salir(self):
		if self.ruta =="":
			resultado = MessageBox.askquestion("Salir de vtext", "¿Desea guardar el contenido de este archivo?")
		else:
			resultado = MessageBox.askquestion("Salir de vtext", "¿Desea guardar los cambios hechos a {}?".format(self.ruta))
		if resultado == "yes":
			self.guardar_como()
		elif resultado == "no":
			self.parent.destroy()

	#========= DESHACER (UNDO) ==========
	def deshacer(self):
		try:
			self.texto.edit_undo()
		except:
			pass

	#========= SELECCIONAR TODO (SELECT ALL) ==========
	def seleccionar_todo(self):
		self.texto.focus_set()
		self.texto.tag_add("sel", "1.0", "end")

	#========= INSERTAR FECHA Y HORA (INSERT DATE AND TIME) ==========
	def fecha_y_hora(self, event=None):
		ahora = datetime.datetime.now()

		if int(ahora.hour) == 00:
			self.texto.focus_set()
			fecha = "{}/{}/{} 12:{}:{} AM".format(ahora.day, ahora.month, ahora.year, ahora.minute, ahora.second)
			self.texto.insert("insert", fecha)

		elif int(ahora.hour) > 00 and int(ahora.hour)<= 11:
			self.texto.focus_set()
			fecha = "{}/{}/{} {}:{}:{} AM".format(ahora.day, ahora.month, ahora.year, ahora.hour, ahora.minute, ahora.second)
			self.texto.insert("insert", fecha)

		elif int(ahora.hour) == 12:
			self.texto.focus_set()
			fecha = "{}/{}/{} {}:{}:{} PM".format(ahora.day, ahora.month, ahora.year, ahora.hour, ahora.minute, ahora.second)
			self.texto.insert("insert", fecha)
		else:
			resta = int(ahora.hour) - 12
			self.texto.focus_set()
			fecha = "{}/{}/{} {}:{}:{} PM".format(ahora.day, ahora.month, ahora.year, resta, ahora.minute, ahora.second)
			self.texto.insert("insert", fecha)

		self.contar_todo_el_texto()

	#========= BUSCAR (SEARCH)	==========
	def buscar(self, event=None):

		def buscar_palabras():
			self.texto.focus_set()
			patron = self.entrada.get()

			if patron == "":
				MessageBox.showinfo("Búsqueda vacía","Ingrese un elemento para iniciar la búsqueda")
			else:

				if self.distinguir.get():
					if self.direccion_busqueda.get() == 'bajar':
						res = self.texto.search(patron, 'insert', forwards=True, stopindex='end', nocase=0)
					else:
						res = self.texto.search(patron, 'insert', backwards=True, stopindex='1.0', nocase=0)

				else:
					if self.direccion_busqueda.get() == 'bajar':
						res = self.texto.search(patron, 'insert', forwards=True, stopindex='end', nocase=1)
					else:
						res = self.texto.search(patron, 'insert', backwards=True, stopindex='1.0', nocase=1)

				self.texto.tag_remove('sel', '1.0', 'end')
							
				try:
					self.texto.tag_add('sel', res, '%s+%ic' % (res, len(patron)))

					if self.direccion_busqueda.get() == 'bajar':
						self.texto.mark_set('insert', '%s+%ic' % (res, len(patron)))
						self.texto.see(res)
					else:
						self.texto.mark_set('insert', '%s' % (res))
						self.texto.see(res)
				except:
					contenido = len(self.texto.get(1.0,"end-1c").replace("\n","").replace("\t",""))
					if contenido == 0:
						MessageBox.showinfo("Entrada de texto vacía","No hay contenido en la entrada de texto, empice a escribir o abra un archivo .txt para iniciar la búsqueda")
					else:
						MessageBox.showinfo("Búsqueda finalizada","No hay más coincidencias")
		if self.toplevel is None:
			self.toplevel = tk.Toplevel(self)
			buscar = self.toplevel
			buscar.title("Buscar")
			buscar.iconbitmap("vtext.ico")
			buscar.resizable(0,0)
			buscar.geometry("470x90")
			buscar.transient(self.parent)
			buscar.protocol('WM_DELETE_WINDOW', self.removewindow)
			self.texto.tag_remove("sel", 1.0,"end-1c")

			self.entrada = ttk.Entry(buscar, width=48)
			self.entrada.place(x=55, y=10)
						
			boton_buscar = ttk.Button(buscar, text="Buscar siguiente", command=buscar_palabras, width=15).place(x=322+37, y=7)
			bonton_cancelar = ttk.Button(buscar, text="Cancelar", width=15, command=self.removewindow).place(x=322+37, y=40)
						
			self.distinguir = IntVar()
			self.check_coincidir = ttk.Checkbutton(buscar,text="Coincidir mayúsculas y minúsculas", variable = self.distinguir, command = True).place(x=5, y=52)
						
			marco = ttk.LabelFrame(buscar, width=120, height=45, text="Dirección").place(x=191+37, y=36)
						
			self.opcion = IntVar()
			self.direccion_busqueda = StringVar(buscar, 'bajar')
						
			radio_subir = ttk.Radiobutton(buscar, text="Subir", value='subir', variable=self.direccion_busqueda).place(x=196+37, y=52)
			radio_bajar = ttk.Radiobutton(buscar, text="Bajar", value='bajar', variable=self.direccion_busqueda).place(x=251+37, y=52)

			lbl_buscar = ttk.Label(buscar, text="Buscar:", justify="left").place(x=5, y=9)

			buscar.mainloop()

		#========= REEMPLAZAR (REPLACE)	==========
	def reemplazar(self, event=None):

		def buscar_palabras():
			self.texto.focus_set()
			patron = self.entrada.get()

			if patron == "":
				MessageBox.showinfo("Búsqueda vacía","Ingrese un elemento para iniciar la búsqueda")
			else:

				if self.distinguir.get():
					if self.direccion_busqueda.get() == 'bajar':
						self.res = self.texto.search(patron, 'insert', forwards=True, stopindex='end', nocase=0)
					else:
						self.res = self.texto.search(patron, 'insert', backwards=True, stopindex='1.0', nocase=0)

				else:
					if self.direccion_busqueda.get() == 'bajar':
						self.res = self.texto.search(patron, 'insert', forwards=True, stopindex='end', nocase=1)
					else:
						self.res = self.texto.search(patron, 'insert', backwards=True, stopindex='1.0', nocase=1)

				self.texto.tag_remove('sel', '1.0', 'end')
							
				try:
					self.texto.tag_add('sel', self.res, '%s+%ic' % (self.res, len(patron)))

					if self.direccion_busqueda.get() == 'bajar':
						self.texto.mark_set('insert', '%s+%ic' % (self.res, len(patron)))
						self.texto.see(self.res)
					else:
						self.texto.mark_set('insert', '%s' % (self.res))
						self.texto.see(self.res)
				except:
					contenido = len(self.texto.get(1.0,"end-1c").replace("\n","").replace("\t",""))
					if contenido == 0:
						MessageBox.showinfo("Entrada de texto vacía","No hay contenido en la entrada de texto, empice a escribir o abra un archivo .txt para iniciar la búsqueda")
					else:
						MessageBox.showinfo("Búsqueda finalizada","No hay más coincidencias")

		#--------- REEMPLAZAR POR PATRON (PATERN REPLACE)	----------
		def reemplazar_patron():
			try:
				if self.texto.selection_get():
					if self.salida.get():
						self.texto.delete(self.res, '%s+%ic' % (self.res, len(self.entrada.get())))
						self.texto.insert('insert', self.salida.get())
						self.texto.tag_remove('sel', '1.0', 'end')
					else:
						MessageBox.showinfo("Campo de reemplazo vacio","Debe ingresar algún parámetro para hacer el reemplazo")
			except:
				MessageBox.showinfo("Búsqueda finalizada","No hay más coincidencias")

		#--------- REEMPLAZAR TODO (REPLACE ALL)	----------
		def reemplazar_todo():
			if self.entrada.get() and self.salida.get():
				resultado = MessageBox.askquestion("Reemplazar todo", "¿Desea reemplazar todos los caracteres '{}' en el texto por '{}'?".format(self.entrada.get(), self.salida.get()))
				if resultado == "yes":
					if self.texto.get(1.0,"end-1c"):
						self.texto.focus_get()
						nuevo_contenido = self.texto.get(1.0,"end-1c").replace(self.entrada.get(), self.salida.get())
						if nuevo_contenido == self.texto.get(1.0,"end-1c"):
							MessageBox.showinfo("No existen coincidencias","La expresión '{}' no se encuentra en el contenido del editor de texto".format(self.entrada.get()))
						else:
							self.texto.delete(1.0,"end")
							self.texto.insert("insert", nuevo_contenido)
							MessageBox.showinfo("Reemplazo completado","Se ha reemplazado el texto de manera exitosa")
					else:
						MessageBox.showinfo("Editor de texto vacío","No hay contenido en el editor de texto")
				elif resultado == "no":
					pass
			elif self.entrada.get() == "":
				MessageBox.showinfo("Campo de entrada vacio","Debe ingresar algún parámetro para hacer la búsqueda")
			elif self.salida.get() == "":
				MessageBox.showinfo("Campo de reemplazo vacio","Debe ingresar algún parámetro para hacer el reemplazo")

		if self.toplevel is None:
			self.toplevel = tk.Toplevel(self)
			buscar = self.toplevel
			buscar.title("Reemplazar")
			buscar.resizable(0,0)
			buscar.geometry("343x122")
			buscar.transient(self.parent)
			buscar.protocol('WM_DELETE_WINDOW', self.removewindow)
			self.texto.tag_remove("sel", 1.0,"end-1c")

			lbl_buscar = ttk.Label(buscar, text="Buscar:", justify="left")
			lbl_buscar.grid(row=0, column=0, sticky="w", padx=5)

			lbl_reemplazar_por = ttk.Label(buscar, text="Remplazar por:", justify="left")
			lbl_reemplazar_por.grid(row=1, column=0, sticky="w", padx=5)

			self.entrada = ttk.Entry(buscar, width=20)
			self.entrada.grid(row=0, column=1, sticky="w", padx=5, columnspan = 2)

			self.salida = ttk.Entry(buscar, width=20)
			self.salida.grid(row=1, column=1, sticky="w", padx=5, columnspan = 2)
						
			boton_buscar = ttk.Button(buscar, text="Buscar siguiente", command=buscar_palabras, width=15)
			boton_buscar.grid(row=0, column=3, sticky="w", padx=5, pady=2)

			boton_reemplazar = ttk.Button(buscar, text="Reemplazar", command=reemplazar_patron, width=15)
			boton_reemplazar.grid(row=1, column=3, sticky="w", padx=5, pady=2)

			boton_reemplazar_todo = ttk.Button(buscar, text="Reemplazar todo", command=reemplazar_todo, width=15)
			boton_reemplazar_todo.grid(row=2, column=3, sticky="w", padx=5, pady=2)

			bonton_cancelar = ttk.Button(buscar, text="Cancelar", width=15, command=self.removewindow)
			bonton_cancelar.grid(row=3, column=3, sticky="w", padx=5, pady=2)

			self.res = StringVar()
			self.res = ""
			self.opcion = IntVar()
			self.direccion_busqueda = StringVar(buscar, 'bajar')

			lbl_direccion = ttk.Label(buscar, text="Dirección:", justify="left")
			lbl_direccion.grid(row=2, column=0, sticky="w", padx=5)	
						
			radio_subir = ttk.Radiobutton(buscar, text="Subir", value='subir', variable=self.direccion_busqueda)
			radio_subir.grid(row=2, column=1, sticky="w", padx=5, columnspan = 3)
			
			radio_bajar = ttk.Radiobutton(buscar, text="Bajar", value='bajar', variable=self.direccion_busqueda)
			radio_bajar.grid(row=2, column=2, sticky="w", padx=5, columnspan = 3)			
			
			self.distinguir = IntVar()
			self.check_coincidir = ttk.Checkbutton(buscar,text="Coincidir mayúsculas y minúsculas", variable = self.distinguir, command = True)
			self.check_coincidir.grid(row=3, column=0, sticky="w", padx=5, columnspan = 3)
						
			buscar.mainloop()

	#========= IR A (GO TO)	==========
	def ir_a(self, event=None):
		if self.toplevel is None:
			self.toplevel = tk.Toplevel(self)
			ir_a = self.toplevel
			ir_a.title("Ir a linea")
			ir_a.resizable(0,0)
			ir_a.geometry("297x66")
			ir_a.protocol('WM_DELETE_WINDOW', self.removewindow)
			
			def ir_a_linea():
				self.texto.focus_set()
				try:
					linea = float(int(entrada.get()))
					self.texto.mark_set("insert", "%d.%d" % (linea,0))
					self.texto.see(linea)
					ir_a.destroy()

				except ValueError:
					if entrada.get() == "":
						MessageBox.showwarning("Error de formato","Entrada vacia, debe ingresar números enteros sin comas o puntos")
						entrada.focus_set()
					else:
						MessageBox.showwarning("Error de formato","Solo se puede ingresar números enteros sin comas o puntos")
						entrada.focus_set()

			cuenta_de_lineas = int(self.texto.index('end-1c').split('.')[0])
			cantidad_de_lineas = StringVar()
			cantidad_de_lineas.set("Líneas: {:,}".format(cuenta_de_lineas))

			lbl_ir_a = ttk.Label(ir_a, text="Número de línea:", justify="left")
			lbl_ir_a.grid(row=0, column=0, sticky="w", padx=5)
			entrada = ttk.Entry(ir_a)
			entrada.grid(row=1, column=0, columnspan=3, sticky=tk.W+tk.E+tk.N+tk.S, padx=5)
			lbl_cantidad = ttk.Label(ir_a, textvar=cantidad_de_lineas, justify="left")
			lbl_cantidad.grid(row=2, column=0, sticky="w", padx=5)
			
			entrada.focus_set()

			boton_aceptar = ttk.Button(ir_a, text="Ir a", command=ir_a_linea).grid(row=1, column=3, sticky=tk.W+tk.E+tk.N+tk.S)
			bonton_cancelar = ttk.Button(ir_a, text="Cancelar", command=self.removewindow).grid(row=1, column=4, sticky=tk.W+tk.E+tk.N+tk.S, padx=5)

			ir_a.mainloop()

	#--------- ABRIR PORTAPAPELES (OPEN CLIPBOARD)	----------
	def abrir_portapapeles(self):
		try:
			win32clipboard.OpenClipboard()
			datos = win32clipboard.GetClipboardData()
			win32clipboard.CloseClipboard()
			return True
		except TypeError:
			return False

	#--------- HABILITAR Y DESHABILITAR OPCIONES DEL MENÚ DE EDICIÓN (ENABLE O DISABLE OPTIONS IN EDIT MENU) ----------
	def habilitar_deshabilitar(self, event):
		try:
			if self.texto.selection_get():
				self.editmenu.entryconfig(3,state="normal") #Cortar
				self.editmenu.entryconfig(4,state="normal") #Copiar
				self.editmenu.entryconfig(5,state="normal") #Pegar
				self.editmenu.entryconfig(6,state="normal") #Eliminar
		except:
			self.editmenu.entryconfig(3,state="disabled") #Cortar
			self.editmenu.entryconfig(4,state="disabled") #Copiar
			self.editmenu.entryconfig(6,state="disabled") #Eliminar

			if self.abrir_portapapeles():
				self.editmenu.entryconfig(5,state="normal") #Pegar
			else:
				self.editmenu.entryconfig(5,state="disabled") #Pegar

	#--------- CONTAR TODO EL TEXTO (INCLUYENDO EL EVENTO AL LEVANTAR UNA TECLA DEL WIDGET DE TEXTO)  COUNT ALL TEXT (KEYRELEASE EVENT INCLUDED OF THE TEXT WIDGET)----------
	def contar_todo_el_texto(self, event=None):
		contenido = self.texto.get(1.0,"end-1c").replace("\n"," ").replace("\t"," ").split(" ")
		palabras = len(contenido)
		
		for a in contenido:
			if a == None or a == "" or a == "\u2003" or a == "\n":
				palabras -= 1 

		lineas = int(self.texto.index('end-1c').split('.')[0])

		if lineas ==1:
			lineas_cuenta = "línea"
		else:
			lineas_cuenta = "líneas"

		if palabras == 1:
			self.contador_de_palabras.set("{:,} palabra | {:,} {}".format(palabras, lineas, lineas_cuenta))
		else:
			self.contador_de_palabras.set("{:,} palabras | {:,} {}".format(palabras, lineas, lineas_cuenta))

	#========= SELECCIONAR COLOR DE FONDO (BACKGROUND SELECTOR) ==========
	def seleccionar_color(self):
		try:
			(rgb, hx) = tk.colorchooser.askcolor()
			self.texto.config(background=hx) 	
		except TclError:
			pass

	#========= SELECCIONAR TIPO DE FUENTE (FONT SELECTOR) ==========
	def fuente(self, event=None):
		try:
			font = askfont()
			if font:
				font['family'] = font['family'].replace(' ', '\ ') # spaces in the family name need to be escaped
				font_str = "%(family)s %(size)i %(weight)s %(slant)s" % font
			if font['underline']:
				font_str += ' underline'
			if font['overstrike']:
				font_str += ' overstrike'
			self.texto.config(font=font_str)
		except:
			pass

	#========= ACERCA DE (ABOUT)	==========
	def acerca_de(self):
		if self.toplevel is None:
			self.toplevel = tk.Toplevel(self)
			self.about = self.toplevel
			self.about.title("Acerca de vtext")
			self.about.resizable(0,0)
			self.about.geometry("460x365")
			self.about.transient(self.parent)
			self.about.protocol('WM_DELETE_WINDOW', self.removewindow)

			descripcion = """_________vtext versión 1.0_________

vtext 
Es un editor de texto plano
Codificado en lenguaje Python 3.6
Con librerías gráficas de Tkinter
Creado por Nilso Viani
Desarrollador Python Junior
Hispanos Soluciones, C.A

_________Agradecimientos a:_________

Héctor Costa
web: escueladevideojuegos.net

Charles R. Severance
e-Book: "Python for Everybody
Exploring Data Using Python 3"

John W. Shipman
web: nmt.edu/tcc/help/pubs/tkinter

Bernd Klein
web: python-course.eu

Alejandro Alvarez
e-Book: "Guia Tkinter Documentation"
Publicación 0.1.1

John E. Grayson
e-Book: "Python and Tkinter Programming"

Harrison Kinsley
youtube: /user/sentdex
web: pythonprogramming.net

Tim Golden's
web: timgolden.me.uk/python/

Daniel Kukiela
(Discord user: #5991)

Vixion
(Discord user: #1682)

Joe Stepp
github.com/Drax-il

_________ stackoverflow.com: ________
Especialmente a:

j_4321
(user:6415268)

Brian Fuller
(user:2491028)

Bryan Oakley
(user:7432)

mgilson
(user:748858)

Jeff Laughlin
(user:1473921)

Brian
(user:9493)

Jeremy Gordon
(user:286062)

Abhishek Kumar
(user:2219529)

unutbu
(user:190597)

AD WAN
(user:8388511)

Goran
(user:7861231)

Reese Currie
(user:491707)

A. Rodas
(user:1019227)
__________________________________

"Tecwant"
youtube: /channel/UCBEziq3AYShnNFqT1jcGsrw

Volunteers in the Tcl community
Tcl Developer Xchange
web: tcl.tk

Python Software Foundation ©
web: pypi.python.org

Anthony Tuininga
cx_Freeze package ©
web: anthony-tuininga.github.io/cx_Freeze

Jordan Russell
Inno Setup Compiler ©
web: jrsoftware.org

Graphic Resources S.L ©
web: flaticon.es

CONVERTICO.COM ©

Al contenido publicado en las siguientes webs y sus autores:

pythonhosted.com
github.com
effbot.org/tkinterbook
acodigo.blogspot.com
mail.python.org
tutorialspoint.com/python
python-para-impacientes.blogspot.com
docs.python.org
recursospython.com

__________ Código fuente en: ________
github.com/nilsoviani/vtext
"""

			#Logo de vtext
			imagen_logo = tk.PhotoImage(file="vtext.png")
			logo_vtext = ttk.Label(self.about, image=imagen_logo, justify="left").place(x=257+43, y=20+55)

			#Logo de Python
			imagen_python = tk.PhotoImage(file="python_logo.png") 
			logo_python = ttk.Label(self.about, image=imagen_python, justify="left").place(x=253, y=270)
				
			#Marco de Información
			lbl_frame_texto = ttk.LabelFrame(self.about, text="Información")
				
			#Barra de desplazamiento de los agradecimientos
			scrollbar = ttk.Scrollbar(lbl_frame_texto)

			#Texto de agradecimientos
			agradecimientos = tk.Text(lbl_frame_texto, yscrollcommand=scrollbar.set, width=34, height=24, wrap="word", font=(False, 8), padx=5)

			scrollbar.config(command=agradecimientos.yview)
			scrollbar.pack(side="right", fill="y")

			agradecimientos.pack(side="left", fill="both", expand=True)
			lbl_frame_texto.place(x=10, y=0)
				
			agradecimientos.insert('insert', descripcion)
			agradecimientos.config(state="disabled")

			self.about.mainloop()

	#========= DESTRUCTOR DE VENTANAS TOP LEVEL (TOP LEVEL WINDOWS DESTROYER) ==========
	def removewindow(self):
		self.toplevel.destroy()
		self.toplevel = None

#Bucle de la Aplicación (App Loop)
if __name__ == "__main__":
	root = tk.Tk()
	root.iconbitmap(default="vtext.ico")
	root.geometry("540x460")
	app = InterfazDeUsuario(parent=root)
	app.mainloop()
