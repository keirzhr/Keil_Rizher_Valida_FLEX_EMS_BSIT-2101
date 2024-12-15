import mysql.connector
from mysql.connector import Error
from tkinter import *
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk 
import tkinter as tk
import subprocess
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re
import sys
import random
import json
import os

# Function to create a connection and close
def create_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="flex_ems",
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error: '{e}'")
        return None

def close_connection(connection):
    if connection.is_connected():
        connection.close()

# Function to add an event to the database
def add_event():
    global current_frame
    connection = create_connection()
    if connection:
        # Get the input field values
        event_name = event_name_entry.get().strip()
        event_date = event_date_entry.get().strip()
        location = location_entry.get().strip()
        description = description_entry.get().strip()
        organizer_contact = organizer_contact_entry.get().strip()
        event_type = event_type_var.get().strip()
        event_image_path = image_path_var.get().strip()

        # Check if required fields are filled
        if not event_name or not event_date or not location or not description or not event_type or event_type == "Select Event Type":
            messagebox.showerror("Error", "Please fill in all required fields and select a valid event type!")
            return

        # Phone number validation (11 digits only)
        clean_phone = ''.join(filter(str.isdigit, organizer_contact))
        if len(clean_phone) != 11:
            messagebox.showerror("Error", "Organizer contact number must be exactly 11 digits!")
            return
        organizer_contact = clean_phone 
        
        query = """
        INSERT INTO Events (event_name, event_date, location, description, event_type, organizer_contact, event_image)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (event_name, event_date, location, description, event_type, organizer_contact, event_image_path)

        try:
            cursor = connection.cursor()
            cursor.execute(query, values)
            connection.commit()
            messagebox.showinfo("Success", "Event added successfully!")

            # Clear the fields after saving the event
            event_name_entry.delete(0, END)
            event_date_entry.delete(0, END)
            location_entry.delete(0, END)
            description_entry.delete(0, END)
            organizer_contact_entry.delete(0, END)
            event_type_var.set("Select Event Type") 
            image_path_var.set("")

        except Error as e:
            messagebox.showerror("Database Error", f"Failed to add event: {e}")
        finally:
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
            close_connection(connection)

if len(sys.argv) > 1:
    user_details_json = sys.argv[1]
    try:
        user_details = json.loads(user_details_json)
    except json.JSONDecodeError:
        print("Error: Unable to parse user details.")
        user_details = {}
else:
    print("Error: No user details provided.")
    user_details = {}

  # Generate a random 6-digit ticket ID
def generate_ticket_id():
    return f"T-{random.randint(100000, 999999)}"

def register_to_event():
    global current_frame
    account_info_frame.destroy()
    welcome_frame.pack_forget()
    add_event_frame.pack_forget()
    admin_dashboard_frame.pack_forget()
    connection = create_connection()
    if not connection:
        messagebox.showerror("Error", "Database connection failed.")
        return

    try:
        cursor = connection.cursor()

        selected_event = event_var.get()
        fields = {
            'event_type': event_type_var.get(),
            'event_id': None,
            'attendee_name': attendee_name_entry.get().strip(),
            'attendee_email': attendee_email_entry.get().strip(),
            'attendee_phone': attendee_phone_entry.get().strip(),
            'attendee_address': attendee_address_entry.get().strip()
        }

        # Validate selected event
        if selected_event == "Select Event":
            messagebox.showerror("Error", "Please select a valid event!")
            return

        cursor.execute("SELECT event_id FROM Events WHERE event_name = %s", (selected_event,))
        result = cursor.fetchone()
        if result:
            fields['event_id'] = result[0]
        else:
            messagebox.showerror("Error", "The selected event could not be found in the database.")
            return

        # Validation check for required fields
        if not all(fields.values()) or fields['event_type'] == "Select Category":
            messagebox.showerror("Error", "Please fill in all required fields and select a valid category and event!")
            return

        # Email validation
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_pattern, fields['attendee_email']):
            messagebox.showerror("Error", "Invalid email format! Please enter a valid email address.")
            return

        # Phone number validation (11 digits only)
        phone_pattern = r'^\d{11}$'
        if not re.match(phone_pattern, fields['attendee_phone']):
            messagebox.showerror("Error", "Phone number must be exactly 11 digits!")
            return

        # Generate a random ticket ID
        ticket_id = generate_ticket_id()

        query = """
        INSERT INTO Attendees (event_id, name, email, attendee_phone, attendee_address, ticket_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (fields['event_id'], fields['attendee_name'], fields['attendee_email'], fields['attendee_phone'], fields['attendee_address'], ticket_id))
        connection.commit()

        # Send email confirmation
        subject = "Event Registration Confirmation"
        body = (
            f"Dear {fields['attendee_name']},\n\n"
            f"You have successfully registered for the event: {selected_event}.\n"
            f"Your ticket ID is: {ticket_id}.\n\n"
            f"Please keep this ticket ID for event entry.\n\nThank you!"
        )
        send_email(fields['attendee_email'], subject, body)

        messagebox.showinfo("Success", "Attendee registered and confirmation email sent successfully!")

        event_var.set("Select Event")
        event_type_var.set("Select Category")
        attendee_name_entry.delete(0, END)
        attendee_email_entry.delete(0, END)
        attendee_phone_entry.delete(0, END)
        attendee_address_entry.delete(0, END)

    except Error as e:
        messagebox.showerror("Database Error", f"Failed to register attendee: {e}")
    finally:
        close_connection(connection)

def send_email(recipient_email, subject, body):
    sender_email = "23-02166@g.batstate-u.edu.ph"
    sender_password = "sbju xzwe lelk pqvz"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string() 
        server.sendmail(sender_email, recipient_email, text)
        server.quit()

    except Exception as e:
        print(f"Error: {e}")
        
