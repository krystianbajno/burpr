import pytest
from burpr import burpr
from burpr.models.BurpRequest import BurpRequest
from burpr.enums.TransportEnum import TransportEnum
from burpr.enums.ProtocolEnum import ProtocolEnum


class TestBurpRequestParsing:
    """Test suite for parsing complex Burp requests."""
    
    def test_basic_get_request(self):
        """Test parsing basic GET request."""
        request = """GET /api/v1/users HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0

"""
        req = burpr.parse_string(request)
        
        assert req.method == "GET"
        assert req.path == "/api/v1/users"
        assert req.host == "example.com"
        assert req.protocol == ProtocolEnum.HTTP1_1
        assert req.headers["User-Agent"] == "Mozilla/5.0"
        assert req.body == ""
    
    def test_post_with_json_body(self):
        """Test POST request with JSON body and placeholders."""
        request = """POST /api/auth HTTP/2
Host: secure.example.com
Authorization: Bearer %TOKEN%
Content-Type: application/json
Content-Length: 58

{"username": "%USER%", "password": "%PASS%", "remember": true}"""
        
        req = burpr.parse_string(request)
        
        assert req.method == "POST"
        assert req.protocol == ProtocolEnum.HTTP2
        assert req.headers["Authorization"] == "Bearer %TOKEN%"
        assert req.body == '{"username": "%USER%", "password": "%PASS%", "remember": true}'
    
    def test_url_encoded_body(self):
        """Test parsing URL-encoded body."""
        request = """POST /login HTTP/1.1
Host: webapp.com
Content-Type: application/x-www-form-urlencoded
Cookie: session=%SESSION_ID%

username=%USERNAME%&password=%PASSWORD%&csrf=%CSRF_TOKEN%"""
        
        req = burpr.parse_string(request)
        assert req.body == "username=%USERNAME%&password=%PASSWORD%&csrf=%CSRF_TOKEN%"
    
    def test_multipart_form_data(self):
        """Test parsing multipart form data."""
        request = """POST /upload HTTP/1.1
Host: files.example.com
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="test.txt"
Content-Type: text/plain

%FILE_CONTENT%
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="description"

%DESCRIPTION%
------WebKitFormBoundary7MA4YWxkTrZu0gW--"""
        
        req = burpr.parse_string(request)
        assert "multipart/form-data" in req.headers["Content-Type"]
        assert "%FILE_CONTENT%" in req.body
        assert "%DESCRIPTION%" in req.body
    
    def test_complex_headers(self):
        """Test request with many headers."""
        request = """GET /api/data HTTP/1.1
Host: api.example.com:8443
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)
Accept: application/json, text/plain, */*
Accept-Language: en-US,en;q=0.9
Accept-Encoding: gzip, deflate, br
Referer: https://app.example.com/dashboard
X-Requested-With: XMLHttpRequest
X-Custom-Header: %CUSTOM_VALUE%
Authorization: Bearer %TOKEN%
Cookie: session=%SESSION%; tracking=%TRACKING_ID%; preferences=dark_mode

"""
        req = burpr.parse_string(request)
        assert req.host == "api.example.com:8443"
        assert req.headers["Accept"] == "application/json, text/plain, */*"
        assert req.headers["X-Custom-Header"] == "%CUSTOM_VALUE%"
        assert req.headers["Cookie"] == "session=%SESSION%; tracking=%TRACKING_ID%; preferences=dark_mode"
    
    def test_query_parameters_in_path(self):
        """Test GET request with query parameters."""
        request = """GET /search?q=%SEARCH_QUERY%&category=%CATEGORY%&page=%PAGE% HTTP/1.1
Host: search.example.com

"""
        req = burpr.parse_string(request)
        assert req.path == "/search?q=%SEARCH_QUERY%&category=%CATEGORY%&page=%PAGE%"
    
    def test_put_request_with_xml(self):
        """Test PUT request with XML body."""
        request = """PUT /api/config HTTP/1.1
Host: config.example.com
Content-Type: application/xml
Authorization: Basic %BASIC_AUTH%

<?xml version="1.0" encoding="UTF-8"?>
<config>
    <setting name="%SETTING_NAME%">%SETTING_VALUE%</setting>
    <debug>%DEBUG_MODE%</debug>
</config>"""
        
        req = burpr.parse_string(request)
        assert req.method == "PUT"
        assert '<?xml version="1.0" encoding="UTF-8"?>' in req.body
        assert '%SETTING_NAME%' in req.body
    
    def test_delete_request(self):
        """Test DELETE request."""
        request = """DELETE /api/users/%USER_ID% HTTP/2
Host: api.example.com
Authorization: Bearer %TOKEN%
X-Confirmation: %CONFIRMATION_CODE%

"""
        req = burpr.parse_string(request)
        assert req.method == "DELETE"
        assert req.path == "/api/users/%USER_ID%"
        assert req.protocol == ProtocolEnum.HTTP2
    
    def test_patch_with_json_patch(self):
        """Test PATCH request with JSON Patch body."""
        request = """PATCH /api/resource/%RESOURCE_ID% HTTP/1.1
Host: api.example.com
Content-Type: application/json-patch+json
Authorization: Bearer %TOKEN%

[
    {"op": "replace", "path": "/status", "value": "%NEW_STATUS%"},
    {"op": "add", "path": "/tags/-", "value": "%NEW_TAG%"}
]"""
        
        req = burpr.parse_string(request)
        assert req.method == "PATCH"
        assert "json-patch" in req.headers["Content-Type"]
        assert '"op": "replace"' in req.body
    
    def test_headers_without_space_after_colon(self):
        """Test parsing headers without space after colon."""
        request = """GET /test HTTP/1.1
Host:example.com
Authorization:Bearer token123
X-Custom:value

"""
        req = burpr.parse_string(request)
        assert req.headers["Host"] == "example.com"
        assert req.headers["Authorization"] == "Bearer token123"
        assert req.headers["X-Custom"] == "value"
    
    def test_http_vs_https_detection(self):
        """Test HTTP/HTTPS transport detection."""
        # Port 80 should be HTTP
        request1 = """GET /api HTTP/1.1
Host: example.com:80

"""
        req1 = burpr.parse_string(request1)
        assert req1.transport == TransportEnum.HTTP
        
        # Default should be HTTPS
        request2 = """GET /api HTTP/1.1
Host: example.com

"""
        req2 = burpr.parse_string(request2)
        assert req2.transport == TransportEnum.HTTPS
    
    def test_empty_body_post(self):
        """Test POST with empty body."""
        request = """POST /api/trigger HTTP/1.1
Host: example.com
Content-Length: 0

"""
        req = burpr.parse_string(request)
        assert req.method == "POST"
        assert req.body == ""
    
    def test_options_request(self):
        """Test OPTIONS request (CORS preflight)."""
        request = """OPTIONS /api/endpoint HTTP/1.1
Host: api.example.com
Origin: https://app.example.com
Access-Control-Request-Method: POST
Access-Control-Request-Headers: authorization,content-type

"""
        req = burpr.parse_string(request)
        assert req.method == "OPTIONS"
        assert req.headers["Origin"] == "https://app.example.com"


