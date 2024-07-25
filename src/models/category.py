from . import db

class Category(db.Model):

    __tablename__ = 'categories'

    name = db.Column(db.String(36), primary_key=True, nullable=False)
    items = db.relationship('Item', back_populates='category')

    def __init__(self, name: str, **kw) -> None:
        super().__init__(**kw)
        self.name = name

    def __repr__(self) -> str:
        return f"<Category {self.name}>"
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
        }
    
    @staticmethod
    def get_all() -> list['Category']:
        from src.persistence import repo 

        categories: list['Category'] = repo.get_all(Category)

        return categories
    
    @staticmethod
    def get(name: str) -> 'Category | None':

        from src.persistence import repo 

        category: 'Category' = repo.get_for_category(name)

        return category
    
    @staticmethod
    def create(name: str) -> 'Category':

        from src.persistence import repo 

        category = Category(name)
        repo.save(category)
        return category
