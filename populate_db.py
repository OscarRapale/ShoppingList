import json
from src.models import db
from src.models.category import Category
from src.models.item import Item
from src import create_app

app = create_app()

def populate_db(data_file):
    with app.app_context():
        with open(data_file, 'r') as file:
            data = json.load(file)

        for category_data in data['categories']:
            category_name = category_data['name']
            category = Category(name=category_name)
            db.session.add(category)
            
            for item_name in category_data['items']:
                item = Item(name=item_name, category_name=category_name)
                db.session.add(item)

        db.session.commit()
        print("Database populated successfully.")

if __name__ == '__main__':
    data_file = 'data/category_item.json'
    populate_db(data_file)
