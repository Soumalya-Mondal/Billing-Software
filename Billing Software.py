from tkinter import *
from tkinter import ttk
import tkinter.messagebox as tmsg
import sqlite3, os, sys, re, win32api, win32print, cv2
from fpdf import FPDF
from math import ceil
from time import strftime


# ================================ Define Function =========================== #

# ================================================ Send Data To Database Function ============================================ #
def productDB(final_list):
	def customer_db(customer_list):
		c.execute('SELECT * FROM customer ORDER BY rowid DESC LIMIT 1')
		if c.fetchone()== None:
			invoice_id= strftime('%y%d%m')+ '0001'
			c.execute('INSERT INTO customer VALUES (:invoice_id,:invoice_date, :customer_name, :customer_phone, :discount_price)', {'invoice_id': invoice_id, 'invoice_date': strftime('%d/%m/%Y'), 'customer_name': customer_list[0], 'customer_phone': customer_list[1], 'discount_price': customer_list[2]})
			conn.commit()
			return invoice_id

		if c.fetchone()!= []:
			c.execute('SELECT * FROM customer ORDER BY rowid DESC LIMIT 1')
			prev_invoice_id= c.fetchone()[0]
			invoice_id= strftime('%y%d%m')+ (str(int(prev_invoice_id[6:])+ 1)[-4:].zfill(4))
			c.execute('INSERT INTO customer VALUES (:invoice_id, :invoice_date, :customer_name, :customer_phone, :discount_price)', {'invoice_id': invoice_id, 'invoice_date': strftime('%d/%m/%Y'), 'customer_name': customer_list[0], 'customer_phone': customer_list[1], 'discount_price': customer_list[2]})
			conn.commit()
			return invoice_id

	def product_db(invoice_id, product_list):
		for i in range(0, int(len(product_list)/4)):
			c.execute('INSERT INTO invoice VALUES (:invoice_id, :product_name, :product_id, :product_quantity, :product_price)', {'invoice_id': invoice_id, 'product_name': product_list[i*4], 'product_id': product_list[(i*4)+ 1], 'product_quantity': product_list[(i*4)+ 2], 'product_price': product_list[(i*4)+ 3]})
			conn.commit()

	conn= sqlite3.connect('G:\\My Drive\\speedly.db')
	c= conn.cursor()

	customerTable= c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='customer'").fetchall()
	invoiceTable= c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='invoice'").fetchall()
	if customerTable== [] and invoiceTable== []:
		c.execute('CREATE TABLE customer (invoice_id TEXT PRIMARY KEY, invoice_date TEXT NOT NULL,customer_name TEXT NOT NULL, customer_phone TEXT NOT NULL, discount_price REAL NOT NULL)')
		c.execute('CREATE TABLE invoice (invoice_id TEXT NOT NULL, product_name TEXT NOT NULL, product_id TEXT NOT NULL, product_quantity INTEGER NOT NULL, product_price REAL NOT NULL)')
		conn.commit()

	invoice_id= customer_db(final_list[0:3])
	product_db(invoice_id, final_list[3:])
	makePDF([str(invoice_id)]+ [strftime('%d/%m/%Y')]+ final_list)

# ============================================================================================================================ #

