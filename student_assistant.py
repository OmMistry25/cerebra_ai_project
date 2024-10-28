from langchain.agents import initialize_agent
from langchain_cerebras import ChatCerebras
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

# =====================================
# Future Platform API Integrations
# =====================================

"""
# Canvas LMS API Integration
class CanvasAPI:
    def __init__(self):
        self.api_key = os.getenv('CANVAS_API_KEY')
        self.base_url = os.getenv('CANVAS_API_URL')
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_assignments(self):
        response = requests.get(
            f"{self.base_url}/api/v1/courses/upcoming_assignments",
            headers=self.headers
        )
        return response.json()

# Gradescope API Integration
class GradescopeAPI:
    def __init__(self):
        self.client_id = os.getenv('GRADESCOPE_CLIENT_ID')
        self.client_secret = os.getenv('GRADESCOPE_CLIENT_SECRET')
        
    def get_assignments(self):
        # Implementation for getting Gradescope assignments
        pass

# PrairieLearn API Integration
class PrairieLearnAPI:
    def __init__(self):
        self.api_token = os.getenv('PRAIRIELEARN_API_TOKEN')
        
    def get_assignments(self):
        # Implementation for getting PrairieLearn assignments
        pass

# Calendar Integration
class CalendarAPI:
    def __init__(self):
        self.google_creds = os.getenv('GOOGLE_CALENDAR_CREDS')
        self.outlook_creds = os.getenv('OUTLOOK_CREDS')
        
    def get_events(self):
        # Implementation for getting calendar events
        pass
"""

# =====================================
# Sample Data for POC
# =====================================
from cerebras.cloud.sdk import Cerebras
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

# Sample data for POC
SAMPLE_DATA = {
    "assignments": [
        {"name": "CS101 Homework", "due_date": "2024-10-30", "course": "CS101", "platform": "Canvas"},
        {"name": "Math Quiz", "due_date": "2024-10-29", "course": "MATH201", "platform": "Gradescope"},
        {"name": "Programming Lab", "due_date": "2024-11-01", "course": "CS101", "platform": "PrairieLearn"}
    ],
    "schedule": [
        {"name": "CS101 Lecture", "time": "10:00 AM", "location": "Room 101", "type": "class"},
        {"name": "MATH201", "time": "2:00 PM", "location": "Room 203", "type": "class"},
        {"name": "CS101 Office Hours", "time": "3:30 PM", "location": "Room 105", "type": "office_hours"}
    ]
}

class StudentAssistant:
    def __init__(self):
        self.client = Cerebras(api_key=os.environ.get("CEREBRAS_API_KEY"))
        self.system_prompt = """You are a helpful student assistant that helps students manage their academic schedule and assignments. 
        You can access information about their classes, assignments, and schedules.
        Always provide clear, concise responses focusing on the specific information requested."""
        
    def get_data_context(self, query: str) -> str:
        """Get relevant data based on the query"""
        context = []
        
        # Add assignments if query seems assignment-related
        if any(word in query.lower() for word in ["assignment", "homework", "due", "deadline", "submit"]):
            context.append("Assignments:")
            for assignment in SAMPLE_DATA["assignments"]:
                context.append(
                    f"- {assignment['name']} ({assignment['course']}) due {assignment['due_date']} on {assignment['platform']}"
                )
        
        # Add schedule if query seems schedule-related
        if any(word in query.lower() for word in ["class", "schedule", "lecture", "where", "when", "next"]):
            context.append("\nSchedule:")
            for event in SAMPLE_DATA["schedule"]:
                context.append(
                    f"- {event['name']} at {event['time']} in {event['location']}"
                )
        
        return "\n".join(context)

    def process_query(self, user_query: str, stream: bool = True) -> str:
        # Get relevant context
        context = self.get_data_context(user_query)
        
        # Prepare messages
        messages = [
            {
                "role": "system",
                "content": self.system_prompt
            },
            {
                "role": "user",
                "content": f"Based on this information:\n{context}\n\nUser question: {user_query}"
            }
        ]
        
        # Create completion
        response = self.client.chat.completions.create(
            messages=messages,
            model="llama3.1-70b",  # Using 70B model for better comprehension
            stream=stream,
            max_completion_tokens=1024,
            temperature=0.2,  # Lower temperature for more focused responses
            top_p=1
        )
        
        if stream:
            print("Assistant: ", end="")
            for chunk in response:
                content = chunk.choices[0].delta.content or ""
                print(content, end="", flush=True)
            print()  # New line after streaming completes
            return ""
        else:
            return response.choices[0].message.content

def main():
    print("Initializing Student Assistant POC...")
    assistant = StudentAssistant()
    
    # Sample queries to demonstrate functionality
    demo_queries = [
        "What assignments do I need to submit this week?",
        "What's my schedule for today?",
        "Where is my CS101 Lecture?",
        "Do I have any CS101 assignments due?",
        "When are the next office hours?",
    ]
    
    print("\nRunning demo queries to showcase functionality...\n")
    for query in demo_queries:
        print(f"\nQuery: {query}")
        assistant.process_query(query)
        print()  # Add spacing between queries
    
    print("\nEntering interactive mode (type 'exit' to quit)")
    while True:
        user_input = input("\nWhat would you like to know? ")
        if user_input.lower() == 'exit':
            break
        try:
            assistant.process_query(user_input)
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()