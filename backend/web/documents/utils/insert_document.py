import lancedb
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import LanceDB
from langchain_text_splitters import  RecursiveCharacterTextSplitter


from web.documents.utils.custom_embeddings import CustomEmbeddings


def insert_documents():
    # 1 读取文档
    loader = TextLoader('./web/documents/data.txt',encoding='utf-8')
    documents = loader.load()
    # 2 文档切分
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=50)
    texts = text_splitter.split_documents(documents)
    print(f"切分成{len(texts)}个片段")
    # 3 embedding
    embeddings = CustomEmbeddings()
    # 4 连接 LanceDB
    db = lancedb.connect('./web/documents/lancedb_storage')
    # 5 写入向量数据库
    vector_db = LanceDB.from_documents(
        documents = texts,
        embedding = embeddings,
        connection = db,
        table_name = 'my_knowledge_base',
        mode="overwrite",
    )
    print(f"已插入{vector_db._table.count_rows()}行数据")
