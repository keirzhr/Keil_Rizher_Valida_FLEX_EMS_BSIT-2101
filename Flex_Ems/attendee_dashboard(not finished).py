import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import mysql.connector
import random
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EventManagementSystem:
    def __init__(self, root, user_email):
        self.root = root
        self.user_email = user_email
        self.root.title("Event Management System")
        self.root.geometry("1000x700")
        self.root.configure(bg="#6EC207")

        PRIMARY_COLOR = "#6EC207"
        SECONDARY_COLOR = "#4CAF50"
        BACKGROUND_COLOR = "#F0F4F0"
        
        nav_frame = tk.Frame(self.root, bg=SECONDARY_COLOR, height=50)
        
        self.root.configure(bg=PRIMARY_COLOR)
        # Create connection method
        self.create_connection = self.get_create_connection()

        # Email configuration
        self.sender_email = "23-02166@g.batstate-u.edu.ph"
        self.sender_password = "wgfr aymd kpix xutw"

        # Create main UI
        self.create_main_ui()

    def get_create_connection(self):
        def create_connection():
            try:
                connection = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='',
                    database='flex_ems'
                )
                return connection
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Could not connect to database: {err}")
                return None
        return create_connection

    def create_main_ui(self):
        # Navigation Frame
        nav_frame = tk.Frame(self.root, bg="#34495E", height=50)
        nav_frame.pack(fill=tk.X, side=tk.TOP)
        nav_frame.pack_propagate(False)

        # Navigation Buttons
        nav_buttons = [
            ("Attendee Profile", self.show_attendee_profile),
            ("Browse Events", self.show_browse_events),
            ("Registered Events", self.show_registered_events)
        ]

        for btn_text, btn_command in nav_buttons:
            btn = tk.Button(nav_frame, text=btn_text, command=btn_command, bg="#2980B9", fg="white", font=("Arial", 10, "bold"),relief=tk.FLAT)
            btn.pack(side=tk.LEFT, padx=10, pady=5)

        # Content Frame
        self.content_frame = tk.Frame(self.root, bg="#6EC207")
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        self.show_browse_events()

    def show_browse_events(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        browse_frame = tk.Frame(self.content_frame, bg="#6EC207")
        browse_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Search 
        search_frame = tk.Frame(browse_frame, bg="#6EC207")
        search_frame.pack(fill=tk.X, pady=10)

        tk.Label(search_frame, text="Search Events:", bg="#6EC207", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)

        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, width=30, bg="#34495E", fg="white")
        search_entry.pack(side=tk.LEFT, padx=5)

        # Event Type Dropdown
        event_types = ["All", "Conference", "Concert", "Workshop", "Seminar"]
        event_type_var = tk.StringVar(value="All")
        event_type_dropdown = ttk.Combobox(search_frame, textvariable=event_type_var, values=event_types, width=15)
        event_type_dropdown.pack(side=tk.LEFT, padx=5)

        # Treeview for Events
        columns = ("ID", "Event Name", "Date", "Location", "Type", "Seats Left")
        tree = ttk.Treeview(browse_frame, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor="center")

        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        def load_events(search_term="", event_type="All"):
            connection = self.create_connection()
            if connection:
                try:
                    cursor = connection.cursor()
                    query = """
                        SELECT event_id, event_name, event_date, location, event_type, 
                        (max_seats - (SELECT COUNT(*) FROM Attendees WHERE Attendees.event_id = Events.event_id)) as seats_left
                        FROM Events
                        WHERE event_date >= CURRENT_DATE()
                    """
                    
                    conditions = []
                    params = []

                    # Add search
                    if search_term:
                        conditions.append("(event_name LIKE %s OR location LIKE %s)")
                        params.extend([f"%{search_term}%", f"%{search_term}%"])

                    # Add event
                    if event_type != "All":
                        conditions.append("event_type = %s")
                        params.append(event_type)
                        
                    if conditions:
                        query += " AND " + " AND ".join(conditions)

                    cursor.execute(query, params)
                    
                    for item in tree.get_children():
                        tree.delete(item)

                    for event in cursor.fetchall():
                        tree.insert("", "end", values=event)

                    connection.close()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load events: {e}")
        # Search button
        search_button = tk.Button(search_frame, text="Search", command=lambda: load_events(search_var.get(), event_type_var.get()), bg="#2980B9", fg="white")
        search_button.pack(side=tk.LEFT, padx=5)

        # Register button
        register_button = tk.Button(browse_frame, text="Register for Selected Event", command=lambda: self.register_for_event(tree), bg="#2980B9", fg="white")
        register_button.pack(pady=10)
        
        load_events()

    def register_for_event(self, tree):
        # Get selected event
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an event to register")
            return

        # Get event details
        event_details = tree.item(selected_item)['values']
        event_id = event_details[0]

        # Open registration window
        self.show_registration_window(event_id)

    def show_registration_window(self, event_id):
        # Registration Window
        reg_window = tk.Toplevel(self.root)
        reg_window.title("Event Registration")
        reg_window.geometry("400x500")
        reg_window.configure(bg="#6EC207")

        tk.Label(reg_window, text="Event Registration", font=("Arial", 16, "bold"), bg="#6EC207", fg="#ECF0F1").pack(pady=10)

        # Registration Fields
        fields = {
            "Full Name": tk.StringVar(),
            "Email": tk.StringVar(value=self.user_email),
            "Phone": tk.StringVar(),
            "Address": tk.StringVar()
        }

        # Generate Ticket ID
        ticket_id = f"T-{random.randint(100000, 999999)}"

        for field_name, field_var in fields.items():
            frame = tk.Frame(reg_window, bg="#6EC207")
            frame.pack(pady=5, padx=20, fill=tk.X)

            tk.Label(frame, text=f"{field_name}:", bg="#6EC207", fg="white").pack(side=tk.LEFT)

            entry = tk.Entry(frame, textvariable=field_var, bg="#34495E", fg="white", width=30)
            entry.pack(side=tk.RIGHT)

        # Ticket ID Display
        tk.Label(reg_window, text=f"Ticket ID: {ticket_id}", bg="#6EC207", fg="white").pack(pady=10)

        def submit_registration():
            # Validate inputs
            for field, var in fields.items():
                if not var.get().strip():
                    messagebox.showerror("Error", f"{field} is required")
                    return

            try:
                connection = self.create_connection()
                if not connection:
                    messagebox.showerror("Connection Error", "Failed to establish database connection")
                    return

                cursor = connection.cursor()
                
                cursor.execute("""
                    SELECT COUNT(*) FROM Attendees 
                    WHERE email = %s AND event_id = %s
                """, (fields["Email"].get(), event_id))
                
                registration_count = cursor.fetchone()[0]
                if registration_count > 0:
                    messagebox.showerror("Error", "You are already registered for this event")
                    connection.close()
                    return

                cursor.execute("""
                    INSERT INTO Attendees 
                    (name, email, event_id, attendee_phone, attendee_address, ticket_id) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    fields["Full Name"].get(), 
                    fields["Email"].get(), 
                    event_id, 
                    fields["Phone"].get(), 
                    fields["Address"].get(), 
                    ticket_id
                ))
                connection.commit()
                connection.close()

                # Send confirmation email
                event_details = self.get_event_details(event_id)
                if event_details:
                    email_body = f"""
                    Event Registration Confirmation

                    Event: {event_details['event_name']}
                    Date: {event_details['event_date']}
                    Location: {event_details['location']}

                    Ticket ID: {ticket_id}

                    Thank you for registering!
                    """
                    email_result = self.send_email(
                        fields["Email"].get(), 
                        "Event Registration Confirmation", 
                        email_body
                    )

                messagebox.showinfo("Success", "Registration Successful!")
                reg_window.destroy()

            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Registration failed: {err}")
            except Exception as e:
                messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

        # Submit Button
        tk.Button(reg_window, 
                text="Submit Registration", 
                command=submit_registration, 
                bg="#2980B9", 
                fg="white").pack(pady=10)
    def show_attendee_profile(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Profile Frame
        profile_frame = tk.Frame(self.content_frame, bg="#6EC207")
        profile_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Profile Title
        tk.Label(profile_frame, text="Attendee Profile", font=("Arial", 16, "bold"), bg="#6EC207", fg="#6EC207").pack(pady=10)

        # Profile Fields
        profile_fields = {
            "Full Name": tk.StringVar(),
            "Email": tk.StringVar(value=self.user_email),
            "Phone": tk.StringVar(),
            "Address": tk.StringVar()
        }

        # Load existing profile data
        connection = self.create_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("""
                    SELECT name, attendee_phone, attendee_address 
                    FROM Attendees 
                    WHERE email = %s 
                    LIMIT 1
                """, (self.user_email,))
                profile_data = cursor.fetchone()
                connection.close()

                if profile_data:
                    profile_fields["Full Name"].set(profile_data.get('name', ''))
                    profile_fields["Phone"].set(profile_data.get('attendee_phone', ''))
                    profile_fields["Address"].set(profile_data.get('attendee_address', ''))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load profile: {e}")

        # Create Entry Fields
        for field_name, field_var in profile_fields.items():
            frame = tk.Frame(profile_frame, bg="#6EC207")
            frame.pack(pady=5, padx=20, fill=tk.X)

            tk.Label(frame, text=f"{field_name}:", bg="#6EC207", fg="white", font=("Arial", 10)).pack(side=tk.LEFT)

            entry = tk.Entry(frame, textvariable=field_var, bg="#34495E", fg="white", width=30)
            entry.pack(side=tk.RIGHT)
            
            if field_name == "Email":
                entry.config(state='readonly')

        def update_profile():
            for field, var in profile_fields.items():
                if field != "Email" and not var.get().strip():
                    messagebox.showerror("Error", f"{field} is required")
                    return

            # Update Profile in Database
            connection = self.create_connection()
            if connection:
                try:
                    cursor = connection.cursor()
                    cursor.execute("""
                        UPDATE Attendees 
                        SET name = %s, 
                            attendee_phone = %s, 
                            attendee_address = %s 
                        WHERE email = %s
                    """, (
                        profile_fields["Full Name"].get(),
                        profile_fields["Phone"].get(),
                        profile_fields["Address"].get(),
                        self.user_email
                    ))
                    connection.commit()
                    connection.close()

                    messagebox.showinfo("Success", "Profile Updated Successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Profile update failed: {e}")

        # Update Profile Button
        update_button = tk.Button(
            profile_frame, 
            text="Update Profile", 
            command=update_profile, 
            bg="#2980B9", 
            fg="white"
        )
        update_button.pack(pady=10)
        
    def get_event_details(self, event_id):
        connection = self.create_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM Events WHERE event_id = %s", (event_id,))
                event_details = cursor.fetchone()
                connection.close()
                return event_details
            except Exception as e:
                messagebox.showerror("Error", f"Failed to fetch event details: {e}")
                return None

    def show_registered_events(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        registered_frame = tk.Frame(self.content_frame, bg="#6EC207")
        registered_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Treeview for Registered Events
        columns = ("Event Name", "Date", "Location", "Ticket ID", "Status")
        tree = ttk.Treeview(registered_frame, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor="center")

        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        def load_registered_events():
            connection = self.create_connection()
            if connection:
                try:
                    cursor = connection.cursor()
                    cursor.execute("""
                        SELECT e.event_name, e.event_date, e.location, a.ticket_id, 
                        CASE 
                            WHEN e.event_date > CURRENT_DATE() THEN 'Upcoming'
                            ELSE 'Completed'
                        END as status
                        FROM Attendees a
                        JOIN Events e ON a.event_id = e.event_id
                        WHERE a.email = %s
                    """, (self.user_email,))

                    for item in tree.get_children():
                        tree.delete(item)

                    for event in cursor.fetchall():
                        tree.insert("", "end", values=event)

                    connection.close()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load registered events: {e}")

        load_registered_events()

    def send_email(self, recipient_email, subject, body):

        try:
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = recipient_email
            message["Subject"] = subject
            message.attach(MIMEText(body, "plain"))

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, recipient_email, message.as_string())
            server.quit()

            return True
        except Exception as e:
            messagebox.showerror("Email Error", f"Could not send email: {e}")
            return False

def main():
    root = tk.Tk()
    app = EventManagementSystem(root, user_email="user@example.com")
    root.mainloop()

if __name__ == "__main__":
    main()
