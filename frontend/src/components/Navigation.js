import React from 'react';
import { Navbar, Container, Nav, Button } from 'react-bootstrap';

const Navigation = ({ currentUser, onLogout }) => {
  return (
    <Navbar bg="white" expand="lg" className="shadow-sm mb-4">
      <Container>
        <Navbar.Brand href="#home" className="fw-bold text-primary">
          <i className="bi bi-shield-shaded me-2"></i>
          HousingSafety
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="ms-auto align-items-center">
            <Nav.Link href="#dashboard">Dashboard</Nav.Link>
            <Nav.Link href="#history">My Requests</Nav.Link>
            <Nav.Link href="#safety-tips">Safety Tips</Nav.Link>
            {currentUser && (
              <Button 
                variant="outline-primary" 
                size="sm" 
                className="ms-lg-3 mt-2 mt-lg-0"
                onClick={onLogout}
              >
                Logout
              </Button>
            )}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default Navigation;
