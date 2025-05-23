import csv
import os
from typing import List
from repository.comment_repository import CommentRepository
from entity.comment import Comment

def export_comments_by_mid_to_csv(
    output_filepath: str, mids: List[int], db_name: str = "./assets/bili_data.db"
):
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
                    comment.rpid,
                    comment.mid,
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