# =================================================== Print The Invoice ====================================================== #
def makePDF(product_details):
	def resource_path_file(relative_path):
		try:
			base_path= sys._MEIPASS
		except Exception:
			base_path= os.path.abspath('.')
		return os.path.join(base_path, relative_path)

	def print_invoice_no(invoice_no):
		pdf.set_font('Times', 'B', 18)
		pdf.set_xy(443, 71)
		pdf.cell(0, 0, f'{invoice_no}')

	def print_invoice_date(invoice_date):
		pdf.set_font('Times', 'B', 18)
		pdf.set_xy(447, 121)
		pdf.cell(0, 0, f'{invoice_date}')

	def print_customer_name(customer_name):
		pdf.set_font('Times', '', 20)
		pdf.set_xy(110, 693)
		pdf.cell(0, 0, f'{customer_name}')

	def print_customer_phone(customer_phone):
		pdf.set_font('Times', '', 20)
		pdf.set_xy(110, 724)
		pdf.cell(0, 0, f'{customer_phone}')

	def print_product_serial_number(count, x_position, y_position, product_serial_number):
		pdf.set_font('Helvetica', 'B', 12)
		pdf.set_xy(x_position, y_position+(count*25))
		pdf.cell(0, 0, f'{product_serial_number}')

	def print_product_name(count, x_position, y_position, product_name):
		pdf.set_font('Helvetica', 'B', 12)
		pdf.set_xy(x_position, y_position+(count*25))
		pdf.cell(0, 0, f'{product_name}')

	def print_product_quantity(count, x_position, y_position, product_quantity):
		pdf.set_font('Helvetica', 'B', 12)
		pdf.set_xy(x_position, y_position+(count*25))
		pdf.cell(0, 0, f'{product_quantity}')

	def print_product_unit_price(count, x_position, y_position, product_unit_price):
		pdf.set_font('Helvetica', 'B', 12)
		pdf.set_xy(x_position, y_position+(count*25))
		pdf.cell(0, 0, f'{product_unit_price}')

	def print_product_total_price(count, x_position, y_position, product_total_price):
		pdf.set_font('Helvetica', 'B', 12)
		pdf.set_xy(x_position, y_position+(count*25))
		pdf.cell(0, 0, f'{product_total_price}')

	def print_discount_price(product_discount_price):
		pdf.set_font('Times', '', 20)
		pdf.set_xy(460, 688)
		pdf.cell(0, 0, f'{product_discount_price}')

	def print_all_product_subtotal_price(all_product_subtotal_price):
		pdf.set_font('Times', '', 20)
		pdf.set_xy(460, 713)
		pdf.cell(0, 0, f'{all_product_subtotal_price}')

	def print_all_product_tax_price(all_product_tax_price):
		pdf.set_font('Times', '', 20)
		pdf.set_xy(459, 737)
		pdf.cell(0, 0, f'{all_product_tax_price}')

	def print_all_product_total_price(all_product_total_price):
		pdf.set_font('Times', 'B', 26)
		pdf.set_xy(460, 765)
		pdf.cell(0, 0, f'{all_product_total_price}')

	def new_add_page():
		pdf.add_page('', '', True)
		path_file= resource_path_file('template_w_tax.png')
		pdf.image(path_file, 0, 0, 595, 842, 'PNG', '')

	count= 0
	product_price= 0
	pdf= FPDF('P', 'pt', 'A4')

	if product_details!= '':
		new_add_page()
		print_invoice_no(f'{product_details[0]}')
		print_invoice_date(f'{product_details[1]}')
		print_customer_name(product_details[2])
		print_customer_phone(f'+91 {product_details[3]}')
		product_detail= product_details[5:]

		for i in range(0, int(len(product_detail)/4)):
			if count== 19:
				print_all_product_subtotal_price(f'{product_price:.2f}')
				new_add_page()
				count= 0

			print_product_serial_number(count, 33, 205, i+1)
			print_product_name(count, 70, 205, f'{product_detail[i*4]} (Sn. {product_detail[(i*4)+1]})')
			print_product_quantity(count, 369, 205, product_detail[(i*4)+2])
			print_product_unit_price(count, 435, 205, product_detail[(i*4)+3])
			print_product_total_price(count, 505, 205, f'{float(product_detail[(i*4)+2]) * float(product_detail[(i*4)+3]):.2f}')
			product_price+= float(product_detail[(i*4)+2])* float(product_detail[(i*4)+3])
			count+= 1

		print_discount_price(f'{float(product_details[4]):.2f}')
		print_all_product_subtotal_price(f'{(float(product_price)- float(product_details[4])):.2f}')
		print_all_product_tax_price(f'{((float(product_price)- float(product_details[4]))* .18):.2f}')
		print_all_product_total_price(ceil(product_price- float(product_details[4])+ ((product_price- float(product_details[4]))* .18)))
		product_price= 0

	# In dev purpose below condition will off 
	if os.path.isfile(f'G:\\My Drive\\{product_details[0]}.pdf'):
		filenames= os.listdir()
		for filename in filenames:
			if filename != 'speedly.exe':
				os.remove(filename)
		pdf.output(f'{product_details[0]}.pdf', 'I')
		clear_all()

		# Print through the printer
		currentprinter= win32print.GetDefaultPrinter()
		win32print.SetDefaultPrinter(currentprinter)
		win32api.ShellExecute(0, 'print', f'{product_detail[0]}.pdf', None, '.', 0)
	else:
		pdf.output(f'G:\\My Drive\\{product_details[0]}.pdf', 'I')
		filenames= os.listdir()
		for filename in filenames:
			if filename!= 'speedly.exe':
				os.remove(filename)
		pdf.output(f'{product_details[0]}.pdf', 'I')
		clear_all()

		# Print Through the printer
		currentprinter= win32print.GetDefaultPrinter()
		win32print.SetDefaultPrinter(currentprinter)
		win32api.ShellExecute(0, 'print', f'{product_details[0]}.pdf', None, '.', 0)
	# pdf.output(f'G:\\My Drive\\{product_details[0]}.pdf', 'I')

def print_again():
	global allData_list
	makePDF(allData_list)

# ============================================================================================================================ #

# ==================== Define Some Validation Function ========================== #
def val_c_contact(input):
	if input.isdigit() and len(input)< 11:
		return True
	elif input== '':
		return True
	else:
		return False

def val_c_name(input):
	if input.istitle() and len(customer_name.get())< 51:
		return True
	elif input== '':
		return True
	else:
		return False

def val_inv_num(input):
	if input.isdigit() and len(input)< 11:
		return True
	elif input== '':
		return True
	else:
		return False

def val_p_name(input):
	regex= '^[a-zA-Z\s0-9]+$'
	if re.search(regex, input) and len(product_name.get())< 100:
		return True
	elif input== '':
		return True
	else:
		return False

def val_p_id(input):
	if input.isalnum():
		return True
	elif input== '':
		return True
	else:
		return False

def val_p_quan(input):
	if input.isdigit():
		return True
	elif input== '':
		return True
	else:
		return False

def val_p_u_price(input):
	regex= '^[0-9.]+$'
	if re.search(regex, input):
		return True
	elif input== '':
		return True
	else:
		return False

