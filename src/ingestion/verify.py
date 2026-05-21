import psycopg2

DB_CONFIG ={
    "host": "ep-sparkling-unit-adoazjll-pooler.c-2.us-east-1.aws.neon.tech",
    "database": "neondb",
    "user": "neondb_owner",
    "password": "npg_u2RvzLXweK9l"
}

def verify_data_retrieval(keyword):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Search for chunks containing specific risk keywords
    query = f"%{keyword}%"
    cur.execute("""
        SELECT content, metadata FROM document_sections 
        WHERE content ILIKE %s LIMIT 3;
    """, (query,))
    
    results = cur.fetchall()
    print(f"\n--- Top 3 Results for '{keyword}' ---")
    for i, (content, meta) in enumerate(results):
        print(f"\n[{i+1}] Source Chunk {meta.get('chunk_index')}:")
        print(f"{content[:200]}...") # Print first 200 chars for verification
    
    cur.close()
    conn.close()

# Test it with a core parameter from your CSV
verify_data_retrieval("Leverage")