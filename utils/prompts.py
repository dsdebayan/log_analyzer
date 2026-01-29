from langchain_core.prompts import ChatPromptTemplate

prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", """You are an log analyzer that analyzes, summarizes, explains log events and suggests resolution.
                Add emoji based on reoccurrence of the event.
                Limit your response to concise sentences. Here is the context: 
                {context}

            """),
                ("human", "{input}")
            ]
        )
