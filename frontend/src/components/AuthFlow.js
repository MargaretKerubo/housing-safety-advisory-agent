import React, { useState } from 'react';
import { Card, Tabs, Tab, Form, Button, Alert, Spinner } from 'react-bootstrap';
import apiService from '../utils/apiService';

const AuthFlow = ({ onLogin }) => {
  const [key, setKey] = useState('login');
  const [loginForm, setLoginForm] = useState({ email: '', password: '' });
  const [signupForm, setSignupForm] = useState({ name: '', email: '', emergency: '', password: '' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const email = loginForm.email.trim();
    const password = loginForm.password;

    if (!email || !password) {
      setError('Please fill in all fields');
      setLoading(false);
      return;
    }

    try {
      const result = await apiService.login({ email, password });
      onLogin(result.user);
    } catch (err) {
      setError(typeof err === 'string' ? err : err.detail || 'Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  const handleSignupSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    const name = signupForm.name.trim();
    const email = signupForm.email.trim();
    const password = signupForm.password;
    const emergency = signupForm.emergency.trim();

    // Basic Validation
    if (!name || !email || !password) {
      setError('Name, Email and Password are required');
      setLoading(false);
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters long');
      setLoading(false);
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError('Please enter a valid email address');
      setLoading(false);
      return;
    }

    try {
      const result = await apiService.register({
        name,
        email,
        password,
        emergency_contact: emergency
      });
      
      setSuccess('Account created successfully!');
      
      // Small delay to show success then login
      setTimeout(() => {
        onLogin(result.user);
      }, 1000);
    } catch (err) {
      setError(typeof err === 'string' ? err : err.detail || 'Registration failed. Email might already be in use.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="auth-card mx-auto shadow-lg" style={{ maxWidth: '500px' }}>
      <Card.Body className="p-4">
        <div className="text-center mb-4">
          <div className="feature-icon mx-auto mb-3">
            <i className="bi bi-house-heart-fill"></i>
          </div>
          <Card.Title className="h2 fw-bold text-dark mb-2">
            {key === 'login' ? 'Welcome Back!' : 'Join Our Community!'}
          </Card.Title>
          <p className="text-muted fs-6">
            {key === 'login' ? 'Sign in to access your personalized housing advisor' : 'Create your account to find your perfect home'}
          </p>
        </div>

        <Tabs
          id="auth-tabs"
          activeKey={key}
          onSelect={(k) => {
            setKey(k);
            setError('');
            setSuccess('');
          }}
          className="mb-4 nav-fill custom-tabs"
          variant="pills"
        >
          <Tab eventKey="login" title="Login">
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

              <Button variant="primary" type="submit" disabled={loading} className="w-100 py-3 rounded-3 fw-bold fs-5 btn-gradient">
                {loading ? (
                  <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" />
                ) : (
                  <>
                    <i className="bi bi-box-arrow-in-right me-2"></i>
                    Sign In
                  </>
                )}
              </Button>
            </Form>
          </Tab>

          <Tab eventKey="signup" title="Sign Up">
            <Form onSubmit={handleSignupSubmit}>
              {error && <Alert variant="danger" className="rounded-3">{error}</Alert>}
              {success && <Alert variant="success" className="rounded-3">{success}</Alert>}

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

              <Button variant="primary" type="submit" disabled={loading} className="w-100 py-3 rounded-3 fw-bold fs-5 btn-gradient">
                {loading ? (
                  <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" />
                ) : (
                  <>
                    <i className="bi bi-person-plus-fill me-2"></i>
                    Create Account
                  </>
                )}
              </Button>
            </Form>
          </Tab>
        </Tabs>

        <div className="text-center mt-4 pt-3 border-top">
          <p className="text-muted small mb-0">
            By continuing, you agree to our <a href="#terms" className="text-decoration-none fw-semibold">Terms of Service</a> and <a href="#privacy" className="text-decoration-none fw-semibold">Privacy Policy</a>
          </p>
        </div>
      </Card.Body>
    </Card>
  );
};

export default AuthFlow;