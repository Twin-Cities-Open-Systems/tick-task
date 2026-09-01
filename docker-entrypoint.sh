#!/bin/sh
# tick-task container entrypoint -- refuses to serve an unauthenticated bind.
#
# The image sets TICK_TASK_HOST=0.0.0.0 because a container is unreachable
# otherwise. docs/SPEC.md MUST-API-002b requires that any non-localhost bind be
# token-authenticated, so starting without a token would ship exactly the
# exposure the spec forbids. Fail closed instead, and say why.
#
# This guard is deliberately independent of the application's own lan_mode
# enforcement: it holds whether or not the auth work in PR 43 has merged, so
# merge order cannot leave an open image.

set -eu

if [ -z "${TICK_TASK_LAN_TOKEN:-}" ]; then
    echo "CRITICAL: TICK_TASK_LAN_TOKEN is not set." >&2
    echo "" >&2
    echo "This image binds ${TICK_TASK_HOST:-0.0.0.0}:${TICK_TASK_PORT:-7000}, which docs/SPEC.md" >&2
    echo "(MUST-API-002b) requires to be token-authenticated. Refusing to start" >&2
    echo "rather than serve unauthenticated on every interface." >&2
    echo "" >&2
    echo "Generate a token and pass it in, for example:" >&2
    echo "  docker run -e TICK_TASK_LAN_TOKEN=\"\$(python3 -c 'import secrets;print(secrets.token_urlsafe(32))')\" ..." >&2
    exit 78   # EX_CONFIG
fi

# Token present but empty-after-trim is the same failure wearing a disguise.
case "${TICK_TASK_LAN_TOKEN}" in
    *[!\ ]*) : ;;
    *) echo "CRITICAL: TICK_TASK_LAN_TOKEN is set but blank." >&2; exit 78 ;;
esac

exec "$@"
