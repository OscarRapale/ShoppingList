from . import db
from src.models.user import User
from src.models.item import Item


class ShoppingList(db.Model):

    __tablename__  = 'shopping_lists'

    name = db.Column(db.String(36), nullable=False)
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'), unique=True, nullable=False)
    owner = db.relationship("User", back_populates='shopping_lists', lazy=True)
    items =  db.relationship("ShoppingListItem", back_populates='shopping_list', lazy='dynamic')

    def __init__(self, name: str, owner_id: str, **kw) -> None:
        super().__init__(**kw)

        self.name = name
        self.owner_id = owner_id

    def __repr__(self) -> str:
        return f"<ShoppingList {self.id} ({self.name})>"   
    
    def to_dict(self) -> dict:

        return {
            "id": self.id,
            "name": self.name,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @staticmethod
    def create(data: dict) -> "ShoppingList":

        from src.persistence import repo

        user: User | None = User.get(data['owner_id'])

        if not user:
            raise ValueError(f"User with ID {data['owner_id']} not found")
        
        new_shopping_list = ShoppingList(name=data['name'], owner_id=data['owner_id'])

        db.session.add(new_shopping_list)
        db.session.commit()

        return new_shopping_list
    
    @staticmethod
    def update(shopping_list_id: str, data: dict) -> "ShoppingList | None":

        from src.persistence import repo

        shopping_list: ShoppingList | None = ShoppingList.get(shopping_list_id)

        if not shopping_list:
            return None
        
        for key, value in data.items():
            setattr(shopping_list, key, value)

        repo.update(shopping_list)

        return shopping_list