def val_d_price(input):
	regex= '^[0-9.]+$'
	if re.search(regex, input):
		return True
	elif input== '':
		return True
	else:
		return False


# ============================================================================= #
# Define product output function
def resource_path_ico(relative_path):
	try:
		base_path= sys._MEIPASS
	except Exception:
		base_path= os.path.abspath('.')
	return os.path.join(base_path, relative_path)

def product_output(product_list):
	global quantity, tax, price
	if product_list!= []:
		for i in range(0, int(len(product_list)/ 4)):
			quantity+= int(product_list[(i*4)+2])
			tax+= float((float(product_list[(i*4)+2])* float(product_list[(i*4)+3]))* .18)
			price+= float((float(product_list[(i*4)+2])* float(product_list[(i*4)+3]))+ ((float(product_list[(i*4)+2])* float(product_list[(i*4)+3]))* .18))

		total_quantity.set(f'{quantity}')
		total_tax.set(f'{tax:.2f}')
		total_price.set(f'{price:.2f}')

		quantity, tax, price= 0, 0, 0
	else:
		total_quantity.set('')
		total_tax.set('')
		total_price.set('')


# Search button function
def search():
	global allData_list
	if invoice_no.get()!= '':

		# Init the DB
		conn= sqlite3.connect('G:\\My Drive\\speedly.db')
		c= conn.cursor()
		allData_list= []
		product_total= 0

		# Find the customer name from DB
		c.execute(f"SELECT * FROM customer WHERE invoice_id = '{invoice_no.get()}'")
		customer_details= c.fetchone()
		if customer_details is not None:
			search_window= Toplevel(root)
			search_window.geometry('600x460')
			search_window.minsize(600, 460)
			search_window.maxsize(600, 460)
			path_ico= resource_path_ico('keys.ico')
			search_window.iconbitmap(path_ico)
			search_window.title('Customer Invoice Details')

			# Define Customer Detilas Frame
			search_customer_frame= LabelFrame(search_window, bd= 7, relief= GROOVE)
			search_customer_frame.place(x= 5, y= 10, width= 592)
			for i in range(0, len(customer_details)):
				allData_list.append(customer_details[i])

			# Find all product from DB
			c.execute(f'SELECT * FROM invoice WHERE invoice_id= {invoice_no.get()}')
			all_product= c.fetchall()

			for i in range(0, len(all_product)):
				for j in range(1, 5):
					allData_list.append(all_product[i][j])
				product_total+= all_product[i][3]* all_product[i][4]

			# Customer Name Fiels
			search_customer_name_label= Label(search_customer_frame, text= 'Name:', font= ('Times New Roman', 14, 'bold'), fg= '#ee2020').grid(row= 0, column= 0)
			search_customer_name_entry= Label(search_customer_frame, text= f'{allData_list[2]}', font= ('Times New Roman', 12, 'bold'), fg='#000000').grid(row= 0, column= 1)

			# Customer contact number field
			search_customer_number_label= Label(search_customer_frame, text= 'Phone:', font= ('Times New Roman', 14, 'bold'), fg= '#ee2020').grid(row= 0, column= 2)
			search_customer_number_entry= Label(search_customer_frame, text= f'{allData_list[3]}', font= ('Times New Roman', 12, 'bold'), fg='#000000').grid(row= 0, column= 3)

			# Invoice Number Field
			search_invoice_number_label= Label(search_customer_frame, text= 'Invoice Number:', font= ('Times New Roman', 14, 'bold'), fg= '#ee2020').grid(row= 1, column= 0)
			search_invoice_number_entry= Label(search_customer_frame, text= f'{allData_list[0]}', font= ('Times New Roman', 12, 'bold'), fg='#000000').grid(row= 1, column= 1)

			# Invoice Date Field
			search_invoice_date_label= Label(search_customer_frame, text= 'Invoice Date:', font= ('Times New Roman', 14, 'bold'), fg= '#ee2020').grid(row= 1, column= 2)
			search_invoice_date_entry= Label(search_customer_frame, text= f'{allData_list[1]}', font= ('Times New Roman', 12, 'bold'), fg='#000000').grid(row= 1, column= 3)

			# Discount Amount Field
			search_discount_label= Label(search_customer_frame, text= 'Discount:', font= ('Times New Roman', 14, 'bold'), fg= '#ee2020').grid(row= 2, column= 0)
			search_discount_entry= Label(search_customer_frame, text= f'₹ {allData_list[4]:.2f}', font= ('Times New Roman', 12, 'bold'), fg='#000000').grid(row= 2, column= 1)

			# Subtotal Amount Field
			search_subtotal_label= Label(search_customer_frame, text= 'Subtotal:', font= ('Times New Roman', 14, 'bold'), fg= '#ee2020').grid(row= 2, column= 2)
			search_subtotal_entry= Label(search_customer_frame, text= f'₹ {float(product_total- allData_list[4]):.2f}', font= ('Times New Roman', 12, 'bold'), fg='#000000').grid(row= 2, column= 3)

			# Tax Amount Field
			search_tax_label= Label(search_customer_frame, text= 'Tax:', font= ('Times New Roman', 14, 'bold'), fg= '#ee2020').grid(row= 3, column= 0)
			search_tax_entry= Label(search_customer_frame, text= f'₹ {(float(product_total- allData_list[4])* .18):.2f}', font= ('Times New Roman', 12, 'bold'), fg='#000000').grid(row= 3, column= 1)

			# Total Amount Field
			search_total_label= Label(search_customer_frame, text= 'Total(R.O):', font= ('Times New Roman', 14, 'bold'), fg= '#ee2020').grid(row= 3, column= 2)
			search_total_entry= Label(search_customer_frame, text= f'₹ {ceil(float(product_total- allData_list[4])+ (float(product_total- allData_list[4])* .18))}', font= ('Times New Roman', 12, 'bold'), fg='#000000').grid(row= 3, column= 3)

			# Define Table View
			search_table_frame= LabelFrame(search_window, bd= 7, relief= GROOVE)
			search_table_frame.place(x= 5, y= 140, width= 592, height= 255)

			customer_table= ttk.Treeview(search_table_frame)
			table_style= ttk.Style()
			table_style.theme_use('clam')
			customer_table['columns']= ('cl_1', 'cl_2', 'cl_3', 'cl_4', 'cl_5', 'cl_6')

			customer_table.column('#0', width= 0, stretch= NO)
			customer_table.column('cl_1',anchor= CENTER, width= 30)
			customer_table.column('cl_2', anchor= CENTER, width= 200)
			customer_table.column('cl_3', anchor= CENTER, width= 120)
			customer_table.column('cl_4', anchor= CENTER, width= 50)
			customer_table.column('cl_5', anchor= CENTER, width= 80)
			customer_table.column('cl_6', anchor= CENTER, width= 80)

			customer_table.heading('#0', text= '')
			customer_table.heading('cl_1', text= 'Sl.', anchor= CENTER)
			customer_table.heading('cl_2', text= 'Product Name', anchor= CENTER)
			customer_table.heading('cl_3', text= 'ID', anchor= CENTER)
			customer_table.heading('cl_4', text= 'Qn.', anchor= CENTER)
			customer_table.heading('cl_5', text= 'Unit Price', anchor= CENTER)
			customer_table.heading('cl_6', text= 'Total', anchor= CENTER)

			product_display_list= allData_list[5:]
			for i in range(0, int(len(product_display_list)/4)):
				customer_table.insert(parent= '', index= 'end', iid= f'{i+1}', values= (f'{i+1}', f'{product_display_list[i*4]}', f'{product_display_list[(i*4)+1]}', f'{product_display_list[(i*4)+2]}', f'{product_display_list[(i*4)+3]:.2f}', f'{(float(product_display_list[(i*4)+2])* float(product_display_list[(i*4)+3])):.2f}'))
			customer_table.pack(pady= 5)

			# Button Function
			search_button_area= LabelFrame(search_window)
			search_button_area.place(x= 250, y= 400)
			# Print Again Button
			search_print_again= Button(search_button_area, command= print_again, text= 'Print Again', font= ('Times New Roman', 14, 'bold'), fg= '#ffffff', bg= '#781010', bd= 5).pack()

		if customer_details is None:
			tmsg.showerror('ERROR!', 'No Record Found')

	if invoice_no.get()== '':
		tmsg.showerror('ERROR!', 'Please Enter Invoice Number')


