
import React, { useState } from 'react';
import {
  Row,
  Col,
  Card,
  Form,
  Button,
  Container,
  Alert,
  Spinner,
  Badge
} from 'react-bootstrap';
import apiService from '../utils/apiService';

const MainApp = ({ currentUser, onLogout }) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [formData, setFormData] = useState({
    location: '',
    destination: '',
    commute_minutes: 30,
    typical_return_time: 'Evening',
    monthly_budget: 5000,
    risk_tolerance: 'medium',
    living_arrangement: 'alone',
    transport_mode: 'matatu',
    preferences: ''
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

    // Check for forbidden terms (basic client-side guardrail)
    const forbidden = ["dangerous", "ghetto", "crime", "sketchy", "unsafe"];
    if (forbidden.some(word => formData.preferences.toLowerCase().includes(word))) {
      setError('🛡️ REFRAME: I can help you compare housing options based on situational factors like lighting, commute, and amenities.');
      setLoading(false);
      return;
    }

    try {
      // Map frontend fields to backend API format
      const inputData = {
        has_all_details: true,
        current_location: '',
        target_location: formData.location,
        workplace_location: formData.destination,
        monthly_budget: parseInt(formData.monthly_budget),
        preferences: formData.preferences,
        risk_tolerance: formData.risk_tolerance,
        typical_return_time: formData.typical_return_time.toLowerCase(),
        living_arrangement: formData.living_arrangement,
        transport_mode: formData.transport_mode,
        commute_minutes: parseInt(formData.commute_minutes),
        familiar_with_area: false,
        has_night_activities: formData.typical_return_time === 'Night'
      };

      // Call the backend API
      const response = await apiService.getHousingRecommendations(inputData);

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

  // Render risk tolerance badge
  const renderRiskBadge = (tolerance) => {
    if (!tolerance) return null;
    const variant = tolerance === 'low' ? 'success' : tolerance === 'high' ? 'warning' : 'info';
    return <Badge bg={variant} className="text-capitalize">{tolerance}</Badge>;
  };

  // Render contextual factors
  const renderContextualFactors = (factors) => {
    if (!factors) return null;
    return (
      <div className="mt-3">
        <h6 className="fw-semibold text-dark small text-uppercase text-muted">Contextual Factors</h6>
        <div className="d-flex flex-wrap gap-2">
          {factors.street_lighting && (
            <Badge bg="secondary" className="text-capitalize">
              <i className="bi bi-lightbulb me-1"></i>
              {factors.street_lighting} lighting
            </Badge>
          )}
          {factors.night_pedestrian_activity && (
            <Badge bg="secondary" className="text-capitalize">
              <i className="bi bi-people me-1"></i>
              {factors.night_pedestrian_activity} night activity
            </Badge>
          )}
          {factors.public_transport_hours && (
            <Badge bg="secondary" className="text-capitalize">
              <i className="bi bi-bus-front me-1"></i>
              Transport: {factors.public_transport_hours}
            </Badge>
          )}
          {factors.community_watch && (
            <Badge bg="success">
              <i className="bi bi-shield-check me-1"></i>
              Community Watch
            </Badge>
          )}
        </div>
      </div>
    );
  };

  // Render community strategies
  const renderCommunityStrategies = (strategies) => {
    if (!strategies) return null;
    return (
      <div className="mt-3">
        <h6 className="fw-semibold text-success small text-uppercase">
          <i className="bi bi-people-fill me-1"></i>
          What Residents Use
        </h6>
        <div className="d-flex flex-wrap gap-1">
          {[...strategies.digital_safety, ...strategies.transport_safety, ...strategies.community_resources]
            .slice(0, 6)
            .map((item, idx) => (
              <span key={idx} className="badge bg-success-subtle text-success-emphasis border border-success">
                {item}
              </span>
            ))}
        </div>
      </div>
    );
  };

  return (
    <Container fluid className="py-4 dashboard-container">
      <Row className="g-4">
        {/* Modern Sidebar */}
        <Col xl={sidebarCollapsed ? 1 : 3} lg={sidebarCollapsed ? 1 : 4} className="d-none d-lg-block">
          <div className={`modern-sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
            {!sidebarCollapsed ? (
              <div className="sidebar-content">
                <div className="user-info">
                  <div className="user-avatar">
                    <span>{currentUser?.name?.charAt(0) || 'U'}</span>
                  </div>
                  <div className="user-details">
                    <h5 className="user-name">{currentUser?.name || 'Guest User'}</h5>
                    <p className="user-email">{currentUser?.email || 'No email'}</p>
                  </div>
                </div>

                <div className="quick-stats">
                  <div className="stat-item">
                    <i className="bi bi-shield-check"></i>
                    <span>Risk Tolerance: {renderRiskBadge(formData.risk_tolerance)}</span>
                  </div>
                  <div className="stat-item">
                    <i className="bi bi-clock"></i>
                    <span>Returns: {formData.typical_return_time}</span>
                  </div>
                </div>

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
                  <h2 className="fw-bold text-dark mb-1">Housing Safety Advisor</h2>
                  <p className="text-muted mb-0 fs-6">Find housing options tailored to your needs and risk tolerance</p>
                </div>
              </div>
            </div>

            {/* Form Section */}
            <Card className="form-card">
              <Form onSubmit={handleSubmit}>
                <div className="form-sections">
                  {/* Location Section */}
                  <div className="form-section mb-5">
                    <div className="section-header mb-4">
                      <div className="d-flex align-items-center">
                        <div className="section-icon-large me-3">
                          <i className="bi bi-geo-alt-fill"></i>
                        </div>
                        <div>
                          <h4 className="fw-bold text-dark mb-1">Location & Commute</h4>
                          <p className="text-muted mb-0">Where are you looking and where do you work?</p>
                        </div>
                      </div>
                    </div>
                    
                    <Row className="g-4">
                      <Col md={6}>
                        <div className="form-group-modern">
                          <Form.Label className="form-label-modern">City/Town</Form.Label>
                          <Form.Control
                            type="text"
                            placeholder="e.g. Nairobi, Kisumu, Mombasa"
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
                          <Form.Label className="form-label-modern">Workplace Area</Form.Label>
                          <Form.Control
                            type="text"
                            placeholder="e.g. Westlands, CBD, Industrial Area"
                            name="destination"
                            value={formData.destination}
                            onChange={handleChange}
                            className="form-control-modern"
                          />
                          <Form.Text className="form-text-modern">
                            Where you'll be commuting to
                          </Form.Text>
                        </div>
                      </Col>
                    </Row>

                    <Row className="g-4 mt-2">
                      <Col md={6}>
                        <div className="form-group-modern">
                          <Form.Label className="form-label-modern">Commute Time (minutes)</Form.Label>
                          <Form.Control
                            type="number"
                            min="5"
                            max="180"
                            name="commute_minutes"
                            value={formData.commute_minutes}
                            onChange={handleChange}
                            className="form-control-modern"
                          />
                          <Form.Text className="form-text-modern">
                            Expected daily commute time
                          </Form.Text>
                        </div>
                      </Col>
                      <Col md={6}>
                        <div className="form-group-modern">
                          <Form.Label className="form-label-modern">Typical Return Time</Form.Label>
                          <Form.Select
                            name="typical_return_time"
                            value={formData.typical_return_time}
                            onChange={handleChange}
                            className="form-control-modern"
                          >
                            <option value="Daytime">Day (Before 6 PM)</option>
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
                          <p className="text-muted mb-0">Set your preferences and budget</p>
                        </div>
                      </div>
                    </div>

                    <div className="budget-section mb-4">
                      <div className="d-flex justify-content-between align-items-center mb-3">
                        <Form.Label className="form-label-modern mb-0">Monthly Budget (KES)</Form.Label>
                        <div className="budget-display">
                          <span className="budget-amount">{parseInt(formData.monthly_budget).toLocaleString()}</span>
                          <span className="budget-currency">KES</span>
                        </div>
                      </div>
                      <Form.Range
                        name="monthly_budget"
                        min="10000"
                        max="150000"
                        step="5000"
                        value={formData.monthly_budget}
                        onChange={handleChange}
                        className="budget-slider mb-2"
                      />
                      <div className="budget-labels">
                        <span>10K</span>
                        <span>45K</span>
                        <span>80K</span>
                        <span>115K</span>
                        <span>150K</span>
                      </div>
                    </div>

                    <Row className="g-4">
                      <Col md={4}>
                        <div className="form-group-modern">
                          <Form.Label className="form-label-modern">Risk Tolerance</Form.Label>
                          <Form.Select
                            name="risk_tolerance"
                            value={formData.risk_tolerance}
                            onChange={handleChange}
                            className="form-control-modern"
                          >
                            <option value="low">Low (Prioritize safety)</option>
                            <option value="medium">Medium (Balanced)</option>
                            <option value="high">High (More flexible)</option>
                          </Form.Select>
                          <Form.Text className="form-text-modern">
                            Your comfort with trade-offs
                          </Form.Text>
                        </div>
                      </Col>
                      <Col md={4}>
                        <div className="form-group-modern">
                          <Form.Label className="form-label-modern">Transport Mode</Form.Label>
                          <Form.Select
                            name="transport_mode"
                            value={formData.transport_mode}
                            onChange={handleChange}
                            className="form-control-modern"
                          >
                            <option value="matatu">Matatu</option>
                            <option value="walking">Walking</option>
                            <option value="bodaboda">Bodaboda</option>
                            <option value="private">Private</option>
                            <option value="bus">Bus</option>
                          </Form.Select>
                          <Form.Text className="form-text-modern">
                            Primary transport mode
                          </Form.Text>
                        </div>
                      </Col>
                      <Col md={4}>
                        <div className="form-group-modern">
                          <Form.Label className="form-label-modern">Living Arrangement</Form.Label>
                          <Form.Select
                            name="living_arrangement"
                            value={formData.living_arrangement}
                            onChange={handleChange}
                            className="form-control-modern"
                          >
                            <option value="alone">Alone</option>
                            <option value="shared">Shared</option>
                            <option value="family">With Family</option>
                          </Form.Select>
                          <Form.Text className="form-text-modern">
                            Who will you live with?
                          </Form.Text>
                        </div>
                      </Col>
                    </Row>

                    <div className="form-group-modern mt-4">
                      <Form.Label className="form-label-modern">Additional Preferences</Form.Label>
                      <Form.Control
                        as="textarea"
                        rows={3}
                        name="preferences"
                        value={formData.preferences}
                        onChange={handleChange}
                        placeholder="e.g., 'Near schools', 'Quiet neighborhood', 'Good amenities'..."
                        className="form-control-modern textarea-modern"
                      />
                      <Form.Text className="form-text-modern">
                        Any specific factors that matter to you
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
                        <Spinner as="span" animation="border" size="sm" className="me-3" />
                        <span>Analyzing Options...</span>
                      </>
                    ) : (
                      <>
                        <i className="bi bi-search me-3"></i>
                        <span>Find Housing Options</span>
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
                    <i className="bi bi-house-check"></i>
                  </div>
                  <div>
                    <h5 className="mb-0 fw-bold">Housing Recommendations</h5>
                    <p className="mb-0 text-muted small">
                      Based on your {formData.risk_tolerance} risk tolerance and {formData.typical_return_time.toLowerCase()} return time
                    </p>
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
                        <p className="text-muted">
                          Budget: {parseInt(formData.monthly_budget).toLocaleString()} KES/month | 
                          Workplace: {formData.destination || 'Not specified'}
                        </p>
                      </div>

                      {result.recommendations?.neighborhoods?.map((area, index) => (
                        <Card key={index} className="neighborhood-card mb-4 border-0 shadow-sm">
                          <Card.Body>
                            <div className="d-flex justify-content-between align-items-start mb-3">
                              <div>
                                <h5 className="fw-bold text-dark mb-1">{area.name}</h5>
                                <p className="text-muted mb-0 small">
                                  {area.distance_to_cbd && `${area.distance_to_cbd} from CBD`}
                                  {area.distance_to_workplace && ` • ${area.distance_to_workplace} from workplace`}
                                </p>
                              </div>
                              {area.key_tradeoffs && (
                                <Badge bg="primary" className="text-capitalize">
                                  {area.key_tradeoffs.substring(0, 30)}...
                                </Badge>
                              )}
                            </div>

                            <Row className="mb-3">
                              <Col md={6}>
                                <div className="border-start border-primary ps-3 py-1">
                                  <h6 className="text-primary fw-semibold">Rent Range</h6>
                                  <p className="mb-0 small">
                                    1BR: {area.average_rent_1br || 'Varies'}<br />
                                    2BR: {area.average_rent_2br || 'Varies'}
                                  </p>
                                </div>
                              </Col>
                              <Col md={6}>
                                <div className="border-start border-success ps-3 py-1">
                                  <h6 className="text-success fw-semibold">Transport</h6>
                                  <p className="mb-0 small">{area.transportation || 'See details'}</p>
                                </div>
                              </Col>
                            </Row>

                            {/* Contextual Safety Factors */}
                            {renderContextualFactors(area.contextual_factors)}

                            {/* Key Trade-offs */}
                            {area.factors_to_consider?.length > 0 && (
                              <div className="mt-3">
                                <h6 className="fw-semibold text-dark small text-uppercase text-muted">Factors to Consider</h6>
                                <ul className="list-unstyled mb-0">
                                  {area.factors_to_consider.slice(0, 4).map((factor, idx) => (
                                    <li key={idx} className="mb-1 small">
                                      <i className="bi bi-arrow-right-circle text-primary me-2"></i>
                                      {factor}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {/* Community Strategies */}
                            {renderCommunityStrategies(area.community_strategies)}

                            {/* Description */}
                            {area.description && (
                              <div className="mt-3 pt-3 border-top">
                                <p className="mb-0 text-muted small">{area.description}</p>
                              </div>
                            )}

                            {/* Amenities */}
                            {area.amenities?.length > 0 && (
                              <div className="mt-3 pt-3 border-top">
                                <h6 className="fw-semibold text-dark small">Nearby Amenities</h6>
                                <div className="d-flex flex-wrap gap-1">
                                  {area.amenities.slice(0, 5).map((amenity, idx) => (
                                    <span key={idx} className="badge bg-light text-dark border">{amenity}</span>
                                  ))}
                                </div>
                              </div>
                            )}
                          </Card.Body>
                        </Card>
                      ))}

                      {/* Detailed Report */}
                      {result.message && (
                        <div className="analysis-container">
                          <div className="analysis-header">
                            <h5>
                              <i className="bi bi-clipboard2-check-fill me-2"></i>
                              Detailed Analysis
                            </h5>
                            <p>Personalized recommendations based on your profile</p>
                          </div>
                          <div className="analysis-content">
                            <div dangerouslySetInnerHTML={{ 
                              __html: result.message
                                .replace(/##\s+(.*?)$/gm, '<h3 class="analysis-section-title">$1</h3>')
                                .replace(/###\s+(.*?)$/gm, '<h4>$1</h4>')
                                .replace(/\n/g, '<br />')
                                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                                .replace(/^- (.*?)$/gm, '<div class="factor-item">• $1</div>')
                            }} />
                          </div>
                        </div>
                      )}
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
            <Button variant="outline-primary" size="sm" onClick={onLogout} className="rounded-3 modern-btn">
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

