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
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
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
    <Container fluid className="py-4 dashboard-container">
      <Row className="g-4">
        {/* Modern Sidebar */}
        <Col xl={sidebarCollapsed ? 1 : 3} lg={sidebarCollapsed ? 1 : 4} className="d-none d-lg-block">
          <div className={`modern-sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
            {!sidebarCollapsed ? (
              <div className="sidebar-content">
                {/* User Info */}
                <div className="user-info">
                  <div className="user-avatar">
                    <span>{currentUser?.name?.charAt(0) || 'U'}</span>
                  </div>
                  <div className="user-details">
                    <h5 className="user-name">{currentUser?.name || 'Guest User'}</h5>
                    <p className="user-email">{currentUser?.email || 'No email'}</p>
                  </div>
                </div>

                {/* Quick Stats */}
                <div className="quick-stats">
                  <div className="stat-item">
                    <i className="bi bi-shield-check"></i>
                    <span>Verified Account</span>
                  </div>
                  <div className="stat-item">
                    <i className="bi bi-telephone"></i>
                    <span>{currentUser?.emergency ? 'Emergency Set' : 'No Emergency'}</span>
                  </div>
                </div>

                {/* Action Button */}
                <button className="sidebar-logout" onClick={onLogout}>
                  <i className="bi bi-box-arrow-right"></i>
                  <span>Sign Out</span>
                </button>
              </div>
            ) : (
              <div className="sidebar-collapsed">
                <div className="collapsed-avatar">
                  <span>{currentUser?.name?.charAt(0) || 'U'}</span>
                </div>
                <button className="collapsed-logout" onClick={onLogout} title="Sign Out">
                  <i className="bi bi-box-arrow-right"></i>
                </button>
              </div>
            )}
            
            {/* Toggle Button */}
            <button
              className="sidebar-toggle"
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              title={sidebarCollapsed ? 'Expand' : 'Collapse'}
            >
              <i className={`bi bi-chevron-${sidebarCollapsed ? 'right' : 'left'}`}></i>
            </button>
          </div>
        </Col>

        {/* Main Content */}
        <Col xl={sidebarCollapsed ? 11 : 9} lg={sidebarCollapsed ? 11 : 8}>
          <div className="main-dashboard">
            {/* Header Section */}
            <div className="dashboard-header mb-4">
              <div className="d-flex align-items-center">
                <div className="header-icon me-4">
                  <i className="bi bi-house-heart-fill"></i>
                </div>
                <div>
                  <h2 className="fw-bold text-dark mb-1">Smart Housing Advisor</h2>
                  <p className="text-muted mb-0 fs-6">Find safe and affordable housing options tailored to your needs</p>
                </div>
              </div>
            </div>

            {/* Form Section */}
            <Card className="form-card">
              <Form onSubmit={handleSubmit}>
                <div className="form-sections">
                  {/* Location & Commute Section */}
                  <div className="form-section mb-5">
                    <div className="section-header mb-4">
                      <div className="d-flex align-items-center">
                        <div className="section-icon-large me-3">
                          <i className="bi bi-geo-alt-fill"></i>
                        </div>
                        <div>
                          <h4 className="fw-bold text-dark mb-1">Location & Commute</h4>
                          <p className="text-muted mb-0">Tell us about your location and commute needs</p>
                        </div>
                      </div>
                    </div>
                    
                    <Row className="g-4">
                      <Col md={6}>
                        <div className="form-group-modern">
                          <Form.Label className="form-label-modern">City/Town</Form.Label>
                          <Form.Control
                            type="text"
                            placeholder="e.g. Kisumu, Nairobi, Mombasa"
                            name="location"
                            value={formData.location}
                            onChange={handleChange}
                            className="form-control-modern"
                            required
                          />
                          <Form.Text className="form-text-modern">
                            The city where you're looking for housing
                          </Form.Text>
                        </div>
                      </Col>
                      <Col md={6}>
                        <div className="form-group-modern">
                          <Form.Label className="form-label-modern">Workplace Location</Form.Label>
                          <Form.Control
                            type="text"
                            placeholder="e.g. CBD, Industrial Area, Westlands"
                            name="destination"
                            value={formData.destination}
                            onChange={handleChange}
                            className="form-control-modern"
                          />
                          <Form.Text className="form-text-modern">
                            Where you'll be commuting to daily
                          </Form.Text>
                        </div>
                      </Col>
                    </Row>

                    <Row className="g-4 mt-2">
                      <Col md={6}>
                        <div className="form-group-modern">
                          <Form.Label className="form-label-modern">Commute Distance (KM)</Form.Label>
                          <Form.Control
                            type="number"
                            min="0.1"
                            step="0.1"
                            name="distance"
                            value={formData.distance}
                            onChange={handleChange}
                            className="form-control-modern"
                          />
                          <Form.Text className="form-text-modern">
                            Approximate distance from home to workplace
                          </Form.Text>
                        </div>
                      </Col>
                      <Col md={6}>
                        <div className="form-group-modern">
                          <Form.Label className="form-label-modern">Typical Return Time</Form.Label>
                          <Form.Select
                            name="time"
                            value={formData.time}
                            onChange={handleChange}
                            className="form-control-modern"
                          >
                            <option value="Day">Day (Before 6 PM)</option>
                            <option value="Evening">Evening (6 PM - 9 PM)</option>
                            <option value="Night">Night (After 9 PM)</option>
                          </Form.Select>
                          <Form.Text className="form-text-modern">
                            When you typically return home
                          </Form.Text>
                        </div>
                      </Col>
                    </Row>
                  </div>

                  {/* Preferences Section */}
                  <div className="form-section mb-5">
                    <div className="section-header mb-4">
                      <div className="d-flex align-items-center">
                        <div className="section-icon-large me-3">
                          <i className="bi bi-sliders2-vertical"></i>
                        </div>
                        <div>
                          <h4 className="fw-bold text-dark mb-1">Preferences</h4>
                          <p className="text-muted mb-0">Set your housing preferences and budget</p>
                        </div>
                      </div>
                    </div>

                    <div className="budget-section mb-4">
                      <div className="d-flex justify-content-between align-items-center mb-3">
                        <Form.Label className="form-label-modern mb-0">Monthly Budget (KES)</Form.Label>
                        <div className="budget-display">
                          <span className="budget-amount">{parseInt(formData.budget).toLocaleString()}</span>
                          <span className="budget-currency">KES</span>
                        </div>
                      </div>
                      <Form.Range
                        name="budget"
                        min="10000"
                        max="100000"
                        step="5000"
                        value={formData.budget}
                        onChange={handleChange}
                        className="budget-slider mb-2"
                      />
                      <div className="budget-labels">
                        <span>10K</span>
                        <span>25K</span>
                        <span>50K</span>
                        <span>75K</span>
                        <span>100K</span>
                      </div>
                      <Form.Text className="form-text-modern">
                        Your maximum monthly rent budget
                      </Form.Text>
                    </div>

                    <Row className="g-4">
                      <Col md={6}>
                        <div className="form-group-modern">
                          <Form.Label className="form-label-modern">Safety Priority</Form.Label>
                          <Form.Select
                            name="safety"
                            value={formData.safety}
                            onChange={handleChange}
                            className="form-control-modern"
                          >
                            <option value="Low">Standard Safety</option>
                            <option value="Medium">Enhanced Safety</option>
                            <option value="High">Maximum Security</option>
                          </Form.Select>
                          <Form.Text className="form-text-modern">
                            How important is security to you?
                          </Form.Text>
                        </div>
                      </Col>
                      <Col md={6}>
                        <div className="form-group-modern">
                          <Form.Label className="form-label-modern">Living Arrangement</Form.Label>
                          <Form.Select
                            name="arrangement"
                            value={formData.arrangement}
                            onChange={handleChange}
                            className="form-control-modern"
                          >
                            <option value="Alone">Living Alone</option>
                            <option value="Shared">Shared Accommodation</option>
                            <option value="Family">With Family</option>
                          </Form.Select>
                          <Form.Text className="form-text-modern">
                            Who will be living with you?
                          </Form.Text>
                        </div>
                      </Col>
                    </Row>

                    <div className="form-group-modern mt-4">
                      <Form.Label className="form-label-modern">Additional Concerns</Form.Label>
                      <Form.Control
                        as="textarea"
                        rows={4}
                        name="query"
                        value={formData.query}
                        onChange={handleChange}
                        placeholder="Describe any specific safety concerns, accessibility needs, or other preferences..."
                        className="form-control-modern textarea-modern"
                      />
                      <Form.Text className="form-text-modern">
                        Any other factors that matter to you in choosing a neighborhood
                      </Form.Text>
                    </div>
                  </div>
                </div>

                <div className="submit-section">
                  <Button
                    variant="primary"
                    type="submit"
                    disabled={loading}
                    className="submit-btn"
                  >
                    {loading ? (
                      <>
                        <Spinner
                          as="span"
                          animation="border"
                          size="sm"
                          role="status"
                          className="me-3"
                        />
                        <span>Analyzing Housing Options...</span>
                      </>
                    ) : (
                      <>
                        <i className="bi bi-search me-3"></i>
                        <span>Find My Perfect Home</span>
                      </>
                    )}
                  </Button>
                </div>
              </Form>
            </Card>

            {error && (
              <Alert variant="warning" className="mt-4 modern-alert">
                <div className="d-flex align-items-center">
                  <i className="bi bi-exclamation-triangle-fill me-3 fs-5"></i>
                  <span>{error}</span>
                </div>
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
          </div>
        </Col>
      </Row>

      {/* Mobile Profile Card */}
      <div className="d-lg-none mt-4">
        <Card className="mobile-profile-card">
          <div className="d-flex justify-content-between align-items-center p-3">
            <div className="d-flex align-items-center">
              <div className="mobile-avatar me-3">
                <i className="bi bi-person-fill"></i>
              </div>
              <div>
                <h6 className="mb-0 fw-bold">{currentUser?.name || 'Guest'}</h6>
                <p className="text-muted small mb-0">{currentUser?.email || 'No email'}</p>
              </div>
            </div>
            <Button
              variant="outline-primary"
              size="sm"
              onClick={onLogout}
              className="rounded-3 modern-btn"
            >
              <i className="bi bi-box-arrow-right me-1"></i> 
              <span className="d-none d-sm-inline">Logout</span>
            </Button>
          </div>
        </Card>
      </div>
    </Container>
  );
};

export default MainApp;