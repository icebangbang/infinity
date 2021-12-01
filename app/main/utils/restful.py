# -*- coding: UTF-8 -*-
from flask import jsonify
from flask import make_response
import simplejson
from app.main.utils.simple_util import DatetimeJsonEncoder
import json

# define statu_dics here
R200_OK = {'code': 200, 'message': 'OK all right.'}
R201_CREATED = {'code': 201, 'message': 'All created.'}
R204_NOCONTENT = {'code': 204, 'message': 'All deleted.'}
R400_BADREQUEST = {'code': 400, 'message': 'Bad request.'}
R403_FORBIDDEN = {'code': 403, 'message': 'You can not do this.'}
R404_NOTFOUND = {'code': 404, 'message': 'No result matched.'}


def full_response(status_dic, data):
    return jsonify({'status': status_dic, 'data': data})


def status_response(status_dic):
    return jsonify({'status': status_dic})


def response_error(error):
    error = error.value
    return response(data=None, message=error.message,
                    success=False, error_code=error.error_code)


# def responseto(data=None, message=None, success=True,cls=None, **kwargs):
#     # type: (object, object, object, object, object) -> object
def response(data=None, message=None, success=True, **kwargs):
    """ 封装 json 响应"""
    result = kwargs
    result['success'] = success
    result['message'] = message
    result['data'] = data

    # # 如果提供了 data，那么不理任何其他参数，直接响应 data
    # if not data:
    #     # data = kwargs
    #     result['error'] = error
    #     if message:
    #         # 除非显示提供 error 的值，否则默认为 True
    #         # 意思是提供了 message 就代表有 error
    #         result['message'] = message
    #         if error is None:
    #             result['error'] = True
    #     else:
    #         # 除非显示提供 error 的值，否则默认为 False
    #         # 意思是没有提供 message 就代表没有 error
    #         if error is None:
    #             data['error'] = False
    # # if not isinstance(data, dict):
    # #     data = {'error':True, 'message':'data 必须是一个 dict！'}
    # resp = make_response(json.dumps(result, allow_nan=False))
    resp = make_response(simplejson.dumps(result, ignore_nan=True, ensure_ascii=False, cls=DatetimeJsonEncoder))
    # 跨域设置
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Content-Type'] = 'application/json'
    resp.headers["Access-Control-Allow-Methods"] = "GET,HEAD,OPTIONS,POST,PUT"
    resp.headers["Access-Control-Request-Headers"] = "token"

    resp.headers[
        "Access-Control-Allow-Headers"] = "token,Origin, X-Requested-With, Content-Type, Accept, Connection, User-Agent,Cookie,Cache-Control"
    return resp


def response_pandas(response):
    # 跨域设置
    response.headers['Access-Control-Allow-Origin'] = '*'
    # response.headers["Content-Disposition"] = "attachment; filename=" + file_name
    response.headers["Access-Control-Allow-Methods"] = "GET,HEAD,OPTIONS,POST,PUT"
    response.headers[
        "Access-Control-Allow-Headers"] = "Origin," \
                                          "X-Requested-With," \
                                          "Content-Type," \
                                          "Accept," \
                                          "Connection," \
                                          "User-Agent," \
                                          "Cookie,Cache-Control"
    return response


def response_file(response, filename):
    # 跨域设置
    response.headers['Access-Control-Allow-Origin'] = '*'
    # response.headers["Content-Disposition"] = "attachment; filename=" + file_name
    response.headers["Access-Control-Allow-Methods"] = "GET,HEAD,OPTIONS,POST,PUT"
    response.headers["Content-Disposition"] = "attachment; filename=" + filename
    response.headers[
        "Access-Control-Allow-Headers"] = "Origin," \
                                          "X-Requested-With," \
                                          "Content-Type," \
                                          "Accept," \
                                          "Connection," \
                                          "User-Agent," \
                                          "Cookie," \
                                          "Cache-Control"
    return response
