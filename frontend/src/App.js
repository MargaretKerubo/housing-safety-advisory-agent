import React, { useState, useEffect, Suspense, lazy } from 'react';
import { Container, Navbar, Nav, Button } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import './styles/App.css';
import LoadingScreen from './components/LoadingScreen';

// Lazy load components for bundle optimization
const AuthFlow = lazy(() => import('./components/AuthFlow'));
const MainApp = lazy(() => import('./components/MainApp'));

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
      <Navbar expand="lg" className="shadow-sm modern-navbar" fixed="top">
        <Container>
          <Navbar.Brand href="#home" className="d-flex align-items-center brand-logo">
            <div className="brand-icon me-3">
              <i className="bi bi-house-heart-fill"></i>
            </div>
            <div>
              <span className="fw-bold fs-3 brand-text">Smart Housing</span>
              <div className="brand-subtitle">Advisory Platform</div>
            </div>
          </Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="ms-auto">
              {isLoggedIn && (
                <Nav.Item>
                  <Button
                    variant="outline-primary"
                    onClick={handleLogout}
                    className="d-flex align-items-center modern-btn"
                  >
                    <i className="bi bi-box-arrow-right me-2"></i> 
                    <span>Sign Out</span>
                  </Button>
                </Nav.Item>
              )}
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>

      <Container className="py-4 main-content">
        <Suspense fallback={<LoadingScreen />}>
          {!isLoggedIn ? (
            <div className="d-flex justify-content-center align-items-center min-vh-100">
              <AuthFlow onLogin={handleLogin} />
            </div>
          ) : (
            <MainApp currentUser={currentUser} onLogout={handleLogout} />
          )}
        </Suspense>
      </Container>

      <footer className="modern-footer py-4 mt-5">
        <Container>
          <div className="text-center">
            <div className="d-flex justify-content-center align-items-center mb-3">
              <div className="footer-icon me-2">
                <i className="bi bi-house-heart"></i>
              </div>
              <span className="fw-semibold">Smart Housing Advisory</span>
            </div>
            <p className="text-muted mb-2">
              Empowering safe and informed housing decisions across Kenya
            </p>
            <small className="text-muted">
              © {new Date().getFullYear()} Smart Housing Advisory Platform | 
              <span className="text-primary fw-semibold"> Promoting Sustainable Communities</span>
            </small>
          </div>
        </Container>
      </footer>
    </div>
  );
}

export default App;