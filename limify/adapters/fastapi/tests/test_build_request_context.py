from types import SimpleNamespace
from limify.adapters.fastapi.context import build_request_context


class MockRequest:
    def __init__(self, method="GET", path="/", headers=None, client_host=None, state=None,):
        self.method = method
        self.url = SimpleNamespace(path=path)
        self.headers = headers or {}
        self.client = SimpleNamespace(host=client_host) if client_host else None
        self.state = state or SimpleNamespace()


#x-forwarded-for should take priority
def test_build_context_uses_x_forwarded_for():
    request = MockRequest(
        headers={"x-forwarded-for": "1.2.3.4, 5.6.7.8"},
        client_host="9.9.9.9"
    )

    context = build_request_context(request)

    assert context.client_ip == "1.2.3.4"


#Fallback to request.client.host
def test_build_context_falls_back_to_client_host():
    request = MockRequest(
        headers={},
        client_host="9.9.9.9"
    )

    context = build_request_context(request)

    assert context.client_ip == "9.9.9.9"


#Fallback to "unknown"
def test_build_context_falls_back_to_unknown():
    request = MockRequest(
        headers={},
        client_host=None
    )

    context = build_request_context(request)

    assert context.client_ip == "unknown"


#Extract user_id
def test_build_context_extracts_user_id():
    state = SimpleNamespace(user_id=42)
    request = MockRequest(state=state)

    context = build_request_context(request)

    assert context.user_id == 42


#Extract org_id
def test_build_context_extracts_org_id():
    state = SimpleNamespace(org_id="acme")
    request = MockRequest(state=state)

    context = build_request_context(request)

    assert context.org_id == "acme"


#Extract API key from header
def test_build_context_extracts_api_key():
    request = MockRequest(
        headers={"x-api-key": "abc123"}
    )

    context = build_request_context(request)

    assert context.api_key == "abc123"


#Full integration case
def test_build_context_full_case():
    state = SimpleNamespace(user_id=1, org_id="org-1")
    request = MockRequest(
        method="POST",
        path="/items",
        headers={
            "x-forwarded-for": "10.0.0.1",
            "x-api-key": "key-123"
        },
        client_host="127.0.0.1",
        state=state
    )

    context = build_request_context(request)

    assert context.method == "POST"
    assert context.path == "/items"
    assert context.client_ip == "10.0.0.1"
    assert context.user_id == 1
    assert context.org_id == "org-1"
    assert context.api_key == "key-123"