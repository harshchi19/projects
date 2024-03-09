import tkinter as tk
from tkinter import messagebox
import mysql.connector
from pathlib import Path
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import *
from tkinter import ttk, simpledialog, filedialog
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

conn = mysql.connector.connect(user='root', password='root', host='localhost', database='logi')
cursor = conn.cursor()

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r'C:\Users\bhave\Desktop\assests')


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


# Create object
root = Tk()

# Adjust size
root.geometry("1035x590")

# Add image file
bg = PhotoImage(file=r'C:\Users\bhave\Downloads\dbms.png')

# Create Canvas
canvas1 = Canvas(root, width=900, height=800)

canvas1.pack(fill="both")

# Display image
canvas1.create_image(0, 0, image=bg, anchor="nw")
root.resizable(0, 0)

def call_next():
    root.destroy()
    #root.update()
    obj=Page1(root)


button_image_1 = PhotoImage(
    file=relative_to_assets("button_1.png"))
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=call_next
)

button_1.place(
    x=660,
    y=460,
    width=200,
    height=40
)

root.mainloop()

def connect_to_database():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='logi'
    )
    return connection

def create_table():
    try:
        connection = connect_to_database()
        cursor = connection.cursor()

        # MySQL Workbench code to create the table
        create_table_query = '''
            CREATE TABLE IF NOT EXISTS user1 (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                phoneno VARCHAR(20) NOT NULL,
                email VARCHAR(255) NOT NULL,
                age INT NOT NULL
            );
        '''
        cursor.execute(create_table_query)
        connection.commit()

    except mysql.connector.Error as error:
        messagebox.showerror('Error', str(error))
    finally:
        try:
            if connection.is_connected():
                cursor.close()
                connection.close()
        except UnboundLocalError:
            pass  # connection was not established, no need to close

def submit():
    try:
        connection = connect_to_database()
        cursor = connection.cursor()

        # Retrieve the input values
        name = entry_name.get()
        email = entry_email.get()
        phone_number = entry_phone_number.get()
        age = entry_age.get()

        # Validate the inputs
        if name == '' or email == '' or phone_number == '' or age == '':
            messagebox.showerror('Error', 'All fields are required')
            return

        # Save the customer details to the database
        cursor.execute("INSERT INTO user1 (username, phoneno, email, age) VALUES (%s, %s, %s, %s)",
                       (name, phone_number, email, age))
        connection.commit()

        # Clear the input fields
        entry_name.delete(0, tk.END)
        entry_email.delete(0, tk.END)
        entry_phone_number.delete(0, tk.END)
        entry_age.delete(0, tk.END)

        # Show a success message
        messagebox.showinfo('Success', 'Customer details saved successfully')

        # Instead of destroying the window, go to the next step in the multi-step form
        root.steps[root.current_step].show_next_step()

    except mysql.connector.Error as error:
        messagebox.showerror('Error', str(error))
    finally:
        try:
            if connection.is_connected():
                cursor.close()
                connection.close()
        except UnboundLocalError:
            pass  # connection was not established, no need to close


# Create the main window
root = tk.Tk()
root.title('Customer Details')

# Set the window size and position
window_width = 400
window_height = 300
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_coordinate = (screen_width / 2) - (window_width / 2)
y_coordinate = (screen_height / 2) - (window_height / 2)
root.geometry(f'{window_width}x{window_height}+{int(x_coordinate)}+{int(y_coordinate)}')

# Set a background color
root.configure(bg='#E1E1E1')

# Create a frame for better organization
frame = tk.Frame(root, bg='#E1E1E1')
frame.pack(padx=20, pady=20, fill='both', expand=True)

# Create the input fields with labels
label_n1 = tk.Label(frame, text='Customer Details', font=('Helvetica', 16, 'bold'), bg='#E1E1E1')
label_n1.pack(pady=(0, 10))

label_name = tk.Label(frame, text='Name:', bg='#E1E1E1')
label_name.pack(anchor='w')
entry_name = tk.Entry(frame)
entry_name.pack(pady=(0, 10))

