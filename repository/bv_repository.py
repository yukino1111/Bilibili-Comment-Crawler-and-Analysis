import sqlite3
from typing import List, Optional, Tuple
from entity.bv import Bv


class BvRepository:
    def __init__(self, db_name):
        self.db_name = db_name

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_name)

    def add_or_update_bv(self, bv: Bv) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            insert_or_replace_sql = """
            INSERT OR REPLACE INTO bv (
                oid, bv, title
            ) VALUES (?, ?, ?)
            """
            cursor.execute(insert_or_replace_sql, bv.to_tuple())
            conn.commit()
            return True
        except sqlite3.Error as e:
            conn.rollback()
            print(f"添加/更新失败: {e}")
            return False
        finally:
            conn.close()

    def add_or_update_bvs_batch(self, bvs: List[Bv]) -> int:
        if not bvs:
            return 0
        conn = self._get_connection()
        cursor = conn.cursor()
        count = 0
        try:
            insert_or_replace_sql = """
            INSERT OR REPLACE INTO bv (
                oid, bv, title
            ) VALUES (?, ?, ?)
            """
            data_to_insert = [bv.to_tuple() for bv in bvs]
            cursor.executemany(insert_or_replace_sql, data_to_insert)
            count = cursor.rowcount
            conn.commit()
            return count
        except sqlite3.Error as e:
            conn.rollback()
            print(f"批量添加/更新失败: {e}")
            return 0
        finally:
            conn.close()

    def delete_bvs_by_oid(self, oids: List[int]) -> int:
        if not oids:
            return 0
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            placeholders = ",".join(["?"] * len(oids))
            delete_sql = f"DELETE FROM bv WHERE oid IN ({placeholders})"
            cursor.execute(delete_sql, tuple(oids))
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count
        except sqlite3.Error as e:
            conn.rollback()
            print(f"删除 bv 失败: {e}")
            return 0
        finally:
            conn.close()

    def get_bvs_by_oid(self, oids: List[int]) -> List[Bv]:
        if not oids:
            return []
        conn = self._get_connection()
        cursor = conn.cursor()
        bvs = []
        try:
            placeholders = ",".join(["?"] * len(oids))
            query_sql = f"SELECT * FROM bv WHERE oid IN ({placeholders})"
            cursor.execute(query_sql, tuple(oids))
            for row in cursor.fetchall():
                bvs.append(Bv.from_db_row(row))
        except sqlite3.Error as e:
            print(f"查询失败: {e}")
        finally:
            conn.close()
        return bvs

    def get_bv_by_oid(self, oid: int) -> Optional[Bv]:
        conn = self._get_connection()
        cursor = conn.cursor()
        bv = None
        try:
            cursor.execute("SELECT * FROM bv WHERE oid = ?", (oid,))
            row = cursor.fetchone()
            bv = Bv.from_db_row(row)
        except sqlite3.Error as e:
            print(f"查询失败: {e}")
        finally:
            conn.close()
        return bv
