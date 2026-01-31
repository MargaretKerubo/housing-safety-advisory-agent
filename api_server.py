from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
import logging

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.agent_orchestrator import run_housing_agent

app = Flask(__name__, static_folder='frontend/build', static_url_path='/')

CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def mapFrontendToInternal(data):
    """
    Map frontend fields to internal format.
    Supports both old field names (for backward compatibility) and new field names.
    """
    # Determine which fields are present and map them
    target_location = data.get('target_location') or data.get('location', '')
    workplace_location = data.get('workplace_location') or data.get('destination', '')
    
    # Map commute
    commute_minutes = data.get('commute_minutes')
    if not commute_minutes:
        distance = data.get('distance', 1)
        # Rough conversion: 1km ≈ 3 minutes for matatu in Nairobi traffic
        commute_minutes = distance * 3
    
    # Map return time
    typical_return_time = data.get('typical_return_time')
    if not typical_return_time:
        time_mapping = {
            'Day': 'daytime',
            'Evening': 'evening', 
            'Night': 'night'
        }
        time_of_day = data.get('time', 'Day')
        typical_return_time = time_mapping.get(time_of_day, 'evening')
    
    # Map budget
    monthly_budget = data.get('monthly_budget')
    if not monthly_budget:
        monthly_budget = data.get('budget', 5000)
    
    # Map risk tolerance
    risk_tolerance = data.get('risk_tolerance')
    if not risk_tolerance:
        safety = data.get('safety', 'Medium')
        risk_mapping = {
            'Low': 'low',
            'Medium': 'medium',
            'High': 'high'
        }
        risk_tolerance = risk_mapping.get(safety, 'medium')
    
    # Map living arrangement
    living_arrangement = data.get('living_arrangement')
    if not living_arrangement:
        arrangement = data.get('arrangement', 'Alone')
        arrangement_mapping = {
            'Alone': 'alone',
            'Shared': 'shared',
            'Family': 'family'
        }
        living_arrangement = arrangement_mapping.get(arrangement, 'alone')
    
    # Map transport mode
    transport_mode = data.get('transport_mode', 'matatu')
    
    # Map preferences
    preferences = data.get('preferences') or data.get('query', '')
    
    # Map has_night_activities
    has_night_activities = data.get('has_night_activities', typical_return_time == 'night')
    
    # Determine has_all_details
    has_all_details = data.get('has_all_details', bool(target_location and monthly_budget))
    
    return {
        'has_all_details': has_all_details,
        'current_location': data.get('current_location', ''),
        'target_location': target_location,
        'workplace_location': workplace_location,
        'monthly_budget': float(monthly_budget) if monthly_budget else 50000,
        'preferences': preferences,
        'risk_tolerance': risk_tolerance,
        'typical_return_time': typical_return_time,
        'living_arrangement': living_arrangement,
        'transport_mode': transport_mode,
        'commute_minutes': int(commute_minutes) if commute_minutes else 30,
        'familiar_with_area': data.get('familiar_with_area', False),
        'has_night_activities': has_night_activities
    }


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve the React app"""
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/housing-recommendations', methods=['POST'])
def get_housing_recommendations():
    """Endpoint to get housing recommendations based on user input"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No data provided',
                'message': 'Please provide housing preferences in JSON format'
            }), 400

        # Map frontend fields to internal format
        internal_data = mapFrontendToInternal(data)
        
        logger.info(f"Processing request: location={internal_data['target_location']}, "
                   f"budget={internal_data['monthly_budget']}, "
                   f"risk_tolerance={internal_data['risk_tolerance']}")

        # Build user input string for the agent
        user_input = f"""
        I am looking for housing in {internal_data['target_location']}.
        My workplace is in {internal_data['workplace_location']}.
        My commute is approximately {internal_data['commute_minutes']} minutes.
        I typically return home in the {internal_data['typical_return_time']}.
        My budget is {internal_data['monthly_budget']} KES per month.
        My risk tolerance is {internal_data['risk_tolerance']} (low/medium/high).
        I will be living {internal_data['living_arrangement']}.
        My primary transport is {internal_data['transport_mode']}.
        Additional preferences: {internal_data['preferences']}
        """

        # Run the housing agent
        result = run_housing_agent(user_input)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            'error': 'Failed to generate housing recommendations',
            'message': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'OK', 
        'service': 'Housing Safety Advisory Agent',
        'version': '2.0.0'
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting server on port {port}")
    app.run(debug=True, host='0.0.0.0', port=port)

