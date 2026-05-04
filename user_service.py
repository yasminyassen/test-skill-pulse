class UserService:
    def __init__(self, repo):
        self.repo = repo

    def get_user(self, user_id: int):
        return self.repo.find_by_id(user_id)

    def create_user(self, user_data: dict):
        self._validate(user_data)
        return self.repo.save(user_data)

    def _validate(self, data):
        if "email" not in data:
            raise ValueError("Email required")