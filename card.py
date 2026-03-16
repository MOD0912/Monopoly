
class Card:
    def __init__(self, name, price=None, color=None, rent=None, owner=None, entity=None):
        self.name = name
        self.price = price
        self.color = color
        self.rent = rent
        self.owner = owner
        self.entity = entity
        self.mortgaged = False

    def __repr__(self):
        return f"Card(name='{self.name}', price={self.price}, color='{self.color}', rent={self.rent}, owner={self.owner})"


if __name__ == "__main__":
    import main