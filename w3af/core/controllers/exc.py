#!/usr/bin/python
# -*- coding: utf-8 -*-  

DEFAULT_ERR_MSG = 'The server has either erred or is incapable of performing\r\nthe requested operation.\r\n'


class ErrorCode(object):

    NORMAL = '0'

    # frame
    INTERNAL_ERROR = '10000'
    PARAMETER_INVALID = '10001'
    ADD_SCHEDULE_FAILED = '10002'
    OPERATE_DB_FAILED = '10003'
    CUR_STATUS_UNSUPPORTED = '10004'
    HAS_TARGET_FAILED = '10005'
    ALL_TARGETS_FAILED = '10006'
    SCAN_NOT_EXIST = '10007'
    TASK_NOT_EXIST = '10008'
    DEL_SCHEDULE_FAILED = '10009'
    HOST_NOT_EXIST = '10010'
    SCAN_VULN_NOT_EXIST = '10011'
    LICENSE_EXPIRED = '10012'
    NOT_EXIST_ACTIVE_AGENT = '10013'

    # scanner
    SCANNER_START_FAILED = '20001'
    SCANNER_INTERNAL_ERROR = '20002'
    SCANNER_EXIT_ABNORMALLY = '20003'
    SCANNER_OVER_LIMIT = '20004'
    TARGET_UNREACHABLE = '20005'
    USER_OP_STOP = '20006'
    SCANNER_LOGIN_FAILED = '20007'
    SCANNER_PROFILE_INVALID = '20008'

    # policy
    POLICY_NOT_EXIST = '30001'
    FAMILY_NOT_EXIST = '30002'
    PLUGIN_NOT_EXIST = '30003'
    VULN_NOT_EXIST = '30004'
    CANNOT_OPERATE_DEFAULT_POLICY = '30005'

    # agent
    AGENT_NOT_EXIST = '40001'
    AGENT_INTERNAL_ERROR = '40002'
    AGENT_IP_NOT_CONFIG = '40003'
    AGENT_SCANNER_INIT_FAILED = '40004'
    AGENT_STATUS_UNSUPPORTED = '40005'
    AGENT_CREATE_FAILED = '40006'
    AGENT_DELETE_FAILED = '40007'
    AGENT_ALREADY_EXIST = '40008'
    AGENT_IS_ERROR = '40009'
    AGENT_HAS_BEEN_DELETED = '40010'
    CANNOT_DELETE_WORKING_AGENT = '40011'
    STANDALONE_CAN_NOT_OP_AGENT = '40012'

    # report
    GENERATE_REPORT_PNG_FAILED = '50001'
    RENDER_HTML_REPORT_FAILED = '50002'

    # connection
    LOST_CONNECTION_TO_MQ = '60001'
    RPC_RSP_TIMEOUT = '60002'
    RPC_RSP_MALFORMED = '60003'

    # parameter
    MISS_HOST = '70001'
    INVALID_HOST = '70002'
    INVALID_SCHEDULE = '70003'
    INVALID_LOGIN = '70004'
    INVALID_POLICY_TYPE = '70005'
    INVALID_POLICY = '70006'
    INVALID_ACTION = '70007'
    INVALID_STATUS = '70008'
    INVALID_LOGIN_URL = '70009'

    # system
    SYS_NO_ENOUGH_MEM = '80001'
    SYS_NO_ENOUGH_DISK = '80002'
    SYS_INTERNAL_ERROR = '80003'

    # user
    USER_IS_NULL = '90001'
    USER_NOT_EXIST = '90002'
    USER_IS_DISABLED = '90003'
    USER_ROLE_NOT_ALLOW_OP = '90004'

    # log
    OP_LOG_NOT_EXIST = '11000'

    # upgrade
    PACKAGE_BROKEN = '12001'
    PACKAGE_IS_EXIST = '12002'
    HAS_UPGRADING = '12003'


class BaseWSGIError(StandardError):
    def __init__(self, err_code=ErrorCode.INTERNAL_ERROR, format_args=(), code=500):
        self.err_code = err_code
        self.code = code
        self.format_args = format_args


class RPCMalformedException(BaseWSGIError):
    def __init__(self):
        super(RPCMalformedException, self).__init__(err_code=ErrorCode.RPC_RSP_MALFORMED)


class RPCTimeoutException(BaseWSGIError):
    def __init__(self):
        super(RPCTimeoutException, self).__init__(err_code=ErrorCode.RPC_RSP_TIMEOUT)


class MQConnectionException(BaseWSGIError):
    def __init__(self):
        super(MQConnectionException, self).__init__(err_code=ErrorCode.LOST_CONNECTION_TO_MQ)

