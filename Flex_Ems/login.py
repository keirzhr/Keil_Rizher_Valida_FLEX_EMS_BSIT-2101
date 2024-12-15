from tkinter import *
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
from tkinter import Tk, Label
import mysql.connector
from hashlib import sha256
import traceback
import os
import subprocess
import re
import sys
import json

# Global variables for entries
user = None
code = None
reg_full_name = None
reg_user = None
reg_email = None
reg_phone = None
reg_pass = None
user_to_delete = None
admin_pass = None
profile_pic_path = None

# MySQL Database Connection
def connect_db():
    try:
        connection  = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="flex_ems"
        )
        return connection
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error connecting to the database: {err}")
        return None

def hash_password(password):
    full_hash = sha256(password.encode()).hexdigest()
    return full_hash[:16] 

hashed_password = hash_password("your_password_here")
print(hashed_password)

# Validate Email
def validate_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

# Validate Phone Number
def validate_phone(phone):  
    # Validate phone number     (11 digits)
    phone_regex = r'^\d{11}$'
    return re.match(phone_regex, phone) is not None

# Upload Photo
def upload_photo():
    global profile_pic_path

    file_path = filedialog.askopenfilename(
        title="Select Profile Photo",
        filetypes=[
            ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg *.jpeg")
        ] 
    )
    
    if file_path:
        try:
            img = Image.open(file_path)
            img.thumbnail((200, 200))
            
            uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
            os.makedirs(uploads_dir, exist_ok=True)
            
            original_name = os.path.basename(file_path)
            name, ext = os.path.splitext(original_name)
            
            filename = original_name
            counter = 1
            while os.path.exists(os.path.join(uploads_dir, filename)):
                filename = f"{name}_{counter}{ext}"
                counter += 1
            
            save_path = os.path.join(uploads_dir, filename)
            
            # Save the resized image
            img.save(save_path)
            
            # Convert save_path to a relative path for database storage
            profile_pic_path = os.path.join("uploads", filename)

            print("Original File Path:", file_path)
            print("Saved File Path:", save_path)
            print("Relative Path for Database:", profile_pic_path)

            photo_label.config(text=f"Uploaded: {filename}", image='', width=17)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload photo: {e}")
            traceback.print_exc()

# Delete User
def delete_user():
    global user_to_delete, admin_pass
    username_to_delete = user_to_delete.get().strip()
    user_password = admin_pass.get().strip()

    if not username_to_delete or not user_password:
        messagebox.showwarning("Validation Error", "Please fill in all fields!")
        return

    connection = connect_db()
    if not connection:
        messagebox.showerror("Connection Error", "Failed to connect to the database.")
        return

    try:
        cursor = connection.cursor()

        cursor.execute("SELECT password FROM users WHERE username = %s", (username_to_delete,))
        result = cursor.fetchone()

        if not result:
            messagebox.showerror("Error", f"User '{username_to_delete}' does not exist!")
            return

        # Validate the provided password (for the admin)
        stored_password_hash = result[0]
        if hash_password(user_password) != stored_password_hash:
            messagebox.showerror("Error", "Incorrect password!")
            return

        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete the user '{username_to_delete}'?\n\nThis action cannot be undone.",
            icon='warning'
        )

        if not confirm:
            return

        # Delete the user
        cursor.execute("DELETE FROM users WHERE username = %s", (username_to_delete,))
        connection.commit()

        if cursor.rowcount > 0:
            messagebox.showinfo("Success", f"User '{username_to_delete}' deleted successfully!")
            
            # Clear the fields after deletion
            if user_to_delete.winfo_exists():
                user_to_delete.delete(0, 'end')  # Clear the username field
            if admin_pass.winfo_exists():
                admin_pass.delete(0, 'end')  # Clear the admin password field

        else:
            messagebox.showwarning("Not Found", f"User '{username_to_delete}' does not exist!")

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"An error occurred: {err}")
    except Exception as e:
        messagebox.showerror("Unexpected Error", f"Unexpected error: {str(e)}")
    finally:
        connection.close()

