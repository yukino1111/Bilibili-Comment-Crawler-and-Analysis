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
        # crawler=BilibiliUserCrawler(db_name=BILI_DB_PATH)
        # for single_mid in mids:
        #     crawled_user = crawler.crawl_user_info(single_mid)
        # crawler = BilibiliUserCommentsCrawler(db_name=BILI_DB_PATH)
        # for single_mid in mids:
        #     total_comments_crawled = crawler.crawl_user_all_comments(
        #         single_mid, delay_seconds=0.5
        #     )
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

    # # 评论

    # # 批量添加
    # print("\n--- 测试批量添加评论 ---")
    # print(
    #     f"批量添加（不覆盖）评论数量: {comment_repo.add_comments_batch([
    #     Comment(
    #         rpid=7,
    #         parentid=0,
    #         mid=106,
    #         name="批量用户1",
    #         information="批量评论1",
    #         time=1678886407,
    #         oid=10002,
    #     ),
    #     Comment(
    #         rpid=8,
    #         parentid=0,
    #         mid=107,
    #         name="批量用户2",
    #         information="批量评论2",
    #         time=1678886408,
    #         oid=10001,
    #     )
    # ], overwrite=False)}"
    # )  # rpid=1 不应该被写入
    # print(
    #     f"批量添加（覆盖）评论数量: {comment_repo.add_comments_batch([
    #     Comment(
    #         rpid=7,
    #         parentid=0,
    #         mid=106,
    #         name="批量用户1",
    #         information="批量评论1",
    #         time=1678886407,
    #         oid=10002,
    #     ),
    #     Comment(
    #         rpid=8,
    #         parentid=0,
    #         mid=107,
    #         name="批量用户2",
    #         information="批量评论2",
    #         time=1678886408,
    #         oid=10001,
    #     )
    # ], overwrite=True)}"
    # )  # rpid=1 应该被写入
    # # --- 测试查询评论 (分页) ---
    # print("\n--- 测试按 mid 分页查询评论 ---")
    # mid_comments = comment_repo.get_comments_by_mid_paginated(
    #     mids=[101, 102], page=1, page_size=2
    # )
    # mid_comments_page2 = comment_repo.get_comments_by_mid_paginated(
    #     mids=[101, 102], page=2, page_size=2
    # )
    # # --- 测试查询评论 (流式) ---
    # print("\n--- 测试按 mid 流式查询评论 ---")
    # mid_stream = comment_repo.get_comments_by_mid_stream(mids=[101, 106])
    # for i, comment in enumerate(mid_stream):
    #     print(f"流式获取mid评论 {i+1}: {comment.name}: {comment.information[:10]}...")
    #     if i >= 5:  # 只打印前几条，避免刷屏
    #         break
    # print("\n--- 测试按 oid 流式查询评论 ---")
    # oid_stream = comment_repo.get_comments_by_oid_stream(oids=[10001, 10002])
    # for i, comment in enumerate(oid_stream):
    #     print(f"流式获取oid评论 {i+1}: {comment.oid} - {comment.information[:10]}...")
    #     if i >= 5:  # 只打印前几条，避免刷屏
    #         break
    # # --- 测试删除评论 ---
    # deleted_count_mid = comment_repo.delete_comments_by_mid(mids=[101])
    # print(f"删除了 mid 101 的 {deleted_count_mid} 条评论。")
    # deleted_count_oid = comment_repo.delete_comments_by_oid(oids=[10002])
    # print(f"删除了 oid 10002 的 {deleted_count_oid} 条评论。")

    # # 用户
    # # 批量添加/更新
    # print("\n--- 测试批量添加/更新用户 ---")
    # user_repo.add_or_update_users_batch(
    #     User(mid=20003, name="批量用户C", sex="男", fans=200, vip=0),
    #     User(mid=20004, name="批量用户D", sex="不明", fans=10, vip=0),
    # )
    # # --- 测试查询用户 ---
    # print("\n--- 测试按 mid 查询用户 ---")
    # queried_users = user_repo.get_users_by_mid(mids=[20001, 20003])
    # print(f"查询 mids [20001, 20003] 的用户:")
    # queried_single_user = user_repo.get_user_by_mid(20002)
    # print(f"查询单个 mid 20002 的用户: {queried_single_user}")
    # # --- 测试删除用户 ---
    # print("\n--- 测试删除用户 ---")
    # deleted_count = user_repo.delete_users_by_mid(mids=[20002, 20004])
    # print(f"删除了 {deleted_count} 条用户记录。")
    # users_after_delete = user_repo.get_users_by_mid(mids=[20001, 20002, 20003, 20004])
    # print(f"删除后用户总数: {len(users_after_delete)}")