# Function to upload an event image
def upload_image():
    image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.gif")])
    
    if image_path:
        image_name = os.path.basename(image_path)

        target_folder = os.path.join(os.path.dirname(__file__), 'images')
        
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
        
        target_path = os.path.join(target_folder, image_name)
        
        if os.path.abspath(image_path) != os.path.abspath(target_path):
            try:
                import shutil
                # Copy the image to the target folder
                shutil.copy(image_path, target_path)
                print(f"Image uploaded successfully: {image_name}")
            except Exception as e:
                print(f"Error uploading image: {e}")
        else:
            print("Image is already in the target folder.")
        
        image_path_var.set(image_name)
        
# Function to load events based on category
def load_events_for_category():
    connection = create_connection()
    if connection:
        event_type = event_type_var.get()

        query = "SELECT event_id, event_name, event_image FROM Events WHERE event_type = %s"
        cursor = connection.cursor()
        cursor.execute(query, (event_type,))
        events = cursor.fetchall()

        event_dropdown['menu'].delete(0, 'end')

        for event_id, event_name, event_image in events:
            event_dropdown['menu'].add_command(label=event_name,command=lambda name=event_name, img=event_image: on_event_select(name, img))
        connection.close()

def on_event_select(event_name, event_image_path):
    event_var.set(event_name) 
    display_event_image(event_image_path)

# Function to show event image when event is selected
def show_event_image(event):
    event_name, event_image_path = event[1], event[2]
    event_var.set(event_name)
    display_event_image(event_image_path)

# Function to clear all input fields in the event form
def Clear_Fields(attendee_fields=None):
    event_name_entry.delete(0, END)
    event_date_entry.delete(0, END)
    location_entry.delete(0, END)
    description_entry.delete(0, END)
    organizer_contact_entry.delete(0, END)
    
    event_type_var.set("Select Event Type")
    image_path_var.set("")
    
    if hasattr(display_event_image, 'event_image_label'):
        display_event_image.event_image_label.destroy()
    
    if attendee_fields:
        for field in attendee_fields:
            if isinstance(field, Entry):
                field.delete(0, END)
            elif isinstance(field, StringVar):
                field.set("") 

# Function to display the event image in the registration form
def display_event_image(image_filename):
    try:
        base_image_path = os.path.join(os.path.dirname(__file__), 'images')
        image_path = os.path.join(base_image_path, image_filename)
        image_path = os.path.normpath(image_path)
        
        if not os.path.exists(image_path):
            print(f"Error: The file {image_path} does not exist.")
            return

        img = Image.open(image_path)
        img = img.resize((140, 190))
        img = ImageTk.PhotoImage(img)

        if hasattr(display_event_image, 'event_image_label'):
            display_event_image.event_image_label.destroy()

        display_event_image.event_image_label = Label(register_attendee_frame, image=img)
        display_event_image.event_image_label.image = img
        display_event_image.event_image_label.place(x=350, y=125)
        
    except Exception as e:
        print(f"Error displaying event image: {e}")

