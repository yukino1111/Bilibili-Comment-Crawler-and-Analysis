# B 站评论爬虫并分析工具

## 功能介绍

### 评论爬取：

支持 BV 号和 UID 两种模式


### 数据分析：

1.  **用户分析：** IP 地区、性别、大会员比例等
2.  **时间分析：** 评论发布时间分布
3.  **内容分析：** 生成评论词云
4.  **数据导出：** 支持 CSV 格式下载

## 使用方法

1. 确保您已安装Python环境
2. 克隆此仓库到本地
   ```
   git clone https://github.com/1dyer/bilibili-comment-crawler.git
   cd bilibili-comment-crawler
   ```
3. 安装所需依赖
   ```
   pip install -r requirements.txt
   ```
4. 直接运行主程序即可

## 致谢

本项目基于以下开源项目：

- 评论爬虫模块：[bilibili-comment-crawler](https://github.com/1dyer/bilibili-comment-crawler)
- UP 主视频获取模块：[参考文章](https://blog.csdn.net/qq_41661843/article/details/136329757)