# Product Clear Fom Text Field
def product_clear():
	global product_list
	product_list= product_list[:-3]
	product_output(product_list)
	billTextArea.delete(str(float(billTextArea.index(END))- 5.0), END)

# Add button function
def product_add():
	global response
	if customer_name.get()!= '' and customer_phone.get()!= '':
		if product_name.get()!= '' and product_id.get()!= '' and product_quantity.get()!= '' and product_unit_price.get()!= '':
			billTextArea.insert(END, f' Name:\t\t{product_name.get()}')
			billTextArea.insert(END, f'\n Quantity:\t\t{product_quantity.get()}')
			billTextArea.insert(END, f'\n Price (each):\t\t{product_unit_price.get()}')
			billTextArea.insert(END, '\n----------------------------------------------------------\n')

			product_list.append(str(product_name.get()))
			product_list.append(str(product_id.get()))
			product_list.append(str(product_quantity.get()))
			product_list.append(str(product_unit_price.get()))
			product_output(product_list)

			product_name.set('')
			product_id.set('')
			product_quantity.set('')
			product_unit_price.set('')
		else:
			tmsg.showerror('ERROR!', 'No Product Found')
	else:
		tmsg.showerror('ERROR!', 'Customer Name & Phone Number Is Empty')


# Call Print and database file function
def invoice_print():
	global product_list
	if customer_name.get()!= '' and customer_phone.get()!= '':
		if product_name.get()== '' and product_id.get()== '' and product_quantity.get()== '' and product_unit_price.get()== '' and total_quantity.get!= '' and total_tax.get()!= '' and total_price.get()!= '':
			if discount_price.get()!= '':
				product_list= [str(customer_name.get())]+ [str(customer_phone.get())]+ [str(discount_price.get())]+ product_list
				productDB(product_list)
				product_list= []
			elif discount_price.get()== '':
				product_list= [str(customer_name.get())]+ [str(customer_phone.get())]+ ['0']+ product_list
				productDB(product_list)
				product_list= []
		else:
			tmsg.showerror('Confirm!', 'Please Press Add Button To Confirm')
	else:
		tmsg.showerror('ERROR!', 'Customer Name & Phone Is Empty')