class TestBindMethod:
    """Test the bind functionality."""
    
    def test_bind_in_path(self):
        """Test binding placeholders in path."""
        request = """GET /api/users/%USER_ID%/posts/%POST_ID% HTTP/1.1
Host: example.com

"""
        req = burpr.parse_string(request)
        req.bind("%USER_ID%", "123").bind("%POST_ID%", "456")
        
        assert req.path == "/api/users/123/posts/456"
    
    def test_bind_in_headers(self):
        """Test binding placeholders in headers."""
        request = """GET /api/data HTTP/1.1
Host: api.example.com
Authorization: Bearer %TOKEN%
X-User-ID: %USER_ID%
X-Session: prefix-%SESSION_ID%-suffix

"""
        req = burpr.parse_string(request)
        req.bind("%TOKEN%", "abc123")
        req.bind("%USER_ID%", "42")
        req.bind("%SESSION_ID%", "xyz789")
        
        assert req.headers["Authorization"] == "Bearer abc123"
        assert req.headers["X-User-ID"] == "42"
        assert req.headers["X-Session"] == "prefix-xyz789-suffix"
    
    def test_bind_in_body(self):
        """Test binding placeholders in body."""
        request = """POST /api/auth HTTP/1.1
Host: example.com
Content-Type: application/json

{"username": "%USERNAME%", "password": "%PASSWORD%", "code": "$2FA_CODE$"}"""
        
        req = burpr.parse_string(request)
        req.bind("%USERNAME%", "admin")
        req.bind("%PASSWORD%", "secure123")
        req.bind("$2FA_CODE$", "123456")
        
        assert req.body == '{"username": "admin", "password": "secure123", "code": "123456"}'
    
    def test_bind_multiple_occurrences(self):
        """Test binding same placeholder multiple times."""
        request = """POST /api/test HTTP/1.1
Host: example.com
X-Token: %TOKEN%
Authorization: Bearer %TOKEN%

{"token": "%TOKEN%", "backup_token": "%TOKEN%"}"""
        
        req = burpr.parse_string(request)
        req.bind("%TOKEN%", "secret123")
        
        assert req.headers["X-Token"] == "secret123"
        assert req.headers["Authorization"] == "Bearer secret123"
        assert req.body.count("secret123") == 2
    
    def test_bind_chaining(self):
        """Test method chaining with bind."""
        request = """GET /%PATH% HTTP/1.1
Host: %HOST%

"""
        req = burpr.parse_string(request)
        result = req.bind("%PATH%", "api/v2/users").bind("%HOST%", "example.com")
        
        assert result is req  # Should return self
        assert req.path == "/api/v2/users"
        assert req.headers["Host"] == "example.com"
        assert req.host == "example.com"


