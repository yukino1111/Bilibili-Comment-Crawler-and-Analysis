import requests
import json
import time
from typing import List, Optional, Dict, Any
from entity.comment import Comment
from repository.comment_repository import CommentRepository
from utils.config import *

class BilibiliUserCommentsCrawler:

    def __init__(self, db_name: str = BILI_DB_PATH):

        self.base_url = "https://api.aicu.cc/api/v3/search/getreply"
        self.comment_repo = CommentRepository(db_name)
        self.crawled_comment_count = 0
        self.page_size = 100  # 每页评论数量

    def _get_comments_page_from_api(
        self, uid: str, pn: int
    ) -> Optional[Dict[str, Any]]:
        params = {
            "uid": uid,
            "pn": pn,
            "ps": self.page_size,
            "mode": 0,  # 0表示按时间排序，1表示按点赞排序
            "keyword": "",  # 留空表示所有评论
        }
        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()  # 检查HTTP响应状态码
            data = response.json()

            if data.get("code") != 0:  # 检查API返回的业务状态码
                print(
                    f"API返回错误 for uid {uid}, page {pn}: {data.get('message', '未知错误')}"
                )
                return None

            return data.get("data")

        except requests.exceptions.RequestException as e:
            print(f"请求用户评论API失败 for uid {uid}, page {pn}: {e}")
            return None
        except json.JSONDecodeError as e:
            print(
                f"解析用户评论JSON失败 for uid {uid}, page {pn}: {e}, 响应内容: {response.text[:200]}..."
            )
            return None

    def _parse_and_save_comment(self, raw_comment_data: Dict[str, Any], user_id: int):
        try:
            rpid = int(raw_comment_data.get("rpid"))
            message = raw_comment_data.get("message", "")
            comment_time = int(raw_comment_data.get("time"))

            # parent 字段可能是一个空对象 {} 或包含 rootid/parentid
            parent_data = raw_comment_data.get("parent", {})
            parentid = int(parent_data.get("rootid", 0)) if parent_data else 0
            # 如果是二级评论，parentid是其根评论的rpid。如果是一级评论，rootid通常是0或其自身rpid。
            # 这里我们统一将parentid设置为其根评论的rpid，如果不存在则为0。

            # dyn 字段包含 oid 和 type
            dyn_data = raw_comment_data.get("dyn", {})
            oid = int(dyn_data.get("oid", 0))  # 视频或内容的ID

            # 暂时填充默认值或空值
            comment_obj = Comment(
                rpid=rpid,
                parentid=parentid,
                mid=user_id,  # 确保mid是int类型
                information=message,
                time=comment_time,
                oid=oid,
            )
            print(
                f"评论: rpid={rpid}, parentid={parentid}, oid={oid}, 信息: {message}, 时间: {comment_time}, 用户ID: {user_id}"
            )
            self.comment_repo.add_mini_comment(comment_obj, overwrite=True)  # 允许覆盖

            self.crawled_comment_count += 1
            # print(f"  - 存储评论: rpid={rpid}, oid={oid}")
        except Exception as e:
            print(f"处理或存储评论数据失败 (rpid: {raw_comment_data.get('rpid')}): {e}")

    def crawl_user_all_comments(self, uid: int, delay_seconds: float = 0.5) -> int:
        if not uid:
            print("请提供用户ID。")
            return 0

        print(f"开始爬取用户 {uid} 的所有评论...")
        self.crawled_comment_count = 0
        current_page = 1
        is_end = False

        while not is_end:
            print(f"  - 正在爬取用户 {uid} 的第 {current_page} 页评论...")
            data = self._get_comments_page_from_api(uid, current_page)

            if not data:
                print(f"获取用户 {uid} 第 {current_page} 页评论失败，停止爬取。")
                break

            replies = data.get("replies", [])
            if not replies:
                print(f"用户 {uid} 第 {current_page} 页无评论数据。")
                is_end = True  # 即使 is_end 为 false，如果 replies 为空也视为结束
                break

            for reply in replies:
                self._parse_and_save_comment(reply, uid)
                print(f"  - 爬取评论: rpid={reply.get('rpid')}, oid={reply.get('dyn').get('oid')}")

            cursor_info = data.get("cursor", {})
            is_end = cursor_info.get("is_end", True)  # 默认如果is_end缺失则视为结束

            if not is_end:
                time.sleep(delay_seconds)  # 延迟，避免请求过快
                current_page += 1
            else:
                print(f"用户 {uid} 的评论已全部爬取。")

        print(
            f"用户 {uid} 的评论爬取完成。总计爬取 {self.crawled_comment_count} 条评论。"
        )
        return self.crawled_comment_count


# --- 数据库初始化和测试部分 ---
if __name__ == "__main__":
    # 确保数据库文件和表已初始化
    def init_db_for_crawler(db_name="bilibili_comments.db"):
        import sqlite3

        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS comment (
            rpid INTEGER PRIMARY KEY, parentid INTEGER, mid INTEGER, name TEXT,
            level INTEGER, sex TEXT, information TEXT, time INTEGER,
            single_reply_num INTEGER, single_like_num INTEGER, sign TEXT,
            ip_location TEXT, vip INTEGER, face TEXT, oid INTEGER
        );
        """
        )
        conn.commit()
        conn.close()
        print(f"数据库 '{db_name}' 表结构已确保存在。")

    # 运行数据库初始化
    init_db_for_crawler()

    # 示例用法
    crawler = BilibiliUserCommentsCrawler(db_name="bilibili_comments.db")

    # 替换为你想爬取的真实B站用户uid
    user_uid_to_crawl = "1234"  # 示例mid，可以替换为真实的B站用户mid
    # 另一个可能评论较多的用户ID，例如：
    # user_uid_to_crawl = "208259" # 罗翔说刑法

    total_comments_crawled = crawler.crawl_user_all_comments(
        user_uid_to_crawl, delay_seconds=0.5
    )
    print(
        f"最终为用户 {user_uid_to_crawl} 爬取并存储到数据库的评论总数: {total_comments_crawled}"
    )

    # 验证数据是否入库 (可选)
    print("\n--- 验证数据库数据 (查询少量评论) ---")
    comment_repo = CommentRepository(db_name="bilibili_comments.db")
    # 注意：这里查询的是该用户的所有评论，而不是某个视频的评论
    # 由于 CommentRepository 的 get_comments_by_mid_paginated 接受 List[int]
    retrieved_comments = comment_repo.get_comments_by_mid_paginated(
        mids=[int(user_uid_to_crawl)], page=1, page_size=5
    )
    print(f"从数据库查询到的用户 {user_uid_to_crawl} 的前5条评论:")
    for comment in retrieved_comments:
        print(
            f"  - Rpid: {comment.rpid}, Oid: {comment.oid}, Content: {comment.information[:30]}..."
        )
