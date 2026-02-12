import json
import logging
from src.db import SQLDB
from src.llm import SQLAgent, DataAnalystAgent, QueryGeneratorAgent
from src.rag import RAGPipeline

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def pretty_print_json(data):
    if isinstance(data, list):
        data = [obj.dict() if hasattr(obj, 'dict') else obj for obj in data]
    elif hasattr(data, 'dict'):
        data = data.dict()
    
    logger.info(json.dumps(data, indent=4, default=str, sort_keys=True))

def main():
    db = SQLDB()
    q = "What strategy should i use to boost the attention and reduce the refunds?"
    
    # 1. DB Context
    db_context = RAGPipeline().query_qna_index(q, "db")
    
    # 2. Business Context
    business_query = QueryGeneratorAgent().generate_query(q, str(db_context))
    business_context = RAGPipeline().query_qna_index(business_query, "business_logic")
    
    # 3. QnA Context
    qna_query = QueryGeneratorAgent().generate_query(q, str(db_context + business_context))
    qna_context = RAGPipeline().query_qna_index(qna_query, "qna")
    
    context = db_context + business_context + qna_context

    logger.info("\n" + "═"*60)
    logger.info(" 🔍  ANALYSING THE USER QUERY")
    logger.info("═"*60)
    pretty_print_json(context)
    logger.info("═"*60 + "\n")

    response = SQLAgent().sql_agent(question=q + "\n\n" + str(context))
  
    if hasattr(response, 'query'):

        print("\n\n\n",response.query)
        data = db.query_db(response.query)
        logger.info(" 📊  DATABASE RESULTS")
        pretty_print_json(data)
    
        logger.info(" 🤖  LLM ANALYSIS")
        analysis = DataAnalystAgent().data_analyst(q, data)
        logger.info(analysis.content)

if __name__ == "__main__":
    main()