class TestCurlParsing:
    """Test curl command parsing."""
    
    def test_basic_curl_get(self):
        """Test basic curl GET command."""
        curl = 'curl https://api.example.com/users'
        req = burpr.from_curl(curl)
        
        assert req.method == "GET"
        assert req.host == "api.example.com"
        assert req.path == "/users"
        assert req.transport == TransportEnum.HTTPS
    
    def test_curl_with_headers(self):
        """Test curl with multiple headers."""
        curl = '''curl -X POST https://api.example.com/data \
            -H "Authorization: Bearer %TOKEN%" \
            -H "Content-Type: application/json" \
            -H "X-Request-ID: %REQUEST_ID%"'''
        
        req = burpr.from_curl(curl)
        
        assert req.method == "POST"
        assert req.headers["Authorization"] == "Bearer %TOKEN%"
        assert req.headers["Content-Type"] == "application/json"
        assert req.headers["X-Request-ID"] == "%REQUEST_ID%"
    
    def test_curl_with_data(self):
        """Test curl with data."""
        curl = 'curl -X POST https://api.example.com/login -d "username=%USER%&password=%PASS%"'
        req = burpr.from_curl(curl)
        
        assert req.method == "POST"
        assert req.body == "username=%USER%&password=%PASS%"
        assert req.headers["Content-Type"] == "application/x-www-form-urlencoded"
    
    def test_curl_with_json_data(self):
        """Test curl with JSON data."""
        curl = '''curl -X PUT https://api.example.com/user/%ID% \
            -H "Content-Type: application/json" \
            -d '{"name": "%NAME%", "email": "%EMAIL%"}'
        '''
        req = burpr.from_curl(curl)
        
        assert req.method == "PUT"
        assert req.path == "/user/%ID%"
        assert req.body == '{"name": "%NAME%", "email": "%EMAIL%"}'
    
    def test_curl_without_protocol(self):
        """Test curl without http/https prefix."""
        curl = 'curl api.example.com/test'
        req = burpr.from_curl(curl)
        
        assert req.host == "api.example.com"
        assert req.path == "/test"
        assert req.transport == TransportEnum.HTTPS  # Default to HTTPS
    
    def test_curl_with_data_raw(self):
        """Test curl with --data-raw."""
        curl = '''curl -X POST https://webhook.site/test \
            --data-raw '{"complex": "%DATA%", "array": [1,2,3]}'
        '''
        req = burpr.from_curl(curl)
        
        assert req.body == '{"complex": "%DATA%", "array": [1,2,3]}'
    
    def test_curl_delete_request(self):
        """Test curl DELETE request."""
        curl = 'curl -X DELETE https://api.example.com/resource/%ID% -H "Authorization: Bearer %TOKEN%"'
        req = burpr.from_curl(curl)
        
        assert req.method == "DELETE"
        assert req.path == "/resource/%ID%"
        assert req.headers["Authorization"] == "Bearer %TOKEN%"