label_email = tk.Label(frame, text='Email:', bg='#E1E1E1')
label_email.pack(anchor='w')
entry_email = tk.Entry(frame)
entry_email.pack(pady=(0, 10))

label_phone_number = tk.Label(frame, text='Phone Number:', bg='#E1E1E1')
label_phone_number.pack(anchor='w')
entry_phone_number = tk.Entry(frame)
entry_phone_number.pack(pady=(0, 10))

label_age = tk.Label(frame, text='Age:', bg='#E1E1E1')
label_age.pack(anchor='w')
entry_age = tk.Entry(frame)
entry_age.pack(pady=(0, 10))

# Create the submit button
button_submit = tk.Button(frame, text='Submit', command=submit, bg='#4CAF50', fg='white')
button_submit.pack()

# Call the function to create the table
create_table()

# Start the main loop
root.mainloop()


class MultiStepForm(tk.Tk):
    def __init__(self, data_from_code1=None):
        super().__init__()
        self.title("Parking Form")

        self.current_step = 0
        self.steps = [
            Page1(self, data_from_code1 if data_from_code1 else {}),
            Page2(self),
            Page3(self),
            Page4(self),
            OnlinePaymentPage(self, data_from_previous_pages={}),
            SummaryPage(self, data_from_previous_pages={})

        ]

        data_from_previous_pages = {}
        for step in self.steps:
            data_from_previous_pages.update(step.get_data())

        total_amount_from_page4 = data_from_previous_pages.get("Total Amount", 0)
        self.steps[-2] = OnlinePaymentPage(self, total_amount=total_amount_from_page4,
                                           data_from_previous_pages=data_from_previous_pages)
        self.steps[-1] = SummaryPage(self, data_from_previous_pages=data_from_previous_pages)
        self.current_step = 0
        self.steps[self.current_step].pack()
        self.prev_button = ttk.Button(self, text="Previous", command=self.prev_step)
        self.prev_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.next_button = ttk.Button(self, text="Next", command=self.next_step)
        self.next_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.nav_frame = ttk.Frame(self)
        self.nav_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.nav_buttons = []
        for i, step in enumerate(self.steps[:3]):
            button = ttk.Button(self.nav_frame, text=f"Step {i + 1}", command=lambda i=i: self.show_step(i))
            button.grid(row=0, column=i, padx=5, pady=5)
            self.nav_buttons.append(button)

        self.animation_speed = 200
        self.transitioning = False

        self.style = ttk.Style()
        self.style.configure('TButton.Green.TButton', background='green')
        self.style.configure('TButton.Red.TButton', background='red')

        self.update_buttons()

    def next_step(self):
        if not self.transitioning and self.current_step < len(self.steps) - 1:
            #self.transitioning
            self.transitioning = True
            self.animate_button(self.next_button, 'Green')
            self.after(self.animation_speed, self.show_next_step)

    def show_next_step(self):
        self.animate_button(self.next_button, 'SystemButtonFace')

        if isinstance(self.steps[self.current_step], Page3):
            data_from_previous_pages = {}
            for step in self.steps[:self.current_step + 1]:
                data_from_previous_pages.update(step.get_data())
            self.steps[self.current_step + 1] = Page4(self, data_from_previous_pages)
        if isinstance(self.steps[self.current_step], OnlinePaymentPage):
            data_from_previous_pages = {}
            for step in self.steps[:self.current_step + 1]:
                data_from_previous_pages.update(step.get_data())
            self.steps[self.current_step + 1] = SummaryPage(self, data_from_previous_pages)

        self.steps[self.current_step].pack_forget()
        self.current_step += 1
        self.steps[self.current_step].pack()
        self.update_buttons()
        self.transitioning = False

    def prev_step(self):
        if not self.transitioning and self.current_step > 0:
            self.transitioning = True
            self.animate_button(self.prev_button, 'Red')
            self.after(self.animation_speed, self.show_prev_step)

    def show_prev_step(self):
        self.animate_button(self.prev_button, 'SystemButtonFace')
        self.steps[self.current_step].pack_forget()
        self.current_step -= 1
        self.steps[self.current_step].pack()
        self.update_buttons()
        self.transitioning = False

    def show_step(self, step_index):
        if not self.transitioning and 0 <= step_index < len(self.steps):
            self.transitioning = True
            self.animate_button(self.nav_buttons[step_index], 'Green')
            self.after(self.animation_speed, lambda: self.show_selected_step(step_index))

    def show_selected_step(self, step_index):
        self.animate_button(self.nav_buttons[step_index], 'SystemButtonFace')

        if isinstance(self.steps[self.current_step], Page3):
            data_from_previous_pages = {}
            for step in self.steps[:self.current_step + 1]:
                data_from_previous_pages.update(step.get_data())
            self.steps[self.current_step] = Page4(self, data_from_previous_pages)

        self.steps[self.current_step].pack_forget()
        self.current_step = step_index
        self.steps[self.current_step].pack()
        self.update_buttons()
        self.transitioning = False

    def animate_button(self, button, color):
        style_name = f'TButton.{color}.TButton'
        button.configure(style=style_name)
        self.after(self.animation_speed, lambda: button.configure(style='TButton'))

    def update_buttons(self):
        self.prev_button["state"] = "normal" if self.current_step > 0 else "disabled"
        self.next_button["state"] = "normal" if self.current_step < len(self.steps) - 1 else "disabled"

        for i, button in enumerate(self.nav_buttons):
            button.state(["!disabled"]) if i != self.current_step else button.state(["disabled"])

        if self.current_step == len(self.steps) - 1:
            self.next_button["text"] = "Submit"
            self.next_button["command"] = self.submit_form
            self.next_button["state"] = "normal"
        else:
            self.next_button["text"] = "Next"
            self.next_button["command"] = self.next_step

    def submit_form(self):
        data = {}
        for step in self.steps:
            data.update(step.get_data())

        total_amount = data.get("Total Amount", 0)
        payment_method = data.get("Payment Method", "")

        if total_amount > 2000 and payment_method == "Cash":
            messagebox.showinfo("Payment Method Error", "Payment should be done using the online method.")
            return

        conn.autocommit = True

        sql = "INSERT INTO parking_data(vehicle_type, vehicle_no, company_name, location, time_slot, duration, total_amount, payment_method) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        values = (
            data.get("Vehicle Type", ""),
            data.get("Vehicle No", ""),  # Changed from "Vehicle Name" to "Vehicle No"
            data.get("Company Name", ""),
            data.get("Location", ""),
            data.get("Time Slot", ""),
            data.get("Duration", ""),
            data.get("Total Amount", ""),
            data.get("Payment Method", "")
        )

        try:
            cursor.execute(sql, values)
            conn.commit()
            print("Data Inserted into Database")
        except Exception as e:
            print(f"Error during database insertion: {e}")
            conn.rollback()

        print(f"SQL Query: {sql}")
        print(f"Values: {values}")

        print(f"Database Connection Status: {conn.is_connected()}")

        self.destroy()

    def fade_in(self):
        self.attributes('-alpha', 1.0)

    def fade_out(self):
        self.attributes('-alpha', 0.1)

