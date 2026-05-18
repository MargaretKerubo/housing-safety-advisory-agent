import React from 'react';
import { Spinner, Container } from 'react-bootstrap';

const LoadingScreen = () => {
  return (
    <Container className="d-flex flex-column justify-content-center align-items-center min-vh-100">
      <div className="text-center">
        <div className="brand-icon mb-4 mx-auto" style={{ width: '80px', height: '80px', fontSize: '2.5rem' }}>
          <i className="bi bi-house-heart-fill"></i>
        </div>
        <Spinner animation="border" variant="primary" style={{ width: '3rem', height: '3rem' }} className="mb-3" />
        <h4 className="fw-bold text-dark">Initializing Advisor</h4>
        <p className="text-muted">Setting up your secure housing portal...</p>
      </div>
    </Container>
  );
};

export default LoadingScreen;
