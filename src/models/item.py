from . import db
from src.models.category import Category


class Item(db.Model):

    __tablename__ = 'items'

    name = db.Column(db.String(36), nullable=False)
    category_name = db.Column(db.String(36), db.ForeignKey('categories.name'), nullable=False)
    category = db.relationship('Category', back_populates='items')
    shopping_lists = db.relationship('ShoppingListItem', back_populates='item')

    def __init__(self, name: str, category_name: str, **kw) -> None:
        super().__init__(**kw)

        self.name = name
        self.category_name = category_name

    def __repr__(self) -> str:
        return f"<Item {self.id} ({self.name})>"
    
    def to_dict(self) -> dict:

        return {
           "id": self.id,
            "name": self.name,
            "category_name": self.category_name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(), 
        }

    @staticmethod
    def create(data: dict) -> "Item":

        from src.persistence import repo

        category = Category.get(data["category_name"])

        if not category:
            raise ValueError("Category not found")

        item = Item(**data)

        repo.save(item)

        return item

    @staticmethod
    def update(item_id: str, data: dict) -> "Item":

        from src.persistence import repo

        item = Item.get(item_id)

        if not item:
            raise ValueError("Item not found")

        for key, value in data.items():
            setattr(item, key, value)

        repo.update(item)

        return item
    
class ShoppingListItem(db.Model):

    __tablename__ = 'shopping_list_items'

    shopping_list_id = db.Column(db.String(36), db.ForeignKey('shopping_lists.id'), primary_key=True)
    item_id = db.Column(db.String(36), db.ForeignKey('items.id'), primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, onupdate=db.func.current_timestamp()) 
    shopping_list = db.relationship("ShoppingList", back_populates='items')
    item = db.relationship("Item", back_populates='shopping_lists')

    def __init__(self, shopping_list_id: str, item_id: str, **kw) -> None:
        super().__init__(**kw)

        self.shopping_list_id = shopping_list_id
        self.item_id = item_id

    def to_dict(self) -> dict:

        return {
            "id": self.id,
            "shopping_list_id": self.shopping_list_id,
            "item_id": self.item_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        
    @staticmethod
    def get(shopping_list_id: str, item_id: str) -> "ShoppingListItem | None":

        from src.persistence import repo

        shopping_list_items: list[ShoppingListItem] = repo.get_all("shopping_list_item")

        for shopping_list_item in shopping_list_items:
            if (
                shopping_list_item.shopping_list_id == shopping_list_id
                and shopping_list_item.item_id == item_id 
            ):
                return shopping_list_item
            
        return None
    
    @staticmethod
    def create(data: dict) -> "ShoppingListItem":

        from src.persistence import repo

        new_shopping_list_item = ShoppingListItem(**data)

        repo.save(new_shopping_list_item)

        return new_shopping_list_item
    
    @staticmethod
    def delete(shopping_list_id: str, item_id: str) -> bool:

        from src.persistence import repo

        shopping_list_item = ShoppingListItem.get(shopping_list_id, item_id)

        if not shopping_list_item:
            return False
        
        repo.delete(shopping_list_item)

        return True
    
    @staticmethod
    def update(entity_id: str, data: dict):
        """Not implemented, for now"""
        raise NotImplementedError(
            "This method is defined only because of the Base class"
        )
