import sqlite3
from typing import List, Optional, Tuple
from entity.user import User


class UserRepository:
    """
    负责 User 实体与数据库交互的仓库类。
    """

    def __init__(self, db_name):
        self.db_name = db_name

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        return sqlite3.connect(self.db_name)

    def add_or_update_user(self, user: User) -> bool:
        """
        向数据库中添加或更新一个用户。
        如果 mid 已存在，则更新该用户的所有可变信息。
        如果 mid 不存在，则插入新用户。
        返回 True 表示操作成功，False 表示失败。
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            # 使用 INSERT OR REPLACE 语句，SQLite 特有且高效的 UPSERT 方式
            # 它会尝试插入新行，如果主键冲突，则替换掉现有行
            insert_or_replace_sql = """
            INSERT OR REPLACE INTO user (
                mid, face, fans, friend, name, sex, sign, like_num, vip, ip_location
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(insert_or_replace_sql, user.to_tuple())
            conn.commit()
            return True
        except sqlite3.Error as e:
            conn.rollback()
            print(f"添加/更新用户失败: {e}")
            return False
        finally:
            conn.close()

    def add_or_update_users_batch(self, users: List[User]) -> int:
        """
        批量添加或更新用户。
        返回实际操作（插入或更新）的用户数量。
        """
        if not users:
            return 0
        conn = self._get_connection()
        cursor = conn.cursor()
        count = 0
        try:
            insert_or_replace_sql = """
            INSERT OR REPLACE INTO user (
                mid, face, fans, friend, name, sex, sign, like_num, vip, ip_location
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            # 使用 executemany 进行批量操作，效率更高
            data_to_insert = [user.to_tuple() for user in users]
            cursor.executemany(insert_or_replace_sql, data_to_insert)
            count = cursor.rowcount  # executemany 的 rowcount 是受影响的总行数
            conn.commit()
            return count
        except sqlite3.Error as e:
            conn.rollback()
            print(f"批量添加/更新用户失败: {e}")
            return 0
        finally:
            conn.close()

    def delete_users_by_mid(self, mids: List[int]) -> int:
        """
        根据一个或多个用户ID (mid) 删除用户。
        返回删除的记录数。
        """
        if not mids:
            return 0
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            placeholders = ",".join(["?"] * len(mids))
            delete_sql = f"DELETE FROM user WHERE mid IN ({placeholders})"
            cursor.execute(delete_sql, tuple(mids))
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count
        except sqlite3.Error as e:
            conn.rollback()
            print(f"按 mid 删除用户失败: {e}")
            return 0
        finally:
            conn.close()

    def get_users_by_mid(self, mids: List[int]) -> List[User]:
        """
        根据一个或多个用户ID (mid) 查询用户。
        返回 User 对象的列表。
        """
        if not mids:
            return []
        conn = self._get_connection()
        cursor = conn.cursor()
        users = []
        try:
            placeholders = ",".join(["?"] * len(mids))
            query_sql = f"SELECT * FROM user WHERE mid IN ({placeholders})"
            cursor.execute(query_sql, tuple(mids))
            for row in cursor.fetchall():
                users.append(User.from_db_row(row))
        except sqlite3.Error as e:
            print(f"按 mid 查询用户失败: {e}")
        finally:
            conn.close()
        return users

    def get_user_by_mid(self, mid: int) -> Optional[User]:
        """
        根据单个用户ID (mid) 查询用户。
        返回单个 User 对象或 None。
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        user = None
        try:
            cursor.execute("SELECT * FROM user WHERE mid = ?", (mid,))
            row = cursor.fetchone()
            user = User.from_db_row(row)
        except sqlite3.Error as e:
            print(f"查询单个用户失败: {e}")
        finally:
            conn.close()
        return user
