import bottle
import simplejson as json

from backend.agent.auth import requires_authentication
from backend.agent.helper import PagedData
from backend.models import Firma, AgentUser
from backend.opb import firma_opb
from backend.podesavanja import podesavanja


@requires_authentication
def controller(agent_user: AgentUser):
    post_data = bottle.request.json.copy()
    base_query = firma_opb.get_filtered_companies({})
    filtered_query = firma_opb.get_filtered_companies(post_data['filters'])
    companies_page = PagedData[Firma](base_query, filtered_query, post_data['pageNumber'], post_data['itemsPerPage'])
    return json.dumps(
        serialize_response(companies_page),
        **podesavanja.JSON_DUMP_OPTIONS
    )


def serialize_response(page_data: PagedData[Firma]):
    serialized_items = []
    for customer in page_data.items:
        if customer.next_certificate_id is not None:
            certificate_expiration_date = customer.next_certificate.not_valid_after.isoformat()
        elif customer.current_certificate_id is not None:
            certificate_expiration_date = customer.current_certificate.not_valid_after.isoformat()
        else:
            certificate_expiration_date = None

        serialized_items.append({
            'id': customer.id,
            'name': customer.naziv,
            'identificationNumber': customer.pib,
            'isActive': customer.je_aktivna,
            'isTaxpayer': customer.je_poreski_obaveznik,
            'certificateExpirationDate': certificate_expiration_date
        })

    return {
        'pagedData': {
            'pageIndex': page_data.page_index,
            'pageNumber': page_data.page_number,
            'itemsPerPage': page_data.items_per_page,
            'totalItems': page_data.total_items,
            'totalPages': page_data.total_pages,
            'items': serialized_items,
            'pageStart': page_data.page_start,
            'pageEnd': page_data.page_end,
            'baseItems': page_data.base_items
        }
    }
