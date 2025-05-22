class Comment:
    def __init__(
        self,
        rpid: int,
        parentid: int = None,
        mid: int = None,
        name: str = None,
        level: int = None,
        sex: str = None,
        information: str = None,
        time: int = None,
        single_reply_num: int = None,
        single_like_num: int = None,
        sign: str = None,
        ip_location: str = None,
        vip: int = None,
        face: str = None,
        oid: int = None,
    ):
        self.rpid = rpid
        self.parentid = parentid
        self.mid = mid
        self.name = name
        self.level = level
        self.sex = sex
        self.information = information
        self.time = time
        self.single_reply_num = single_reply_num
        self.single_like_num = single_like_num
        self.sign = sign
        self.ip_location = ip_location
        self.vip = vip
        self.face = face
        self.oid = oid

    def to_tuple(self):
        return (
            self.rpid,
            self.parentid,
            self.mid,
            self.name,
            self.level,
            self.sex,
            self.information,
            self.time,
            self.single_reply_num,
            self.single_like_num,
            self.sign,
            self.ip_location,
            self.vip,
            self.face,
            self.oid,
        )

    @classmethod
    def from_db_row(cls, row: tuple):
        if row is None:
            return None
        return cls(
            rpid=row[0],
            parentid=row[1],
            mid=row[2],
            name=row[3],
            level=row[4],
            sex=row[5],
            information=row[6],
            time=row[7],
            single_reply_num=row[8],
            single_like_num=row[9],
            sign=row[10],
            ip_location=row[11],
            vip=row[12],
            face=row[13],
            oid=row[14],
        )