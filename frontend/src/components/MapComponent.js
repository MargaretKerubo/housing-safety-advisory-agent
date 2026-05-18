import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icons in Leaflet with Webpack/React
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

// Component to handle map centering and zooming when coordinates change
const MapUpdater = ({ center, zoom }) => {
  const map = useMap();
  useEffect(() => {
    if (center) {
      map.setView(center, zoom || 13);
    }
  }, [center, zoom, map]);
  return null;
};

const MapComponent = ({ neighborhoods, height = "400px" }) => {
  // Filter neighborhoods with valid coordinates
  const markers = neighborhoods?.filter(n => n.latitude && n.longitude) || [];
  
  // Default center (Nairobi) if no markers
  const defaultCenter = [-1.2921, 36.8219];
  const center = markers.length > 0 
    ? [markers[0].latitude, markers[0].longitude] 
    : defaultCenter;

  return (
    <div className="map-wrapper shadow-sm rounded-4 overflow-hidden mb-4" style={{ height, border: '2px solid #e2e8f0' }}>
      <MapContainer 
        center={center} 
        zoom={12} 
        scrollWheelZoom={false}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {markers.map((neighborhood, index) => (
          <Marker 
            key={index} 
            position={[neighborhood.latitude, neighborhood.longitude]}
          >
            <Popup>
              <div className="p-1">
                <h6 className="fw-bold mb-1">{neighborhood.name}</h6>
                <p className="small mb-2 text-muted">{neighborhood.distance_to_cbd} from work</p>
                <div className="d-flex justify-content-between align-items-center">
                  <span className="badge bg-primary text-white" style={{ fontSize: '0.7rem' }}>
                    {neighborhood.security_rating}
                  </span>
                  <span className="fw-bold text-dark" style={{ fontSize: '0.8rem' }}>
                    {neighborhood.average_rent_1br} KES
                  </span>
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
        
        <MapUpdater center={center} />
      </MapContainer>
    </div>
  );
};

export default MapComponent;