# Clear all the text field
def clear_all():
	global quantity, tax, price, product_list
	customer_name.set('')
	customer_phone.set('')
	invoice_no.set('')

	product_name.set('')
	product_id.set('')
	product_quantity.set('')
	product_unit_price.set('')

	total_quantity.set('')
	total_tax.set('')
	total_price.set('')
	discount_price.set('')

	billTextArea.delete('1.0', END)

	product_list= []
	quantity, tax, price= 0, 0, 0

def customer_details():
	if not os.path.exists('G:\\My Drive\\speedly.db'):
		tmsg.showerror('ERROR!', 'No Details Found')
	else:
		details_window= Toplevel(root)
		details_window.geometry('538x360')
		details_window.minsize(538, 360)
		details_window.maxsize(538, 360)
		path_ico= resource_path_ico('keys.ico')
		details_window.iconbitmap(path_ico)
		details_window.title('Customer Details Panel')

		details_table_frame= LabelFrame(details_window, bd= 7, relief= GROOVE)
		details_table_frame.place(x= 2, y= 5, width= 534, height= 250)

		customer_details_table= ttk.Treeview(details_table_frame)
		table_style= ttk.Style()
		table_style.theme_use('clam')
		customer_details_table['columns']= ('cl_1', 'cl_2', 'cl_3', 'cl_4')

		customer_details_table.column('#0', width= 0, stretch= NO)
		customer_details_table.column('cl_1', anchor= CENTER, width= 100)
		customer_details_table.column('cl_2', anchor= CENTER, width= 200)
		customer_details_table.column('cl_3', anchor= CENTER, width= 100)
		customer_details_table.column('cl_4', anchor= CENTER, width= 100)

		customer_details_table.heading('#0', text= '')
		customer_details_table.heading('cl_1', text='Invoice ID', anchor= CENTER)
		customer_details_table.heading('cl_2', text= 'Name', anchor= CENTER)
		customer_details_table.heading('cl_3', text= 'Phone', anchor= CENTER)
		customer_details_table.heading('cl_4', text= 'Date', anchor= CENTER)

		conn= sqlite3.connect('G:\\My Drive\\speedly.db')
		c= conn.cursor()
		c.execute('SELECT * FROM customer')
		customer_details= c.fetchall()
		total_invoice= len(customer_details)

		for i in range(0, len(customer_details)):
			customer_details_table.insert(parent= '', index= 'end', iid= f'{i}', values= (f'{customer_details[i][0]}', f'{customer_details[i][2]}', f'{customer_details[i][3]}', f'{customer_details[i][1]}'))
		customer_details_table.pack(padx= 2, pady= 2)

		customer_details_count_frame= LabelFrame(details_window, bd= 7, relief= GROOVE)
		customer_details_count_frame.place(x= 2, y= 255, height= 100, width= 534)

		c.execute('SELECT COUNT(DISTINCT customer_phone), COUNT(DISTINCT customer_name) from customer')
		uphone= c.fetchall()

		customer_phone_count_label= Label(customer_details_count_frame, text= 'Total Unique Customer(Phone):', font= ('Times New Roman', 14, 'bold'), fg= '#ee2020').grid(row= 0, column= 0)
		customer_phone_count_entry= Label(customer_details_count_frame, text= f'{uphone[0][0]}', font= ('Times New Roman', 12, 'bold'), fg='#000000').grid(row= 0, column= 1)

		customer_name_count_label= Label(customer_details_count_frame, text= 'Total Unique Customer(Name):', font= ('Times New Roman', 14, 'bold'), fg= '#ee2020').grid(row= 1, column= 0)
		customer_name_count_entry= Label(customer_details_count_frame, text= f'{uphone[0][1]}', font= ('Times New Roman', 12, 'bold'), fg='#000000').grid(row= 1, column= 1)

		total_invoice_count= Label(customer_details_count_frame, text= 'Total Invoice Generate:', font= ('Times New Roman', 14, 'bold'), fg= '#ee2020').grid(row= 2, column= 0)
		total_invoice_count= Label(customer_details_count_frame, text= f'{total_invoice}', font= ('Times New Roman', 12, 'bold'), fg='#000000').grid(row= 2, column= 1)
		total_invoice= 0


