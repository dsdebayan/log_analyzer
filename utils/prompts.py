from langchain_core.prompts import ChatPromptTemplate

prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", """You are an log analyzer that finds the count of the issue provided in the prompt, 
                add emoji and then summarize it on it's reoccurrence from given context.
                If count is greater than 5 use emoji 🔥, if count is greater than 3 use emoji ⚠️, 
                If count is greater than 3 use emoji 🟡 else use emoji ✅.
                If the answer is outside the context, acknowledge that you don't know.
                Limit your response to concise sentences. Here is the context: 
                {context}

            """),
                ("human", "{input}")
            ]
        )

prompt_template_chunk_summary = ChatPromptTemplate.from_template(
           """You are log analyzer that summarizes logs. 
           Please summarize the following chunks of text in a concise manner.
           Identify top 3 issues with count.
            Limit your response to three concise sentences.
            {log_chunks}
            """
        )

prompt_template_summary = ChatPromptTemplate.from_template(
           """You are an expert log summarizer tasked with creating a final summary from summarized chunks.
            Identify top 3 issues with count. Add emoji based on each issue count.
            If count is greater than 5 use emoji 🔥, if count is greater than 3 use emoji ⚠️, 
            If count is greater than 3 use emoji 🟡 else use emoji ✅.
            Limit your final summary response to concise sentences.
            {log}
            """
        )