# Show Delete User View
def show_delete_user_view():
    global user_to_delete, admin_pass
    # Clear current frame
    for widget in frame.winfo_children():
        widget.destroy()
    
    # Create delete user container
    delete_frame = Frame(frame, bg='#1A1A19')
    delete_frame.pack(pady=70, padx=80)

    # Heading
    heading = Label(delete_frame, text='Delete User', fg='#FF4500', bg='#1A1A19', font=('Roboto', 32, 'bold'))
    heading.pack(pady=(0, 30))

    # Username to Delete Section
    username_label = Label(delete_frame, text='Username to Delete', fg='#FFFFFF', bg='#1A1A19', font=('Arial', 10))
    username_label.pack(anchor='w', pady=(0, 5))
    user_to_delete = Entry(delete_frame, width=40, fg="white", bg='#2C2C2C', font=('Arial', 12),insertbackground="white",
                           bd=0, relief=FLAT, highlightthickness=10, highlightcolor='#FF4500', highlightbackground='#2C2C2C')
    user_to_delete.pack(fill='x', pady=(0, 15))
    user_to_delete.insert(0, "Enter Username to Delete")
    user_to_delete.bind("<FocusIn>", lambda e: on_enter(user_to_delete, "Enter Username to Delete"))
    user_to_delete.bind("<FocusOut>", lambda e: on_leave(user_to_delete, "Enter Username to Delete"))

    # Password Section
    password_label = Label(delete_frame, text='Confirm Password', fg='#FFFFFF', bg='#1A1A19', font=('Arial', 10))
    password_label.pack(anchor='w', pady=(0, 5))
    admin_pass = Entry(delete_frame, width=40, fg="white", bg='#2C2C2C', font=('Arial', 12), insertbackground="white",
                       bd=0, relief=FLAT, highlightthickness=10, highlightcolor='#FF4500', highlightbackground='#2C2C2C', show="*")
    admin_pass.pack(fill='x', pady=(0, 20))
    admin_pass.insert(0, "Enter Password")
    admin_pass.bind("<FocusIn>", lambda e: on_enter(admin_pass, "Enter Password"))
    admin_pass.bind("<FocusOut>", lambda e: on_leave(admin_pass, "Enter Password"))

    # Delete Button
    delete_btn = Button(delete_frame, text='Delete', width=30, bg='red', fg='white', font=('Segoe UI', 13, 'bold'), command=delete_user, relief=FLAT)
    delete_btn.pack(pady=(0, 15))

    # Back to Login Button
    back_btn = Button(delete_frame, text='Back to Login', fg='white', bg='green', font=('Arial', 11), command=show_login_view, relief=FLAT)
    back_btn.pack(pady=(10, 0))
    
# for login 
current_dir = os.path.dirname(os.path.abspath(__file__))
flex_ems_path = os.path.join(current_dir, 'flex_ems.py')

