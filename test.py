from src.models.category import Category
from src.models.item import Item
from src.models import db
from src import create_app

app = create_app()
test_item = Item(name="test item", category_name="test category")

with app.app_context():
    db.session.add(test_item)
    db.session.commit()
