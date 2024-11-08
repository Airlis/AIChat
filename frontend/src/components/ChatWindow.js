import React from 'react';
import { ChatList } from 'react-chat-elements';
import 'react-chat-elements/dist/main.css';

const ChatWindow = ({ messages }) => {
  return (
    <ChatList className="chat-list" dataSource={messages} />
  );
};

export default ChatWindow;
