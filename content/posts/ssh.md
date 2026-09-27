---
title: SSH
url: /posts/ssh/
draft: false
source_group: 自瞄
source_file: 自瞄/SSH.md
showtoc: true
aliases:
- /posts/1970/01/ssh/
---

## 微机端配置



**1\.确认网络接口名称**

```Plain Text
ip a
```

找到连接电脑的以太网接口,常见名称有eth0,eno1,enp3s0,enp3s0,enx状态应为up且

`LOWER_UP`（已连接网线），但可能没有 IPv4 地址。

假设接口名为 `eno1`，下文均以 `eno1` 为例，实际操作请替换。



**2\.编辑netplan配置文件**

Ubantu22\.04使用netplan管理网络

```Plain Text
ls /etc/netplan/
```

通常会有一个\.yaml文件,备份并编辑它们

```Plain Text
sudo cp /etc/netplan/01-network-manager-all.yaml /etc/netplan/01-network-manager-all.yaml.bak
sudo nano /etc/netplan/01-network-manager-all.yaml
```

将内容修改为\(锁进必须使用空格,不能使用Tab\)

```YAML
network:
  version: 2
  renderer: NetworkManager   # 如果原文件有这行则保留，没有可不写
  ethernets:
    eno1:
      dhcp4: no
      addresses:
        - 192.168.137.3/24      # 静态 IP
      routes:
        - to: default
          via: 192.168.137.1    # 网关指向 Windows 共享网卡的 IP
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]   # DNS
```

保存退出\(nano: `Ctrl+O` 回车，`Ctrl+X`\)



**3\.应用配置**

```Plain Text
sudo netplan aply
```

无报错则静态IP已生效,且重启后依然保留









**4\.验证网络连通性**

```Plain Text
ip a show eno1       # 确认 IP 已变为 192.168.137.3
ping 192.168.137.1   # 测试与 Windows 电脑的连通性
ping 8.8.8.8         # 测试外网连通性
```







**5\.安装并启动SSH服务**

```Plain Text
sudo ufw allow 22
```



或使用firewalld: 

```Plain Text
sudo firewall-cmd --add-service=ssh --permanent
sudo firewall-cmd --reload
```







r

## **Windows电脑端配置**

**1\.为连接微机的网卡设置静态IP**

1. 打开 控制面板 → 网络和共享中心 → 更改适配器设置。

2. 右键点击连接微机的网卡（如“以太网”），选择 属性。

3. 双击 Internet 协议版本 4 \(TCP/IPv4\)。

4. 选择 使用下面的 IP 地址：

    - IP 地址：`192.168.137.1`

    - 子网掩码：`255.255.255.0`

    - 默认网关：留空

    - 首选 DNS：可留空或填 `8.8.8.8`

5. 点击 确定 保存。





**2\.启用 Internet 连接共享（ICS）**

1. 回到该网卡的 属性 窗口，切换到 共享 选项卡。

2. 勾选 允许其他网络用户通过此计算机的 Internet 连接来连接。

3. 在 家庭网络连接 下拉框中，选择电脑用于上网的网卡（如 “WLAN”）。

4. 点击 确定。

    - 如果系统提示该网卡 IP 将被改为 `192.168.137.1`，直接确认即可（与手动设置一致）。

    - 最终确保该网卡 IP 为 `192.168.137.1`。



**3\.检查 Windows 防火墙**

通常 ICS 会自动配置转发规则，但若遇到问题可暂时关闭防火墙测试：

打开 Windows 安全中心 → 防火墙和网络保护 → 暂时关闭专用网络防火墙（测试后记得重新开启）。





**4\.确认 OpenSSH 客户端已安装**

Windows 10/11 一般自带，可在 CMD 或 PowerShell 中检查：

powershell

ssh \-V

若未安装，通过 设置 → 应用 → 可选功能 → 添加功能 搜索 “OpenSSH 客户端” 安装。





**5\.创建或编辑SSH配置文件**

- 打开文件资源管理器，地址栏输入 `%USERPROFILE%\.ssh` 并回车。

- 如果 `.ssh` 文件夹不存在，手动创建（或执行 `mkdir %USERPROFILE%\.ssh`）。

- 在文件夹内新建或编辑 `config` 文件（无扩展名）。





**6\.添加主机条目**

根据你的 Ubuntu 信息（IP=`192.168.137.3`，用户名=`arm`），添加：

```Plain Text
Host ubuntu-arm
    HostName 192.168.137.3
    User arm
    Port 22
    IdentityFile ~/.ssh/id_rsa   # 可选，如果使用密钥登录
```
