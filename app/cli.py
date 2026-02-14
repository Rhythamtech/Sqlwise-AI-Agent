import time
from workflow.pipeline import (
    rewrite_user_query,
    retrieve_context_parallel,
    prepare_context_and_examples,
    create_sql_plan,
    generate_sql_query,
    validate_generated_sql,
    execute_and_heal_sql,
    analyze_sql_results
)
from src.rag import RAGPipeline
from src.db import SQLDB
from workflow.helper import format_json_results

def run_pipeline_orchestrator(question: str):
    """
    Main Pipeline Orchestration using a generator for status updates.
    Yields dicts with 'status' and optionally 'data' or 'error'.
    """
    rag = RAGPipeline()
    db = SQLDB()
    
    yield {"status": "Starting pipeline...", "step": 0}
    
    # Step 1: Rewrite
    yield {"status": "Rewriting query...", "step": 1}
    rewritten_q = rewrite_user_query(question)
    
    # Step 2: Parallel RAG
    yield {"status": "Retrieving context and examples...", "step": 2}
    retrieval_results = retrieve_context_parallel(rewritten_q, rag)
    
    # Step 3: Context Assembly
    yield {"status": "Assembling context...", "step": 3}
    context, few_shots = prepare_context_and_examples(retrieval_results)
    
    # Step 4: Query Planning
    yield {"status": "Creating SQL plan...", "step": 4}
    plan = create_sql_plan(question, context)
    
    # Step 5: SQL Generation
    yield {"status": "Generating SQL query...", "step": 5}
    sql_response = generate_sql_query(question, context, few_shots, plan)
    
    # Step 6: Smart Validation
    yield {"status": "Validating SQL...", "step": 6}
    validated_response = validate_generated_sql(question, sql_response, context)
    
    if hasattr(validated_response, "query"):
        yield {"status": "SQL generated successfully", "sql": validated_response.query}
    
    # Step 7: Execution & Healing
    yield {"status": "Executing SQL engine...", "step": 7}
    data, error = execute_and_heal_sql(question, validated_response, db, context)
    
    if error:
        yield {"status": "Pipeline failed", "error": error}
        return

    yield {"status": "Data retrieved successfully", "data": format_json_results(data)}
    
    # Step 8: Data Analysis
    yield {"status": "Analyzing results...", "step": 8}
    analysis = analyze_sql_results(question, data)
    
    yield {"status": "Pipeline completed", "analysis": analysis.content}

if __name__ == "__main__":
    import json
    
    user_question = input("\n 💬 Enter your question: ").strip()
    if not user_question:
        user_question = "What is the total generated revenue (USD) from all order items weekwise? And Give me statergy to improve the revenue."
    
    print("\n🚀 Executing Agent Workflow...\n")
    
    for update in run_pipeline_orchestrator(user_question):
        status = update.get("status")
        if "sql" in update:
            print(f"🔍 SQL: {update['sql']}\n")
        elif "data" in update:
            print(f"📊 DATA: {json.dumps(str(update['data']), indent=2)}\n")
        elif "analysis" in update:
            print(f"🤖 ANALYSIS: {update['analysis']}\n")
        elif "error" in update:
            print(f"❌ ERROR: {update['error']}\n")
        else:
            print(f"⚙️ {status}")
