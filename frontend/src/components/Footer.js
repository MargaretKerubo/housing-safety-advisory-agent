import React from 'react';
import { Container, Row, Col } from 'react-bootstrap';

const Footer = () => {
  return (
    <footer className="bg-light py-4 mt-auto border-top">
      <Container>
        <Row className="align-items-center">
          <Col md={6} className="text-center text-md-start">
            <p className="text-muted mb-0">
              © 2026 Housing Safety Advisory AI Agent. Built for ethical and safe housing search.
            </p>
          </Col>
          <Col md={6} className="text-center text-md-end">
            <div className="footer-links">
              <a href="#privacy" className="text-muted text-decoration-none me-3">Privacy Policy</a>
              <a href="#terms" className="text-muted text-decoration-none me-3">Terms of Service</a>
              <a href="#contact" className="text-muted text-decoration-none">Contact Support</a>
            </div>
          </Col>
        </Row>
      </Container>
    </footer>
  );
};

export default Footer;
