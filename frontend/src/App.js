import React from 'react';
import { useSelector } from 'react-redux';
import { Layout } from 'antd';
import { Routes, Route } from 'react-router-dom';
import UrlInputForm from './components/UrlInputForm';
import Chatbot from './components/Chatbot';
import Results from './components/Results';
import './App.css'; // Import the CSS file

const { Header, Content } = Layout;

const App = () => {
  return (
    <Layout>
      <Header className="header">Visitor AI Classification</Header>
      <Content className="content">
        <Routes>
          <Route path="/" element={<UrlInputForm />} />
          <Route path="/chat" element={<Chatbot />} />
          <Route path="/results" element={<Results />} />
        </Routes>
      </Content>
    </Layout>
  );
};

export default App;
