#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import re
import logging
import hashlib
import uuid
from datetime import datetime
from optparse import OptionParser
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

from scoring import get_interests, get_score

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}


class Field(object):
    def __init__(self, nullable=False, required=False):
        self.nullable = nullable
        self.required = required

    def validate(self, value):
        if self.required and value is None:
            raise ValueError("This field is required.")
        if not self.nullable and not value:
            raise ValueError("Value is nulled")

    def parse_validate(self, value):
        pass

    def is_empty(self, value):
        if not bool(value):
            raise ValueError("Value is empty")


class CharField(Field):
    def parse_validate(self, value):
        """
        Validate field value. Validation rules:
            1) String
        Args:
            value: Field value
        """
        self.validate(value)
        if not (value is None):
            if not isinstance(value, basestring):
                raise ValueError("Value is not string format")
            return value if isinstance(value, unicode) else value.decode("utf-8")


class ArgumentsField(Field):
    def parse_validate(self, value):
        """
        Validate field value. Validation rules:
            1) Dictionary
        Returns:
            value: Field value
        """
        self.validate(value)
        if not isinstance(value, dict):
            raise ValueError("Arguments is not dict")
        return value


class EmailField(CharField):
    rx_email = re.compile(r"^[a-zA-Z0-9_]+@[a-zA-Z0-9]+.[a-zA-Z]+", re.MULTILINE)

    def parse_validate(self, value):
        """
        Validate field value. Validation rules:
            1) String
            2) Check regexp email format
        Returns:
            value: Field value
        """
        super(EmailField, self).parse_validate(value)
        if not (value is None):
            return self.type_email(value)

    def type_email(self, value):
        if not self.rx_email.search(value):
            raise ValueError("String is not Email address")
        return value


class PhoneField(Field):
    def parse_validate(self, value):
        """
       Validate field value. Validation rules:
           1) String or number
           2) Length - 11
           2) First character - '7'
       Returns:
           value: Field value
       """
        self.validate(value)
        if not (value is None):
            if (
                not isinstance(value, basestring) and not isinstance(value, int)
            ) or not str(value).isdigit():
                raise ValueError("Phone number must be number")
            if not len(str(value)) == 11 or not str(value).startswith("7"):
                raise ValueError("Phone number should be 7**********")
            return value


class DateField(Field):
    def parse_validate(self, value):
        """
        Validate field value. Validation rules:
            1) String
            2) Format - DD.MM.YYYY
        Returns:
            value: Field value
        """
        self.validate(value)
        if isinstance(value, str):
            try:
                datetime.strptime(value, "%d.%m.%Y")
            except ValueError:
                raise ValueError("Bad date format, should be DD.MM.YYYY")
            return value
        elif not (value is None):
            raise ValueError("Date not string format")


class BirthDayField(DateField):
    def parse_validate(self, value):
        """
        Validate field value. Validation rules:
            1) Date
            2) 0 < Now - value <= 70 years
        Returns:
            value: Field value
        """
        super(BirthDayField, self).parse_validate(value)
        if not (value is None):
            bdate = datetime.strptime(value, "%d.%m.%Y")
            age = (datetime.today() - bdate).days / 365
            if not (0 < age < 70):
                raise ValueError("Age %s over 70" % age)
            return value


class GenderField(Field):
    def parse_validate(self, value):
        """
       Validate field value. Validation rules:
           1) Number
           2) Value in (0, 1, 2)
       Returns:
           value: Field value
       """
        self.validate(value)
        if value is not None:
            if not isinstance(value, int):
                raise ValueError("Gender value not at int")
            elif value not in (0, 1, 2):
                raise ValueError("Gender value invalid format")
            return value


class ClientIDsField(Field):
    def parse_validate(self, value):
        """
        Validate field value. Validation rules:
            1) Array
            2) Elements - number
            3) Array not empty
        Returns:
            value: Field value
        """
        self.is_empty(value)
        self.validate(value)
        if not isinstance(value, list):
            raise ValueError("Client IDs is not list format %s" % value)
        if not all(isinstance(x, int) for x in value):
            raise ValueError("Client IDs is not current format %s" % value)
        return value


