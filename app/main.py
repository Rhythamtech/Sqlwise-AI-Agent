from src.db import SQLDB
from src.llm import SQLAgent, DataAnalystAgent

def main():
    db = SQLDB()
    q = "list of most lovable product on site?"
    response = SQLAgent().sql_agent(q)
    print(response.query)

    data = db.query_db(response.query)
    print(data)

    response = DataAnalystAgent().data_analyst(q, data)
    print(response.content)


if __name__ == "__main__":
    main()
