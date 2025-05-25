from app.agent.chat_agent_scheme import UserChatAgentRequest, AssistantChatAgentResponse


class ChatAgentClient:
    def __init__(self):
        self.agent_name = "ChatAgentClient"

    def process(self, user_chat_agent_request: UserChatAgentRequest) -> AssistantChatAgentResponse:
        # TODO implement the logic to process the chat
        agent_name = self.agent_name
        return AssistantChatAgentResponse(
            message=f"Here is the {agent_name} Processed message: This is a placeholder response for the user-question",
            figure=None,  # Placeholder for any figure data if needed
        )
