import React from 'react';
import { Layout } from 'antd';
import UrlInput from './components/UrlInput';
import ChatBox from './components/ChatBox';
import './styles/App.css';

// The main application component that brings everything together.
const { Header, Content } = Layout;

const App = () => {
  return (
    <Layout className="app-layout">
      <Header className="header">
        <h1>Visitor AI Classification</h1>
      </Header>
      <Content className="content">
        <div className="main-content">
          <UrlInput />
          {/* Other content */}
        </div>
      </Content>
      <ChatBox />
    </Layout>
  );
};

export default App;