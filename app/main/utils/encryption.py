import hashlib
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
from app.application import app
import logging

k = '2018_11_21_pai_l'.encode('utf-8')
iv = b'2018112120181121'


def md5_encrypt(param):
    """
    md5密码加密方式
    :param param
    :return: str
    """
    m = hashlib.md5()
    m.update(param.encode("UTF-8"))

    return m.hexdigest()


def aes_encrypt(text, key=None):
    """
    aes加密token
    :param text
    :return: str
    """
    key = k if key is None else key

    length = AES.block_size
    text = text.encode('utf-8')
    count = len(key)
    if count < length:
        add = length-count
        key +=('\0' * add).encode('utf-8')

    cipher = AES.new(key, AES.MODE_CBC, iv)

    count = len(text)
    # 加密函数，如果text不足16位就用空格补足为16位，
    # 如果大于16当时不是16的倍数，那就补足为16的倍数。
    if count < length:
        add = length - count
        # \0 backspace
        text += ('\0' * add).encode('utf-8')
    elif count > length:
        add = (length - (count % length))
        text += ('\0' * add).encode('utf-8')

    cipher_text = cipher.encrypt(text)

    # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
    # 所以这里统一把加密后的字符串转化为16进制字符串
    return b2a_hex(cipher_text)


def aes_decrypt(text, key=None):

    """
    aes解密token
    :param text
    :return: str
    """

    key = k if key is None else key
    length = AES.block_size
    text = text.encode('utf-8')
    count = len(key)
    if count < length:
        add = length - count
        key += ('\0' * add).encode('utf-8')

    cipher = AES.new(key, AES.MODE_CBC, iv)
    # text 存在随意输入风险
    try:
        plain_text = cipher.decrypt(a2b_hex(text))
    except Exception as e:
        logging.error(e)
        return None
    # 解密后，去掉补足的空格用strip() 去掉
    return bytes.decode(plain_text).rstrip('\0')

def decrypt_id(text,key=None,user_id=None):
    if app.config['ID_ENCRYPT'] is False:
        return text
    return aes_decrypt(text,key)[:-len(user_id)]

# e = encrypt("userID_12_1542764414")  # 加密
# d = aes_decrypt("cd2830827b3df75d15128bc27f95d802")  # 解密
# print("加密:", e)
# print("解密:", d)