class TestSerialization:
    """Test converting BurpRequest back to Burp format."""
    
    def test_to_burp_format(self):
        """Test basic serialization."""
        req = BurpRequest(
            host="example.com",
            path="/api/test",
            protocol=ProtocolEnum.HTTP1_1,
            method="POST",
            headers={"Host": "example.com", "Content-Type": "application/json"},
            body='{"key": "%VALUE%"}',
            transport=TransportEnum.HTTPS
        )
        
        burp_str = burpr.to_burp_format(req)
        lines = burp_str.split("\n")
        
        assert lines[0] == "POST /api/test HTTP/1.1"
        assert "Host: example.com" in lines
        assert "Content-Type: application/json" in lines
        assert lines[-1] == '{"key": "%VALUE%"}'
    
    def test_to_burp_format_empty_body(self):
        """Test serialization with empty body."""
        req = BurpRequest(
            host="example.com",
            path="/test",
            protocol=ProtocolEnum.HTTP2,
            method="GET",
            headers={"Host": "example.com"},
            body="",
            transport=TransportEnum.HTTPS
        )
        
        burp_str = burpr.to_burp_format(req)
        lines = burp_str.split("\n")
        
        assert lines[0] == "GET /test HTTP/2"
        assert lines[-1] == ""  # Empty line after headers


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_clone_request(self):
        """Test cloning a request."""
        request = """POST /api/test HTTP/1.1
Host: example.com
X-Custom: %VALUE%

{"data": "%DATA%"}"""
        
        req1 = burpr.parse_string(request)
        req2 = burpr.clone(req1)
        
        # Modify clone
        req2.bind("%VALUE%", "modified")
        req2.bind("%DATA%", "changed")
        
        # Original should be unchanged
        assert "%VALUE%" in req1.headers["X-Custom"]
        assert "%DATA%" in req1.body
        assert req2.headers["X-Custom"] == "modified"
        assert "changed" in req2.body
    
    def test_prepare_content_length(self):
        """Test prepare function sets Content-Length."""
        req = BurpRequest(
            host="example.com",
            path="/api",
            method="POST",
            headers={},
            body='{"test": "data"}',
            transport=TransportEnum.HTTPS
        )
        
        burpr.prepare(req)
        assert req.headers["Content-Length"] == "16"
    
    def test_prepare_empty_body(self):
        """Test prepare with empty body."""
        req = BurpRequest(
            host="example.com",
            path="/api",
            method="POST",
            headers={},
            body="",
            transport=TransportEnum.HTTPS
        )
        
        burpr.prepare(req)
        assert req.headers["Content-Length"] == "0"


