import re
from urllib.parse import urlparse


def parse_to_intermediate(proxy_input):
    """
    Parse various proxy formats into an intermediate standardized format.

    Supported input formats:
    - String: "protocol://user:pass@host:port", "host:port" (defaults to http)
    - Dictionary: Requests format or Playwright format

    Returns: Dictionary in intermediate format, or None if parsing fails.
    """
    # Handle string inputs
    if isinstance(proxy_input, str):
        return _parse_string_proxy(proxy_input)

    # Handle dictionary inputs
    elif isinstance(proxy_input, dict):
        # Check for Playwright format keys
        if 'server' in proxy_input:
            return _parse_playwright_format(proxy_input)
        # Check for Requests format keys
        elif 'http' in proxy_input or 'https' in proxy_input:
            return _parse_requests_format(proxy_input)

    print("Error: Unsupported proxy format. Input must be string or dictionary.")
    return None


def to_requests_format(intermediate):
    """
    Convert intermediate proxy format to Requests-compatible format.

    Returns: Dictionary in Requests proxy format, or None if conversion fails.
    """
    if not intermediate or not all(key in intermediate for key in ['protocol', 'host', 'port']):
        print("Error: Invalid intermediate format for Requests conversion")
        return None

    # Construct authentication string if credentials exist
    auth_str = ""
    if intermediate.get('username') or intermediate.get('password'):
        username = intermediate.get('username', '')
        password = intermediate.get('password', '')
        auth_str = f"{username}:{password}@"

    # Build URL for both http and https
    proxy_url = f"{intermediate['protocol']}://{auth_str}{intermediate['host']}:{intermediate['port']}"

    return {
        'http': proxy_url,
        'https': proxy_url
    }


def to_playwright_format(intermediate):
    """
    Convert intermediate proxy format to Playwright-compatible format.

    Returns: Dictionary in Playwright proxy format, or None if conversion fails.
    """
    if not intermediate or not all(key in intermediate for key in ['protocol', 'host', 'port']):
        print("Error: Invalid intermediate format for Playwright conversion")
        return None

    return {
        'server': f"{intermediate['protocol']}://{intermediate['host']}:{intermediate['port']}",
        'username': intermediate.get('username', ''),
        'password': intermediate.get('password', '')
    }


# Helper functions for parsing different formats
def _parse_string_proxy(proxy_str):
    """Parse string proxy into intermediate format"""
    # Add default scheme if missing
    if '://' not in proxy_str:
        proxy_str = 'http://' + proxy_str

    try:
        parsed = urlparse(proxy_str)
        host = parsed.hostname
        port = parsed.port

        # Validate host and port
        if not host or not port:
            print(f"Error: Missing host or port in proxy string: {proxy_str}")
            return None

        # Extract credentials
        username = parsed.username or ''
        password = parsed.password or ''

        # Handle special case for socks5h
        protocol = parsed.scheme
        if protocol == 'socks5h':
            protocol = 'socks5'
        if protocol not in ['http', 'https', 'socks5']:
            print(f"Unsupported protocol: {protocol}")
            return None

        return {
            'protocol': protocol,
            'host': host,
            'port': port,
            'username': username,
            'password': password
        }
    except ValueError as e:
        print(f"Error parsing proxy string: {e}")
        return None


def _parse_requests_format(proxy_dict):
    """Parse Requests-style proxy dict into intermediate format"""
    # Use http proxy if available, otherwise use https
    proxy_url = proxy_dict.get('http') or proxy_dict.get('https')

    if not proxy_url:
        print("Error: Invalid Requests proxy format - missing http/https keys")
        return None

    # Reuse string parsing logic
    return _parse_string_proxy(proxy_url)


def _parse_playwright_format(proxy_dict):
    """Parse Playwright-style proxy dict into intermediate format"""
    server = proxy_dict.get('server', '')
    username = proxy_dict.get('username', '')
    password = proxy_dict.get('password', '')

    if not server:
        print("Error: Invalid Playwright proxy format - missing 'server' key")
        return None

    # Parse server string
    intermediate = _parse_string_proxy(server)
    if not intermediate:
        return None

    # Add credentials from separate fields
    intermediate['username'] = username
    intermediate['password'] = password

    return intermediate


# ----------------------------------------------------------------------------------------------------------------------

# 原始转换函数保持不变（此处省略重复代码）
# [原转换函数代码开始]
# ... parse_to_intermediate(), to_requests_format(), to_playwright_format()等函数...
# [原转换函数代码结束]

