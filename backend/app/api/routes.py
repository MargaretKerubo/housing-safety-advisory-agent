from flask import Blueprint, request, jsonify
import logging
from app.services import HousingAdvisoryService

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/housing-recommendations', methods=['POST'])
def get_housing_recommendations():
    """Endpoint to get housing recommendations based on user input."""
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

        # Initialize service on demand
        housing_service = HousingAdvisoryService()
        result = housing_service.process_housing_request(user_input)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error processing housing recommendation request: {str(e)}")
        return jsonify({
            'error': 'Failed to generate housing recommendations',
            'message': str(e)
        }), 500


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'OK', 'service': 'Housing Safety Advisory Agent'})
