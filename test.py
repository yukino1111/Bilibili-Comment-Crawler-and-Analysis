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