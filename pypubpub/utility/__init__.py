


class Titlemachine():
    """A class that generates a title with a count for a given base parent paper"""
    def __init__(self, parent_title):
        self.base = parent_title
        self.count = 0
        self.ctr = (i for i in range(1, 10^10))
    def title(self, parent_title=None):
        """A method that generates a title with a count for a given base parent paper"""
        base = parent_title or self.base
        self.count+=1
        return f'Evaluation {self.count} of "{base}"'
    @classmethod
    def title_method(cls,parent_title=None):
        """A classmethod that returns a method that generates a title with a count for a given base parent paper"""
        return cls(parent_title).title


def titler(parent_title=None, tpl= lambda p,i:f'Evaluation {i} of "{p}"'):
    """A method that returns a method that generates a title with a count for a given base parent paper"""
    c = (i for i in range(1,200))
    def h(parent_title=parent_title, tpl=tpl):
        if parent_title is None:
            raise Exception("No base title provided")
        return tpl(parent_title, next(c))
    return h

