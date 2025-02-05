
## HD 分层钱包
当前主流的 HD 分层钱包主要涉及三个 BIP：
- BIP32：分层确定性钱包（HD Wallets），从一个种子（seed）派生词出一颗树状的钱包私钥
- BIP-39：助记词（Mnemonic）标准，将 seed 映射成一系列助记词，帮助用户记忆
- BIP44：定义分层路径的规范，标准化派生的规范，当前已经定义的 [cointype](https://trustwallet.github.io/docc/documentation/walletcore/cointype/)


运行 HD 钱包示例
```shell
pip3 install -r requirements.txt
python3 HD.py
```