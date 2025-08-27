# Changelog

All notable changes to burpr will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-27

### Added
- Initial release of burpr library
- Parse Burp Suite HTTP requests from strings and files
- Parse curl commands with full argument support
- Parse HTTP/2 requests with pseudo-headers
- Parse from Python requests library objects
- Placeholder system using %VARIABLE% format for dynamic values
- `.bind()` method for replacing placeholders with actual values
- Direct request execution with `.make_request()` and `.make_httpx_request()`
- Convert to requests.PreparedRequest with `.to_request()`
- Utility functions: clone(), prepare(), to_burp_format()
- Comprehensive error handling with BurpParseError
- Support for all HTTP methods (GET, POST, PUT, DELETE, PATCH, OPTIONS, etc.)
- Support for various content types (JSON, XML, form data, multipart)
- HTTP/HTTPS transport detection based on port and scheme
- Method chaining support for bind() operations
- Comprehensive test suite with 47+ tests

### Security
- Added warnings against malicious code generation
- Secure placeholder handling to prevent injection attacks

### Dependencies
- requests >= 2.25.0
- httpx[http2] >= 0.23.0