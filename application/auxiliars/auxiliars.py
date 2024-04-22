

from application.enums.messages import MessagesEnum
from application.exceptions import ApiException, ValidationException, CustomException

def check_basic_data_fields(request):
    required_fields = ["meta_data", "data"]
    required_fields_metadata = ["table", "mac_address"]
    if request['where'] == {}:
        error = ApiException(MessagesEnum.PARAM_REQUIRED_ERROR)
        error.params = "Request body"
        error.set_message_params()
        return error
    
    for field in required_fields:
        if field not in request['where']:
            error = ApiException(MessagesEnum.PARAM_REQUIRED_ERROR)
            error.params = field
            error.set_message_params()
            return error    
     
    for field in required_fields_metadata:
        if field not in request['where']['meta_data']:
            error = ApiException(MessagesEnum.PARAM_REQUIRED_ERROR)
            error.params = field
            error.set_message_params()
            return error    
     
    return True