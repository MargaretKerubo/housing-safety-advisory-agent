from flask import Blueprint, request, jsonify
import logging
from app.services.agent_orchestrator import HousingAgent

logger = logging.getLogger(__name__)

agent_bp = Blueprint('agent', __name__, url_prefix='/api/agent')


@agent_bp.route('/query', methods=['POST'])
def agent_query():
    """Skills-based agent endpoint."""
    try:
        data = request.get_json()
        user_query = data.get('query', '')
        conversation_history = data.get('conversation_history', [])
        
        if not user_query:
            return jsonify({'error': 'Query is required'}), 400
        
        logger.info(f"Agent query: {user_query[:100]}...")
        
        agent = HousingAgent()
        result = agent.run(user_query, conversation_history)
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Agent error: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Agent execution failed',
            'message': str(e)
        }), 500


@agent_bp.route('/skills', methods=['GET'])
def list_skills():
    """List available skills."""
    try:
        from app.skills import SkillRegistry, PropertySearchSkill, CrimeStatsSkill, TransitDataSkill, NeighborhoodComparisonSkill, SafetyAnalysisSkill
        
        registry = SkillRegistry()
        registry.register(PropertySearchSkill())
        registry.register(CrimeStatsSkill())
        registry.register(TransitDataSkill())
        registry.register(NeighborhoodComparisonSkill())
        registry.register(SafetyAnalysisSkill())
        
        return jsonify({
            'skills': registry.list_schemas()
        })
    
    except Exception as e:
        logger.error(f"Error listing skills: {str(e)}")
        return jsonify({'error': str(e)}), 500
