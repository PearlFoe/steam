from tkinter import *

class Menu(object):
	def __init__(self, window):
		super().__init__()
		self.window = window

	def add_text(self, text, col, row, padx, pady, sticky):
		lbl = Label(self.window, 
						text=text, 
						font=("Arial Bold", 12))
		lbl.grid(column=col, row=row, sticky=sticky, padx=padx, pady=pady, ipadx=10)

	def add_entry_window(self, col, row):
		message = StringVar()
		txt = Entry(self.window, width=10, textvariable=message)
		txt.grid(column=col, row=row, sticky='en', pady=18)

		return message

	def add_check_btn(self, text, col, row):
		chk_state = BooleanVar()
		chk = Checkbutton(self.window, text=text, var=chk_state)  
		chk.grid(column=col, row=row)

		return chk_state

	def add_btn(self, text, color, col, row, command=None):
		if not command:
			btn = Button(self.window, 
							text=text, 
							fg=color,
							command=self.is_clicked)
		else:
			btn = Button(self.window, 
							text=text, 
							fg=color, 
							command=command)
		btn.grid(column=col,row=row, padx=5, pady=5)

	def add_list_box(self, items, side):
		scrollbar = Scrollbar(self.window)
		scrollbar.pack(side=RIGHT, fill=Y)

		lb = Listbox(self.window, yscrollcommand=scrollbar.set) 

		for i in items:
			lb.insert(END, i)

		self.var = StringVar()

		lb.bind("<<ListboxSelect>>", self.is_selected)

		lb.pack(side=side, pady=10)
		scrollbar.config( command = lb.yview )

		return self.var

	def is_selected(self, event):
		sender = event.widget
		idx = sender.curselection()
		value = sender.get(idx)
		
		self.var.set(value)

	def is_clicked(self):
		print(max_price.get())
		print(game.get())
		print(min_volume.get())
		print(min_profit.get())
		print(param.get())
		print(sleep_delay.get())
		print(ban_sleep_delay.get())
		print(get_min_data_flag.get())