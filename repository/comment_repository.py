import sqlite3
from typing import List, Optional, Tuple, Iterator  # 导入类型提示
from entity.comment import Comment
class CommentRepository:
    def __init__(self, db_name):
        self.db_name = db_name

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_name)

    def add_comment(self, comment: Comment, overwrite: bool = False) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            # 检查 rpid 是否已存在
            cursor.execute("SELECT 1 FROM comment WHERE rpid = ?", (comment.rpid,))
            exists = cursor.fetchone()

            if exists:
                if overwrite:
                    # 如果存在且允许覆盖，则执行 UPDATE
                    update_sql = """
                    UPDATE comment SET
                        parentid = ?, mid = ?, name = ?, level = ?, sex = ?,
                        information = ?, time = ?, single_reply_num = ?,
                        single_like_num = ?, sign = ?, ip_location = ?,
                        vip = ?, face = ?, oid = ?
                    WHERE rpid = ?
                    """
                    # 更新操作，rpid 在 WHERE 子句，所以元组参数顺序要调整
                    params = (
                        comment.parentid,
                        comment.mid,
                        comment.name,
                        comment.level,
                        comment.sex,
                        comment.information,
                        comment.time,
                        comment.single_reply_num,
                        comment.single_like_num,
                        comment.sign,
                        comment.ip_location,
                        comment.vip,
                        comment.face,
                        comment.oid,
                        comment.rpid,
                    )
                    cursor.execute(update_sql, params)
                    conn.commit()
                    return True
                else:
                    # 如果存在且不允许覆盖，则不操作
                    return False
            else:
                # 如果不存在，则执行 INSERT
                insert_sql = """
                INSERT INTO comment (
                    rpid, parentid, mid, name, level, sex, information,
                    time, single_reply_num, single_like_num, sign,
                    ip_location, vip, face, oid
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(insert_sql, comment.to_tuple())
                conn.commit()
                return True
        except sqlite3.Error as e:
            conn.rollback()
            print(f"添加/更新评论失败: {e}")
            return False
        finally:
            conn.close()

    def add_comments_batch(
        self, comments: List[Comment], overwrite: bool = False
    ) -> int:
        """
        批量添加评论。提高了插入效率。
        根据 rpid 判断是否是新增或覆盖。
        返回实际操作（插入或更新）的评论数量。
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        count = 0
        try:
            for comment in comments:
                cursor.execute("SELECT 1 FROM comment WHERE rpid = ?", (comment.rpid,))
                exists = cursor.fetchone()

                if exists:
                    if overwrite:
                        update_sql = """
                        UPDATE comment SET
                            parentid = ?, mid = ?, name = ?, level = ?, sex = ?,
                            information = ?, time = ?, single_reply_num = ?,
                            single_like_num = ?, sign = ?, ip_location = ?,
                            vip = ?, face = ?, oid = ?
                        WHERE rpid = ?
                        """
                        params = (
                            comment.parentid,
                            comment.mid,
                            comment.name,
                            comment.level,
                            comment.sex,
                            comment.information,
                            comment.time,
                            comment.single_reply_num,
                            comment.single_like_num,
                            comment.sign,
                            comment.ip_location,
                            comment.vip,
                            comment.face,
                            comment.oid,
                            comment.rpid,
                        )
                        cursor.execute(update_sql, params)
                        count += 1
                else:
                    insert_sql = """
                    INSERT INTO comment (
                        rpid, parentid, mid, name, level, sex, information,
                        time, single_reply_num, single_like_num, sign,
                        ip_location, vip, face, oid
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    cursor.execute(insert_sql, comment.to_tuple())
                    count += 1
            conn.commit()
            return count
        except sqlite3.Error as e:
            conn.rollback()
            print(f"批量添加/更新评论失败: {e}")
            return 0
        finally:
            conn.close()

    def delete_comments_by_mid(self, mids: List[int]) -> int:
        """
        根据一个或多个用户ID (mid) 删除评论。
        返回删除的记录数。
        """
        if not mids:
            return 0
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            # 使用 IN 子句处理多个 mid
            placeholders = ",".join(["?"] * len(mids))
            delete_sql = f"DELETE FROM comment WHERE mid IN ({placeholders})"
            cursor.execute(delete_sql, tuple(mids))
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count
        except sqlite3.Error as e:
            conn.rollback()
            print(f"按 mid 删除评论失败: {e}")
            return 0
        finally:
            conn.close()

    def delete_comments_by_oid(self, oids: List[int]) -> int:
        """
        根据一个或多个视频ID (oid) 删除评论。
        返回删除的记录数。
        """
        if not oids:
            return 0
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            # 使用 IN 子句处理多个 oid
            placeholders = ",".join(["?"] * len(oids))
            delete_sql = f"DELETE FROM comment WHERE oid IN ({placeholders})"
            cursor.execute(delete_sql, tuple(oids))
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count
        except sqlite3.Error as e:
            conn.rollback()
            print(f"按 oid 删除评论失败: {e}")
            return 0
        finally:
            conn.close()

    def get_comments_by_mid_paginated(
        self, mids: List[int], page: int = 1, page_size: int = 20
    ) -> List[Comment]:
        """
        根据一个或多个用户ID (mid) 查询评论，并支持分页。
        返回 Comment 对象的列表。
        """
        if not mids:
            return []
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 20  # 默认值，防止传入无效值

        offset = (page - 1) * page_size
        conn = self._get_connection()
        cursor = conn.cursor()
        comments = []
        try:
            placeholders = ",".join(["?"] * len(mids))
            query_sql = f"""
            SELECT * FROM comment
            WHERE mid IN ({placeholders})
            ORDER BY time DESC -- 通常按时间倒序排列
            LIMIT ? OFFSET ?
            """
            cursor.execute(query_sql, tuple(mids + [page_size, offset]))
            for row in cursor.fetchall():
                comments.append(Comment.from_db_row(row))
        except sqlite3.Error as e:
            print(f"按 mid 分页查询评论失败: {e}")
        finally:
            conn.close()
        return comments

    def get_comments_by_oid_paginated(
        self, oids: List[int], page: int = 1, page_size: int = 20
    ) -> List[Comment]:
        """
        根据一个或多个视频ID (oid) 查询评论，并支持分页。
        返回 Comment 对象的列表。
        """
        if not oids:
            return []
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 20

        offset = (page - 1) * page_size
        conn = self._get_connection()
        cursor = conn.cursor()
        comments = []
        try:
            placeholders = ",".join(["?"] * len(oids))
            query_sql = f"""
            SELECT * FROM comment
            WHERE oid IN ({placeholders})
            ORDER BY time DESC
            LIMIT ? OFFSET ?
            """
            cursor.execute(query_sql, tuple(oids + [page_size, offset]))
            for row in cursor.fetchall():
                comments.append(Comment.from_db_row(row))
        except sqlite3.Error as e:
            print(f"按 oid 分页查询评论失败: {e}")
        finally:
            conn.close()
        return comments

    def get_comments_by_mid_stream(self, mids: List[int]) -> Iterator[Comment]:
        """
        根据一个或多个用户ID (mid) 流式查询评论。
        返回一个 Comment 对象的迭代器。
        """
        if not mids:
            return  # 使用 return 结束生成器

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            placeholders = ",".join(["?"] * len(mids))
            query_sql = f"""
            SELECT * FROM comment
            WHERE mid IN ({placeholders})
            ORDER BY time ASC -- 流式通常按时间升序处理
            """
            cursor.execute(query_sql, tuple(mids))
            while True:
                rows = cursor.fetchmany(1000)  # 每次取1000条，避免一次性加载过多内存
                if not rows:
                    break
                for row in rows:
                    yield Comment.from_db_row(row)
        except sqlite3.Error as e:
            print(f"按 mid 流式查询评论失败: {e}")
        finally:
            if conn:
                conn.close()

    def get_comments_by_oid_stream(self, oids: List[int]) -> Iterator[Comment]:
        """
        根据一个或多个视频ID (oid) 流式查询评论。
        返回一个 Comment 对象的迭代器。
        """
        if not oids:
            return  # 使用 return 结束生成器

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            placeholders = ",".join(["?"] * len(oids))
            query_sql = f"""
            SELECT * FROM comment
            WHERE oid IN ({placeholders})
            ORDER BY time ASC -- 流式通常按时间升序处理
            """
            cursor.execute(query_sql, tuple(oids))
            while True:
                rows = cursor.fetchmany(1000)  # 每次取1000条
                if not rows:
                    break
                for row in rows:
                    yield Comment.from_db_row(row)
        except sqlite3.Error as e:
            print(f"按 oid 流式查询评论失败: {e}")
        finally:
            if conn:
                conn.close()

