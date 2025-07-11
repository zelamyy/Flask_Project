from werkzeug.security import generate_password_hash

password = "teacher123"  # You can change this to any password
hashed = generate_password_hash(password)

print("Your hashed password is:\n", hashed)