class FormStep(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.data = {}

    def get_data(self):
        return self.data

class Page1(FormStep):
    def __init__(self, master, data_from_code1=None):
        super().__init__(master)
        ttk.Label(self, text="").pack(pady=10)
        self.vehicle_type = tk.StringVar(value=data_from_code1.get("Vehicle Type", ""))
        ttk.Label(self, text="Vehicle Type:").pack()
        ttk.Combobox(self, values=["Two Wheeler", "Hatchback", "SUV", "Sedan", "Limousine"],
                     textvariable=self.vehicle_type).pack(pady=5)

        self.vehicle_no = tk.StringVar(value=data_from_code1.get("Vehicle No", ""))
        ttk.Label(self, text="Vehicle No:").pack()  # Changed from "Vehicle Name" to "Vehicle No"
        ttk.Entry(self, textvariable=self.vehicle_no).pack(pady=5)

        self.company_name = tk.StringVar(value=data_from_code1.get("Company Name", ""))
        ttk.Label(self, text="Company Name:").pack()
        ttk.Entry(self, textvariable=self.company_name).pack(pady=5)

    def get_data(self):
        self.data.update(super().get_data())
        self.data["Vehicle Type"] = self.vehicle_type.get()
        self.data["Vehicle No"] = self.vehicle_no.get()  # Changed from "Vehicle Name" to "Vehicle No"
        self.data["Company Name"] = self.company_name.get()
        return self.data

class Page2(FormStep):
    def __init__(self, master):
        super().__init__(master)
        ttk.Label(self, text="").pack(pady=10)

        self.location = tk.StringVar()
        ttk.Label(self, text="Location:").pack()
        ttk.Combobox(self,values=["Virar", "Nalasopara", "Bhayandar", "Mira Road", "Dahisar", "Andheri", "Vile Parle"],
                    textvariable=self.location).pack(pady=5)

        self.time_slot = tk.StringVar()
        ttk.Label(self, text="Time Slot:").pack()
        ttk.Combobox(self, values=["10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "1:00"],
                    textvariable=self.time_slot).pack(pady=5)

        self.duration = tk.StringVar()
        ttk.Label(self, text="Duration:").pack()
        ttk.Combobox(self, values=["1 hour", "2 hour", "3 hour", "4 hour", "5 hour"],
                    textvariable=self.duration).pack(pady=5)

    def get_data(self):
        self.data.update(super().get_data())
        self.data["Location"] = self.location.get()
        self.data["Time Slot"] = self.time_slot.get()
        self.data["Duration"] = self.duration.get()
        return self.data

class Page3(FormStep):
    def __init__(self, master):
        super().__init__(master)
        ttk.Label(self, text="").pack(pady=10)

        self.var1 = tk.BooleanVar()
        self.var2 = tk.BooleanVar()
        self.var3 = tk.BooleanVar()
        self.var4 = tk.BooleanVar()
        self.var5 = tk.BooleanVar()
        self.var6 = tk.BooleanVar()

        ttk.Label(self, text="                       Service                Price           ").pack()
        ttk.Checkbutton(self, text="                      Service1              1000            ",
                            variable=self.var1).pack(pady=2)
        ttk.Checkbutton(self, text="                      Service2              2000            ",
                            variable=self.var2).pack(pady=2)
        ttk.Checkbutton(self, text="                      Service3              3000            ",
                            variable=self.var3).pack(pady=2)
        ttk.Checkbutton(self, text="                      Service4              4000            ",
                            variable=self.var4).pack(pady=2)
        ttk.Checkbutton(self, text="                      Service5              5000            ",
                            variable=self.var5).pack(pady=2)
        ttk.Checkbutton(self, text="                      Service6              6000            ",
                            variable=self.var6).pack(pady=2)

    def get_data(self):
        self.data.update(super().get_data())
        self.total_amount = 0

        if self.var1.get():
            self.total_amount += 1000
        if self.var2.get():
            self.total_amount += 2000
        if self.var3.get():
            self.total_amount += 3000
        if self.var4.get():
            self.total_amount += 4000
        if self.var5.get():
            self.total_amount += 5000
        if self.var6.get():
            self.total_amount += 6000

        self.data["Total Amount"] = self.total_amount
        return self.data

class Page4(FormStep):
    def __init__(self, master, data_from_previous_pages=None):
        super().__init__(master)
        ttk.Label(self, text="").pack(pady=10)

        if data_from_previous_pages:
            ttk.Label(self, text="Vehicle Type: {}".format(data_from_previous_pages.get("Vehicle Type", ""))).pack()
            ttk.Label(self, text="Vehicle No: {}".format(data_from_previous_pages.get("Vehicle No", ""))).pack()
            ttk.Label(self, text="Company Name: {}".format(data_from_previous_pages.get("Company Name", ""))).pack()
            ttk.Label(self, text="Location: {}".format(data_from_previous_pages.get("Location", ""))).pack()
            ttk.Label(self, text="Time Slot: {}".format(data_from_previous_pages.get("Time Slot", ""))).pack()
            ttk.Label(self, text="Duration: {}".format(data_from_previous_pages.get("Duration", ""))).pack()
            ttk.Label(self, text="Total Amount: {}".format(data_from_previous_pages.get("Total Amount", ""))).pack()
        else:
            ttk.Label(self, text="No data from previous pages.").pack()

        ttk.Label(self, text="").pack(pady=10)
        ttk.Label(self, text="Payment Method:").pack()

        self.payment_method = tk.StringVar()
        online_button = ttk.Radiobutton(self, text="Online", variable=self.payment_method, value="Online")
        online_button.pack()
        cash_button = ttk.Radiobutton(self, text="Cash", variable=self.payment_method, value="Cash")
        cash_button.pack()

        if data_from_previous_pages and data_from_previous_pages.get("Total Amount", 0) > 2000:
            cash_button.state(['disabled'])
        self.next_button = ttk.Button(self, text="Next", command=self.show_payment_summary)
        self.next_button.pack(side=tk.RIGHT, padx=10, pady=10)

    def show_payment_summary(self):

        data = self.get_data()

        if data.get("Payment Method") == "Cash":
            self.master.destroy()
            return

        self.master.show_next_step()

    def get_data(self):
        self.data.update(super().get_data())
        self.data["Payment Method"] = self.payment_method.get()
        self.master.steps[self.master.current_step].data_from_previous_pages = self.data
        return self.data

class OnlinePaymentPage(FormStep):
    def __init__(self, master, total_amount=0, data_from_previous_pages=None):
        super().__init__(master)
        self.total_amount = total_amount
        self.data_from_previous_pages = data_from_previous_pages

        ttk.Label(self, text="Online Payment").pack(pady=10)

        #ttk.Label(self, text=f"Total Amount: {self.total_amount}").pack()

        ttk.Label(self, text="Payment By").pack()

        self.payment_method = tk.StringVar()
        ttk.Radiobutton(self, text="UPI", variable=self.payment_method, value="UPI").pack()
        ttk.Radiobutton(self, text="Debit Card", variable=self.payment_method, value="Debit Card").pack()
        ttk.Radiobutton(self, text="Credit Card", variable=self.payment_method, value="Credit Card").pack()

        ttk.Label(self, text="Enter ID/CARD NO").pack()
        self.id_type = tk.StringVar()
        id_options = ["UPI ID", "Debit Card NO", "Credit Card NO"]
        ttk.Combobox(self, values=id_options, textvariable=self.id_type).pack(pady=5)

        ttk.Button(self, text="Next", command=self.show_payment_summary).pack(side=tk.RIGHT, padx=10, pady=10)
        ttk.Button(self, text="Previous", command=self.show_previous_page).pack(side=tk.LEFT, padx=10, pady=10)

    def show_payment_summary(self):
        data_from_previous_pages = self.master.steps[-2].get_data()
        total_amount_from_page4 = data_from_previous_pages.get("Total Amount", 0)

        payment_by = self.payment_method.get()
        id_card_no = "N/A"

        if payment_by == "UPI":
            id_card_no = simpledialog.askstring("Input", "Enter UPI ID:")
        elif payment_by in ["Debit Card", "Credit Card"]:
            id_card_no = simpledialog.askinteger("Input", f"Enter {self.id_type.get()}:")

        # Save data to the database before proceeding
        self.save_to_database(data_from_previous_pages, payment_by, id_card_no)

        ttk.Label(self, text=f"Payment By: {payment_by}").pack()
        ttk.Label(self, text=f"{self.id_type.get()}: {id_card_no}").pack()

        self.master.show_next_step()

    def save_to_database(self, data_from_previous_pages, payment_by, id_card_no):
        data = self.get_data()
        data.update(data_from_previous_pages)
        data["Payment Method"] = payment_by
        data["ID Type"] = self.id_type.get()
        data["ID/Card No"] = id_card_no

        sql = "INSERT INTO parking_data(vehicle_type, vehicle_no, company_name, location, time_slot, duration, total_amount, payment_method, id_type, id_card_no) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (
            data.get("Vehicle Type", ""),
            data.get("Vehicle No", ""),
            data.get("Company Name", ""),
            data.get("Location", ""),
            data.get("Time Slot", ""),
            data.get("Duration", ""),
            data.get("Total Amount", ""),
            data.get("Payment Method", ""),
            data.get("ID Type", ""),
            data.get("ID/Card No", "")
        )

        try:
            cursor.execute(sql, values)
            conn.commit()
            print("Data Inserted into Database")
        except Exception as e:
            print(f"Error during database insertion: {e}")
            conn.rollback()

        print(f"SQL Query: {sql}")
        print(f"Values: {values}")

    def show_previous_page(self):
        self.master.show_prev_step()

    def get_data(self):
        self.data.update(super().get_data())
        return {
            "Payment Method": self.payment_method.get(),
            "ID Type": self.id_type.get()
        }

class SummaryPage(FormStep):
    def __init__(self, master, data_from_previous_pages=None):
        super().__init__(master)
        self.data_from_previous_pages = data_from_previous_pages

        ttk.Label(self, text="Summary Page").pack(pady=10)

        if data_from_previous_pages:
            ttk.Label(self, text="Vehicle Type: {}".format(data_from_previous_pages.get("Vehicle Type", ""))).pack()
            ttk.Label(self, text="Vehicle No: {}".format(data_from_previous_pages.get("Vehicle No", ""))).pack()
            ttk.Label(self, text="Company Name: {}".format(data_from_previous_pages.get("Company Name", ""))).pack()
            tk.Label(self, text="Location: {}".format(data_from_previous_pages.get("Location", ""))).pack()
            ttk.Label(self, text="Time Slot: {}".format(data_from_previous_pages.get("Time Slot", ""))).pack()
            ttk.Label(self, text="Duration: {}".format(data_from_previous_pages.get("Duration", ""))).pack()
            ttk.Label(self, text="Total Amount: {}".format(data_from_previous_pages.get("Total Amount", ""))).pack()

        ttk.Button(self, text="Download Data as PDF", command=self.download_data).pack(side=tk.RIGHT, padx=10,
                                                                                           pady=10)
        ttk.Button(self, text="Previous", command=self.show_previous_page).pack(side=tk.LEFT, padx=10, pady=10)

    def download_data(self):
        data = self.get_data()

        # Ask the user to choose the location to save the PDF file
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])

        if file_path:
            # Generate PDF and save it
            self.create_pdf(file_path)

            # Save the data to the database
            self.save_to_database(data)

            messagebox.showinfo("Download Complete", f"Data has been downloaded to {file_path}")

            # Destroy the window after download
            self.master.destroy()

    def save_to_database(self, data):
        sql = "INSERT INTO parking_data(vehicle_type, vehicle_no, company_name, location, time_slot, duration, total_amount, payment_method) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        values = (
            data.get("Vehicle Type", ""),
            data.get("Vehicle No", ""),
            data.get("Company Name", ""),
            data.get("Location", ""),
            data.get("Time Slot", ""),
            data.get("Duration", ""),
            data.get("Total Amount", ""),
            data.get("Payment Method", "")
        )

        try:
            cursor.execute(sql, values)
            conn.commit()
            print("Data Inserted into Database")
        except Exception as e:
            print(f"Error during database insertion: {e}")
            conn.rollback()

        print(f"SQL Query: {sql}")
        print(f"Values: {values}")

    def create_pdf(self, file_path):
        # Create a PDF document
        pdf_canvas = canvas.Canvas(file_path, pagesize=letter)

        # Set font and size
        pdf_canvas.setFont("Helvetica", 12)

        # Write data to the PDF
        data = self.get_data()
        y_position = 750  # Starting Y position
        for key, value in data.items():
            pdf_canvas.drawString(100, y_position, f"{key}: {value}")
            y_position -= 20

        # Save the PDF document
        pdf_canvas.save()

    def show_previous_page(self):
        self.master.show_prev_step()

    def get_data(self):
        return self.data_from_previous_pages

if __name__ == "__main__":
    root = MultiStepForm()
    root.mainloop()




