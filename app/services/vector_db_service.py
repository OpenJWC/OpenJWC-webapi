import os
import chromadb
from datetime import date
from zhipuai import ZhipuAI
from datetime import datetime
from app.utils.logging_manager import setup_logger
from app.core.config import MAX_DAY_DIFF

# 初始化智谱客户端和向量数据库
client = ZhipuAI(api_key=os.environ.get("ZHIPUAI_API_KEY"))
chroma_client = chromadb.PersistentClient(path="./data/chroma_db")
collection = chroma_client.get_or_create_collection(name="notices")

logger = setup_logger("vector_db_logs")


class VectorDBService:
    @staticmethod
    def get_embedding(text: str):
        """调用智谱 embedding-3 接口"""
        logger.info(f"调用智谱 embedding-3 接口，输入文本: {text}")
        try:
            response = client.embeddings.create(
                model="embedding-3",
                input=text,
            )
        except Exception as e:
            logger.error(f"调用智谱 embedding-3 接口失败: {e}")
            raise Exception("调用智谱 embedding-3 接口失败")
        return response.data[0].embedding

    def check_notice_exists(self, source_notice_id: str) -> bool:
        """
        核心拦截器：检查这篇资讯是否已经处理过。
        """
        results = collection.get(
            where={"source_id": source_notice_id}, limit=1, include=["metadatas"]
        )
        if len(results["ids"]) > 0:
            logger.info(f"资讯{source_notice_id}已经处理")
            return True
        else:
            logger.info(f"资讯未处理{source_notice_id}，将进行向量化处理")
            return False

    def add_chunk(self, chunk_id: str, content: str, metadata: dict):
        logger.info(f"正在为 Chunk {chunk_id} 生成 Embedding (消耗 Token)...")
        vector = self.get_embedding(content)

        collection.upsert(
            ids=[chunk_id],
            embeddings=[vector],
            documents=[content],
            metadatas=[metadata],
        )

    def search(self, query: str, n_results: int = 10):
        """语义搜索"""
        query_vector = self.get_embedding(f"{query}, 今日日期{date.today()}")
        results = collection.query(query_embeddings=[query_vector], n_results=n_results)

        # 安全隐患修复：如果数据库为空，results["documents"][0] 会报错 IndexError
        if not results.get("documents") or not results["documents"][0]:
            logger.warning("知识库中暂无相关资讯")
            return "知识库中暂无相关资讯"
        logger.info(f"搜索到 {len(results['documents'])} 条相关资讯")
        return "\n".join(results["documents"][0])

    def process_and_index_notice(self, notice: dict):
        """
        用来向量化并入库整条信息。
        此处接受的notice结构应为{"id":..., "title":..., "content_text":..., "date":...}
        原因是出于向量数据库、传统数据库以及json文件之间解耦的考量，
        此处写入向量数据库的数据是从传统数据库中读出的。
        """
        notice_id = notice["id"]  # 这里的 id 是 Rust 传来的链接哈希
        if self.check_notice_exists(notice_id):
            logger.info(f"资讯 [{notice['title']}] ({notice_id}) 内容未变，跳过。")
            return False
        # 此处按理因为id不是全文哈希，我们其实看不出内容有没有变，但是先这样了。
        date_str = notice["date"]
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        today = datetime.now()
        diff = today - date_obj
        if diff.days > MAX_DAY_DIFF:
            logger.info(f"资讯发布日期距今已有{MAX_DAY_DIFF}天，认作旧闻而跳过。")
            return False
        content = notice["content_text"]
        if content is None:
            logger.info(f"资讯[{notice['title']}]无正文信息，跳过")
            return False
        chunk_size = 500
        chunks = [
            content[i : i + chunk_size] for i in range(0, len(content), chunk_size)
        ]
        logger.info(f"开始处理并向量化新资讯 [{notice['title']}]...")
        for i, chunk in enumerate(chunks):
            chunk_id = f"{notice_id}_chunk_{i}"
            # 存入向量库
            self.add_chunk(
                chunk_id=chunk_id,
                content=chunk,
                metadata={"source_id": notice_id, "title": notice["title"]},
            )
        logger.info(f"资讯 [{notice['title']}] 入库完成。")
        return True


vector_db = VectorDBService()

if __name__ == "__main__":
    from app.crawler_wrapper import sync_vector_db

    sync_vector_db()
