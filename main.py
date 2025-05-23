from analyzer.analyze_comment import CommentAnalyzer
from crawler.get_single_video_comment import BilibiliCommentCrawler
from crawler.get_user_all_comment import BilibiliUserCommentsCrawler
from crawler.get_user_information import BilibiliUserCrawler
from database.db_manage import init_bilibili_db
from entity.user import User
from repository.user_repository import UserRepository
from utils.config import *
import os
from repository.comment_repository import CommentRepository
from entity.comment import Comment
from utils.get_csv import export_comments_by_mid_to_csv, export_comments_by_oid_to_csv
from repository.bv_repository import BvRepository
from utils import get_user_all_bv
if __name__ == "__main__":
    # DELETE = 1
    # if DELETE and os.path.exists(BILI_DB_PATH):
    #     # 删除BILI_DB_PATH的文件
    #     try:
    #         os.remove(BILI_DB_PATH)
    #         print(f"已删除文件: {BILI_DB_PATH}")
    #     except Exception as e:
    #         print(f"删除文件时出错: {e}")

    init_bilibili_db(BILI_DB_PATH)
    comment_repo = CommentRepository(BILI_DB_PATH)
    user_repo = UserRepository(BILI_DB_PATH)
    bv_repo = BvRepository(BILI_DB_PATH)

    bvs = []
    video_oids = []

    print("请选择获取评论模式：")
    print("0: 获取视频评论（多个BV号用逗号间隔）")
    print("1: 获取单个up主视频评论")
    print("2: 获取uid所有评论")
    get_mode = int(input("请输入模式（0/1/2）："))
    if get_mode == 0:
        print("请输入视频BV号：")
        bv_input = input()
        print("是否开启二级评论爬取：")
        print("0: 否")
        print("1: 是")
        is_second = int(input())
        if is_second == 0:
            is_second = False
        else:
            is_second = True
        bvs = [bv.strip() for bv in bv_input.split(",") if bv.strip()]
        for bv in bvs:
            crawler = BilibiliCommentCrawler(bv=bv, is_second=True)
            crawled_count = crawler.crawl()
        try:
            video_oids = bv_repo.get_oids_by_bids(bvs)
        except Exception as e:
            print(f"验证数据库数据失败: {e}")
        export_comments_by_oid_to_csv(
            output_filepath=OUTPUT_CSV_PATH,
            oids=video_oids,
            db_name=BILI_DB_PATH,
        )

    elif get_mode == 1:
        print("请输入up主ID：")
        up_id = input()
        print("是否开启二级评论爬取（默认开启）：")
        print("0: 否")
        print("1: 是")
        is_second = int(input())
        if is_second == 0:
            is_second = False
        else:
            is_second = True

        # 获取UP主所有视频aid列表
        crawler = get_user_all_bv.GetInfo(up_id, headless=True)
        video_ids = crawler.next_page()
        print(f"共获取到 {len(video_ids)} 个视频，开始批量爬取评论...")
        for bv in video_ids:
            crawler = BilibiliCommentCrawler(bv=bv, is_second=True)
            crawled_count = crawler.crawl()
        try:
            video_oids = bv_repo.get_oids_by_bids(video_ids)
        except Exception as e:
            print(f"验证数据库数据失败: {e}")
        print(video_oids)
        export_comments_by_oid_to_csv(
            output_filepath=OUTPUT_CSV_PATH,
            oids=video_oids,
            db_name=BILI_DB_PATH,
        )
    elif get_mode == 2:
        print("请输入用户ID：")
        uid = input()
        mids=[]
        mids.append(uid)  # 示例mid，可以替换为真实的B站用户mid
        crawler=BilibiliUserCrawler(db_name=BILI_DB_PATH)
        for single_mid in mids:
            crawled_user = crawler.crawl_user_info(single_mid)
        crawler = BilibiliUserCommentsCrawler(db_name=BILI_DB_PATH)
        for single_mid in mids:
            total_comments_crawled = crawler.crawl_user_all_comments(
                single_mid, delay_seconds=0.5
            )
        export_comments_by_mid_to_csv(
            output_filepath=OUTPUT_CSV_PATH,
            mids=mids,
            db_name=BILI_DB_PATH,
        )
    else:
        print("输入错误")
        exit(1)

    print("请选择是否分析：")

    print("0: 否")
    print("1: 是")
    analyze_mode = int(input())

    if analyze_mode == 1:
        analyzer = CommentAnalyzer(csv_path=OUTPUT_CSV_PATH)
        if get_mode == 0 or get_mode == 1:
            analyzer.run_all_analysis()
        elif get_mode == 2:
            analyzer.run_mini_analysis()

    elif analyze_mode == 0:
        print("程序退出")
        exit(0)
    else:
        print("输入错误")
        exit(1)
