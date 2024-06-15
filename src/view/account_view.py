# login_popup.py

import customtkinter

from utilities.auth_client import AuthClient


class AccountPopup(customtkinter.CTkToplevel):
    def __init__(self, master, auth_client, controller):
        super().__init__(master)
        self.auth_client = auth_client
        self.controller = controller
        self.geometry("600x500")
        self.title("Account")
        self.focus_set()
        self.logged_in_user = self.auth_client.get_user()

        if self.logged_in_user:
            self.licenses = self.auth_client.get_licenses()
            print(self.logged_in_user.json().get("name"))
            self.logged_in_view(self.logged_in_user.json())
        else:
            self.login_form()

    def submit_credentials(self):
        email = self.entry_email.get()
        password = self.entry_password.get()
        try:
            user_data = self.auth_client.login_and_get_token(email, password)  # This should return the user data
            if user_data:
                self.destroy()
                self.controller.update_login(user_data)  # Notify the controller about the successful login
                print("Login successful")
        except Exception as e:
            print(f"Login failed: {e}")

    def login_form(self):
        self.clear_widgets()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Email Entry
        self.entry_email = customtkinter.CTkEntry(master=self)
        label_email = customtkinter.CTkLabel(master=self, text="Email:")
        label_email.grid(row=0, column=0, padx=20, pady=10)
        self.entry_email.grid(row=1, column=0, padx=20, pady=10)

        # Password Entry
        self.entry_password = customtkinter.CTkEntry(master=self, show="*")
        label_password = customtkinter.CTkLabel(master=self, text="Password:")
        label_password.grid(row=2, column=0, padx=20, pady=10)
        self.entry_password.grid(row=3, column=0, padx=20, pady=10)

        # Submit Button
        btn_submit = customtkinter.CTkButton(master=self, text="Submit", command=self.submit_credentials)
        btn_submit.grid(row=4, column=0, padx=20, pady=20)

    def logged_in_view(self, user):
        name = user.get("name")
        id = user.get("id")
        email = user.get("email")

        self.clear_widgets()

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Welcome Label
        welcome_label = customtkinter.CTkLabel(master=self, text=f"Welcome, {name}({id})!", font=("Arial", 18))
        welcome_label.grid(row=0, column=0, columnspan=2, padx=20, pady=10)

        # Licenses Label
        label_licenses = customtkinter.CTkLabel(master=self, text="Your Licenses:")
        label_licenses.grid(row=1, column=0, padx=20, pady=10)

        # License List
        licenses = self.licenses
        license_text = ""
        for license in licenses.json():
            print(license)
            product = license["licensable"]["product"]
            license_text += f"Product: {product['name']}\n"
            license_text += f"Expiration Date: {license['expiration_date']}\n\n"

        licenses_label = customtkinter.CTkLabel(master=self, text=license_text, justify="left")
        licenses_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")

        # Account Details Label
        label_account = customtkinter.CTkLabel(master=self, text="Account Details:")
        label_account.grid(row=1, column=1, padx=20, pady=10)

        # Account Details
        account_details = f"Email: {email}\n"  # Add other account details if needed
        account_label = customtkinter.CTkLabel(master=self, text=account_details, justify="left")
        account_label.grid(row=2, column=1, padx=20, pady=10)

        # Logout Button
        btn_logout = customtkinter.CTkButton(master=self, text="Logout", command=self.logout)
        btn_logout.grid(row=3, column=0, columnspan=2, padx=20, pady=20)

    def logout(self):
        self.auth_client.logout()  # Assuming this method logs out the user
        # self.controller.update_login(None)  # Notify the controller about the logout
        self.destroy()
        print("Logged out successfully")

    def clear_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()
