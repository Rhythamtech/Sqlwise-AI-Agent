from langchain_core.prompts import ChatPromptTemplate

sql_schema = """
            CREATE TABLE metadata (
                [Table] nvarchar(25) NULL,
                [Field] varchar(60) NULL,
                [Description] varchar(128) NULL
            )

            CREATE TABLE orders (
                order_id int,
                created_at DATETIME,
                session_id int,
                user_id int,
                primary_product_id	int,
                items_purchased	int,
                price_usd float,
                price_inr float, -- Calculate via usd to inr
                cogs_usd float,
                cogs_inr float  -- Calculate via usd to inr
            )

            CREATE TABLE order_items (
                order_item_id int,
                order_id int,
                created_at DATETIME,
                product_id	int,
                is_primary_item int,    
                price_usd float,
                price_inr float, -- Calculate via usd to inr
                cogs_usd float,
                cogs_inr float  -- Calculate via usd to inr
            )

            CREATE TABLE products (
                product_id int,
                created_at DATETIME,
                product_name varchar(128) NULL
            )


            CREATE TABLE pageviews (
                pageview_id	int,
                created_at DATETIME,
                session_id	int,
                pageview_url nvarchar(256) NULL
            )


            CREATE TABLE sessions (
                session_id int,
                created_at	DATETIME,
                user_id	int ,
                is_repeat_session int,
                utm_source varchar(60) NULL,
                utm_campaign VARCHAR(128) NULL,
                utm_content	VARCHAR(128) NULL,
                device_type VARCHAR(60) NULL,
                http_referer NVARCHAR(128) NULL,
            ) 

            CREATE TABLE refunds (
                refund_id int,
                created_at DATETIME ,
                order_item_id int,
                order_id int,
                refund_amount_usd	float,
                refund_amount_inr	float, -- Calculate via usd to inr
            )
            """

sql_system_prompt = """
You are a expert senior data analyst having experience of 5+ years in SQL database.
Given an input question, create a syntactically correct SQL SERVER query to run.

## Rules
1. Unless the user specifies a specific number of examples they wish to obtain, always limit your
query to at most 10 relevant results.
2. Never query for all the columns from a specific table, only ask for the relevant columns given the question.
3. You MUST double check your query before resulting it as final query.
4. Do NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

## output format

{{
    "query": "SELECT * FROM table_name",
    "explanation": "Explanation of the query"
}}

"""

data_analyst_prompt = """
You are a expert senior data analyst having experience of 5+ years works with large scale data Analysis.
Based on the shared data, and question ask by business analyst, answer the question.

## Rules
1. You must double check your answer before resulting it as final answer.
2. Your response must be relevant to the question asked.
3. The shared data is correct and accurate. Write what you see in the data. Do a perfect analysis.
4. Need share your views analysis on the data, Provide best possible insights.
"""