class TestRequestsLibraryParsing:
    """Test parsing requests library objects."""
    
    def test_from_requests_simple(self):
        """Test creating BurpRequest from requests-style arguments."""
        req = burpr.from_requests("GET", "https://api.example.com/users")
        
        assert req.method == "GET"
        assert req.host == "api.example.com"
        assert req.path == "/users"
        assert req.transport == TransportEnum.HTTPS
        assert req.body == ""
    
    def test_from_requests_with_json(self):
        """Test from_requests with JSON data."""
        req = burpr.from_requests(
            "POST", 
            "https://api.example.com/users",
            json={"name": "%NAME%", "email": "%EMAIL%"},
            headers={"Authorization": "Bearer %TOKEN%"}
        )
        
        assert req.method == "POST"
        assert req.headers["Content-Type"] == "application/json"
        assert req.headers["Authorization"] == "Bearer %TOKEN%"
        assert '"name": "%NAME%"' in req.body
        assert '"email": "%EMAIL%"' in req.body
    
    def test_from_requests_with_data(self):
        """Test from_requests with form data."""
        req = burpr.from_requests(
            "POST",
            "https://example.com/login",
            data={"username": "%USER%", "password": "%PASS%"}
        )
        
        assert req.headers["Content-Type"] == "application/x-www-form-urlencoded"
        assert "username=%USER%" in req.body
        assert "password=%PASS%" in req.body
    
    def test_from_requests_with_params(self):
        """Test from_requests with query parameters."""
        req = burpr.from_requests(
            "GET",
            "https://api.example.com/search",
            params={"q": "%QUERY%", "limit": "10"}
        )
        
        assert req.path == "/search?q=%QUERY%&limit=10"
    
    def test_from_requests_response_mock(self):
        """Test from_requests_response with mock object."""
        # Create a mock response object
        class MockRequest:
            def __init__(self):
                self.method = "POST"
                self.url = "https://api.example.com/data"
                self.headers = {"X-Custom": "%VALUE%"}
                self.body = "test=%TEST%"
        
        class MockResponse:
            def __init__(self):
                self.request = MockRequest()
        
        req = burpr.from_requests_response(MockResponse())
        
        assert req.method == "POST"
        assert req.host == "api.example.com"
        assert req.path == "/data"
        assert req.headers["X-Custom"] == "%VALUE%"
        assert req.body == "test=%TEST%"


class TestHTTP2Parsing:
    """Test HTTP/2 request parsing."""
    
    def test_from_http2_basic(self):
        """Test basic HTTP/2 request parsing."""
        headers = {
            ":method": "GET",
            ":path": "/api/users",
            ":authority": "example.com",
            ":scheme": "https"
        }
        
        req = burpr.from_http2(headers)
        
        assert req.method == "GET"
        assert req.path == "/api/users"
        assert req.host == "example.com"
        assert req.protocol == ProtocolEnum.HTTP2
        assert req.transport == TransportEnum.HTTPS
        assert req.headers["Host"] == "example.com"
    
    def test_from_http2_with_body(self):
        """Test HTTP/2 with body and headers."""
        headers = {
            ":method": "POST",
            ":path": "/api/data",
            ":authority": "api.example.com",
            ":scheme": "https",
            "content-type": "application/json",
            "authorization": "Bearer %TOKEN%",
            "x-request-id": "%REQUEST_ID%"
        }
        body = '{"action": "%ACTION%", "data": "%DATA%"}'
        
        req = burpr.from_http2(headers, body)
        
        assert req.method == "POST"
        assert req.protocol == ProtocolEnum.HTTP2
        assert req.headers["content-type"] == "application/json"
        assert req.headers["authorization"] == "Bearer %TOKEN%"
        assert req.body == body
    
    def test_from_http2_http_scheme(self):
        """Test HTTP/2 with HTTP scheme."""
        headers = {
            ":method": "GET",
            ":path": "/test",
            ":authority": "example.com:80",
            ":scheme": "http"
        }
        
        req = burpr.from_http2(headers)
        
        assert req.transport == TransportEnum.HTTP
        assert req.host == "example.com:80"
    
    def test_from_http2_with_placeholders(self):
        """Test HTTP/2 with placeholders that can be bound."""
        headers = {
            ":method": "PUT",
            ":path": "/api/users/%USER_ID%",
            ":authority": "%API_HOST%",
            ":scheme": "https",
            "authorization": "Bearer %TOKEN%"
        }
        body = '{"status": "%STATUS%"}'
        
        req = burpr.from_http2(headers, body)
        req.bind("%USER_ID%", "123")
        req.bind("%API_HOST%", "api.production.com")
        req.bind("%TOKEN%", "secret-token")
        req.bind("%STATUS%", "active")
        
        assert req.path == "/api/users/123"
        assert req.host == "api.production.com"
        assert req.headers["Host"] == "api.production.com"
        assert req.headers["authorization"] == "Bearer secret-token"
        assert req.body == '{"status": "active"}'


