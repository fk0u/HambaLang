# HambaLang — interpreter, compiler, HambaVM v4 (+ toolchain legacy v3)
FROM python:3.12-slim

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -e ".[http]" && rm -rf web

ENTRYPOINT ["hambalang"]
CMD ["run", "examples/full_demo.hl", "--fast"]
