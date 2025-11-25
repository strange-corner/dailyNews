import abc
import os


class SeqElem:

    @abc.abstractmethod
    def ident(self):
        return


class Article(SeqElem):

    def __init__(self, filename):
        self.filename = filename

    def ident(self) -> str:
        return self.filename


class CategoryMarker(SeqElem):

    def __init__(self, name):
        self.name = name

    def ident(self) -> str:
        return self.name


class PageFlow:
    def __init__(self):
        self.seq = []

    def elements(self) -> list[SeqElem]:
        return self.seq

    def add(self, elem: SeqElem):
        self.seq.append(elem)

    def refreshArticles(self, folder: str):
        self.removeArticles()
        if os.path.isdir(folder):
            for fname in os.listdir(folder):
                if fname.endswith(".tex") and fname.startswith("a_"):
                    self.seq.append(Article(fname))

    def removeArticles(self):
        self.seq = [ele for ele in self.seq if type(ele) != Article]

    def move_up(self, eleset: list[int]):
        for idx in eleset:
            if idx > 0:
                self.seq.insert(idx - 1, self.seq.pop(idx))

    def move_dn(self, eleset: list[int]):
        eleset = list(eleset)
        eleset.reverse()
        for idx in eleset:
            if idx < len(self.seq):
                self.seq.insert(idx + 1, self.seq.pop(idx))