def sells_details():
	if not os.path.exists('G:\\My Drive\\speedly.db'):
		tmsg.showerror('ERROR!', 'No Details Found')
	else:
		invoice_quantity= 0
		invoice_total= 0

		discount= 0
		tax= 0
		total= 0
		sells_window= Toplevel(root)
		sells_window.geometry('538x360')
		sells_window.minsize(538, 360)
		sells_window.maxsize(538, 360)
		path_ico= resource_path_ico('keys.ico')
		sells_window.iconbitmap(path_ico)
		sells_window.title('Business Details Panel')

		sells_table_frame= LabelFrame(sells_window, bd= 7, relief= GROOVE)
		sells_table_frame.place(x= 2, y= 5, width= 534, height= 250)

		sells_details_table= ttk.Treeview(sells_table_frame)
		table_style= ttk.Style()
		table_style.theme_use('clam')
		sells_details_table['columns']= ('cl_1', 'cl_2', 'cl_3', 'cl_4', 'cl_5')

		sells_details_table.column('#0', width= 0, stretch= NO)
		sells_details_table.column('cl_1', anchor= CENTER, width= 100)
		sells_details_table.column('cl_2', anchor= CENTER, width= 100)
		sells_details_table.column('cl_3', anchor= CENTER, width= 100)
		sells_details_table.column('cl_4', anchor= CENTER, width= 100)
		sells_details_table.column('cl_5', anchor= CENTER, width= 100)

		sells_details_table.heading('#0', text= '')
		sells_details_table.heading('cl_1', text='Invoice ID', anchor= CENTER)
		sells_details_table.heading('cl_2', text= 'Quantity', anchor= CENTER)
		sells_details_table.heading('cl_3', text= 'Discount', anchor= CENTER)
		sells_details_table.heading('cl_4', text= 'Tax', anchor= CENTER)
		sells_details_table.heading('cl_5', text= 'Total', anchor= CENTER)

		conn= sqlite3.connect('G:\\My Drive\\speedly.db')
		c= conn.cursor()
		c.execute('SELECT * FROM customer')
		customer_details= c.fetchall()

		for i in range(0, len(customer_details)):
			c.execute(f'SELECT * FROM invoice WHERE invoice_id= {customer_details[i][0]}')
			product_details= c.fetchall()

			for j in range(0, len(product_details)):
				invoice_quantity+= int(product_details[j][3])
				invoice_total+=  (int(product_details[j][3])* float(product_details[j][4]))

			sells_details_table.insert(parent= '', index= 'end', iid= f'{i}', values= (f'{customer_details[i][0]}', f'{invoice_quantity}', f'{customer_details[i][4]:.2f}', f'{((invoice_total- customer_details[i][4]) *.18):.2f}', f'{((invoice_total- customer_details[i][4])+ ((invoice_total- customer_details[i][4]) *.18)):.2f}'))

			total+= float((invoice_total- customer_details[i][4])+ ((invoice_total- customer_details[i][4]) *.18))
			tax+= float((invoice_total- customer_details[i][4]) *.18)
			discount+= float(customer_details[i][4])

			invoice_quantity= 0
			invoice_total= 0

		sells_details_table.pack(padx= 2, pady= 2)

		sells_count_frame= LabelFrame(sells_window, bd= 7, relief= GROOVE)
		sells_count_frame.place(x= 2, y= 255, height= 100, width= 534)

		sells_discount_count_label= Label(sells_count_frame, text= 'Total Discount Given:', font= ('Times New Roman', 14, 'bold'), fg= '#ee2020').grid(row= 0, column= 0)
		sells_discount_count_entry= Label(sells_count_frame, text= f'{discount:.2f}', font= ('Times New Roman', 12, 'bold'), fg='#000000').grid(row= 0, column= 1)

		sells_tax_count_label= Label(sells_count_frame, text= 'Total Tax Amount:', font= ('Times New Roman', 14, 'bold'), fg= '#ee2020').grid(row= 2, column= 0)
		sells_tax_count_entry= Label(sells_count_frame, text= f'{tax:.2f}', font= ('Times New Roman', 12, 'bold'), fg='#000000').grid(row= 2, column= 1)

		sells_total_count_label= Label(sells_count_frame, text= 'Total Sells Amount:', font= ('Times New Roman', 14, 'bold'), fg= '#ee2020').grid(row= 3, column= 0)
		sells_total_count_entry= Label(sells_count_frame, text= f'{total:.2f}', font= ('Times New Roman', 12, 'bold'), fg='#000000').grid(row= 3, column= 1)



# Intializing the TK
root= Tk()
path_ico= resource_path_ico('keys.ico')
root.iconbitmap(path_ico)
root.geometry('1280x720')
root.minsize(1280, 720)
root.maxsize(1280, 720)
root.title('Made With Love by SOUMALYA')

# =================== Declare some variables ================================== #
# Customer details variable
customer_name= StringVar()
customer_phone= StringVar()
invoice_no= StringVar()

# Product detials variable
product_name= StringVar()
product_id= StringVar()
product_quantity= StringVar()
product_unit_price= StringVar()

# Bill output variable
total_quantity= StringVar()
total_tax= StringVar()
total_price= StringVar()
discount_price= StringVar()

# Declare some variable
product_list= []
tax= 0
quantity= 0
price= 0

# ===================================================================== Menubar Config ======================================================================= #
application_menu= Menu(root)
root.config(menu= application_menu)

details_menu= Menu(application_menu, tearoff= 0)
application_menu.add_cascade(label= 'All Details', menu= details_menu)
details_menu.add_command(label= 'Customer Panel', command= customer_details)
details_menu.add_separator()
details_menu.add_command(label= 'Business Panel', command= sells_details)

# =========================== Making Window Widget ============================ #
# Define Main Window With Title
title= Label(root, text= 'Speedly Electronics', font= ('Times New Roman', 30, 'bold'), bd= 10, relief= SUNKEN, bg= '#c0efff', fg= '#000000').pack(fill= X)

