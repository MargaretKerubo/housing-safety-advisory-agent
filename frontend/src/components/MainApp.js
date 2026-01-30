import React, { useState } from 'react';
import {
  Row,
  Col,
  Card,
  Form,
  Button,
  Accordion,
  Container,
  Alert,
  Spinner,
  ProgressBar,
  Badge
} from 'react-bootstrap';
import apiService from '../utils/apiService';

const MainApp = ({ currentUser, onLogout }) => {
  const [formData, setFormData] = useState({
    location: '',
    destination: '',
    distance: 1,
    time: 'Day',
    budget: 20000,
    safety: 'Medium',
    arrangement: 'Alone',
    query: ''
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setResult(null);
    setLoading(true);

    // Check for forbidden terms
    const forbidden = ["dangerous", "ghetto", "crime", "sketchy"];
    if (forbidden.some(word => formData.query.toLowerCase().includes(word))) {
      setError('🛡️ REFRAME: I can help you compare housing options based on situational factors like lighting and transit proximity.');
      setLoading(false);
      return;
    }

    try {
      // Prepare the data to send to the backend
      const inputData = {
        location: formData.location,
        destination: formData.destination,
        distance: parseFloat(formData.distance),
        time: formData.time,
        budget: parseInt(formData.budget),
        safety: formData.safety,
        arrangement: formData.arrangement,
        query: formData.query
      };

      // Call the backend API to get housing recommendations
      const response = await apiService.getHousingRecommendations(inputData);

      // Process the response based on the actual format from our backend
      if (response.status === 'success') {
        setResult(response);
      } else if (response.status === 'needs_more_info') {
        setResult(response);
      } else {
        setError('Unexpected response format from the server.');
      }
    } catch (err) {
      setError('Error generating recommendations. Please try again.');
      console.error('API Error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Function to render security rating badge
  const renderSecurityRating = (rating) => {
    if (!rating) return null;

    let variant = 'secondary';
    if (rating.includes('5') || rating.includes('4')) {
      variant = 'success';
    } else if (rating.includes('3')) {
      variant = 'warning';
    } else if (rating.includes('2') || rating.includes('1')) {
      variant = 'danger';
    }

    return <Badge bg={variant}>{rating}</Badge>;
  };

  return (
    <Container fluid className="py-4">
      <Row>
        {/* Sidebar - User Profile */}
        <Col lg={3} className="d-none d-lg-block">
          <Card className="profile-card h-100">
            <div className="text-center mb-4">
              <div className="feature-icon mx-auto mb-3">
                <i className="bi bi-person-fill"></i>
              </div>
              <h5 className="fw-bold text-dark">{currentUser?.name || 'Guest User'}</h5>
              <p className="text-muted small mb-1">{currentUser?.email || 'No email provided'}</p>
            </div>

            <div className="border-top pt-3 mt-3">
              <h6 className="fw-semibold text-dark mb-2"><i className="bi bi-shield-lock me-2"></i>Security</h6>
              <p className="text-muted small mb-0">
                Emergency: <span className="fw-medium">{currentUser?.emergency || 'N/A'}</span>
              </p>
            </div>

            <div className="mt-4">
              <Button
                variant="outline-primary"
                onClick={onLogout}
                className="w-100 py-2 rounded-2 fw-semibold"
              >
                <i className="bi bi-box-arrow-right me-2"></i>Sign Out
              </Button>
            </div>
          </Card>
        </Col>

        {/* Main Content */}
        <Col lg={9}>
          <Card className="advisor-card">
            <div className="d-flex align-items-center mb-4">
              <div className="feature-icon me-3">
                <i className="bi bi-house-heart"></i>
              </div>
              <div>
                <h3 className="fw-bold text-dark mb-0">🏠 Smart Housing Advisor</h3>
                <p className="text-muted mb-0">Find safe and affordable housing options tailored to your needs</p>
              </div>
            </div>

            <Form onSubmit={handleSubmit}>
              <Accordion defaultActiveKey={['0']} alwaysOpen className="mb-4">
                {/* Location & Commute Section */}
                <Accordion.Item eventKey="0" className="border-0">
                  <Accordion.Header className="bg-light rounded-3 p-3">
                    <div className="d-flex align-items-center">
                      <div className="feature-icon me-3">
                        <i className="bi bi-geo-alt-fill"></i>
                      </div>
                      <div>
                        <h5 className="mb-0 fw-bold">📍 Location & Commute</h5>
                        <p className="mb-0 text-muted small">Tell us about your location and commute needs</p>
                      </div>
                    </div>
                  </Accordion.Header>
                  <Accordion.Body className="pt-4">
                    <Row>
                      <Col md={6}>
                        <Form.Group className="mb-4" controlId="location">
                          <Form.Label className="fw-semibold text-dark">City/Town</Form.Label>
                          <Form.Control
                            type="text"
                            placeholder="e.g. Kisumu, Nairobi, Mombasa"
                            name="location"
                            value={formData.location}
                            onChange={handleChange}
                            className="rounded-2 py-2"
                            required
                          />
                          <Form.Text className="text-muted">
                            The city where you're looking for housing
                          </Form.Text>
                        </Form.Group>
                      </Col>
                      <Col md={6}>
                        <Form.Group className="mb-4" controlId="destination">
                          <Form.Label className="fw-semibold text-dark">Workplace Location</Form.Label>
                          <Form.Control
                            type="text"
                            placeholder="e.g. CBD, Industrial Area, Westlands"
                            name="destination"
                            value={formData.destination}
                            onChange={handleChange}
                            className="rounded-2 py-2"
                          />
                          <Form.Text className="text-muted">
                            Where you'll be commuting to daily
                          </Form.Text>
                        </Form.Group>
                      </Col>
                    </Row>

                    <Row>
                      <Col md={6}>
                        <Form.Group className="mb-4" controlId="distance">
                          <Form.Label className="fw-semibold text-dark">Commute Distance (KM)</Form.Label>
                          <Form.Control
                            type="number"
                            min="0.1"
                            step="0.1"
                            name="distance"
                            value={formData.distance}
                            onChange={handleChange}
                            className="rounded-2 py-2"
                          />
                          <Form.Text className="text-muted">
                            Approximate distance from home to workplace
                          </Form.Text>
                        </Form.Group>
                      </Col>
                      <Col md={6}>
                        <Form.Group className="mb-4" controlId="time">
                          <Form.Label className="fw-semibold text-dark">Typical Return Time</Form.Label>
                          <Form.Select
                            name="time"
                            value={formData.time}
                            onChange={handleChange}
                            className="rounded-2 py-2"
                          >
                            <option value="Day">Day (Before 6 PM)</option>
                            <option value="Evening">Evening (6 PM - 9 PM)</option>
                            <option value="Night">Night (After 9 PM)</option>
                          </Form.Select>
                          <Form.Text className="text-muted">
                            When you typically return home
                          </Form.Text>
                        </Form.Group>
                      </Col>
                    </Row>
                  </Accordion.Body>
                </Accordion.Item>

                {/* Preferences Section */}
                <Accordion.Item eventKey="1" className="border-0">
                  <Accordion.Header className="bg-light rounded-3 p-3">
                    <div className="d-flex align-items-center">
                      <div className="feature-icon me-3">
                        <i className="bi bi-sliders2-vertical"></i>
                      </div>
                      <div>
                        <h5 className="mb-0 fw-bold">💰 Preferences</h5>
                        <p className="mb-0 text-muted small">Set your housing preferences and budget</p>
                      </div>
                    </div>
                  </Accordion.Header>
                  <Accordion.Body className="pt-4">
                    <Form.Group className="mb-4" controlId="budget">
                      <div className="d-flex justify-content-between align-items-center mb-2">
                        <Form.Label className="fw-semibold text-dark">Monthly Budget (KES)</Form.Label>
                        <span className="fw-bold text-primary fs-5">{parseInt(formData.budget).toLocaleString()} KES</span>
                      </div>
                      <Form.Range
                        name="budget"
                        min="10000"
                        max="100000"
                        step="5000"
                        value={formData.budget}
                        onChange={handleChange}
                        className="mb-2"
                      />
                      <div className="input-range-labels">
                        <span>10,000</span>
                        <span>25,000</span>
                        <span>50,000</span>
                        <span>75,000</span>
                        <span>100,000</span>
                      </div>
                      <Form.Text className="text-muted">
                        Your maximum monthly rent budget
                      </Form.Text>
                    </Form.Group>

                    <Row>
                      <Col md={6}>
                        <Form.Group className="mb-4" controlId="safety">
                          <Form.Label className="fw-semibold text-dark">Safety Priority</Form.Label>
                          <Form.Select
                            name="safety"
                            value={formData.safety}
                            onChange={handleChange}
                            className="rounded-2 py-2"
                          >
                            <option value="Low">Standard Safety</option>
                            <option value="Medium">Enhanced Safety</option>
                            <option value="High">Maximum Security</option>
                          </Form.Select>
                          <Form.Text className="text-muted">
                            How important is security to you?
                          </Form.Text>
                        </Form.Group>
                      </Col>
                      <Col md={6}>
                        <Form.Group className="mb-4" controlId="arrangement">
                          <Form.Label className="fw-semibold text-dark">Living Arrangement</Form.Label>
                          <Form.Select
                            name="arrangement"
                            value={formData.arrangement}
                            onChange={handleChange}
                            className="rounded-2 py-2"
                          >
                            <option value="Alone">Living Alone</option>
                            <option value="Shared">Shared Accommodation</option>
                            <option value="Family">With Family</option>
                          </Form.Select>
                          <Form.Text className="text-muted">
                            Who will be living with you?
                          </Form.Text>
                        </Form.Group>
                      </Col>
                    </Row>

                    <Form.Group className="mb-4" controlId="query">
                      <Form.Label className="fw-semibold text-dark">Additional Concerns</Form.Label>
                      <Form.Control
                        as="textarea"
                        rows={3}
                        name="query"
                        value={formData.query}
                        onChange={handleChange}
                        placeholder="Describe any specific safety concerns, accessibility needs, or other preferences..."
                        className="rounded-2 py-2"
                      />
                      <Form.Text className="text-muted">
                        Any other factors that matter to you in choosing a neighborhood
                      </Form.Text>
                    </Form.Group>
                  </Accordion.Body>
                </Accordion.Item>
              </Accordion>

              <Button
                variant="primary"
                type="submit"
                disabled={loading}
                className="w-100 py-3 rounded-3 fw-bold fs-5"
              >
                {loading ? (
                  <>
                    <Spinner
                      as="span"
                      animation="border"
                      size="sm"
                      role="status"
                      className="me-2"
                    />
                    Analyzing Housing Options...
                  </>
                ) : (
                  <>
                    <i className="bi bi-search me-2"></i>
                    Find My Perfect Home
                  </>
                )}
              </Button>
            </Form>

            {error && (
              <Alert variant="warning" className="mt-4 rounded-3">
                <i className="bi bi-exclamation-triangle-fill me-2"></i>
                {error}
              </Alert>
            )}

            {result && (
              <Card className="mt-4 advisor-card">
                <Card.Header className="d-flex align-items-center">
                  <div className="feature-icon me-3">
                    <i className="bi bi-file-earmark-text"></i>
                  </div>
                  <div>
                    <h5 className="mb-0 fw-bold">Advisor Report</h5>
                    <p className="mb-0 text-muted small">Your personalized housing recommendations</p>
                  </div>
                </Card.Header>
                <Card.Body>
                  {result.status === 'needs_more_info' ? (
                    <div className="text-center py-4">
                      <div className="feature-icon mx-auto mb-3">
                        <i className="bi bi-chat-dots"></i>
                      </div>
                      <h5 className="fw-bold">More Information Needed</h5>
                      <p className="text-muted">{result.message}</p>
                    </div>
                  ) : (
                    <>
                      <div className="mb-4">
                        <h4 className="fw-bold text-dark">Recommended Areas in {formData.location}</h4>
                        <p className="text-muted">Based on your preferences and budget of {parseInt(formData.budget).toLocaleString()} KES</p>
                      </div>

                      {result.recommendations && result.recommendations.neighborhoods.map((area, index) => (
                        <Card key={index} className="neighborhood-card mb-4 border-0 shadow-sm">
                          <Card.Body>
                            <div className="d-flex justify-content-between align-items-start mb-3">
                              <div>
                                <h5 className="fw-bold text-dark mb-1">{area.name}</h5>
                                <p className="text-muted mb-0">{area.distance_to_cbd} from {formData.destination}</p>
                              </div>
                              <div className="text-end">
                                <div className="mb-1">Security:</div>
                                {renderSecurityRating(area.security_rating)}
                              </div>
                            </div>

                            <Row className="mb-3">
                              <Col md={6}>
                                <div className="border-start border-primary ps-3 py-1">
                                  <h6 className="text-primary fw-semibold">Rent Range</h6>
                                  <p className="mb-0">
                                    <strong>1BR:</strong> {area.average_rent_1br} KES<br />
                                    <strong>2BR:</strong> {area.average_rent_2br} KES
                                  </p>
                                </div>
                              </Col>
                              <Col md={6}>
                                <div className="border-start border-success ps-3 py-1">
                                  <h6 className="text-success fw-semibold">Transportation</h6>
                                  <p className="mb-0">{area.transportation}</p>
                                </div>
                              </Col>
                            </Row>

                            <div className="mb-3">
                              <h6 className="fw-semibold text-dark">Description</h6>
                              <p className="mb-2">{area.description}</p>
                            </div>

                            <div className="row">
                              <div className="col-md-6">
                                <div className="border-start border-success ps-3">
                                  <h6 className="text-success fw-semibold">Pros</h6>
                                  <ul className="list-unstyled">
                                    {area.pros.map((pro, idx) => (
                                      <li key={idx} className="mb-1"><i className="bi bi-check-circle-fill text-success me-2"></i>{pro}</li>
                                    ))}
                                  </ul>
                                </div>
                              </div>
                              <div className="col-md-6">
                                <div className="border-start border-warning ps-3">
                                  <h6 className="text-warning fw-semibold">Cons</h6>
                                  <ul className="list-unstyled">
                                    {area.cons.map((con, idx) => (
                                      <li key={idx} className="mb-1"><i className="bi bi-x-circle-fill text-warning me-2"></i>{con}</li>
                                    ))}
                                  </ul>
                                </div>
                              </div>
                            </div>

                            <div className="border-top pt-3 mt-3">
                              <h6 className="fw-semibold text-dark">Amenities</h6>
                              <div className="d-flex flex-wrap gap-2">
                                {area.amenities.map((amenity, idx) => (
                                  <span key={idx} className="badge bg-light text-dark border">{amenity}</span>
                                ))}
                              </div>
                            </div>
                          </Card.Body>
                        </Card>
                      ))}

                      <div className="border-top pt-4 mt-4">
                        <h5 className="fw-bold text-dark mb-3">Detailed Recommendation</h5>
                        <div className="bg-light p-4 rounded-3">
                          <div dangerouslySetInnerHTML={{ __html: result.message.replace(/\n/g, '<br />') }} />
                        </div>
                      </div>
                    </>
                  )}
                </Card.Body>
              </Card>
            )}
          </Card>
        </Col>
      </Row>

      {/* Mobile logout button */}
      <div className="d-lg-none mt-3">
        <Card className="profile-card">
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h6 className="mb-0 fw-bold">{currentUser?.name || 'Guest'}</h6>
              <p className="text-muted small mb-0">{currentUser?.email || 'No email'}</p>
            </div>
            <Button
              variant="outline-primary"
              size="sm"
              onClick={onLogout}
              className="rounded-2"
            >
              <i className="bi bi-box-arrow-right"></i> Logout
            </Button>
          </div>
        </Card>
      </div>
    </Container>
  );
};

export default MainApp;