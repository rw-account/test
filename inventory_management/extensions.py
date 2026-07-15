from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=[])

# للحماية من  CSRF 

from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()