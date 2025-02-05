"""Creates a random API key
"""
import secrets
import string

def generate_secure_random_key(length: int) -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

# Example usage:
secure_key = generate_secure_random_key(16)
print(secure_key)