class TestRequestMethods:
    """Test BurpRequest methods for making requests."""
    
    def test_to_request(self):
        """Test converting to requests.Request object."""
        req = BurpRequest(
            host="api.example.com",
            path="/users",
            method="POST",
            headers={"Authorization": "Bearer token123"},
            body='{"name": "test"}',
            transport=TransportEnum.HTTPS
        )
        
        # Mock requests module
        import sys
        from unittest.mock import MagicMock
        
        mock_requests = MagicMock()
        mock_request = MagicMock()
        mock_prepared = MagicMock()
        mock_request.prepare.return_value = mock_prepared
        mock_requests.Request.return_value = mock_request
        
        sys.modules['requests'] = mock_requests
        
        result = req.to_request()
        
        mock_requests.Request.assert_called_once_with(
            method="POST",
            url="https://api.example.com/users",
            headers={"Authorization": "Bearer token123"},
            data='{"name": "test"}'
        )
        assert result == mock_prepared
    
    def test_make_request_warning_http2(self):
        """Test that HTTP/2 request shows warning with requests library."""
        req = BurpRequest(
            host="example.com",
            path="/test",
            method="GET",
            protocol=ProtocolEnum.HTTP2,
            transport=TransportEnum.HTTPS
        )
        
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # Mock the requests module
            import sys
            from unittest.mock import MagicMock
            mock_requests = MagicMock()
            sys.modules['requests'] = mock_requests
            
            try:
                req.make_request()
            except:
                pass
            
            assert len(w) == 1
            assert "HTTP/2" in str(w[0].message)
            assert "httpx" in str(w[0].message)


class TestErrorHandling:
    """Test error handling."""
    
    def test_empty_request_string(self):
        """Test parsing empty string raises error."""
        with pytest.raises(burpr.BurpParseError, match="Empty request string"):
            burpr.parse_string("")
    
    def test_invalid_request_line(self):
        """Test invalid request line raises error."""
        with pytest.raises(burpr.BurpParseError, match="Invalid request line"):
            burpr.parse_string("INVALID REQUEST")
    
    def test_missing_host_header(self):
        """Test missing Host header raises error."""
        request = """GET /test HTTP/1.1
User-Agent: Test

"""
        with pytest.raises(burpr.BurpParseError, match="Missing required Host header"):
            burpr.parse_string(request)
    
    def test_invalid_header_format(self):
        """Test invalid header format raises error."""
        request = """GET /test HTTP/1.1
Host: example.com
Invalid Header Without Colon

"""
        with pytest.raises(burpr.BurpParseError, match="Invalid header format"):
            burpr.parse_string(request)
    
    def test_curl_no_url(self):
        """Test curl without URL raises error."""
        with pytest.raises(burpr.BurpParseError, match="No URL found"):
            burpr.from_curl("curl -X POST")
    
    def test_curl_invalid_url(self):
        """Test curl with invalid URL raises error."""
        with pytest.raises(burpr.BurpParseError, match="Invalid URL format"):
            burpr.from_curl("curl ://")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])