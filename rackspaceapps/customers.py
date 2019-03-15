from .errors import UnexpectedStatusError, InvalidParameterError
import csv, io


def list_invoices(api):

    session = api.build_session()

    def request(account_number=''):
        if not account_number:
            account_number = api._account_number
        resource = ('customers', account_number, 'invoices')
        url = api.build_resource(resource)
        per_page = 100
        current_page = 0
        offset = 0
        invoices = []
        page_invoices = True
        while page_invoices:
            query = {'size': per_page, 'offset': offset}
            response = session.get(url, params=query)
            try:
                data = response.json()
            except (ValueError, TypeError):
                data = {}
            if response.status_code != 200:
                err = 'Expected 200, got: {} ({})'
                raise UnexpectedStatusError(err.format(response.status_code,
                                                       response.text))
            total = data.get('Total', 0)
            page_invoices = data.get('Items', [])
            invoices = invoices + page_invoices
            if offset + per_page > total:
                break
            current_page += 1
            offset = current_page * per_page
        return invoices

    return request


def invoice_lines(api):

    session = api.build_session()

    def request(invoice, account_number=''):
        if not account_number:
            account_number = api._account_number
        resource = ('customers', account_number, 'invoices', invoice)
        url = api.build_resource(resource)
        response = session.get(url)
        csvfile = csv.DictReader(io.StringIO(response.text))
        try:
            data = [row for row in csvfile]
        except:
            data = []
        if response.status_code != 200:
            err = 'Expected 200, got: {} ({})'
            raise UnexpectedStatusError(err.format(response.status_code,
                                                   response.text))
        return data

    return request

