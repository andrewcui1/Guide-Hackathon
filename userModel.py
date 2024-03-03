class User:
    def __init__(self, phoneNumber, threadID, createdTimeStamp, messageHistory):
        self.phoneNumber = phoneNumber
        self.threadID = threadID
        self.createdTimeStamp = createdTimeStamp
        self.messageHistory = messageHistory
        

class Message:
    def __init__(self, sender, receiver, content, createdTimeStamp):
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.createdTimeStamp = createdTimeStamp
