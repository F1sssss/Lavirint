import bottle
import simplejson as json

from backend.customer.auth import requires_authentication
from backend.logging import logger
from backend.opb import dospjela_faktura_opb
from backend.podesavanja import podesavanja


@requires_authentication
def on_transition_finish_check_due_payments__turn_off_notifications(operater, firma):
    is_valid, error_message = validate_post_data(bottle.request.json)
    if not is_valid:
        logger.error(error_message)
        bottle.response.status = 400
        return bottle.response

    notifications = dospjela_faktura_opb.get_notification_by_ids(bottle.request.json['notificationIds'])
    for notification in notifications:
        if notification.operater_id != operater.id:
            bottle.response.status = 403
            return bottle.response

    dospjela_faktura_opb.set_notifications_as_seen(bottle.request.json['notificationIds'])

    return json.dumps({
        'isSuccess': True
    }, **podesavanja.JSON_DUMP_OPTIONS)


def validate_post_data(data):
    if 'notificationIds' not in data:
        return False, 'Missing required parameter "notificationIds"'

    if not isinstance(data['notificationIds'], list):
        return False, 'Parameter "notificationIds" must be an array'

    for notification_id in data['notificationIds']:
        if not isinstance(notification_id, int):
            return False, 'Members of "notificationIds" list must be integers'

    return True, None
