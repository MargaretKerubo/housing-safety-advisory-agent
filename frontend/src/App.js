import React, { useState, useEffect } from 'react';
import { Container, Navbar, Nav, Button, Tab, Row, Col } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import './styles/App.css';
import AuthFlow from './components/AuthFlow';
import MainApp from './components/MainApp';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);

  // Load session state from localStorage on component mount
  useEffect(() => {
    const loggedIn = localStorage.getItem('isLoggedIn');
    const user = localStorage.getItem('currentUser');

    if (loggedIn === 'true' && user) {
      setIsLoggedIn(true);
      setCurrentUser(JSON.parse(user));
    }
  }, []);

  const handleLogin = (userData) => {
    setIsLoggedIn(true);
    setCurrentUser(userData);
    localStorage.setItem('isLoggedIn', 'true');
    localStorage.setItem('currentUser', JSON.stringify(userData));
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setCurrentUser(null);
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('currentUser');
  };

  return (
    <div className="App">
      <Navbar bg="primary" variant="dark" expand="lg" className="shadow-sm">
        <Container>
          <Navbar.Brand href="#home" className="d-flex align-items-center">
            <i className="bi bi-house-door-fill me-2"></i>
            <span className="fw-bold fs-4">🏠 Smart Housing Advisor</span>
          </Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="ms-auto">
              {isLoggedIn && (
                <Nav.Item>
                  <Button
                    variant="outline-light"
                    onClick={handleLogout}
                    className="d-flex align-items-center"
                  >
                    <i className="bi bi-box-arrow-right me-1"></i> Logout
                  </Button>
                </Nav.Item>
              )}
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>

      <Container className="py-4">
        {!isLoggedIn ? (
          <div className="d-flex justify-content-center">
            <AuthFlow onLogin={handleLogin} />
          </div>
        ) : (
          <MainApp currentUser={currentUser} onLogout={handleLogout} />
        )}
      </Container>

      <footer className="bg-light py-3 mt-5">
        <Container>
          <div className="text-center text-muted">
            <small>© {new Date().getFullYear()} Smart Housing Advisor | Promoting Safe Housing Solutions</small>
          </div>
        </Container>
      </footer>
    </div>
  );
}

export default App;