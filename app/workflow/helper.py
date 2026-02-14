import json
import sqlglot
import sqlglot.errors

def extract_few_shot_examples(qna_results: list, max_examples: int = 3) -> str:
    """
    Pull Q→SQL examples from QnA retrieval results.
    The QnA knowledge base documents contain 'sql_query' in their page_content.
    """
    examples = []
    for doc in qna_results:
        content = doc.get("page_content", "")
        # Parse the stringified dict back if needed
        try:
            parsed = eval(content) if isinstance(content, str) and content.startswith("{") else {}
        except Exception:
            parsed = {}

        sql = parsed.get("sql_query", "")
        question = parsed.get("question", "")
        if sql and question:
            examples.append(f"Q: {question}\nSQL: {sql}")

        if len(examples) >= max_examples:
            break

    if not examples:
        return ""

    header = "\n\n## Few-Shot Examples (similar past queries):\n"
    return header + "\n\n".join(examples)


def check_sql_syntax(sql: str) -> str | None:
    """Run sqlglot syntax check. Returns error string or None if clean."""
    try:
        sqlglot.transpile(sql=sql.replace("\n", " "), read="tsql", write="tsql")
        return None
    except sqlglot.errors.ParseError as e:
        return str(e.errors)

def format_json_results(data):
    """Format dicts/lists for display or further processing."""
    if isinstance(data, list):
        data = [obj.dict() if hasattr(obj, "dict") else obj for obj in data]
    elif hasattr(data, "dict"):
        data = data.dict()
    return data