# Define Customer Detilas Frame
customer_frame= LabelFrame(root, text= 'Customer Details', font= ('Times New Roman', 15, 'bold'), bg= '#c0efff', fg= '#000000', bd= 7, relief= GROOVE)
customer_frame.place(x= 0, y= 69, relwidth= 1)

# Define customer name
customer_name_label= Label(customer_frame, text= 'Customer Name:', font= ('Times New Roman', 18, 'bold'), bg= '#c0efff', fg= '#000000').grid(row= 0, column= 0, padx= 10, pady= 15)
customer_name_entry= Entry(customer_frame, textvariable= customer_name, width= 20, font= ('Arial', 14), bd= 5, relief= SUNKEN)
validaton_customer_name= root.register(val_c_name)
customer_name_entry.config(validate= 'key', validatecommand= (validaton_customer_name, '%P'))
customer_name_entry.grid(row= 0, column= 1, padx= 10, pady= 15)

# Define customer phone
customer_contact_label= Label(customer_frame, text= 'Phone:', font= ('Times New Roman', 18, 'bold'), bg= '#c0efff', fg= '#000000').grid(row= 0, column= 2, padx= 10, pady= 15)
customer_contact_entry= Entry(customer_frame, textvariable= customer_phone, width= 20, font= ('Arial', 14), bd= 5, relief= SUNKEN)
validation_customer_contact= root.register(val_c_contact)
customer_contact_entry.config(validate= 'key', validatecommand= (validation_customer_contact, '%P'))
customer_contact_entry.grid(row= 0, column= 3, padx= 10, pady= 15)

# Define invoice number
invoice_number_label= Label(customer_frame, text= 'Invoice Num:', font= ('Times New Roman', 18, 'bold'), bg= '#c0efff', fg= '#000000').grid(row= 0, column= 4, padx= 10, pady= 15)
invoice_number_entry= Entry(customer_frame, textvariable= invoice_no, width= 15, font=('Arial', 14), bd= 5, relief= SUNKEN)
validation_invoice_number= root.register(val_inv_num)
invoice_number_entry.config(validate= 'key', validatecommand= (validation_invoice_number, '%P'))
invoice_number_entry.grid(row= 0, column= 5, padx= 10, pady= 15)

# Define search button
invoice_search= Button(customer_frame, command= search, text= 'Search', width= 8, font= ('Arial', 12, 'bold'), bd= 5, bg= '#0a6600', fg= '#ffffff').grid(row= 0, column= 6, padx= 2, pady= 15)



# Define Product Detials Entry Frame
product_frame= LabelFrame(root, text= 'Product Details', font= ('Times New Roman', 15, 'bold'), bg= '#c0efff', fg= '#000000', bd= 5, relief= SUNKEN)
product_frame.place(x= 0, y= 170, width= 400, height= 350)

# Define product name
product_name_label= Label(product_frame, text= 'Product Name:', font= ('Times New Roman', 15, 'bold'), bg= '#c0efff', fg= '#000000').grid(row= 0, column= 0, padx= 10, pady= 15, sticky= 'w')
product_name_entry= Entry(product_frame, textvariable= product_name, font= ('Times New Roman', 15, 'bold'), bd= 5, relief= SUNKEN)
validation_product_name= root.register(val_p_name)
product_name_entry.config(validate= 'key', validatecommand= (validation_product_name, '%P'))
product_name_entry.grid(row= 0, column= 1, padx= 10, pady= 15)

# Define product id
product_id_label= Label(product_frame, text= 'Product ID:', font= ('Times New Roman', 15, 'bold'), bg= '#c0efff', fg= '#000000').grid(row= 1, column= 0, padx= 10, pady= 15, sticky= 'w')
product_id_entry= Entry(product_frame, textvariable= product_id, font= ('Times New Roman', 15, 'bold'), bd= 5, relief= SUNKEN)
validation_product_id= root.register(val_p_id)
product_id_entry.config(validate= 'key', validatecommand= (validation_product_id, '%P'))
product_id_entry.grid(row= 1, column= 1, padx= 10, pady= 15)

# Define product quantity
product_quantity_label= Label(product_frame, text= 'Quantity:', font= ('Times New Roman', 15, 'bold'), bg= '#c0efff', fg= '#000000').grid(row= 2, column= 0, padx= 10, pady= 15, sticky= 'w')
product_quantity_entry= Entry(product_frame, textvariable= product_quantity, font= ('Times New Roman', 15, 'bold'), bd= 5, relief= SUNKEN)
validation_product_quantity= root.register(val_p_quan)
product_quantity_entry.config(validate= 'key', validatecommand= (validation_product_quantity, '%P'))
product_quantity_entry.grid(row= 2, column= 1, padx= 10, pady= 15)

# Define product unit price
product_unit_price_label= Label(product_frame, text= 'Unit Price:', font= ('Times New Roman', 15, 'bold'), bg= '#c0efff', fg= '#000000').grid(row= 3, column= 0, padx= 10, pady= 15, sticky= 'w')
product_unit_price_entry= Entry(product_frame, textvariable= product_unit_price, font= ('Times New Roman', 15, 'bold'), bd= 5, relief= SUNKEN)
validation_product_unit_price= root.register(val_p_u_price)
product_unit_price_entry.config(validate= 'key', validatecommand= (validation_product_unit_price, '%P'))
product_unit_price_entry.grid(row= 3, column= 1, padx= 10, pady= 15)

