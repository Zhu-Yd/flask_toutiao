def custom_404_error(error):
    response = {
        'status': 404,
        'message': 'The requested resource was not found on this server.',
        'error': error.data.get('message') if error.data.get('message') else str(error)
    }
    return response, 404
