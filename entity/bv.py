class Bv:
    def __init__(
        self,
        oid: int,
        bv: str = None,
        title: str = None,
    ):
        self.oid = oid
        self.bv = bv
        self.title = title

    def to_tuple(self):
        return (self.oid, self.bv, self.title)

    @classmethod
    def from_db_row(cls, row: tuple):
        if row is None:
            return None
        return cls(oid=row[0], bv=row[1], title=row[2])