def validate_login():
    # Get input from user interface
    username = user.get().strip()  # Replace with appropriate widget reference
    password = code.get().strip()  # Replace with appropriate widget reference

    # Validate input
    if not username or username == "Username" or not password or password == "Password":
        messagebox.showwarning("Validation Error", "Please enter a valid username and password.")
        return

    connection = connect_db()  # Ensure this function is defined and connects to your DB
    if not connection:
        messagebox.showerror("Database Error", "Unable to connect to the database.")
        return

    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT user_id, username, full_name, email, phone, profile_pic, password
            FROM users 
            WHERE username = %s AND password = %s
        """
        cursor.execute(query, (username, hash_password(password)))  # Ensure `hash_password` is defined
        user_details = cursor.fetchone()

        if user_details:
            messagebox.showinfo("Success", f"Welcome, {user_details['full_name']}!")

            # Pass user details to the next script
            if os.path.exists(flex_ems_path):  # Ensure `flex_ems_path` is defined
                subprocess.Popen([sys.executable, flex_ems_path, json.dumps(user_details)])
                root.destroy()  # Close the current window
            else:
                messagebox.showerror("Error", f"Could not find {flex_ems_path}. Please check the file path.")
        else:   
            messagebox.showerror("Login Failed", "Invalid username or password.")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Database error: {err}")
    finally:
        connection.close()


# Login Section
def show_login_view():
    global user, code
    for widget in frame.winfo_children():
        widget.destroy()
    
    login_frame = Frame(frame, bg='#1A1A19')
    login_frame.pack(pady=70, padx=80)

    # Heading
    heading = Label(login_frame, text='Log In', fg='#6EC207', bg='#1A1A19', font=('Roboto', 32, 'bold'))
    heading.pack(pady=(0, 30))

    # Username Section
    username_label = Label(login_frame, text='Username', fg='#FFFFFF', bg='#1A1A19', font=('Arial', 10))
    username_label.pack(anchor='w', pady=(0, 5))
    user = Entry(login_frame, width=40, fg="white", bg='#2C2C2C', font=('Arial', 12), insertbackground="white",
                 bd=0, relief=FLAT, highlightthickness=10, highlightcolor='#6EC207', highlightbackground='#2C2C2C')
    user.pack(fill='x', pady=(0, 15))
    user.insert(0, "Enter Username")
    user.bind("<FocusIn>", lambda e: on_enter(user, "Enter Username"))
    user.bind("<FocusOut>", lambda e: on_leave(user, "Enter Username"))

    # Password Section
    password_label = Label(login_frame, text='Password', fg='#FFFFFF', bg='#1A1A19', font=('Arial', 10))
    password_label.pack(anchor='w', pady=(0, 5))
    code = Entry(login_frame, width=40, fg="white", bg='#2C2C2C', font=('Arial', 12), insertbackground="white",
                 bd=0, relief=FLAT, highlightthickness=10, highlightcolor='#6EC207', highlightbackground='#2C2C2C', show="*")
    code.pack(fill='x', pady=(0, 20))
    code.insert(0, "Enter Password")
    code.bind("<FocusIn>", lambda e: on_enter(code, "Enter Password"))
    code.bind("<FocusOut>", lambda e: on_leave(code, "Enter Password"))

    # Login Button
    login_btn = Button(login_frame, text='Log In', width=30, bg='#6EC207', fg='white', font=('Segoe UI', 13, 'bold'), command=validate_login, relief=FLAT)
    login_btn.pack(pady=(0, 15))

    # Button Frame for additional options
    button_frame = Frame(login_frame, bg='#1A1A19')
    button_frame.pack(fill='x', pady=(10, 0))

    # Register and Delete User Buttons
    register_btn = Button(button_frame, text='Register User', fg='white', bg='#023E8A', font=('Arial', 11), command=show_register_view, relief=FLAT)
    register_btn.pack(side=LEFT, expand=True, padx=10)

    delete_btn = Button(button_frame, text='Delete User', fg='white', bg='#FF4500', font=('Arial', 11), command=show_delete_user_view, relief=FLAT)
    delete_btn.pack(side=LEFT, expand=True, padx=10)
    
# Show Register View
def register_user():
    global reg_full_name, reg_user, reg_email, reg_phone, reg_pass, profile_pic_path
    
    # Collect input values
    full_name = reg_full_name.get().strip()
    username = reg_user.get().strip()
    email = reg_email.get().strip()
    phone = reg_phone.get().strip()
    password = reg_pass.get().strip()
    errors = []
    
    # Full Name
    if not full_name or full_name == "Enter Full Name":
        errors.append("Please enter a valid full name")
    
    # Username
    if not username or username == "Enter Username":
        errors.append("Please enter a valid username")
    
    # Email
    if not email or email == "Enter Email" or not validate_email(email):
        errors.append("Please enter a valid email address")
    
    # Phone
    if not phone or phone == "Enter Phone Number" or not validate_phone(phone):
        errors.append("Please enter a valid 11-digit phone number")
    
    # Password
    if not password or password == "Enter Password":
        errors.append("Please enter a password")
    
    # Photo
    if not profile_pic_path:
        errors.append("Please upload a profile picture")
    
    # Display errors
    if errors:
        messagebox.showwarning("Validation Error", "\n".join(errors))
        return
    
    # Now proceed to database insertion
    connection = connect_db()
    if not connection:
        messagebox.showerror("Connection Error", "Failed to connect to the database")
        return

    try:
        cursor = connection.cursor()

        # Check if username already exists  
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            messagebox.showwarning("Username Taken", "The username is already taken. Please choose another.")
            return
        
        # Insert user data into the database
        insert_query = """
            INSERT INTO users (username, password, full_name, email, phone, profile_pic) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            username, 
            hash_password(password), 
            full_name,
            email,
            phone,
            profile_pic_path
        ))
        
        connection.commit()
        
        # Success message
        messagebox.showinfo("Success", "User registered successfully!")
        show_login_view()
        
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
        print(f"Detailed Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

#keil
def show_register_view():
    global reg_full_name, reg_user, reg_email, reg_phone, reg_pass, photo_label

    for widget in frame.winfo_children():
        widget.destroy()

    main_container = Frame(frame, bg='#1A1A19')
    main_container.pack(pady=50, fill='x') 

    # Heading
    heading = Label(main_container, text='Register New User', padx=90, fg='#2196F3', bg='#1A1A19', font=('Roboto', 30, 'bold'))
    heading.pack(pady=(20, 20), anchor='w')

    row_container = Frame(main_container, bg='#1A1A19')
    row_container.pack(fill='x', anchor='w')

    left_column = Frame(row_container, bg='#1A1A19', padx=10)
    left_column.pack(side=LEFT, expand=True, fill='x', anchor='w') 

    # Full Name Field
    full_name_label = Label(left_column, text='Full Name', fg='#FFFFFF', bg='#1A1A19', font=('Arial', 10))
    full_name_label.pack(anchor='w', pady=(0, 5))
    reg_full_name = Entry(left_column, width=25, fg="white", bg='#2C2C2C', font=('Arial', 12), insertbackground="white", 
                          bd=0, relief=FLAT, highlightthickness=10, highlightcolor='#2196F3', highlightbackground='#2C2C2C')
    reg_full_name.pack(fill='x', pady=(0, 15))
    reg_full_name.insert(0, "Enter Full Name")
    reg_full_name.bind("<FocusIn>", lambda e: on_enter(reg_full_name, "Enter Full Name"))
    reg_full_name.bind("<FocusOut>", lambda e: on_leave(reg_full_name, "Enter Full Name"))

    # Phone Number Field
    email_label = Label(left_column, text='Email', fg='#FFFFFF', bg='#1A1A19', font=('Arial', 10))
    email_label.pack(anchor='w', pady=(0, 5))
    reg_email = Entry(left_column, width=25, fg="white", bg='#2C2C2C', font=('Arial', 12), insertbackground="white",
                      bd=0, relief=FLAT, highlightthickness=10, highlightcolor='#2196F3', highlightbackground='#2C2C2C')
    reg_email.pack(fill='x', pady=(0, 15))
    reg_email.insert(0, "Enter Email")
    reg_email.bind("<FocusIn>", lambda e: on_enter(reg_email, "Enter Email"))
    reg_email.bind("<FocusOut>", lambda e: on_leave(reg_email, "Enter Email"))
    
    phone_label = Label(left_column, text='Phone Number', fg='#FFFFFF', bg='#1A1A19', font=('Arial', 10))
    phone_label.pack(anchor='w', pady=(0, 5))
    reg_phone = Entry(left_column, width=25, fg="white", bg='#2C2C2C', font=('Arial', 12), insertbackground="white", bd=0, relief=FLAT,
                      highlightthickness=10, highlightcolor='#2196F3', highlightbackground='#2C2C2C')
    reg_phone.pack(fill='x', pady=(0, 15))
    reg_phone.insert(0, "Enter Phone Number")
    reg_phone.bind("<FocusIn>", lambda e: on_enter(reg_phone, "Enter Phone Number"))
    reg_phone.bind("<FocusOut>", lambda e: on_leave(reg_phone, "Enter Phone Number"))

    right_column = Frame(row_container, bg='#1A1A19', padx=10)
    right_column.pack(side=RIGHT, expand=True, fill='x')

    # Username Field
    username_label = Label(right_column, text='Username', fg='#FFFFFF', bg='#1A1A19', font=('Arial', 10))
    username_label.pack(anchor='w', pady=(0, 5))
    reg_user = Entry(right_column, width=25, fg="white", bg='#2C2C2C', font=('Arial', 12), insertbackground="white", 
                     bd=0, relief=FLAT, highlightthickness=10, highlightcolor='#2196F3', highlightbackground='#2C2C2C')
    reg_user.pack(fill='x', pady=(0, 15))
    reg_user.insert(0, "Enter Username")
    reg_user.bind("<FocusIn>", lambda e: on_enter(reg_user, "Enter Username"))
    reg_user.bind("<FocusOut>", lambda e: on_leave(reg_user, "Enter Username"))

    # Password Field
    password_label = Label(right_column, text='Password', fg='#FFFFFF', bg='#1A1A19', font=('Arial', 10))
    password_label.pack(anchor='w', pady=(0, 5))
    reg_pass = Entry(right_column, width=25, fg="white", bg='#2C2C2C', font=('Arial', 12), insertbackground="white", bd=0, relief=FLAT,
                    highlightthickness=10, highlightcolor='#2196F3', highlightbackground='#2C2C2C', show="*")
    reg_pass.pack(fill='x', pady=(0, 15))
    reg_pass.insert(0, "Enter Password")
    reg_pass.bind("<FocusIn>", lambda e: on_enter(reg_pass, "Enter Password"))
    reg_pass.bind("<FocusOut>", lambda e: on_leave(reg_pass, "Enter Password"))

    # Photo Upload Section
    photo_frame = Frame(right_column, bg='#1A1A19')
    photo_frame.pack(fill='x', pady=(0, 15))

    # Upload Photo Button
    upload_btn = Button(photo_frame, text='Upload Photo', command=upload_photo, bg='#2196F3', fg='white', font=('Arial', 11), relief=FLAT)
    upload_btn.pack(padx=(0, 10))

    # Photo Preview 
    photo_label = Label(photo_frame, fg="blue", bg='#1A1A19', font=('Arial', 10))
    photo_label.pack(fill='x', pady=(10, 0))  # Add padding to separate from the button

    # Button Frame
    button_frame = Frame(main_container, bg='#1A1A19')
    button_frame.pack(fill='x', pady=(10, 0))

    # Register Button
    register_btn = Button(button_frame, width=30, text='Register', bg='#2196F3', fg='white', font=('Segoe UI', 13, 'bold'), command=register_user, relief=FLAT)
    register_btn.pack(pady=(0, 10))

    # Back Button
    back_btn = Button(button_frame, text='Back to Login', fg='white', bg='green', font=('Arial', 11), command=show_login_view, relief=FLAT)
    back_btn.pack(pady=(0, 20))

# Placeholder Functions
def on_leave(entry, default_text):
    if not entry.get():
        entry.insert(0, default_text)
        entry.config(fg="white")

def on_enter(entry, default_text):
    if entry.get() == default_text:
        entry.delete(0, "end")
        entry.config(fg="white")

# Main Login Window
root = Tk()
root.title('Registration System')
root.geometry('1080x650+250+110')
root.configure(bg="#1A1A19")
root.resizable(False, False)

try:
    script_dir = os.path.dirname(__file__)
    image_path = os.path.join(script_dir, 'images', 'person.png')
    
    img = Image.open(image_path)
    img = img.resize((270, 270)) 
    img = ImageTk.PhotoImage(img)
    label = Label(root, image=img, bg='#1A1A19')  
    label.image = img
    label.place(x=130, y=180)

except Exception as e:
    print(f"Error loading image: {e}")
    label = Label(root, text="Image not found")
    label.place(x=130, y=180)


frame = Frame(root, width=350, height=600, bg='#1A1A19')
frame.place(x=430, y=60) 

# Start with login view
show_login_view()

root.mainloop() 