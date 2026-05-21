import psycopg2
from psycopg2 import extras
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Database configuration - Best practice is to use environment variables
DB_CONFIG = {
    "host": "ep-sparkling-unit-adoazjll-pooler.c-2.us-east-1.aws.neon.tech",
    "database": "neondb",
    "user": "neondb_owner",
    "password": "npg_u2RvzLXweK9l"
}

def insert_ocr_with_chunks(file_path, issuer_name, doc_type):
    """
    Reads OCR text, breaks it into overlapping chunks, and inserts into Postgres.
    """
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # 1. Ensure Issuer exists
        cur.execute("INSERT INTO issuers (name) VALUES (%s) ON CONFLICT (name) DO NOTHING;", (issuer_name,))
        cur.execute("SELECT issuer_id FROM issuers WHERE name = %s;", (issuer_name,))
        issuer_id = cur.fetchone()[0]

        # 2. Register the Document
        file_name = os.path.basename(file_path)
        cur.execute("""
            INSERT INTO documents (issuer_id, doc_type, file_name)
            VALUES (%s, %s, %s) RETURNING doc_id;
        """, (issuer_id, doc_type, file_name))
        doc_id = cur.fetchone()[0]

        # 3. Read and Chunk the Text
        with open(file_path, 'r', encoding='utf-8') as f:
            full_text = f.read()

        # Split logic: paragraph -> sentence -> characters
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = text_splitter.split_text(full_text)

        # 4. Prepare data for bulk insert
        data_to_insert = [
            (doc_id, chunk, extras.Json({"chunk_index": i, "total": len(chunks)}))
            for i, chunk in enumerate(chunks)
        ]

        # 5. Bulk Insert for high performance
        extras.execute_values(cur, """
            INSERT INTO document_sections (doc_id, content, metadata)
            VALUES %s
        """, data_to_insert)

        conn.commit()
        print(f"   Successfully indexed {len(chunks)} chunks for {issuer_name}")

    except Exception as e:
        print(f"   Error in db_ingestion: {e}")
        if conn: conn.rollback()
    finally:
        if conn: conn.close()