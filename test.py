import collections
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
from wordcloud import WordCloud
import jieba
import os
import re
from snownlp import SnowNLP
import matplotlib.dates as mdates
from typing import List, Optional
from repository.comment_repository import CommentRepository
from analyzer.analyze_comment import CommentAnalyzer
from repository.user_repository import UserRepository
from crawler.get_single_video_comment import BilibiliCommentCrawler

import utils.get_csv

try:
    from entity.comment import Comment
    from entity.user import User
    from repository.comment_repository import CommentRepository
    from repository.user_repository import UserRepository
except ImportError:
    # 如果项目结构不同，或者是在测试环境下，提供一个调试提示
    print(
        "Warning: Could not import core modules. Please check your project structure or Python path."
    )
    print("Assuming entity/ and repository/ are in the same parent directory.")

# --- 使用示例 ---
if __name__ == "__main__":
    # 确保 'assets/fonts/PingFang-Medium.ttf' 和 'assets/hit_stopwords.txt' 存在
    # 假设你有一个名为 'BV1_example.csv' 的评论数据文件
    # 替换为你的实际CSV文件路径
    _db_file = "./assets/bili_data.db"
    utils.get_csv.export_comments_by_oid_to_csv(
        output_filepath="./output_csv/comments_by_oid_10001.csv",
        oids=[114544999399889],
        db_name=_db_file,
    )
    example_csv_path = "./output_csv/comments_by_oid_10001.csv"

    analyzer = CommentAnalyzer(example_csv_path)
    analyzer.run_all_analysis()


# if __name__ == "__main__":

#     def init_db_for_crawler(db_name="./assets/bili_data.db"):
#         conn = sqlite3.connect(db_name)
#         cursor = conn.cursor()
#         cursor.execute(
#             """
#         CREATE TABLE IF NOT EXISTS user (
#             mid INTEGER PRIMARY KEY, face TEXT, fans INTEGER, friend INTEGER,
#             name TEXT, sex TEXT, sign TEXT, like_num INTEGER, vip INTEGER
#         );
#         """
#         )
#         cursor.execute(
#             """
#         CREATE TABLE IF NOT EXISTS comment (
#             rpid INTEGER PRIMARY KEY, parentid INTEGER, mid INTEGER, name TEXT,
#             level INTEGER, sex TEXT, information TEXT, time INTEGER,
#             single_reply_num INTEGER, single_like_num INTEGER, sign TEXT,
#             ip_location TEXT, vip INTEGER, face TEXT, oid INTEGER
#         );
#         """
#         )
#         conn.commit()
#         conn.close()
#         print(f"数据库 '{db_name}' 表结构已确保存在。")

#     import sqlite3  # 导入 sqlite3 以用于测试时的数据库初始化

#     init_db_for_crawler()

#     print("--- 开始爬取评论示例 ---")
#     crawler = BilibiliCommentCrawler(
#         bv="BV1v2JBzPEMv", is_second=True
#     )  # 替换为你想爬取的BV号
#     # 或者 crawler = BilibiliCommentCrawler(bv="BV1tiEJzNEiy", is_second=True)

#     crawled_count = crawler.crawl()
#     print(f"最终爬取并存储到数据库的评论总数: {crawled_count}")

#     # 验证数据是否入库 (可选)
#     print("\n--- 验证数据库数据 (查询少量数据) ---")
#     repo = CommentRepository()
#     # 假设你爬取了BV1v2JBzPEMv，其oid可以通过get_information获取或直接查询
#     # 为了测试方便，这里假设oid已经获取，或者你可以根据实际爬取到的oid来查询
#     try:
#         # 重新获取 BV1v2JBzPEMv 的 oid，确保查询准确
#         temp_crawler = BilibiliCommentCrawler(bv="BV1v2JBzPEMv")
#         video_oid, _ = temp_crawler.get_information()  # 这可能会再次发起网络请求

#         comments_from_db = repo.get_comments_by_oid_paginated(
#             oids=[int(video_oid)], page=1, page_size=5
#         )
#         print(f"从数据库查询到的前5条评论 (oid={video_oid}):")
#         for comment in comments_from_db:
#             print(
#                 f"  - Rpid: {comment.rpid}, User: {comment.name}, Content: {comment.information[:30]}..."
#             )

#         user_repo = UserRepository()
#         users_from_db = user_repo.get_users_by_mid(
#             mids=[comment.mid for comment in comments_from_db]
#         )
#         print(f"从数据库查询到的相关用户:")
#         for user in users_from_db:
#             print(f"  - Mid: {user.mid}, Name: {user.name}, Fans: {user.fans}")

#     except Exception as e:
#         print(f"验证数据库数据失败: {e}")
