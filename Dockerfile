# syntax=docker/dockerfile:1

# tick-task -- LAN-mode server image.
#
# This image serves the deployment shape docs/SPEC.md defines as MUST-API-002b:
# the API bound to 0.0.0.0 behind token authentication, explicitly opted into.
# It does NOT replace the desktop distribution path -- docs/DECISIONS.md chose
# PyInstaller for handing the app to an end user, and that decision stands.
# Container and PyInstaller are peer formats in the HEE release system's
# packaging matrix (prompts/hee/docs/MODULES/RELEASE_SYSTEM.md), not
# alternatives to each other.
#
# API only: the app mounts no static files and / redirects to /docs. The vite
# frontend is not served from this image.

ARG PYTHON_VERSION=3.12

# --- build -------------------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# The project version is dynamic via setuptools-scm, which reads git. The build
# context has no .git, so without this the install fails outright. CI passes the
# real version; the default keeps a bare "docker build ." working.
ARG VERSION=0.0.0+docker
ENV SETUPTOOLS_SCM_PRETEND_VERSION=${VERSION}

WORKDIR /src
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY alembic.ini ./
COPY alembic/ ./alembic/

RUN python -m pip install --upgrade pip setuptools wheel \
 && python -m pip install .

# --- runtime -----------------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:${PATH}"

# A real service account, not root and not a world-writable directory.
RUN groupadd --system --gid 10001 tick-task \
 && useradd --system --uid 10001 --gid tick-task --home-dir /var/lib/tick-task \
      --shell /usr/sbin/nologin tick-task

COPY --from=builder /opt/venv /opt/venv
COPY --chown=root:root docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod 0755 /usr/local/bin/docker-entrypoint.sh

# 0750: owner rwx, group rx, world nothing.
RUN install -d -o tick-task -g tick-task -m 0750 /var/lib/tick-task
VOLUME ["/var/lib/tick-task"]

# 0.0.0.0 is not a policy choice here -- a container is unreachable otherwise.
# The token guard in the entrypoint is what keeps that bind from being open.
ENV TICK_TASK_HOST=0.0.0.0 \
    TICK_TASK_PORT=7000 \
    TICK_TASK_LAN_MODE=true \
    TICK_TASK_DATA_DIR=/var/lib/tick-task \
    TICK_TASK_DATABASE_URL=sqlite+aiosqlite:////var/lib/tick-task/tick-task.db

USER tick-task
WORKDIR /var/lib/tick-task
EXPOSE 7000

# The health endpoint is authenticated: require_lan_token guards every route
# when lan_mode is on, so an unauthenticated probe gets 401 and the container
# would report unhealthy forever. Send the token the same way a client does.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import os,sys,urllib.request as u; r=u.Request('http://127.0.0.1:7000/api/v1/health', headers={'Authorization': 'Bearer ' + os.environ.get('TICK_TASK_LAN_TOKEN','')}); sys.exit(0 if u.urlopen(r, timeout=4).status == 200 else 1)"

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["tick-task"]
