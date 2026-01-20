"""
MFA Admin Tool - Tkinter GUI for managing users and Aadhaar-Phone mappings.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import sys
import re

# Add backend to path for imports
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from PIL import Image, ImageTk
import io

# MongoDB sync client (Tkinter doesn't play well with async)
from pymongo import MongoClient
from passlib.context import CryptContext

# Try to import face_recognition
try:
    import face_recognition
    import numpy as np
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("WARNING: face_recognition not available. Face encoding will be simulated.")


class AdminTool:
    """Main admin tool application."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("MFA Admin Panel")
        self.root.geometry("600x700")
        self.root.resizable(True, True)
        
        # Password hashing
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # MongoDB connection
        self.client = None
        self.db = None
        self.connect_to_mongodb()
        
        # Selected image path
        self.selected_image_path = None
        self.face_encoding = None
        
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
        
        # Image section
        image_frame = ttk.LabelFrame(tab, text="Face Photo", padding="10")
        image_frame.pack(fill=tk.X, pady=20)
        
        # Browse button
        browse_btn = ttk.Button(image_frame, text="Browse Image...", command=self.browse_image)
        browse_btn.pack(side=tk.LEFT)
        
        # Image path label
        self.image_path_var = tk.StringVar(value="No image selected")
        ttk.Label(image_frame, textvariable=self.image_path_var).pack(side=tk.LEFT, padx=10)
        
        # Image preview frame
        preview_frame = ttk.Frame(tab)
        preview_frame.pack(fill=tk.X, pady=10)
        
        # Image preview label
        self.image_preview = ttk.Label(preview_frame, text="Image Preview")
        self.image_preview.pack()
        
        # Face detection status
        self.face_status_var = tk.StringVar(value="")
        self.face_status_label = ttk.Label(preview_frame, textvariable=self.face_status_var)
        self.face_status_label.pack(pady=5)
        
        # Submit button
        submit_btn = ttk.Button(tab, text="Add User to Database", command=self.add_user)
        submit_btn.pack(pady=20)
    
    def create_add_aadhaar_tab(self):
        """Create the Add Aadhaar-Phone tab."""
        tab = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(tab, text="Add Aadhaar-Phone")
        
        # Form fields
        fields_frame = ttk.Frame(tab)
        fields_frame.pack(fill=tk.X)
        
        # Aadhaar ID
        ttk.Label(fields_frame, text="Aadhaar ID:").grid(row=0, column=0, sticky=tk.W, pady=10)
        self.aadhaar_link_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.aadhaar_link_var, width=40).grid(row=0, column=1, pady=10, padx=5)
        
        # Phone
        ttk.Label(fields_frame, text="Phone (+91):").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.phone_link_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.phone_link_var, width=40).grid(row=1, column=1, pady=10, padx=5)
        
        # Info text
        info_text = """
This simulates the Aadhaar registry where phone numbers are linked to Aadhaar IDs.

During OTP verification, the system looks up the phone number 
associated with the user's Aadhaar ID and sends the OTP to that number.
        """
        info_label = ttk.Label(tab, text=info_text, wraplength=500, justify=tk.LEFT)
        info_label.pack(pady=20)
        
        # Submit button
        submit_btn = ttk.Button(tab, text="Add Aadhaar-Phone Link", command=self.add_aadhaar_phone)
        submit_btn.pack(pady=20)
        
        # Separator
        ttk.Separator(tab, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)
        
        # View existing entries
        ttk.Label(tab, text="Existing Aadhaar-Phone Links:", font=("Helvetica", 10, "bold")).pack(anchor=tk.W)
        
        # Treeview for existing entries
        columns = ("aadhaar_id", "phone_no")
        self.aadhaar_tree = ttk.Treeview(tab, columns=columns, show="headings", height=5)
        self.aadhaar_tree.heading("aadhaar_id", text="Aadhaar ID")
        self.aadhaar_tree.heading("phone_no", text="Phone Number")
        self.aadhaar_tree.pack(fill=tk.X, pady=10)
        
        # Refresh button
        refresh_btn = ttk.Button(tab, text="Refresh List", command=self.refresh_aadhaar_list)
        refresh_btn.pack()
        
        # Initial load
        self.refresh_aadhaar_list()
    
    def browse_image(self):
        """Open file dialog to select an image."""
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"),
            ("All files", "*.*")
        ]
        
        filepath = filedialog.askopenfilename(
            title="Select Face Photo",
            filetypes=filetypes
        )
        
        if filepath:
            self.selected_image_path = filepath
            self.image_path_var.set(Path(filepath).name)
            self.load_and_process_image(filepath)
    
    def load_and_process_image(self, filepath):
        """Load image, show preview, and extract face encoding."""
        try:
            # Load and resize for preview
            image = Image.open(filepath)
            
            # Resize for preview (max 200x200)
            image.thumbnail((200, 200))
            
            # Convert to PhotoImage for display
            photo = ImageTk.PhotoImage(image)
            self.image_preview.configure(image=photo)
            self.image_preview.image = photo  # Keep reference
            
            # Extract face encoding
            self.extract_face_encoding(filepath)
            
        except Exception as e:
            messagebox.showerror("Image Error", f"Could not load image:\n{e}")
    
    def extract_face_encoding(self, filepath):
        """Extract face encoding from the image."""
        self.face_encoding = None
        
        if not FACE_RECOGNITION_AVAILABLE:
            # Simulate face detection
            self.face_encoding = [0.0] * 128
            self.face_status_var.set("⚠ Face detection simulated (library not available)")
            return
        
        try:
            # Load image with face_recognition
            image = face_recognition.load_image_file(filepath)
            
            # Find faces
            face_locations = face_recognition.face_locations(image)
            
            if not face_locations:
                self.face_status_var.set("❌ No face detected in image")
                return
            
            if len(face_locations) > 1:
                self.face_status_var.set(f"⚠ Multiple faces detected ({len(face_locations)}). Using first face.")
            else:
                self.face_status_var.set("✓ Face detected successfully")
            
            # Get encoding
            encodings = face_recognition.face_encodings(image, face_locations)
            
            if encodings:
                self.face_encoding = encodings[0].tolist()
            else:
                self.face_status_var.set("❌ Could not extract face encoding")
                
        except Exception as e:
            self.face_status_var.set(f"❌ Error: {str(e)}")
    
    def validate_email(self, email):
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_aadhaar(self, aadhaar):
        """Validate Aadhaar ID (12 digits)."""
        return re.match(r'^\d{12}$', aadhaar) is not None
    
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
            errors.append("Aadhaar ID must be 12 digits")
        
        if not self.validate_phone(phone):
            errors.append("Phone must be in format +91XXXXXXXXXX")
        
        if self.face_encoding is None:
            errors.append("Please select an image with a detectable face")
        
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
        user_doc = {
            "email": email,
            "name": name,
            "password_hash": self.pwd_context.hash(password),
            "aadhaar_id": aadhaar,
            "phone_no": phone,
            "face_encoding": self.face_encoding
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
            self.image_path_var.set("No image selected")
            self.face_status_var.set("")
            self.image_preview.configure(image="")
            self.selected_image_path = None
            self.face_encoding = None
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not add user:\n{e}")
    
    def add_aadhaar_phone(self):
        """Add Aadhaar-Phone link to the database."""
        aadhaar = self.aadhaar_link_var.get().strip()
        phone = self.phone_link_var.get().strip()
        
        # Validate
        errors = []
        
        if not self.validate_aadhaar(aadhaar):
            errors.append("Aadhaar ID must be 12 digits")
        
        if not self.validate_phone(phone):
            errors.append("Phone must be in format +91XXXXXXXXXX")
        
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return
        
        # Check if entry already exists
        if self.db.aadhaar_phone.find_one({"aadhaar_id": aadhaar}):
            # Update existing
            result = messagebox.askyesno(
                "Entry Exists",
                "An entry for this Aadhaar ID already exists. Update the phone number?"
            )
            if result:
                self.db.aadhaar_phone.update_one(
                    {"aadhaar_id": aadhaar},
                    {"$set": {"phone_no": phone}}
                )
                self.status_var.set("Aadhaar-Phone link updated!")
                messagebox.showinfo("Success", "Aadhaar-Phone link has been updated.")
            return
        
        # Create document
        doc = {
            "aadhaar_id": aadhaar,
            "phone_no": phone
        }
        
        try:
            self.db.aadhaar_phone.insert_one(doc)
            self.status_var.set("Aadhaar-Phone link added!")
            messagebox.showinfo("Success", "Aadhaar-Phone link has been added.")
            
            # Clear form and refresh list
            self.aadhaar_link_var.set("")
            self.phone_link_var.set("")
            self.refresh_aadhaar_list()
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not add link:\n{e}")
    
    def refresh_aadhaar_list(self):
        """Refresh the Aadhaar-Phone list."""
        # Clear existing items
        for item in self.aadhaar_tree.get_children():
            self.aadhaar_tree.delete(item)
        
        # Load from database
        try:
            entries = self.db.aadhaar_phone.find()
            for entry in entries:
                self.aadhaar_tree.insert("", tk.END, values=(
                    entry["aadhaar_id"],
                    entry["phone_no"]
                ))
        except Exception as e:
            print(f"Error loading Aadhaar-Phone list: {e}")
    
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

