from . import db
from flask_bcrypt import generate_password_hash, check_password_hash

class User(db.Model):

    __tablename__ = 'users'

    email = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    username = db.Column(db.String(36), unique=True, nullable=False)
    shopping_lists = db.relationship("ShoppingList", back_populates='owner')


    def __init__(self, email: str, password: str, is_admin: bool, username: str, **kw):
        super().__init__(**kw)
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.is_admin = is_admin
        self.username = username

    def __repr__(self) -> str:
        return f"<User {self.id} ({self.email})>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        return {
            'id' : self.id,
            'email': self.email,
            'username': self.username,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }          
    
    @staticmethod
    def create(user: dict) -> 'User':
        from src.persistence import repo

        users: list['User'] = User.get_all()

        for u in users:
            if u.email == user["email"]:
                raise ValueError("User already exists")
            if u.username == user["username"]:
                raise ValueError("Username already taken")
            
        new_user = User(**user)

        repo.save(new_user)

        return new_user
    
    @staticmethod
    def update(user_id: str, data: dict) -> 'User | None':
        from src.persistence import repo

        user: User | None = User.get(user_id)

        if not user:
            return None
        
        if 'email' in data:
            user.email = data['email']
        if 'password' in data:
            user.set_password(data['password'])
        if 'username' in data:
            user.username = data['username']

        repo.update(user)

        return user
