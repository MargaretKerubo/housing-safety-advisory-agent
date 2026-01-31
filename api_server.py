
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

        # Extract parameters from the request
        location = data.get('location', '')
        destination = data.get('destination', '')
        distance = data.get('distance', 1)
        time_of_day = data.get('time', 'Day')
        budget = data.get('budget', 20000)
        safety = data.get('safety', 'Medium')
        arrangement = data.get('arrangement', 'Alone')
        query = data.get('query', '')

        # Format the user input for the housing agent
        user_input = f"""
        I'm looking for housing in {location}.
        My workplace is in {destination}.
        The commute distance is {distance}km.
        I plan to return at {time_of_day}.
        My budget is {budget} KES per month.
        I prefer {safety} safety tolerance.
        I will be living {arrangement}.
        Additional concerns: {query}
        """

        logger.info(f"Processing housing recommendation request for location: {location}")

        # Run the housing agent with the user input
        result = run_housing_agent(user_input)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error processing housing recommendation request: {str(e)}")
        return jsonify({
            'error': 'Failed to generate housing recommendations',
            'message': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'OK', 'service': 'Housing Safety Advisory Agent'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))