# Function to display the admin dashboardq
def show_admin_dashboard():
    account_info_frame.destroy()
    welcome_frame.pack_forget()
    add_event_frame.pack_forget()
    register_attendee_frame.pack_forget()
    admin_dashboard_frame.pack(fill=BOTH, expand=True, padx=30, pady=60)

    for widget in admin_dashboard_frame.winfo_children():
        widget.destroy()

    Label(admin_dashboard_frame, text="Admin Dashboard", 
          font=("Arial", 18, "bold"), fg="#6EC207", bg="#1A1A19").pack(pady=10)

    button_frame_top = Frame(admin_dashboard_frame, bg="#1A1A19")
    button_frame_top.pack(pady=5)

    def load_events():
        show_listbox("Events")

    def load_attendees():
        show_listbox("Attendees")

    # Hover effec
    def hover_in(button):
        button.config(bg="#4CAF50")

    def hover_out(button):
        if button["state"] != "active":
            button.config(bg="#333") 
        
    # Create the "View Events" and "View Attendees" buttons
    view_events_button = Button(button_frame_top, text="View Events", command=load_events, width=15, bg="#333", fg="white")
    view_attendees_button = Button(button_frame_top, text="View Attendees", command=load_attendees, width=15, bg="#333", fg="white")

    # Bind hover effects to buttons
    view_events_button.bind("<Enter>", lambda event: hover_in(event, view_events_button))
    view_events_button.bind("<Leave>", lambda event: hover_out(event, view_events_button))
    view_attendees_button.bind("<Enter>", lambda event: hover_in(event, view_attendees_button))
    view_attendees_button.bind("<Leave>", lambda event: hover_out(event, view_attendees_button))
    view_events_button.grid(row=0, column=0, padx=10)
    view_attendees_button.grid(row=0, column=1, padx=10)

    # Middle section to display information
    list_frame = Frame(admin_dashboard_frame, bg="#1A1A19")
    list_frame.pack(fill=BOTH, expand=True, pady=10)

    # Scrollbars
    y_scrollbar = Scrollbar(list_frame, orient=VERTICAL)
    x_scrollbar = Scrollbar(list_frame, orient=HORIZONTAL)

    listbox = Listbox(list_frame, width=100, height=17, yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set,
                      bg="#1A1A19", fg="white", selectbackground="#555", selectforeground="white")
    
    y_scrollbar.config(command=listbox.yview)
    x_scrollbar.config(command=listbox.xview)
    y_scrollbar.pack(side=RIGHT, fill=Y)
    x_scrollbar.pack(side=BOTTOM, fill=X)

    listbox.pack(side=LEFT, fill=BOTH, expand=False)

    def show_listbox(table):
        listbox.delete(0, END)
        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            if table == "Events":
                cursor.execute("SELECT event_id, event_name, event_date, location, event_type, organizer_contact FROM Events")
                data = cursor.fetchall()
                headers = f"{'ID':<5} | {'Event Name':<35} | {'Date':<13} | {'Location':<25} | {'Event Type':<15} | {'Organizer Contact':<20}"
            elif table == "Attendees":
                cursor.execute("""
                    SELECT attendee_id, name, email, event_id, attendee_phone, attendee_address, ticket_id
                    FROM Attendees
                """)
                data = cursor.fetchall()
                headers = f"{'ID':<5} | {'Name':<25} | {'Email':<25} | {'Event':<5} | {'Phone':<15} | {'Address':<20} | {'Ticket':<10}"
            else:
                data = []
                headers = ""

            # Style the headers
            listbox.insert(END, headers)
            listbox.insert(END, "-" * len(headers))

            for i, row in enumerate(data):
                if table == "Events":
                    try:
                        formatted_date = row[2].strftime("%Y-%m-%d") if row[2] else "N/A"
                    except:
                        formatted_date = str(row[2]) if row[2] else "N/A"

                    formatted_row = f"{row[0]:<5} | {row[1][:35]:<35} | {formatted_date:<13} | {row[3][:25]:<25} | {row[4][:15]:<15} | {row[5][:20]:<20}"

                    listbox.insert(END, formatted_row)
                elif table == "Attendees":
                    event_registered = str(row[3]) if row[3] != 0 else "Not Reg"
                    attendee_phone = str(row[4]) if row[4] else "N/A"
                    attendee_address = row[5] if row[5] else "N/A"
                    ticket_id = row[6] if row[6] else "N/A"

                    attendee_phone = ''.join(c for c in attendee_phone if c.isdigit())

                    formatted_row = f"{row[0]:<5} | {row[1][:25]:<25} | {row[2][:25]:<25} | {event_registered:<5} | {attendee_phone[:15]:<15} | {attendee_address[:20]:<20} | {ticket_id[:10]:<10}"
                    
                    listbox.insert(END, formatted_row)

            connection.close()

        listbox.configure(bg="#1A1A19",fg="white", selectbackground="#4CAF50", selectforeground="white", activestyle='none', font=("Courier", 11) )
        
    def hover_in(event, widget):
        widget.config(bg="#4CAF50")  # Change color on hover

    def hover_out(event, widget):
        widget.config(bg="#333")  # Revert back to original color 

    search_var = StringVar()
    search_frame = Frame(admin_dashboard_frame, bg="#1A1A19")
    search_frame.pack(pady=5)
    Label(search_frame, text="Search:", fg="white", bg="#1A1A19").grid(row=0, column=0, padx=5)
    search_entry = Entry(search_frame, textvariable=search_var, width=40, bg="#1A1A19", fg="white", insertbackground="white")
    search_entry.grid(row=0, column=1, padx=5)

    # Function to perform search
    def search_list():
        query = search_var.get().lower()
        filtered_data = [row for row in listbox.get(2, END) if query in row.lower()]
        listbox.delete(2, END)
        for row in filtered_data:
            listbox.insert(END, row)

    # Search button with hover
    search_button = Button(search_frame, text="Search", command=search_list, bg="#333", fg="white", width=10)
    search_button.grid(row=0, column=2, padx=5)
    search_button.bind("<Enter>", lambda event: hover_in(event, search_button))
    search_button.bind("<Leave>", lambda event: hover_out(event, search_button))

    action_frame = Frame(admin_dashboard_frame, bg="#1A1A19")
    action_frame.pack(pady=10)

    def delete_selected():
        selected = listbox.curselection()
        if selected and selected[0] > 1: 
            selected_item = listbox.get(selected[0])

            if "Event Name" in listbox.get(0):
                table, id_column = "Events", "event_id"
                selected_id = selected_item.split()[0].strip()
            elif "Name" in listbox.get(0):
                table, id_column = "Attendees", "attendee_id"
                selected_id = selected_item.split()[0].strip()
            else:
                messagebox.showerror("Error", "Unable to determine the selected table.")
                return

            confirm = messagebox.askyesno("Confirmation", f"Are you sure you want to delete this {table[:-1]}?")
            if not confirm:
                return  # Cancel deletion if the user selects No
            # and to delete
            connection = create_connection()
            if connection:
                try:
                    cursor = connection.cursor()
                    cursor.execute(f"DELETE FROM {table} WHERE {id_column} = %s", (selected_id,))
                    connection.commit()
                    connection.close()
                    messagebox.showinfo("Success", f"{  table[:-1]} deleted successfully!")

                    show_listbox("Events" if table == "Events" else "Attendees")
                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred: {e}")
                finally:
                    connection.close()
        else:
            messagebox.showerror("Error", "Please select a valid item to delete.")

    def update_selected():
        selected = listbox.curselection()
        if selected and selected[0] > 1:
            selected_item = listbox.get(selected[0])

            if "Event Name" in listbox.get(0):
                update_event(selected_item)
            elif "Name" in listbox.get(0): 
                update_attendee(selected_item)
            else:
                messagebox.showerror("Error", "Unable to determine the selected table.")

    def update_event(selected_item):
        event_details = selected_item.split()
        event_id = event_details[0]

        # Create update window
        update_window = Toplevel(admin_dashboard_frame)
        update_window.title("Update Event")
        update_window.geometry("500x600+650+130")
        update_window.configure(bg="#1A1A19")
        update_window.resizable(False, False)

        main_frame = Frame(update_window, bg="#1A1A19", padx=30, pady=20)
        main_frame.pack(fill=BOTH, expand=True)

        # Title
        title_label = Label(main_frame, text="Update Event Details", font=("Arial", 18, "bold"), fg="#6EC207", bg="#1A1A19")
        title_label.pack(pady=(0, 20))

        labels = ["Event Name:", "Event Date:", "Location:", "Event Type:", "Organizer Contact:"]
        entries = []

        for label_text in labels:
            input_frame = Frame(main_frame, bg="#1A1A19")
            input_frame.pack(fill=X, pady=5)

            label = Label(input_frame, text=label_text, font=("Arial", 10), fg="white", bg="#1A1A19", anchor="w", width=20)
            label.pack(side=LEFT, padx=(0, 10))

            entry = Entry(input_frame, width=40, bg="#333", fg="white", insertbackground="white", font=("Arial", 10),relief=FLAT,
                          highlightthickness=1,highlightcolor="#6EC207",highlightbackground="#444")
            entry.pack(side=LEFT, expand=True, fill=X)
            entries.append(entry)

        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT event_name, event_date, location, event_type, organizer_contact FROM Events WHERE event_id = %s", (event_id,))
            existing_data = cursor.fetchone()
            connection.close()
            
            if existing_data:
                for entry, value in zip(entries, existing_data):
                    entry.insert(0, str(value) if value is not None else "")

        def save_event_updates():
            # Collect updated values
            updated_values = [entry.get() for entry in entries]
            
            connection = create_connection()
            if connection:
                try:
                    cursor = connection.cursor()
                    cursor.execute("""
                        UPDATE Events 
                        SET event_name = %s, event_date = %s, location = %s, 
                            event_type = %s, organizer_contact = %s 
                        WHERE event_id = %s
                    """, (*updated_values, event_id))
                    connection.commit()
                    messagebox.showinfo("Success", "Event updated successfully!")
                    update_window.destroy()
                    show_listbox("Events")  # Refresh the events list
                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred: {e}")
                finally:
                    connection.close()

        # Button Frame
        button_frame = Frame(main_frame, bg="#1A1A19")
        button_frame.pack(pady=20, fill=X)

        # Cancel Button
        cancel_button = Button(button_frame, text="Cancel", command=update_window.destroy, bg="#FF4500", fg="white", width=15,font=("Arial", 10, "bold"))
        cancel_button.pack(side=LEFT, expand=True, padx=10)

        # Save Button
        save_button = Button(button_frame, text="Save Updates", command=save_event_updates, bg="#4CAF50", fg="white", width=15,font=("Arial", 10, "bold"))
        save_button.pack(side=RIGHT, expand=True, padx=10)

    def update_attendee(selected_item):
        attendee_details = selected_item.split()
        attendee_id = attendee_details[0]

        # Create update window
        update_window = Toplevel(admin_dashboard_frame)
        update_window.title("Update Attendee")
        update_window.geometry("500x600+650+130")
        update_window.configure(bg="#1A1A19")
        update_window.resizable(False, False)

        main_frame = Frame(update_window, bg="#1A1A19", padx=30, pady=20)
        main_frame.pack(fill=BOTH, expand=True)

        # Title Label
        title_label = Label(main_frame, text="Update Attendee Details", font=("Arial", 18, "bold"), fg="#6EC207", bg="#1A1A19")
        title_label.pack(pady=(0, 20))

        labels = ["Name:", "Email:", "Event ID:", "Phone:", "Address:", "Ticket ID:"]
        entries = []

        for label_text in labels:
            input_frame = Frame(main_frame, bg="#1A1A19")
            input_frame.pack(fill=X, pady=5)

            label = Label(input_frame, text=label_text, font=("Arial", 10), fg="white", bg="#1A1A19",anchor="w", width=20)
            label.pack(side=LEFT, padx=(0, 10))

            entry = Entry(input_frame, width=40, bg="#333", fg="white", insertbackground="white", font=("Arial", 10),relief=FLAT,highlightthickness=1,highlightcolor="#6EC207",highlightbackground="#444")
            entry.pack(side=LEFT, expand=True, fill=X)
            entries.append(entry)

        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT name, email, event_id, attendee_phone, 
                    attendee_address, ticket_id 
                FROM Attendees 
                WHERE attendee_id = %s
            """, (attendee_id,))
            existing_data = cursor.fetchone()
            connection.close()

            if existing_data:
                for entry, value in zip(entries, existing_data):
                    entry.insert(0, str(value) if value is not None else "")

        def save_attendee_updates():
            updated_values = [entry.get() for entry in entries]
            
            connection = create_connection()
            if connection:
                try:
                    cursor = connection.cursor()
                    cursor.execute("""
                        UPDATE Attendees 
                        SET name = %s, email = %s, event_id = %s, 
                            attendee_phone = %s, attendee_address = %s, ticket_id = %s 
                        WHERE attendee_id = %s
                    """, (*updated_values, attendee_id))
                    connection.commit()
                    messagebox.showinfo("Success", "Attendee updated successfully!")
                    update_window.destroy()
                    show_listbox("Attendees")
                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred: {e}")
                finally:
                    connection.close()

        # Button Frame
        button_frame = Frame(main_frame, bg="#1A1A19")
        button_frame.pack(pady=20, fill=X)

        # Cancel Button
        cancel_button = Button(button_frame, text="Cancel", command=update_window.destroy, bg="#FF4500", fg="white", width=15,font=("Arial", 10, "bold"))
        cancel_button.pack(side=LEFT, expand=True, padx=10)

        # Save Button
        save_button = Button(button_frame, text="Save Updates", command=save_attendee_updates, bg="#4CAF50", fg="white", width=15,font=("Arial", 10, "bold"))
        save_button.pack(side=RIGHT, expand=True, padx=10)

    # Delete and Update Buttons
    Button(action_frame, text="Delete", command=delete_selected, width=15, bg="#FF4500", fg="white").grid(row=0, column=0, padx=10)
    Button(action_frame, text="Update", command=update_selected, width=15, bg="#4CAF50", fg="white").grid(row=0, column=1, padx=10)

    load_events()

def log_out(window):
    response = messagebox.askyesno("Logout Confirmation", "Are you sure you want to logout?")
    if response:  # If user confirms
        window.destroy()

        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            login_script_path = os.path.join(current_dir, 'login.py')
            subprocess.Popen([sys.executable, login_script_path], shell=True)
        except Exception as e:
            print(f"Error starting login.py: {e}")


def show_event_form():
    welcome_frame.pack_forget()
    add_event_frame.pack_forget()
    register_attendee_frame.pack_forget()
    admin_dashboard_frame.pack_forget()
    account_info_frame.pack_forget()
    add_event_frame.pack(fill=BOTH, expand=False, padx=30, pady=50)

def show_register_form():
    welcome_frame.pack_forget()
    add_event_frame.pack_forget()
    admin_dashboard_frame.pack_forget()
    account_info_frame.pack_forget()
    register_attendee_frame.pack(fill=BOTH, expand=False, padx=30, pady=20)
    

def switch_frame(new_frame):
    """
    Hides the currently active frame and displays the new frame.
    """
    global current_frame
    if current_frame:
        current_frame.pack_forget()
    current_frame = new_frame 
    current_frame.pack(fill=BOTH, expand=True, padx=30, pady=50)
  
# pin
def load_profile_picture(profile_pic_path):
    default_pic_path = os.path.join(os.path.dirname(__file__), 'images', 'person.png')
   
    profile_pic_path = os.path.join(os.path.dirname(__file__), profile_pic_path)
    
    if not os.path.exists(profile_pic_path):
        profile_pic_path = default_pic_path
    
    try:
        profile_image = Image.open(profile_pic_path)
        profile_image = profile_image.resize((200, 200), Image.LANCZOS)
        return ImageTk.PhotoImage(profile_image)
    except Exception as e:
        print(f"Error loading profile picture: {e}")
        profile_image = Image.open(default_pic_path)
        profile_image = profile_image.resize((200, 200), Image.LANCZOS)
        return ImageTk.PhotoImage(profile_image)


def show_account_info(user_details):
    global current_frame, account_info_frame

    if 'account_info_frame' in globals() and account_info_frame:
        account_info_frame.destroy()

    # Hide all other frames
    for frame in [welcome_frame, add_event_frame, register_attendee_frame, admin_dashboard_frame]:
        frame.pack_forget()

    account_info_frame = tk.Frame(content_frame, bg="#1A1A19")
    account_info_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=65)

    # Title
    title_label = tk.Label(account_info_frame, text="Account Information", font=("Arial", 18, "bold"), fg="#6EC207", bg="#1A1A19")
    title_label.pack(pady=20)

    # Main Container
    main_container = tk.Frame(account_info_frame, bg="#1A1A19")
    main_container.pack(expand=True, fill=tk.BOTH)

    # Profile Picture Section
    profile_frame = tk.Frame(main_container, bg="#1A1A19")
    profile_frame.pack(expand=True)
    profile_pic_path = user_details.get("profile_pic", "uploads/person.png")
    profile_photo = load_profile_picture(profile_pic_path)
    profile_label = tk.Label(profile_frame, image=profile_photo, bg="#1A1A19")
    profile_label.image = profile_photo
    profile_label.pack(pady=10)

    def update_profile():
        update_window = tk.Toplevel(account_info_frame)
        update_window.title("Update Profile")
        update_window.geometry("500x600+650+130")
        update_window.configure(bg="#1A1A19")
        update_window.transient(account_info_frame) 
        update_window.grab_set()  
        
        # Create a frame for profile picture preview
        profile_pic_frame = tk.Frame(update_window, bg="#1A1A19")
        profile_pic_frame.pack(pady=10)

        # Display the current profile picture
        current_profile_pic = user_details.get("profile_pic", "uploads/person.png")
        profile_photo = load_profile_picture(current_profile_pic)

        profile_pic_label = tk.Label(profile_pic_frame, image=profile_photo, bg="#1A1A19")
        profile_pic_label.image = profile_photo
        profile_pic_label.pack()

        # Function to create labeled entries
        def create_labeled_entry(parent, label_text, default_value, show_char=None):
            frame = tk.Frame(parent, bg="#1A1A19")
            frame.pack(fill=tk.X, pady=5)

            label = tk.Label(frame, text=label_text, font=("Arial", 12), fg="white", bg="#1A1A19", width=20, anchor="w")
            label.pack(side=tk.LEFT, padx=10)

            entry = tk.Entry(frame, font=("Arial", 12), bg="#2A2A2A", fg="white", width=20, show=show_char)
            entry.insert(0, default_value)
            entry.pack(side=tk.LEFT, padx=10)

            return entry

        # Function to change profile picture
        def change_profile_picture():
            file_path = filedialog.askopenfilename(
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
            )
            if file_path:
                file_name = os.path.basename(file_path)
                profile_pic_path = f"uploads\\{file_name}"
                
                user_details['profile_pic'] = profile_pic_path
     
                new_photo = load_profile_picture(file_path)
                profile_pic_label.configure(image=new_photo)
                profile_pic_label.image = new_photo

                uploads_dir = "uploads"
                if not os.path.exists(uploads_dir):
                    os.makedirs(uploads_dir)
                try:
                    destination = os.path.join(uploads_dir, file_name)
                    with open(file_path, 'rb') as source_file:
                        with open(destination, 'wb') as dest_file:
                            dest_file.write(source_file.read())
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save profile picture: {e}")

        # entry fields
        full_name_entry = create_labeled_entry(update_window, "Full Name:", user_details.get("full_name", ""))
        username_entry = create_labeled_entry(update_window, "Username:", user_details.get("username", ""))
        email_entry = create_labeled_entry(update_window, "Email:", user_details.get("email", ""))
        phone_entry = create_labeled_entry(update_window, "Phone Number:", user_details.get("phone", ""))
        password_entry = create_labeled_entry(update_window, "New Password:", "", show_char='*')

        # Profile Picture Change Button
        change_pic_button = tk.Button(
            update_window, 
            text="Change Profile Picture", 
            command=change_profile_picture, 
            bg="#6EC207", fg="black", 
            font=("Arial", 10, "bold")
        )
        change_pic_button.pack(pady=10)

        # Save updates function
        def save_updates():
            # Collect updated details
            updated_details = {
                "full_name": full_name_entry.get(),
                "username": username_entry.get(),
                "email": email_entry.get(),
                "phone": phone_entry.get(),
                "profile_pic": user_details.get('profile_pic', current_profile_pic),
                "password": password_entry.get() or user_details.get('password'),
                "user_id": user_details.get("user_id")
            }

            # Add error handling and verification
            if "user_id" not in updated_details or not updated_details["user_id"]:
                messagebox.showerror("Error", "User ID is missing. Cannot update profile.")
                return

            connection = create_connection()
            if connection:
                cursor = connection.cursor()
                try:
                    cursor.execute("""
                        UPDATE users 
                        SET full_name = %s, username = %s, email = %s, phone = %s, profile_pic = %s, password = %s
                        WHERE user_id = %s
                    """, (
                        updated_details["full_name"],
                        updated_details["username"],
                        updated_details["email"],
                        updated_details["phone"],
                        updated_details["profile_pic"],
                        updated_details["password"],
                        updated_details["user_id"]
                    ))
                    connection.commit()
                    messagebox.showinfo("Success", "Profile updated successfully!")
                    
                    # Refresh account info with new details
                    user_details.update(updated_details)
                    show_account_info(user_details)
                except Exception as e:
                    connection.rollback() 
                    messagebox.showerror("Error", f"Failed to update profile: {e}")
                finally:
                    cursor.close()
                    close_connection(connection)
            else:
                messagebox.showerror("Error", "Failed to connect to the database.")

            update_window.destroy()
            
        # Save and Cancel Buttons
        def cancel_update():
            update_window.destroy()
            
        button_frame = tk.Frame(update_window, bg="#1A1A19")
        button_frame.pack(pady=20)

        save_button = tk.Button(button_frame, text="Save Updates", command=save_updates, bg="#6EC207", fg="black", font=("Arial", 12, "bold"))
        save_button.pack(side=tk.LEFT, padx=10)

        cancel_button = tk.Button(button_frame, text="Cancel", command=cancel_update, bg="#DC3545", fg="white", font=("Arial", 12, "bold"))
        cancel_button.pack(side=tk.LEFT, padx=10)


    # Update Profile Button
    update_button = tk.Button(account_info_frame, text="Update Profile", command=update_profile, bg="#6EC207", fg="black", font=("Arial", 10, "bold"))
    update_button.pack(pady=25)

    info_frame = tk.Frame(main_container, bg="#1A1A19")
    info_frame.pack(expand=True)

    details = [
        ("Full Name:", user_details.get("full_name", "N/A")),
        ("Username:", user_details.get("username", "N/A")),
        ("Email:", user_details.get("email", "N/A")),
        ("Phone Number:", user_details.get("phone", "N/A")),
    ]

    for label, value in details:
        row_frame = tk.Frame(info_frame, bg="#1A1A19")
        row_frame.pack(fill=tk.X, pady=5)

        tk.Label(row_frame, text=label, font=("Arial", 12), fg="white", bg="#1A1A19", width=20, anchor="e").pack(side=tk.LEFT, padx=10)
        tk.Label(row_frame, text=value, font=("Arial", 12), fg="#6EC207", bg="#1A1A19", anchor="w").pack(side=tk.LEFT, padx=10)

    current_frame = account_info_frame


# Main window function
def main_window():
    global add_event_frame, register_attendee_frame, admin_dashboard_frame, update_time, welcome_frame, content_frame, current_frame, account_info_frame
    global event_name_entry, event_date_entry, location_entry, description_entry, organizer_contact_entry
    global attendee_name_entry, attendee_email_entry, attendee_phone_entry, attendee_address_entry, event_var, event_type_dropdown, event_dropdown
    global event_type_var, image_path_var
    
    window = Tk()
    window.geometry('1080x650+250+110')
    window.title("FLEX EMS")
    window.resizable(False, False)
    window.config(bg="#6EC207")

    event_type_var = StringVar()
    event_var = StringVar()
    image_path_var = StringVar()
    
    # Main menu frame
    main_menu_frame = Frame(window, bg="#1A1A19")
    main_menu_frame.pack(side=LEFT, fill=Y, padx=5, pady=5)
    
    content_frame = Frame(window, bg="#1A1A19")
    content_frame.pack(fill=BOTH, padx=5, pady=5)
    
    add_event_frame = Frame(content_frame, bg="#1A1A19")
    register_attendee_frame = Frame(content_frame, bg="#1A1A19")
    admin_dashboard_frame = Frame(content_frame, bg="#1A1A19")
    
    button_frame = Frame(add_event_frame, bg="#1A1A19")
    button_frame.grid(row=9, column=0, columnspan=2, pady=20)
    
    account_info_frame = Frame(content_frame, bg="#1A1A19")
    account_info_frame.pack(fill=BOTH, expand=True, padx=30, pady=50)
        
    welcome_frame = Frame(content_frame, bg="#1A1A19")
    welcome_frame.pack(fill=BOTH, expand=True)

    # Create a frame to organize the image and text
    welcome_content_frame = Frame(welcome_frame, bg="#1A1A19")
    welcome_content_frame.grid(row=0, column=0, sticky="nsew", padx=120, pady=20)

    # Configure grid weights
    welcome_content_frame.grid_rowconfigure(0, weight=0)
    welcome_content_frame.grid_rowconfigure(1, weight=1)
    welcome_content_frame.grid_columnconfigure(0, weight=1)

    #welcome logo 
    if getattr(sys, 'frozen', False):
        image_path = os.path.join(sys._MEIPASS, 'images', 'settinggreen.png') 
    else:
        # If running as a regular Python script
        image_path = os.path.join(os.path.dirname(__file__), 'images', 'settinggreen.png')

    # Check if the image file exists
    if os.path.exists(image_path):
        img = Image.open(image_path)
        img = img.resize((250, 250), Image.Resampling.LANCZOS)
        welcome_img = ImageTk.PhotoImage(img)
    else:
        print(f"Error: The image file '{image_path}' does not exist.")

    # Image Label
    welcome_image_label = Label(welcome_content_frame, image=welcome_img, bg="#1A1A19")
    welcome_image_label.image = welcome_img 
    welcome_image_label.grid(row=0, column=0, padx=10, pady=(10, 10))

    # Text Label
    welcome_text = Text(welcome_content_frame, wrap=WORD, font=("Arial", 16), height=6, width=35, bg="#1A1A19", fg="white", bd=0, relief=FLAT)
    welcome_text.grid(row=1, column=0, padx=10, pady=(0, 100), sticky="nsew")
    welcome_text.insert(END, "Welcome to FLEX-EMS\n", "center")
    welcome_text.insert(END, "Select an option from the left menu to get started", "center")
    welcome_text.tag_configure("center", justify="center")
    welcome_text.config(state=DISABLED)

    Label(main_menu_frame, text="FLEX-EMS", font=("Roboto", 20), fg="#6EC207", bg="#1A1A19", anchor="w").pack(pady=(30, 5), padx=30)
    Label(main_menu_frame, text="Flexible and Lean Event Management System", font=("Arial", 12), fg="white", bg="#1A1A19", anchor="w").pack(pady=(5, 30), padx=30)
    
    # Buttons in Main Menu
    Button(main_menu_frame, text="Add Event", command=show_event_form, width=25, height=2, font=("Arial", 14), fg="white", bg="#6EC207").pack(pady=15)
    Button(main_menu_frame, text="Register Attendee", command=show_register_form, width=25, height=2, font=("Arial", 14), fg="white", bg="#6EC207").pack(pady=15)
    Button(main_menu_frame, text="Admin Dashboard", command=show_admin_dashboard, width=25, height=2, font=("Arial", 14), fg="white", bg="#6EC207").pack(pady=15)
    Button(main_menu_frame, text="Account Info", command=lambda: show_account_info(user_details), width=25, height=2, font=("Arial", 14), fg="white", bg="#6EC207").pack(pady=15)   

    Button(main_menu_frame, text="Log Out", command=lambda: log_out(window), width=25, height=2, font=("Arial", 14), fg="white", bg="#FF4500").pack(pady=15)
    Label(main_menu_frame, text="Developed by Keil Rizher - BSIT 2101 (2024)", font=("Arial", 11), fg="white", bg="#1A1A19", anchor="w").place(relx=0, rely=1, x=45, y=-5, anchor="sw")
    
    #Addd event
    Label(add_event_frame, text="Add New Event", font=("Arial", 18, "bold"), fg="#6EC207", bg="#1A1A19").grid(row=0, column=0, columnspan=3, padx=200, pady=30, sticky="W")
    Label(add_event_frame, text="Event Name", fg="white", bg="#1A1A19",font=("Arial", 12)).grid(row=1, column=0, pady=10, padx=10, sticky=W)
    event_name_entry = Entry(add_event_frame, width=30, font=("Arial", 12), fg="white", bg="#1A1A19", insertbackground="white")
    event_name_entry.grid(row=1, columnspan=2, pady=10, padx=240)

    #Event Date
    Label(add_event_frame, text="Event Date(YYYY-MM-DD)", fg="white", bg="#1A1A19", font=("Arial", 12)).grid(row=2, column=0, pady=10, padx=10, sticky="W")
    event_date_entry = Entry(add_event_frame, width=30, fg="white", bg="#1A1A19", insertbackground="white", font=("Arial", 12))
    event_date_entry.grid(row=2, columnspan=2, pady=10)

    #Location
    Label(add_event_frame, text="Location", fg="white", bg="#1A1A19", font=("Arial", 12)).grid(row=3, column=0, pady=10, padx=10, sticky=W)
    location_entry = Entry(add_event_frame, width=30, fg="white", bg="#1A1A19", insertbackground="white", font=("Arial", 12))
    location_entry.grid(row=3, columnspan=2, pady=10)

    #Description
    Label(add_event_frame, text="Description", fg="white", bg="#1A1A19", font=("Arial", 12)).grid(row=4, column=0, pady=10, padx=10, sticky=W)
    description_entry = Entry(add_event_frame, width=30, fg="white", bg="#1A1A19", insertbackground="white",  font=("Arial", 12))
    description_entry.grid(row=4, columnspan=2, pady=10)

    #Organizer Contact
    Label(add_event_frame, text="Organizer Contact", fg="white", bg="#1A1A19", font=("Arial", 12)).grid(row=5, column=0, pady=10, padx=10, sticky=W)
    organizer_contact_entry = Entry(add_event_frame, width=30, fg="white", bg="#1A1A19",  font=("Arial", 12), insertbackground="white")
    organizer_contact_entry.grid(row=5, columnspan=2, pady=10, padx=10)

    #Event Type
    Label(add_event_frame, text="Event Type", fg="white", bg="#1A1A19", font=("Arial", 12)).grid(row=6, column=0, pady=10, padx=10, sticky=W)
    event_type_var = StringVar()
    event_type_var.set("Select Event Type")
    event_type_dropdown = OptionMenu(add_event_frame, event_type_var, "Concert", "Conference", "Workshop", "Seminar", "Festival")
    event_type_dropdown.config(fg="white", bg="#1A1A19", width=38)
    event_type_dropdown.grid(row=6, columnspan=2, pady=10)

    #Upload Event Image
    Label(add_event_frame, text="Upload Event Image", fg="white", bg="#1A1A19", font=("Arial", 10)).grid(row=7, column=0, padx=50, sticky=W)
    Button(add_event_frame, text="Upload Image", command=upload_image, width=20, fg="white", bg="#6EC207", font=("Arial, 10")).grid(row=7, columnspan=2, pady=20, padx=10)
    Label(add_event_frame, textvariable=image_path_var, fg="white", bg="#1A1A19", wraplength=540, padx=20, font=("Arial", 9)).grid(row=8, columnspan=1, pady=10, sticky=W)

    Button(button_frame, text="Save Event", command=add_event, width=15, fg="white", bg="#6EC207", font=("Arial", 11)).grid(row=0, column=0, padx=(10, 10), sticky=W)
    Button(button_frame, text="Clear Fields", command=lambda: Clear_Fields([event_name_entry, event_date_entry, location_entry, description_entry,
                organizer_contact_entry, event_type_var, image_path_var]), width=15, fg="white", bg="#FF4500", font=("Arial", 11)).grid(row=0, column=1, padx=(10, 10), sticky=W)

    # Title
    Label(register_attendee_frame, text="Register Attendee", font=("Arial", 18, "bold"), fg="#6EC207", bg="#1A1A19").grid(columnspan=1, padx=200, pady=(60, 10), sticky="w")

    # Select Event Category
    event_type_var.set("Select Category")
    event_type_dropdown = OptionMenu(register_attendee_frame, event_type_var, "Concert", "Conference", "Workshop", "Seminar", "Festival")
    event_type_dropdown.config(fg="white", bg="#1A1A19", width=20, font=("Arial", 11))
    event_type_dropdown.grid(row=1, column=0, columnspan=2,padx=120, pady=(21, 10), sticky="w")

    # Load Events Button and Event Dropdown
    Button(register_attendee_frame, text="Load Events", command=load_events_for_category,fg="white", bg="gray", font=("Arial", 11, "bold"),
           width=22).grid(row=2, column=0, pady=(30, 30), columnspan=2, padx=120, sticky="w")
    event_var.set("Select Event")
    event_dropdown = OptionMenu(register_attendee_frame, event_var, ())
    event_dropdown.config(fg="white", bg="#1A1A19", width=20, font=("Arial", 11))
    event_dropdown.grid(row=3, column=0, pady=(0, 80), columnspan=2, padx=120, sticky="w")

   # Attendee Name and Email Fields
    Label(register_attendee_frame, text="Attendee Name", fg="white", bg="#1A1A19", font=("Arial", 13)).grid(
        row=3,padx=90, pady=(70, 10), sticky="w")
    attendee_name_entry = Entry(register_attendee_frame, width=28, fg="white", bg="#1A1A19", insertbackground="white", font=("Arial", 13))
    attendee_name_entry.grid(row=3, padx=240,columnspan=2, pady=(70, 10), sticky="w")


    Label(register_attendee_frame, text="Attendee Email", fg="white", bg="#1A1A19", font=("Arial", 13)).grid(row=4, padx=90,  pady=(8, 10), sticky="w")
    attendee_email_entry = Entry(register_attendee_frame, width=28, fg="white", bg="#1A1A19", insertbackground="white", font=("Arial", 13))
    attendee_email_entry.grid(row=4, columnspan=1, pady=(8, 10), padx=240)

    # Attendee Phone and Address Fields
    Label(register_attendee_frame, text="Attendee Phone", fg="white", bg="#1A1A19", font=("Arial", 13)).grid(row=5, column=0, padx=90, pady=(8, 10), sticky="w")
    attendee_phone_entry = Entry(register_attendee_frame, width=28, fg="white", bg="#1A1A19", insertbackground="white", font=("Arial", 13))
    attendee_phone_entry.grid(row=5, columnspan=1, pady=(8, 10), padx=240)

    Label(register_attendee_frame, text="Attendee Address", fg="white", bg="#1A1A19", font=("Arial", 13)).grid(row=6, padx=90, pady=(8, 10), sticky="w")
    attendee_address_entry = Entry(register_attendee_frame, width=28, fg="white", bg="#1A1A19", insertbackground="white", font=("Arial", 13))
    attendee_address_entry.grid(row=6, columnspan=1, pady=(8, 10), padx=10)

    # register and clear fields buttons
    button_frame = Frame(register_attendee_frame, bg="#1A1A19")
    button_frame.grid(row=7, padx=73, columnspan=2, pady=(35, 30), sticky="w")

    Button(button_frame,text="Register",command=register_to_event, width=20,fg="white", bg="#6EC207", font=("Arial", 12)).grid(padx=20) 
    Button(button_frame, text="Clear Fields",command=lambda: Clear_Fields(attendee_fields=[attendee_name_entry, attendee_email_entry,attendee_phone_entry,
            attendee_address_entry, event_var]), width=20, fg="white", bg="#FF4500", font=("Arial", 12)).grid(row=0, column=1, padx=5)
    
    window.mainloop()

if __name__ == "__main__":
    main_window()

#color used list
#D9534F - light red
#6EC207 - green
#1A1A19 - grey

