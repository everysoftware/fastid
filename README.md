# FastAPI Template

A production-ready template for FastAPI projects ⚡

## Features

Main features of this template:

- Safe and secure **JWT Authentication** with RSA Encryption (access + refresh tokens)
- Simple and extendable **RBAC** (supports user & superuser roles)
- Powerful **user management** for superusers
- Limit-offset **pagination** with sorting
- Well-designed **architecture** & **file-structure** with SOLID & patterns applying
- Fast **deployment** with Docker, Makefile, gunicorn & pre-commit
- **Test framework** for faster test-writing with examples

## Installation

1. Clone the repository:

```bash
git clone https://github.com/everysoftware/fastapi-template
```

2. Generate RSA keys:

```bash
openssl genrsa -out certs/private.pem 2048
openssl rsa -in certs/private.pem -pubout -out certs/public.pem
```

3. Create a `.env` file. Use the `.env.example` as a reference.
4. Run the application:

```bash
make up
```

**Made with love ❤️**
