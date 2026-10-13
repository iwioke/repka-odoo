FROM odoo:18.0-20251222@sha256:d97b033cc20156af2bbbdf29c8f7a127a4c25e60ed5152758af815164527adfb

USER root
COPY requirements-oca.txt /tmp/requirements-oca.txt
RUN python3 -m pip install --break-system-packages --no-cache-dir --no-deps --require-hashes -r /tmp/requirements-oca.txt \
    && rm /tmp/requirements-oca.txt
COPY scripts/container/entrypoint.sh /usr/local/bin/repka-entrypoint
RUN chmod 0755 /usr/local/bin/repka-entrypoint
ENTRYPOINT ["/usr/local/bin/repka-entrypoint"]
