# chat model for chat completion database

import uuid
from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from pydantic import Field
from typing import List

# Chat completion payload example
# {
#   "model": "gpt-4o",
#   "messages": [
#     {
#       "role": "system",
#       "content": "You are a travel assistant with expertise in creating personalized travel itineraries. Provide detailed, practical, and concise recommendations, including specific locations, activities, and tips based on the user's preferences. Always consider budget, travel dates, and any special requests."
#     },
#     {
#       "role": "user",
#       "content": "I'm planning a 5-day trip to Italy in June 2025 with a moderate budget. I love history, food, and scenic views. Where should I go, and what should I do?"
#     },
#     {
#       "role": "assistant",
#       "content": "For a 5-day trip to Italy with a focus on history, food, and scenic views on a moderate budget, I recommend visiting Rome and Florence. Here's a suggested itinerary:\n\n**Day 1-3: Rome**\n- **Day 1**: Visit the Colosseum (book skip-the-line tickets online for ~€16) and Roman Forum for a dive into ancient history. Enjoy dinner at a trattoria in Trastevere, like Osteria da Zi Umberto (~€15-20 per person).\n- **Day 2**: Explore the Pantheon (free entry) and Vatican Museums (Sistine Chapel, ~€20). Take an evening stroll at Piazza Navona. Try gelato at Gelateria del Teatro (~€3).\n- **Day 3**: Visit the Capitoline Museums (€15) and take a scenic walk along the Tiber River. Enjoy carbonara at Roscioli (~€12).\n\n**Day 4-5: Florence**\n- **Day 4**: Take a morning train from Rome to Florence (~€30, 1.5 hours). Visit the Uffizi Gallery (book ahead, ~€20) and stroll Ponte Vecchio for views. Dine at Trattoria Mario for affordable Tuscan dishes (~€10-15).\n- **Day 5**: Explore the Florence Cathedral (Duomo, free entry; dome climb ~€20) and enjoy views from Piazzale Michelangelo (free). Try a lampredotto sandwich at a local food stall (~€5).\n\n**Tips**: Book accommodations like budget hotels or Airbnb (~€60-100/night). Use regional trains for cost savings. June weather is warm, so pack light clothing and book tickets early to avoid crowds."
#     },
#     {
#       "role": "user",
#       "content": "That sounds great! Can you suggest a specific hotel in Rome and any food markets to visit in Florence?"
#     },
#     {
#       "role": "assistant",
#       "content": "**Rome Hotel**: Consider **Hotel Artemide**, a centrally located 4-star hotel with rates around €80-100 per night on a moderate budget. It’s near Termini Station and within walking distance of major sites like the Trevi Fountain. Book directly for potential deals.\n\n**Florence Food Markets**:\n- **Mercato Centrale**: A vibrant indoor market with food stalls offering fresh pasta, pizza, and local cheeses. Try a plate of fresh tortellini (~€8) or focaccia. Open daily, great for lunch.\n- **Sant’Ambrogio Market**: Less touristy, with fresh produce and local specialties like porchetta sandwiches (~€5). It’s perfect for an authentic experience, located near Santa Croce. Open mornings until 2 PM.\n\n**Tip**: In Florence, pair market visits with a stop at a nearby café for espresso (~€1.50) to soak in the local vibe."
#     },
#     {
#       "role": "user",
#       "content": "What about transportation between cities and within Florence?"
#     },
#     {
#       "role": "assistant",
#       "content": "**Between Cities**: Take a high-speed train (Italo or Trenitalia) from Rome to Florence. Book in advance for tickets around €25-35 one-way (1.5 hours). Trains depart from Roma Termini and arrive at Firenze Santa Maria Novella. Check schedules on trenitalia.com or italo.it.\n\n**Within Florence**: Florence is compact and walkable, so you won’t need much public transport. For longer distances (e.g., to Piazzale Michelangelo), use ATAF buses (~€1.50 per ride, buy tickets at tabaccherie). Alternatively, rent a bike (~€10/day) for a scenic way to explore. Taxis are pricier (~€10-15 for short trips), so stick to walking or buses for budget travel.",
#        "plot": {
#            "data": {},
#            "layout": {}
#        }
#     }
#   ],
#   "temperature": 0.8,
#   "max_tokens": 500,
#   "top_p": 1.0,
#   "frequency_penalty": 0.2,
#   "presence_penalty": 0.1
#   "stream": false
# }


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    """
    A message in a chat completion.
    """
    message_id: str = Field(..., description="The unique identifier for the message", default_factory=lambda: str(uuid.uuid4()))
    role: MessageRole = Field(..., description="The role of the message sender", examples=[MessageRole.USER, MessageRole.ASSISTANT, MessageRole.SYSTEM])
    content: str = Field(..., description="The content of the message")
    timestamp: datetime = Field(default_factory=datetime.now, description="The timestamp of the message")


class ChatCompletion(BaseModel):
    """
    A chat completion.
    """
    completion_id: str = Field(..., description="The unique identifier for the chat completion", default_factory=lambda: str(uuid.uuid4()))

    # openai compatible fields
    model: str = Field(..., description="The model used for the chat completion", examples=["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"])
    messages: List[ChatMessage] = Field(..., description="The messages in the chat completion")

    # not implemented yet
    # temperature: float = Field(default=0.7,ge=0.0, le=1.0, description="What sampling temperature to use, between 0 and 1. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.")
    # max_tokens: int = Field(default=1000, ge=0, le=10000, description="The maximum number of tokens to generate in the chat completion.")
    # top_p: float = Field(default=1.0, ge=0.0, le=1.0, description="An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.")
    # frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0, description="Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.")
    # presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0, description="Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.")
    # n: int = Field(default=1, ge=1, le=10, description="How many chat completion choices to generate for each prompt.")
    
    stream: bool = Field(default=False, description="If set to true, the model response data will be streamed to the client as it is generated using [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format). See the [Streaming section below](/docs/api-reference/chat/streaming) for more information, along with the [streaming responses](/docs/guides/streaming-responses) guide for more information on how to handle the streaming events. ")


    # audit fields
    created_by: str = Field(..., description="The user who created the chat completion")
    created_date: datetime = Field(default_factory=datetime.now, description="The date and time the chat completion was created")
    last_updated_by: str = Field(..., description="The user who last updated the chat completion")
    last_updated_date: datetime = Field(default_factory=datetime.now, description="The date and time the chat completion was last updated")
    
    