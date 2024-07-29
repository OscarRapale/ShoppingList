from src.models.category import Category
from src.models.item import Item
from src.models.user import User
from src.models import db
from src import create_app

app = create_app()
test_user = User(email="user@example.com", password="password", username="Testuser", is_admin=False)

with app.app_context():
    db.session.add(test_user)
    db.session.commit()
