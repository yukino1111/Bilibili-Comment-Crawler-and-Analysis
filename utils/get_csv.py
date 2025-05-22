import csv
import os
from typing import List
from repository.comment_repository import CommentRepository
from entity.comment import Comment

def export_comments_by_mid_to_csv(
    output_filepath: str, mids: List[int], db_name: str = "./assets/bili_data.db"
):
    """
    根据给定的用户ID (mid) 列表，查询评论并将其导出到 CSV 文件。

    Args:
        output_filepath (str): CSV 文件的完整输出路径（含文件名）。
        mids (List[int]): 用户ID列表。
        db_name (str): 数据库文件名。
    """
    if not mids:
        print(
            "Warning: No mids provided for export. CSV file will be empty (header only if created)."
        )
        return

    repo = CommentRepository(db_name)
    comments_iterator = repo.get_comments_by_mid_stream(mids)

    # 确保输出目录存在
    output_dir = os.path.dirname(output_filepath)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        with open(output_filepath, "w", newline="", encoding="utf-8-sig") as csvfile:
            csv_writer = csv.writer(csvfile)

            # 写入 CSV 表头
            header = [
                "序号",
                "上级评论ID",
                "评论ID",
                "用户ID",
                "用户名",
                "用户等级",
                "性别",
                "评论内容",
                "评论时间",
                "回复数",
                "点赞数",
                "个性签名",
                "IP属地",
                "是否是大会员",
                "头像",
            ]
            csv_writer.writerow(header)

            row_number = 0
            for comment in comments_iterator:
                row_number += 1
                try:
                    # 将 Unix 时间戳转换为易读的日期时间格式
                    import datetime

                    comment_time_str = datetime.datetime.fromtimestamp(
                        comment.time
                    ).strftime("%Y-%m-%d %H:%M:%S")
                except (TypeError, ValueError):
                    comment_time_str = str(comment.time)  # 转换失败则保留原样

                # 将 VIP 状态从数字转换为文字描述
                vip_status = "是" if comment.vip == 1 else "否"

                # 根据你的字段顺序构建行数据
                row_data = [
                    row_number,
                    comment.parentid,
                    comment.rpid,
                    comment.mid,
                    comment.name,
                    comment.level,
                    comment.sex,
                    comment.information,
                    comment_time_str,  # 转换后的时间
                    comment.single_reply_num,
                    comment.single_like_num,
                    comment.sign,
                    comment.ip_location,
                    vip_status,  # 转换后的VIP状态
                    comment.face,
                ]
                csv_writer.writerow(row_data)
        print(
            f"评论已成功导出到: {output_filepath} (根据 mid: {mids})，共 {row_number} 条记录。"
        )
    except Exception as e:
        print(f"导出评论到 CSV 失败: {e}")


def export_comments_by_oid_to_csv(
    output_filepath: str, oids: List[int], db_name: str = "bilibili_comments.db"
):
    if not oids:
        print(
            "Warning: No oids provided for export. CSV file will be empty (header only if created)."
        )
        return

    repo = CommentRepository(db_name)
    comments_iterator = repo.get_comments_by_oid_stream(oids)  # 使用 oid 的流式查询

    # 确保输出目录存在
    output_dir = os.path.dirname(output_filepath)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        with open(output_filepath, "w", newline="", encoding="utf-8-sig") as csvfile:
            csv_writer = csv.writer(csvfile)

            # 写入 CSV 表头 (与按 mid 导出相同)
            header = [
                "序号",
                "上级评论ID",
                "评论ID",
                "用户ID",
                "用户名",
                "用户等级",
                "性别",
                "评论内容",
                "评论时间",
                "回复数",
                "点赞数",
                "个性签名",
                "IP属地",
                "是否是大会员",
                "头像",
            ]
            csv_writer.writerow(header)

            row_number = 0
            for comment in comments_iterator:
                row_number += 1
                try:
                    import datetime

                    comment_time_str = datetime.datetime.fromtimestamp(
                        comment.time
                    ).strftime("%Y-%m-%d %H:%M:%S")
                except (TypeError, ValueError):
                    comment_time_str = str(comment.time)

                vip_status = "是" if comment.vip == 1 else "否"

                row_data = [
                    row_number,
                    comment.parentid,
                    comment.rpid,  # 评论ID
                    comment.mid,  # 用户ID
                    comment.name,
                    comment.level,
                    comment.sex,
                    comment.information,
                    comment_time_str,
                    comment.single_reply_num,
                    comment.single_like_num,
                    comment.sign,
                    comment.ip_location,
                    vip_status,
                    comment.face,
                ]
                csv_writer.writerow(row_data)
        print(
            f"评论已成功导出到: {output_filepath} (根据 oid: {oids})，共 {row_number} 条记录。"
        )
    except Exception as e:
        print(f"导出评论到 CSV 失败: {e}")


# --- 测试部分 ---
if __name__ == "__main__":
    # 为了测试，我们需要一个数据库文件和一些数据。
    # 假设你已经运行了 CommentRepository 的测试部分，并且 'test_comments.db' 已经有一些数据。
    # 如果没有，请先运行 CommentRepository.py 中的 __main__ 部分。

    # 确保有数据库文件（如果不存在，mock CommentRepository 也能工作）
    _db_file = "./assets/bili_data.db"  # 假设使用原始数据库文件名

    # 确保输出目录存在
    if not os.path.exists("output_csv"):
        os.makedirs("output_csv")

    # # 测试导出 by mid
    # print("\n--- 导出评论 (按 mid) ---")
    # export_comments_by_mid_to_csv(
    #     output_filepath="./output_csv/comments_by_mid_101_102.csv",
    #     mids=[101, 102],
    #     db_name=_db_file,
    # )

    # 测试导出 by oid
    print("\n--- 导出评论 (按 oid) ---")
    export_comments_by_oid_to_csv(
        output_filepath="./output_csv/comments_by_oid_10001.csv",
        oids=[114544999399889],
        db_name=_db_file,
    )

    # print("\n--- 导出评论 (按多个 oid) ---")
    # export_comments_by_oid_to_csv(
    #     output_filepath="./output_csv/comments_by_oid_10001_10002.csv",
    #     oids=[10001, 10002],
    #     db_name=_db_file,
    # )
