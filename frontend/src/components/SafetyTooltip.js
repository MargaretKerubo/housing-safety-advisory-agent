import React from 'react';
import { OverlayTrigger, Tooltip } from 'react-bootstrap';

const SafetyTooltip = ({ content, children }) => {
  const renderTooltip = (props) => (
    <Tooltip id="safety-tooltip" {...props}>
      {content}
    </Tooltip>
  );

  return (
    <OverlayTrigger
      placement="top"
      delay={{ show: 250, hide: 400 }}
      overlay={renderTooltip}
    >
      <span className="info-icon ms-2">
        <i className="bi bi-info-circle-fill small text-muted"></i>
        {children}
      </span>
    </OverlayTrigger>
  );
};

export default SafetyTooltip;
