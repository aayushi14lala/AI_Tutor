from openai import OpenAI
import time

def send_query_get_response(client, user_question, assistant_id, include_similarity_search=True):
    try:
        # Create a new thread
        thread = client.beta.threads.create()
        thread_id = thread.id

        # Optionally modify the query for similarity search
        if include_similarity_search:
            user_question += (' and tell me which file are the top results based on your similarity search '
                              '(an example can be: you can refer to the course material titled '
                              '"Present Value Relations" in the file "Lec 2-3.pdf" under slides 20-34.)')

        # Send the user's question
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_question,
        )

        # Create and start the run
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
        )

        # Initialize timer
        start_time = time.time()
        timeout = 60  # seconds
        interval = 2  # seconds (to avoid excessive API calls)

        # Wait for completion
        while True:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            
            if run.status == 'completed':
                break
            elif time.time() - start_time > timeout:
                print("Timeout: The response took too long.")
                return "Server response timeout. Please try again later."
            
            time.sleep(interval)

        # Fetch messages (ensure messages exist)
        messages = client.beta.threads.messages.list(thread_id=thread_id, order='asc')
        if not messages.data:
            return "Server issue, try again."

        # Extract response safely
        last_message = messages.data[-1]
        if hasattr(last_message, 'content') and last_message.content:
            response = last_message.content[0].text.value
            return response

        return "Unexpected response format. Please try again."
    
    except Exception as e:
        return f"Error occurred: {str(e)}"
