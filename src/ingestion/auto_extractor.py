import os
import json
import psycopg2
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Configuration
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('models/gemini-2.5-flash')

DB_CONFIG = {
    "host": "ep-sparkling-unit-adoazjll-pooler.c-2.us-east-1.aws.neon.tech",
    "database": "neondb",
    "user": "neondb_owner",
    "password": "npg_u2RvzLXweK9l"
}

def run_auto_extraction(issuer_name):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # 2. Retrieve the most relevant chunks for Varthana
    # We look for keywords like 'Ratio', 'Covenant', 'Leverage'
    # 2. Advanced Retrieval Logic
    # We increase the limit to 60 chunks and look for "Table-like" keywords
    cur.execute("""
        SELECT content FROM document_sections 
        JOIN documents ON document_sections.doc_id = documents.doc_id
        JOIN issuers ON documents.issuer_id = issuers.issuer_id
        WHERE issuers.name = %s 
        AND (
            content ILIKE '%%ratio%%' 
            OR content ILIKE '%%covenant%%' 
            OR content ILIKE '%%financial%%'
            OR content ILIKE '%%key indicators%%'
            OR content ILIKE '%%capital adequacy ratio%%'
            OR content ILIKE '%%leverage%%'
            OR content ILIKE '%%gearing%%'
            OR content ILIKE '%%asset quality%%'
            OR content ILIKE '%%adequacy%%'
        )
        ORDER BY section_id ASC  
        LIMIT 120;
    """, (issuer_name,))
    
    chunks = [row[0] for row in cur.fetchall()]
    context = "\n---\n".join(chunks)

    # 3. Enhanced Prompt (Adding "Gearing" which is a common term for Leverage in India)
    # prompt = f"""
    # Act as a Senior Credit Analyst. Extract these exact metrics from the text snippets for {issuer_name}.
    # If a value is not explicitly stated, look for synonyms (e.g., 'Gearing' for 'Leverage' or 'CRAR' for 'Capital Adequacy').
    
    # Return ONLY a valid JSON object:
    # {{
    #   "metrics": [
    #     {{"parameter": "Capital Adequacy", "value": "VALUE", "limit": "LIMIT", "status": "Compliant/Breached"}},
    #     {{"parameter": "Leverage Ratio", "value": "VALUE", "limit": "LIMIT", "status": "Compliant/Breached"}},
    #     {{"parameter": "Net Stage 3", "value": "VALUE", "limit": "LIMIT", "status": "Compliant/Breached"}},
    #     {{"parameter": "Security Cover", "value": "VALUE", "limit": "LIMIT", "status": "Compliant/Breached"}}
    #   ]
    # }}

    # TEXT SNIPPETS:
    # {context}
    # """

    prompt = f"""
    ROLE: You are a Senior Credit Risk Analyst at a Global Investment Bank.
    
    TASK: Analyze the provided [TEXT SNIPPETS] to extract 4 key financial pillars for {issuer_name}.
    
    [TEXT SNIPPETS]:
    {context}

    EXTRACTION RULES:
    1. CAPITAL ADEQUACY: Look for 'CRAR', 'Capital Adequacy', or 'Tier 1'. Usually a %. 
       (Target Covenant Limit is typically 15%).
    2. LEVERAGE: Look for 'Gearing', 'Debt to Equity', or 'Debt/TNW'. Usually a multiplier (e.g. 3.5x).
       (Target Covenant Limit is typically 4.0x or 5.0x).
    3. ASSET QUALITY: Look for 'Net Stage 3', 'Net NPA', or 'PAR 90'. Usually a %.
       (Target Covenant Limit is typically 1% or 2%).
    4. SECURITY COVER: Look for 'Asset Cover', 'Collateral Cover', or 'Security Multiplier'. Usually a multiplier (e.g. 1.1x).

    LOGIC FOR 'STATUS' COLUMN:
    - If Actual is safer than the Limit (e.g., Leverage 3x < 4x Limit) -> "Compliant"
    - If Actual is worse than the Limit (e.g., Leverage 4.5x > 4x Limit) -> "Breached"
    - If the Limit is not in the text, use industry standards (15% for CRAR, 4.0x for Leverage) and mark Status.

    OUTPUT FORMAT: Return ONLY a valid JSON object. 
    {{
      "metrics": [
        {{
          "parameter": "Capital Adequacy",
          "value": "28.53%",
          "limit": "15.00%",
          "status": "Compliant"
        }},
        ... (repeat for all 4)
      ]
    }}
    """
    # How temperature is set in the code:
    generation_config = genai.types.GenerationConfig(
    temperature=0.0,  # Absolute zero for maximum factual precision
    response_mime_type="application/json", # Forces strict JSON format
    )
    response = model.generate_content(prompt, generation_config=generation_config)
    # 4. Generate and Parse
    # response = model.generate_content(prompt)
    # Clean the response to ensure it's pure JSON
    json_data = response.text.replace('```json', '').replace('```', '').strip()
    extracted = json.loads(json_data)

    # 5. Insert into financial_metrics table
    cur.execute("SELECT issuer_id FROM issuers WHERE name = %s;", (issuer_name,))
    issuer_id = cur.fetchone()[0]

    for item in extracted['metrics']:
        cur.execute("""
            INSERT INTO financial_metrics (issuer_id, parameter_name, raw_value, covenant_limit, status)
            VALUES (%s, %s, %s, %s, %s);
        """, (issuer_id, item['parameter'], item['value'], item['limit'], item['status']))

    conn.commit()
    print(f"✅ Success! Extracted {len(extracted['metrics'])} parameters for {issuer_name}")
    cur.close()
    conn.close()

if __name__ == "__main__":
    run_auto_extraction("Varthana")