# Define product clear button
product_clear_button= Button(product_frame, command= product_clear, text= 'Clear', width= 8, font= ('Arial', 12, 'bold'), bd= 5, bg= '#7b7a16', fg= '#ffffff').grid(row= 4, column= 0, padx= 2, pady= 5)

# Define product add button
product_add_button= Button(product_frame, command= product_add, text= 'Add', width= 8, font= ('Arial', 12, 'bold'), bd= 5, bg= '#0a6600', fg= '#ffffff').grid(row= 4, column= 1, padx= 2, pady= 5)


# Define billing details output frame
output_frame= LabelFrame(root, text= 'Bill Calculation', font= ('Times New Roman', 15, 'bold'), bg= '#c0efff', fg= '#000000', bd= 5, relief= SUNKEN)
output_frame.place(x= 405, y= 170, width= 410, height= 350)


# Define total quantity
total_quantity_label= Label(output_frame, text= 'Total Quantity:', font=('Times New Roman', 15, 'bold'), bg= '#c0efff', fg= '#000000').grid(row= 1, column= 0, padx= 10, pady= 15, sticky= 'w')
total_quantity_entry= Entry(output_frame, textvariable= total_quantity, state= DISABLED, justify= 'center', font= ('Times New Roman', 15, 'bold'), disabledforeground= '#ff0000', bd= 5, relief= SUNKEN).grid(row= 1, column= 1, padx= 10, pady= 15)

# Define total tax
total_tax_label= Label(output_frame, text= 'Total Tax(18%):', font=('Times New Roman', 15, 'bold'), bg= '#c0efff', fg= '#000000').grid(row= 2, column= 0, padx= 10, pady= 15, sticky= 'w')
total_tax_entry= Entry(output_frame, textvariable= total_tax, state= DISABLED, justify= 'center', font= ('Times New Roman', 15, 'bold'), disabledforeground= '#ff0000', bd= 5, relief= SUNKEN).grid(row= 2, column= 1, padx= 10, pady= 15)

# Define total price
total_price_label= Label(output_frame, text= 'Total Price:', font=('Times New Roman', 15, 'bold'), bg= '#c0efff', fg= '#000000').grid(row= 3, column= 0, padx= 10, pady= 15, sticky= 'w')
total_price_entry= Entry(output_frame, textvariable= total_price, state= DISABLED, justify= 'center', font= ('Times New Roman', 15, 'bold'), disabledforeground= '#ff0000', bd= 5, relief= SUNKEN).grid(row= 3, column= 1, padx= 10, pady= 15)

# Define discount button
discount_price_label= Label(output_frame, text= 'Discount:', font=('Times New Roman', 15, 'bold'), bg= '#c0efff', fg= '#000000').grid(row= 4, column= 0, padx= 10, pady= 15, sticky= 'w')
discount_price_entry= Entry(output_frame, textvariable= discount_price, font= ('Times New Roman', 15, 'bold'), bd= 5, relief= SUNKEN)
validation_discount_price= root.register(val_d_price)
discount_price_entry.config(validate= 'key', validatecommand= (validation_discount_price, '%P'))
discount_price_entry.grid(row= 4, column= 1, padx= 10, pady= 15)

# Define print button
print_button= Button(output_frame, command= invoice_print, text= 'Print', width= 8, font= ('Arial', 12, 'bold'), bd= 5, bg= '#781010', fg= '#ffffff').grid(row= 5, column= 0, padx= 2, pady= 5)

# Define clear all field button
product_clear_all_button= Button(output_frame, command= clear_all, text= 'Clear All', width= 8, font= ('Arial', 12, 'bold'), bd= 5, bg= '#0b0aff', fg= '#ffffff').grid(row= 5, column= 1, padx= 2, pady= 5)

# Define Search Show
product_show_frame= LabelFrame(root, text= 'Customer Details (Maybe Later)', font= ('Times New Roman', 15, 'bold'), bg= '#c0efff', fg= '#000000', bd= 5, relief= SUNKEN)
product_show_frame.place(x= 0, y= 520, height= 200, width= 815)


# Define bill text area
bill_area= Frame(root, bd= 10, relief= GROOVE)
bill_area.place(x= 820, y= 170, width= 450, height= 550)
bill_area_title= Label(bill_area, text= 'Products List', font= ('Arials', 15, 'bold'), bd= 7, relief= GROOVE).pack(fill= X)
bill_area_scrollY= Scrollbar(bill_area, orient= VERTICAL)
billTextArea= Text(bill_area, font= ('Times New Roman', 15, 'bold'), yscrollcommand= bill_area_scrollY.set)
bill_area_scrollY.pack(side= RIGHT, fill= Y)
bill_area_scrollY.config(comman= billTextArea.yview)
billTextArea.pack(fill= BOTH, expand= 1)

# Define Tkinter Mainloop Function
root.mainloop()