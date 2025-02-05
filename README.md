HD 分层钱包的示例实现

### HD 分层钱包原理
#### BIP32（分层确定性钱包）
BIP32 定义了一种从单个主密钥派生出一系列子密钥的方法。通过使用一个主密钥和一个链码，可以派生出任意数量的子密钥，这些子密钥可以进一步派生出更多的子密钥，形成一个树形结构。派生过程分为硬化派生和非硬化派生：
硬化派生：使用父私钥和索引进行派生，安全性更高，即使某个子密钥泄露，也不会影响其他子密钥和父密钥。
非硬化派生：使用父公钥和索引进行派生，可以在不暴露私钥的情况下派生子公钥，适用于需要共享公钥的场景。

#### BIP39（助记词）
BIP39 规定了一种将随机熵转换为易于记忆的助记词的方法。通过生成一定长度的随机熵，计算其哈希值并取校验和，然后将熵和校验和拼接，分割成 11 位的块，每个块对应一个单词，最终形成一个助记词序列。助记词可以方便地备份和恢复钱包。

#### BIP44（多币种分层确定性钱包结构）
BIP44 定义了一种统一的 HD 钱包结构，用于支持多种加密货币。它规定了一个 5 层的派生路径：m / purpose' / coin_type' / account' / change / address_index，其中：
- purpose：固定为 44'，表示使用 BIP44 规范。
- coin_type：表示加密货币的类型，例如比特币为 0'，以太坊为 60'。
- account：表示用户的账户索引。
- change：表示是否为找零地址，0 表示接收地址，1 表示找零地址。
- address_index：表示地址的索引。

当前已经定义的 [cointype](https://trustwallet.github.io/docc/documentation/walletcore/cointype/)

### 代码结构
- wordlist.txt：BIP39 英文单词表，用于生成助记词。
- HD.py：主要代码文件，包含了助记词生成、密钥派生、地址生成等功能的实现。

### 运行示例
#### 步骤 1：克隆仓库
```bash
git clone git@github.com:rayjun/HD-Wallet-explain.git
cd HD-Wallet-explain
```
#### 步骤 2：安装依赖库
```bash
pip3 install -r requirements.txt
````

#### 步骤 3：运行代码
在终端中运行 HD.py 文件：
```bash
python HD.py
```

### 示例输出
```plaintext
生成的助记词: hold decrease auto boss law stadium mobile village situate cactus lend brisk
主密钥: 97e7e5daf9e53aed9cf8b700301b8e564bf1ab4ba668ad8d4ae3266e867ecc41
主链码: 9aebdf8c2157c314fb4eb09dd9679b36675f2f59fbf841b8fc2895d70052c4d6
以太坊派生密钥: 5d71e1df244ec328ff79dcc8043a0434086948fdb4d413909917a82859e13c33
以太坊派生链码: 8f70a1d7dc1919e6e048998dec38e65905fa5466d5291998e81a354e3c123b52
以太坊地址: 0x43cd94dd30c629b4d3aee406a8744516a8b6b6c4
比特币派生密钥: 9cf6752be0490e9e144aba7a6ec01b6b9c3ddbffec7362cc6fd7c90a369675bc
比特币派生链码: 67404089cdc9eb05838eff7387e5e8840c0bd008ecdb81cc480e6387fefcd409
比特币 P2PKH 地址: 14G6tDgEHWZhNy3CM9QxuPcRNNqDPPRhek
```
### 注意事项
上面的代码仅仅是一个示例，不要在生产环境中使用

### 许可证
本项目采用 [MIT 许可证](./LICENSE)。