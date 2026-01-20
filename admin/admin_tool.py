"""
MFA Admin Tool - Tkinter GUI for managing users and Aadhaar-Email mappings.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import sys
import re

# Add backend to path for imports
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# MongoDB sync client (Tkinter doesn't play well with async)
from pymongo import MongoClient
import bcrypt


class AdminTool:
    """Main admin tool application."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("MFA Admin Panel")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Password hashing (using bcrypt directly)
        
        # MongoDB connection
        self.client = None
        self.db = None
        self.connect_to_mongodb()
        
        # Create UI
        self.create_ui()
    
    def connect_to_mongodb(self):
        """Connect to MongoDB."""
        try:
            # Try to load from .env, fall back to defaults
            mongodb_url = "mongodb://localhost:27017"
            database_name = "mfa_auth_db"
            
            self.client = MongoClient(mongodb_url)
            self.db = self.client[database_name]
            
            # Test connection
            self.client.admin.command('ping')
            print(f"Connected to MongoDB: {database_name}")
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not connect to MongoDB:\n{e}")
    
    def create_ui(self):
        """Create the main UI with tabs."""
        # Style configuration
        style = ttk.Style()
        style.configure("TNotebook.Tab", padding=[20, 10])
        style.configure("TButton", padding=[10, 5])
        style.configure("Header.TLabel", font=("Helvetica", 16, "bold"))
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = ttk.Label(main_frame, text="MFA Admin Panel", style="Header.TLabel")
        header.pack(pady=(0, 10))
        
        # Notebook (tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_add_user_tab()
        self.create_add_aadhaar_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, pady=(10, 0))
    
    def create_add_user_tab(self):
        """Create the Add User tab."""
        tab = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(tab, text="Add User")
        
        # Form fields
        fields_frame = ttk.Frame(tab)
        fields_frame.pack(fill=tk.X)
        
        # Email
        ttk.Label(fields_frame, text="Email:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.email_var, width=40).grid(row=0, column=1, pady=5, padx=5)
        
        # Name
        ttk.Label(fields_frame, text="Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.name_var, width=40).grid(row=1, column=1, pady=5, padx=5)
        
        # Password
        ttk.Label(fields_frame, text="Password:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.password_var, width=40, show="*").grid(row=2, column=1, pady=5, padx=5)
        
        # Aadhaar ID
        ttk.Label(fields_frame, text="Aadhaar ID:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.aadhaar_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.aadhaar_var, width=40).grid(row=3, column=1, pady=5, padx=5)
        
        # Phone
        ttk.Label(fields_frame, text="Phone (+91):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.phone_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.phone_var, width=40).grid(row=4, column=1, pady=5, padx=5)
        
        # Submit button
        submit_btn = ttk.Button(tab, text="Add User to Database", command=self.add_user)
        submit_btn.pack(pady=20)
    
    def create_add_aadhaar_tab(self):
        """Create the Add Aadhaar-Email tab."""
        tab = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(tab, text="Add Aadhaar-Email")
        
        # Form fields
        fields_frame = ttk.Frame(tab)
        fields_frame.pack(fill=tk.X)
        
        # Aadhaar ID
        ttk.Label(fields_frame, text="Aadhaar ID:").grid(row=0, column=0, sticky=tk.W, pady=10)
        self.aadhaar_link_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.aadhaar_link_var, width=40).grid(row=0, column=1, pady=10, padx=5)
        
        # Email
        ttk.Label(fields_frame, text="Email:").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.email_link_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.email_link_var, width=40).grid(row=1, column=1, pady=10, padx=5)
        
        # Info text
        info_text = """
This simulates the Aadhaar registry where email addresses are linked to Aadhaar IDs.

During OTP verification, the system looks up the email address 
associated with the user's Aadhaar ID and sends the OTP to that email.
        """
        info_label = ttk.Label(tab, text=info_text, wraplength=500, justify=tk.LEFT)
        info_label.pack(pady=20)
        
        # Submit button
        submit_btn = ttk.Button(tab, text="Add Aadhaar-Email Link", command=self.add_aadhaar_email)
        submit_btn.pack(pady=20)
        
        # Separator
        ttk.Separator(tab, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)
        
        # View existing entries
        ttk.Label(tab, text="Existing Aadhaar-Email Links:", font=("Helvetica", 10, "bold")).pack(anchor=tk.W)
        
        # Treeview for existing entries
        columns = ("aadhaar_id", "email")
        self.aadhaar_tree = ttk.Treeview(tab, columns=columns, show="headings", height=5)
        self.aadhaar_tree.heading("aadhaar_id", text="Aadhaar ID")
        self.aadhaar_tree.heading("email", text="Email Address")
        self.aadhaar_tree.pack(fill=tk.X, pady=10)
        
        # Refresh button
        refresh_btn = ttk.Button(tab, text="Refresh List", command=self.refresh_aadhaar_list)
        refresh_btn.pack()
        
        # Initial load
        self.refresh_aadhaar_list()
    
    def validate_email(self, email):
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_aadhaar(self, aadhaar):
        """Validate Aadhaar ID (16 digits)."""
        return re.match(r'^\d{16}$', aadhaar) is not None
    
    def validate_phone(self, phone):
        """Validate phone number (+91 followed by 10 digits)."""
        return re.match(r'^\+91\d{10}$', phone) is not None
    
    def add_user(self):
        """Add user to the database."""
        # Get values
        email = self.email_var.get().strip()
        name = self.name_var.get().strip()
        password = self.password_var.get()
        aadhaar = self.aadhaar_var.get().strip()
        phone = self.phone_var.get().strip()
        
        # Validate
        errors = []
        
        if not email or not self.validate_email(email):
            errors.append("Invalid email address")
        
        if not name:
            errors.append("Name is required")
        
        if len(password) < 6:
            errors.append("Password must be at least 6 characters")
        
        if not self.validate_aadhaar(aadhaar):
            errors.append("Aadhaar ID must be 16 digits")
        
        if not self.validate_phone(phone):
            errors.append("Phone must be in format +91XXXXXXXXXX")
        
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return
        
        # Check if user already exists
        if self.db.users.find_one({"email": email}):
            messagebox.showerror("Error", "A user with this email already exists")
            return
        
        if self.db.users.find_one({"aadhaar_id": aadhaar}):
            messagebox.showerror("Error", "A user with this Aadhaar ID already exists")
            return
        
        # Create user document
        # Hash password using bcrypt directly
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
        
        user_doc = {
            "email": email,
            "name": name,
            "password_hash": password_hash,
            "aadhaar_id": aadhaar,
            "phone_no": phone
        }
        
        try:
            self.db.users.insert_one(user_doc)
            self.status_var.set(f"User '{name}' added successfully!")
            messagebox.showinfo("Success", f"User '{name}' has been added to the database.")
            
            # Clear form
            self.email_var.set("")
            self.name_var.set("")
            self.password_var.set("")
            self.aadhaar_var.set("")
            self.phone_var.set("")
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not add user:\n{e}")
    
    def add_aadhaar_email(self):
        """Add Aadhaar-Email link to the database."""
        aadhaar = self.aadhaar_link_var.get().strip()
        email = self.email_link_var.get().strip()
        
        # Validate
        errors = []
        
        if not self.validate_aadhaar(aadhaar):
            errors.append("Aadhaar ID must be 16 digits")
        
        if not email or not self.validate_email(email):
            errors.append("Invalid email address")
        
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return
        
        # Check if entry already exists
        if self.db.aadhaar_phone.find_one({"aadhaar_id": aadhaar}):
            # Update existing
            result = messagebox.askyesno(
                "Entry Exists",
                "An entry for this Aadhaar ID already exists. Update the email address?"
            )
            if result:
                self.db.aadhaar_phone.update_one(
                    {"aadhaar_id": aadhaar},
                    {"$set": {"email": email}}
                )
                self.status_var.set("Aadhaar-Email link updated!")
                messagebox.showinfo("Success", "Aadhaar-Email link has been updated.")
            return
        
        # Create document
        doc = {
            "aadhaar_id": aadhaar,
            "email": email
        }
        
        try:
            self.db.aadhaar_phone.insert_one(doc)
            self.status_var.set("Aadhaar-Email link added!")
            messagebox.showinfo("Success", "Aadhaar-Email link has been added.")
            
            # Clear form and refresh list
            self.aadhaar_link_var.set("")
            self.email_link_var.set("")
            self.refresh_aadhaar_list()
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not add link:\n{e}")
    
    def refresh_aadhaar_list(self):
        """Refresh the Aadhaar-Email list."""
        # Clear existing items
        for item in self.aadhaar_tree.get_children():
            self.aadhaar_tree.delete(item)
        
        # Load from database
        try:
            entries = self.db.aadhaar_phone.find()
            for entry in entries:
                # Handle both old (phone_no) and new (email) formats
                email_value = entry.get("email") or entry.get("phone_no", "N/A")
                self.aadhaar_tree.insert("", tk.END, values=(
                    entry["aadhaar_id"],
                    email_value
                ))
        except Exception as e:
            print(f"Error loading Aadhaar-Email list: {e}")
    
    def on_closing(self):
        """Handle window close."""
        if self.client:
            self.client.close()
        self.root.destroy()


def main():
    """Main entry point."""
    root = tk.Tk()
    app = AdminTool(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()

