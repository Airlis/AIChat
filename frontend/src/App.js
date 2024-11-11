import React from 'react';
import { Layout } from 'antd';
import UrlInput from './components/UrlInput';
import ChatBox from './components/ChatBox';
import LoadingOverlay from './components/Loading';
import { useSelector } from 'react-redux';
import './styles/App.css';

// The main application component that brings everything together.
const { Header, Content } = Layout;

const App = () => {
  const { loading } = useSelector((state) => state.chat);

  return (
    <Layout>
      <Header style={{ color: 'white', textAlign: 'center' }}>
        <h1>Visitor AI Classification</h1>
      </Header>
      <Content style={{ padding: '20px', minHeight: '100vh' }}>
        <UrlInput />
        <ChatBox />
        {loading && <LoadingOverlay />}
      </Content>
    </Layout>
  );
};

export default App;
