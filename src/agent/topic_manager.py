class TopicManager:
    def __init__(self):
        self.current_topic = None
        self.topic_keywords = set(['new project', 'different data', 'start over'])
    
    def is_new_topic(self, command: str) -> bool:
        """
        Detect if the command indicates a new topic
        """
        command_lower = command.lower()
        
        # Check for explicit topic change indicators
        for keyword in self.topic_keywords:
            if keyword in command_lower:
                return True
        
        # Add more sophisticated topic detection logic here
        return False 