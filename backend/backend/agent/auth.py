import bottle

from backend.opb import agent_user_opb


def requires_authentication(func):
    def wrapper(*args, **kwargs):
        agent_id = bottle.request.session.get('agent_user_id')
        if agent_id is None:
            bottle.response.status = 401
            return bottle.response

        agent = agent_user_opb.get_by_id(agent_id)

        try:
            return func(*[agent, *args], **kwargs)
        except Exception:
            raise

    return wrapper
