def custom_404_error(error):
    response = {
        'status': error.code,
        'message': error.name,
        'error': error.data.get('message') if error.data.get('message') else str(error)
    }
    return response, error.code
