import React from 'react';
import { Layout } from 'antd';
import UrlInput from './components/UrlInput';
import ChatBox from './components/ChatBox';

const { Header, Content } = Layout;

const App = () => {
  return (
    <Layout>
      <Header style={{ color: 'white', textAlign: 'center' }}>
        <h1>Visitor AI Classification</h1>
      </Header>
      <Content style={{ padding: '20px', minHeight: '100vh' }}>
        <UrlInput />
        <ChatBox />
      </Content>
    </Layout>
  );
};

export default App;
