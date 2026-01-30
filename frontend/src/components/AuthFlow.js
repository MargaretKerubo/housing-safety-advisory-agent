import React, { useState } from 'react';
import { Card, Tabs, Tab, Form, Button, Alert, Row, Col } from 'react-bootstrap';

const AuthFlow = ({ onLogin }) => {
  const [key, setKey] = useState('login');
  const [loginForm, setLoginForm] = useState({ email: '', password: '' });
  const [signupForm, setSignupForm] = useState({ name: '', email: '', emergency: '', password: '' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Mock user database stored in localStorage
  const getUsersDb = () => {
    const usersStr = localStorage.getItem('usersDb');
    return usersStr ? JSON.parse(usersStr) : {};
  };

  const setUsersDb = (users) => {
    localStorage.setItem('usersDb', JSON.stringify(users));
  };

  const handleLoginSubmit = (e) => {
    e.preventDefault();
    setError('');

    const usersDb = getUsersDb();
    const user = usersDb[loginForm.email];

    if (user) {
      // In a real app, you'd verify the password here
      onLogin({
        name: user.name,
        email: loginForm.email,
        emergency: user.emergency
      });
    } else {
      setError('Invalid email or password');
    }
  };

  const handleSignupSubmit = (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    const usersDb = getUsersDb();

    if (usersDb[signupForm.email]) {
      setError('Email already registered');
      return;
    }

    // Add user to database
    usersDb[signupForm.email] = {
      name: signupForm.name,
      emergency: signupForm.emergency
    };
    setUsersDb(usersDb);

    setSuccess('Account created successfully! Please go to the Login tab.');

    // Reset form
    setSignupForm({ name: '', email: '', emergency: '', password: '' });
  };

  return (
    <Card className="auth-card mx-auto shadow-lg" style={{ maxWidth: '500px' }}>
      <Card.Body className="p-4">
        <div className="text-center mb-4">
          <div className="feature-icon mx-auto mb-3">
            <i className="bi bi-person-circle"></i>
          </div>
          <Card.Title className="h3 fw-bold text-dark">
            {key === 'login' ? 'Welcome Back!' : 'Join Us Today!'}
          </Card.Title>
          <p className="text-muted">
            {key === 'login' ? 'Sign in to access your dashboard' : 'Create an account to get started'}
          </p>
        </div>

        <Tabs
          id="auth-tabs"
          activeKey={key}
          onSelect={(k) => setKey(k)}
          className="mb-4 nav-fill"
        >
          <Tab eventKey="login" title="Login" className="fade show active">
            <Form onSubmit={handleLoginSubmit}>
              {error && <Alert variant="danger" className="rounded-3">{error}</Alert>}

              <Form.Group className="mb-3" controlId="loginEmail">
                <Form.Label className="fw-semibold text-dark">Email Address</Form.Label>
                <Form.Control
                  type="email"
                  placeholder="Enter your email"
                  value={loginForm.email}
                  onChange={(e) => setLoginForm({...loginForm, email: e.target.value})}
                  className="rounded-2 py-2"
                  required
                />
              </Form.Group>

              <Form.Group className="mb-3" controlId="loginPassword">
                <Form.Label className="fw-semibold text-dark">Password</Form.Label>
                <Form.Control
                  type="password"
                  placeholder="Enter your password"
                  value={loginForm.password}
                  onChange={(e) => setLoginForm({...loginForm, password: e.target.value})}
                  className="rounded-2 py-2"
                  required
                />
              </Form.Group>

              <Button variant="primary" type="submit" className="w-100 py-2 rounded-2 fw-semibold">
                Sign In
              </Button>
            </Form>
          </Tab>

          <Tab eventKey="signup" title="Sign Up" className="fade show active">
            <Form onSubmit={handleSignupSubmit}>
              {error && <Alert variant="danger" className="rounded-3">{error}</Alert>}
              {success && <Alert variant="success" className="rounded-3">{success}</Alert>}

              <Row>
                <Col md={12}>
                  <Form.Group className="mb-3" controlId="signupName">
                    <Form.Label className="fw-semibold text-dark">Full Name</Form.Label>
                    <Form.Control
                      type="text"
                      placeholder="Enter your full name"
                      value={signupForm.name}
                      onChange={(e) => setSignupForm({...signupForm, name: e.target.value})}
                      className="rounded-2 py-2"
                      required
                    />
                  </Form.Group>
                </Col>
              </Row>

              <Form.Group className="mb-3" controlId="signupEmail">
                <Form.Label className="fw-semibold text-dark">Email Address</Form.Label>
                <Form.Control
                  type="email"
                  placeholder="Enter your email"
                  value={signupForm.email}
                  onChange={(e) => setSignupForm({...signupForm, email: e.target.value})}
                  className="rounded-2 py-2"
                  required
                />
              </Form.Group>

              <Form.Group className="mb-3" controlId="signupEmergency">
                <Form.Label className="fw-semibold text-dark">Emergency Contact</Form.Label>
                <Form.Control
                  type="text"
                  placeholder="Emergency contact name and phone"
                  value={signupForm.emergency}
                  onChange={(e) => setSignupForm({...signupForm, emergency: e.target.value})}
                  className="rounded-2 py-2"
                />
              </Form.Group>

              <Form.Group className="mb-3" controlId="signupPassword">
                <Form.Label className="fw-semibold text-dark">Password</Form.Label>
                <Form.Control
                  type="password"
                  placeholder="Create a password"
                  value={signupForm.password}
                  onChange={(e) => setSignupForm({...signupForm, password: e.target.value})}
                  className="rounded-2 py-2"
                  required
                />
              </Form.Group>

              <Button variant="primary" type="submit" className="w-100 py-2 rounded-2 fw-semibold">
                Create Account
              </Button>
            </Form>
          </Tab>
        </Tabs>

        <div className="text-center mt-4">
          <p className="text-muted small">
            By signing up, you agree to our <a href="#terms">Terms of Service</a> and <a href="#privacy">Privacy Policy</a>
          </p>
        </div>
      </Card.Body>
    </Card>
  );
};

export default AuthFlow;