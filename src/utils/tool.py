# -*- coding: utf-8 -*-
"""
    utils.tool
    ~~~~~~~~~~

    Some tool classes and functions.

    :copyright: (c) 2019 by staugur.
    :license: BSD 3-Clause, see LICENSE for more details.
"""

import hmac
import hashlib
from uuid import uuid4
from re import compile, IGNORECASE
from time import time
from datetime import datetime
from random import randrange, sample
from redis import from_url
from .log import Logger
from ._compat import string_types, text_type, PY2, urlparse

logger = Logger("sys").getLogger
err_logger = Logger("error").getLogger
comma_pat = compile(r"\s*,\s*")
verticaline_pat = compile(r"\s*\|\s*")
username_pat = compile(r'^[a-zA-Z][0-9a-zA-Z\_]{0,31}$')
point_pat = compile(r'^\w{1,9}\.?\w{1,9}$')
url_pat = compile(
    r'^(?:http)s?://'
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
    r'localhost|'
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    r'(?::\d+)?'
    r'(?:/?|[/?]\S+)$', IGNORECASE
)
er_group_pat = compile(r",(&&|\|\|),")
er_pat = compile(r'(&&|\|\||!)')


def rsp(*args):
    return "picbed:" + ":".join(map(str, args))


def md5(text):
    if not PY2 and isinstance(text, text_type):
        text = text.encode("utf-8")
    return hashlib.md5(text).hexdigest()


def sha1(text):
    if not PY2 and isinstance(text, text_type):
        text = text.encode("utf-8")
    return hashlib.sha1(text).hexdigest()


def sha256(text):
    if isinstance(text, text_type):
        text = text.encode("utf-8")
    return hashlib.sha256(text).hexdigest()


def hmac_sha256(key, text):
    if PY2 and isinstance(key, text_type):
        key = key.encode("utf-8")
    if not PY2 and isinstance(key, text_type):
        key = key.encode("utf-8")
    if not PY2 and isinstance(text, text_type):
        text = text.encode("utf-8")
    return hmac.new(key=key, msg=text, digestmod=hashlib.sha256).hexdigest()


def get_current_timestamp(is_float=False):
    return time() if is_float else int(time())


def create_redis_engine(redis_url=None):
    from config import REDIS
    return from_url(redis_url or REDIS, decode_responses=True)


def gen_rnd_filename(fmt):
    if fmt == "time1":
        return int(round(time() * 1000))
    elif fmt == "time2":
        return "%s%s" % (
            int(round(time() * 1000)), str(randrange(1000, 10000))
        )
    elif fmt == "time3":
        return "%s%s" % (
            datetime.now().strftime('%Y%m%d%H%M%S'),
            str(randrange(1000, 10000))
        )


def get_today(fmt="%Y/%m/%d"):
    return datetime.now().strftime(fmt)


def allowed_file(filename, suffix=None):
    suffix = set(suffix or ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'])
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in suffix


def parse_valid_comma(s):
    if isinstance(s, string_types):
        return [i for i in comma_pat.split(s) if i]


def parse_valid_verticaline(s):
    if isinstance(s, string_types):
        return [i for i in verticaline_pat.split(s) if i]


def is_true(value):
    if value and value in (True, "True", "true", "on", 1, "1", "yes"):
        return True
    return False


def ListEqualSplit(l, n=5):
    return [l[i:i+n] for i in range(0, len(l), n)]


def generate_random(length=6):
    code_list = []
    for i in range(10):  # 0-9数字
        code_list.append(str(i))
    for i in range(65, 91):  # A-Z
        code_list.append(chr(i))
    for i in range(97, 123):  # a-z
        code_list.append(chr(i))

    myslice = sample(code_list, length)
    return ''.join(myslice)


def format_upload_src(fmt, value):
    if fmt and isinstance(fmt, string_types):
        if point_pat.match(fmt):
            if "." in fmt:
                fmts = fmt.split('.')
                return {fmts[0]: {fmts[1]: value}}
            else:
                return {fmt: value}
    return dict(src=value)


class Attribution(dict):

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)


class Attribute(dict):

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            return ''


def get_origin(url):
    """从url提取出符合CORS格式的origin地址"""
    parsed_uri = urlparse(url)
    return '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)


def check_origin(addr):
    """Check whether UrlAddr is in a valid host origin, for example::

        http://ip:port
        https://abc.com
    """
    if addr and isinstance(addr, string_types):
        try:
            origin = get_origin(addr)
        except (ValueError, TypeError, Exception):
            return False
        else:
            return url_pat.match(origin)
    return False


def check_ip(ip_str):
    sep = ip_str.split('.')
    if len(sep) != 4:
        return False
    for x in sep:
        try:
            int_x = int(x)
            if int_x < 0 or int_x > 255:
                return False
        except ValueError:
            return False
    return True


def gen_uuid():
    return uuid4().hex


class Relation:
    """将符号替换为内置方法
    1. && = _and
    2. || = _or
    3. !  = _not
    4. << = _in
    5. >> = _notin
    """

    @classmethod
    def signal2func(cls, s):
        if s == "&&":
            return cls._and
        elif s == "||":
            return cls._or
        elif s == "!":
            return cls._not
        elif s == "<<":
            return cls._in
        elif s == ">>":
            return cls._notin
        else:
            raise ValueError

    @staticmethod
    def _and(a1, a2):
        return a1 and a2

    @staticmethod
    def _or(o1, o2):
        return o1 or o2

    @staticmethod
    def _not(n):
        return not n

    @staticmethod
    def _in(src, dst):
        return src in dst

    @staticmethod
    def _notin(src, dst):
        return src not in dst


def parse_er(er):
    """解析er规则，其格式是opt1&&opt2||opt3，前面最多一个!，后面不能有符号"""
    if er:
        ers = er_group_pat.split(er)
        rules = []
        for er in ers:
            if er == "&&":
                rules.append(Relation._and)
            elif er == "||":
                rules.append(Relation._or)
            else:
                r = []
                for i in er_pat.split(er):
                    try:
                        f = Relation.signal2func(i)
                    except ValueError:
                        if i:
                            if i in ("ip", "ep", "origin", "method"):
                                r.append(i)
                            else:
                                raise
                    else:
                        r.append(f)
                if r:
                    rules.append(r)
        #: 合法的rules是至少三个元素的list
        if len(ers) == 1:
            rules = rules[0]
        return rules


def parse_ir(ir):
    """解析ir规则，其格式是opt1:>>,opt2:<<"""
    if ir:
        return {
            i.split(":")[0]: i.split(":")[1]
            for i in parse_valid_comma(ir)
            if i
        }