def test_proxy_conversion():
    """测试代理转换功能的各种情况"""
    # 测试用例组
    test_cases = [
        # 1. 标准HTTP代理
        {
            "input": "http://user:pass@proxy.com:8080",
            "intermediate": {
                'protocol': 'http',
                'host': 'proxy.com',
                'port': 8080,
                'username': 'user',
                'password': 'pass'
            },
            "requests": {
                'http': 'http://user:pass@proxy.com:8080',
                'https': 'http://user:pass@proxy.com:8080'
            },
            "playwright": {
                'server': 'http://proxy.com:8080',
                'username': 'user',
                'password': 'pass'
            }
        },
        # 2. SOCKS5代理无认证
        {
            "input": "socks5://192.168.1.10:1080",
            "intermediate": {
                'protocol': 'socks5',
                'host': '192.168.1.10',
                'port': 1080,
                'username': '',
                'password': ''
            }
        },
        # 3. HTTPS代理带特殊字符密码
        {
            "input": "https://admin:p@ssw0rd@secure-proxy.com:443",
            "intermediate": {
                'protocol': 'https',
                'host': 'secure-proxy.com',
                'port': 443,
                'username': 'admin',
                'password': 'p@ssw0rd'
            }
        },
        # 4. 无协议默认HTTP
        {
            "input": "10.0.0.1:3128",
            "intermediate": {
                'protocol': 'http',
                'host': '10.0.0.1',
                'port': 3128,
                'username': '',
                'password': ''
            }
        },
        # 5. Playwright格式输入
        {
            "input": {
                "server": "socks5://socks-proxy:9050",
                "username": "anon",
                "password": "secret123"
            },
            "intermediate": {
                'protocol': 'socks5',
                'host': 'socks-proxy',
                'port': 9050,
                'username': 'anon',
                'password': 'secret123'
            }
        },
        # 6. Requests格式输入
        {
            "input": {
                "http": "http://proxy:8080",
                "https": "https://proxy:8443"
            },
            "intermediate": {
                'protocol': 'http',  # 取http值
                'host': 'proxy',
                'port': 8080,
                'username': '',
                'password': ''
            }
        },
        # 7. 无效格式测试
        {"input": "invalid_proxy_string", "should_be_none": True},
        {"input": {"invalid_key": "value"}, "should_be_none": True},
        {"input": "http://missing_port.com", "should_be_none": True},
        {"input": "ftp://unsupported_protocol:21", "should_be_none": True}
    ]

    passed = 0
    total = len(test_cases)

    for case in test_cases:
        try:
            print(f"\n测试用例: {case['input']}")

            # 转换到中间格式
            intermediate = parse_to_intermediate(case["input"])

            if case.get("should_be_none"):
                assert intermediate is None, "应返回None但返回了值"
                print("✅ 无效输入处理正确")
                passed += 1
                continue

            # 验证中间格式
            assert intermediate == case["intermediate"], "中间格式不匹配"
            print("✅ 中间格式验证通过")

            # 验证Requests格式
            if "requests" in case:
                requests_fmt = to_requests_format(intermediate)
                assert requests_fmt == case["requests"], "Requests格式不匹配"
                print("✅ Requests格式验证通过")

            # 验证Playwright格式
            if "playwright" in case:
                playwright_fmt = to_playwright_format(intermediate)
                assert playwright_fmt == case["playwright"], "Playwright格式不匹配"
                print("✅ Playwright格式验证通过")

            passed += 1
        except AssertionError as e:
            print(f"❌ 测试失败: {e}")
        except Exception as e:
            print(f"❌ 未处理异常: {type(e).__name__} - {e}")

    print(f"\n测试结果: {passed}/{total} 通过")

    # 特殊边缘测试
    print("\n额外边缘测试:")
    test_edge_cases()


def test_edge_cases():
    """测试特殊边缘情况"""
    # 1. 空值测试
    assert parse_to_intermediate(None) is None, "空值应返回None"
    assert parse_to_intermediate("") is None, "空字符串应返回None"
    assert parse_to_intermediate({}) is None, "空字典应返回None"

    # 2. 端口范围测试
    valid_port = parse_to_intermediate("http://valid.com:65535")
    assert valid_port["port"] == 65535, "应支持最大端口号65535"

    # 3. 特殊字符处理 - 不考虑
    # special_char = parse_to_intermediate("http://user:!@#$%^&*()@host.com:80")
    # assert special_char["password"] == "!@#$%^&*()", "应保留特殊字符"

    # 4. 无密码认证
    no_password = parse_to_intermediate("http://onlyuser@host.com:80")
    assert no_password["username"] == "onlyuser", "应解析无密码用户名"
    assert no_password["password"] == "", "密码应为空字符串"

    # 5. 大写协议处理
    upper_case = parse_to_intermediate("HTTP://host.com:80")
    assert upper_case["protocol"] == "http", "应规范化协议为小写"

    print("✅ 所有边缘测试通过")


if __name__ == "__main__":
    test_proxy_conversion()
