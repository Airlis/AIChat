import React from 'react';
import { Form, Input, Button, Card } from 'antd';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { submitUrl } from '../redux/slices/appSlice';

const UrlInputForm = () => {
  const [form] = Form.useForm();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { loading, error } = useSelector((state) => state.app);

  const onFinish = (values) => {
    dispatch(submitUrl(values.url))
      .unwrap()
      .then(() => {
        navigate('/chat');
      })
      .catch((err) => {
        console.error('Failed to submit URL:', err);
      });
  };

  return (
    <Card style={{ maxWidth: 600, margin: '50px auto' }}>
      <Form form={form} onFinish={onFinish} layout="vertical">
        <Form.Item
          name="url"
          label="Website URL"
          rules={[
            { required: true, message: 'Please enter a website URL' },
            { type: 'url', message: 'Please enter a valid URL' },
          ]}
        >
          <Input placeholder="Enter website URL" />
        </Form.Item>
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading}>
            Generate Questions
          </Button>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default UrlInputForm;
