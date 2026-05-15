
from datetime import datetime, timezone, timedelta
from conn import run_query
import hashlib, secrets

def EmailVerificationToken(user_id):
    raw_token = secrets.token_urlsafe(32) # attached to link
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest() # store in db
    token_id = secrets.token_hex(16) # attached to link

    expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)

    response = run_query("""
            INSERT INTO access_token
              (token_id,user_id,token_hash,token_type,expires_at)    
              VALUES
              (%s,%s,%s,%s,%s)
            """,
            (token_id,user_id,token_hash,'email_verify',expires_at))
    
    token = run_query("SELECT * FROM access_token WHERE user_id = %s", (response, ), fetch="one")

    if response is None and token is None:
        return False

    return token
