
class Card:
    def __init__(self, name, price=None, color=None, owner=None, entity=None):
        self.name = name
        self.price = price
        self.color = color
        self.owner = owner
        self.entity = entity

    def __repr__(self):
        return f"Card(name='{self.name}', price={self.price}, color='{self.color}', owner={self.owner})"
