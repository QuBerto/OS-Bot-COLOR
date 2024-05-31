import json
import os

import requests


class AuthClient:
    def __init__(self, token_file="token.enc", key_file="secret.key"):
        self.token_file = token_file
        self.key_file = key_file
        self.host = "http://localhost/license/public/api/"
        self.user_endpoint = f"{self.host}user"
        self.login_endpoint = f"{self.host}login"
        self.licenses_endpoint = f"{self.host}check_licenses"
        self.key = self.load_key()

    def generate_key(self):
        key = 3  # You can change this to any integer value for the Caesar cipher
        with open(self.key_file, "w") as key_file:
            key_file.write(str(key))
        return key

    def load_key(self):
        if os.path.exists(self.key_file):
            with open(self.key_file, "r") as key_file:
                return int(key_file.read())
        else:
            return self.generate_key()

    def encrypt(self, message, key):
        encrypted = ""
        for char in message:
            if char.isalpha():
                if char.islower():
                    encrypted += chr((ord(char) - ord("a") + key) % 26 + ord("a"))
                else:
                    encrypted += chr((ord(char) - ord("A") + key) % 26 + ord("A"))
            else:
                encrypted += char
        return encrypted

    def decrypt(self, encrypted_message, key):
        decrypted = ""
        for char in encrypted_message:
            if char.isalpha():
                if char.islower():
                    decrypted += chr((ord(char) - ord("a") - key) % 26 + ord("a"))
                else:
                    decrypted += chr((ord(char) - ord("A") - key) % 26 + ord("A"))
            else:
                decrypted += char
        return decrypted

    def encrypt_token(self, token):
        encrypted_token = self.encrypt(token, self.key)
        with open(self.token_file, "w") as token_file:
            print(f"Encrypted token: {encrypted_token}")
            token_file.write(encrypted_token)

    def decrypt_token(self):
        if os.path.exists(self.token_file):
            with open(self.token_file, "r") as token_file:
                encrypted_token = token_file.read()
            return self.decrypt(encrypted_token, self.key)
        return None

    def login_and_get_token(self, email, password):
        response = requests.post(self.login_endpoint, json={"email": email, "password": password})
        response.raise_for_status()
        token = response.json().get("access_token")
        print(f"Got token: {token}")
        if token:
            self.encrypt_token(token)
        return token

    def verify_token(self, token, return_user=False):
        url = self.user_endpoint  # Endpoint to verify the token
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Accept": "application/json"}
        response = requests.get(url, headers=headers)
        if not return_user:
            return response.status_code == 200
        elif response.status_code == 200:
            return response
        else:
            return response.status_code == 200

    def get_user(self, email=None, password=None):
        token = self.decrypt_token()
        user = self.verify_token(token, return_user=True)
        if token and user:
            print(f"User: {user.json()}")
            return user
        else:
            return False

    def get_user_api(self):
        return self.get_user().json()

    def get_token(self, email=None, password=None):
        token = self.decrypt_token()
        if token and self.verify_token(token):
            print(f"Cached token: {token}")
            return token
        elif email and password:
            print("Getting new token")
            return self.login_and_get_token(email, password)
        else:
            raise ValueError("No valid token available and no credentials provided")

    def make_authenticated_request(self, email=None, password=None):
        print("Get Token")
        token = self.get_token(email, password)
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Accept": "application/json"}
        print("Try login")
        url = self.login_endpoint
        response = requests.get(url, headers=headers)

        if response.status_code == 401:
            print("Login Failed")
            # If unauthorized, try to login again and retry the request once
            if email and password:
                token = self.login_and_get_token(email, password)
                headers["Authorization"] = f"Bearer {token}"
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    print("Login successful, saved new token")
                    return response.json()
                else:
                    print("Login failed again.")
                    response.raise_for_status()
            else:
                raise ValueError("Unauthorized and no credentials provided for reauthentication")

        response.raise_for_status()
        print("Login successful")
        return response.json()


if __name__ == "__main__":
    email = "admin@example.com"
    password = "123qwqw321"

    client = AuthClient()

    # Example API request

    try:
        user_data = client.make_authenticated_request(email, password)
        print("User Data:", json.dumps(user_data, indent=4))
        print("Request successful:", True)
    except Exception as e:
        print("Error:", str(e))
        print("Request successful:", False)
