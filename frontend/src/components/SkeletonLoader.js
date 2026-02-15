import React from 'react';
import { Card, Placeholder, Row, Col } from 'react-bootstrap';

const SkeletonLoader = () => {
  return (
    <Card className="neighborhood-card mb-4 border-0 shadow-sm">
      <Card.Body>
        <Placeholder as="div" animation="glow" className="mb-3">
          <Placeholder xs={6} size="lg" className="rounded" />
        </Placeholder>
        <Row className="mb-3">
          <Col md={6}>
            <Placeholder as="div" animation="glow">
              <Placeholder xs={4} className="mb-2" /> <br />
              <Placeholder xs={8} />
            </Placeholder>
          </Col>
          <Col md={6}>
            <Placeholder as="div" animation="glow">
              <Placeholder xs={4} className="mb-2" /> <br />
              <Placeholder xs={8} />
            </Placeholder>
          </Col>
        </Row>
        <Placeholder as="p" animation="glow">
          <Placeholder xs={12} />
          <Placeholder xs={10} />
        </Placeholder>
        <div className="d-flex gap-2 mt-3">
          <Placeholder xs={2} size="sm" className="rounded-pill" />
          <Placeholder xs={2} size="sm" className="rounded-pill" />
        </div>
      </Card.Body>
    </Card>
  );
};

export default SkeletonLoader;