class RequestHandler(object):
    def validate_handle(self, request, arguments, ctx, store):
        if not arguments.is_valid():
            return arguments.errfmt(), INVALID_REQUEST
        return self.handle(request, arguments, ctx, store)

    def handle(self, request, arguments, ctx):
        return {}, OK


class RequestMeta(type):
    def __new__(mcs, name, bases, attrs):
        field_list = {}
        for k, field in attrs.items():
            if isinstance(field, Field):
                field_list[k] = field
        cls = super(RequestMeta, mcs).__new__(mcs, name, bases, attrs)
        cls.fields = field_list
        return cls


class RequestBase(object):
    __metaclass__ = RequestMeta

    def __init__(self, request):
        self.errors = []
        self.request = request
        self.vl_check = False

    def clean(self):
        for name, field in self.fields.items():
            value = self.request.get(name)
            try:
                setattr(self, name, field.parse_validate(value))
            except ValueError as e:
                self.errors.append("%s field validation error: %s" % (name, e))
        if not self.errors:
            logging.info("Validation is OK")
            return True
        logging.error("Validation is False")
        return False

    def is_valid(self):
        return self.clean()

    def errfmt(self):
        return ", ".join(self.errors)


class ClientsInterestsRequest(RequestBase):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)


class ClientsInterestsHandler(RequestHandler):
    request_type = ClientsInterestsRequest

    def handle(self, request, arguments, ctx, store):
        ctx["nclients"] = len(arguments.client_ids)
        return {cid: get_interests(store, cid) for cid in arguments.client_ids}, OK


class OnlineScoreRequest(RequestBase):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    vl = [("first_name", "last_name"), ("phone", "email"), ("gender", "birthday")]

    def validate_list(self):
        for res in self.vl:
            v = list(set(self.request.keys()) & set(res))
            if len(v) == 2:
                self.vl_check = True
            else:
                err = "arguments: Required %s" % str(res)
                self.errors.append(err)
        if self.vl_check:
            self.vl_check = False
            return True
        return False

    def is_valid(self):
        default_valid = super(OnlineScoreRequest, self).is_valid()
        if not default_valid:
            return default_valid
        return self.validate_list()


class OnlineScoreHandler(RequestHandler):
    request_type = OnlineScoreRequest

    def handle(self, request, arguments, ctx, store):
        if request.is_admin:
            score = 42
        else:
            score = get_score(
                store,
                arguments.phone,
                arguments.email,
                arguments.birthday,
                arguments.gender,
                arguments.first_name,
                arguments.last_name,
            )

        ctx["has"] = [
            name
            for name, field in self.request_type.fields.items()
            if getattr(arguments, name, None) is not None
        ]
        return {"score": score}, OK


class MethodRequest(RequestBase):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512(
            datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT
        ).hexdigest()
    else:
        digest = hashlib.sha512(
            str(request.account) + str(request.login) + SALT
        ).hexdigest()
    if digest == request.token:
        return True
    return False


def r_convert(req):
    try:
        return eval(req)
    except:
        return req

def method_handler(request, ctx, store):
    methods_map = {
        "online_score": OnlineScoreHandler,
        "clients_interests": ClientsInterestsHandler,
    }
    if not bool(request["body"]):
        return None, INVALID_REQUEST
    method_request = MethodRequest(r_convert(request["body"]))
    logging.info("Check validate method request")
    if not method_request.is_valid():
        return method_request.errfmt(), INVALID_REQUEST
    logging.info("Check auth")
    if not check_auth(method_request):
        return None, FORBIDDEN
    handler_cls = methods_map.get(method_request.method)
    if not handler_cls:
        return "Method Not Found", NOT_FOUND
    response, code = handler_cls().validate_handle(
        method_request, handler_cls.request_type(method_request.arguments), ctx, store
    )
    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {"method": method_handler}
    store = None

    def get_request_id(self, headers):
        return headers.get("HTTP_X_REQUEST_ID", uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers["Content-Length"]))
            request = json.loads(json.dumps(data_string))
        except:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path](
                        {"body": request, "headers": self.headers}, context, self.store
                    )
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r))
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(
        filename=opts.log,
        level=logging.INFO,
        format="[%(asctime)s] %(levelname).1s %(message)s",
        datefmt="%Y.%m.%d %H:%M:%S",
    )
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
