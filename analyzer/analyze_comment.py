import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
from wordcloud import WordCloud
import jieba
import os
import re
from snownlp import SnowNLP
import matplotlib.dates as mdates
import collections
import numpy as np  # 用于数值计算

# from utils.config import FONT_PATH, HIT_STOPWORDS_PATH, IMAGE_DIR # 实际项目中启用


# 为了独立运行，暂时模拟 config
class MockConfig:
    # 确保这个路径有效，或替换为你系统中存在的字体
    FONT_PATH = "C:/Windows/Fonts/simhei.ttf"
    HIT_STOPWORDS_PATH = os.path.join(
        os.path.dirname(__file__), "hit_stopwords.txt"
    )  # 假定停用词文件在同目录下
    IMAGE_DIR = os.path.join(os.path.dirname(__file__), "output_images")


FONT_PATH = MockConfig.FONT_PATH
HIT_STOPWORDS_PATH = MockConfig.HIT_STOPWORDS_PATH
IMAGE_DIR = MockConfig.IMAGE_DIR

class CommentAnalyzer:
    def __init__(self, csv_path, db_name):
        self.csv_path = csv_path
        self.db_name = db_name  # 新增数据库名，未来可能从数据库加载数据

        self.font_path = FONT_PATH
        self.stopwords_path = HIT_STOPWORDS_PATH
        self.output_dir = IMAGE_DIR
        self.df = None  # 存储原始评论数据
        self.df_unique_users = None  # 存储按用户ID去重后的数据
        self._setup_matplotlib_font()  # 设置matplotlib字体
        self._create_output_directory()  # 创建输出目录

    def _setup_matplotlib_font(self):
        """设置matplotlib支持中文显示和使用指定字体。"""
        try:
            font = fm.FontProperties(fname=self.font_path)
            plt.rcParams["font.sans-serif"] = [font.get_name()]
            plt.rcParams["axes.unicode_minus"] = False
            print(f"成功设置matplotlib字体: {font.get_name()}")
        except Exception as e:
            print(
                f"警告: 设置matplotlib字体失败，请检查字体文件路径 '{self.font_path}' 是否正确或文件是否有效。错误信息: {e}"
            )
            plt.rcParams["font.sans-serif"] = ["SimHei", "Arial Unicode MS"]  # Fallback
            plt.rcParams["axes.unicode_minus"] = False
            print("回退到默认中文字体。")

    def _create_output_directory(self):
        """创建保存图片的文件夹。"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"创建输出目录: {self.output_dir}")

    def load_data(self):
        """加载CSV文件并进行初步数据清洗。"""
        try:
            self.df = pd.read_csv(self.csv_path)
            print(f"成功加载数据文件: {self.csv_path}")

            self.df["评论ID"] = self.df["评论ID"].astype(str)
            self.df["评论时间"] = pd.to_datetime(self.df["评论时间"])

            # 针对用户维度的分析，根据用户ID去重，保留每个用户的第一次出现记录
            # 使用copy()避免SettingWithCopyWarning
            self.df_unique_users = self.df.drop_duplicates(subset=["用户ID"]).copy()
            print(f"原始评论数量: {len(self.df)}")
            print(f"去重用户数量: {len(self.df_unique_users)}")

        except FileNotFoundError:
            print(
                f"错误：未找到指定的CSV文件: {self.csv_path}。请检查文件路径是否正确。"
            )
            self.df = None
            self.df_unique_users = None
            return False
        except Exception as e:
            print(f"加载或处理数据时发生错误: {e}")
            self.df = None
            self.df_unique_users = None
            return False
        return True

    def _display_plot(
        self,
        plot_data,
        plot_type,
        show_title,
        show_title_size,
        x,
        y,
        dpi,
        **plot_kwargs,
    ):
        """
        在新窗口显示图表。
        """
        display_fig, display_ax = plt.subplots(figsize=(x / dpi, y / dpi), dpi=dpi)

        self._render_plot_on_ax(display_ax, plot_data, plot_type, **plot_kwargs)

        # 始终显示坐标轴，除了词云、饼图和雷达图
        if plot_type in ["imshow", "pie", "radar"]:
            display_ax.axis("off")
        else:  # For bar/line plots, set labels
            if "xlabel" in plot_kwargs:
                display_ax.set_xlabel(plot_kwargs["xlabel"])
            if "ylabel" in plot_kwargs:
                display_ax.set_ylabel(plot_kwargs["ylabel"])

        if show_title:
            display_ax.set_title(show_title, fontsize=show_title_size)

        display_fig.tight_layout()  # 调整布局
        plt.show()
        plt.close(display_fig)  # 关闭显示窗口，释放资源

    def _save_plot(
        self, plot_data, plot_type, save_filename, x, y, dpi, save_format, **plot_kwargs
    ):
        """
        将图表保存到文件。
        """
        save_figsize = (x / dpi, y / dpi)

        save_fig, save_ax = plt.subplots(figsize=save_figsize, dpi=dpi)

        self._render_plot_on_ax(save_ax, plot_data, plot_type, **plot_kwargs)

        # 始终不显示标题，不显示坐标轴 (除了词云、饼图和雷达图)
        if plot_type in ["imshow", "pie", "radar"]:
            save_ax.axis("off")
        else:
            if "xlabel" in plot_kwargs:
                save_ax.set_xlabel(plot_kwargs["xlabel"])
            if "ylabel" in plot_kwargs:
                save_ax.set_ylabel(plot_kwargs["ylabel"])

        save_fig.subplots_adjust(bottom=0, top=1, left=0, right=1)

        if not save_filename.lower().endswith(f".{save_format}"):
            save_filename_with_ext = (
                f"{os.path.splitext(save_filename)[0]}.{save_format}"
            )
        else:
            save_filename_with_ext = save_filename

        getSavePath = os.path.join(self.output_dir, save_filename_with_ext)

        plt.savefig(
            getSavePath,
            bbox_inches="tight",
            format=save_format,
            transparent=True,
            dpi=dpi,
        )
        print(f"图片已保存到: {getSavePath} (格式: {save_format}, 透明背景: True)")
        plt.close(save_fig)

    def _render_plot_on_ax(self, ax, plot_data, plot_type, **plot_kwargs):
        """
        内部辅助方法：在给定的Axes对象上绘制图表。
        """
        if plot_type == "imshow":
            ax.imshow(
                plot_data,
                interpolation=plot_kwargs.get("interpolation", "bilinear"),
            )
        elif plot_type == "bar":
            sns.barplot(
                x=plot_data[0],
                y=plot_data[1],
                ax=ax,
                palette=plot_kwargs.get("palette", "viridis"),
            )
            if "rotation" in plot_kwargs and plot_kwargs["rotation"] is not None:
                ax.set_xticks(plot_kwargs.get("xticks", ax.get_xticks()))
                ax.set_xticklabels(
                    plot_kwargs.get("xticklabels", ax.get_xticklabels()),
                    rotation=plot_kwargs["rotation"],
                    ha=plot_kwargs.get("ha", "center"),
                )
        elif plot_type == "pie":
            ax.pie(
                plot_data[0],
                labels=plot_data[1],
                autopct=plot_kwargs.get("autopct", "%1.1f%%"),
                startangle=plot_kwargs.get("startangle", 140),
                colors=plot_kwargs.get("colors"),
            )
            ax.axis("equal")
        elif plot_type == "line":
            plot_data.plot(kind="line", ax=ax)
            if plot_kwargs.get("format_dates", False):
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
                ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        elif plot_type == "radar":  # 新增雷达图绘制逻辑
            # plot_data: (categories, values_red, values_blue)
            categories = plot_data[0]
            values_red = plot_data[1]  # 最爱发评论的人
            values_blue = plot_data[2]  # 平均评论

            num_vars = len(categories)
            # 计算每个角度
            angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
            # 闭合雷达图
            values_red = values_red + values_red[:1]
            values_blue = values_blue + values_blue[:1]
            angles = angles + angles[:1]

            # 绘制线条
            ax.plot(
                angles,
                values_red,
                color="r",
                linewidth=2,
                linestyle="solid",
                label="最活跃用户评论",
            )
            ax.fill(angles, values_red, color="r", alpha=0.25)

            ax.plot(
                angles,
                values_blue,
                color="b",
                linewidth=2,
                linestyle="solid",
                label="平均评论",
            )
            ax.fill(angles, values_blue, color="b", alpha=0.25)

            # 设置标签
            ax.set_yticklabels([])  # 不显示刻度
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories, fontsize=12)  # 维度标签
            ax.legend(loc="upper right", bbox_to_anchor=(1.1, 1.1))  # 显示图例

    def plot_figure(
        self,
        plot_data,
        plot_type,
        save_filename,
        x: int,
        y: int,
        show_plot: bool = True,
        show_title: str = "",
        show_title_size: int = 16,
        dpi: int = 100,
        save_format: str = "png",
        **plot_kwargs,
    ):
        """
        统一的绘图和保存函数。
        :param plot_data: 要绘制的数据。
        :param plot_type: 绘制类型 ('bar', 'pie', 'line', 'imshow', 'radar')。
        :param save_filename: 保存文件的文件名。
        :param x: 图形宽度 (像素，原始尺度)。
        :param y: 图形高度 (像素，原始尺度)。
        :param show_plot: 是否在弹窗显示图表。
        :param show_title: 显示图表的标题。
        :param show_title_size: 显示图表标题的字体大小。
        :param dpi: 图片保存和显示的DPI。
        :param save_format: 图片保存的格式 (如 'png', 'jpg', 'svg', 'pdf')。
        :param plot_kwargs: 其他传递给底层绘图函数的参数。
        """
        # 调用保存函数
        self._save_plot(
            plot_data, plot_type, save_filename, x, y, dpi, save_format, **plot_kwargs
        )

        # 调用显示函数
        if show_plot:
            self._display_plot(
                plot_data,
                plot_type,
                show_title,
                show_title_size,
                x,
                y,
                dpi,
                **plot_kwargs,
            )

    # (其他分析方法保持不变，这里省略以节省篇幅，但它们会调用 plot_figure)
    def analyze_ip_distribution(self):
        """分析用户IP属地分布并生成柱状图（基于去重用户）。"""
        if self.df_unique_users is None:
            print("数据未加载，无法进行IP属地分析。")
            return
        filtered_users = self.df_unique_users.copy()
        filtered_users = filtered_users[filtered_users["IP属地"] != "未知"]
        ip_counts = filtered_users["IP属地"].value_counts().head(10)
        if ip_counts.empty:
            print("过滤IP属地为'未知'后，没有足够的有效数据进行IP属地分析。")
            return
        self.plot_figure(
            plot_data=(ip_counts.index, ip_counts.values),
            plot_type="bar",
            save_filename="user_ip_top10_distribution.png",
            x=1600,
            y=900,
            show_plot=True,
            show_title="用户IP属地 Top 10 分布",
            show_title_size=16,
            dpi=100,
            palette="viridis",
            xlabel="IP属地",
            ylabel="用户数量",
            rotation=45,
            ha="right",
        )

    def analyze_vip_status(self):
        """分析用户大会员状态并生成扇形图（基于去重用户）。"""
        if self.df_unique_users is None:
            print("数据未加载，无法进行大会员状态分析。")
            return
        vip_counts = self.df_unique_users["是否是大会员"].value_counts()
        if vip_counts.empty:
            print("没有足够的数据进行大会员状态分析。")
            return
        self.plot_figure(
            plot_data=(vip_counts.values, vip_counts.index),
            plot_type="pie",
            save_filename="user_vip_status.png",
            x=800,
            y=800,
            show_plot=True,
            show_title="用户大会员状态分布",
            show_title_size=16,
            dpi=100,
            autopct="%1.1f%%",
            startangle=140,
        )

    def analyze_gender_distribution(self):
        """分析用户性别分布并生成扇形图（基于去重用户）。"""
        if self.df_unique_users is None:
            print("数据未加载，无法进行性别分析。")
            return
        gender_counts = self.df_unique_users["性别"].value_counts()
        if gender_counts.empty:
            print("没有足够的数据进行性别分析。")
            return
        self.plot_figure(
            plot_data=(gender_counts.values, gender_counts.index),
            plot_type="pie",
            save_filename="user_gender_distribution.png",
            x=800,
            y=800,
            show_plot=True,
            show_title="用户性别分布",
            show_title_size=16,
            dpi=100,
            autopct="%1.1f%%",
            startangle=140,
        )

    def analyze_level_distribution(self):
        """分析用户等级分布并生成扇形图（基于去重用户）。"""
        if self.df_unique_users is None:
            print("数据未加载，无法进行用户等级分析。")
            return
        level_counts = self.df_unique_users["用户等级"].value_counts().sort_index()
        if level_counts.empty:
            print("没有足够的数据进行用户等级分析。")
            return
        self.plot_figure(
            plot_data=(level_counts.values, level_counts.index),
            plot_type="pie",
            save_filename="user_level_distribution.png",
            x=800,
            y=800,
            show_plot=True,
            show_title="用户等级分布",
            show_title_size=16,
            dpi=100,
            autopct="%1.1f%%",
            startangle=140,
        )

    def analyze_comment_time_trend(self):
        """分析评论数量随时间变化趋势并生成折线图（基于所有评论）。"""
        if self.df is None:
            print("数据未加载，无法进行评论时间趋势分析。")
            return
        if not pd.api.types.is_datetime64_any_dtype(self.df["评论时间"]):
            self.df["评论时间"] = pd.to_datetime(self.df["评论时间"])
        df_sorted_time = self.df.sort_values(by="评论时间")
        comment_counts_by_day = df_sorted_time.groupby(
            df_sorted_time["评论时间"].dt.date
        ).size()
        if comment_counts_by_day.empty:
            print("没有足够的数据进行评论时间趋势分析。")
            return
        self.plot_figure(
            plot_data=comment_counts_by_day,
            plot_type="line",
            save_filename="comment_time_trend.png",
            x=1600,
            y=900,
            show_plot=True,
            show_title="评论数量随时间变化趋势",
            show_title_size=16,
            dpi=100,
            xlabel="日期",
            ylabel="评论数量",
            format_dates=True,
        )

    def analyze_comment_hour_distribution(self):
        """分析评论数量按小时分布并生成柱状图（基于所有评论）。"""
        if self.df is None:
            print("数据未加载，无法进行评论小时分布分析。")
            return
        if not pd.api.types.is_datetime64_any_dtype(self.df["评论时间"]):
            self.df["评论时间"] = pd.to_datetime(self.df["评论时间"])
        self.df["评论小时"] = self.df["评论时间"].dt.hour
        comment_counts_by_hour = self.df["评论小时"].value_counts().sort_index()
        full_hour_index = pd.Index(range(24))
        comment_counts_by_hour = comment_counts_by_hour.reindex(
            full_hour_index, fill_value=0
        )
        if comment_counts_by_hour.empty:
            print("没有足够的数据进行评论小时分布分析。")
            return
        self.plot_figure(
            plot_data=(
                comment_counts_by_hour.index,
                comment_counts_by_hour.values,
            ),
            plot_type="bar",
            save_filename="comment_hour_distribution.png",
            x=1600,
            y=900,
            show_plot=True,
            show_title="评论数量按小时分布",
            show_title_size=16,
            dpi=100,
            palette="viridis",
            xlabel="小时",
            ylabel="评论数量",
            xticks=range(24),
        )

    def analyze_sentiment(self):
        if self.df is None or self.df.empty:
            print("评论数据为空，无法进行情感分析。")
            return
        print("开始进行情感分析...")
        if "sentiment_score" not in self.df.columns:
            self.df["sentiment_score"] = self.df["评论内容"].apply(
                lambda x: SnowNLP(str(x)).sentiments if pd.notnull(x) else None
            )

        def classify_sentiment(score):
            if score is None:
                return "未知"
            elif score > 0.7:
                return "积极"
            elif score < 0.3:
                return "消极"
            else:
                return "中立"

        if "sentiment_label" not in self.df.columns:
            self.df["sentiment_label"] = self.df["sentiment_score"].apply(
                classify_sentiment
            )
        print("情感分析完成。")
        sentiment_counts = self.df["sentiment_label"].value_counts()
        if not sentiment_counts.empty:
            self.plot_figure(
                plot_data=(
                    sentiment_counts.values,
                    sentiment_counts.index,
                ),
                plot_type="pie",
                save_filename="comment_sentiment_distribution.png",
                x=800,
                y=800,
                show_plot=True,
                show_title="评论情感分布",
                show_title_size=16,
                dpi=100,
                autopct="%1.1f%%",
                startangle=140,
                colors=sns.color_palette("pastel"),
            )
        else:
            print("没有足够的有效情感分析结果来生成分布图。")
        average_sentiment_score = self.df["sentiment_score"].dropna().mean()
        print(f"评论的平均情感分数 (0-1, 1为最积极): {average_sentiment_score:.4f}")

    def generate_wordcloud(self):
        if self.df is None:
            print("数据未加载，无法生成词云。")
            return
        all_comments = " ".join(self.df["评论内容"].dropna())
        all_comments = re.sub(r"\[.*?\]", "", all_comments)
        stopwords = set()
        try:
            with open(self.stopwords_path, "r", encoding="utf-8") as f:
                for line in f:
                    stopwords.add(line.strip())
            print(f"成功加载停用词文件: {self.stopwords_path}")
        except FileNotFoundError:
            print(
                f"警告：未找到停用词文件: {self.stopwords_path}，将不使用停用词过滤。"
            )
        seg_list = jieba.cut(all_comments, cut_all=False)
        filtered_words = [
            word for word in seg_list if word not in stopwords and len(word) > 1
        ]
        word_count = collections.Counter(filtered_words)
        wordcloud = WordCloud(
            width=1600,
            height=900,
            background_color="white",
            collocations=False,
            font_path=self.font_path,
            scale=2,
        ).generate_from_frequencies(word_count)
        self.plot_figure(
            plot_data=wordcloud,
            plot_type="imshow",
            save_filename="comment_wordcloud.png",
            x=1600,
            y=900,
            show_plot=True,
            show_title="评论内容词云",
            show_title_size=16,
            dpi=100,
        )

    def analyze_radar_chart(self):
        """
        生成用户特征雷达图。
        红线：最爱发评论的用户中，点赞+评论*10最高的那条评论的指标。
        蓝线：所有评论的平均指标。
        维度：用户等级（0-6），回复数，点赞数，是否是大会员。
        """
        if self.df is None or self.df.empty:
            print("数据未加载或为空，无法进行雷达图分析。")
            return

        # 1. 找到“最爱发评论的那个人”（用户ID频率最高的）
        most_frequent_user_id = self.df["用户ID"].mode().iloc[0]
        print(f"最活跃用户ID: {most_frequent_user_id}")

        # 2. 筛选出该用户的所有评论
        most_frequent_user_comments = self.df[
            self.df["用户ID"] == most_frequent_user_id
        ].copy()

        if most_frequent_user_comments.empty:
            print(f"未找到用户ID {most_frequent_user_id} 的评论，无法进行雷达图分析。")
            return

        # 3. 在这些评论中，找到 (点赞数 + 回复数 * 10) 最高的那条评论
        most_frequent_user_comments["score"] = (
            most_frequent_user_comments["点赞数"]
            + most_frequent_user_comments["回复数"] * 10
        )

        # 确保 score 列不为空，或者处理NaN值
        most_frequent_user_comments["score"] = most_frequent_user_comments[
            "score"
        ].fillna(0)

        # 如果有多个最高 score 的评论，取第一条
        best_comment_for_frequent_user = most_frequent_user_comments.loc[
            most_frequent_user_comments["score"].idxmax()
        ]

        # 提取其维度数据 (红线数据)
        # 将"是"/"否"转换为0/1，方便归一化
        vip_status_red = (
            1 if best_comment_for_frequent_user["是否是大会员"] == "是" else 0
        )

        data_red = {
            "用户等级": best_comment_for_frequent_user["用户等级"],
            "回复数": best_comment_for_frequent_user["回复数"],
            "点赞数": best_comment_for_frequent_user["点赞数"],
            "是否是大会员": vip_status_red,
        }
        print(f"最活跃用户特征数据（红线）: {data_red}")

        # 4. 计算所有评论的平均指标 (蓝线数据)
        # 用户等级平均值直接基于所有评论的“用户等级”列
        avg_level = self.df["用户等级"].mean()
        avg_reply_num = self.df["回复数"].mean()
        avg_like_num = self.df["点赞数"].mean()
        # 大会员比例作为平均值
        avg_vip_status = (
            self.df["是否是大会员"] == "是"
        ).mean()  # 转换为 0/1 后取平均，表示比例

        data_blue = {
            "用户等级": avg_level,
            "回复数": avg_reply_num,
            "点赞数": avg_like_num,
            "是否是大会员": avg_vip_status,
        }
        print(f"平均评论特征数据（蓝线）: {data_blue}")

        # 5. 数据归一化 (Min-Max Normalization: (x - min) / (max - min))
        # 确定每个维度的最大值，用于归一化。
        # 等级最高6，回复数和点赞数取所有评论中的最大值，vip最高1

        max_level = 6  # 等级固定为6
        max_reply_num = (
            self.df["回复数"].max() if not self.df["回复数"].empty else 1
        )  # 避免除以0
        max_like_num = (
            self.df["点赞数"].max() if not self.df["点赞数"].empty else 1
        )  # 避免除以0
        max_vip = 1  # VIP固定为1

        # 如果最大值是0，要设置为1避免除以0
        max_reply_num = max(1, max_reply_num)
        max_like_num = max(1, max_like_num)

        # 归一化红线数据
        normalized_red = [
            data_red["用户等级"] / max_level,
            data_red["回复数"] / max_reply_num,
            data_red["点赞数"] / max_like_num,
            data_red["是否是大会员"] / max_vip,
        ]

        # 归一化蓝线数据
        normalized_blue = [
            data_blue["用户等级"] / max_level,
            data_blue["回复数"] / max_reply_num,
            data_blue["点赞数"] / max_like_num,
            data_blue["是否是大会员"] / max_vip,
        ]

        # 由于雷达图点赞和回复数可能为0，归一化后也为0，这是正常情况。
        # 如果需要更平滑的雷达图，可以考虑加一个小 epsilon 或 Min-Max scaling of a larger range

        categories = ["用户等级", "回复数", "点赞数", "是否是大会员"]

        # 6. 绘制雷达图
        self.plot_figure(
            plot_data=(categories, normalized_red, normalized_blue),
            plot_type="radar",  # 新增的雷达图类型
            save_filename="user_features_radar_chart.png",
            x=900,  # 雷达图通常更方正
            y=900,
            show_plot=True,
            show_title="用户特征雷达图：最活跃用户 vs. 平均评论",
            show_title_size=16,
            dpi=100,
        )

    def run_all_analysis(self):
        """运行所有分析和图表生成。"""
        if self.load_data():
            self.analyze_ip_distribution()
            self.analyze_vip_status()
            self.analyze_gender_distribution()
            self.analyze_level_distribution()
            self.analyze_comment_time_trend()
            self.analyze_comment_hour_distribution()
            self.analyze_sentiment()
            self.generate_wordcloud()
            self.analyze_radar_chart()
            print("所有分析已完成。")


# --- 如何使用 (测试部分) ---
if __name__ == "__main__":
    analyzer = CommentAnalyzer(test_csv_path="")
    analyzer.run_all_analysis()

