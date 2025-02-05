import hashlib
import hmac
import os
import math
from ecdsa import SECP256k1, SigningKey, VerifyingKey
import base58
# 从 wordlist.txt 读取单词列表
def load_wordlist(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # 一次性读取所有行并去除换行符
            wordlist = [line.strip() for line in file.readlines()]
        return wordlist
    except FileNotFoundError:
        print(f"错误：未找到 {file_path} 文件。")
        return []
    except Exception as e:
        print(f"读取文件时发生错误：{e}")
        return []

# 加载单词列表
WORD_LIST = load_wordlist('wordlist.txt')

def generate_entropy(strength=128):
    """
    生成指定强度的随机熵
    """
    if strength % 32 != 0:
        raise ValueError("Strength must be divisible by 32")
    num_bytes = strength // 8
    return os.urandom(num_bytes)

def entropy_to_mnemonic(entropy):
    """
    将熵转换为助记词
    """
    entropy_length = len(entropy) * 8
    checksum_length = entropy_length // 32

    # 计算熵的哈希值
    entropy_hash = hashlib.sha256(entropy).digest()
    checksum = bin(int.from_bytes(entropy_hash, byteorder='big'))[2:].zfill(256)[:checksum_length]

    # 将熵和校验和拼接
    entropy_bin = bin(int.from_bytes(entropy, byteorder='big'))[2:].zfill(entropy_length)
    entropy_with_checksum = entropy_bin + checksum

    # 分割成 11 位的块
    chunks = [entropy_with_checksum[i:i + 11] for i in range(0, len(entropy_with_checksum), 11)]

    # 根据块的索引从单词表中选择单词
    mnemonic = [WORD_LIST[int(chunk, 2)] for chunk in chunks]
    return " ".join(mnemonic)


def mnemonic_to_seed(mnemonic, passphrase=""):
    """
    将助记词转换为种子
    """
    salt = "mnemonic" + passphrase
    seed = hashlib.pbkdf2_hmac('sha512', mnemonic.encode('utf-8'), salt.encode('utf-8'), 2048)
    return seed


def generate_master_key(seed):
    """
    从种子生成主密钥和链码
    """
    h = hmac.new(b"Bitcoin seed", seed, hashlib.sha512).digest()
    key = h[:32]
    chain_code = h[32:]
    return key, chain_code


def derive_child_key(parent_key, parent_chain_code, index):
    """
    派生子密钥和链码
    """
    if index >= 2 ** 31:  # 硬化派生
        data = b'\x00' + parent_key + index.to_bytes(4, byteorder='big')
    else:
        # 非硬化派生，需要先计算公钥
        sk = SigningKey.from_string(parent_key, curve=SECP256k1)
        vk = sk.get_verifying_key()
        public_key = b'\x04' + vk.to_string()
        data = public_key + index.to_bytes(4, byteorder='big')

    h = hmac.new(parent_chain_code, data, hashlib.sha512).digest()
    child_key = (int.from_bytes(h[:32], byteorder='big') + int.from_bytes(parent_key, byteorder='big')) % SECP256k1.order
    child_chain_code = h[32:]
    return child_key.to_bytes(32, byteorder='big'), child_chain_code


def derive_key_from_path(master_key, master_chain_code, path):
    """
    根据派生路径派生密钥
    """
    segments = path.split('/')[1:]
    current_key = master_key
    current_chain_code = master_chain_code
    for segment in segments:
        if segment.endswith("'"):
            index = int(segment[:-1]) + 2 ** 31
        else:
            index = int(segment)
        current_key, current_chain_code = derive_child_key(current_key, current_chain_code, index)
    return current_key, current_chain_code


def private_key_to_public_key(private_key):
    """
    将私钥转换为公钥
    """
    sk = SigningKey.from_string(private_key, curve=SECP256k1)
    vk = sk.get_verifying_key()
    return b'\x04' + vk.to_string()


def public_key_to_p2pkh_address(public_key):
    """
    将公钥转换为比特币 P2PKH 地址
    """
    # 计算公钥的 SHA-256 哈希值
    sha256_hash = hashlib.sha256(public_key).digest()
    # 计算 RIPEMD-160 哈希值
    ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
    # 添加版本字节（主网为 0x00）
    versioned_ripemd160 = b'\x00' + ripemd160_hash
    # 计算校验和
    checksum = hashlib.sha256(hashlib.sha256(versioned_ripemd160).digest()).digest()[:4]
    # 拼接版本字节、RIPEMD-160 哈希值和校验和
    address_bytes = versioned_ripemd160 + checksum
    # 进行 Base58 编码
    address = base58.b58encode(address_bytes).decode()
    return address


def private_key_to_ethereum_address(private_key):
    """
    将私钥转换为以太坊地址
    """
    # 从私钥生成公钥
    public_key = private_key_to_public_key(private_key)
    # 去除公钥的前缀字节 0x04
    public_key_without_prefix = public_key[1:]
    # 计算公钥的 Keccak-256 哈希值
    keccak_hash = hashlib.sha3_256(public_key_without_prefix).digest()
    # 取哈希值的后 20 字节
    address_bytes = keccak_hash[-20:]
    # 添加 0x 前缀并转换为十六进制字符串
    ethereum_address = '0x' + address_bytes.hex()
    return ethereum_address


# 示例用法
if __name__ == "__main__":
    try:
        # 生成熵
        entropy = generate_entropy()
        # 熵转换为助记词
        mnemonic = entropy_to_mnemonic(entropy)
        print(f"生成的助记词: {mnemonic}")

        # 助记词转换为种子
        seed = mnemonic_to_seed(mnemonic)

        # 从种子生成主密钥和链码
        master_key, master_chain_code = generate_master_key(seed)
        print(f"主密钥: {master_key.hex()}")
        print(f"主链码: {master_chain_code.hex()}")

        # 定义派生路径
        path = "m/44'/60'/0'/0/0"  # 以太坊派生路径
        # 根据路径派生密钥
        derived_key, derived_chain_code = derive_key_from_path(master_key, master_chain_code, path)
        print(f"以太坊派生密钥: {derived_key.hex()}")
        print(f"以太坊派生链码: {derived_chain_code.hex()}")

        # 私钥转换为以太坊地址
        ethereum_address = private_key_to_ethereum_address(derived_key)
        print(f"以太坊地址: {ethereum_address}")

        path = "m/44'/0'/0'/0/0"  # 比特币派生路径
        # 根据路径派生密钥
        derived_key, derived_chain_code = derive_key_from_path(master_key, master_chain_code, path)
        print(f"比特币派生密钥: {derived_key.hex()}")
        print(f"比特币派生链码: {derived_chain_code.hex()}")
        # 私钥转换为公钥
        public_key = private_key_to_public_key(derived_key)
        # 公钥转换为 P2PKH 地址
        address = public_key_to_p2pkh_address(public_key)
        print(f"比特币 P2PKH 地址: {address}")
    except ValueError as e:
        print(f"错误: {e}")