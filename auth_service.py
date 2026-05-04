class AuthService:
    def authenticate(self, email: str, password: str):
        return email == "admin@example.com" and password == "1234"