#     print("请选择获取评论模式：")
#     print("0: 获取视频评论（多个BV号用逗号间隔）")
#     print("1: 获取单个up主视频评论")
#     print("2: 获取uid评论")
#     get_mode = int(input("请输入模式（0/1/2）："))


# if __name__ == "__main__":
#     print("请选择获取评论模式：")
#     print("0: 获取视频评论（多个BV号用逗号间隔）")
#     print("1: 获取单个up主视频评论")
#     get_mode = int(input("请输入模式（0/1）："))
#     single_pos = ""
#     # 创建基础目录结构
#     bv_dir = os.path.join(".", "comment", "bv")
#     up_dir = os.path.join(".", "comment", "up")

#     if not os.path.exists(bv_dir):
#         os.makedirs(bv_dir)
#     if not os.path.exists(up_dir):
#         os.makedirs(up_dir)

#     if get_mode == 0:
#         print("请输入视频BV号：")
#         bv_input = input()
#         print("是否开启二级评论爬取：")
#         print("0: 否")
#         print("1: 是")
#         is_second = int(input())
#         bv_list = [bv.strip() for bv in bv_input.split(",") if bv.strip()]
#         successfully_crawled_bvs = []
#         for i, bv in enumerate(bv_list):
#             try:
#                 print(f"正在爬取第 {i+1}/{len(bv_list)} 个BV号：{bv}")
#                 crawler_success = BilibiliCommentCrawler(bv, is_second).crawl()
#                 if crawler_success:
#                     successfully_crawled_bvs.append(bv)
#             except Exception as e:
#                 print(f"爬取BV号 {bv} 时出错: {e}")
#         if not successfully_crawled_bvs:
#             print("所有BV号的评论爬取都失败了，请检查BV号或稍后再试。")
#         first_bv = successfully_crawled_bvs[0]
#         merged_filename_base = f"{first_bv}"  # 文件名基础，加上“等”字
#         if len(successfully_crawled_bvs) > 1:
#             merged_filename_base += "等"

#         if is_second == 0:
#             is_second = False
#         else:
#             is_second = True
#         single_pos = comment_merger.CommentMerger().merge_comments(
#             successfully_crawled_bvs, merged_filename_base
#         )  # 可以指定输出目录
#         print(single_pos)

#     elif get_mode == 1:
#         print("请输入up主ID：")
#         up_id = input()
#         print("是否开启二级评论爬取（默认开启）：")
#         print("0: 否")
#         print("1: 是")
#         is_second = int(input())
#         if is_second == 0:
#             is_second = False
#         else:
#             is_second = True

#         # 获取UP主所有视频aid列表
#         crawler = get_all_bv.GetInfo(up_id, headless=True)
#         video_ids = crawler.next_page()
#         print(f"共获取到 {len(video_ids)} 个视频，开始批量爬取评论...")
#         for i, id in enumerate(video_ids):
#             try:
#                 print(f"正在爬取第 {i+1}/{len(video_ids)} 个视频，AID: {id}")
#                 # B站可以通过av号访问视频，aid就是av号去掉前缀
#                 BilibiliCommentCrawler(id, is_second).crawl()
#             except Exception as e:
#                 print(f"爬取视频 AID: {id} 时出错: {e}")

#         single_pos = comment_merger.CommentMerger().merge_comments(
#             video_ids, up_id
#         )  # 可以指定输出目录

#     else:
#         print("输入错误")
#         exit(1)

#     print("请选择是否分析：")

#     print("0: 否")
#     print("1: 是")
#     analyze_mode = int(input())

#     if analyze_mode == 1:
#         analyze.CommentAnalyzer(single_pos).run_all_analysis()

#     elif analyze_mode == 0:
#         print("程序退出")
#         exit(0)
#     else:
#         print("输入错误")
#         exit(1)
