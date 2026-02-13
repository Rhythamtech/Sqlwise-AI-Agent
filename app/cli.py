import json
import sqlglot.errors
from sqlglot import exp
from src.db import SQLDB
from utils import convert_json_to_toon  
from sqlglot import parse_one
from src.llm import SQLAgent, DataAnalystAgent, QueryGeneratorAgent, QueryValidatorAgent
from src.rag import RAGPipeline


def pretty_print_json(data):
    if isinstance(data, list):
        data = [obj.dict() if hasattr(obj, 'dict') else obj for obj in data]
    elif hasattr(data, 'dict'):
        data = data.dict()
    
    print(json.dumps(data, indent=4, default=str, sort_keys=True))

def main():
    rag = RAGPipeline()
    db = SQLDB()
    q = "can you pull the net revenue from the last 30 days just for returning customers? Focus on primary products only, skip any orders that got fully refunded, show it in INR, and rank the top 3 by revenue?"

    # 1. DB Context
    db_context = rag.query_qna_index(q, "db")
    toon_db_context = convert_json_to_toon(db_context)
    
    # 2. Business Context
    business_query = QueryGeneratorAgent().generate_query(q, str(toon_db_context))
    business_context = rag.query_qna_index(business_query, "business_logic",k=2)
    toon_business_context = convert_json_to_toon(business_context)
    
    # 3. QnA Context
    qna_query = QueryGeneratorAgent().generate_query(q, str(toon_db_context + toon_business_context))
    qna_context =  rag.query_qna_index(qna_query, "qna")
    toon_qna_context = convert_json_to_toon(qna_context)

    context = toon_db_context + toon_business_context + toon_qna_context

    response = SQLAgent().sql_agent(question= "Question: "+q + "\n\nContext: "+str(context))
  
    if hasattr(response, 'query'):
        sql_error = None
        try:
            sqlglot.transpile(read='tsql', write='tsql', sql=response.query.replace('\n', ' '))
        except sqlglot.errors.ParseError as e:
            sql_error = e.errors

        print("SQL Error: ", sql_error)

        response = QueryValidatorAgent().validate_query( "Question: "+q + "\n SQL Error: "+str(sql_error), response.query)
        
        # print("\n 🚀 GENERATED SQL QUERY:")
        print(response.query)

        # parsed_query = parse_one(response.query,read="tsql")
        # tables = [t.name for t in parsed_query.find_all(exp.Table)]
        # print("Tables: ", tables)

        data = db.query_db(response.query)
        print("\n" + "═"*60)
        print(" 📊  DATABASE RESULTS")
        print("═"*60)
        pretty_print_json(data)
        print("═"*60 + "\n")
    
        print(" 🤖  LLM ANALYSIS")
        analysis = DataAnalystAgent().data_analyst(q, data)
        print("\n", analysis.content)

if __name__ == "__main__":
    main()