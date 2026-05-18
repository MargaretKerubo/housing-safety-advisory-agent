import React from 'react';
import { Container, Button, Alert } from 'react-bootstrap';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
    // You could also log the error to an error reporting service here
    console.error("Uncaught error:", error, errorInfo);
  }

  handleRestart = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <Container className="d-flex flex-column justify-content-center align-items-center min-vh-100">
          <div className="text-center p-5 shadow-lg rounded-4 bg-white" style={{ maxWidth: '600px' }}>
            <div className="brand-icon mb-4 mx-auto" style={{ width: '80px', height: '80px', fontSize: '2.5rem', background: 'linear-gradient(135deg, #ef4444, #dc2626)' }}>
              <i className="bi bi-exclamation-octagon-fill"></i>
            </div>
            <h2 className="fw-bold text-dark mb-3">Something went wrong</h2>
            <p className="text-muted mb-4">
              We encountered an unexpected error. This might be due to a temporary connection issue or a glitch in the application.
            </p>
            {this.state.error && (
              <Alert variant="danger" className="text-start small mb-4 overflow-auto" style={{ maxHeight: '150px' }}>
                <code>{this.state.error.toString()}</code>
              </Alert>
            )}
            <div className="d-grid gap-3 d-sm-flex justify-content-sm-center">
              <Button 
                variant="primary" 
                onClick={this.handleRestart}
                className="px-4 py-2 rounded-3 fw-bold"
              >
                <i className="bi bi-arrow-clockwise me-2"></i>
                Reload Application
              </Button>
              <Button 
                variant="outline-secondary" 
                href="/"
                className="px-4 py-2 rounded-3"
              >
                Go to Homepage
              </Button>
            </div>
          </div>
        </Container>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
